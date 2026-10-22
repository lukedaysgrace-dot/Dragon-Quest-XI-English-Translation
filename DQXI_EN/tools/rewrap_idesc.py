#!/usr/bin/env python3
"""Pre-wrap item descriptions in text/en/64_item_desc.json with explicit \n (the game wraps by character, splitting words)."""
import sys,json,os,tempfile
sys.path.insert(0,'/home/claude/tools')
import wrap,font_patch
d=tempfile.mkdtemp()
for n in ('3D12','3D14','2D14','2D9','2D14SH'):
    p=f'/home/claude/work/ext/romfs/font/{n}.bffnt'
    if os.path.exists(p):
        data,_=font_patch.patch(n,p); open(d+f'/{n}.bffnt','wb').write(data)
M=wrap.Metrics(d)
SPEC=[('3D12',124),('2D14',115)]
SH=json.load(open('/home/claude/maps/idesc_short.json',encoding='utf-8')) if os.path.exists('/home/claude/maps/idesc_short.json') else {}
p='/home/claude/text/en/64_item_desc.json'
t=json.load(open(p,encoding='utf-8'))
bad=[]
for k,v in t['tm'].items():
    flat=v.replace('\n',' ')
    flat=SH.get(flat,flat)
    L=wrap.wrap(M,flat,SPEC)
    if len(L)>3: bad.append(L)
    t['tm'][k]='\n'.join(L)
json.dump(t,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('rewrapped',len(t['tm']),'still >3 lines:',len(bad))
for L in bad: print(' ',' / '.join(L))
