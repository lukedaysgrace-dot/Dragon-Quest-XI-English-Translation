import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from _paths import TOOLS, FONTS, DB, ROWS
import sys, json
sys.path.insert(0,TOOLS); import wrap
M=wrap.Metrics(FONTS)
SPEC=[('3D14',330/0.92)]
jp=[l.rstrip('\n') for l in open('maps/story_jp.txt',encoding='utf8')]
tm={}; bad=[]
for l in open('maps/story_en.txt',encoding='utf8'):
    i,e=l.rstrip('\n').split('=',1)
    lines=wrap.wrap(M,e,SPEC)
    if len(lines)>5: bad.append((i,len(lines)))
    tm[jp[int(i)-1].replace('⏎','\n')]='\n'.join(lines)
json.dump({"_comment":"Story-so-far recaps (gamecmn story_*.bxon), fan translation, 5 lines max.","status":"translated","source":"fan","tm":tm},
 open('/mnt/user-data/outputs/en/73_story_recap.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(tm),bad, max(len(v) for v in tm.values()))
