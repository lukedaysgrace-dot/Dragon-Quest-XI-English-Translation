#!/usr/bin/env python3
"""Structural verification of a built patch against the original RomFS.

For every rebuilt .pack:
  * archive parses, entry names/order identical, BXON type identical;
  * for BXON: every original pointer still points at a '&&&&' block; all bytes outside
    original string blocks are unchanged; each string decodes and re-encodes losslessly;
  * for SARC/BFLYT: same file list, same section list, text panes parse.
Usage: verify_build.py <romfs_dir> <build_dir>
"""
import os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack import Pack
from bxon import Bxon, MARK
from sarc import Sarc
import lyt, textcodec as tc

def check_bxon(o, n, where, errs):
    bo = Bxon(o)
    nd = n
    if nd[:0x20] != o[:0x20]: errs.append(where + ' header changed')
    str_bytes = set()
    for s, e in bo.blocks:
        if s in bo.strings: str_bytes.update(range(s, e))
    ptrpos = {p for ps in bo.ptrs.values() for p in ps}
    for i in range(0, len(o)):
        if i in str_bytes or i in ptrpos or any(i - k in ptrpos for k in (1, 2, 3)): continue
        if nd[i] != o[i]:
            errs.append('%s byte %#x changed outside strings' % (where, i)); break
    for t, ps in bo.ptrs.items():
        for p in ps:
            v = struct.unpack_from('<i', nd, p)[0]
            tgt = p + v
            if nd[tgt-4:tgt] != MARK: errs.append('%s ptr@%#x -> %#x not a block' % (where, p, tgt)); continue
            if t in bo.strings:
                u = []; k = tgt
                while True:
                    c = nd[k] | nd[k+1] << 8; k += 2
                    if c == 0: break
                    u.append(c)
                if tc.encode(tc.decode(u), tc.detect_nl(u) if tc.detect_nl(u) in ('crlf', 'lf') else 'crlf') != u and tc.detect_nl(u) != 'mixed':
                    errs.append('%s string@%#x not round-trippable' % (where, tgt))

def main():
    root, build = sys.argv[1], sys.argv[2]
    nf = ne = 0; errs = []
    for dp, dn, fn in os.walk(os.path.join(build, 'romfs')):
        for f in fn:
            if not f.endswith('.pack'): continue
            rel = os.path.relpath(os.path.join(dp, f), os.path.join(build, 'romfs'))
            po = Pack(os.path.join(root, rel)); pn = Pack(os.path.join(dp, f)); nf += 1
            if [e['name'] for e in po.entries] != [e['name'] for e in pn.entries]:
                errs.append(rel + ' entry list differs'); continue
            if po.meta != pn.meta: errs.append(rel + ' hash table differs')
            for a, b in zip(po.entries, pn.entries):
                if a['data'] == b['data']: continue
                ne += 1
                w = rel + ':' + a['name']
                if a['data'][:4] == b'BXON': check_bxon(a['data'], b['data'], w, errs)
                elif a['data'][:4] == b'SARC':
                    so, sn = Sarc(a['data']), Sarc(b['data'])
                    if [x['name'] for x in so.files] != [x['name'] for x in sn.files]: errs.append(w + ' sarc list differs')
                    for x, y in zip(so.files, sn.files):
                        if x['data'] != y['data'] and x['name'].endswith('.bflyt'):
                            sx = [(m, ) for _, m, _ in lyt.sections(x['data'])]
                            sy = [(m, ) for _, m, _ in lyt.sections(y['data'])]
                            if sx != sy: errs.append(w + ':' + x['name'] + ' section list differs')
                            try: lyt.text_panes(y['data'])
                            except Exception as ex: errs.append(w + ':' + x['name'] + ' txt1 parse ' + str(ex))
    print('packs', nf, 'entries changed', ne, 'errors', len(errs))
    for e in errs[:40]: print('  ', e)
    return 1 if errs else 0

if __name__ == '__main__':
    sys.exit(main())
