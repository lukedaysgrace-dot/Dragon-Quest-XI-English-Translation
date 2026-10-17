#!/usr/bin/env python3
"""Lossless conversion between DQXI 3DS UTF-16 message strings and editable text.

Control codes found in the game data (see PROGRESS.md for statistics):
  0x0001 base 0x0002 reading 0x0003   furigana (ruby)      -> {ruby:base|reading}
  0x0004 N                            runtime variable #N  -> {var:N}
  0x000D 0x000A                       line break (dialogue)  -> \\n   (string flagged nl=crlf)
  0x000A                              line break (UI)        -> \\n   (string flagged nl=lf)
  any other code < 0x20               -> {x:XXXX}
  literal '{' / '}'                   -> {{ / }}
"""
import re

def detect_nl(u):
    s = ''.join(map(chr, u))
    crlf = s.count('\r\n'); lf = s.count('\n') - crlf; cr = s.count('\r') - crlf
    if crlf and not lf and not cr: return 'crlf'
    if lf and not crlf and not cr: return 'lf'
    if not crlf and not lf and not cr: return 'none'
    return 'mixed'

def decode(u, nl=None):
    nl = nl or detect_nl(u)
    out = []; i = 0; n = len(u)
    while i < n:
        c = u[i]
        if c == 1:
            j = i + 1; base = []
            while j < n and u[j] != 2: base.append(u[j]); j += 1
            k = j + 1; rd = []
            while k < n and u[k] != 3: rd.append(u[k]); k += 1
            if j < n and k < n:
                out.append('{ruby:%s|%s}' % (decode(base, 'none'), decode(rd, 'none'))); i = k + 1; continue
            out.append('{x:0001}'); i += 1; continue
        if c == 4 and i + 1 < n:
            out.append('{var:%d}' % u[i+1]); i += 2; continue
        if c == 0x0D and nl == 'crlf' and i + 1 < n and u[i+1] == 0x0A:
            out.append('\n'); i += 2; continue
        if c == 0x0A and nl == 'lf':
            out.append('\n'); i += 1; continue
        if c < 0x20:
            out.append('{x:%04X}' % c); i += 1; continue
        ch = chr(c)
        out.append('{{' if ch == '{' else '}}' if ch == '}' else ch)
        i += 1
    return ''.join(out)

TOK = re.compile(r'\{\{|\}\}|\{ruby:([^|{}]*)\|([^{}]*)\}|\{var:(\d+)\}|\{x:([0-9A-Fa-f]{4})\}|\{[^{}]*\}|\n|.', re.S)

class EncodeError(ValueError): pass

def encode(s, nl='crlf'):
    out = []
    for m in TOK.finditer(s):
        t = m.group(0)
        if t == '{{': out.append(ord('{'))
        elif t == '}}': out.append(ord('}'))
        elif m.group(1) is not None:
            out.append(1); out += encode(m.group(1), 'none'); out.append(2); out += encode(m.group(2), 'none'); out.append(3)
        elif m.group(3) is not None: out += [4, int(m.group(3))]
        elif m.group(4) is not None: out.append(int(m.group(4), 16))
        elif t.startswith('{') and len(t) > 1: raise EncodeError('unknown tag %r' % t)
        elif t == '\n':
            out += [0x0D, 0x0A] if nl == 'crlf' else [0x0A]
        else:
            c = ord(t)
            if c > 0xFFFF: raise EncodeError('non-BMP char %r' % t)
            out.append(c)
    return out

_JP = re.compile('[぀-ヿ一-鿿！-～　-〿]')
def is_text(u):
    """Filter out binary blocks that merely look like strings."""
    skip = False
    for c in u:
        if skip: skip = False; continue          # parameter of {var:N}
        if c == 4: skip = True; continue
        if c < 0x20 and c not in (1, 2, 3, 9, 0x0A, 0x0D): return False
        if 0x7F <= c < 0xA0 or c >= 0xFFF0 or 0x3400 <= c < 0x4E00 or 0xD800 <= c < 0xE000: return False
    return True

def has_japanese(s):
    return bool(_JP.search(s))
