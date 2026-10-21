#!/usr/bin/env python3
"""expand.py <dump.txt> <in.omap> <out.omap>
In.omap lines: '<firstoffset> f: text'. Replaces the first offset by the full offset list of the dump line that starts with that offset."""
import sys,re
dump,inp,out=sys.argv[1:4]
full={}
for l in open(dump,encoding='utf-8'):
    if l.startswith('#') or l.startswith('@') or not l.strip(): continue
    toks=l.split(' ')
    offs=[]
    for t in toks:
        if re.fullmatch(r'[0-9a-f]{3,6}',t): offs.append(t)
        else: break
    if offs: full[offs[0]]=offs
o=open(out,'w',encoding='utf-8')
for l in open(inp,encoding='utf-8'):
    l=l.rstrip('\n')
    m=re.match(r'^([0-9a-f]{3,6}) f: (.*)$',l)
    if m and m.group(1) in full:
        o.write(' '.join(full[m.group(1)])+' f: '+m.group(2)+'\n')
    elif m:
        print('NOT IN DUMP',m.group(1),file=sys.stderr); o.write(l+'\n')
    else: o.write(l+'\n')
