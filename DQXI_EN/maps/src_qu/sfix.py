import sys
new={}
for l in sys.stdin:
    l=l.rstrip('\n')
    if l: i,t=l.split('|',1); new[int(i)]=t
f='/tmp/cs/sg_1.txt'
L=open(f).read().split('\n')
for k,l in enumerate(L):
    if '|' in l and int(l.split('|')[0]) in new: L[k]=l.split('|')[0]+'|'+new[int(l.split('|')[0])]
open(f,'w').write('\n'.join(L))
