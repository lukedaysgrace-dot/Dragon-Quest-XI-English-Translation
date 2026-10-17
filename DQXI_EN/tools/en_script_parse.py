#!/usr/bin/env python3
"""Parse the user-supplied official English script (RTF tables, converted by pandoc to JSON)
into rows: {file, section, idx, speaker, pages[]}.  pages = paragraphs inside the text cell
(the script puts one message window per paragraph).
Usage: en_script_parse.py <pandoc_json_dir> <out.jsonl>"""
import json, sys, os, glob

def inl(xs):
    out = []
    for x in xs:
        t = x['t']
        if t == 'Str': out.append(x['c'])
        elif t == 'Space': out.append(' ')
        elif t in ('SoftBreak',): out.append(' ')
        elif t == 'LineBreak': out.append('\n')
        elif t in ('Strong', 'Emph', 'Underline', 'SmallCaps', 'Strikeout', 'Superscript', 'Subscript'):
            out.append(inl(x['c']))
        elif t == 'Span': out.append(inl(x['c'][1]))
        elif t == 'Quoted':
            q = '"' if x['c'][0]['t'] == 'DoubleQuote' else "'"
            out.append(q + inl(x['c'][1]) + q)
        elif t == 'Code': out.append(x['c'][1])
    return ''.join(out)

def blocks_text(bs):
    paras = []
    for b in bs:
        if b['t'] in ('Para', 'Plain'): paras.append(inl(b['c']))
        elif b['t'] == 'Div': paras += blocks_text(b['c'][1])
    return paras

def table_rows(tb):
    c = tb['c']
    rows = []
    bodies = c[4]
    for body in bodies:
        for r in body[3]:
            cells = [blocks_text(cell[4]) for cell in r[1]]
            rows.append(cells)
    for r in c[3][1]:   # head rows
        rows.insert(0, [blocks_text(cell[4]) for cell in r[1]])
    return rows

def main():
    src, outp = sys.argv[1], sys.argv[2]
    n = 0
    with open(outp, 'w', encoding='utf-8') as out:
        for fn in sorted(glob.glob(os.path.join(src, '*.json'))):
            name = os.path.basename(fn)[:-5]
            d = json.load(open(fn, encoding='utf-8'))
            section = ''; sub = ''; idx = 0
            for b in d['blocks']:
                if b['t'] in ('Para', 'Plain', 'Header'):
                    t = inl(b['c'] if b['t'] != 'Header' else b['c'][2]).strip()
                    if t and len(t) < 120 and '\n' not in t: section = t; idx = 0
                elif b['t'] == 'Table':
                    for cells in table_rows(b):
                        cells = [[p.strip() for p in c if p.strip()] for c in cells]
                        if not any(cells): continue
                        if len(cells) >= 2:
                            spk = ' '.join(cells[0]); pages = [p for c in cells[1:] for p in c]
                        else:
                            spk = ''; pages = cells[0]
                        if len(pages) == 0 and spk and len(cells) == 2:
                            # heading row inside a table
                            section = spk; continue
                        out.write(json.dumps({'file': name, 'section': section, 'idx': idx,
                                              'speaker': spk, 'pages': pages}, ensure_ascii=False) + '\n')
                        idx += 1; n += 1
    print('rows', n)

if __name__ == '__main__':
    main()
