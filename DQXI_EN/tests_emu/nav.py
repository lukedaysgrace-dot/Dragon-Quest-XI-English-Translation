#!/usr/bin/env python3
"""Closed-loop map-aligned walking in 3D mode, using the bottom-screen 2D map.
The 2D map scrolls with the hero; phase correlation of two map crops gives the hero's map motion.
Because the 3D camera can change at any time, each step re-uses the last good stick direction while it keeps
moving the hero the right way, and otherwise probes all 8 stick directions and takes the best.

  nav.py walk <N|NE|E|SE|S|SW|W|NW> <map px>   [more dir px pairs...]
  nav.py probe
"""
import sys, subprocess, time, math, json, os
import numpy as np
from PIL import Image
ENV = {'DISPLAY': ':99'}
STATE = '/tmp/nav_state.json'
STICK = [['Up'], ['Up', 'Right'], ['Right'], ['Down', 'Right'], ['Down'], ['Down', 'Left'], ['Left'], ['Up', 'Left']]
DIRS = {'N': (0, -1), 'NE': (1, -1), 'E': (1, 0), 'SE': (1, 1), 'S': (0, 1), 'SW': (-1, 1), 'W': (-1, 0), 'NW': (-1, -1)}

def grab():
    """(gray map array, hero screen position or None). Map area = bottom screen rows 240..480 (minus UI)."""
    subprocess.run(['import', '-window', 'root', '/tmp/nav.png'], env=ENV, check=True)
    im = Image.open('/tmp/nav.png').convert('RGB').crop((480, 476, 800, 716))
    a = np.asarray(im).astype(int)
    m = ((a[:, :, 0] == 0) & (a[:, :, 1] == 165) & (a[:, :, 2] == 173)) | ((a[:, :, 0] == 0) & (a[:, :, 1] == 107) & (a[:, :, 2] == 115))
    ys, xs = np.nonzero(m)
    hero = (xs.mean(), ys.mean()) if len(xs) >= 8 else None
    g = np.asarray(im.convert('L'), dtype=np.float32)
    return g, hero

def shift(a, b):
    A = np.fft.fft2(a - a.mean()); B = np.fft.fft2(b - b.mean())
    R = A.conj() * B; R /= np.abs(R) + 1e-9
    r = np.fft.ifft2(R).real
    y, x = np.unravel_index(np.argmax(r), r.shape); h, w = r.shape
    if y > h // 2: y -= h
    if x > w // 2: x -= w
    return int(x), int(y)

def hold(keys, secs):
    subprocess.run(['xdotool', 'mousemove', '640', '400', 'click', '1'], env=ENV); time.sleep(0.15)
    subprocess.run(['xdotool'] + sum([['keydown', k] for k in keys], []), env=ENV)
    time.sleep(secs)
    subprocess.run(['xdotool'] + sum([['keyup', k] for k in keys], []), env=ENV)
    time.sleep(0.5)

def masked(g, hs):
    g = g.copy(); mu = g.mean()
    for h in hs:
        if h is None: continue
        x, y = int(h[0]), int(h[1])
        g[max(0, y - 40):y + 40, max(0, x - 40):x + 40] = mu
    return g

def motion(keys, secs):
    (ga, ha) = grab(); hold(keys, secs); (gb, hb) = grab()
    dx, dy = shift(masked(ga, [ha, hb])[10:200, 10:310], masked(gb, [ha, hb])[10:200, 10:310])
    if ha is None or hb is None: return -dx, -dy
    return (hb[0] - ha[0]) - dx, (hb[1] - ha[1]) - dy

def score(m, d):
    n = math.hypot(*m)
    if n < 3: return -1, n
    return (m[0] * d[0] + m[1] * d[1]) / (n * math.hypot(*d)), n

def walk(dname, dist, step=0.5):
    d = DIRS[dname]
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    k = st.get('last')
    done = 0.0; fails = 0
    while done < dist and fails < 3:
        if k is not None:
            m = motion(STICK[k], step); c, n = score(m, d)
            if c > 0.85:
                done += n * c; fails = 0; continue
        best = None
        for i in range(8):
            m = motion(STICK[i], 0.4); c, n = score(m, d)
            if best is None or c > best[0]: best = (c, i, n)
            if c > 0.92: break
        if best[0] < 0.5:
            fails += 1; k = None; print('  %s: no good direction (best cos %.2f)' % (dname, best[0])); continue
        k = best[1]; done += best[2] * best[0]
    json.dump({'last': k}, open(STATE, 'w'))
    print('%s %d: moved %.0f px%s' % (dname, dist, done, '' if done >= dist else ' (stopped)'))
    return done >= dist

if __name__ == '__main__':
    if sys.argv[1] == 'probe':
        for i, ks in enumerate(STICK): print(ks, motion(ks, 0.3))
    elif sys.argv[1] == 'walk':
        a = sys.argv[2:]
        for i in range(0, len(a), 2):
            if not walk(a[i], float(a[i + 1])): break
