import sqlite3,re,sys
sys.path.insert(0,'/home/claude/tools')
from kana2en import title
db=sqlite3.connect('/home/claude/work/proj/db/progress.sqlite')
P=dict(zip("北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 山梨 長野 富山 石川 福井 岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄 アジア ヨーロッパ アフリカ アメリカ オセアニア 南極 いなか 都会 遠い国 アレフガルド ロトゼタシア アストルティア ラダトーム ローレシア アリアハン 山奥の村 サンタローズ ライフコッド フィッシュベル トラペッタ ウォルロ村 エテーネの村 イシの村 ぱふぱふ小屋 森の中 こたつ".split(),
"Hokkaido|Aomori|Iwate|Miyagi|Akita|Yamagata|Fukushima|Ibaraki|Tochigi|Gunma|Saitama|Chiba|Tokyo|Kanagawa|Niigata|Yamanashi|Nagano|Toyama|Ishikawa|Fukui|Gifu|Shizuoka|Aichi|Mie|Shiga|Kyoto|Osaka|Hyogo|Nara|Wakayama|Tottori|Shimane|Okayama|Hiroshima|Yamaguchi|Tokushima|Kagawa|Ehime|Kochi|Fukuoka|Saga|Nagasaki|Kumamoto|Oita|Miyazaki|Kagoshima|Okinawa|Asia|Europe|Africa|America|Oceania|Antarctica|The countryside|The big city|Faraway lands|Alefgard|Erdrea|Astoltia|Tantegel|Lorasia|Aliahan|Mountain villages|Sancrest|Lifecod|Fishbel|Trodain|Wallrow|Ethene|Cobblestone|The puff-puff parlor|The forest|The kotatsu".split('|')))
H=dict(zip("アウトドア 水泳 野球 射撃 筋トレ 散歩 自転車 カヌー ゴルフ サーフィン サッカー 乗馬 サバゲー ダイビング スポーツ観戦 ハイキング バスケットボール ダンス テニス ボルダリング アイドル ライブ ボイトレ 楽器演奏 カラオケ 映像配信 実況 アニソン コスプレ お絵描き アニメ ゲーム ボードゲーム ネットゲーム カードゲーム 人狼ゲーム 謎解き 麻雀 パズル スマホ SNS ブログ インターネット オークション ショッピング ホームパーティー 宴会 旅行 ドライブ 廃墟巡り カメラ 読書 映画 囲碁 将棋 株 親孝行 自分探し じゃんけん ツチノコ探し 日曜大工 プラモデル フルコンプ 妄想 食べること 料理 歴史 人助け 切手集め 占い 茶道 貯金 釣り 鉄道 勉強 盆栽 手芸 おしゃべり オシャレ おそうじ ダイエット ネイルアート ネコ イヌ ねること 冒険 レベル上げ 錬金・鍛冶 しばりプレイ ぱふぱふ メタル狩り ルーレット ポーカー スロット ひとりキャンプ".split(),
"the outdoors|swimming|baseball|shooting|strength training|walks|cycling|canoeing|golf|surfing|soccer|horseback riding|airsoft|scuba diving|watching sports|hiking|basketball|dancing|tennis|bouldering|idols|live shows|voice training|playing instruments|karaoke|video streaming|commentary|anime songs|cosplay|drawing|anime|games|board games|online games|card games|werewolf games|puzzle solving|mahjong|puzzles|smartphones|social media|blogging|the internet|auctions|shopping|house parties|banquets|travel|drives|touring ruins|cameras|reading|movies|Go|shogi|stocks|filial piety|finding myself|rock-paper-scissors|hunting for the Tsuchinoko|DIY|model kits|completing collections|daydreaming|eating|cooking|history|helping people|stamp collecting|fortune-telling|tea ceremony|saving money|fishing|trains|studying|bonsai|crafts|chatting|fashion|cleaning|dieting|nail art|cats|dogs|sleeping|adventure|leveling up|alchemy and smithing|challenge runs|puff-puff|metal slime hunting|roulette|poker|slots|solo camping".split('|')))
print(len(P),len(H))
def tr(j):
    j=j.replace('　','　')
    m=re.fullmatch(r'(.+)　サイコー！',j)
    if m: return P[m[1]]+' is the best!'
    m=re.fullmatch(r'ビバ！　(.+)！',j)
    if m: return 'Viva '+(P.get(m[1]) or H[m[1]])+'!'
    m=re.fullmatch(r'好きなものは　(.+)！',j)
    if m: return 'My favorite thing is '+H[m[1]]+'!'
    m=re.fullmatch(r'(.+)　大好き！',j)
    if m: return 'I love '+H[m[1]]+'!'
    raise Exception(j)
for e,short in(('dummy_player_message.bxon','dm'),('dummy_player_name.bxon','dn')):
    rows=db.execute("select off,jp_norm from strings where entry=? and status='untranslated' order by off",(e,)).fetchall()
    first={}
    for o,j in rows: first.setdefault(j,o)
    open(f'/tmp/cs/fieldcmn_{short}.txt','w').write(f'@fieldcmn {e}\n# npc 7 cond None\n'+''.join('%x %s \n'%(o,j.replace('\n','⏎')) for j,o in first.items()))
    f=(lambda j:tr(j)) if short=='dm' else (lambda j:title(j))
    open(f'/tmp/cs/fieldcmn_{short}.src','w').write(f'@fieldcmn {e}\n'+''.join('%x f: %s\n'%(o,f(j)) for j,o in first.items()))
