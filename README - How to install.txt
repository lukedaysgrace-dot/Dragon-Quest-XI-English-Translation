DRAGON QUEST XI (3DS, Japanese) - ENGLISH FAN TRANSLATION
How to install
=========================================================

You need:
  - Your Japanese 3DS copy of the game, title ID 0004000000199200.
    In this folder that is:  D-Q-XI-S-S-T-o-M-(Japan).3ds
  - Azahar (3DS emulator for PC), OR a real 3DS with Luma3DS custom firmware.

The patch never changes your game file. It is loaded on top of it every time
you start the game, so you can remove it at any time.


1. PICK ONE VERSION
---------------------------------------------------------
There are two folders in "Claude outputs". Install ONE of them, not both.

  DQXI3DS_EN_voice  - English text + English voices + English movies.
                      (Voices and movies were converted from your own Steam
                      copy of DQXI S. Do not share this folder.)
                      Size: about 1.7 GB.

  DQXI3DS_EN_text   - English text, with the game's original Japanese voices
                      and Japanese movies.
                      Size: about 120 MB.

Both have the same translation, box-size fixes, official names and English
title-screen subtitle. Only the audio and movies differ.

Inside each version folder:
  azahar\load\mods\0004000000199200\romfs\         (the translation files)
  azahar\load\mods\0004000000199200\exefs\code.ips (game code patch)
  code.ips                                          (same file, for a 3DS)


2. INSTALL ON AZAHAR (PC)
---------------------------------------------------------
a) Open Azahar. If the game is not in the list yet: File > Load File...
   and pick  D-Q-XI-S-S-T-o-M-(Japan).3ds , then close the game again.

b) In Azahar's game list, right-click Dragon Quest XI > "Open Mods Location".
   (If that option is missing, open File Explorer, go to
    %APPDATA%\Azahar\load\mods\   and create a folder named
    0004000000199200 .)

c) If there is already a "romfs" or "exefs" folder in there, delete both.

d) Open the version you picked, go into
      azahar\load\mods\0004000000199200\
   and copy the two folders  romfs  and  exefs  into the mods folder
   from step b.

   It must end up like this:
      ...\load\mods\0004000000199200\romfs\
      ...\load\mods\0004000000199200\exefs\code.ips

e) Start the game from Azahar. The title screen should read
   "Echoes of an Elusive Age" under the logo and the menus are in English.


3. INSTALL ON A REAL 3DS (LUMA3DS)
---------------------------------------------------------
a) Put the 3DS's SD card in your PC.
b) Create the folder  SD:\luma\titles\0004000000199200\
   (delete any old "romfs" folder and "code.ips" in it first).
c) From the version you picked, copy:
      azahar\load\mods\0004000000199200\romfs   ->  SD:\luma\titles\0004000000199200\romfs
      code.ips (next to the README)            ->  SD:\luma\titles\0004000000199200\code.ips
d) Hold SELECT while powering on the 3DS to open the Luma menu and turn on
   "Enable game patching". Save, then start the game.
   (Not tested on real hardware yet - only in Azahar.)


4. SWITCHING BETWEEN ENGLISH AND JAPANESE VOICES
---------------------------------------------------------
Close the game, delete  romfs  and  exefs  from the mods folder (Azahar) or
romfs  and  code.ips  from SD:\luma\titles\0004000000199200\ (3DS), then copy
in the other version exactly as in step 2 or 3.
Your save files are not affected - they are kept separately.

To go back to the plain Japanese game, just delete those folders/files.


5. IF SOMETHING LOOKS WRONG
---------------------------------------------------------
- Still Japanese: check the folder is named exactly 0004000000199200 and that
  romfs and exefs are directly inside it (not inside another folder).
  Restart Azahar after copying.
- Voices missing in the voice version: make sure you copied the whole romfs
  folder (it contains a "sound" folder of about 1.4 GB).
- Text running past a box, a wrong name, a Japanese line, or a voice playing on
  the wrong line: take a screenshot or note the scene and report it - it can
  be fixed in the translation files.

Known limits: credits keep the staff names in Japanese (job titles are
English); the 2D-mode title logo is an unused placeholder and was left as is.
