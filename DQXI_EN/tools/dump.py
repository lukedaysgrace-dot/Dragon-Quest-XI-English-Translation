#!/usr/bin/env python3
# dump strings of packs: dump.py <pack-like-pattern> [entry] [--all]
import sqlite3, sys, re
db=sqlite3.connect('/home/claude/work/proj/db/progress.sqlite')
pat=sys.argv[1]; ent=sys.argv[2] if len(sys.argv)>2 and not sys.argv[2].startswith('-') else '%'
allf='--all' in sys.argv
def clean(s):
    s=re.sub(r'\{ruby:([^|}]*)\|[^}]*\}',r'\1',s or '')
    return s.replace('\n','⏎')
for pack,entry,off,jp,en,st in db.execute("select pack,entry,off,jp,en,status from strings where pack like ? and entry like ? order by pack,entry,off",(pat,ent)):
    if st=='translated' and not allf: continue
    print('%s|%x\t%s%s'%(pack.split('/')[-1].replace('.pack',''),off,clean(jp),('\t=> '+clean(en)) if en else ''))
