#!/bin/bash
# mv.sh "Dir secs" ... ; then snap 2D map crop to shots/mv.png
E=/home/claude/emu/emu.sh
for a in "$@"; do $E hold $a; done; sleep 1.5
/home/claude/emu/snap.sh mvfull
python3 -c "
from PIL import Image
im=Image.open('/home/claude/emu/shots/mvfull.png'); im.resize((200,240)).save('/home/claude/emu/shots/mv.png')"
