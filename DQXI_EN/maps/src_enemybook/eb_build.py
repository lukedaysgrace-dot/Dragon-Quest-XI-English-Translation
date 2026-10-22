import sys,json,os,re,glob
sys.path.insert(0,'/home/claude/tools')
os.environ.setdefault('DQXI_CONDENSE','0.92')
import wrap
m=wrap.Metrics('/home/claude/work/build/romfs/font')
recs=json.load(open('/tmp/cs/eb_recs.json'))
tr={}
for f in sorted(glob.glob('/tmp/cs/eb_[0-9]*.txt')):
    for l in open(f):
        l=l.rstrip('\n')
        if l: i,t=l.split('|',1); tr[int(i)]=t
out=['@record_3d enemy_book.bxon']; bad=[]
LIM=float(os.environ.get('LIM','160'))
for i,t in sorted(tr.items()):
    first=recs[i][0].split(' ')[0]
    lines=wrap.wrap(m,t,[('3D14',LIM)])
    if len(lines)>4: bad.append((i,len(lines),t))
    out.append('%s f: %s'%(first,'\\n'.join(lines)))
open('/tmp/cs/record_3d_eb.src','w').write('\n'.join(out)+'\n\n')
print(len(tr),'records,',len(bad),'over 4 lines; missing',[i for i in range(max(tr)+1) if i not in tr][:5])
for b in bad: print(b[0],b[1],b[2][:70])
