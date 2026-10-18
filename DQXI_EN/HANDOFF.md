# HANDOFF — read this first (for the next Claude session)

You are continuing an English fan translation of the **Japanese 3DS Dragon Quest XI**
(title ID 0004000000199200). Everything lives in this folder (`DQXI_EN`); the ROM is the `.3ds` file
in the parent folder, the official English script RTFs are in `../DQXI SCRIPT/`.
`PROGRESS.md` has the full technical record; this file is the short version.

## 1. How Lucas wants this done
* **When he asks a question, answer it and stop.** Don't start working until he says to.
* **All building and testing happens in your cloud workspace, never on his PC.** Use his computer
  only to copy files in and out of this folder.
* **One agent only.** No sub-agents.
* **Never say something works unless you tested it in the emulator.**
* Small, verifiable steps. Keep originals untouched. Update `PROGRESS.md` and this file at the end of
  each stage, and copy results back into this folder (nothing syncs automatically).
* Keep messages short.

## 2. Where things stand (session 5, 2026-10-17)
* Session 5 found that the private files (official-line JSONs, `cob_*/hel_*` map scripts, release
  zips) never made it into this GitHub folder (they are git-ignored). They were **rebuilt from the
  script RTFs** with a new compact map format (`maps/*.omap`, see §5). **Keep the `*.omap` files and
  `text/en/*_official.json` on Lucas's PC** — they are git-ignored on purpose, so a fresh clone
  won't have them. Back them up outside git.
* Translated (official script where the scene matches, fan otherwise), all passing `check_fit`:
  Cobblestone (opening + past/ruined), Heliodor (castle, dungeon, town, downtown, books, quests),
  Manglegrove/Kingsbarrow leftovers, **a_050** (Kingsbarrow, ruined Cobblestone, past Cobblestone,
  Falls, escape), **a_060 Hotto** (cutscenes, NPCs in haiku like the official script, field events,
  party chat, labyrinth, two smith quests), **a_070 Gallopolis** (cutscenes; all chapter-05 town/palace/racetrack/circus NPCs in `r006`; a_070 script
  incl. newspapers; party chat `talk_party_a070`; quests: painter/Wild Side, cactus cutlet chef, Hakim's
  letter part 1 + quest logs),
  quest titles (all 89), story recaps up to Hotto, scenario guide up to Hotto.
* **Seen in-game this session** (Azahar, fresh boot): English name entry, prologue subtitles,
  Gemma headscarf cutscene, Cobblestone villager dialogue with name plates. Everything else is
  fit-checked only.
* Place-name fixes: ダーハルーネ = Gondolia, ソルティコ = Puerto Valor, ナプガーナ = Manglegrove,
  デンダ = Jarvis, 虹色の枝 = Rainbough.

## 3. Next steps
1. Gallopolis leftovers: story recaps + scenario guide entries for a_070 (`maps/story_*.txt`,
   `guide2.txt`); later-act `r006` NPCs (chapters 0x/1x after Act 1) can wait for Act 2.
   Names: アポロ = Hakim, ディアナ = Akia, 勇者の星 = Erdwin's Lantern, ビーストモード = Wild Side,
   ワイバーンドッグ = spitzfire, サボテンゴールド = golden globe.
2. Then a_080 (Gondolia/Puerto Valor), area by area.
3. Play-test Heliodor/Hotto in the emulator when possible; package v0.4 with `tools/make_release.py`.

## 4. Setting up a fresh cloud workspace
1. The ROM is 4 GB and staging caps at 400 MB per file: on Lucas's PC write the used part
   (0xA240E000 bytes) in 390 MiB chunks into `DQXI_EN/work_tmp/rom/` (one python call per chunk —
   background jobs die), stage each, `cat` them in the cloud and pad with 0xFF to 4 GiB
   (SHA-256 `0f04b51b…9b74` = original). Then delete the chunks (ask for delete permission).
2. `pip install numpy pillow --break-system-packages`; `apt-get install xdotool libopengl0 libgl1
   libegl1 libgl1-mesa-dri libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1
   libxcb-render-util0 libxcb-xinerama0 libxcb-image0 libpulse0`.
3. `python3 tools/apply_patch.py rom.3ds work v0.4-dev` (≈3 min).
4. Official script: `pandoc -f rtf -t json` every RTF in `../DQXI SCRIPT/` into a folder, then
   `python3 tools/en_script_parse.py <json_dir> official/rows.jsonl` (row 12140 must be the
   "Sorry, you're not getting through here..." line).
5. Emulator: `https://github.com/azahar-emu/azahar/releases/download/2126.2/azahar.AppImage`,
   `--appimage-extract` into `/home/claude/azahar`. Scripts in `tests_emu/` have CRLF endings on
   Windows — run `sed -i 's/\r$//'` on them. `tests_emu/series.py <name> <n> <secs> [1=press A]`
   grabs a montage of frames (cheap way to watch cutscenes).

## 5. Translating an area (the routine, session 5 version)
1. `tools/dump.py '%a_070_cs%'` (cutscenes), `tools/dump2.py r006 --cond 05` (NPCs grouped by NPC
   and story condition, identical Japanese listed once with all offsets), `tools/rows.py 'NPC - Act 1'
   <start> <count>` / `tools/rows.py -g <regex> [file]` (official script).
2. Write `maps/<area>.omap`: `@pack [entry]`, then `<offsets> o<row>[.<page>]` (official row),
   `o: text` (condensed official), `f: text` (fan), `ow:`/`fw:` (pre-wrapped UI text such as quest
   logs). Later lines override earlier ones, so condensed versions are appended at the end.
3. `tools/go.sh <omap> <NN_prefix>` → `text/en/NN_prefix_official.json` / `_fan.json` + fit check;
   `tools/fails.py text/en/NN_*.json` lists what doesn't fit (3 lines max) in omap form.
   Identical Japanese in other packs gets the same English through the TM automatically.
4. Recaps: append to `maps/story_jp.txt`/`story_en.txt`, run `maps/mk_story.py`.
   Objectives: `maps/guide*.txt`, run `maps/mk_guide.py`.
5. `tests_emu/rebuild.sh` rebuilds and installs into the cloud Azahar.

## 6. Conventions
* `{var:1}` = hero name. Speaker-name plates are separate strings (`text/en/01_names.json`).
* Hotto natives speak in haiku (official style); 3-page official haiku become 3 lines.
* Names: see `00_glossary.json`, `01_names.json`, `72_places.json`.
