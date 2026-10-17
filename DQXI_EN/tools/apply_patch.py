#!/usr/bin/env python3
"""One-shot end-user build: Japanese ROM + this project's translations -> LayeredFS patch.

Usage: python3 apply_patch.py <DQXI_JP.3ds> <work_dir> [version]
Steps (all reproducible, nothing proprietary is shipped with the project):
  1. extract the RomFS text-bearing folders from YOUR decrypted cartridge dump
  2. dump Japanese strings + UI layouts into a fresh progress DB
  3. import text/en/*.json translations
  4. rebuild modified archives, patch fonts, verify structure
  5. write LayeredFS folders for Luma3DS and Azahar/Citra
Requires Python 3.8+, numpy (pip install numpy).
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
NEED = '/script,/param,/font,/ui,/battlecmn,/gamecmn,/syscmn,/fieldcmn,/2dcmn,/divecmn'

def run(*a):
    print('>>', ' '.join(a)); subprocess.check_call([sys.executable] + list(a))

def main():
    rom, work = sys.argv[1], os.path.abspath(sys.argv[2])
    ver = sys.argv[3] if len(sys.argv) > 3 else 'local'
    ext = os.path.join(work, 'ext'); proj = os.path.join(work, 'proj'); build = os.path.join(work, 'build')
    os.makedirs(os.path.join(proj, 'text'), exist_ok=True)
    en = os.path.join(proj, 'text', 'en')
    if not os.path.exists(en):
        try: os.symlink(os.path.join(PROJ, 'text', 'en'), en)
        except OSError:
            import shutil; shutil.copytree(os.path.join(PROJ, 'text', 'en'), en)
    run(os.path.join(HERE, 'ctr_extract.py'), rom, ext, '--only=' + NEED)
    run(os.path.join(HERE, 'text_dump.py'), os.path.join(ext, 'romfs'), proj)
    run(os.path.join(HERE, 'lyt_dump.py'), os.path.join(ext, 'romfs'), proj)
    run(os.path.join(HERE, 'tr_import.py'), proj)
    os.environ.setdefault('DQXI_CONDENSE', '0.92')
    # redrawn textures with baked-in text (name-entry keyboard) -> picked up by build_patch via DQXI_TEX_DIR
    tex = os.path.join(work, 'tex')
    run(os.path.join(HERE, 'make_textures.py'), os.path.join(ext, 'romfs'), os.path.join(ext, 'romfs', 'font'),
        os.path.join(PROJ, 'maps'), tex)
    os.environ['DQXI_TEX_DIR'] = tex
    run(os.path.join(HERE, 'build_patch.py'), os.path.join(ext, 'romfs'), proj, build, '--all-layouts')
    # code.bin string patch (battle commands, equipment slots...) -> build/exefs/code.ips
    import blz, shutil
    code = os.path.join(ext, 'exefs', 'code.bin')
    if os.path.exists(code):
        dec = os.path.join(work, 'code_dec.bin')
        open(dec, 'wb').write(blz.decompress(open(code, 'rb').read()))
        run(os.path.join(HERE, 'code_patch.py'), dec, os.path.join(PROJ, 'maps', 'code_strings.tsv'),
            os.path.join(work, 'build_code'))
        os.makedirs(os.path.join(build, 'exefs'), exist_ok=True)
        shutil.copy(os.path.join(work, 'build_code', 'code.ips'), os.path.join(build, 'exefs', 'code.ips'))
    run(os.path.join(HERE, 'verify_build.py'), os.path.join(ext, 'romfs'), build)
    run(os.path.join(HERE, 'make_release.py'), build, os.path.join(work, 'release'), ver)

if __name__ == '__main__':
    main()
