#!/usr/bin/env python3
# term.py JP1 JP2 ...  -> exact-key lookup in text/en tm (names, items, monsters, places)
import json,glob,sys
tm={}
for f in sorted(glob.glob('/home/claude/text/en/*.json')):
    try: tm.update(json.load(open(f)).get('tm',{}))
    except: pass
for t in sys.argv[1:]:
    r=[(k,v) for k,v in tm.items() if t in k and len(k)<=len(t)+6]
    print(t,'=>',[(k,v) for k,v in r][:3] if r else '??')
