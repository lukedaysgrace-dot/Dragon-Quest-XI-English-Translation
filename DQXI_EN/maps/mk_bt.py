import json, glob
jp=[l.rstrip('\n') for l in open('maps/bt_jp.txt',encoding='utf8')]
tm={}
for f in sorted(glob.glob('maps/bt_en*.txt')):
    for l in open(f,encoding='utf8'):
        l=l.rstrip('\n')
        if '=' not in l: continue
        i,e=l.split('=',1)
        tm[jp[int(i)-1].replace('⏎','\n')]=e.replace('\\n','\n')
json.dump({"_comment":"Battle messages (battlecmn battle_Text.bxon) not covered by 40_battle_core. Fan translation; auto-wrapped by the builder.",
 "status":"translated","source":"fan","tm":tm},open('/mnt/user-data/outputs/en/71_battle_text.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(tm))
