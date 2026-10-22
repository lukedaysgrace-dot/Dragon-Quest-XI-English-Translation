#!/usr/bin/env python3
# misc_fill.py: frozen maps/src_small/misc_jp.txt ("N Btype | jp") + misc_en.txt ("N|English") -> text/en/119_misc_fan.json
import re,json
jp={}
for l in open('/home/claude/DQXI_EN/maps/src_small/misc_jp.txt',encoding='utf-8'):
    m=re.match(r'(\d+) \S+ \| (.*)',l.rstrip('\n'))
    if m: jp[int(m.group(1))]=m.group(2).replace('⏎','\n').replace('_','\u3000')
en={}
for l in open('/home/claude/DQXI_EN/maps/src_small/misc_en.txt',encoding='utf-8'):
    m=re.match(r'(\d+)\|(.*)',l.rstrip('\n'))
    if m: en[int(m.group(1))]=m.group(2).replace('\\n','\n')
out={jp[n]:e for n,e in en.items()}
json.dump({'_comment':'misc leftovers','status':'translated','source':'fan','tm':out},open('/home/claude/DQXI_EN/text/en/119_misc_fan.json','w'),ensure_ascii=False,indent=0)
print('wrote',len(out),'of',len(jp))
