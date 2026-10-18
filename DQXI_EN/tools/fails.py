#!/usr/bin/env python3
# fails.py <json...> : list strings failing fit, grouped by english, in omap form
import sys, json, sqlite3, collections
sys.path.insert(0,'/home/claude/tools')
import os; os.environ.setdefault('DQXI_CONDENSE','0.92')
import wrap
from build_patch import fix_chars
db=sqlite3.connect('/home/claude/work/proj/db/progress.sqlite'); m=wrap.Metrics('/home/claude/work/build/romfs/font')
g=collections.OrderedDict()
for fn in sys.argv[1:]:
    d=json.load(open(fn))
    for sid,en in d.get('id',{}).items():
        bt,jp=db.execute('select btype,jp from strings where id=?',(sid,)).fetchone()
        t,p=wrap.layout(m,fix_chars(en),bt,jp)
        if p:
            pk,ent,off=sid.split('|'); g.setdefault((pk,ent,en),[]).append(off)
cur=None
for (pk,ent,en),offs in g.items():
    s=pk.rsplit('/',1)[-1].replace('.pack','')
    if (s,ent)!=cur: cur=(s,ent); print('@'+s+(' '+ent if ent not in('npc_ie.bxon','ie.bxon','cs_text.bxon','talk_content.bxon') else ''))
    print(' '.join(offs),'o:' ,en, ' [%d]'%len(en))
