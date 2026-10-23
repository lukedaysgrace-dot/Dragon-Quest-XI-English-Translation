#!/usr/bin/env python3
"""BFLIM codec for RGBA8 (fmt 9) and RGB565 (fmt 5) textures (8x8 tiles, Morton order, swizzle 4 = rotated).
Usage: bflim_rgb.py dec in.bflim out.png | bflim_rgb.py enc orig.bflim in.png out.bflim"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import bflim

def _xy(i):
    x = y = 0
    for b in range(3):
        x |= ((i >> (2 * b)) & 1) << b; y |= ((i >> (2 * b + 1)) & 1) << b
    return x, y

def decode(d):
    w, h, fmt, swz, size = bflim.info(d)
    pw, ph = bflim._dims(w, h, swz)
    bpp = {9: 4, 5: 2}[fmt]
    img = Image.new('RGBA', (pw, ph)); px = img.load(); o = 0
    for ty in range(0, ph, 8):
        for tx in range(0, pw, 8):
            for i in range(64):
                x, y = _xy(i); v = d[o + i * bpp:o + i * bpp + bpp]
                if fmt == 9: px[tx + x, ty + y] = (v[3], v[2], v[1], v[0])
                else:
                    c = v[0] | v[1] << 8
                    px[tx + x, ty + y] = (((c >> 11) & 31) * 255 // 31, ((c >> 5) & 63) * 255 // 63, (c & 31) * 255 // 31, 255)
            o += 64 * bpp
    if swz == 4: img = img.transpose(Image.Transpose.ROTATE_90)
    return img.crop((0, 0, w, h))

def encode(orig, img):
    w, h, fmt, swz, size = bflim.info(orig)
    img = img.convert('RGBA')
    if swz == 4: img = img.transpose(Image.Transpose.ROTATE_270)
    pw, ph = bflim._dims(w, h, swz)
    cv = Image.new('RGBA', (pw, ph)); cv.paste(img, (0, 0)); px = cv.load(); out = bytearray()
    for ty in range(0, ph, 8):
        for tx in range(0, pw, 8):
            for i in range(64):
                x, y = _xy(i); r, g, b, a = px[tx + x, ty + y]
                if fmt == 9: out += bytes([a, b, g, r])
                else:
                    c = (r * 31 // 255) << 11 | (g * 63 // 255) << 5 | (b * 31 // 255)
                    out += bytes([c & 255, c >> 8])
    assert len(out) == size, (len(out), size)
    return bytes(out) + orig[size:]

if __name__ == '__main__':
    if sys.argv[1] == 'dec': decode(open(sys.argv[2], 'rb').read()).save(sys.argv[3])
    else: open(sys.argv[4], 'wb').write(encode(open(sys.argv[2], 'rb').read(), Image.open(sys.argv[3])))
