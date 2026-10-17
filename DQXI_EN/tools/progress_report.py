#!/usr/bin/env python3
"""Translation coverage report from the progress DB (Markdown to stdout, CSV export optional).
Usage: progress_report.py <project_dir> [--csv out.csv]
A string counts as covered when it has its own English (status translated/reviewed/tested)
or its Japanese (furigana stripped) is in the translation memory."""
import os, sys, re, sqlite3, csv, collections
RUBY = re.compile(r'\{ruby:([^|{}]*)\|[^{}]*\}')

def main():
    proj = sys.argv[1]
    db = sqlite3.connect(os.path.join(proj, 'db', 'progress.sqlite'))
    tm = {jp for (jp,) in db.execute("select jp from tm where en is not null and en!=''")}
    agg = collections.defaultdict(lambda: [0, 0, 0, 0])   # total, covered, unique, unique covered
    seen = collections.defaultdict(set)
    rows = db.execute("select id,btype,jp,en,status from strings where status!='skip'").fetchall()
    out = []
    for sid, bt, jp, en, st in rows:
        n = RUBY.sub(r'\1', jp)
        cov = bool(en and st in ('translated', 'reviewed', 'tested')) or n in tm
        a = agg[bt]; a[0] += 1; a[1] += cov
        if n not in seen[bt]:
            seen[bt].add(n); a[2] += 1; a[3] += cov
        out.append((sid, bt, st if cov else 'untranslated'))
    tot = [sum(v[i] for v in agg.values()) for i in range(4)]
    print('| data type | strings | covered | unique JP | unique covered | % |')
    print('|---|---:|---:|---:|---:|---:|')
    for bt, v in sorted(agg.items(), key=lambda x: -x[1][0]):
        print('| %s | %d | %d | %d | %d | %.1f%% |' % (bt, v[0], v[1], v[2], v[3], 100.0 * v[1] / max(1, v[0])))
    print('| **total** | %d | %d | %d | %d | %.1f%% |' % (tot[0], tot[1], tot[2], tot[3], 100.0 * tot[1] / max(1, tot[0])))
    st = dict(db.execute('select status,count(*) from strings group by status').fetchall())
    print('\nDB status column: ' + ', '.join('%s=%d' % kv for kv in sorted(st.items())))
    if '--csv' in sys.argv:
        with open(sys.argv[sys.argv.index('--csv') + 1], 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(['id', 'type', 'state']); w.writerows(out)

if __name__ == '__main__':
    main()
