#!/usr/bin/env python3
# dump2.py <pack short> [entry] [--all] [--cond PREFIX]  -> region/script ie grouped by npc/cond, unique JP once
import sys, re, sqlite3, collections
sys.path.insert(0,'/home/claude/tools')
from pack import Pack
from ie_struct import chains
db=sqlite3.connect('/home/claude/work/proj/db/progress.sqlite')
av=sys.argv[1:]
if '--cond' in av: i=av.index('--cond'); av=av[:i]+av[i+2:]
a=[x for x in av if not x.startswith('--')]
short=a[0]; ent=a[1] if len(a)>1 else ('npc_ie.bxon' if short.startswith('r') else 'ie.bxon')
allf='--all' in sys.argv
cp=None
if '--cond' in sys.argv: cp=sys.argv[sys.argv.index('--cond')+1]
pack=db.execute("select distinct pack from strings where pack like ?",('%/'+short+'.pack',)).fetchone()[0]
data=Pack('/home/claude/work/ext/romfs'+pack).get(ent)
info=chains(data)
S={r[0]:(r[1],r[2],r[3]) for r in db.execute("select off,jp_norm,en,status from strings where pack=? and entry=?",(pack,ent))}
def cl(s): return (s or '').replace('\n','⏎')
byjp=collections.defaultdict(list)
for i in info:
    if i['off'] in S: byjp[S[i['off']][0]].append(i['off'])
seen=set(); last=None
print('@'+short+('' if ent in('npc_ie.bxon','ie.bxon') else ' '+ent))
for i in info:
    o=i['off']
    if o not in S: continue
    jp,en,st=S[o]
    if cp and not i.get('cond','').startswith(cp): continue
    if jp in seen: continue
    seen.add(jp)
    if st=='translated' and not allf: continue
    hdr=(i.get('npc'),i.get('cond'))
    if hdr!=last: print('# npc %s cond %s'%hdr); last=hdr
    offs=[x for x in byjp[jp]]
    print(' '.join('%x'%x for x in offs), cl(jp), ('=> '+cl(en)) if en else '')
