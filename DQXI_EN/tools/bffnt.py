#!/usr/bin/env python3
"""Minimal 3DS BFFNT (CFNT/FFNT) reader: lists code points, widths, glyph sheet info.
Usage: bffnt.py info font.bffnt [chars]"""
import struct, sys

class Font:
    def __init__(self, path):
        d = self.d = open(path, 'rb').read()
        assert d[:4] in (b'CFNT', b'FFNT'), d[:4]
        self.bom = d[4:6]
        hdr = struct.unpack_from('<H', d, 6)[0]
        nblocks = struct.unpack_from('<I', d, 0x10)[0] if d[:4]==b'FFNT' else struct.unpack_from('<I', d, 0x10)[0]
        self.cmap = {}; self.cwdh = []; self.blocks = {}
        o = hdr
        while o < len(d) - 8:
            mag = d[o:o+4]; sz = struct.unpack_from('<I', d, o+4)[0]
            self.blocks.setdefault(mag, []).append(o)
            if mag == b'FINF':
                (self.ftype, self.height, self.width, self.ascent, self.linefeed, self.alter) = struct.unpack_from('<BBBBHH', d, o+8)
                self.def_left, self.def_glyph, self.def_char = struct.unpack_from('<bBB', d, o+0x10)
                self.encoding = d[o+0x13]
            elif mag == b'TGLP':
                (self.cw, self.ch, self.nsheets, self.maxw, self.sheetsize, self.baseline, self.fmt, self.cols, self.rows, self.sw, self.sh) = struct.unpack_from('<BBBBIHHHHHH', d, o+8)
                self.sheet_off = struct.unpack_from('<I', d, o+0x1C)[0]
                self.tglp = o
            elif mag == b'CWDH':
                start, end = struct.unpack_from('<HH', d, o+8)
                for i in range(end - start + 1):
                    self.cwdh.append((start + i,) + struct.unpack_from('<bBB', d, o+0x10+3*i))
            elif mag == b'CMAP':
                cs, ce, meth = struct.unpack_from('<HHH', d, o+8)
                b = o + 0x14
                if meth == 0:
                    off = struct.unpack_from('<H', d, b)[0]
                    for c in range(cs, ce+1): self.cmap[c] = off + c - cs
                elif meth == 1:
                    for c in range(cs, ce+1):
                        g = struct.unpack_from('<H', d, b + 2*(c-cs))[0]
                        if g != 0xFFFF: self.cmap[c] = g
                elif meth == 2:
                    n = struct.unpack_from('<H', d, b)[0]
                    for i in range(n):
                        c, g = struct.unpack_from('<HH', d, b+2+4*i); self.cmap[c] = g
            if sz == 0: break
            o += sz
        self.widths = {g: (l, gw, cw) for g, l, gw, cw in self.cwdh}

if __name__ == '__main__':
    f = Font(sys.argv[2])
    print('blocks', {k.decode(): len(v) for k, v in f.blocks.items()})
    print('FINF h=%d w=%d asc=%d lf=%d enc=%d' % (f.height, f.width, f.ascent, f.linefeed, f.encoding))
    print('TGLP cell %dx%d base=%d maxw=%d sheets=%d fmt=%d grid %dx%d sheet %dx%d' % (f.cw, f.ch, f.baseline, f.maxw, f.nsheets, f.fmt, f.cols, f.rows, f.sw, f.sh))
    print('glyphs', len(f.cmap))
    chars = sys.argv[3] if len(sys.argv) > 3 else 'AaMmWwIi .,!?\'"-0123456789'
    for ch in chars:
        g = f.cmap.get(ord(ch))
        print(repr(ch), g, f.widths.get(g) if g is not None else 'MISSING')

# ---------------------------------------------------------------- sheets / glyph images
def _morton(x, y):
    m = 0
    for i in range(3):
        m |= ((x >> i) & 1) << (2*i) | ((y >> i) & 1) << (2*i + 1)
    return m

def decode_sheet(font, idx=0):
    """Decode TGLP sheet (A4 format 11 only) to a numpy uint8 alpha array [h][w]."""
    import numpy as np
    assert font.fmt == 11, 'only A4 sheets supported'
    w, h = font.sw, font.sh
    raw = np.frombuffer(font.d, dtype=np.uint8, count=font.sheetsize, offset=font.sheet_off + idx*font.sheetsize)
    nib = np.empty(raw.size*2, np.uint8); nib[0::2] = raw & 15; nib[1::2] = raw >> 4
    img = np.zeros((h, w), np.uint8)
    mort = [_morton(x, y) for y in range(8) for x in range(8)]
    tiles = nib.reshape(-1, 64)
    tx = w // 8
    t = 0
    for ty in range(h // 8):
        for txx in range(tx):
            tile = tiles[t]; t += 1
            blk = np.empty(64, np.uint8)
            blk[:] = tile[mort]
            img[ty*8:ty*8+8, txx*8:txx*8+8] = blk.reshape(8, 8)
    return img * 17

def glyph_cell(font, g, img=None):
    """Return (x, y) of glyph g's cell on the (decoded) sheet; cells are cw+1 x ch+1 incl. 1px border."""
    cols = font.cols
    c = g % (cols * font.rows)
    return (c % cols) * (font.cw + 1) + 1, (c // cols) * (font.ch + 1) + 1

def set_widths(font, table):
    """Patch CWDH entries in font.d. table: {glyph_index: (left, glyph_w, char_w)}; returns new bytes."""
    d = bytearray(font.d)
    for o in font.blocks[b'CWDH']:
        start, end = struct.unpack_from('<HH', d, o+8)
        for g, (l, gw, cw) in table.items():
            if start <= g <= end:
                struct.pack_into('<bBB', d, o+0x10+3*(g-start), l, gw, cw)
    return bytes(d)
