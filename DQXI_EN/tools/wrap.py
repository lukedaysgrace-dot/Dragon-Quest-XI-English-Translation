#!/usr/bin/env python3
"""Pixel-accurate word wrapping for English text using the game's (patched) fonts.

Dialogue windows (measured from the layouts, see PROGRESS.md):
  3D talk window  win_talk_3d.bflyt  txt1  350 px, 3D14 @ scale 1, 3 lines
  2D talk window  win_talk_lw_2d     txt   300 px, 2D14 @ scale 1, 3 lines
  2D battle msg   win_talk_2d        txt   338 px, 2D9  @ scale 1
The same string is shown by both modes, so a line must fit every font listed for its context.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bffnt

VAR_WIDTH = {1: 8, 2: 10, 3: 10}     # assumed max visible chars for {var:N} (hero name=8)
DEFAULT_VAR_CHARS = 12

class Metrics:
    def __init__(self, font_dir):
        self.f = {}
        for n in ('3D12', '3D14', '2D14', '2D9', '2D14SH'):
            p = os.path.join(font_dir, n + '.bffnt')
            if os.path.exists(p): self.f[n] = bffnt.Font(p)
    def width(self, font, s):
        f = self.f[font]; w = 0
        for tok in re.finditer(r'\{var:(\d+)\}|\{ruby:([^|]*)\|[^}]*\}|\{x:[0-9A-F]{4}\}|\{\{|\}\}|.', s):
            if tok.group(1):
                n = VAR_WIDTH.get(int(tok.group(1)), DEFAULT_VAR_CHARS)
                w += n * self._cw(f, 'M') * 0.75; continue
            if tok.group(2) is not None:
                w += self.width(font, tok.group(2)); continue
            t = tok.group(0)
            if t.startswith('{x:'): continue
            w += self._cw(f, t[0])
        return w
    def _cw(self, f, ch):
        g = f.cmap.get(ord(ch))
        if g is None: g = f.cmap.get(ord('?'))
        return f.widths[g][2] if g in f.widths else f.width

# context -> list of (font, max_px), max_lines
CONTEXTS = {
    'talk':   ([('3D14', 326), ('2D14', 290)], 3),
    'battle': ([('2D9', 326), ('3D14', 326)], 3),
}
TALK_TYPES = {'CharacterIEData', 'TalkPartyContent2', 'TextBlock', 'ChurchMsg', 'ShopMsg', 'InnMsg', 'BankMsg',
              'CasinoMsg', 'JewelShopMsg', 'SavePointMsg', 'SerenHintMessage', 'ItemFailureMessage',
              'SpiritTalkParam', 'UIMessage', 'DummyPlayerMessage'}

def context_for(btype):
    if btype in TALK_TYPES: return 'talk'
    if btype == 'BattleText': return 'battle'
    return None

CONDENSE = float(os.environ.get('DQXI_CONDENSE', '1'))   # text panes are drawn at fontSize.x*CONDENSE

def fits(m, line, specs, scale=None):
    sc = CONDENSE if scale is None else scale
    return all(m.width(font, line) * sc <= px for font, px in specs)

def wrap(m, text, specs):
    """Greedy wrap; explicit newlines are kept. Returns list of lines."""
    out = []
    for para in text.split('\n'):
        # break points: spaces, and after a dash (U+2015 is the game's em dash)
        words = re.findall(r'[^ \u2015]*\u2015|[^ \u2015]+', para) or ['']
        seps = []
        pos = 0
        for w in words:
            i = para.index(w, pos); seps.append(para[pos:i]); pos = i + len(w)
        cur = ''
        for w, sep in zip(words, seps):
            if cur and cur.endswith('\u2015') and sep == '': cand = cur + w
            else: cand = w if not cur else cur + ' ' + w
            if not cur or fits(m, cand, specs):
                cur = cand
            else:
                out.append(cur); cur = w
        out.append(cur)
    return out

def adaptive_specs(m, jp_text):
    """For UI strings without a known window: the widest Japanese line (3D14) is a safe width."""
    lines = jp_text.split('\n')
    px = max(m.width('3D14', l) for l in lines) if lines else 0
    return [('3D14', max(px, 40))], len(lines)

def layout(m, en, btype, jp):
    """Return (wrapped_text, problems[])."""
    ctx = context_for(btype)
    probs = []
    if ctx and '{x:000A}' not in en and '{x:000D}' not in en:
        specs, maxl = CONTEXTS[ctx]
        lines = wrap(m, en, specs)
    elif ctx:
        # explicit control-code layout (battle reward lines etc.): keep as written, only check
        specs, maxl = CONTEXTS[ctx]
        lines = en.split('\n')
        for l in re.split(r'\{x:000[AD]\}|\n', en):
            if not fits(m, l, specs): probs.append('too wide: %r' % l)
    else:
        specs, maxl = adaptive_specs(m, jp)
        lines = en.split('\n')       # UI text: keep translator's breaks, only check
        for l in lines:
            if not fits(m, l, specs, 1.0): probs.append('too wide (%.0f > %.0f px): %r' % (m.width(specs[0][0], l), specs[0][1], l))
    if len(lines) > maxl: probs.append('%d lines > %d' % (len(lines), maxl))
    return '\n'.join(lines), probs
