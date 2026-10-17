#!/usr/bin/env python3
"""Patch UTF-16 UI strings embedded in code.bin (decompressed ExeFS .code).

Strings that fit their original slot are overwritten in place.  Longer strings are
relocated into the zero padding at the end of the text segment (mapped R-X, unused):
every `add rX, pc, #imm` that computes the old address is rewritten to
`ldr rX, [pc, #off]`, and the old (4-byte aligned) slot receives the absolute pointer
to the new string.  Output: IPS patch (offsets relative to code.bin start, base 0x100000).
Usage: code_patch.py <code_dec.bin> <strings.tsv> <out_dir>
  strings.tsv: addr<TAB>japanese(check)<TAB>english
"""
import sys, os, struct

BASE = 0x100000

def ror(v, r): return ((v >> r) | (v << (32 - r))) & 0xffffffff

def read_u16(d, a):
    o = a - BASE; s = ''
    while True:
        c = struct.unpack_from('<H', d, o)[0]; o += 2
        if c == 0: return s
        s += chr(c)

def capacity(d, a):
    o = a - BASE; n = len(read_u16(d, a)) * 2 + 2; j = o + n
    while j < len(d) and d[j] == 0 and (j - o) < 256: j += 1
    return j - o

def find_adr(d, target, text_end):
    hits = []
    for o in range(0, text_end - BASE, 4):
        ins = struct.unpack_from('<I', d, o)[0]
        if (ins >> 25) & 7 != 1: continue
        opc = (ins >> 21) & 0xf; rn = (ins >> 16) & 0xf
        if rn != 15 or opc not in (2, 4): continue
        imm = ror(ins & 0xff, 2 * ((ins >> 8) & 0xf))
        pc = o + BASE + 8
        if (pc + imm if opc == 4 else pc - imm) == target: hits.append(o + BASE)
    return hits

def keyboard(d, orig, path, free, free_end, log):
    pages = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'): continue
        if line.startswith('page\t'): pages.append((int(line.split('\t')[1], 16), [])); continue
        cells = line.split(' ')
        if len(cells) != 12: sys.exit('keyboard row needs 12 cells: %r' % line)
        pages[-1][1].append(cells)
    cache = {}
    def string(txt):
        nonlocal free
        if txt in cache: return cache[txt]
        blob = txt.encode('utf-16le') + b'\0\0'; blob += b'\0' * ((-len(blob)) % 4)
        if free + len(blob) > free_end: sys.exit('free area full')
        d[free - BASE:free - BASE + len(blob)] = blob; cache[txt] = free; free += len(blob)
        return cache[txt]
    for base, rows in pages:
        if len(rows) != 6: sys.exit('keyboard page needs 6 rows')
        for r in range(6):
            for c in range(12):
                if c == 11 and r >= 3: continue          # column 11 only has 3 keys
                k = c * 6 + r if c < 11 else 66 + r
                tok = rows[r][c]
                txt = '' if tok == '_' else ' ' if tok == 'SP' else tok
                a = base + 12 * k
                struct.pack_into('<III', d, a - BASE, string(txt), 0, 0)
        log.append('keyboard page %x: 69 keys' % base)
    return free

def main():
    code, tsv, out = sys.argv[1:4]
    d = bytearray(open(code, 'rb').read()); orig = bytes(d)
    text_end = 0x10000 + BASE  # will be set from padding search
    # free area: zero padding after .text (exheader text size 0x62403c -> mapped to 0x725000)
    free = 0x724040; free_end = 0x725000
    text_end = 0x724040
    log = []
    for line in open(tsv, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'): continue
        a, jp, en = line.split('\t'); a = int(a, 16)
        cur = read_u16(orig, a)
        if cur != jp: sys.exit('mismatch at %x: %r != %r' % (a, cur, jp))
        cap = capacity(orig, a); need = len(en) * 2 + 2
        if need <= cap:
            o = a - BASE
            d[o:o + cap] = en.encode('utf-16le') + b'\0' * (cap - len(en) * 2)
            log.append('%x inplace %r' % (a, en)); continue
        refs = find_adr(orig, a, text_end)
        lits = [o + BASE for o in range(0, len(orig) - 3, 4) if struct.unpack_from('<I', orig, o)[0] == a]
        if not refs and lits:
            # referenced through literal pools: repoint every literal to a copy in the free area
            new = free; blob = en.encode('utf-16le') + b'\0\0'
            blob += b'\0' * ((-len(blob)) % 4)
            if free + len(blob) > free_end: sys.exit('free area full')
            d[free - BASE:free - BASE + len(blob)] = blob; free += len(blob)
            for p in lits: struct.pack_into('<I', d, p - BASE, new)
            log.append('%x lit-reloc->%x %r lits=%s' % (a, new, en, [hex(x) for x in lits])); continue
        if not refs or a % 4:
            log.append('%x SKIPPED: cannot relocate %r (%d adr refs, align %d, cap %d)' % (a, en, len(refs), a % 4, cap)); continue
        new = free; blob = en.encode('utf-16le') + b'\0\0'
        blob += b'\0' * ((-len(blob)) % 4)
        if free + len(blob) > free_end: sys.exit('free area full')
        d[free - BASE:free - BASE + len(blob)] = blob; free += len(blob)
        for p in refs:
            ins = struct.unpack_from('<I', orig, p - BASE)[0]
            cond = ins & 0xF0000000; rd = (ins >> 12) & 0xf
            off = a - (p + 8)
            u = 1 if off >= 0 else 0
            if abs(off) > 4095: sys.exit('slot out of ldr range %x' % p)
            ldr = cond | 0x05100000 | (u << 23) | (15 << 16) | (rd << 12) | abs(off)
            struct.pack_into('<I', d, p - BASE, ldr)
        o = a - BASE
        d[o:o + cap] = struct.pack('<I', new) + b'\0' * (cap - 4)
        log.append('%x reloc->%x %r refs=%s' % (a, new, en, [hex(r) for r in refs]))
    # name-entry keyboard (maps/keyboard.tsv next to the strings file)
    kb = os.path.join(os.path.dirname(os.path.abspath(tsv)), 'keyboard.tsv')
    if os.path.exists(kb):
        free = keyboard(d, orig, kb, free, free_end, log)
    # IPS
    os.makedirs(out, exist_ok=True)
    ips = bytearray(b'PATCH'); i = 0; n = len(d)
    while i < n:
        if d[i] == orig[i]: i += 1; continue
        j = i
        while j < n and (d[j] != orig[j] or (j + 1 < n and d[j + 1] != orig[j + 1])) and j - i < 0xFFFF: j += 1
        if i == 0x454F46: i -= 1  # avoid 'EOF' offset
        ips += struct.pack('>I', i)[1:] + struct.pack('>H', j - i) + d[i:j]; i = j
    ips += b'EOF'
    open(os.path.join(out, 'code.ips'), 'wb').write(ips)
    open(os.path.join(out, 'code_patch.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log)); print('ips bytes', len(ips), 'free used', hex(free - 0x724040))

if __name__ == '__main__':
    main()
