#!/usr/bin/env python3
"""Add Japanese text found in UI layouts (SARC -> BFLYT txt1 panes) to the progress DB.
id = "<pack>|<arc>|<bflyt>|<pane>"   btype = "LYT"
Placeholder panes (text overwritten at runtime: 'ああああ', test strings) are stored with status 'skip'.
Usage: lyt_dump.py <romfs_dir> <project_dir>
"""
import os, sys, re, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack import Pack
from sarc import Sarc
import lyt, textcodec as tc
from text_dump import SCHEMA

REAL_WORDS = {'いいえ', 'たたく', 'け付け', 'アジア'}   # short real words that look like filler

def is_placeholder(t):
    core = re.sub(r'[\s　\n]', '', t)
    if not core: return True
    if core in REAL_WORDS: return False
    if len(set(core)) <= 2 and len(core) >= 3: return True
    if 'テスト' in t or 'ダミー' in t or 'にしのしま' in t: return True
    return False

def iter_layouts(root):
    for dp, dn, fn in os.walk(os.path.join(root, 'ui')):
        for f in sorted(fn):
            if not f.endswith('.pack'): continue
            rel = '/' + os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/')
            pk = Pack(os.path.join(dp, f))
            for e in pk.entries:
                if e['data'][:4] != b'SARC': continue
                s = Sarc(e['data'])
                for fl in s.files:
                    if fl['name'] and fl['name'].endswith('.bflyt'):
                        yield rel, e['name'], fl['name'], fl['data']

def main():
    root, proj = sys.argv[1], sys.argv[2]
    db = sqlite3.connect(os.path.join(proj, 'db', 'progress.sqlite'))
    db.executescript(SCHEMA)
    n = 0
    for rel, arc, fl, d in iter_layouts(root):
        fonts = lyt.fonts(d)
        for p in lyt.text_panes(d):
            t = p['text']
            if not tc.has_japanese(t): continue
            sid = '%s|%s|%s|%s' % (rel, arc, fl, p['name'])
            fnt = fonts[p['font']] if p['font'] < len(fonts) else '?'
            note = 'w=%.0f h=%.0f font=%s fs=%.0f buf=%d' % (p['w'], p['h'], fnt, p['fs'][0], p['buf'])
            st = 'skip' if is_placeholder(t) else 'untranslated'
            db.execute("INSERT INTO strings(id,pack,entry,btype,off,nl,jp,status,note) VALUES(?,?,?,?,?,?,?,?,?) "
                       "ON CONFLICT(id) DO UPDATE SET jp=excluded.jp, note=excluded.note",
                       (sid, rel, arc + '|' + fl, 'LYT', 0, 'lf', t, st, note))
            n += 1
    db.commit()
    print('layout strings', n, 'non-placeholder',
          db.execute("select count(*), count(distinct jp) from strings where btype='LYT' and status!='skip'").fetchone())

if __name__ == '__main__':
    main()
