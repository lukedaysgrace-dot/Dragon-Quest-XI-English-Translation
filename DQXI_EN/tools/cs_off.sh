#!/bin/bash
# cs_off.sh pack... : run and print offender src lines (offset + text)
cd /home/claude
for k in "$@"; do
 bash tools/go.sh cs_$k 30_cs_$k 2>&1 | grep -o "cs_text.bxon|[0-9a-f]*|\|bxon|[0-9a-f]*\| \['" >/dev/null
 bash tools/go.sh cs_$k 30_cs_$k 2>&1 | grep "lines >\|too wide" | sed -E 's/.*\|([0-9a-f]+) .*/\1/' | sort -u | while read o; do grep -E "^$o( [0-9a-f]+)* f: " /tmp/cs/$k.src | sed "s|^|$k |"; done
done
