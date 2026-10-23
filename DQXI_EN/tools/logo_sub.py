#!/usr/bin/env python3
"""Title screen: remove the Japanese subtitle lines under the logo (the white/grey text pixels are
filled in from the surrounding pixels) and write the English subtitle there in a plain font with a
soft dark outline. The logo artwork itself is left untouched.
Usage: logo_sub.py orig.bflim out.bflim"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import bflim_rgb

TEXT = 'Echoes of an Elusive Age'
AREA = (186, 170, 322, 202)        # Japanese subtitle area in the 512x256 texture (both lines)
FONT = os.environ.get('LOGO_FONT', '/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf')
TEXT_BOX = (176, 170, 336, 204)    # room for the English line (a bit wider than the old Japanese)
MAX_SIZE = 16

def erase(img):
    a = np.array(img).astype(np.int16)
    x0, y0, x1, y1 = AREA
    sat = a[..., :3].max(2) - a[..., :3].min(2)
    m = np.zeros(a.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = ((a[..., 3] > 20) & (sat < 45))[y0:y1, x0:x1]
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    rgb = cv2.inpaint(a[..., :3].astype(np.uint8), m, 4, cv2.INPAINT_TELEA)
    al = cv2.inpaint(a[..., 3].astype(np.uint8), m, 4, cv2.INPAINT_TELEA)
    out = np.dstack([rgb, al]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

def main(src, dst):
    orig = open(src, 'rb').read()
    img = erase(bflim_rgb.decode(orig))
    x0, y0, x1, y1 = TEXT_BOX
    size = MAX_SIZE
    while True:
        f = ImageFont.truetype(FONT, size)
        bb = f.getbbox(TEXT)
        if bb[2] - bb[0] <= x1 - x0 - 4 or size <= 8: break
        size -= 1
    x = (x0 + x1 - (bb[2] - bb[0])) // 2 - bb[0]
    y = (y0 + y1 - (bb[3] - bb[1])) // 2 - bb[1]
    # soft dark glow, then crisp white text with a thin dark edge
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((x, y), TEXT, font=f, fill=(20, 14, 40, 255), stroke_width=2, stroke_fill=(20, 14, 40, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(1.2))
    img = Image.alpha_composite(img, glow)
    top = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(top).text((x, y), TEXT, font=f, fill=(255, 255, 255, 255), stroke_width=1, stroke_fill=(30, 20, 50, 255))
    img = Image.alpha_composite(img, top)
    open(dst, 'wb').write(bflim_rgb.encode(orig, img))
    return img

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
