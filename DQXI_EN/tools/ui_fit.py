#!/usr/bin/env python3
"""UI fit audit with per-field limits instead of per-string Japanese widths.

A string's field = (bxon entry, btype, number of Japanese lines). The space the game gives a field
is at least as wide as its widest Japanese line and as tall as its tallest Japanese string, so the
limit for every string in the field is the max over the whole field. Font: 3D12 (used by ~60% of UI
panes); English is drawn condensed (DQXI_CONDENSE, default 0.92) so it gets that much more room.
Item-name fields from 62b_item_names_2line.json are 2-line on purpose (battle target window).
Usage: ui_fit.py <proj> <font_dir> [btype...]   -> report on stdout
"""
import sys, os, re, sqlite3, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wrap
from build_patch import fix_chars

COND = float(os.environ.get('DQXI_CONDENSE', '0.92'))
import json
TWO_LINE = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'text', 'en', '62b_item_names_2line.json'), encoding='utf-8'))['id'])

# Real panes (from the BFLYT layouts, scale = fontSize / font width = 1 for all of these).
# btype -> {'multi'|'single': ([(font, px), ...], max_lines)}   multi = Japanese has line breaks
RULES = {
    'EnemyBaseParam':      {'multi': ([('3D12', 130), ('2D9', 110)], 2),      # win_target_3d/2d txt_target (widened, grow.txt)
                            'single': ([('3D12', 150), ('2D9', 150)], 1)},    # win_enemy txt_l*
    'UIMapParamSet':       {'single': ([('3D12', 150), ('2D9', 150)], 1)},    # menu_map_place txt_place
    'QuestUIParam':        {'multi': ([('3D14', 260), ('2D9', 200)], 5),      # menu_senreki_quest2 txt
                            'single': ([('3D14', 180)], 1)},                  # quest list column (seen in game)
    'AchievementParam':    {'multi': ([('3D14', 300)], 3),                    # menu_senreki_title txt
                            'single': ([('3D14', 230)], 1)},                  # txt_title
    'UIStoryFlagRelation': {'multi': ([('3D14', 400)], 7),                    # common_3d_up_senreki txt_story
                            'single': ([('3D14', 400)], 7)},
    'CSChapterParam':      {'single': ([('3D12', 186), ('2D9', 170)], 1)},    # menu_memories_list txt_l*
    'EnemyBookParam':      {'multi': ([('3D12', 160)], 3),                    # menu_senreki_monster txt_place
                            'single': ([('3D12', 160)], 3)},
    'PassiveSkillParam':   {'multi': ([('3D12', 120)], 4)},                   # common_3d_lw_skill txt_pane
    'UIAnotherNameParam':  {'single': ([('3D12', 150)], 1)},                  # win_tsuyosa1 txt_title (status)
}
# extra horizontal squeeze given to the pane in grow.txt (x0.80 etc.)
BT_SCALE = {'UIMapParamSet': 0.80, 'CSChapterParam': 0.80, 'UIAnotherNameParam': 0.88, 'EnemyBaseParam': 0.88}
ITEM_DESC = ([('3D12', 124), ('2D14', 115)], 3)   # item descriptions, verified in game (rewrap_idesc.py)

def vis_lines(s):
    return [l for l in re.split(r'\{x:000[AD]\}|\n', s.replace('\r', ''))]

def main():
    proj, fdir = sys.argv[1:3]; only = set(sys.argv[3:])
    m = wrap.Metrics(fdir)
    db = sqlite3.connect(os.path.join(proj, 'db', 'progress.sqlite'))
    tm = dict(db.execute('select jp,en from tm'))
    rows = db.execute('select id,entry,btype,jp,jp_norm,en from strings').fetchall()
    # effective limit = max(real pane, widest Japanese line of the same field): if the Japanese
    # needs more room than the pane we mapped, the game clearly allows it (or the mapping is loose)
    fonts = ('3D12', '3D14', '2D9', '2D14')
    field = collections.defaultdict(lambda: [collections.Counter(), 0])
    items = []
    for sid, entry, bt, jp, jpn, en in rows:
        if bt == 'LYT' or wrap.context_for(bt) or (only and bt not in only): continue
        en = en or tm.get(jpn) or tm.get(jp)
        if not en: continue
        jl = vis_lines(jp)
        key = (entry, bt, len(jl))
        f = field[key]
        for fn in fonts:
            f[0][fn] = max(f[0][fn], max(m.width(fn, l) for l in jl))
        f[1] = max(f[1], len(jl))
        items.append((sid, key, fix_chars(en)))
    bad = collections.Counter(); out = []
    for sid, key, en in items:
        jmax, lmax = field[key]
        el = vis_lines(en)
        kind = 'multi' if key[2] > 1 else 'single'
        rule = RULES.get(key[1], {}).get(kind)
        if key[1] == 'ItemParam' and kind == 'multi' and sid not in TWO_LINE and jmax['3D12'] > 60:
            rule = ITEM_DESC
        tag = 'PANE' if rule else 'GUESS'
        specs, maxl = rule if rule else ([('3D12', 0)], 0)
        probs = []
        for fn, px in specs:
            lim = max(px, jmax[fn] * (1.0 if rule else 1.08))
            w = max(m.width(fn, l) for l in el) * COND * (BT_SCALE.get(key[1], 1.0) if rule else 1.0)
            if w > lim + 0.5: probs.append('%s %.0f>%.0f' % (fn, w, lim))
        if len(el) > max(maxl, lmax) and sid not in TWO_LINE: probs.append('lines %d>%d' % (len(el), max(maxl, lmax)))
        if probs:
            bad[key[1]] += 1
            out.append('%s\t%s\t%s\t%s' % (sid, key[1], ';'.join([tag] + probs), en.replace('\n', '\u23ce')))
    print('\n'.join(out)); print('#', sum(bad.values()), dict(bad.most_common()), file=sys.stderr)

if __name__ == '__main__':
    main()
