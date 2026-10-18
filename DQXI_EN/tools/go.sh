#!/bin/bash
# go.sh <omap name> <out prefix>   e.g. go.sh cob_cs 51b_cobblestone_cs
set -e
cd /home/claude
DQXI_FONTS=/home/claude/work/build/romfs/font python3 tools/omap2json.py maps/$1.omap work/proj/db/progress.sqlite official/rows.jsonl text/en/$2
F=$(ls text/en/$2_*.json)
DQXI_CONDENSE=0.92 python3 tools/check_fit.py work/proj/db/progress.sqlite work/build/romfs/font $F
