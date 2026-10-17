#!/usr/bin/env python3
"""SARC archive (UI layouts) read/rebuild.  Usage: sarc.py list|x file.arc [outdir]"""
import struct, sys, os

def _hash(name, key):
    h = 0
    for c in name.encode(): h = (h * key + c) & 0xFFFFFFFF
    return h

class Sarc:
    def __init__(self, data):
        d = self.d = bytes(data)
        assert d[:4] == b'SARC'
        hl, bom, size, doff, ver = struct.unpack_from('<HHIIH', d, 4)
        self.doff = doff
        o = hl
        assert d[o:o+4] == b'SFAT'
        shl, n, self.key = struct.unpack_from('<HHI', d, o+4)
        nodes = []
        for i in range(n):
            h, attr, s, e = struct.unpack_from('<IIII', d, o + shl + 16*i)
            nodes.append((h, attr, s, e))
        fo = o + shl + 16*n
        assert d[fo:fo+4] == b'SFNT'
        names = fo + 8
        self.files = []
        for h, attr, s, e in nodes:
            name = None
            if attr & 0x01000000:
                no = names + (attr & 0xFFFF) * 4
                name = d[no:d.index(b'\0', no)].decode()
            self.files.append({'name': name, 'hash': h, 'attr': attr, 'data': d[doff+s:doff+e], 'start': s})

    def get(self, name):
        return next(f['data'] for f in self.files if f['name'] == name)

    def replace(self, name, data):
        next(f for f in self.files if f['name'] == name)['data'] = bytes(data)

    def build(self):
        d = self.d
        hl = struct.unpack_from('<H', d, 4)[0]
        # keep header, SFAT, SFNT verbatim (names/hashes unchanged), re-layout data
        head = bytearray(d[:self.doff])
        out = bytearray()
        n = len(self.files)
        sfat = hl
        shl = struct.unpack_from('<H', d, sfat+4)[0]
        for i, f in enumerate(self.files):
            # preserve original alignment of each file's start
            align = 4
            for a in (0x2000, 0x1000, 0x400, 0x100, 0x80, 0x20, 8):
                if f['start'] % a == 0 and (f['start'] or a <= 0x80): align = a; break
            align = min(align, 0x80)
            while len(out) % align: out.append(0)
            s = len(out); out += f['data']; e = len(out)
            struct.pack_into('<II', head, sfat + shl + 16*i + 8, s, e)
        res = head + out
        struct.pack_into('<I', res, 8, len(res))
        return bytes(res)

if __name__ == '__main__':
    s = Sarc(open(sys.argv[2], 'rb').read())
    if sys.argv[1] == 'list':
        for f in s.files: print('%8x %8d %s' % (f['start'], len(f['data']), f['name']))
    elif sys.argv[1] == 'x':
        for f in s.files:
            p = os.path.join(sys.argv[3], f['name']); os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'wb').write(f['data'])
