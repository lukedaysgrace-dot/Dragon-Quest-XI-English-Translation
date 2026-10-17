#!/bin/bash
# snap.sh <name> : screenshot of the emulator screens only
/home/claude/emu/emu.sh shot /tmp/full.png
python3 -c "
from PIL import Image
Image.open('/tmp/full.png').crop((440,236,840,716)).save('/home/claude/emu/shots/$1.png')"
