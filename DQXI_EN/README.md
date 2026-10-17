# Dragon Quest XI (3DS, Japan) — English fan translation toolkit

Supports: Japanese retail cartridge dump, title ID 0004000000199200, CTR-P-BTZJ, NCCH v2
(fingerprints in PROGRESS.md §1). The dump must be **decrypted** (e.g. GodMode9 "decrypt").

## Building the patch yourself
```
pip install numpy
python3 tools/apply_patch.py "D-Q-XI-S-S-T-o-M-(Japan).3ds" work v0.1
```
Output: `work/release/v0.1/`
* `luma/titles/0004000000199200/` (`romfs/` + `code.ips`) → copy `luma` to the root of the 3DS SD card,
  enable "Enable game patching" in the Luma3DS config (hold SELECT at boot).
* `azahar/load/mods/0004000000199200/` (`romfs/` + `exefs/code.ips`) → copy the `load` folder into the
  Azahar user folder (Azahar: File > Open Azahar Folder).
* `code.ips` translates text hard-coded in the program (battle commands, equipment slots); both parts are needed.
`work/build/report.txt` lists text that may overflow; `work/build/manifest.sha256` checksums every file.

## Translating
Edit or add `text/en/*.json` (format in `tools/tr_import.py`), then rerun `apply_patch.py`
(or `tr_import.py` + `build_patch.py` if you keep the work folder). `tools/progress_report.py` prints coverage.
If you own the official English localization (PC/PS4/Switch), it can be added as a file with
`"source": "official"`; nothing official is included here.

## What may be shared
Share `tools/`, the fan-translation files in `text/en/` (`"source": "fan"` / `"name"`), `README.md`,
`PROGRESS.md`. **Do not share** `text/jp/`, `db/`, `release/`, `build/`, `work_tmp/`, or any `text/en/` file
with `"source": "official"` — those contain data from the copyrighted game or its official script.

## Status
v0.3 released (menus + first battle). In progress toward v0.4: name entry keyboard in English (tested),
Heliodor story/NPC/quest text (translated, play-test pending). Not yet tested: real hardware,
anything after Cobblestone in-game. See PROGRESS.md §10–11.

## Putting this on GitHub
The `.gitignore` in the parent folder keeps out everything that must not be uploaded: the ROM,
`db/`, `release/`, `work_tmp/`, `text/jp/`, the `*_official.json` files and the map scripts that
contain official script lines. Check `git status` before the first push.
