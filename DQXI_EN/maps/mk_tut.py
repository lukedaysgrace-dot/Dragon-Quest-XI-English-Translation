import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from _paths import TOOLS, FONTS, DB, ROWS
import sys, json
sys.path.insert(0,TOOLS)
import wrap
M=wrap.Metrics(FONTS)
C=0.92
SPEC=[('3D12',336/C),('2D9',310/C/1.1)]
jp=[l.rstrip('\n') for l in open('maps/tut_jp.txt',encoding='utf8')]
tm={}; prob=[]
for l in open('maps/tut_en.txt',encoding='utf8'):
    l=l.rstrip('\n')
    if '=' not in l: continue
    i,e=l.split('=',1); i=int(i)
    paras=e.split('|')
    lines=[]
    for k,p in enumerate(paras):
        if k: lines.append('')
        lines+=wrap.wrap(M,p,SPEC)
    t='\n'.join(lines)
    if len(lines)>11 or len(t)>500: prob.append((i,len(lines),len(t)))
    tm[jp[i-1].replace('⏎','\n')]=t
json.dump({"_comment":"Tutorial windows (gamecmn tutorial.bxon). Fan translation, pre-wrapped for win_sakusen_tutorial3 (3D 336px / 2D 310px).",
 "status":"translated","source":"fan","tm":tm},open('/mnt/user-data/outputs/en/68_tutorials.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(tm),'problems',prob)
