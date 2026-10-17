#!/bin/bash
# helper: xvfb|start [rom]|stop|shot <file>|key <keys...>|hold <key> <secs>|log [n]
export DISPLAY=:99
U=$HOME/.local/share/azahar-emu
case "$1" in
  xvfb) pgrep -x Xvfb >/dev/null || (setsid nohup Xvfb :99 -screen 0 1280x960x24 >/tmp/xvfb.log 2>&1 < /dev/null &); sleep 1;;
  start) pkill -x azahar; sleep 1
         cd /home/claude/azahar/squashfs-root && LIBGL_ALWAYS_SOFTWARE=1 setsid nohup ./AppRun "${2:-/home/claude/rom/dqxi.3ds}" >/tmp/azahar.out 2>&1 < /dev/null & ;;
  stop) pkill -x azahar;;
  shot) import -window root "${2:-/tmp/shot.png}";;
  key) shift; W=$(xdotool search --name "Azahar" | tail -1); xdotool windowactivate --sync $W 2>/dev/null; for k in "$@"; do xdotool keydown $k; sleep 0.15; xdotool keyup $k; sleep 0.35; done;;
  hold) W=$(xdotool search --name "Azahar" | tail -1); xdotool windowactivate $W 2>/dev/null; xdotool keydown $2; sleep $3; xdotool keyup $2;;
  log) tail -n ${2:-30} $U/log/azahar_log.txt;;
esac
