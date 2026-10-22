#!/usr/bin/env python3
# mksave.py -> builds test save Data0 with quests/titles/monsters unlocked (from Data0.orig). Stop emulator first.
import zlib,struct,shutil,os,glob,sys
D=glob.glob(os.path.expanduser('~/.local/share/azahar-emu/sdmc/Nintendo 3DS/*/*/title/00040000/00199200/data/00000001'))[0]
src=D+'/Data0.orig'
if not os.path.exists(src): shutil.copy(D+'/Data0',src)
b=bytearray(open(src,'rb').read())
nq=len([l for l in open('/home/claude/saveed/repo/item/quest.txt',encoding='utf-8') if l.strip() and l[0]!='#'])
for i in range(nq):
    b[0x6F65+i]= 2 if i%5==0 else (9 if i%2 else 8)   # mix: in progress / complete / cleared
for i in range(0x6764,0x6764+30): b[i]=0xFF
b[0x6764+30]=0x07          # titles 265 bits
for i in range(948): b[0x78E4+i*4:0x78E4+i*4+4]=struct.pack('<I',7)  # monsters defeated
def ids(f):
    r=[]
    for l in open('/home/claude/saveed/repo/item/'+f,encoding='utf-8'):
        if l.strip() and l[0]!='#':
            a=l.split('\t')[0]
            r.append(int(a,16) if a.startswith('0x') else int(a))
    return r
for i,t in enumerate(ids('tool.txt')[:168]): b[0x3E34+i*4:0x3E34+i*4+4]=struct.pack('<HH',t,9)
for i,t in enumerate(ids('equipment.txt')[:2340]): b[0x40EC+i*4:0x40EC+i*4+4]=struct.pack('<HH',t,1)
b[0x10]=40; b[0x14:0x18]=struct.pack('<I',60000)   # hero level/exp
b[0xC8AC:0xC8B0]=struct.pack('<I',zlib.crc32(bytes(b[:0xC8A8]))&0xffffffff) 
open(D+'/Data0','wb').write(b); print('ok',len(b),nq)
