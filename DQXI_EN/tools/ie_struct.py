#!/usr/bin/env python3
"""Group CharacterIEData strings (region npc_ie / script ie.bxon) by NPC record and story condition.

Layout found in param/region/r*.pack npc_ie.bxon:
  root: N records x 24 bytes (index = NPC slot); record +0x08 u32 count, +0x0C relptr -> condition table
  condition entry (16 bytes): u32 nlines, relptr -> dialogue, u8[4] cond (chapter, step, ?, variant), u8[4] cond2
  dialogue -> list of lines -> speaker/text strings
Each string is mapped back up the pointer chain, giving (npc, cond, order).
"""
import sys, struct, bisect
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from bxon import Bxon

def chains(data):
    b = Bxon(data)
    d = b.d
    starts = sorted(s for s, e in b.blocks)
    def block_of(pos):
        k = bisect.bisect_right(starts, pos) - 1
        return starts[k] if k >= 0 and pos >= starts[k] else 0x2c
    parent = {}
    for t, ps in b.ptrs.items():
        parent[t] = ps[0]
    out = []
    for s, u in b.string_list():
        chain = []; cur = s
        for _ in range(8):
            p = parent.get(cur)
            if p is None: break
            chain.append(p); cur = block_of(p)
            if cur == 0x2c or cur < 0x2c: break
        # chain[-1] is the pointer inside the root array
        info = {'off': s, 'u': u, 'chain': chain}
        if chain and block_of(chain[-1]) <= 0x2c or (chain and chain[-1] < starts[1] if len(starts) > 1 else False):
            info['npc'] = (chain[-1] - 0x2c) // 24
        if len(chain) >= 2:
            pe = chain[-2]          # pointer inside condition table entry (entry+4)
            info['cond'] = bytes(d[pe + 4:pe + 8]).hex()
            info['cond2'] = bytes(d[pe + 8:pe + 12]).hex()
        out.append(info)
    return out
