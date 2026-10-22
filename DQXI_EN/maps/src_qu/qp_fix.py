import json,sys,unicodedata,re
sys.path.insert(0,'/home/claude/tools')
from wrap import Metrics
M=Metrics('/tmp/tex')
T=json.load(open('/tmp/cs/off_titles.json'))
N=lambda s: re.sub(r'[\s　・…]','',unicodedata.normalize('NFKC',s))
ids=[l.split('\t') for l in open('/home/claude/saveed/repo/item/quest.txt',encoding='utf-8').read().split('\n') if l and l[0]!='#']
jp={int(a):N(b) for a,b in ids}
omap={k:k for k in range(4,32)}
omap.update({k:k-1 for k in range(33,49)})
SHORT={7:"Cactus Cutlet to Die For",11:"Skincare for the Fierce",20:"Agony and the Ecstasy",27:"Seeds for the Future",34:"Madame Labouche's Lesson",37:"Where No Rose Grows",38:"The Sage's Stone",40:"Some Kanaloamari, Please",44:"Richie's Roulette Test",45:"A Momentous Occasion",48:"A Long-Lost Love Letter",5:"Smiths and Sparkly Spots"}
over={}
rows=[(l.split(' ',1)[0],l.split(' ',1)[1].strip()) for l in open('/tmp/cs/qp_list.txt',encoding='utf-8').read().split('\n') if l.strip()]
src=[l.split(' f: ',1)[1].strip() for l in open('/tmp/cs/gamecmn_qp.src',encoding='utf-8') if ' f: ' in l]
byn={N(j):k for k,j in jp.items()}
OVR=json.load(open('/tmp/cs/qp_over.json')) if __import__('os').path.exists('/tmp/cs/qp_over.json') else {}
out=[]
for (o,j),e in zip(rows,src):
    k=byn.get(N(j))
    if k in omap: e=SHORT.get(k) or T[omap[k]]
    if k is None: print('nomatch',j)
    if N(j) in OVR: e=OVR[N(j)]
    w=M.width('3D12',e)
    if w>176: print('WIDE',k,j,e,round(w))
    out.append((o,e))
open('/tmp/cs/gamecmn_qp.src','w',encoding='utf-8').write('@gamecmn quest_param.bxon\n'+''.join(f'{o} f: {e}\n' for o,e in out))
