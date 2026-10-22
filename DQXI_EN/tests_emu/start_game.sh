#!/bin/bash
# boot -> Continue slot (arg1: number of 'g' presses to select slot, default 2 => slot 3) -> mash intro -> Tor route
export DISPLAY=:99
E=/home/claude/emu/emu.sh
$E xvfb; $E start; sleep 50
for i in 1 2 3; do $E key a; sleep 4; done     # title, menu, Continue
for i in $(seq 1 ${1:-2}); do $E key g; done; $E key a; sleep 5   # slot
$E key a; sleep 4; $E key a; sleep 4           # story so far
for i in $(seq 1 100); do $E key a >/dev/null; sleep 4; done   # intro -> Tor
echo intro > /tmp/start.state
