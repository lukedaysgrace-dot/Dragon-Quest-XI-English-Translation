#!/usr/bin/env python3
# unc.py <btype> [from] [count]     : numbered list of uncovered unique JP (index = stable while coverage is unchanged)
# unc.py <btype> --fill en.txt out.json [--status fan]: lines "N|English" (\n escapes ok) -> tm JSON in text/en/
import sqlite3,sys,glob,json,re
a=sys.argv[1:]; bt=a[0]
db=sqlite3.connect('/home/claude/work/proj/db/progress.sqlite')
tm=set(r[0] for r in db.execute("select jp from tm where en is not null and en!=''"))
for f in glob.glob('/home/claude/text/en/*.json'):
    if '--fill' in a and f.endswith('/'+a[a.index('--fill')+2]): continue
    try: d=json.load(open(f,encoding='utf-8'))
    except Exception: continue
    tm|=set(d.get('tm',{}).keys())
    ids=set(d.get('id',{}).keys())
    globals().setdefault('IDS',set()).update(ids)
IDS=globals().get('IDS',set())
seen={}; lst=[]
q="select id,pack,entry,jp,jp_norm,en,status from strings where btype=? and status!='skip' order by pack,entry,off"
for sid,pack,ent,jp,jn,en,st in db.execute(q,(bt,)):
    if (en and st in('translated','reviewed','tested')) or jn in tm or sid in IDS or jn in seen: continue
    seen[jn]=1; lst.append((pack.split('/')[-1],ent,sid.rsplit('|',1)[1],jn))
if '--fill' in a:
    i=a.index('--fill'); src=a[i+1]; out=a[i+2]
    en={}
    for l in open(src,encoding='utf-8'):
        l=l.rstrip('\n')
        if not l.strip() or l.startswith('#'): continue
        n,e=l.split('|',1); en[int(n)]=e.replace('\\n','\n')
    res={}
    for n,e in en.items():
        res[lst[n-1][3]]=e
    json.dump({'_comment':'%s fill from %s'%(bt,src),'status':'translated','source':'fan','tm':res},open('/home/claude/text/en/'+out,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print('wrote',len(res),'of',len(lst),'uncovered; missing:',[n for n in range(1,len(lst)+1) if n not in en][:40])
else:
    s=int(a[1]) if len(a)>1 and a[1].isdigit() else 1; c=int(a[2]) if len(a)>2 else 10**9
    for n,(p,e,o,jn) in enumerate(lst,1):
        if s<=n<s+c: print(n,p.replace('.pack',''),o,'|',jn.replace('\n','⏎').replace('\u3000','_'))
    print('total',len(lst))
