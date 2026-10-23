#!/usr/bin/env python3
"""Exact fit check for translated BFLYT panes (btype LYT): English width in the pane's own font and
size (after our condense/resizes, read from the BUILT layout) vs the pane width; lines vs pane height.
Usage: lyt_fit.py <proj> <built_romfs>"""
import sys, os, sqlite3, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wrap, lyt, bffnt
from pack import Pack
from sarc import Sarc
from build_patch import fix_chars

def main():
    proj, romfs = sys.argv[1:3]
    db = sqlite3.connect(os.path.join(proj, 'db', 'progress.sqlite'))
    tm = dict(db.execute('select jp,en from tm'))
    fonts = {n: bffnt.Font(os.path.join(romfs, 'font', n + '.bffnt')) for n in ('3D12', '3D14', '2D14', '2D9', '2D14SH')}
    m = wrap.Metrics(os.path.join(romfs, 'font'))
    want = collections.defaultdict(dict)
    for sid, jp, jpn, en, st in db.execute("select id,jp,jp_norm,en,status from strings where btype='LYT'"):
        en = en or tm.get(jpn) or tm.get(jp)
        if not en or st == 'skip': continue
        pack, arc, fl, pane = sid.split('|')
        want[(pack, arc, fl)][pane] = (fix_chars(en).replace('\r', ''), jp)
    bad = 0
    byfile = collections.defaultdict(dict)
    for (pack, arc, fl), panes in want.items():
        byfile[pack][(arc, fl)] = panes
    for pack, files in byfile.items():
        p = os.path.join(romfs, pack.lstrip('/'))
        if not os.path.exists(p): continue
        pk = Pack(p); ents = {e['name']: e['data'] for e in pk.entries}
        for (arc, fl), panes in files.items():
            if arc not in ents or ents[arc][:4] != b'SARC': continue
            s = Sarc(ents[arc]); f = next((x for x in s.files if x['name'] == fl), None)
            if not f: continue
            fn = lyt.fonts(f['data'])
            for t in lyt.text_panes(f['data']):
                if t['name'] not in panes: continue
                en, jp = panes[t['name']]
                font = fn[t['font']].replace('.bffnt', '') if t['font'] < len(fn) else '3D12'
                if font not in m.f: continue
                sx = t['fs'][0] / fonts[font].width
                lines = en.split('\n')
                w = max(m.width(font, l) + max(0, len(l) - 1) * t['cs'] for l in lines) * sx
                jw = max(m.width(font, l) for l in jp.split('\n')) * t['fs'][0] / fonts[font].width / wrap.CONDENSE if False else \
                     max(m.width(font, l) for l in jp.replace('\r', '').split('\n')) * sx / (wrap.CONDENSE or 1)
                lh = fonts[font].linefeed * t['fs'][1] / fonts[font].height + t['ls']
                h = len(lines) * lh
                lim = max(t['w'] * (1.3 if '/ui/map/' in pack else 1.0), jw)
                probs = []
                if w > lim + 1: probs.append('wide %.0f>%.0f' % (w, lim))
                if len(lines) > max(1, len(jp.replace('\r', '').split('\n'))) and h > t['h'] + lh * 0.5:
                    probs.append('lines %d (%.0f>%.0f px)' % (len(lines), h, t['h']))
                if probs:
                    bad += 1
                    print('%s|%s|%s|%s\t%s\t%s' % (pack, arc, fl, t['name'], ';'.join(probs), en.replace('\n', '⏎')))
    print('#', bad, file=sys.stderr)

if __name__ == '__main__':
    main()
