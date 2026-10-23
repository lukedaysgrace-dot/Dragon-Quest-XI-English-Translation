#!/usr/bin/env python3
"""BFLYT (FLYT) text-pane tool.

txt1 section layout (offsets relative to section start, verified on game data):
  0x0C name[24]  0x4C size(w,h f32)  0x54 u16 textBufBytes  0x56 u16 textStrBytes
  0x58 u16 material  0x5A u16 font  0x5C u8 pos  0x5D u8 align ... 0x64 u32 textStrOffset
  0x70 fontSize(x,y f32)  0x78 charSpace f32  0x7C lineSpace f32  0x80 u32 textIdOffset
textBufBytes is the capacity the runtime allocates for this pane; strings set by game code
longer than it are truncated, so for English we enlarge it (safe: it only changes an allocation size).
Usage: lyt.py dump file.bflyt
"""
import struct, sys

def sections(d):
    hl = struct.unpack_from('<H', d, 6)[0]
    n = struct.unpack_from('<H', d, 0x10)[0]
    o = hl
    for _ in range(n):
        mag = d[o:o+4]; sz = struct.unpack_from('<I', d, o+4)[0]
        yield o, mag, sz
        o += sz

def fonts(d):
    for o, mag, sz in sections(d):
        if mag == b'fnl1':
            n = struct.unpack_from('<H', d, o+8)[0]
            res = []
            for i in range(n):
                off = struct.unpack_from('<I', d, o+0xC+4*i)[0]
                p = o + 0xC + off
                res.append(d[p:d.index(b'\0', p)].decode())
            return res
    return []

def text_panes(d):
    out = []
    for o, mag, sz in sections(d):
        if mag != b'txt1': continue
        name = d[o+0xC:o+0x24].split(b'\0')[0].decode('ascii', 'replace')
        w, h = struct.unpack_from('<ff', d, o+0x4C)
        buf, sl, mat, font = struct.unpack_from('<HHHH', d, o+0x54)
        pos, align = d[o+0x5C], d[o+0x5D]
        toff = struct.unpack_from('<I', d, o+0x64)[0]
        fsx, fsy, cs, ls = struct.unpack_from('<ffff', d, o+0x70)
        txt = d[o+toff:o+toff+sl].decode('utf-16le') if sl else ''
        out.append({'sec': o, 'size': sz, 'name': name, 'w': w, 'h': h, 'buf': buf, 'strbytes': sl,
                    'font': font, 'align': align, 'fs': (fsx, fsy), 'cs': cs, 'ls': ls,
                    'toff': toff, 'text': txt.rstrip('\0')})
    return out

def rebuild(d, edits=None, min_buf=0, buf_scale=1, buf_cap=0xFFF0, buf_add=0, grow=None, fsx_scale=1.0, sizes=None, fscale=None):
    """edits: {pane_name: new_text}. Returns new file bytes.
    Rewrites each txt1 section: text string replaced/kept, textBufBytes enlarged."""
    edits = edits or {}
    hl = struct.unpack_from('<H', d, 6)[0]
    out = bytearray(d[:hl])
    for o, mag, sz in sections(d):
        sec = bytearray(d[o:o+sz])
        if mag == b'txt1':
            name = sec[0xC:0x24].split(b'\0')[0].decode('ascii', 'replace')
            buf, sl = struct.unpack_from('<HH', sec, 0x54)
            toff = struct.unpack_from('<I', sec, 0x64)[0]
            tid = struct.unpack_from('<I', sec, 0x80)[0]
            if name in edits:
                new = edits[name].encode('utf-16le') + b'\0\0'
                old_end = toff + ((buf + 3) & ~3)          # text area is the full buffer, 4-aligned
                if buf == 0: old_end = toff
                area = new + b'\0' * ((-len(new)) % 4)
                tail = sec[old_end:]
                sec = sec[:toff] + area + tail
                delta = len(area) - (old_end - toff)
                if tid and tid >= old_end:
                    struct.pack_into('<I', sec, 0x80, tid + delta)
                # other offsets after text (per-char transform etc.) at 0x84.. only in newer versions
                for k in (0x84, 0x88):
                    if k + 4 <= 0x8C and len(sec) > k:
                        pass
                sl = len(new); buf = len(area)
                struct.pack_into('<HH', sec, 0x54, buf, sl)
            sc = fsx_scale * (fscale or {}).get(name, 1.0)
            if sc != 1.0:
                fx = struct.unpack_from('<f', sec, 0x70)[0]
                struct.pack_into('<f', sec, 0x70, fx * sc)
            if sizes and name in sizes:
                v = sizes[name]
                struct.pack_into('<ff', sec, 0x4C, v[0], v[1])
                if len(v) == 4: struct.pack_into('<ff', sec, 0x2C, v[2], v[3])   # optional new position
            want = (grow or {}).get(name, 0)
            if min_buf or buf_scale != 1 or buf_add or want:
                nb = max(buf, want, min(max(min_buf, int(buf * buf_scale) + buf_add), buf_cap))
                nb = min(nb, 0xFFF0) & ~1
                # enlarging only the declared capacity; the file keeps the original-size area,
                # so we must also grow the in-file area (runtime copies buf bytes from file)
                if nb > buf:
                    pad = (((nb + 3) & ~3) - ((buf + 3) & ~3))
                    a_end = toff + ((buf + 3) & ~3)
                    sec = sec[:a_end] + b'\0' * pad + sec[a_end:]
                    tid = struct.unpack_from('<I', sec, 0x80)[0]
                    if tid and tid >= a_end: struct.pack_into('<I', sec, 0x80, tid + pad)
                    struct.pack_into('<H', sec, 0x54, nb)
            struct.pack_into('<I', sec, 4, len(sec))
        out += sec
    struct.pack_into('<I', out, 0xC, len(out))
    return bytes(out)

if __name__ == '__main__':
    d = open(sys.argv[2], 'rb').read()
    print('fonts', fonts(d))
    for p in text_panes(d):
        print('%-20s w=%6.1f h=%5.1f buf=%4d font=%d fs=%s cs=%.1f ls=%.1f %r' % (p['name'], p['w'], p['h'], p['buf'], p['font'], p['fs'], p['cs'], p['ls'], p['text']))
