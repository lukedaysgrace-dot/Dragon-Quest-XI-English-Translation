#!/usr/bin/env python3
"""Build the English LayeredFS patch from the progress DB.

Usage: build_patch.py <romfs_dir> <project_dir> <out_dir> [--all-layouts] [--only=<pack prefix>]
  out_dir/romfs/...           modified files (relative to RomFS root)
  out_dir/report.txt          overflow / encoding problems
  out_dir/manifest.sha256     checksums of every output file
Translations come from strings.en (status translated/reviewed/tested) or, failing that,
from the translation memory tm (same Japanese text -> same English).
"""
import os, sys, re, sqlite3, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack import Pack
from bxon import Bxon
from sarc import Sarc
import lyt, textcodec as tc, wrap, font_patch

OK = ('translated', 'reviewed', 'tested')
# characters the game fonts lack (verified in-game: missing glyphs are silently dropped)
CHAR_MAP = {'\u2014': '\u2015', '\u2013': '-', '\u2018': "'", '\u2019': "'", '\u00e9': 'e', '\u00e8': 'e',
            '\u00ea': 'e', '\u00e0': 'a', '\u00ee': 'i', '\u00ef': 'i', '\u00e7': 'c', '\u00fb': 'u', '\u00f4': 'o',
            '\u00c9': 'E', '\u00a0': ' ', '\u00f6': 'o', '\u00fc': 'u', '\u00f1': 'n', '\u00e2': 'a'}
def fix_chars(s):
    return ''.join(CHAR_MAP.get(c, c) for c in s)
MIN_BUF = int(os.environ.get('DQXI_MIN_BUF', '0'))
# horizontal condense of every text pane (fontSize.x *= CONDENSE) - gives English ~8% more room
CONDENSE = float(os.environ.get('DQXI_CONDENSE', '1'))
# per-pane buffer growth whitelist: lines 'layoutname.bflyt|pane=bytes' in tools/grow.txt
TEX_DIR = os.environ.get('DQXI_TEX_DIR', '')
GROW = {}; SIZES = {}   # grow.txt: 'layout|pane=bytes' (buffer) or 'layout|pane=w,h' (pane size)
_gp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grow.txt')
if os.path.exists(_gp):
    for _l in open(_gp, encoding='utf-8'):
        _l = _l.split('#')[0].strip()
        if '=' in _l:
            _k, _v = _l.split('=')
            if ',' in _v: SIZES[_k.strip()] = tuple(float(x) for x in _v.split(','))
            else: GROW[_k.strip()] = int(_v)
# NOTE: growth of all panes crashed the game in a cutscene (a_010_cs_040) - default off; use GROW whitelist
# targeted growth: every text pane gets buf*SCALE+ADD bytes, capped at CAP (runtime-filled names/labels need room)
BUF_SCALE = float(os.environ.get('DQXI_BUF_SCALE', '1')); BUF_ADD = int(os.environ.get('DQXI_BUF_ADD', '0')); BUF_CAP = int(os.environ.get('DQXI_BUF_CAP', '64'))   # >0 enlarges every text pane buffer; 256 overflowed the UI heap (crash) - see PROGRESS

def load_translations(db):
    tm = {jp: en for jp, en in db.execute("select jp,en from tm where en is not null and en!=''")}
    RUBY = re.compile(r'\{ruby:([^|{}]*)\|[^{}]*\}')
    per = collections.defaultdict(dict)
    n = 0
    for sid, pack, entry, btype, off, nl, jp, en, st in db.execute(
            "select id,pack,entry,btype,off,nl,jp,en,status from strings where status!='skip'"):
        t = en if (en and st in OK) else tm.get(RUBY.sub(r'\1', jp))
        if t is None: continue
        per[pack][sid] = (entry, btype, off, nl, jp, t); n += 1
    return per, n

def main():
    root, proj, out = sys.argv[1], sys.argv[2], sys.argv[3]
    all_layouts = '--all-layouts' in sys.argv
    only = [a.split('=', 1)[1] for a in sys.argv if a.startswith('--only=')]
    db = sqlite3.connect(os.path.join(proj, 'db', 'progress.sqlite'))
    per, n = load_translations(db)
    os.makedirs(os.path.join(out, 'romfs'), exist_ok=True)
    rep = open(os.path.join(out, 'report.txt'), 'w', encoding='utf-8')
    # fonts first (wrapping uses the patched metrics)
    for name in font_patch.SPACE:
        data, _ = font_patch.patch(name, os.path.join(root, 'font', name + '.bffnt'))
        os.makedirs(os.path.join(out, 'romfs', 'font'), exist_ok=True)
        open(os.path.join(out, 'romfs', 'font', name + '.bffnt'), 'wb').write(data)
    m = wrap.Metrics(os.path.join(out, 'romfs', 'font'))
    packs = set(per)
    if all_layouts:
        for dp, dn, fn in os.walk(os.path.join(root, 'ui')):
            for f in fn:
                if f.endswith('.pack'):
                    packs.add('/' + os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/'))
    if TEX_DIR and os.path.isdir(TEX_DIR):
        for dp, dn, fn in os.walk(TEX_DIR):
            rel = os.path.relpath(dp, TEX_DIR).replace(os.sep, '/')
            parts = rel.split('/')
            for i, part in enumerate(parts):
                if part.endswith('.pack'): packs.add('/' + '/'.join(parts[:i + 1])); break
    if only: packs = {p for p in packs if p.startswith(tuple(only))}
    stats = collections.Counter()
    for pack in sorted(packs):
        tr = per.get(pack, {})
        pk = Pack(os.path.join(root, pack.lstrip('/')))
        changed = False
        by_entry = collections.defaultdict(list)
        for sid, v in tr.items(): by_entry[v[0]].append((sid,) + v)
        for e in pk.entries:
            d = e['data']
            if d[:4] == b'BXON' and e['name'] in by_entry:
                b = Bxon(d)
                for sid, entry, btype, off, nl, jp, en in by_entry[e['name']]:
                    text, probs = wrap.layout(m, fix_chars(en), btype, jp)
                    for p in probs: rep.write('%s\t%s\n' % (sid, p)); stats['overflow'] += 1
                    try:
                        u = tc.encode(text, 'crlf' if nl == 'crlf' else 'lf')
                    except tc.EncodeError as ex:
                        rep.write('%s\tENCODE %s\n' % (sid, ex)); stats['encode_err'] += 1; continue
                    if off not in b.strings:
                        rep.write('%s\tSTALE id (offset not a string)\n' % sid); continue
                    b.replace(off, u); stats['bxon'] += 1
                pk.replace(e['name'], b.data()); changed = True
            elif d[:4] == b'SARC':
                s = Sarc(d); sch = False
                for fl in s.files:
                    if not (fl['name'] and fl['name'].endswith('.bflyt')): continue
                    key = e['name'] + '|' + fl['name']
                    edits = {}
                    for sid, entry, btype, off, nl, jp, en in by_entry.get(key, []):
                        edits[sid.rsplit('|', 1)[1]] = fix_chars(en).replace('\r', ''); stats['lyt'] += 1
                    lname = fl['name'].rsplit('/', 1)[-1]
                    grow = {k.split('|', 1)[1]: v for k, v in GROW.items() if k.split('|', 1)[0] == lname}
                    sizes = {k.split('|', 1)[1]: v for k, v in SIZES.items() if k.split('|', 1)[0] == lname}
                    if edits or all_layouts or BUF_SCALE != 1 or grow or sizes:
                        nd = lyt.rebuild(fl['data'], edits, min_buf=MIN_BUF, buf_scale=BUF_SCALE, buf_cap=BUF_CAP, buf_add=BUF_ADD,
                                         grow=grow, fsx_scale=CONDENSE, sizes=sizes)
                        if nd != fl['data']:
                            s.replace(fl['name'], nd); sch = True
                # replacement textures: <TEX_DIR>/<pack path>/<arc>/<file>
                if TEX_DIR:
                    for fl in s.files:
                        if not fl['name']: continue
                        t = os.path.join(TEX_DIR, pack.lstrip('/'), e['name'], fl['name'])
                        if os.path.exists(t):
                            s.replace(fl['name'], open(t, 'rb').read()); sch = True; stats['tex'] += 1
                if sch:
                    pk.replace(e['name'], s.build()); changed = True
        if changed:
            dst = os.path.join(out, 'romfs', pack.lstrip('/'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'wb').write(pk.build())
            stats['packs'] += 1
    rep.close()
    with open(os.path.join(out, 'manifest.sha256'), 'w') as mf:
        for dp, dn, fn in os.walk(os.path.join(out, 'romfs')):
            for f in sorted(fn):
                p = os.path.join(dp, f)
                mf.write('%s  %s\n' % (hashlib.sha256(open(p, 'rb').read()).hexdigest(),
                                      os.path.relpath(p, out).replace(os.sep, '/')))
    print('translations available', n, dict(stats))

if __name__ == '__main__':
    main()
