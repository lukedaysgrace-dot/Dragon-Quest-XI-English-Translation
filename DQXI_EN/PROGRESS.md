# DQXI 3DS English Translation — PROGRESS

Last updated: 2026-10-15 (session 2, Cobblestone)

## 0. Status at a glance

| Stage | State |
|---|---|
| ROM inspection, ExeFS/RomFS extraction | **done** (own extractor, decrypted image) |
| Archive / compression formats (PACK, PACA=BLZ, SARC) | **done**, byte-identical round trip on all 3,021 packs and 401 SARCs |
| Text format (BXON), control codes, furigana | **done**, lossless decode/encode |
| UI layout text (BFLYT txt1) | **done** (dump + rewrite + buffer enlargement) |
| Fonts (BFFNT, ASCII present) | width-table patch done; glyph art untouched |
| Insertion pipeline + structural verifier | **done**, 0 verifier errors |
| Proof-of-concept translation (title/menus, opening, first battle) | **written** (727 unique strings) |
| In-game testing (emulator/hardware) | **started** — Azahar 2126.2 (headless, cloud workspace): title → new game → prologue → first village verified (§6) |
| Full translation | ~1.6 % of unique Japanese strings |

> Items marked "in-game ✅" in §6 were seen on screen in Azahar. Everything else is verified at the
> file level only. Real 3DS hardware has not been tested.

## 1. Game image (confirmed)

* File: `D-Q-XI-S-S-T-o-M-(Japan).3ds`, 4 GiB NCSD (CCI), **decrypted** (NCCH flags[7] = NoCrypto).
* Title ID `0004000000199200`, product code `CTR-P-BTZJ`, NCCH version 2, internal name `triple`.
* Revision fingerprints (from the NCCH header, cheap to check):
  * ExeFS superblock SHA-256 `9f7d0958c2cf466e84f5728030807b64c74098534e568577226d1c8aabafb7e6`
  * RomFS superblock SHA-256 `c31bd48e52ac95735779ea39d98c069bdd1c6afd32fc5ad7192bd378191eb9df`
  * exheader (first 0x400) SHA-256 `29fcfa7cb27fd3eb116b5f47cfa0e7a055c00f07e8d953fa01dc72ddf26d158d`
  * code.bin (BLZ-compressed, as on card) SHA-256 `ea3d2c02780e7d7406137cc5099e2ccdf9da4a90f48f35f97d59f0a08c298a2f`
* ExeFS: `.code` is BLZ-compressed (3.9 MB -> 7,090,176 bytes; text 0x100000, ro 0x725000, data 0x79b000).
* RomFS: 21,250 files, 2.53 GB. Text-relevant: `script/` (769 .pack), `param/` (551), `ui/` (398 .pack),
  `gamecmn/syscmn/battlecmn/fieldcmn/divecmn/2dcmn.pack`, `font/` (6 .bffnt).

## 2. Formats (confirmed against data and code.bin)

### PACK / PACA archive (`tools/pack.py`)
```
0x00 'PACK' | 'PACA'   0x04 u32 total size   0x08 u16 0x0100, u16 0xFEFF
0x0C u16 count   0x0E u16 table offset (0x18)   0x10 u32 end of table   0x14 u32 archive hash
0x18 u32 offsets[count], then u32[2*count] per-entry name hashes (kept verbatim)
entry: u16 header size, u16 align flag, u32 data size, name[], data, pad to 4
```
* **PACA = the whole file BLZ-compressed** (same backward-LZ as ExeFS .code; header/table stay raw at
  the front because BLZ compresses from the end). `total size` is the decompressed size.
* The per-entry 8-byte table values depend only on the entry *name* (identical data with different
  names gives different values) → no content checksum; safe to change data.
* code.bin fn @0x0056f7a4 parses PACK entries (`ldrh [r4,#0xc]` count, `[r4,#0xe]` table, entry `ldrh [r6]`
  header size, `[r6,#4]` size) and accepts both `PACK` and `PACA` magics (strings @0x789df4/0x789dfc).
* Rebuild is byte-identical for all 3,021 packs tested. Output is written as raw `PACK` (see bug list).

### BXON data container (`tools/bxon.py`)
* `BXON`, version 1, type hash, type name (e.g. `CharacterIEData`, `TextBlock`, `UIText`, `BattleText`,
  `ItemParam`...), then `u32 count, s32 relptr`.
* **All pointers are self-relative signed 32-bit**; every pointed-to block is preceded by the marker
  `&&&&` (0x26262626) and padded with `@` (0x40).
* Strings: UTF-16LE, NUL-terminated, each in its own block. Insertion: in place if it fits, otherwise
  a new block is appended at EOF and every pointer to the old block is redirected. Nothing else moves.

### Text encoding / control codes (`tools/textcodec.py`)
| raw | meaning | editable form |
|---|---|---|
| `0001 base 0002 reading 0003` | furigana | `{ruby:base|reading}` |
| `0004 N` | runtime variable N (1 = hero name, 2/3 = actor/target, 5–7 item/spell names, 8–15 numbers) | `{var:N}` |
| `000D 000A` | line break (dialogue) | `\n` (nl=crlf) |
| `000A` | line break (UI) | `\n` (nl=lf) |
| other < 0x20 | kept verbatim | `{x:XXXX}` |
* `%ls`, `%d`-style printf tokens also occur and are kept verbatim.
* Every message is **at most 3 lines = one window page**; long conversations are multiple strings.
  There is no page-break code, so English must fit 3 lines.

### SARC + BFLYT layouts (`tools/sarc.py`, `tools/lyt.py`)
* 401 SARCs (UI layouts, BCLIM/BFLIM textures, animations); rebuild byte-identical.
* `txt1` pane: `0x54 u16 textBufBytes`, `0x56 u16 strBytes`, `0x5A font idx`, `0x64 text offset`,
  `0x70 font size`, `0x80 textID offset`. 7,785 Japanese panes (6,415 real, 1,119 unique; the rest are
  placeholders such as `ああああ`).
* `textBufBytes` is the runtime capacity of the text box: strings set by the game code longer than this
  are truncated by the layout library. Builds raise every buffer to ≥256 bytes.

### Fonts (`tools/bffnt.py`, `tools/font_patch.py`)
* FFNT v4, one 1024×1024 A4 sheet each, CMAP covers full ASCII in every font.

| font | used for | ASCII widths (orig.) | patch |
|---|---|---|---|
| 3D14 | 3D dialogue (15×16) | proportional | space 14→5 px |
| 3D12 | 3D small UI | proportional | — |
| 2D14 | 2D dialogue (15×16) | **monospace 12 px** | proportional: left 0, advance = glyph+1 (digits kept tabular), space 4 |
| 2D9  | 2D battle text (11 px) | **monospace 11 px** | same as 2D14 |
| 2D14SH | 2D outlined | proportional | space 5 |
| credit2D | staff roll | 218 glyphs | not yet |

### Window geometry (from layouts)
| window | layout | width | font | lines |
|---|---|---|---|---|
| 3D talk | common_2way `win_talk_3d.bflyt` txt1/txt2 | 350 px | 3D14 | 3 |
| 2D talk | common_2way `win_talk_lw_2d.bflyt` txt | 300 px | 2D14 | 3 |
| 2D battle message | battle_2d `win_talk_2d.bflyt` txt | 338 px | 2D9 | 3 |
Auto-wrap (`tools/wrap.py`) makes every dialogue line fit **both** the 3D (346 px) and 2D (296 px) window.

## 3. Text inventory

* 81,206 BXON strings (43,321 unique after furigana removal) + 6,415 layout strings.
* Biggest groups: NPC/event dialogue `CharacterIEData` 32.5k, `TextBlock` (cutscene captions + field
  messages) 9.8k, `BattleText` 7.7k, party chat `TalkPartyContent2` 6.0k, items `ItemParam` 5.5k.
* Japanese text dumps: `text/jp/**.json` (generated from your ROM — **do not distribute**).

## 4. Translation coverage

Coverage counts a string as done if it has its own English or its Japanese is in the translation
memory (so speaker names propagate everywhere). "unique covered" is the honest measure of work done.

| data type | strings | covered | unique JP | unique covered | % |
|---|---:|---:|---:|---:|---:|
| CharacterIEData | 32496 | 1927 | 17520 | 33 | 5.9% |
| TextBlock | 9819 | 2717 | 5438 | 38 | 27.7% |
| BattleText | 7670 | 1160 | 3092 | 131 | 15.1% |
| LYT | 6415 | 1016 | 1119 | 143 | 15.8% |
| TalkPartyContent2 | 5982 | 0 | 4783 | 0 | 0.0% |
| ItemParam | 5539 | 5 | 2052 | 2 | 0.1% |
| UIMapParamSet | 1842 | 0 | 194 | 0 | 0.0% |
| ChurchMsg | 1653 | 0 | 273 | 0 | 0.0% |
| UIText | 1576 | 535 | 830 | 273 | 33.9% |
| CreditTextData | 1520 | 0 | 722 | 0 | 0.0% |
| UIMessage | 1404 | 80 | 569 | 53 | 5.7% |
| EnemyBaseParam | 1064 | 6 | 741 | 3 | 0.6% |
| EnemyBookParam | 1022 | 4 | 744 | 1 | 0.4% |
| CSChapterParam | 940 | 1 | 805 | 1 | 0.1% |
| AchievementParam | 894 | 0 | 859 | 0 | 0.0% |
| ShopMsg | 840 | 0 | 161 | 0 | 0.0% |
| UIStoryFlagRelation | 684 | 0 | 479 | 0 | 0.0% |
| EnemySpecialAttack | 671 | 9 | 382 | 3 | 1.3% |
| QuestUIParam | 634 | 0 | 592 | 0 | 0.0% |
| ItemFailureMessage | 588 | 0 | 127 | 0 | 0.0% |
| PassiveSkillParam | 464 | 0 | 86 | 0 | 0.0% |
| DummyPlayerMessage | 430 | 0 | 430 | 0 | 0.0% |
| UIGuideParam | 419 | 0 | 314 | 0 | 0.0% |
| CasinoMsg | 354 | 0 | 75 | 0 | 0.0% |
| SpiritNameTableRow | 306 | 0 | 306 | 0 | 0.0% |
| SpiritTalkParam | 300 | 0 | 70 | 0 | 0.0% |
| UITutorialParam | 222 | 13 | 177 | 7 | 5.9% |
| DummyPlayerName | 199 | 0 | 199 | 0 | 0.0% |
| ItemAdditionalEffec | 194 | 8 | 192 | 8 | 4.1% |
| BankMsg | 189 | 0 | 44 | 0 | 0.0% |
| InnMsg | 150 | 0 | 26 | 0 | 0.0% |
| LevelAreaCommonPara | 120 | 2 | 100 | 2 | 1.7% |
| JewelShopMsg | 90 | 0 | 26 | 0 | 0.0% |
| QuestIDParam | 89 | 0 | 89 | 0 | 0.0% |
| UIAnotherNameParam | 80 | 0 | 34 | 0 | 0.0% |
| SavePointMsg | 63 | 18 | 20 | 6 | 28.6% |
| ScenarioIDParam | 52 | 0 | 52 | 0 | 0.0% |
| SerenHintMessage | 51 | 0 | 17 | 0 | 0.0% |
| ProgramParam | 49 | 9 | 49 | 9 | 18.4% |
| PanelsRou | 38 | 0 | 28 | 0 | 0.0% |
| UIDetailRecordParam | 35 | 0 | 21 | 0 | 0.0% |
| PastWorldParam | 33 | 0 | 33 | 0 | 0.0% |
| TalkParty2DOverwrit | 32 | 0 | 4 | 0 | 0.0% |
| PlayerInitializePar | 30 | 17 | 21 | 9 | 56.7% |
| PanelsHero | 28 | 0 | 25 | 0 | 0.0% |
| PanelsCamu | 27 | 0 | 22 | 0 | 0.0% |
| SmithArtParam | 26 | 0 | 26 | 0 | 0.0% |
| PanelsVeronica | 26 | 0 | 24 | 0 | 0.0% |
| PanelsEXSena | 25 | 0 | 23 | 0 | 0.0% |
| RuraPointParam | 24 | 1 | 23 | 1 | 4.2% |
| PanelsSena | 24 | 0 | 19 | 0 | 0.0% |
| PanelsMartina | 23 | 0 | 21 | 0 | 0.0% |
| PanelsGraig | 21 | 0 | 19 | 0 | 0.0% |
| RevivalPointParam | 20 | 2 | 19 | 1 | 10.0% |
| PanelsSylvia | 20 | 0 | 20 | 0 | 0.0% |
| ShopTypeText | 18 | 0 | 5 | 0 | 0.0% |
| TrainingTrialParam | 17 | 0 | 17 | 0 | 0.0% |
| NPCJockeyVisualPara | 16 | 2 | 15 | 2 | 12.5% |
| PastAltarParam | 11 | 0 | 11 | 0 | 0.0% |
| PokerHandParam | 10 | 0 | 10 | 0 | 0.0% |
| SpecialRevivalSpell | 7 | 0 | 7 | 0 | 0.0% |
| SavePointParam | 7 | 1 | 7 | 1 | 14.3% |
| ItemFukubikiParam | 6 | 0 | 6 | 0 | 0.0% |
| HorseRaceRankParam | 6 | 0 | 6 | 0 | 0.0% |
| PrizeshopParam | 5 | 0 | 5 | 0 | 0.0% |
| SpiritPresentParam | 5 | 0 | 5 | 0 | 0.0% |
| SmithMaterialParam | 4 | 0 | 4 | 0 | 0.0% |
| MiniGameCategoryPar | 3 | 0 | 3 | 0 | 0.0% |
| **total** | 87621 | 7533 | 44237 | 727 | 8.6% |

DB status column: skip=1342, translated=7533, untranslated=80088

## 5. Tools (all in `tools/`)
| tool | purpose |
|---|---|
| `ctr_extract.py` | NCSD/NCCH → exheader, ExeFS, RomFS (+ index with image offsets) |
| `blz.py` | BLZ decompression (ExeFS code, PACA) |
| `pack.py` | PACK/PACA list/extract/rebuild |
| `bxon.py` | BXON string discovery and relocation-safe replacement |
| `textcodec.py` | lossless UTF-16 ⇄ editable text with control codes |
| `sarc.py`, `lyt.py` | SARC rebuild, BFLYT text panes (dump/edit/buffer growth) |
| `bffnt.py`, `font_patch.py` | font reader, sheet decoder, width patch |
| `text_dump.py`, `lyt_dump.py` | build progress DB + Japanese JSON dumps |
| `tr_import.py` | import `text/en/*.json` (translation memory + per-id) |
| `wrap.py` | pixel-accurate wrapping with the game fonts |
| `build_patch.py` | rebuild all affected files into a RomFS overlay + report + SHA-256 manifest |
| `verify_build.py` | structural checks of every rebuilt file against the original |
| `make_release.py`, `apply_patch.py` | LayeredFS packaging; one-shot build from a ROM |
| `progress_report.py` | this coverage table / CSV |

## 6. Tests

| test | result |
|---|---|
| PACK rebuild, 3,021 packs | byte-identical |
| SARC rebuild, 401 archives | byte-identical |
| BXON decode→encode, all strings | lossless |
| Build v0.1-poc: 420 packs, 6,517 BXON strings, 1,016 layout panes | verifier: 0 errors |
| v0.1 full patch in Azahar | **crashed** ~3 s after boot (heap free-list corruption, PC 0x55E968 / 0x6F1C9C) |
| bisect (fonts+cmn packs / +UI packs / UI text-only / UI layouts without buffer growth) | ok / crash / ok / ok → cause: enlarging every BFLYT text buffer to 256 B overflowed the fixed UI heap. Fixed: buffers left at original size (`DQXI_MIN_BUF=0`). |
| raw `PACK` written where the game shipped `PACA` | in-game ✅ (loads fine) |
| v0.2 boot, LayeredFS 850 files | in-game ✅ no errors in log |
| title menu (New adventure log / Revival password / Enter present code) | in-game ✅ |
| adventure-log slots, "Creating adventure log..." 3-line system message | in-game ✅ |
| prologue cutscene subtitles (a_010_cs_030), "Sixteen years later" | in-game ✅ (the subtitle renderer also wraps on its own) |
| 3D cutscene dialogue window with `{var:1}` hero name, 3 wrapped lines | in-game ✅ (longest line touched the frame → wrap width cut to 326 px) |
| 3D field message window (Circle Pad tutorial, a_010 ie.bxon) | in-game ✅ |
| furigana (ruby) rendering of untranslated Japanese next to English | in-game ✅ (no interference) |
| first battle, 2D-only mode, menus | not reached yet |
| real hardware (Luma3DS) | not tested |

## 7. Known issues / risks (untested until emulator run)
1. ~~Raw PACK instead of PACA~~ — verified working in Azahar.
1a. **Text-box buffers cannot be enlarged globally** (crash). Strings the game code writes into
   layout panes at runtime are capped at the pane's original buffer (Japanese length). Long English
   item/monster names in such panes may be truncated → enlarge only specific panes, measured one by one.
2. Relocated strings make BXON files larger (dead old blocks remain). If some loader uses a fixed
   buffer this could overflow → re-layout the string area to reclaim space.
3. Dialogue with `{var:1}` (hero name) is wrapped assuming ≤8 characters.
4. Name entry keyboard is kana-only. The character grid comes from UTF-16 tables in code.bin
   (.rodata @0x72EF3C hiragana / katakana / dakuten conversion). Plan: replace with A–Z / a–z via a
   `code.ips` (Luma `luma/titles/<tid>/code.ips`, Azahar `mods/<tid>/exefs/code.ips`). Name limit is 6.
   The confirm prompt and "Name" label are translated in v0.2.
5. English articles/plurals for monster names (`{var:2}`) are handled by neutral phrasing.
6. UI width warnings in `build/report.txt` use the Japanese string width as the limit (pessimistic);
   real limits must be checked on screen.
7. Text baked into textures (title logo, some UI images) not yet inventoried.
8. The user supplied the official English script (30 RTF files, 36,444 rows; parsed by
   `tools/en_script_parse.py`). It is English-only and not in game-data order (e.g. region file r001 has
   2,311 Japanese strings across story states vs 239 English rows for Cobblestone), so it must be
   matched by meaning, not position. Lines taken from it are kept in files with `"source": "official"`
   and must not be redistributed.


## 9. Cobblestone (session 2)

* NPC dialogue in `param/region/r001.pack` (`npc_ie.bxon` 2,311 strings, `book_ie.bxon` signs/notes) is
  organised as NPC slot → story-condition table → lines (`tools/ie_struct.py`). Condition byte 0 = chapter
  (00 = opening Cobblestone, 03 = past Cobblestone / ruined village, 0f/1d/1f/34 = later acts).
* Translated: all opening-era Cobblestone NPCs (incl. windcutter-feather side quest, Zeckendorf, camp
  instructor, border guards), the past-Cobblestone visit and ruined village, signs and Dunstan's pun notebook,
  and the 16 a_010 cutscenes (birth → village → Tor → Luminary reveal → departure → Heliodor gate).
  526 strings / 437 unique Japanese lines. Source mapping files: `maps/cob_*.py`.
* Official script used where the scene exists (matched by meaning, not position); lines were condensed where
  they did not fit 3 lines. Fan-translated where the 3DS has content the script lacks (quest giver,
  Zeckendorf, sign posts, pun notebook, guards' variants, "Sixteen years later").
* In-game verified (Azahar): village NPC lines, Dunstan/Amber send-off with speaker name plates,
  Gemma's walk-to-the-Tor dialogue, all within 3 lines.
* **Found:** a 4th line is never shown (no auto-scroll) → `wrap.py` now flags >3 lines and all Cobblestone
  text was re-cut to fit. The fonts have no em-dash / curly apostrophe / accented letters (they are silently
  dropped) → `build_patch.py` maps — to ―, ’ to ', é to e, etc.
* Still to verify in-game: the first battle on the Tor, 2D-only mode, the ruined-village scenes.

## 10. First battle and menus (session 3) — release v0.3-menus-battle

**In-game verified (Azahar, cloud emulator, 3D mode):** boot → save → Cobblestone → Tor shrine prayer →
first slime battle → victory → back in the field, no crash. Battle commands (Fight/Tactics/Switch/Flee,
Attack/Spells/Defend/Skills/Items/Equip), enemy list ("Slime  3"), attack/damage/defeat/drop messages
("Slime C attacks!", "Sandy takes 3 damage!", "Slime A is defeated!", "... obtained Medicinal herb."),
"Follow orders" / "View status" on the bottom screen, Items list + details, Equip screen, Stats screen.

**New translation files (text/en):** 62_items (1,087 names), 64_item_desc (968 descriptions, pre-wrapped
to the 116 px detail window), 63_battle_acts (skills/spells/status names + 330 descriptions, wrapped to the
90 px battle help window), 65_scenario_guide (opening objectives), 66_hero_titles, 67_menu_msgs (item/equip/
save/menu messages), 68_tutorials (all 177 tutorial pages), 69_program_param, 70_cs_lastlines,
71_battle_text (1,443 battle messages: ailments, buffs, pep powers, enemy actions).
Spell names follow series English (Frizz, Crack, Zap, Kazapple, Oomph...). A few are guesses and are
marked fan (e.g. Kasizzlezzle, Landmine series, Regen).

**Code patch (new): `tools/code_patch.py` + `maps/code_strings.tsv` → `exefs/code.ips`.** Battle command
labels, equipment slot names and a few others are UTF-16 literals inside code.bin, not data files.
Strings that fit are overwritten; longer ones are moved into the unused padding at the end of .text
(0x724040–0x725000) and the `add rX, pc, #imm` that loads them is rewritten to `ldr rX, [pc, #off]`
with the old slot holding the new pointer. Also changes the enemy-letter format `%ls%c` → `%ls %c`
("Slime A"). Luma: `titles/0004000000199200/code.ips`; Azahar: `mods/0004000000199200/exefs/code.ips`.
Verified working in-game.

**Fixes:**
* CRASH in cutscene a_010_cs_040 (Gemma's headscarf) — caused by growing every layout text buffer
  (BUF_SCALE 2.5). Growth is now OFF by default; only whitelisted panes grow (`tools/grow.txt`, the
  tutorial window). Verified: cutscene plays through.
* Extractor missed the last string of a BXON when it ended at EOF without '@' padding (e.g. Gemma's
  "{name}, they're coming this way!" before the battle). Fixed in `bxon.py`; re-extraction found 359 more
  strings (89,322 total).
* All UI text panes are condensed horizontally to 92 % (`DQXI_CONDENSE=0.92`) to give English room;
  list item names longer than the 130 px list pane got short forms (`maps/items_short.txt`).
* Stat labels shortened ("Mag. might", "Mag. mend") – previously truncated.

**Known issues / not yet checked:**
* Hero name still Japanese kana (name-entry keyboard patch still to do — it is the next code.ips item).
* 2D-mode battle screens not yet looked at in-game (same data, different layouts).
* Victory EXP/gold window and level-up text passed too quickly to screenshot — recheck.
* Battle help-window descriptions only checked by measurement, not on screen.
* Build command: `DQXI_CONDENSE=0.92 python3 tools/build_patch.py <romfs> <proj> build --all-layouts`
  then `tools/code_patch.py code_dec.bin maps/code_strings.tsv build_code` and copy `code.ips` to
  `build/exefs/`.

## 11. Checks + Heliodor (session 4) — work in progress toward v0.4

**Verified in-game (fresh boot, Azahar 3D mode):** name-entry keyboard in English (typed "Eleven"),
confirm prompt, save-slot list ("Cobblestone Tor"), story-recap screen; 2D-style and 3D battles;
victory messages ("You defeated Slimes!", drop + "obtained Medicinal herb."); battle Items list with
one-line descriptions (U+3000 now as narrow as a space); bottom-screen item label now breaks at a word
("Cobblestone / blade", new `62b_item_names_2line.json`, built by `maps/mk_item2line.py`).
Still to look at on screen: one-line EXP/gold message, widened target-name window, skill help window.

**Heliodor translated (not yet seen in-game):**
| file | content | lines |
|---|---|---|
| 80_heliodor_cs | castle gate, King Carnelian, dungeon, sewers, dragon, cliff jump (a_010_cs_130/140, a_020) | 76 |
| 81_heliodor_cs2 | chapel, Erik joins, camp + Fun-Size Forge, woodcutter/Tricky Devil, Downtown, Ruby, sentry, Derk (a_030) | 219 |
| 82_heliodor_npc | r021 NPCs for chapters 00–03/06: town, castle, downtown, cat/Bev/tourist/Harmachis/hide-and-seek quests | 576 |
| 83_heliodor_misc | field events (script a_020/a_030), Erik's party chat a020/a030, foothills chapel + Real Decoy quest (r002) | 88 |
| 84_heliodor_book | r021 book_ie: Erik's hints, dog girl, Cammo, Ruby's letter, tunnel digger, bookshelves | 255 |
| 85_quests_a1 | quest titles + quest log texts for the Cobblestone/Heliodor quests | 49 |
| 86_manglegrove | Manglegrove (r003) + Kingsbarrow surroundings (r004) | 42 |
Official script used wherever the scene matches (by meaning); 3DS-only or different lines are fan
translations (e.g. 3DS-only quest dialogue, Erik's 3DS party chat). Names: Tricky Devil, Flint, Derk,
Ruby, Roxy (3DS "Diana"), Mistress Bev, Cammo, Bullseye, Amelia (the cat).

**New checks / tools:**
* `tools/check_fit.py <db> <font_dir> <files.json>` — wraps every line exactly like the build does and
  flags anything over 3 lines (the game never shows a 4th line) or too wide. All new files pass.
* `tools/wrap.py` now accounts for the 92 % horizontal condense and can break after an em dash.
* `tools/apply_patch.py` now also builds the redrawn name-entry keyboard textures (`make_textures.py`).
* `maps/_paths.py` — map scripts no longer have hard-coded paths (env vars DQXI_TOOLS/FONTS/DB/OFFICIAL_ROWS).
* `tests_emu/` — the headless emulator harness, incl. `nav.py` (walks the hero using the 2D map on the
  bottom screen) and `fight.py`.

## 8. Next steps
1. Play through Heliodor in the emulator (castle → dungeon → chapel → Downtown → Derk → Manglegrove),
   fix anything that overflows or crashes; check EXP line, target window, skill help window.
2. Release v0.4 (Cobblestone + Heliodor), sync to the Azahar mods folder.
3. Continue story in scenario order: Cobblestone return/Kingsbarrow (a_040/a_050), then Gallopolis (a_060+);
   remaining scenario guide, story recaps, party chat, books/signs and quests along the way.
4. Real-hardware test (Luma) when possible.

## 12. Session 5 (2026-10-17) — rebuilt private files, a_050 → a_070
* Private (git-ignored) files were missing from the PC copy, so the official-line mappings were rebuilt
  from the script RTFs with `tools/omap2json.py` (`maps/*.omap` → `text/en/*_official.json` / `_fan.json`).
* New areas, all `check_fit` problems: 0: a_050 (Kingsbarrow / ruined + past Cobblestone), a_060 Hotto
  (cutscenes, haiku NPCs, party chat, quests), a_070 Gallopolis (cutscenes `89_`, NPCs `89b_`,
  script + party chat `89c_`, quests + quest logs `89d_`), quest titles, story recaps / guide up to Hotto.
* Rebuild: packs 705, entries changed 862, errors 0. No a_070 string in the overflow report.
* In-game verified this session: name entry, prologue, Gemma cutscene, Cobblestone NPCs.
  **Hotto and Gallopolis are fit-checked only — not yet seen in the emulator.**

## 13. Session 6 (2026-10-21) — cutscene (cs_text) packs, a_180 → c_020_cs_105
* Translated ~300 `cs_text.bxon` cutscene packs (`maps/cs_<pack>.omap`): a_180, all of b_010–b_170
  (Sword of Light forging, Indignus, Jasper, Mordegon, epilogue, Time's Sphere decision) and c_010–c_020_cs_105
  (past-timeline Heliodor, Calasmos reveal, Watchers' village, Morcant/Seer reveal). All `cs_run` = "problems: 0".
* Patch was rebuilt once mid-session (includes up to ~b_060). Everything later is **fit-checked only**,
  not rebuilt or seen in the emulator (late-game scenes can't be reached from the current save).
* **All 350 cs_text packs are now translated** (through y_010_cs_050). Patch was rebuilt with everything (0 errors) and boots
  in Azahar without crashing; the late-game cutscenes themselves are still not reachable from the save, so only seen = boot + early game.
* Name fixes this session: Octagonia fighters use official names (Vince, Underdigger, Abominable Showman, Sinderella, Whambelina,
  Golden Boy, Arachtor) — r017_e/r022_* were corrected from "Humphrey". Tickington/Tockle/-tchi, Kurutchi, Jorocchi, Lord Dragon,
  Wyrmalroth, Zomaiden, Psaroid, Nimclops, Mortamammoth, Hoopthorne, Orgodelotl, Hunkorvus, Nelgelas, Friend of Time per official/3DS.
* Remaining categories: talk_content (talk_party a100+), ie.bxon cutscene/b-series, enemy_book, achievement,
  cutscene_chapter_param, staffroll_text_1/2, passive_skill, dummy_player_message/name, quest_ui_param, scenario_guide,
  spirit_* tables, script_message, ui_profile_text, item_add_effect_text, quest_param, casino slot_msg, misc,
  ~237 cosmetic overflows in m2d_ui_map_param. Then rebuild (`tests_emu/rebuild.sh`), retest in emulator, re-sync.

## Session 7 (enemy book + achievements)
- Achievements: `maps/ach_gamecmn_ach.omap` (243 records), sources/builders in `maps/src_ach/` (ach_build.py wraps at 290 px, 3 lines).
- Enemy book (monster descriptions, 740 records): `maps/eb_record_3d_eb.omap`, `text/en/30_eb_record_3d_eb_fan.json`. Sources in `maps/src_enemybook/` (eb_1..7, eb_90 = generated from the two template sentences + names.json from enemy_base). Build: copy /tmp/cs/eb.txt (dump via tools/dump2.py record_3d enemy_book.bxon) to record_3d_eb.txt, run eb_build.py (LIM=160 px, max 4 lines), then `tools/cs_run.sh enemy_book.bxon eb record_3d_eb`.
- grow.txt: `menu_senreki_monster_3d.bflyt|txt_place=512`.
- Verified in emulator: Records menu, Quest list, Monster list (English). Monster descriptions and the Titles list are NOT viewable (unseen entries show ?????) - unverified in game. tools/check_fit.py reports ~80 "too wide" for enemy book because it uses JP widths; real pane is 160 px.
- Still untranslated (priority): passive_skill, quest_ui_param, scenario_guide, spirit_*, ui_profile_text, item_add_effect_text, script_message, cutscene_chapter_param, staffroll, battle_Text, dummy_player_*, quest_param, talk_party_*.

## Session 7b (menu text batch)
Built from sources in `maps/src_qu/` (qu_*.txt = quest_ui_param 392 recs via qu_build.py LIM=240; sg_1.txt = scenario_guide 234 recs via sg_build.py LIM=265, max 2 lines; ps_en.txt = passive_skill; st_en.txt = spirit_talk_param (Yotch lines); pf_en.txt = ui_profile_text; ie_en.txt = item_add_effect_text; sm_en.txt = script_message). spirit_name_table = katakana->romaji via `tools/kana2en.py` (made-up Yotch names).
Maps: maps/{qu,sg,ps,sn,st,pf,ie,sm}_*.omap. Names follow the Switch-official glossary found in the DB tm table (Octagonia, Phnom Nonh, Champs Sauvages, Gallopolis, Sniflheim, Lonalulu, Angri-La, Arboria, Havens Above, Irwin = Arwin, Erdwin = Roshu, Diego, Kinai, Romia, Zwaardsrust, Mount Pang Lai, Mount Huji, Cetacea ...). tm (select jp,en from tm) is the best name source - query it before inventing names.
Verified in emulator (reachable only): Search message ("searched the ground / But found nothing"), Records > Story so far, Quest list, Monster list, Item menu. NOT viewable early: passive skills, item effects, quest log details, scenario objectives, profile, Yotch lines, monster descriptions -> unverified in game; check_fit.py limits are derived from JP widths and flag most of them (real panes are wider).
Remaining untranslated: cutscene_chapter_param (866), staffroll_text_1/2 (760 each), battle_Text (724 x2), dummy_player_message (431) + dummy_player_name (198), quest_param (82), talk_party_* (~6000), d021c ie, LYT strings.

## Session 7c
- Added: `qp_gamecmn_qp.omap` (quest titles, 82), `cc_gamecmn_cc.omap` (cutscene chapter titles, 744 unique JP), `dm_fieldcmn_dm.omap` (StreetPass dummy lines, 431), `dn_fieldcmn_dn.omap` (dummy names, 198). Sources/builders in `maps/src_qu/` (qp_*, cc_en1.txt, gamecmn_cc.*, fieldcmn_dm/dn.*, dm_build.py).
- Rebuild 0 errors, boots; Records > Quest list still works. Quest titles, chapter titles (cutscene viewer), StreetPass text are NOT viewable early -> unverified in game; chapter-title widths unchecked (check_fit uses JP widths and flags them).
- Emulator keys on field: `z` = open menu, `g` = down, `h` = right, `s` = back, `a` = confirm.
- Still untranslated: staffroll headings, talk_party_* (~6000), some ie packs (d021c/a_150/b_060/b011c/b012c), LYT strings.

## Session 7d - in-game verification with a test save
- `tools/mksave.py` builds a test save from the Save Editor's layout (quests mixed Active/Clear/Done, all titles, all monsters, all tools+gear in bag, CRC fixed). Backs up to Data0.orig. Stop emulator first. Load via boot_save.sh + to_green.sh.
- Emulator keys on field: z=menu, g=down, h=right, s=back, a=confirm. Item-list pages via h.
- Found + fixed in game: (1) quest titles overflowed the 180 px list column -> now official Switch names (official/rows.jsonl "Misc - Quest Text") where they exist, else short own names (maps/src_qu/qp_fix.py, qp_over.json); (2) quest status badges were Japanese textures (icon_quest_order/clear/achievementtga) -> redrawn Active/Clear/Done by tools/badge_tex.py via make_textures.py; (3) Misc menu help text overflowed -> rewrote 5 strings in 10_ui_core.json; (4) item descriptions wrapped mid-word (game wraps by character) -> tools/rewrap_idesc.py pre-wraps 968 descriptions at <=124px (3D12) / 115 (2D14), 17 shortened in maps/idesc_short.json; (5) Equip popup heading was a 2nd literal in code.bin (0x19c9d8) -> added to code_strings.tsv.
- Verified in game: Quest list (all 12 pages + detail pane), Monster list entries/descriptions (sampled 16), Misc menu, Items (all 168 consumable/material descriptions), Equip screen, Stats.
- NOT yet verified: Titles/achievements screen, passive skills/Skill panel, gear-effect text, equipment (weapon/armour) descriptions, profile text, Yotch (Tockle) screens, cutscene viewer chapter titles, StreetPass text, late-game dialogue.
- Known small things: Quest list entry 90 is a blank placeholder; quest-complete popup texts still use older names for a few quests ("Bunny Once More" vs official "A Rush of Blood").

## Session 7e
- Trimmed 13 tutorial pages (68_tutorials.json) to <= the Japanese line count; Skill Panel tutorial verified fitting in game.
- Skill Panel screens: translated static labels (Need/Have, Panel status:, MP cost:, Learned, Condition:, Points used, Gold needed:, Skills to reset) via 60_menus_lyt.json + widths in tools/grow.txt; spread the Swords/Greatswords summary columns (menu_skill_get_3d). Verified in game: Skill Panel main, node view, summary.
- Title names shortened (maps/src_ach/title_short.json), "Unused" key added to 10_ui_core.json, mksave.py updated (243 titles, hero lv40) - rebuilt 0 errors.
- Still NOT verified in game: Titles pages 6-16, gear bag descriptions, passive skills / Skills tab, gear-effect text, profile text, Tockle screens, cutscene viewer chapter titles, StreetPass text, late-game dialogue. Untranslated layout strings that remain are mostly dev placeholders (not shown).
- Emulator: after boot_save, ~45 presses of `a` are needed to clear the Gemma opening dialogue before `z` opens the menu. Misc menu = z, h, g g g, a; Skill Panel = 5th entry.
