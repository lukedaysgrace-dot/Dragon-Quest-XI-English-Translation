import sys,json,os,re,glob
sys.path.insert(0,'/home/claude/tools')
os.environ.setdefault('DQXI_CONDENSE','0.92')
import wrap
m=wrap.Metrics('/home/claude/work/build/romfs/font')
lst=[l.rstrip('\n').split(' ',1) for l in open('/tmp/cs/qu_list.txt')]
tr={}
for f in sorted(glob.glob('/tmp/cs/qu_[0-9]*.txt')):
    for l in open(f):
        l=l.rstrip('\n')
        if l: i,t=l.split('|',1); tr[int(i)]=t
LIM=float(os.environ.get('LIM','240')); MAXL=int(os.environ.get('MAXL','5'))
out=['@gamecmn quest_ui_param.bxon']; bad=[]
for i,t in sorted(tr.items()):
    jpl=lst[i][1].count('⏎')+1
    lines=wrap.wrap(m,t,[('3D14',LIM)])
    if len(lines)>max(jpl,MAXL if jpl<5 else jpl): bad.append((i,len(lines),jpl,t))
    out.append('%s f: %s'%(lst[i][0],'\\n'.join(lines)))
open('/tmp/cs/gamecmn_qu.src','w').write('\n'.join(out)+'\n\n')
print(len(tr),'recs',len(bad),'over; missing',[i for i in range(max(tr)+1) if i not in tr][:5])
for b in bad: print(b[0],b[1],b[2],b[3][:70])
