#!/usr/bin/env python3
"""fixm.py <pairs-file> src...   apply 'old ||| new' pairs to every src file where old occurs (no assert)."""
import sys
pairs=[l.split(' ||| ') for l in open(sys.argv[1],encoding='utf-8').read().strip().split('\n') if ' ||| ' in l]
for p in sys.argv[2:]:
    s=open(p,encoding='utf-8').read(); o=s
    for a,b in pairs: s=s.replace(a,b)
    if s!=o: open(p,'w',encoding='utf-8').write(s)
