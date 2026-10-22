#!/usr/bin/env python3
# Builds text/en/111_panels_fan.json (skill-panel bonus texts) from templates. Run: python3 maps/src_small/panels_build.py
import sqlite3, json, re, unicodedata
db = sqlite3.connect('/home/claude/work/proj/db/progress.sqlite')
S = {'ちから':'Strength','みのまもり':'Resilience','すばやさ':'Agility','きようさ':'Deftness','みりょく':'Charm',
     'こうげき魔力':'Mag. might','かいふく魔力':'Mag. mend','さいだいＨＰ':'Max HP','さいだいＭＰ':'Max MP'}
W = {'短剣':'Dagger','片手剣':'Sword','両手剣':'Greatsword','ブーメラン':'Boomerang','ヤリ':'Spear','オノ':'Axe',
     'ツメ':'Claw','ムチ':'Whip','スティック':'Wand','両手杖':'Staff','盾':'Shield'}
E = {'氷':'ice','風':'wind','炎':'fire','土':'earth','光':'light','雷':'lightning'}
MANUAL = {
 '二刀流装備が　可能になった！':'You can now\ndual-wield!',
 '常時　敵の攻撃を　かわしやすくなった！':'Evade enemy attacks\nmore often!',
 'ぬすむでの成功率が　増えた！':'Steal success\nrate up!',
 'ゾーンに　入りやすくなった！':'Enter the pep\nzone more easily!',
 '二刀攻撃時の　右手のこうげき力が　増えた！':'Right-hand attack\nwhen dual-wielding up!',
 'ゾーンに入った時\nさらに　能力が高まるようになった！':'Stats rise even\nhigher in the zone!',
 '戦闘に勝つと　ＭＰが　すこし回復する！':'Recover a little MP\nafter winning battles!',
 '戦闘に勝つと　ＭＰが　そこそこ回復する！':'Recover some MP\nafter winning battles!',
 '呪文を　となえた時\nたまに　もう１度　呪文がこだまする！':'Spells sometimes echo\nfor a second cast!',
 '旋律特技の効果が　アップした！':'Melody skills are\nmore effective!',
 'におうだち中に\n受けるダメージが　減るようになった！':'Take less damage\nwhile standing firm!',
 'かばう中に　受けるダメージが\n減るようになった！':'Take less damage\nwhile covering!',
 '仲間をかばった時に\nたまに　カウンター攻撃するようになった！':'Sometimes counter-\nattack after covering!',
 '両手剣を装備して　ガードした時に\nカウンターが　できるようになった！':'Counter-attack when\nguarding with a greatsword!',
 '常時　会心のいちげきが　出やすくなった！':'Land critical hits\nmore often!',
 '短剣装備時に　敵を状態異常にさせる\n成功率が　上がった！':'Dagger ailment\nsuccess rate up!',
 'ブーメランでの攻撃時\n攻撃が　当たりやすくなった！':'Boomerang attacks\nhit more often!',
 'ツメ装備時に\n敵の攻撃を　かわしやすくなった！':'Evade enemy attacks\nmore often with claws!',
 'ヤリ装備時\n武器ガードを　しやすくなった！':'Parry more easily\nwith a spear!',
 '両手剣装備時\n武器ガードを　しやすくなった！':'Parry more easily\nwith a greatsword!',
 '盾装備時\n盾ガードを　しやすくなった！':'Block more easily\nwith a shield!',
 'スティックでの攻撃時に\n吸収できるＭＰが　増えた！':'MP absorbed with\nwand attacks up!',
 '両手杖での攻撃時に\n吸収できるＭＰが　増えた！':'MP absorbed with\nstaff attacks up!',
 'ツメでの攻撃時に\nＨＰを　吸収できるようになった！':'Absorb HP with\nclaw attacks!',
 'ツメでの攻撃時に\nＭＰを　吸収できるようになった！':'Absorb MP with\nclaw attacks!',
 'ムチでの攻撃時に\nＭＰを　吸収できるようになった！':'Absorb MP with\nwhip attacks!',
}
def num(s): return unicodedata.normalize('NFKC', s)
out = {}; left = []
tm = {r[0] for r in db.execute("select jp from tm where en is not null and en!=''")}
for (jn,) in db.execute("select distinct jp_norm from strings where btype like 'Panels%' and status!='skip'"):
    if jn in tm: continue
    if jn in MANUAL: out[jn] = MANUAL[jn]; continue
    m = re.fullmatch(r'(' + '|'.join(S) + r')が　([０-９]+)　増えた！', jn)
    if m: out[jn] = '%s up by %s!' % (S[m.group(1)], num(m.group(2))); continue
    m = re.fullmatch(r'(' + '|'.join(W) + r')装備時の　(こうげき力|しゅび力)が\n([０-９]+)　増えた！', jn)
    if m:
        st = 'attack' if m.group(2) == 'こうげき力' else 'defence'
        out[jn] = '%s %s\nup by %s!' % (W[m.group(1)], st, num(m.group(3))); continue
    m = re.fullmatch(r'(' + '|'.join(W) + r')(?:での攻撃時|での攻撃時)\n会心のいちげきが　出やすくなった！', jn)
    if m: out[jn] = '%s attacks crit\nmore often!' % W[m.group(1)]; continue
    m = re.fullmatch(r'(' + '|'.join(W) + r')装備時の　(かいふく魔力|こうげき魔力|ＭＰ)が\n([０-９]+)　増えた！', jn)
    if m:
        st = {'かいふく魔力':'Mag. mend','こうげき魔力':'Mag. might','ＭＰ':'Max MP'}[m.group(2)]
        out[jn] = '%s %s\nup by %s!' % (W[m.group(1)], st, num(m.group(3))); continue
    m = re.fullmatch(r'(.)属性と　(.)属性のダメージを\n軽減するようになった！', jn)
    if m and m.group(1) in E and m.group(2) in E:
        out[jn] = 'Reduces %s and %s\ndamage taken!' % (E[m.group(1)], E[m.group(2)]); continue
    left.append(jn)
json.dump({'_comment':'Skill panel bonus texts (panel_*.bxon). Templated, fan.','status':'translated','source':'fan','tm':out},
          open('/home/claude/DQXI_EN/text/en/111_panels_fan.json','w',encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(out), 'done;', len(left), 'left')
for l in left: print(repr(l))
