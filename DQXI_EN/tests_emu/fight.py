#!/usr/bin/env python3
"""Auto-battle: put the cursor on Fight (detect the menu cursor), then mash A until the field map is back.
Works for the 3D battle layout (yellow arrow cursor) and the 2D-style one (white triangle)."""
import subprocess, time
from PIL import Image
ENV = {'DISPLAY': ':99'}
def shot():
    subprocess.run(['import', '-window', 'root', '/tmp/f.png'], env=ENV, check=True)
    return Image.open('/tmp/f.png').convert('RGB').crop((440, 236, 840, 716))
def key(k):
    subprocess.run(['xdotool', 'mousemove', '640', '400', 'click', '1'], env=ENV); time.sleep(0.15)
    subprocess.run(['xdotool', 'keydown', k], env=ENV); time.sleep(0.12)
    subprocess.run(['xdotool', 'keyup', k], env=ENV); time.sleep(0.35)
def cursor_row(im):
    # menu box rows at y ~ 172, 188, 204, 220 (Fight/Tactics/Switch/Flee); cursor drawn at x 12-30
    best = None
    for r, y in enumerate((172, 188, 204, 220)):
        n = 0
        for x in range(10, 32):
            for yy in range(y - 5, y + 5):
                p = im.getpixel((x, yy))
                if p[0] > 200 and p[1] > 160 and p[2] < 120: n += 1      # yellow arrow
                elif p[0] > 230 and p[1] > 230 and p[2] > 230 and x < 26: n += 0.3  # white triangle
        if best is None or n > best[0]: best = (n, r)
    return best[1] if best and best[0] > 3 else None
def field(im):
    m = im.crop((40, 250, 360, 470)).resize((32, 22))
    return sum(1 for p in m.get_flattened_data() if (p[1] > p[0] + 25 and p[1] > p[2] + 25) or (abs(p[0]-p[1]) < 30 and 60 < p[0] < 200 and p[2] < p[1])) > 200
def menu_up(im):
    m = im.crop((10, 165, 95, 230))
    return sum(1 for p in m.get_flattened_data() if sum(p) < 90) > 2500
for it in range(80):
    im = shot()
    if menu_up(im):
        r = cursor_row(im)
        if r: [key('t') for _ in range(r)]
        key('a'); time.sleep(0.8); key('a'); time.sleep(0.6); key('a')
    else:
        key('a')
    time.sleep(0.9)
    if it > 3 and not menu_up(im):
        im2 = shot()
        if field(im2) and not menu_up(im2):
            print('battle over'); break
