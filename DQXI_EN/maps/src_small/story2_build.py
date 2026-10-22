#!/usr/bin/env python3
# story2_build.py : maps/src_small/story2_jp.txt (frozen list) + story2_en.txt ("N=English") -> text/en/115_story2_fan.json (wrapped, <=5 lines)
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0,'/home/claude/tools'); import wrap
M=wrap.Metrics('/home/claude/work/ext/romfs/font') if False else None
from _paths import FONTS
M=wrap.Metrics(FONTS)
SPEC=[('3D14',330/0.92)]
H=os.path.dirname(os.path.abspath(__file__))
jp=[l.rstrip('\n') for l in open(H+'/story2_jp.txt',encoding='utf8')]
tm={}; bad=[]
EN={}
for l in open(H+'/story2_en.txt',encoding='utf8'):
    l=l.rstrip('\n')
    if not l.strip() or l.startswith('#'): continue
    i,e=l.split('=',1); EN[int(i)]=e
for i,e in sorted(EN.items()):
    lines=wrap.wrap(M,e,SPEC)
    if len(lines)>5: bad.append((i,len(lines),len(e)))
    tm[jp[i-1].replace('⏎','\n')]='\n'.join(lines)
json.dump({"_comment":"Story-so-far recaps 2 (gamecmn story_*.bxon, a100+), fan translation, 5 lines max.","status":"translated","source":"fan","tm":tm},
 open('/home/claude/DQXI_EN/text/en/115_story2_fan.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(tm),'of',len(jp),'bad(>5 lines):',bad)
