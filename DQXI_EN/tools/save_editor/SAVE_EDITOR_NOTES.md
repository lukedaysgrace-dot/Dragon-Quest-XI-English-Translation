# DQ11 3DS Save Editor (reference for future sessions)

Source: https://github.com/monkheyonepiece/Dragon-Quest-11-3DS-Save-Editor (GPL-3.0).
Packed as `DQ11_3DS_Save_Editor_src.tar.gz` (extract with `tar xzf`, creates `repo/`).

Facts learned (use these to write a Python save patcher; the editor itself is a Windows WPF/C# app):
* Slots are Data0/Data1/Data2 files. CRC32 covers bytes [0, 0xC8A8) and is stored at 0xC8AC.
  After any byte edit, recompute the CRC or the game rejects the save.
* Key code: `DQ11/SaveData.cs`, `Crc32.cs`, `DataContext.cs` (gold 0x3E28/0x3E2C/0x6584, playtime 0x3E24),
  `Character.cs` (stats at base+0x100..0x112, 2 bytes each, max 999).
* `item/en/story.txt` lists party-unlock flags (0x69B5-0x69BC), boat flag (0x6A13), etc.
* It does NOT expose story chapter / map position. To find those, diff saves taken at known story points.
* Emulator save path (Azahar): `.../sdmc/Nintendo 3DS/<id>/<id>/title/00040000/00199200/data/00000001/`.
