#!/bin/bash
# cs_run.sh <entry> <prefix> pack...   (entry e.g. cs_text.bxon). Expands /tmp/cs/<pack>.src against /tmp/cs/<pack>.txt, builds, reports offenders.
cd /home/claude
E=$1; P=$2; shift 2
for k in "$@"; do
  python3 tools/expand.py /tmp/cs/$k.txt /tmp/cs/$k.src maps/${P}_$k.omap
  out=$(bash tools/go.sh ${P}_$k 30_${P}_$k 2>&1)
  echo "== $k $(echo "$out" | tail -1)"
  echo "$out" | grep -A5 "lines >\|too wide" | awk '!s[$0]++'
done
