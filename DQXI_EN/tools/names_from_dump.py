import sys,re
# print label-like lines (short text w/o quote) from dump2 output, offsets list intact
for l in open(sys.argv[1]):
    l=l.rstrip('\n')
    if l.startswith('#') or l.startswith('@'): continue
    parts=l.split(' ')
    # text begins at first token that's not hex
    i=0
    while i<len(parts) and re.fullmatch(r'[0-9a-f]{3,6}',parts[i]): i+=1
    t=' '.join(parts[i:])
    if t and '「' not in t and len(t)<=14 and '⏎' not in t and not t.startswith('{'):
        print(' '.join(parts[:i]),'|',t)
