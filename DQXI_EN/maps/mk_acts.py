import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from _paths import TOOLS, FONTS, DB, ROWS
import sys, json, sqlite3
sys.path.insert(0,TOOLS)
import wrap
M=wrap.Metrics(FONTS)
C=0.92
BATTLE=[('2D9',90/C),('3D12',94/C)]
def load(f):
    d={}
    for l in open(f,encoding='utf8'):
        l=l.rstrip('\n')
        if '=' in l: j,e=l.split('=',1); d[j]=e
    return d
names=load('maps/acts_names.txt'); desc=load('maps/acts_desc.txt'); misc=load('maps/acts_misc.txt')
def brk(en):
    if len(en)<=12 or ' ' not in en: return en
    sp=[i for i,c in enumerate(en) if c==' ']
    i=min(sp,key=lambda i:abs(i-len(en)/2))
    return en[:i+1]+'\n'+en[i+1:]
db=sqlite3.connect('proj/db/progress.sqlite')
tm={}; probs=[]; miss=[]
for (jn,) in db.execute("select distinct jp_norm from strings where entry='battle_act_text.bxon'"):
    flat=jn.replace('\n','')
    k=jn.replace('\n','⏎')
    if k in desc:
        en=desc[k]
        lines=wrap.wrap(M,en,BATTLE)
        if len(lines)>3: probs.append((len(lines),en,lines))
        tm[jn]='\n'.join(lines)
    elif k in misc: tm[jn]=misc[k].replace('⏎','\n')
    elif flat in names: tm[jn]=brk(names[flat]) if '\n' in jn else names[flat]
    else: miss.append(jn)
json.dump({"_comment":"Battle skills/spells/status names and descriptions (gamecmn battle_act_text.bxon). Spell names follow series English naming; others fan renderings. Descriptions pre-wrapped for the 90px battle help window.",
 "status":"translated","source":"fan","tm":tm},open('/mnt/user-data/outputs/en/63_battle_acts.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print('tm',len(tm),'missing',len(miss),'over3',len(probs))
for m in miss: print(' MISS',repr(m))
for p in probs: print(' LONG',p[0],p[2])
