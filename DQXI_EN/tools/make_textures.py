#!/usr/bin/env python3
"""Generate replacement textures into <out_dir> (mirroring romfs/pack/arc/file paths).
Currently: the name-entry keyboard (title.pack + any other pack carrying win_keyboard*_3d.bflim).
Usage: make_textures.py <romfs_dir> <font_dir> <maps_dir> <out_dir>"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack import Pack
from sarc import Sarc
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    romfs, fonts, maps, out = sys.argv[1:5]
    kb = os.path.join(maps, 'keyboard.tsv')
    # use the English-patched font (ASCII widths) for the glyphs
    import font_patch, tempfile
    fdir = tempfile.mkdtemp()
    data, _ = font_patch.patch('3D12', os.path.join(fonts, '3D12.bffnt'))
    open(os.path.join(fdir, '3D12.bffnt'), 'wb').write(data)
    fonts = fdir
    n = 0
    for pk_rel in ('ui/title.pack',):
        pk = Pack(os.path.join(romfs, pk_rel))
        for e in pk.entries:
            if e['data'][:4] != b'SARC': continue
            for fl in Sarc(e['data']).files:
                name = fl['name'] or ''
                for tex, page in (('timg/win_keyboard_3d.bflim', 0), ('timg/win_keyboardB_3d.bflim', 1)):
                    if name != tex: continue
                    dst = os.path.join(out, pk_rel, e['name'], name)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    src = dst + '.orig'
                    open(src, 'wb').write(fl['data'])
                    subprocess.check_call([sys.executable, os.path.join(HERE, 'kb_texture.py'), fonts, kb, src, str(page), dst])
                    os.remove(src); n += 1
    # quest-list status badges (icon_quest_*.bflim) in every ui pack that carries them
    import glob
    badge = {'timg/icon_quest_order.bflim': 'Active', 'timg/icon_quest_clear.bflim': 'Clear', 'timg/icon_quest_achievementtga.bflim': 'Done'}
    for pkf in sorted(glob.glob(os.path.join(romfs, 'ui', '*.pack'))):
        pk_rel = os.path.relpath(pkf, romfs).replace(os.sep, '/')
        try: pk = Pack(pkf)
        except Exception: continue
        for e in pk.entries:
            if e['data'][:4] != b'SARC': continue
            try: fls = Sarc(e['data']).files
            except Exception: continue
            for fl in fls:
                name = fl['name'] or ''
                if name not in badge: continue
                dst = os.path.join(out, pk_rel, e['name'], name)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                src = dst + '.orig'
                open(src, 'wb').write(fl['data'])
                subprocess.check_call([sys.executable, os.path.join(HERE, 'badge_tex.py'), os.path.join(fonts, '3D12.bffnt'), src, badge[name], dst])
                os.remove(src); n += 1
    # title screen: English subtitle plate over the Japanese subtitle under the logo (logo art untouched)
    pk_rel = 'ui/logo_3d.pack'
    pk = Pack(os.path.join(romfs, pk_rel))
    for e in pk.entries:
        if e['data'][:4] != b'SARC': continue
        for fl in Sarc(e['data']).files:
            if (fl['name'] or '') != 'timg/title_logo_3d.bflim': continue
            dst = os.path.join(out, pk_rel, e['name'], fl['name'])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            src = dst + '.orig'; open(src, 'wb').write(fl['data'])
            subprocess.check_call([sys.executable, os.path.join(HERE, 'logo_sub.py'), src, dst])
            os.remove(src); n += 1
    print('textures', n)

if __name__ == '__main__':
    main()
