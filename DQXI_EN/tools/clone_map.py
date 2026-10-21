#!/usr/bin/env python3
"""clone_map.py <src.omap> <dst.omap> <dst_pack> [entry]
For every fan/official English line of the source omap, find strings with identical Japanese
(jp_norm) in dst_pack/entry (not yet translated) and write an omap with the same English."""
import sys, re, sqlite3, collections
src, dst, dpack = sys.argv[1:4]
ent_over = sys.argv[4] if len(sys.argv) > 4 else None
db = sqlite3.connect('/home/claude/work/proj/db/progress.sqlite')
packs = {}
for (p,) in db.execute('select distinct pack from strings'): packs.setdefault(p.rsplit('/',1)[-1].replace('.pack',''), p)
jp2en = {}; cur = None; ent = None
for line in open(src, encoding='utf-8'):
    s = line.rstrip('\n')
    if not s.strip() or s.startswith('#'): continue
    if s.startswith('@'):
        a = s[1:].split(); cur = packs[a[0]]; ent = a[1] if len(a) > 1 else None; continue
    m = re.match(r'^((?:[0-9a-f]+\s+)+)(f:|o:)\s*(.*)$', s)
    if not m: continue
    off = int(m.group(1).split()[0], 16)
    r = db.execute('select jp_norm from strings where pack=? and entry=? and off=?', (cur, ent, off)).fetchone()
    if r: jp2en.setdefault(r[0], (m.group(2), m.group(3)))
ent = ent_over or ent
out = ['@%s %s' % (dpack, ent)]; n = 0
by = collections.defaultdict(list)
for off, jn in db.execute('select off, jp_norm from strings where pack=? and entry=?', (packs[dpack], ent)):
    if jn in jp2en: by[jn].append(off)
for jn, offs in by.items():
    k, en = jp2en[jn]
    out.append('%s %s %s' % (' '.join('%x' % o for o in offs), k, en)); n += len(offs)
open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('cloned', n, 'strings into', dst)
