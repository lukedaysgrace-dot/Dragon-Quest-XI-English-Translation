#!/bin/bash
# from boot: load save, go up Cobblestone Tor to the first slime battle
E=/home/claude/emu/emu.sh; M=/home/claude/emu/mv.sh; S=/home/claude/emu/snap.sh
/home/claude/emu/boot_save.sh >/dev/null 2>&1
/home/claude/emu/to_green.sh 500
for i in $(seq 1 30); do $E key a; sleep 2.5; done
$S tb1
$M "t 3" "h 3" "g 1.2" "h 3" "g 0.8" "h 2" "t 3" "h 1" "t 4" "h 2.5" "g 1.5" "h 3"
for i in $(seq 1 24); do $E key a; sleep 2.5; done
$S tb2
$M "t 0.6" "h 0.6" "g 0.45" "h 4"
for i in 1 2 3 4; do $E key a; sleep 2.5; done
$M "t 3"
sleep 3; for i in $(seq 1 22); do $E key a; sleep 2.5; done
$S tb3
$M "h 1.5" "t 2" "h 1.2" "t 3" "t 3"
sleep 10; for i in 1 2 3 4 5 6; do $E key a; sleep 2.5; done
sleep 6; $S tb4
echo done > /tmp/tb.done
