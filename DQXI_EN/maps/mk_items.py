import sqlite3, json, collections
m={}
for f in ['maps/items1.txt','maps/items2.txt','maps/items3.txt','maps/items4.txt','maps/items_short.txt']:
    for l in open(f,encoding='utf8'):
        l=l.rstrip('\n')
        if '=' in l: j,e=l.split('=',1); m[j]=e
db=sqlite3.connect('proj/db/progress.sqlite')
variants=collections.defaultdict(set)
for (jn,) in db.execute("select distinct jp_norm from strings where entry='item.bxon'"):
    k=jn.replace('\n','')
    if k in m: variants[k].add(jn)
# also exact unbroken name anywhere
def brk(en):
    if len(en)<=12 or ' ' not in en: return en
    sp=[i for i,c in enumerate(en) if c==' ']
    i=min(sp,key=lambda i:abs(i-len(en)/2))
    return en[:i+1]+'\n'+en[i+1:]
tm={}
for k,en in m.items():
    tm[k]=en
    for v in variants[k]:
        tm[v]=brk(en) if '\n' in v else en
json.dump({"_comment":"Item names (syscmn item.bxon). Official-style naming where known (series standard), otherwise fan renderings. Names that are line-broken in JP get 'A \\nB' (break used only in narrow windows).",
 "status":"translated","source":"name","tm":tm},open('/mnt/user-data/outputs/en/62_items.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(m),len(tm), sum(1 for k in m if not variants[k]))
