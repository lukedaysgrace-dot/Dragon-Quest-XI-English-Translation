#!/usr/bin/env python3
"""Check translation json files against the dialogue window limits (3 lines, pixel widths).
Usage: check_fit.py <db> <font_dir> <file.json>...   -> prints id, problems, wrapped text"""
import sys, os, json, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wrap
from build_patch import fix_chars

def main():
    db = sqlite3.connect(sys.argv[1]); m = wrap.Metrics(sys.argv[2]); bad = 0
    for fn in sys.argv[3:]:
        d = json.load(open(fn, encoding='utf-8'))
        for sid, en in d.get('id', {}).items():
            r = db.execute('select btype, jp from strings where id=?', (sid,)).fetchone()
            if not r: print('MISSING', sid); continue
            text, probs = wrap.layout(m, fix_chars(en), r[0], r[1])
            if probs:
                bad += 1; print(sid, probs); print('   ' + text.replace('\n', '\n   '))
    print('problems:', bad)

if __name__ == '__main__':
    main()
