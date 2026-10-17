#!/bin/bash
# state.sh save|load <slot 1-10>
export DISPLAY=:99
if [ "$1" = save ]; then y0=341; else y0=318; fi
xdotool mousemove 286 224 click 1; sleep 1; xdotool mousemove 312 $y0; sleep 1
xdotool mousemove 600 $y0; sleep 0.4
if [ "$1" = save ]; then y=$((389+23*($2-1))); else y=$((366+23*($2-1))); fi
xdotool mousemove 600 $y click 1; sleep 5
