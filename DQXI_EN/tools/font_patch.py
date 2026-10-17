#!/usr/bin/env python3
"""English font fixes (CWDH width table only; glyph bitmaps are untouched).

* 2D14 / 2D9 (pixel fonts for the 2D mode) are monospaced for ASCII (12/11 px cells).
  Make printable ASCII proportional: left=0, advance = glyph_width + 1 (digits stay
  tabular so numbers in menus still line up).
* ASCII space is 12-14 px in several fonts -> 4-5 px.
Usage: font_patch.py <romfs_dir> <out_romfs_dir>
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bffnt

SPACE = {'3D12': 4, '3D14': 5, '2D14': 4, '2D14SH': 5, '2D9': 4}
VWF = ('2D14', '2D9')

def patch(name, src):
    f = bffnt.Font(src)
    table = {}
    for c in range(0x20, 0x7F):
        g = f.cmap.get(c)
        if g is None or g not in f.widths: continue
        l, gw, cw = f.widths[g]
        if c == 0x20:
            if name in SPACE: table[g] = (0, 0, SPACE[name])
            continue
        if name in VWF and not chr(c).isdigit():
            table[g] = (0, gw, gw + 1)
    # U+3000 (ideographic space): the game turns line breaks into it when it shows a multi-line
    # description on one line (battle item list) -> make it as narrow as an ASCII space
    g = f.cmap.get(0x3000)
    if g is not None and name in SPACE: table[g] = (0, 0, SPACE[name])
    return bffnt.set_widths(f, table), len(table)

def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(out, 'font'), exist_ok=True)
    for name in SPACE:
        data, n = patch(name, os.path.join(src, 'font', name + '.bffnt'))
        open(os.path.join(out, 'font', name + '.bffnt'), 'wb').write(data)
        print(name, 'patched', n, 'width entries')

if __name__ == '__main__':
    main()
