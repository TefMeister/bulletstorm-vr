# 2026-10-07 (/lm reader, static): why the HUD is right-eye only, and a build that draws it in both eyes

Lane: /lm bulletstorm-vr (static reader helper). For the dossier §6 (two eyes per frame) and §8 (UI / HUD).

## Where the HUD takes its rectangle `[inferred-static 2026-10-07]`

All RVAs from base `0x140000000`, read from `UGameViewportClient::Draw` (`0x619630`) on disk with PDB names.
- Player loop: `CalcSceneView` (call `0x619d15`) returns one view; Draw stores it in a player-index -> view map
  (TSet Add at `0x619def`, map at Draw's `[rbp+0xf8]`). Still in that loop, `PlayerController.PreRender(Canvas)` runs
  with the canvas sized and shifted to that view (`0x61a0be`..`0x61a183`). stereo.c returns the RIGHT view, so both
  see the right eye only.
- HUD loop, after `BeginRenderingViewFamily` (`0x61a7a6`..`0x61abb5`): looks the view up again, reads `X/Y/SizeX/SizeY`
  (`FSceneView` +0x54/+0x58/+0x64/+0x68), runs `PlayerController.AdjustHUDRenderSize` and
  `FSystemSettings::UnScaleScreenCoords` (`0x2e6ee0`), sets `UCanvas` SizeX/SizeY (+0x90/+0x94) and SceneView (+0xa0),
  `UCanvas::Update` (`0x82a4a0`, runs Canvas.Reset), `FCanvas::PushAbsoluteTransform` (`0x825fa0`) to the view's corner,
  then `HUD.PostRender` through the HUD's ProcessEvent (vtable +0x248 = `AActor::ProcessEvent` `0x3276a0`, call at
  `0x61aa84`; HUD.Canvas = `AHUD` +0x538), then each `Interaction.PostRender(Canvas)` (Actor +0x5c8 list), then
  `FCanvas::PopTransform` (`0x825320`).
- After that, subtitles and `UUIInteraction::RenderUI` and the stats HUD draw over the whole viewport, not per view.
- No Scaleform/GFx in this build (only `AWorldInfo::IsWithGFx` stubs): the HUD is Canvas drawing.
- `pdb_disasm.py`'s symbol naming returns nothing on this PDB; `staging/bulletstorm-vr/tools/pdb_disasm_named.py`
  names targets from a `pdb_symbols.py "*"` dump instead. Named listing of Draw: `tools/gvc_named.txt`.

## Options weighed

1. **Run HUD.PostRender once per eye (CHOSEN).** Smallest change: the engine's own canvas path does all the work, the
   two passes batch into one canvas flush like split-screen. HUD markers that project 3D->2D through
   `Canvas.SceneView` get each eye's own view. Risk: PostRender runs twice per frame; the second pass sees
   `RenderDelta` = 0 (AHUD +0x544, computed from LastHUDRenderTime), which should only mean "no extra time passes"
   `[hypothesis]`.
2. Restore the player's full Origin/Size for the HUD: the HUD would be drawn once across BOTH halves, its left part in
   the left eye and its right part in the right eye. Wrong picture; rejected.
3. Draw the HUD once into a separate target and composite into both halves: needs render-thread work and a new render
   target; far more invasive. Kept as the fallback if (1) shows script side effects.

## The build `[compile-verified 2026-10-07]`

`staging/bulletstorm-vr/proxy-dxgi/src/hud_eyes.c`, dll `899d7c9a8ade` at
`staging/bulletstorm-vr/builds/dxgi-2026-10-07-stereo-hud-per-eye-899d7c9a8ade.dll` (also `proxy-dxgi/build/dxgi.dll`).
Detours `AActor::ProcessEvent`, filters on the return address `0x61aa8a`; after the engine's right-eye PostRender it
sets the canvas SceneView to the left view, calls `UCanvas::Update`, pushes a relative translation of
(left corner - right corner, both through `UnScaleScreenCoords`) with `FCanvas::PushRelativeTransform` (`0x826490`),
calls PostRender again, pops, and puts the right view back. Guards: known bytes at the ProcessEvent prologue and the
call site, stereo on, both views recorded this frame (stereo.c now publishes them and clears them at every
CalcSceneView call), and the canvas really holding the right view.
- Switch: numpad 1, starts OFF (= current behaviour) unless `bulletstorm_hud_per_eye.on` is beside the exe.
- Self-test `test/hud_eyes_selftest.c`: 12/12 pass `[verified-numerically 2026-10-07, n=1 run]`. A non-game exe that
  loads the dll logs three refusals and installs nothing `[measured 2026-10-07]`. Exports match the system dxgi (19).
  The unchanged source rebuilds byte-identical to `e80145977754` `[measured 2026-10-07]`.

## What to look for in a live run

Install `899d7c9a8ade`, gameplay, numpad 7 (stereo), then numpad 1.
- Log: `AActor::ProcessEvent at ...: hud-per-eye hook IN (status 0)` at start; after numpad 1 `hud per eye ON`; then
  once a second `hud per eye ON: HUD.PostRender calls ~N, left passes drawn ~N, skipped: ... 0; last shift (-640, 0)`.
  Drawn about equal to calls = working. `view mismatch` climbing = the canvas held a different view (the map lookup
  is not what this reading says). `no views` climbing = CalcSceneView is called again between the loops.
- Picture: the HUD (ammo, crosshair, skill points) now in BOTH halves, each inside its own half, same layout. With
  numpad 1 off again: right half only, as before.
- Watch for: HUD animations or popups behaving differently (running twice), a crash in the first frames after numpad 1
  (would point at the transform stack), the console/subtitles still right-only or spanning both (expected: not
  handled; interactions are drawn once, subtitles across the whole screen).
- Not in this build: interactions per eye, subtitles per eye, the PreRender pass per eye, headset output.
