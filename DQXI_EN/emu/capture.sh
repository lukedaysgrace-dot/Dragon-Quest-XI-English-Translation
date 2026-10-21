#!/bin/bash
# capture.sh <seconds interval> <count>: save full-root screenshots to emu/shots/s7
export DISPLAY=:99
for i in $(seq 1 $2); do import -window root /home/claude/emu/shots/s7/f$(printf %03d $i).png 2>/dev/null; sleep $1; done
