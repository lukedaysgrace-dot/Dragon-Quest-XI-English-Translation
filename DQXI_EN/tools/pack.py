#!/usr/bin/env python3
"""DQXI 3DS PACK/PACA archive codec.

Format (little-endian), confirmed against code.bin (fn @0x56f7a4) and data:
  0x00 char[4] 'PACK' (raw) or 'PACA' (whole file BLZ-compressed, see blz.py)
  0x04 u32  total (decompressed) size
  0x08 u16  0x0100 version ; u16 0xFEFF (BOM)
  0x0C u16  entry count N ; u16 offset of offset-table (always 0x18)
  0x10 u32  end of offset table, aligned (== 0x18 + 4N rounded up to 0x10? see build())
  0x14 u32  hash of the archive (preserved verbatim)
  0x18 u32[N] entry offsets ; followed by u32[2N] per-entry hash pair (preserved)
  entry: u16 hdr_size ; u16 align_flag ; u32 data_size ; char name[hdr_size-8] ; data[data_size] ; pad to 4
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blz

def load(path_or_bytes):
    d = open(path_or_bytes, 'rb').read() if isinstance(path_or_bytes, str) else path_or_bytes
    compressed = d[:4] == b'PACA'
    if compressed:
        d = blz.decompress(d)
        d = b'PACK' + d[4:]
    assert d[:4] == b'PACK', d[:4]
    return d, compressed

class Pack:
    def __init__(self, data):
        self.raw, self.compressed = load(data)
        d = self.raw
        self.version, self.bom, self.count, self.tbl = struct.unpack_from('<HHHH', d, 8)
        self.tbl_end, self.hash = struct.unpack_from('<II', d, 0x10)
        self.offsets = list(struct.unpack_from('<%dI' % self.count, d, self.tbl))
        self.entries = []
        for o in self.offsets:
            hs, fl, sz = struct.unpack_from('<HHI', d, o)
            name = d[o + 8:o + hs].split(b'\0')[0].decode('ascii')
            self.entries.append({'name': name, 'hdr': d[o:o + hs], 'flag': fl,
                                 'data': d[o + hs:o + hs + sz], 'off': o})
        # everything between the offset table and the first entry (hash table) kept verbatim
        self.meta = d[self.tbl + 4 * self.count:self.offsets[0]] if self.count else b''

    def get(self, name):
        for e in self.entries:
            if e['name'] == name: return e['data']
        raise KeyError(name)

    def replace(self, name, data):
        for e in self.entries:
            if e['name'] == name: e['data'] = bytes(data); return
        raise KeyError(name)

    def build(self, compress=False):
        """Rebuild. Entry data alignment: data starts at entry_off + hdr_size, and the
        original layout aligns data to (1 << something) given by hdr_size choice; we keep
        each entry's original hdr_size but re-pad so that data alignment modulo 0x80 is
        preserved when possible."""
        out = bytearray(self.raw[:self.tbl])
        out += b'\0' * (4 * self.count)
        out += self.meta
        offs = []
        for e in self.entries:
            hs = len(e['hdr'])
            # preserve the alignment of the data start that the original had
            orig_data = e['off'] + hs
            align = 4
            for a in (0x80, 0x40, 0x20, 0x10, 8):
                if orig_data % a == 0: align = a; break
            # entry header start must be 4-aligned; choose start so data is aligned
            start = (len(out) + 3) & ~3
            while (start + hs) % align: start += 4
            out += b'\0' * (start - len(out))
            offs.append(start)
            hdr = bytearray(e['hdr']); struct.pack_into('<I', hdr, 4, len(e['data']))
            out += hdr + e['data']
        out += b'\0' * ((-len(out)) % 4)
        struct.pack_into('<%dI' % self.count, out, self.tbl, *offs)
        struct.pack_into('<I', out, 4, len(out))
        if compress:
            raise NotImplementedError('PACA re-compression: write PACK (game accepts both magics)')
        return bytes(out)

def main():
    cmd = sys.argv[1]
    if cmd == 'list':
        p = Pack(sys.argv[2])
        print('compressed' if p.compressed else 'raw', p.count, 'entries')
        for e in p.entries: print('%8x %2d %8d %s' % (e['off'], e['flag'], len(e['data']), e['name']))
    elif cmd == 'x':
        p = Pack(sys.argv[2]); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
        for e in p.entries: open(os.path.join(out, e['name']), 'wb').write(e['data'])
    elif cmd == 'dec':
        open(sys.argv[3], 'wb').write(load(sys.argv[2])[0])
    else:
        sys.exit(__doc__)

if __name__ == '__main__':
    main()
