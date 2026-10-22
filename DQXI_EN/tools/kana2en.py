#!/usr/bin/env python3
"""Katakana/hiragana -> simple Hepburn romaji (for made-up names). kana2en(s) -> 'Title' string."""
import re
B={'ア':'a','イ':'i','ウ':'u','エ':'e','オ':'o','カ':'ka','キ':'ki','ク':'ku','ケ':'ke','コ':'ko','サ':'sa','シ':'shi','ス':'su','セ':'se','ソ':'so','タ':'ta','チ':'chi','ツ':'tsu','テ':'te','ト':'to','ナ':'na','ニ':'ni','ヌ':'nu','ネ':'ne','ノ':'no','ハ':'ha','ヒ':'hi','フ':'fu','ヘ':'he','ホ':'ho','マ':'ma','ミ':'mi','ム':'mu','メ':'me','モ':'mo','ヤ':'ya','ユ':'yu','ヨ':'yo','ラ':'ra','リ':'ri','ル':'ru','レ':'re','ロ':'ro','ワ':'wa','ヲ':'o','ン':'n','ガ':'ga','ギ':'gi','グ':'gu','ゲ':'ge','ゴ':'go','ザ':'za','ジ':'ji','ズ':'zu','ゼ':'ze','ゾ':'zo','ダ':'da','ヂ':'ji','ヅ':'zu','デ':'de','ド':'do','バ':'ba','ビ':'bi','ブ':'bu','ベ':'be','ボ':'bo','パ':'pa','ピ':'pi','プ':'pu','ペ':'pe','ポ':'po','ヴ':'vu'}
SM={'ァ':'a','ィ':'i','ゥ':'u','ェ':'e','ォ':'o'}
Y={'ャ':'ya','ュ':'yu','ョ':'yo'}
def h2k(s): return ''.join(chr(ord(c)+0x60) if 'ぁ'<=c<='ゖ' else c for c in s)
def kana2en(s):
    s=h2k(s); out=[]; i=0; geminate=False
    while i<len(s):
        c=s[i]
        if c=='ッ': geminate=True; i+=1; continue
        if c=='ー': 
            pass
            i+=1; continue
        if c not in B: out.append(c); i+=1; continue
        r=B[c]; nxt=s[i+1] if i+1<len(s) else ''
        if nxt in Y:
            base=r[:-1] if r not in('shi','chi','ji') else r[:-1]
            ya=Y[nxt]
            if r in('shi','chi','ji'): r=r[:-1]+ya[1:] if False else r[:-1]+ya[1]+ya[2:] if False else r[:-1]+ya[1:]
            else: r=r[:-1]+ya
            i+=1
        elif nxt in SM:
            v=SM[nxt]
            if r in('shi','chi','ji'): r=r[:-1]+v if r!='ji' else 'je'
            elif r=='fu': r='f'+v
            elif r=='tsu': r='ts'+v
            elif r=='te' and v=='i': r='ti'
            elif r in('de',) and v=='i': r='di'
            elif r=='u' : r='w'+v
            elif r=='vu': r='v'+v
            else: r=r[:-1]+v
            i+=1
        if geminate: r=r[0]+r; geminate=False
        out.append(r); i+=1
    return ''.join(out)
def title(s): 
    t=kana2en(s); return t[:1].upper()+t[1:]
if __name__=='__main__':
    import sys
    for a in sys.argv[1:]: print(a,title(a))
