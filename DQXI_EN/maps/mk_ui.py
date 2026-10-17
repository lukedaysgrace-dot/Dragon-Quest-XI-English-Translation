import json, glob
tm={}
for f in sorted(glob.glob('maps/ui_msgs*.txt')):
    for l in open(f,encoding='utf8'):
        l=l.rstrip('\n')
        if '=' not in l: continue
        j,e=l.split('=',1)
        tm[j.replace('⏎','\n')]=e.replace('\\n','\n')
json.dump({"_comment":"Menu / item / equip / save messages (ui mainmenu_msg, item_msg, ui_equip_msg, equip_text, ui_text, save_point_msg). Fan translation.",
 "status":"translated","source":"fan","tm":tm},open('/mnt/user-data/outputs/en/67_menu_msgs.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(tm))
