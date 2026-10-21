#!/usr/bin/env python3
# gaps.py [pack-like]  -> list of still-untranslated strings (not in id maps, not in tm, no en)
import sqlite3,json,glob,sys,re,collections
ids=set();tm=set()
for f in glob.glob('/home/claude/text/en/*.json'):
    try: d=json.load(open(f))
    except: continue
    ids|=set(d.get('id',{}).keys()); tm|=set(d.get('tm',{}).keys())
c=sqlite3.connect('/home/claude/work/proj/db/progress.sqlite')
pat=sys.argv[1] if len(sys.argv)>1 else '%'
cnt=collections.Counter()
rows=[]
for id_,pack,ent,off,jp,jn,en,st in c.execute("select id,pack,entry,off,jp,jp_norm,en,status from strings where pack like ? order by seq",(pat,)):
    if id_ in ids or jp in tm or jn in tm or en or st=='translated': continue
    rows.append((pack.split('/')[-1].replace('.pack',''),ent,off,jp)); cnt[(rows[-1][0],ent)]+=1
if '-v' in sys.argv:
    for p,e,o,jp in rows: print('%s|%x\t%s'%(p,o,re.sub(r'\{ruby:([^|}]*)\|[^}]*\}',r'\1',jp).replace('\n','⏎')))
else:
    for k,v in sorted(cnt.items()): print(k,v)
    print(len(rows))
