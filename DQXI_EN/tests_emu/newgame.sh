#!/bin/bash
# fresh boot -> new adventure log slot 1 -> name "Alex" -> confirm
E=/home/claude/emu/emu.sh
$E xvfb; $E stop; sleep 1; rm -rf ~/.local/share/azahar-emu/sdmc/Nintendo*/*/*/title/00040000/00199200/data 2>/dev/null
$E start; sleep 45
for i in 1 2 3 4; do $E key a; sleep 3; done
$E key a; sleep 3     # slot 1 -> keyboard
$E key a; sleep 1     # types A
python3 /home/claude/emu/type_name.py lex
$E key g h h a; sleep 2   # End
$E key a; sleep 20        # Yes
