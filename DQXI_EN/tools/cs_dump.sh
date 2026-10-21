#!/bin/bash
# cs_dump.sh <entry> pack...  -> dumps to /tmp/cs/<pack>.txt and prints them without # header lines
cd /home/claude; E=$1; shift
for k in "$@"; do python3 tools/dump2.py $k $E > /tmp/cs/$k.txt; echo "### $k"; grep -v '^#' /tmp/cs/$k.txt; done
