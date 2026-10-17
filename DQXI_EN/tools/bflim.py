#!/usr/bin/env python3
"""Minimal BFLIM (CTR layout texture) codec for LA4 / L8 / A8 / LA8 / RGBA4 textures.
Handles 8x8 tiling + Morton order and the 'swizzle' rotate flag (4 = rotated 90 degrees).
Usage: bflim.py dec in.bflim out.png | bflim.py enc orig.bflim in.png out.bflim"""
import struct, sys
from PIL import Image

def morton(x, y):
    m = 0
    for i in range(3):
        m |= ((x >> i) & 1) << (2 * i) | ((y >> i) & 1) << (2 * i + 1)
    return m

def info(d):
    imag = d[-0x14:]
    w, h, align, fmt, swz = struct.unpack_from('<HHHBB', imag, 8)
    size = struct.unpack_from('<I', imag, 16)[0]
    return w, h, fmt, swz, size

BPP = {0: 1, 1: 1, 2: 1, 3: 2, 8: 2}

def _dims(w, h, swz):
    # physical (stored) dimensions; rotated textures are stored transposed, padded to pow2
    pw, ph = (h, w) if swz == 4 else (w, h)
    P = lambda v: 1 << (v - 1).bit_length()
    return P(max(pw, 8)), P(max(ph, 8))

def decode(d):
    w, h, fmt, swz, size = info(d)
    pw, ph = _dims(w, h, swz)
    bpp = BPP[fmt]
    img = Image.new('LA', (pw, ph))
    px = img.load(); o = 0
    for ty in range(0, ph, 8):
        for tx in range(0, pw, 8):
            for i in range(64):
                x = y = 0
                for b in range(3):
                    x |= ((i >> (2 * b)) & 1) << b; y |= ((i >> (2 * b + 1)) & 1) << b
                v = d[o + i * bpp: o + i * bpp + bpp]
                if fmt == 2: L, A = (v[0] >> 4) * 17, (v[0] & 15) * 17
                elif fmt == 0: L, A = v[0], 255
                elif fmt == 1: L, A = 255, v[0]
                elif fmt == 3: L, A = v[1], v[0]
                else: raise SystemExit('fmt %d unsupported' % fmt)
                px[tx + x, ty + y] = (L, A)
            o += 64 * bpp
    if swz == 4: img = img.transpose(Image.Transpose.ROTATE_90)
    return img.crop((0, 0, w, h)) if img.size != (w, h) else img

def encode(orig, img):
    w, h, fmt, swz, size = info(orig)
    img = img.convert('LA')
    if swz == 4: img = img.transpose(Image.Transpose.ROTATE_270)
    pw, ph = _dims(w, h, swz)
    canvas = Image.new('LA', (pw, ph)); canvas.paste(img, (0, 0)); px = canvas.load()
    bpp = BPP[fmt]; out = bytearray()
    for ty in range(0, ph, 8):
        for tx in range(0, pw, 8):
            for i in range(64):
                x = y = 0
                for b in range(3):
                    x |= ((i >> (2 * b)) & 1) << b; y |= ((i >> (2 * b + 1)) & 1) << b
                L, A = px[tx + x, ty + y]
                if fmt == 2: out.append(((L + 8) // 17) << 4 | ((A + 8) // 17))
                elif fmt == 0: out.append(L)
                elif fmt == 1: out.append(A)
                elif fmt == 3: out += bytes([A, L])
    assert len(out) == size, (len(out), size)
    return bytes(out) + orig[size:]

if __name__ == '__main__':
    if sys.argv[1] == 'dec':
        decode(open(sys.argv[2], 'rb').read()).save(sys.argv[3])
    else:
        o = open(sys.argv[2], 'rb').read()
        open(sys.argv[4], 'wb').write(encode(o, Image.open(sys.argv[3])))
