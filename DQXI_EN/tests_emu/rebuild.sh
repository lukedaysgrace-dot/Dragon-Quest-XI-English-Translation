#!/bin/bash
# rebuild patch (romfs + code.ips) and install into the cloud Azahar mods folder
set -e
cd /home/claude/work
python3 /home/claude/tools/tr_import.py proj > /tmp/tr_import.log 2>&1 || { tail -5 /tmp/tr_import.log; exit 1; }; head -1 /tmp/tr_import.log
rm -rf build tex
python3 /home/claude/tools/make_textures.py ext/romfs ext/romfs/font maps tex
DQXI_TEX_DIR=/home/claude/work/tex DQXI_CONDENSE=0.92 python3 /home/claude/tools/build_patch.py ext/romfs proj build --all-layouts 2>&1 | tail -1
python3 /home/claude/tools/verify_build.py ext/romfs build 2>&1 | tail -1
python3 /home/claude/tools/code_patch.py code_dec.bin maps/code_strings.tsv build_code | tail -1
mkdir -p build/exefs && cp build_code/code.ips build/exefs/
M=~/.local/share/azahar-emu/load/mods/0004000000199200
rm -rf $M && mkdir -p $M && cp -r build/romfs build/exefs $M/
echo installed
