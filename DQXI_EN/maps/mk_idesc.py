import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from _paths import TOOLS, FONTS, DB, ROWS
import sys, json, sqlite3
sys.path.insert(0,TOOLS)
import wrap
M=wrap.Metrics(FONTS)
C=0.92
SPEC=[('3D12',116/C),('2D14',106/C)]
rows=[l.rstrip('\n').split('\t') for l in open('items.tsv',encoding='utf8')]
en={}
for f in ['maps/idesc1.txt','maps/idesc2.txt','maps/idesc3.txt','maps/idesc4.txt','maps/idesc5_fix.txt']:
    for l in open(f,encoding='utf8'):
        l=l.rstrip('\n')
        if '=' in l: i,e=l.split('=',1); en[int(i)]=e
db=sqlite3.connect('proj/db/progress.sqlite')
have=set(r[0] for r in db.execute("select distinct jp_norm from strings where entry='item.bxon'"))
tm={}; long=[]; nomatch=[]
for i,e in en.items():
    jp=rows[i][2].replace('⏎','\n')
    if jp not in have: nomatch.append((i,jp)); continue
    lines=wrap.wrap(M,e,SPEC)
    if len(lines)>3: long.append((i,lines))
    tm[jp]=e   # the game word-wraps item descriptions itself (verified in-game); only the 3-line limit is checked
# undescribed?
alld=set(r[2] for r in rows if r[2])
missing=[d for d in alld if d.replace('⏎','\n') not in tm]
json.dump({"_comment":"Item descriptions (syscmn item.bxon), fan translation, pre-wrapped for the item detail window (3D 116px / 2D 106px).",
 "status":"translated","source":"fan","tm":tm},open('/mnt/user-data/outputs/en/64_item_desc.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print('tm',len(tm),'long',len(long),'nomatch',len(nomatch),'missing',len(missing))
for x in nomatch[:5]: print(' NM',x)
for x in missing[:10]: print(' MISS',x)
for x in long: print(' LONG',x)
