#!/bin/bash
for i in $(seq 1 110); do [ -f /tmp/nav.done ] && { cat /tmp/nav.out; exit 0; }; sleep 1; done; echo still-running; cat /tmp/nav.out
