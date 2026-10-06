# 2026-10-06: the first camera edit works

Dev PC, `/lm`, picked because it was the top flat-screen job meant for Opus. First time this game ran on the
dev PC with our camera file in it.

## What happened

- **Our file hooks the right place.** The log says `hook IN` as soon as the game starts, so this is the game
  build the hook was written for. `[verified-live 2026-10-06, n=1]`
- **Moving the eye works.** In the level (Act 7, Chapter 2), standing still, four presses of numpad 6 moved
  the eye 20 cm to the right. Near things (the gun in your hands, a pillar on the right) slid a long way;
  the ceiling lights and an enemy further off slid only a little; the HUD text stayed where it was. Numpad 5
  snapped everything straight back. Did it twice, same both times. That is exactly what a second eye needs.
  `[verified-live 2026-10-06, n=2 cycles]`
- **The window is now 1280×720.** The command-line size is ignored on this PC because the game's own settings
  file said 1920×1080; changed that file (backed up), and the window measured exactly 1280×720 with the screen
  left alone. `[measured 2026-10-06, n=1]`
- **Music is off**, set in the game's own audio menu (it is only stored in a packed profile file, not a text
  file). Voice volume was already at zero; left as found.
- **Driving it:** the game ignores the simple kind of synthetic key press and needs raw key codes. Launch,
  menus, level load, pause menu, options and quitting all work by keyboard now.

## What the helper found (static)

- How the engine bundles camera views for drawing: the split-screen code already puts several views into one
  bundle and sends it to the renderer once. Adding a second eye as "one more view" in that bundle looks like
  the natural route. Addresses in the dossier, §6. `[inferred-static 2026-10-06]`
- Where the music setting lives (a packed, cloud-synced profile file), and that the console key is `~`.

## Not established

- Whether the console opens (not tried).
- Anything about two eyes at once: only one shifted eye exists so far.
- Tefa has not yet confirmed the 1280×720 window by eye.

Evidence: `dev-archive/recon/2026-10-06-first-camera-edit-works/`. Dossier §6 and §10.
