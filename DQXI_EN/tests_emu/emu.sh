#!/bin/bash
# helper: xvfb|start [rom]|stop|shot <file>|key <keys...>|hold <key> <secs>|log [n]
export DISPLAY=:99
U=$HOME/.local/share/azahar-emu
case "$1" in
  xvfb) pgrep -x Xvfb >/dev/null || (setsid nohup Xvfb :99 -screen 0 1280x960x24 >/tmp/xvfb.log 2>&1 < /dev/null &); sleep 1;;
  start) pkill -9 -f squashfs-root/AppRun; sleep 2
         cd /home/claude/azahar/squashfs-root && LIBGL_ALWAYS_SOFTWARE=1 setsid nohup ./AppRun "${2:-/home/claude/rom/dqxi.3ds}" >/tmp/azahar.out 2>&1 < /dev/null & ;;
  stop) pkill -9 -f squashfs-root/AppRun;;
  shot) import -window root "${2:-/tmp/shot.png}";;
  key) shift; xdotool mousemove 640 400 click 1 2>/dev/null; sleep 0.2; for k in "$@"; do xdotool keydown $k; sleep 0.15; xdotool keyup $k; sleep 0.35; done;;
  hold) xdotool mousemove 640 400 click 1 2>/dev/null; sleep 0.2; xdotool keydown $2; sleep $3; xdotool keyup $2;;
  hold2) xdotool mousemove 640 400 click 1 2>/dev/null; sleep 0.2; xdotool keydown $2 keydown $3; sleep $4; xdotool keyup $2 keyup $3;;
  log) tail -n ${2:-30} $U/log/azahar_log.txt;;
esac
