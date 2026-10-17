#!/bin/bash
# boot game fresh and load in-game save slot 1 (skips recap). Leaves game at Tor start.
E=/home/claude/emu/emu.sh; S=/home/claude/emu/snap.sh
$E xvfb; $E start; sleep 40
for i in 1 2 3; do $E key a; sleep 4; done   # title -> menu
$E key a; sleep 4        # continue adventure
$E key a; sleep 4        # slot 1
$E key g; sleep 1; $E key a; sleep 25   # "view story so far?" -> No
$S boot
echo done > /tmp/boot.done
