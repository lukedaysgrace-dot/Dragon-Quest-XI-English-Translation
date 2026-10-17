#!/bin/bash
# run nav.py walk in background; result in /tmp/nav.out, done flag /tmp/nav.done
rm -f /tmp/nav.done
(setsid nohup bash -c "python3 /home/claude/emu/nav.py walk $* > /tmp/nav.out 2>&1; /home/claude/emu/snap.sh nav; touch /tmp/nav.done" < /dev/null > /dev/null 2>&1 &)
