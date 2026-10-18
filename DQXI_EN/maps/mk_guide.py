import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from _paths import TOOLS, FONTS, DB, ROWS
import sys, json, glob
sys.path.insert(0,TOOLS)
import wrap
M=wrap.Metrics(FONTS)
SPEC=[('3D14',290)]
tm={}; bad=[]
for f in sorted(glob.glob('maps/guide*.txt')):
    for l in open(f,encoding='utf8'):
        l=l.rstrip('\n')
        if '=' not in l: continue
        j,e=l.split('=',1)
        lines=wrap.wrap(M,e,SPEC)
        if len(lines)>2: bad.append(lines)
        tm[j.replace('⏎','\n')]='\n'.join(lines)
json.dump({"_comment":"Bottom-screen objective hints (gamecmn scenario_guide.bxon). Fan translation; place names follow the official localisation where known.",
 "status":"translated","source":"fan","tm":tm},open('text/en/65_scenario_guide.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(tm),'over2',len(bad))
for b in bad: print(b)
