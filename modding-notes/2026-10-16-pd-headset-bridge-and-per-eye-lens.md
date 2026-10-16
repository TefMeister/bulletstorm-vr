# 2026-10-16 (`/pd`, dev PC, no launch): the headset bridge and each eye's own lens, built and installed, unseen

**The game was not launched, and nothing here has run inside it.** Everything below is compile-verified and proven by
stand-alone tests on this PC's graphics card, nothing more.

## What was built

The board's top `[PD]` row: *per-eye off-centre projection + headset output*. Build `dxgi.dll` `f71d78ed277e`
(`staging/bulletstorm-vr/proxy-dxgi/`, kept as `staging/bulletstorm-vr/builds/dxgi-2026-10-16-headset-bridge-f71d78ed277e.dll`).

1. **The headset bridge is Metro Exodus's, copied whole** (`src/xr/`, from `staging/metro-exodus-vr/share-cpu-2026-10-15/`,
   which put Metro's own picture in the OpenXR simulator with the head turning the view on 2026-10-15). Its shape: our
   own headset thread with its OWN D3D11 device (The Evil Within's 2026-10-06 lesson: a session on the game's device
   stalled the game inside the runtime), the game thread hands each picture over without ever waiting (LOCK, then RING,
   then CPU, each the moment the one before fails).
2. **Side by side, not alternating.** Metro alternates eyes frame by frame; Bulletstorm draws both eyes into one back
   buffer (the 2026-10-06 split-screen route). So each Present hands the whole back buffer to both eyes, and each eye's
   layer shows only its own half (`MhUsed.sbs`, `mxr.c` `eye_rect`). Each eye carries its own record of what it was
   drawn with (`mxr_share_capture_pair`).
3. **Each eye drawn with the headset's own lens.** The headset thread hands each eye's lens (from `xrLocateViews`) to the
   game (`mh_publish_lens`). Before each eye's `CalcSceneView`, the `FSceneView` detour now also points the
   constructor's projection argument at our copy, whose x and y map exactly that eye's four tangents to the screen
   edges; depth is the game's. The stub gained one instruction (`lea r8, [rsp+0xd8]`: the projection slot). This is the
   off-centre per-eye projection, and because the layer is told the same lens, the picture and the layer agree by
   construction. `projection=game` keeps the game's own symmetric lens instead (Metro's way).
4. **Head tracking**: Metro's `mhead.c` unchanged (UE3's view space is x right, y up, z forward, row vectors: the same as
   Metro's). The head matrix goes in before the eye shift, so the eyes sit along the head's right. Its translation is
   scaled by `units_per_metre` (default 100: 1 UE3 unit = 1 cm `[hypothesis]`).
5. **Frame pairing**: UE3 draws on its own render thread, so the pair drawn by `CalcSceneView` is presented later. The
   pair goes into Metro's first-in-first-out queue; each game Present takes the oldest. A frame drawn without stereo
   goes to both eyes whole.

Switch: `bulletstorm_xr.ini` `[xr] openxr=1` (then stereo starts ON). Installed with `openxr=0`, so a plain launch is the
2026-10-07 build's behaviour. `openxr_loader.dll` copied beside the exe from the Metro install (`97a8e5f74fc2`).

## How it was checked `[verified-numerically 2026-10-16]`

- View-hook self-test: 18 checks, including: with a lens set the constructor gets our projection, its x and y give
  back exactly the eye's tangents, the lens edges land on the screen edges, depth and w columns are the game's, the
  game's own matrix is untouched; with a head matrix the view is game × head then the eye shift.
- Metro's tests, unchanged: queue, format pick, ring (93,706 reads, 0 torn), head maths (20,033 checks).
- The picture hand-over on two real D3D11 devices of this PC's GTX 1660 SUPER: LOCK, RING, CPU and the fall-back
  switch all pass every pixel; plus a new side-by-side run per way where each eye must arrive with its own record of
  the same frame: 0 wrong in all three.
- Loaded into a program that is not the game: the three hooks refuse, nothing else starts.

## What is NOT established

- That the game's device accepts any of the three hand-over ways (the test devices are plain ones) `[hypothesis]`.
- That one `CalcSceneView` pair maps to exactly one Present (the queue depth in the log will say) `[hypothesis]`.
- That UE3 uses nothing else that assumes a symmetric projection (screen-space effects, post-process) `[hypothesis]`.
  If the headset picture looks right in the middle but smeared or shifted at the edges, suspect this first, and test
  with `projection=game`: if that is clean, the lens swap is the cause, not the bridge.
- 1 unit = 1 cm `[hypothesis]`: if moving the head 10 cm moves the view far more or less, change `units_per_metre`.

## The next live test (`/lm`, dev PC, the OpenXR simulator)

Set `openxr=1` and `runtime_json=` (the simulator's json) in `bulletstorm_xr.ini`, launch, reach gameplay.
- `bulletstorm_xr_log.txt` says `session running`, then `headset lens handed to the game`, then `bxr pair 1..6` with
  `headset lens 1`, then `bxr present` lines saying `STEREO PAIR` with frames waiting about 1-2 → the bridge and pairing work.
- Simulator preview: each eye shows its own half, near things offset the right way between the eyes.
- `test_pattern=1` first if the picture does not appear: red/blue proves the bridge alone.
