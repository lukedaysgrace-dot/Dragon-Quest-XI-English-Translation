import json
names={k:v.replace('\n',' ') for k,v in json.load(open('/tmp/cs/names.json')).items()}
names['おばけキノコ']='Ghost mushroom'; names['合体能力を持つスライム']='a slime that can fuse'
r=json.load(open('/tmp/cs/eb_recs.json'))
A='魔王の　悪しきチカラによって⏎身も心も支配され　凶暴化した⏎'
B='大いなる暗黒のチカラに⏎影響を受けて　邪悪に変化した⏎'
out=[];non=[]
for i,x in enumerate(r):
    t=x[0].split(' ')[-2] if x[0].endswith(' ') else x[0]
    done=False
    for P,tpl in ((A,"Berserk under the demon lord's evil power: %s."),(B,"Twisted evil by great darkness: %s.")):
        if P in t:
            nm=t.split(P)[1].rstrip('。 ').strip()
            out.append('%d|%s'%(i,tpl%names[nm])); done=True
    if not done and i>=390: non.append(i)
open('/tmp/cs/eb_90.txt','w').write('\n'.join(out)+'\n')
print(len(out),non)
