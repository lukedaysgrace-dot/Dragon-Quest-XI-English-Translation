#!/usr/bin/env python3
"""Extract ExeFS and RomFS from a decrypted (NoCrypto) .3ds/.cci image.

Usage: ctr_extract.py <image.3ds> <outdir> [--list] [--only=/script,/param,...]
(existing files of the right size are skipped, so runs can be resumed)
Writes outdir/exheader.bin, outdir/exefs/*, outdir/romfs/** and outdir/romfs_index.tsv
(path, offset-in-image, size) so files can be located/verified later.
"""
import os, struct, sys

MU = 0x200

def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def u64(b, o): return struct.unpack_from('<Q', b, o)[0]

def read_at(f, off, n):
    f.seek(off); return f.read(n)

def ncch_info(f):
    h = read_at(f, 0, 0x200)
    assert h[0x100:0x104] == b'NCSD', 'not an NCSD image'
    p0 = u32(h, 0x120) * MU
    n = read_at(f, p0, 0x200)
    assert n[0x100:0x104] == b'NCCH'
    flags = n[0x188:0x190]
    if not flags[7] & 0x04:
        sys.exit('NCCH partition is encrypted; decrypt it first (e.g. GodMode9 / Decrypt9).')
    info = {'base': p0, 'exh_size': u32(n, 0x180)}
    for name, o in (('exefs', 0x1A0), ('romfs', 0x1B0)):
        info[name] = (p0 + u32(n, o) * MU, u32(n, o + 4) * MU)
    return info

def extract_exefs(f, off, out):
    hdr = read_at(f, off, 0x200)
    os.makedirs(out, exist_ok=True)
    for i in range(10):
        name = hdr[i*16:i*16+8].rstrip(b'\0').decode()
        o, s = struct.unpack_from('<II', hdr, i*16+8)
        if not name: continue
        with open(os.path.join(out, name.lstrip('.') + '.bin'), 'wb') as g:
            g.write(read_at(f, off + 0x200 + o, s))
        print('exefs', name, hex(s))

def romfs_l3(f, off):
    ivfc = read_at(f, off, 0x60)
    assert ivfc[:4] == b'IVFC', ivfc[:4]
    master = u32(ivfc, 0x08)
    bs3 = u32(ivfc, 0x4C)   # level-3 block size (log2)
    l3 = off + ((0x60 + master + (1 << bs3) - 1) & ~((1 << bs3) - 1))
    return l3

def walk_romfs(f, l3):
    h = read_at(f, l3, 0x28)
    hs, dho, dhl, dmo, dml, fho, fhl, fmo, fml, fdo = struct.unpack('<10I', h)
    dmeta = read_at(f, l3 + dmo, dml)
    fmeta = read_at(f, l3 + fmo, fml)
    data = l3 + fdo
    out = []
    def name_of(meta, o, base):
        nl = u32(meta, o + base)
        return meta[o + base + 4:o + base + 4 + nl].decode('utf-16le')
    def do_dir(doff, path):
        child = u32(dmeta, doff + 0x08)
        ffile = u32(dmeta, doff + 0x0C)
        while ffile != 0xFFFFFFFF:
            nl = u32(fmeta, ffile + 0x1C)
            nm = fmeta[ffile + 0x20:ffile + 0x20 + nl].decode('utf-16le')
            do = u64(fmeta, ffile + 0x08); sz = u64(fmeta, ffile + 0x10)
            out.append((path + '/' + nm, data + do, sz))
            ffile = u32(fmeta, ffile + 0x04)
        while child != 0xFFFFFFFF:
            nl = u32(dmeta, child + 0x14)
            nm = dmeta[child + 0x18:child + 0x18 + nl].decode('utf-16le')
            do_dir(child, path + '/' + nm)
            child = u32(dmeta, child + 0x04)
    do_dir(0, '')
    return out

def main():
    img, outdir = sys.argv[1], sys.argv[2]
    only_list = '--list' in sys.argv
    with open(img, 'rb') as f:
        info = ncch_info(f)
        os.makedirs(outdir, exist_ok=True)
        files = walk_romfs(f, romfs_l3(f, info['romfs'][0]))
        with open(os.path.join(outdir, 'romfs_index.tsv'), 'w', encoding='utf-8') as idx:
            for p, o, s in files: idx.write(f'{p}\t{o:#x}\t{s}\n')
        print(len(files), 'romfs files,', sum(s for _, _, s in files) / 2**20, 'MiB')
        if only_list: return
        with open(os.path.join(outdir, 'exheader.bin'), 'wb') as g:
            g.write(read_at(f, info['base'] + 0x200, 0x800))
        extract_exefs(f, info['exefs'][0], os.path.join(outdir, 'exefs'))
        prefixes = [a[len('--only='):].split(',') for a in sys.argv if a.startswith('--only=')]
        prefixes = prefixes[0] if prefixes else None
        for p, o, s in files:
            if prefixes and not any(p.startswith(x) for x in prefixes): continue
            dst = os.path.join(outdir, 'romfs', p.lstrip('/'))
            if os.path.exists(dst) and os.path.getsize(dst) == s: continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            f.seek(o); rem = s
            with open(dst, 'wb') as g:
                while rem:
                    chunk = f.read(min(rem, 1 << 22)); g.write(chunk); rem -= len(chunk)

if __name__ == '__main__':
    main()
