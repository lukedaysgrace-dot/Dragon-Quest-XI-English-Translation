#!/bin/bash
# clone_all.sh <omap name> <out prefix> [entry]  : clone a common_2d omap to common_2way and common_3d
cd /home/claude
for p in common_2way common_3d; do
  python3 tools/clone_map.py maps/$1.omap maps/$1_$p.omap $p $3 || continue
  bash tools/go.sh ${1}_$p ${2}_$p 2>&1 | tail -2
done
