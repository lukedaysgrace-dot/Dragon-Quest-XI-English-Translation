#!/bin/bash
# press A (except first loop) until the battle main menu (Fight/Tactics/Switch/Flee) is up; max 15 tries
for i in $(seq 1 15); do
  /home/claude/emu/snap.sh z
  r=$(python3 -c "
from PIL import Image
im=Image.open('/home/claude/emu/shots/z.png').convert('RGB')
# main menu box left at x~30-95,y~165-230 has black bg with white frame; message box spans to x 375
a=sum(1 for x in range(110,370) for y in range(168,226) if sum(im.getpixel((x,y)))<60)
b=sum(1 for x in range(32,96) for y in range(168,226) if sum(im.getpixel((x,y)))<60)
w=sum(1 for x in range(40,60) for y in range(170,180) if sum(im.getpixel((x,y)))>600)
print(1 if (b>2500 and w>5 and a<9000) else 0)")
  [ "$r" = 1 ] && { echo menu; exit 0; }
  /home/claude/emu/emu.sh key a; sleep 2.2
done; echo nomenu
