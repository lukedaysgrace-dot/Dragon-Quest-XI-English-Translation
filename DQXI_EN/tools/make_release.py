#!/usr/bin/env python3
"""Package a built patch (build_patch.py output) as LayeredFS folders + zip.

Usage: make_release.py <build_dir> <release_dir> <version>
Creates:
  release/<version>/luma/titles/0004000000199200/romfs/...      (Luma3DS game patching, real hardware)
  release/<version>/azahar/load/mods/0004000000199200/romfs/... (Azahar / Citra-based emulators)
  release/DQXI3DS_EN_<version>.zip  (luma layout + docs + manifest)
"""
import os, sys, shutil, zipfile
TID = '0004000000199200'

def main():
    build, rel, ver = sys.argv[1:4]
    base = os.path.join(rel, ver)
    if os.path.exists(base): shutil.rmtree(base, ignore_errors=True)
    for layout in (('luma', 'titles', TID, 'romfs'), ('azahar', 'load', 'mods', TID, 'romfs')):
        dst = os.path.join(base, *layout)
        shutil.copytree(os.path.join(build, 'romfs'), dst, dirs_exist_ok=True)
        ips = os.path.join(build, 'exefs', 'code.ips')
        if os.path.exists(ips):   # Luma: titles/<tid>/code.ips ; Azahar: mods/<tid>/exefs/code.ips
            tgt = os.path.join(os.path.dirname(dst), 'code.ips') if layout[0] == 'luma' else \
                  os.path.join(os.path.dirname(dst), 'exefs', 'code.ips')
            os.makedirs(os.path.dirname(tgt), exist_ok=True); shutil.copy(ips, tgt)
    for f in ('manifest.sha256', 'report.txt'):
        if os.path.exists(os.path.join(build, f)): shutil.copy(os.path.join(build, f), base)
    z = os.path.join(rel, 'DQXI3DS_EN_%s.zip' % ver)
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        root = os.path.join(base, 'luma')
        for dp, dn, fn in os.walk(root):
            for f in fn:
                p = os.path.join(dp, f)
                zf.write(p, os.path.relpath(p, base))
        zf.write(os.path.join(base, 'manifest.sha256'), 'manifest.sha256')
    print('release at', base, 'zip', z, os.path.getsize(z) // 1024, 'KiB')

if __name__ == '__main__':
    main()
