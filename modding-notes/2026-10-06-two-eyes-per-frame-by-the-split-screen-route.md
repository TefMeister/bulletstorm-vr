# 2026-10-06 (later): two eyes per frame, by the split-screen route

Dev PC, `/lm`, run on Opus although the board row asked for Fable (Tefa's instruction for the dev PC, 2026-10-06).

## The idea

Bulletstorm can already draw several players' views in one frame for split-screen: the engine asks each player for
their view, collects them all, and draws them together. Each player's view gets a slice of the screen from two numbers
on the player (where it starts, how big it is). So for our one player we ask twice: once for the left half with the
camera moved a little left, once for the right half moved a little right. The engine thinks it is drawing two-player
split-screen.

## What happened

- **It works.** Numpad 7 turns it on: the picture splits into two eyes, near things shift between them much more than
  far things (the gun most, a pillar less, an enemy in the distance hardly at all), and the game keeps running. Numpad 7
  again gives the normal picture back. `[verified-live 2026-10-06, n=1]`
- **First try was smeared.** Both eyes shared one memory of the last frame, so the motion blur thought the camera jumped
  back and forth every frame. The fix: give the left eye a memory of its own, made by the engine's own function for
  that. Second try: clean. `[verified-live 2026-10-06, n=1]`
- **The HUD only shows in the right eye.** The engine draws the HUD once per player, after it has the (right) view.

## Next

1. The HUD in both eyes.
2. Each eye's own lens shape (off-centre projection) and sending the two halves to the headset.

## Not established

- Frame rate cost on a real PC (the dev PC is slow by design).
- Behaviour across a level change or a cutscene with the extra view memory.
- Anything in a headset.

Pictures and log: `dev-archive/recon/2026-10-06-two-eyes-split-screen-route/`. Code: `staging/bulletstorm-vr/proxy-dxgi/src/stereo.c`.
