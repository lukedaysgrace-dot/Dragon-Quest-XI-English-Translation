import sys,glob
new={}
for l in sys.stdin:
    l=l.rstrip('\n')
    if l: i,t=l.split('|',1); new[int(i)]=t
for f in glob.glob('/tmp/cs/eb_[0-9]*.txt'):
    L=open(f).read().split('\n'); ch=False
    for k,l in enumerate(L):
        if '|' in l and l.split('|')[0].isdigit() and int(l.split('|')[0]) in new:
            L[k]=l.split('|')[0]+'|'+new[int(l.split('|')[0])]; ch=True
    if ch: open(f,'w').write('\n'.join(L))
