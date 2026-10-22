#!/usr/bin/env python3
"""Redraw the quest-list status badges (icon_quest_order/clear/achievementtga) in English. Usage: badge_tex.py <font_dir> <orig.bflim> <label> <out.bflim> [preview.png]"""
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bffnt,bflim_rgba as R
from PIL import Image
def glyph_text(fp,s):
    f=bffnt.Font(fp); sheets={}
    # collect (alpha image) for string
    adv=[];
    for ch in s:
        g=f.cmap.get(ord(ch)); adv.append(f.widths[g][2] if g is not None else 6)
    W=sum(adv)+2
    img=Image.new('L',(W,f.ch+2),0); px=img.load(); x=1
    for ch in s:
        g=f.cmap.get(ord(ch))
        if g is None: x+=6; continue
        per=f.cols*f.rows; sh=g//per
        if sh not in sheets: sheets[sh]=bffnt.decode_sheet(f,sh)
        a=sheets[sh]; cx,cy=bffnt.glyph_cell(f,g); left,gw,cw=f.widths[g]
        for yy in range(f.ch):
            for xx in range(gw):
                al=int(a[cy+yy,cx+xx]); X=x+left+xx
                if al and 0<=X<W: px[X,yy+1]=max(px[X,yy+1],al)
        x+=cw
    return img
def make(fp,orig,label,color):
    im=R.dec4444(orig); w,h=im.size; px=im.load()
    fill=[]; 
    for y in range(h):
        for x in range(w):
            r,g,b,a=px[x,y]
            if a>200 and max(r,g,b)<130: fill.append((r,g,b))
    fc=tuple(sum(c[i] for c in fill)//len(fill) for i in range(3)) if fill else (60,60,60)
    # clear text region: inner area of pill (rows 2..h-3, cols 8..w-9)
    for y in range(2,h-2):
        for x in range(8,w-8):
            r,g,b,a=px[x,y]
            if a>0: px[x,y]=fc+(255,)
    t=glyph_text(fp,label); tw,th=t.size
    ox=(w-tw)//2; oy=(h-th)//2
    sh=Image.new('RGBA',(w,h),(0,0,0,0)); sp=sh.load(); tp=t.load()
    for y in range(th):
        for x in range(tw):
            a=tp[x,y]
            if a:
                X,Y=ox+x,oy+y
                if 0<=X<w and 0<=Y<h:
                    # dark outline pass
                    for dx,dy in((1,0),(0,1),(1,1)):
                        if 0<=X+dx<w and 0<=Y+dy<h and sp[X+dx,Y+dy][3]<a: sp[X+dx,Y+dy]=(20,10,0,a)
    for y in range(th):
        for x in range(tw):
            a=tp[x,y]
            if a:
                X,Y=ox+x,oy+y
                if 0<=X<w and 0<=Y<h: sp[X,Y]=color+(a,)
    im.alpha_composite(sh)
    return im
if __name__=='__main__':
    fp,src,label,out=sys.argv[1:5]
    col={'Active':(255,170,40),'Clear':(60,220,255),'Done':(170,240,50)}[label]
    o=open(src,'rb').read(); im=make(fp,o,label,col)
    open(out,'wb').write(R.enc4444(o,im))
    if len(sys.argv)>5:
        bg=Image.new('RGBA',im.size,(110,110,110,255)); bg.alpha_composite(im); bg.resize((256,64),Image.NEAREST).save(sys.argv[5])
