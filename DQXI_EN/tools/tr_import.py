#!/usr/bin/env python3
"""Import translations from text/en/*.json into the progress DB.

File format (UTF-8 JSON):
  {"status": "translated",                      # default status for this file
   "source": "fan",                             # fan | official | name
   "tm": {"<japanese>": "<english>", ...},      # translation memory: applies to EVERY string
                                                #  whose Japanese (furigana stripped) matches
   "id": {"<string id>": "<english>", ...}}     # context-specific, overrides tm
Japanese keys are compared after removing {ruby:..|..} readings, so "冒険の書" matches
"{ruby:冒険|ぼうけん}の{ruby:書|しょ}".  English may contain \\n, {var:N}, {x:XXXX}.
Usage: tr_import.py <project_dir>
"""
import os, sys, json, re, sqlite3, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_dump import SCHEMA

RUBY = re.compile(r'\{ruby:([^|{}]*)\|[^{}]*\}')
def norm(jp): return RUBY.sub(r'\1', jp)

def main():
    proj = sys.argv[1]
    db = sqlite3.connect(os.path.join(proj, 'db', 'progress.sqlite'))
    db.executescript(SCHEMA)
    try: db.execute('ALTER TABLE strings ADD COLUMN jp_norm TEXT')
    except sqlite3.OperationalError: pass
    db.execute('CREATE INDEX IF NOT EXISTS strings_jpn ON strings(jp_norm)')
    rows = db.execute('select id,jp from strings where jp_norm is null').fetchall()
    db.executemany('update strings set jp_norm=? where id=?', [(norm(j), i) for i, j in rows])
    ntm = nid = 0; missing = []
    for fn in sorted(glob.glob(os.path.join(proj, 'text', 'en', '*.json'))):
        d = json.load(open(fn, encoding='utf-8'))
        st = d.get('status', 'translated'); src = d.get('source', 'fan')
        for jp, en in d.get('tm', {}).items():
            k = norm(jp)
            db.execute('INSERT INTO tm(jp,en,source,status) VALUES(?,?,?,?) ON CONFLICT(jp) DO UPDATE SET '
                       'en=excluded.en, source=excluded.source, status=excluded.status', (k, en, src, st))
            hit = db.execute("update strings set status=? where jp_norm=? and status in ('untranslated','translated') and (en is null or en='')", (st, k)).rowcount
            if not hit: missing.append((os.path.basename(fn), k))
            ntm += 1
        for sid, en in d.get('id', {}).items():
            c = db.execute('update strings set en=?, status=? where id=?', (en, st, sid)).rowcount
            if not c: missing.append((os.path.basename(fn), sid))
            nid += 1
    db.commit()
    print('imported tm=%d id=%d' % (ntm, nid))
    for f, k in missing[:50]: print('  WARN no string matches', f, repr(k[:60]))
    if len(missing) > 50: print('  ... %d more' % (len(missing) - 50))

if __name__ == '__main__':
    main()
