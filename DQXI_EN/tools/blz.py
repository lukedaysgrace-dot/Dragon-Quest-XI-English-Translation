#!/usr/bin/env python3
"""Nintendo 3DS backward-LZ (BLZ) codec for ExeFS .code.  Usage: blz.py d|c in out"""
import struct, sys

def decompress(src: bytes) -> bytes:
    buf_top_bottom, extra = struct.unpack_from('<II', src, len(src) - 8)
    hdr_len = buf_top_bottom >> 24
    comp_len = buf_top_bottom & 0xFFFFFF
    out = bytearray(src) + bytearray(extra)
    dst = len(out)
    s = len(src) - hdr_len
    end = len(src) - comp_len
    while s > end:
        s -= 1; flags = out[s]
        for _ in range(8):
            if s <= end: break
            if flags & 0x80:
                s -= 2
                v = out[s] | (out[s + 1] << 8)
                n = ((v >> 12) & 0xF) + 3
                disp = (v & 0xFFF) + 3
                for _ in range(n):
                    dst -= 1
                    out[dst] = out[dst + disp]
            else:
                s -= 1; dst -= 1
                out[dst] = out[s]
            flags = (flags << 1) & 0xFF
            if dst <= end: break
    return bytes(out)

if __name__ == '__main__':
    mode, a, b = sys.argv[1:4]
    data = open(a, 'rb').read()
    if mode == 'd':
        open(b, 'wb').write(decompress(data))
    else:
        sys.exit('compression not needed: patch code via IPS/exheader with uncompressed code (see docs)')
