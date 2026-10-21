#!/bin/bash
# lenchk.sh src... : show dialogue lines longer than 100 chars (likely >3 windows lines)
for f in "$@"; do awk -v F="$f" '/ f: "/ { t=$0; sub(/^[0-9a-f ]+ f: /,"",t); if (length(t)>101) print F": "length(t)": "substr(t,1,60) }' "$f"; done
