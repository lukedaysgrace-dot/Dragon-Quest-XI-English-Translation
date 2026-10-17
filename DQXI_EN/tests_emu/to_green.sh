#!/bin/bash
# press A every ~15s until 2D field map (green) shows on bottom screen; max $1 s
E=/home/claude/emu/emu.sh; S=/home/claude/emu/snap.sh; end=$((SECONDS+${1:-600}))
while [ $SECONDS -lt $end ]; do
  $S poll; g=$(python3 -c "
from PIL import Image
im=Image.open('/home/claude/emu/shots/poll.png').convert('RGB').crop((40,250,360,470)).resize((32,22))
print(sum(1 for r,g,b in im.get_flattened_data() if g>r+30 and g>b+30))")
  [ "$g" -gt 300 ] && { echo green; exit 0; }
  $E key a; sleep 12
done; echo timeout
