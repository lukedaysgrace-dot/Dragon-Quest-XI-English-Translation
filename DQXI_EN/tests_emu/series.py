# series.py <name> <count> <interval> [press_a 0/1] [top|both] : grab frames, write montage shots/<name>_m.png
import subprocess, sys, time
from PIL import Image
name, n, iv = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
press = len(sys.argv) > 4 and sys.argv[4] == '1'
part = sys.argv[5] if len(sys.argv) > 5 else 'top'
fr = []
for i in range(n):
    subprocess.call(['import', '-window', 'root', '/tmp/ser.png'], env={'DISPLAY': ':99'})
    im = Image.open('/tmp/ser.png').convert('RGB')
    box = (440, 240, 840, 480) if part == 'top' else (440, 236, 840, 716)
    c = im.crop(box); sc = float(__import__('os').environ.get('SC', '1'))
    fr.append(c.resize((int(c.width*sc), int(c.height*sc))) if sc != 1 else c)
    if press: subprocess.call(['/home/claude/emu/emu.sh', 'key', 'a'])
    time.sleep(iv)
w, h = fr[0].size; cols = 2
rows = (len(fr) + cols - 1) // cols
m = Image.new('RGB', (w * cols, h * rows))
for i, f in enumerate(fr): m.paste(f, ((i % cols) * w, (i // cols) * h))
m.save('/home/claude/emu/shots/%s_m.png' % name)
