#!/usr/bin/env python3
# party_fill.py : builds text/en/116_party_fan.json from the FROZEN list maps/src_small/party_jp_all.txt
# and maps/src_small/party_en.txt ("N|English"; later lines override). Do NOT use unc.py --fill for this:
# unc.py numbering shifts once tr_import has loaded earlier batches into the DB.
import re,json,sqlite3,glob,sys
R='/home/claude/DQXI_EN/'
jp={}
for l in open(R+'maps/src_small/party_jp_all.txt',encoding='utf-8'):
    m=re.match(r'(\d+) \S+ \S+ \| (.*)',l.rstrip('\n'))
    if m: jp[int(m.group(1))]=m.group(2).replace('⏎','\n').replace('_','\u3000')
en={}
for l in open(R+'maps/src_small/party_en.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if not l.strip() or l.startswith('#'): continue
    n,e=l.split('|',1); en[int(n)]=e.replace('\\n','\n')
out={jp[n]:e for n,e in en.items()}
fn=R+'text/en/116_party_fan.json'
old={}
try: old=json.load(open(fn,encoding='utf-8')).get('tm',{})
except Exception: pass
json.dump({'_comment':'party chat (TalkPartyContent2), numbering frozen in maps/src_small/party_jp_all.txt','status':'translated','source':'fan','tm':out},open(fn,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
print('wrote',len(out),'of',len(jp))
# purge stale pairs from the DB tm table
bad=[k for k in old if k not in out]
if bad:
    covered=set()
    for f in glob.glob(R+'text/en/*.json'):
        if f==fn: continue
        try: covered|=set(json.load(open(f,encoding='utf-8')).get('tm',{}))
        except Exception: pass
    db=sqlite3.connect('/home/claude/work/proj/db/progress.sqlite'); n=0
    for k in bad:
        if k in covered: continue
        db.execute('delete from tm where jp=?',(k,))
        n+=db.execute("update strings set status='untranslated' where jp_norm=? and status='translated' and (en is null or en='')",(k,)).rowcount
    db.commit(); print('purged',len(bad),'stale keys; strings reset',n)
