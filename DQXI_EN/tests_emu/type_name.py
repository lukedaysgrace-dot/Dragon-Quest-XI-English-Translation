import subprocess, sys, time
grid = [l.split(' ') for l in """A B C D E a b c d e _ !
F G H I J f g h i j _ ?
K L M N O k l m n o ~ .
P Q R S T p q r s t 123 _
U V W X Y u v w x y Back _
Z - ' & , z SP ? ! . End _""".split('\n')]
pos = {}
for r, row in enumerate(grid):
    for c, t in enumerate(row): pos.setdefault(t, (r, c))
cur = (0, 0)
def key(k): subprocess.call(['/home/claude/emu/emu.sh', 'key', k])
for ch in sys.argv[1]:
    r, c = pos[ch]
    dr, dc = r - cur[0], c - cur[1]
    seq = (['g'] * dr if dr > 0 else ['t'] * -dr) + (['h'] * dc if dc > 0 else ['f'] * -dc)
    if seq: subprocess.call(['/home/claude/emu/emu.sh', 'key'] + seq)
    key('a'); time.sleep(0.6); cur = (r, c)
