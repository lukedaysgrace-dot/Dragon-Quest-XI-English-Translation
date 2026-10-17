#!/usr/bin/env python3
"""Redraw the name-entry keyboard textures (title.pack timg/win_keyboard*_3d.bflim) with the English
layout from maps/keyboard.tsv, using glyphs from the game's own 3D12 font so the style matches.
Usage: kb_texture.py <font_dir> <keyboard.tsv> <orig.bflim> <page_index> <out.bflim> [preview.png]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bffnt, bflim
from PIL import Image

COLX = [1, 22, 42, 63, 84, 116, 137, 158, 179, 200, 222, 243]
ROWY = [0, 17, 34, 51, 68, 85]

def pages(path):
    out = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'): continue
        if line.startswith('page\t'): out.append([]); continue
        out[-1].append(line.split(' '))
    return out

class Glyphs:
    def __init__(self, font_path):
        self.f = bffnt.Font(font_path)
        self.sheets = {}
    def draw(self, img, x, y, ch):
        f = self.f; g = f.cmap.get(ord(ch))
        if g is None: return 0
        per = f.cols * f.rows; sheet = g // per
        if sheet not in self.sheets: self.sheets[sheet] = bffnt.decode_sheet(f, sheet)
        a = self.sheets[sheet]; cx, cy = bffnt.glyph_cell(f, g)
        left, gw, cw = f.widths[g]
        px = img.load()
        for yy in range(f.ch):
            for xx in range(gw):
                al = int(a[cy + yy, cx + xx])
                if al and 0 <= x + left + xx < img.size[0] and 0 <= y + yy < img.size[1]:
                    L, A = px[x + left + xx, y + yy]
                    px[x + left + xx, y + yy] = (255, max(A, al))
        return cw
    def width(self, s):
        return sum(self.f.widths[self.f.cmap[ord(c)]][2] for c in s if ord(c) in self.f.cmap)

def main():
    font_dir, tsv, orig, page, out = sys.argv[1:6]
    o = open(orig, 'rb').read()
    img = bflim.decode(o).convert('LA')
    G = Glyphs(os.path.join(font_dir, '3D12.bffnt'))
    rows = pages(tsv)[int(page)]
    px = img.load()
    for r in range(6):
        for c in range(12):
            if c == 11 and r >= 3: continue
            tok = rows[r][c]
            label = '' if tok in ('_', 'SP') else tok
            x0 = COLX[c] - 1; x1 = (COLX[c + 1] - 2) if c < 11 else 255
            if c == 10 and r >= 3: x1 = 255               # function keys span cols 10-11
            y0 = ROWY[r]
            for yy in range(y0, y0 + 15):
                for xx in range(x0, x1 + 1): px[xx, yy] = (255, 0)
            if tok == 'SP': label = '␣' if 0x2423 in G.f.cmap else ''
            if not label: continue
            w = G.width(label)
            x = x0 + 1 if (c == 10 and r >= 3) else x0 + max(0, (x1 - x0 + 1 - w) // 2)
            for ch in label: x += G.draw(img, x, y0, ch)
    # bottom buttons (next / previous) used by the password keyboard
    for (bx0, bx1, label) in ((0, 45, 'Next'), (48, 93, 'Prev')):
        has_box = sum(1 for xx in range(bx0, bx1) if px[xx, 111][1] > 200 and px[xx, 111][0] < 64) > 20
        if not has_box: continue
        for yy in range(111, 127):
            for xx in range(bx0 + 1, bx1):
                px[xx, yy] = (0, 255)
        w = G.width(label); x = bx0 + (bx1 - bx0 + 1 - w) // 2
        for ch in label: x += G.draw(img, x, 113, ch)
    open(out, 'wb').write(bflim.encode(o, img))
    if len(sys.argv) > 6:
        bg = Image.new('RGBA', img.size, (40, 30, 20, 255)); im = img.convert('RGBA')
        bg.alpha_composite(im); bg.resize((img.size[0] * 3, img.size[1] * 3), Image.NEAREST).save(sys.argv[6])

if __name__ == '__main__':
    main()
