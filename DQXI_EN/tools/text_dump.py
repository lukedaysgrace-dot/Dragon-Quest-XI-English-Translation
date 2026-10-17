#!/usr/bin/env python3
"""Dump every message string of the game into editable UTF-8 JSON + a SQLite progress DB.

Usage: text_dump.py <extracted_romfs_dir> <project_dir>
Writes:
  <project>/text/jp/<pack path>.json    one file per .pack: {entry: {type, strings:[{id,off,nl,jp,refs}]}}
  <project>/db/progress.sqlite          table strings + table tm (unique Japanese -> English)
String id = "<pack path>|<entry name>|<hex offset of string in the ORIGINAL bxon>".
Re-running is safe: existing translations/status in the DB are kept.
"""
import os, sys, json, sqlite3, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack import Pack
from bxon import Bxon
import textcodec as tc

SKIP = ('/sound', '/movie', '/3d/model', '/3d/motion', '/2d/model', '/2d/battle2', '/2d/bg', '/3d/bg', '/effect', '/level2d', '/level3d')

SCHEMA = '''
CREATE TABLE IF NOT EXISTS strings(
  id TEXT PRIMARY KEY, pack TEXT, entry TEXT, btype TEXT, off INTEGER, nl TEXT,
  jp TEXT, en TEXT, status TEXT DEFAULT 'untranslated', note TEXT, seq INTEGER);
CREATE INDEX IF NOT EXISTS strings_jp ON strings(jp);
CREATE INDEX IF NOT EXISTS strings_pack ON strings(pack);
-- status: untranslated | translated | reviewed | tested | skip
CREATE TABLE IF NOT EXISTS tm(jp TEXT PRIMARY KEY, en TEXT, source TEXT, status TEXT);
-- source: official (user-supplied localization) | fan (this project) | name (glossary)
'''

def iter_packs(root):
    for dp, dn, fn in os.walk(root):
        rel = dp[len(root):].replace(os.sep, '/')
        if rel.startswith(SKIP): continue
        for f in sorted(fn):
            if f.endswith('.pack'): yield rel + '/' + f, os.path.join(dp, f)

def main():
    root = os.path.abspath(sys.argv[1]); proj = sys.argv[2]
    os.makedirs(os.path.join(proj, 'db'), exist_ok=True)
    db = sqlite3.connect(os.path.join(proj, 'db', 'progress.sqlite'))
    db.executescript(SCHEMA)
    total = 0; seq = 0
    for rel, path in iter_packs(root):
        try:
            pk = Pack(path)
        except Exception as ex:
            print('WARN cannot parse', rel, ex); continue
        out = {}
        for e in pk.entries:
            if e['data'][:4] != b'BXON': continue
            b = Bxon(e['data'])
            lst = []
            for off, u in b.string_list():
                if not tc.is_text(u) or not u: continue
                nl = tc.detect_nl(u)
                jp = tc.decode(u, nl)
                if not tc.has_japanese(jp): continue
                sid = '%s|%s|%x' % (rel, e['name'], off)
                lst.append({'id': sid, 'off': off, 'nl': nl, 'jp': jp})
                seq += 1
                db.execute('INSERT INTO strings(id,pack,entry,btype,off,nl,jp,seq) VALUES(?,?,?,?,?,?,?,?) '
                           'ON CONFLICT(id) DO UPDATE SET jp=excluded.jp, nl=excluded.nl, seq=excluded.seq',
                           (sid, rel, e['name'], b.typename, off, nl, jp, seq))
            if lst:
                out[e['name']] = {'type': b.typename, 'strings': lst}
                total += len(lst)
        if out:
            dst = os.path.join(proj, 'text', 'jp', rel.lstrip('/') + '.json')
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'w', encoding='utf-8') as f:
                json.dump({'pack': rel, 'entries': out}, f, ensure_ascii=False, indent=1)
    db.commit()
    u = db.execute('select count(distinct jp) from strings').fetchone()[0]
    print('strings', total, 'unique', u)

if __name__ == '__main__':
    main()
