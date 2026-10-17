#!/usr/bin/env python3
"""DQXI 3DS BXON container: string discovery and relocation-safe string replacement.

Layout (confirmed by inspection, see PROGRESS.md):
  0x00 'BXON' u32 version(1) u32 typehash char[20] typename
  0x20 u32 count, s32 relptr(->root array)    -- relptrs are SELF-RELATIVE s32
  every pointed-to block is preceded by the 4-byte marker '&&&&' (0x26262626)
  and blocks are padded to 4 bytes with '@' (0x40).
  Strings are UTF-16LE, NUL-terminated, each in its own '&&&&' block.

Replacement policy: if the new string fits in the old block it is written in place;
otherwise a new '&&&&' block is appended at EOF and every pointer to the old block
is redirected. Nothing else in the file moves, so non-string offsets stay valid.
"""
import struct

MARK = b'&&&&'

def _is_string_block(d, start, end):
    """Return (text_u16_list) if [start,end) is exactly a UTF16 string + NUL + '@' pad."""
    i = start
    chars = []
    while i + 2 <= end:
        c = d[i] | (d[i+1] << 8)
        i += 2
        if c == 0:
            pad = d[i:end]
            if len(pad) < 4 and all(b == 0x40 for b in pad) and (i + len(pad)) % 4 == 0:
                return chars
            if i == end == len(d):      # last string in file: not padded at EOF
                return chars
            return None
        chars.append(c)
    return None

class Bxon:
    def __init__(self, data):
        self.d = bytearray(data)
        assert self.d[:4] == b'BXON'
        self.typename = bytes(self.d[12:0x20]).split(b'\0')[0].decode()
        self._scan()

    def _scan(self):
        d = self.d
        n = len(d)
        marks = [i for i in range(0x20, n - 3, 4) if d[i:i+4] == MARK]
        self.blocks = []            # (start, end)
        for k, m in enumerate(marks):
            end = marks[k+1] if k + 1 < len(marks) else n
            self.blocks.append((m + 4, end))
        starts = {s: e for s, e in self.blocks}
        self.strings = {}           # start -> list of u16
        for s, e in self.blocks:
            t = _is_string_block(d, s, e)
            if t is not None: self.strings[s] = t
        str_ranges = set()
        for s in self.strings:
            str_ranges.update(range(s, starts[s], 4))
        self.ptrs = {}              # target -> [pointer positions]
        for p in range(0x20, n - 3, 4):
            if p in str_ranges: continue
            v = struct.unpack_from('<i', d, p)[0]
            if v <= 0: continue
            t = p + v
            if t in starts:
                self.ptrs.setdefault(t, []).append(p)
        # only strings that something points at are real strings
        self.strings = {s: t for s, t in self.strings.items() if s in self.ptrs}

    def string_list(self):
        """[(start_offset, [u16...])] in file order"""
        return sorted(self.strings.items())

    def replace(self, start, u16s):
        d = self.d
        enc = b''.join(struct.pack('<H', c) for c in u16s) + b'\0\0'
        enc += b'@' * ((-len(enc)) % 4)
        old_end = next(e for s, e in self.blocks if s == start)
        if len(enc) <= old_end - start:
            # in place; leftover space is filled with '@' (reader stops at the NUL)
            d[start:old_end] = enc.ljust(old_end - start, b'@')
            return start
        # relocate
        while len(d) % 4: d.append(0x40)
        d += MARK
        new = len(d)
        d += enc
        for p in self.ptrs[start]:
            struct.pack_into('<i', d, p, new - p)
        return new

    def data(self):
        return bytes(self.d)
