import sys,json,os,re
sys.path.insert(0,'/home/claude/tools')
os.environ.setdefault('DQXI_CONDENSE','0.92')
import wrap
m=wrap.Metrics('/home/claude/work/build/romfs/font')
recs=json.load(open('/tmp/cs/ach_recs.json'))
tr={}
SH=json.load(open('/home/claude/maps/src_ach/title_short.json'))
for l in open('/tmp/cs/ach_all.txt'):
    l=l.rstrip('\n')
    if l:
        i,t,d=l.split('|',2); t=SH.get(i,t); tr[i]=[t,d]
        if m.width('3D14',t)>215: print('LONG TITLE',i,t,round(m.width('3D14',t)))
def jpwidth(d):
    ls=re.sub(r'\{ruby:([^|]*)\|[^}]*\}',r'\1',d).split('⏎')
    return max(m.width('3D14',l) for l in ls)
out=['@gamecmn achievement.bxon']; bad=[]
for k,(t,d) in tr.items():
    r=recs[int(k)]
    toff=r[0].split(' ',1)[0]
    out.append('%s f: %s'%(toff,t))
    if len(r)>=3: out.append('%s f: %s'%(r[1].split(' ',1)[0],t))
    doff=r[-1].split(' ',1)[0]
    if len(r)>=2:
        lim=290
        lines=wrap.wrap(m,d,[('3D14',lim)])
        if len(lines)>3: bad.append((k,len(lines),d))
        out.append('%s f: %s'%(doff,'\\n'.join(lines)))
open('/tmp/cs/gamecmn_ach.src','w').write('\n'.join(out)+'\n\n')
print(len(tr),'records;',len(bad),'overflow');
for b in bad: print(b)
