# Emulator test harness (Linux, headless)

Scripts used to play-test the patch in Azahar running under Xvfb (no screen needed). Paths inside
are for the original cloud workspace (`/home/claude/...`); adjust `emu.sh` / `rebuild.sh` for your machine.

* `emu.sh` – start/stop Azahar on Xvfb :99, screenshots, key presses (xdotool)
* `snap.sh` – screenshot of the two 3DS screens; `state.sh` – save/load emulator save states via the menu
* `boot_save.sh`, `to_green.sh`, `to_battle2.sh` – boot, load in-game save 1, walk to the first battle
* `nav.py` / `navbg.sh` / `navwait.sh` – closed-loop walking in 3D mode using the bottom-screen 2D map
  (phase correlation of the map scroll) – `nav.py walk N 120 NE 60`
* `fight.py` – mash through a battle with "Fight"
* `type_name.py` – types a name on the English name-entry keyboard
* `rebuild.sh` – full rebuild (import → textures → build → verify → code.ips) and install into Azahar mods
Keys (Azahar default keyboard map): A=a, B=s, X=z, Y=x, D-pad=t/g/f/h, circle pad=arrow keys, Start=m.
