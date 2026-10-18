#!/usr/bin/env python3
"""Compact map file -> per-id translation JSON (<prefix>_official.json + <prefix>_fan.json).

Usage: omap2json.py <file.omap> <progress.sqlite> <rows.jsonl> <out_prefix>

Map format (one string per line, '#' starts a comment):
  @a_010_cs_010             current pack (short name; entry defaults: cs_text.bxon for cutscenes,
  @r021 book_ie.bxon         npc_ie.bxon for region packs, ie.bxon for /script, talk_content.bxon
                             for talk_party) - an explicit entry may follow the pack name
  200 o3120                 official row 3120 (speaker prefix "Name: " and <yesno> removed, <pc> -> hero)
  200 o3142.1               page 1 (0-based) of a multi-page official row
  200 o3142.0+3142.1        several pages/rows joined with a space
  200 o: text               condensed / adapted official line (counts as official)
  200 f: text               fan translation
  200 = 1f4                 same English as offset 1f4 of the current pack
  200 1f4 2a0 o3120         several offsets on one line get the same English
  "\\n" in a text forces a line break (normally the build wraps automatically).
"""
import sys, re, json, sqlite3

def load_rows(p):
    return [json.loads(l) for l in open(p, encoding='utf-8')]

SPK = re.compile(r"^(\*|[A-Z][\w .'\-&]{0,30}):\s+")

def clean_official(t):
    t = SPK.sub('', t.strip())
    t = re.sub(r'\s*<yesno[^>]*>\s*|\s*\[yes/no\]\s*', ' ', t).strip()
    t = t.replace('<pc>', '{var:1}').replace('[pc]', '{var:1}')
    t = re.sub(r'<LM_[^>]*>', '', t)
    return t

def official(rows, ref):
    parts = []
    for r in ref.split('+'):
        if '.' in r:
            i, p = r.split('.'); parts.append(clean_official(rows[int(i)]['pages'][int(p)]))
        else:
            pg = [clean_official(x) for x in rows[int(r)]['pages']]
            # haiku (Hotto) and other short verse: one page per line
            parts.append('\n'.join(pg) if len(pg) == 3 and all(len(x) <= 40 for x in pg) else ' '.join(pg))
    return ' '.join(parts)

_M = None
def uiwrap(en, jp):
    global _M
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import wrap
    from build_patch import fix_chars
    if _M is None:
        _M = wrap.Metrics(os.environ.get('DQXI_FONTS', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work', 'build', 'romfs', 'font')))
    specs, _ = wrap.adaptive_specs(_M, jp)
    lines = []
    for para in en.split('\n'):
        cur = ''
        for w in para.split(' '):
            cand = w if not cur else cur + ' ' + w
            if cur and not wrap.fits(_M, fix_chars(cand), specs, 1.0): lines.append(cur); cur = w
            else: cur = cand
        lines.append(cur)
    return '\n'.join(lines)

def main():
    mp, dbp, rowsp, outp = sys.argv[1:5]
    rows = load_rows(rowsp)
    db = sqlite3.connect(dbp)
    packs = {}
    for (p,) in db.execute('select distinct pack from strings'):
        packs.setdefault(p.rsplit('/', 1)[-1].replace('.pack', ''), p)
    out = {'o': {}, 'f': {}}; cur = None; ent = None; errs = []; done = {}
    for ln, line in enumerate(open(mp, encoding='utf-8'), 1):
        s = line.rstrip('\n')
        if not s.strip() or s.lstrip().startswith('#'): continue
        if s.startswith('@'):
            a = s[1:].split()
            cur = packs.get(a[0]) or errs.append('%d: unknown pack %s' % (ln, a[0]))
            if len(a) > 1: ent = a[1]
            elif '/cs/' in (cur or ''): ent = 'cs_text.bxon'
            elif '/region/' in (cur or ''): ent = 'npc_ie.bxon'
            elif '/talk_party/' in (cur or ''): ent = 'talk_content.bxon'
            else: ent = 'ie.bxon'
            continue
        m = re.match(r'^((?:[0-9a-f]+\s+)+)(ow:|fw:|o:|f:|o[0-9][0-9.+]*w?|=)\s*(.*)$', s)
        if not m: errs.append('%d: bad line %r' % (ln, s)); continue
        offs = [int(x, 16) for x in m.group(1).split()]
        kind, rest = m.group(2), m.group(3)
        if kind == '=':
            k = (cur, ent, int(rest.strip(), 16))
            if k not in done: errs.append('%d: = target not defined yet' % ln); continue
            src, en = done[k]
        elif kind in ('f:', 'fw:'): src, en = 'f', rest.strip()
        elif kind in ('o:', 'ow:'): src, en = 'o', rest.strip()
        else:
            try: src, en = 'o', official(rows, kind[1:].rstrip('w'))
            except Exception as e: errs.append('%d: %s' % (ln, e)); continue
        en = en.replace('\\n', '\n').replace(' \u00b6 ', '\n')
        if kind.endswith('w') or kind.endswith('w:'):
            # UI text that the game does not wrap (quest log...): break at the Japanese line width
            r = db.execute('select jp_norm from strings where id=?', ('%s|%s|%x' % (cur, ent, offs[0]),)).fetchone()
            if r: en = uiwrap(en, r[0])
        for off in offs:
            sid = '%s|%s|%x' % (cur, ent, off)
            if not db.execute('select 1 from strings where id=?', (sid,)).fetchone():
                errs.append('%d: no string %s' % (ln, sid)); continue
            out[src][sid] = en; done[(cur, ent, off)] = (src, en)
            out['f' if src == 'o' else 'o'].pop(sid, None)
    # identical Japanese elsewhere (other region packs, other story states) gets the same English
    # through the translation memory; conflicting translations of one Japanese line are left out
    tm = {'o': {}, 'f': {}}; seen = {}
    for src in ('o', 'f'):
        for sid, en in out[src].items():
            r = db.execute('select jp_norm, btype from strings where id=?', (sid,)).fetchone()
            if not r or not r[0] or r[1] != 'CharacterIEData': continue
            if r[0] in seen and seen[r[0]] != (src, en): seen[r[0]] = None; continue
            seen[r[0]] = (src, en)
    for jp, v in seen.items():
        if v: tm[v[0]][jp] = v[1]
    for src, name in (('o', 'official'), ('f', 'fan')):
        if out[src]:
            json.dump({'status': 'translated', 'source': 'official' if src == 'o' else 'fan',
                       '_comment': 'generated by omap2json.py from ' + mp.split('/')[-1], 'id': out[src],
                       'tm': tm[src]},
                      open('%s_%s.json' % (outp, name), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('official', len(out['o']), 'fan', len(out['f']), 'errors', len(errs))
    for e in errs: print('  ', e)
    sys.exit(1 if errs else 0)

if __name__ == '__main__':
    main()
