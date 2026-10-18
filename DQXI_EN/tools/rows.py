#!/usr/bin/env python3
# rows.py <file-substring> <start> <count>   (start = index within that file)  | rows.py -g <regex> [file-substring]
import json, sys, re
R=[json.loads(l) for l in open('/home/claude/official/rows.jsonl')]
if sys.argv[1]=='-g':
    rx=re.compile(sys.argv[2],re.I); fs=sys.argv[3] if len(sys.argv)>3 else ''
    for i,r in enumerate(R):
        t=' / '.join(r['pages'])
        if fs in r['file'] and rx.search(t): print(i, r['file'][:14], r['section'][:30], '|', t[:300])
    sys.exit()
fs=sys.argv[1]; a=int(sys.argv[2]); n=int(sys.argv[3])
L=[(i,r) for i,r in enumerate(R) if fs in r['file']]
sec=None
for i,r in L[a:a+n]:
    if r['section']!=sec: sec=r['section']; print('##',sec)
    print(i, (r['speaker']+': ' if r['speaker'] else '')+' ¶ '.join(r['pages']))
