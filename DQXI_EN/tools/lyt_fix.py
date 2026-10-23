#!/usr/bin/env python3
"""Fix LYT panes reported by lyt_fit.py: first squeeze the font horizontally (>= MIN_SCALE),
then fall back to the shorter forms in maps/lyt_short.txt. Map labels (ui/map/) are free-floating
text on the area map, so they may run up to MAP_SLACK x the pane width.
Writes: tools/grow.txt (auto block of 'layout|pane=xS' lines) and text/en/998_lyt_fit_fan.json (id overrides).
Usage: lyt_fix.py <lyt_fit.txt> <proj> <font_dir>"""
import sys, os, re, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wrap
MIN_SCALE, MAP_SLACK = 0.80, 1.3
BEGIN, END = '# --- auto: lyt_fix.py (font squeeze) ---', '# --- end auto ---'

def main():
    rep, proj, fdir = sys.argv[1:4]
    short = {}
    for l in open(os.path.join(HERE, '..', 'maps', 'lyt_short.txt'), encoding='utf-8'):
        l = l.strip()
        if l and not l.startswith('#'):
            a = l.split('|'); short[a[0]] = a[1:]
    scale = {}; ids = {}; left = []
    for l in open(rep, encoding='utf-8'):
        if l.startswith('#'): continue
        sid, p, en = l.rstrip('\n').split('\t')
        m = re.search(r'wide (\d+)>(\d+)', p)
        if not m: left.append((sid, p, en)); continue
        w, lim = int(m.group(1)), int(m.group(2))
        if '/ui/map/' in sid: lim *= MAP_SLACK
        key = sid.split('|')[2].rsplit('/', 1)[-1] + '|' + sid.split('|')[3]
        need = lim / w
        if need >= MIN_SCALE:
            scale[key] = min(scale.get(key, 1), int(need * 100) / 100); continue
        # shorter text: widths scale linearly with the text, so estimate from the measured width
        base = en.replace('⏎', '')
        cur_px_per_unit = w / max(1, len(base))
        done = False
        for alt in short.get(base, []):
            w2 = w * (len(alt) / max(1, len(base)))      # rough; refined by the next lyt_fit run
            if w2 * MIN_SCALE <= lim or alt == short[base][-1]:
                ids[sid.replace('⏎', '')] = alt
                s = min(1, lim / w2) if w2 else 1
                if s < 1: scale[key] = min(scale.get(key, 1), max(MIN_SCALE, int(s * 100) / 100))
                done = True; break
        if not done:
            scale[key] = MIN_SCALE; left.append((sid, p, en))
    gp = os.path.join(HERE, 'grow.txt'); g = open(gp, encoding='utf-8').read()
    if BEGIN in g: g = g[:g.index(BEGIN)] + g[g.index(END) + len(END) + 1:]
    g = g.rstrip('\n') + '\n' + BEGIN + '\n' + ''.join('%s=x%.2f\n' % (k, v) for k, v in sorted(scale.items())) + END + '\n'
    open(gp, 'w', encoding='utf-8').write(g)
    out = os.path.join(proj, 'text', 'en', '998_lyt_fit_fan.json')
    old = json.load(open(out, encoding='utf-8'))['id'] if os.path.exists(out) else {}
    old.update(ids)
    json.dump({'_comment': 'shorter UI/map labels so they fit their panes (tools/lyt_fix.py)', 'status': 'translated',
               'source': 'fan', 'id': old}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('scaled panes', len(scale), 'text overrides', len(ids), 'unresolved', len(left))
    for x in left: print('LEFT', *x)

if __name__ == '__main__':
    main()
