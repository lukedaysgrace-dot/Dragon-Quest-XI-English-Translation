#!/usr/bin/env python3
"""setl.py [dir]  (stdin lines: '<pack> <offset> <new text>')  replaces the text of the src line starting with that offset."""
import sys,re
d=sys.argv[1] if len(sys.argv)>1 else '/tmp/cs'
for l in sys.stdin:
    l=l.rstrip('\n')
    if not l.strip(): continue
    m=re.match(r'(\S+) ([0-9a-f]+) (.*)$',l)
    if not m: print('BAD',l); continue
    k,off,t=m.groups(); p=f'{d}/{k}.src'
    L=open(p,encoding='utf-8').read().split('\n'); n=0
    for i,x in enumerate(L):
        if re.match(r'^%s( [0-9a-f]+)* f: '%off,x):
            L[i]=re.sub(r' f: .*$',lambda _:' f: '+t,x,count=1); n+=1
    if n!=1: print('MISS',k,off,n)
    open(p,'w',encoding='utf-8').write('\n'.join(L))
