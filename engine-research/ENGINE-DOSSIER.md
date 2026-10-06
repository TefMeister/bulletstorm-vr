# Engine Dossier — Bulletstorm: Full Clip Edition (Unreal Engine 3)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `dev-archive/` and `modding-notes/` folders; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0, repo created (2026-09-15); the game is still downloading, so nothing has been read from it yet. · **VR-readiness verdict:** TBD.

## 1. Identity
- Game / build / version: Bulletstorm: Full Clip Edition, Steam build (app 501590). **Still downloading** on the home PC (about 12% on 2026-09-15); no files on disk yet.
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). Official release, not a fan port.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: **Unreal Engine 3** `[reported]`. Unchecked against the binary. Alice: Madness Returns and Enslaved are UE3 projects on this account.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.):
- Distinctive file formats / build tags / symbol naming: —

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): not yet looked at — nothing installed.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: Direct3D 11 in the 2017 remaster `[reported]`. Unchecked.
- Developer console / cvar system present? how opened?: not yet investigated.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: unchecked.
- Attach workflow that works: not yet tested.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested.

**🎮 2026-09-17 (home PC, `/lm`) — FIRST LIVE LOOK.**
- **Runs:** Runs and reaches the main-menu background `[verified-live 2026-09-17, n=3]`. Window title: `Bulletstorm: Full Clip Edition (64-bit, DX11)`. Via Steam it runs fullscreen and minimises whenever focus is lost.
- **With our file added:** A 64-bit `dxgi.dll` proxy in `Binaries\Win64\` loads and the game runs with it `[verified-live 2026-09-17, n=1]`: `CreateDXGIFactory`, `CompatValue`, `CreateDXGIFactory1`. ⭐ **The game ships `StormGame-Win64-Shipping.pdb`** — full debug symbols next to the exe `[measured 2026-09-17]`, which should make the camera search far cheaper than on any other UE3 project here. The proxy comes from the shared generator `staging/_shared/proxy-gen/` (every export of the real system dll re-exported with the same ordinals; first call of each export logged). 
- **Windowed (for measuring; 1280×720 keeps aspect-keyed numbers the same on both PCs):** Start `Binaries\Win64\StormGame-Win64-Shipping.exe -windowed ResX=1280 ResY=720` directly → 1280×720 client window `[verified-live 2026-09-17, n=2]`.
- **Driving it:** Direct exe launch with the flags above (`steam_appid.txt` is present). `WM_CLOSE` exits cleanly.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from: **the CPU side is named by the shipped PDB** (2026-09-28, `/pd`):
  `ULocalPlayer::CalcSceneView` (RVA `0x615bb0`, 4438 bytes) builds the per-frame view from
  `APlayerController::GetPlayerViewPoint` (`0x3e23d0`) / `ACamera::GetCameraViewPoint` (`0x3c0e20`) into
  `FSceneView::FSceneView` (`0x938680`, `0x9382d0`, `0x964110`); a global `GViewProjectionMatrix` sits at
  `0x3991580` `[inferred-static 2026-09-28]`. Hook point for per-eye offset + projection swap: `CalcSceneView`.
  UE3's 3D Vision path is compiled in (`GAllowNvidiaStereo3d`, `FD3D11DynamicRHI::CreateStereoFixTexture`) and
  enabled in `BaseEngine.ini:297`. Full table: `dev-archive/recon/2026-09-28-pdb-camera-symbols/`.
  Tool: `dev-archive/tools/pdb_symbols.py` (dbghelp; `llvm-pdbutil` cannot open this PDB).
- **2026-10-01 (`/pd`): the hook point, read from the code.** `CalcSceneView` builds the view matrix in its frame at
  `[rbp+0x60]` (−ViewLocation translation × `FInverseRotationMatrix`) and the projection at `[rbp+0xb0]`
  (`FPerspectiveMatrix`, then one entry `[rbp+0xd0]` overwritten from screen extents), and passes `&ViewMatrix` and
  `&ProjectionMatrix` as stack args 16 and 17 (`[rsp+0x80]`, `[rsp+0x88]`) to `FSceneView::FSceneView`
  (`0x140938680`) at `0x140616bac`; the argument order matches the struct (`FSceneView` +0x80 ViewMatrix, +0xc0
  ProjectionMatrix, derived matrices from +0x200, ViewOrigin +0x3e0) `[inferred-static 2026-10-01]`. Hook: detour
  the constructor, filter return address `0x140616bb1`, swap both inputs; the constructor derives the rest.
  Layout tool `dev-archive/tools/pdb_types.py`; note `modding-notes/2026-10-01-pd-calcsceneview-hands-the-view-and-projection-to-fsceneview.md`.
- The per-eye override maths (`K_eye = …`): view `ViewMatrix · T(−eye_offset)` (row vectors, UE3 view space, cm),
  projection replaced whole by the eye's off-centre one `[hypothesis]`.

**Prior art for two views per frame (drained from `/gr` 2026-10-04):** BL1GOTYVR, a UE3 / D3D11 / 64-bit
mod like this one, renders both eyes in one frame by handing the render-command constructor a view family
with **two owned views**, applying both eye positions from one frozen OpenXR pose, and splitting the
side-by-side backbuffer into the two eye images; it falls back to alternate-eye rendering on a mismatch
`[reported]`. Their two dead ends on this engine generation: calling `GameViewportClient::Draw` twice per
frame corrupts the heap (`0xC0000374`), and writing into a scene view after its render command ran crashes
`[reported]`. ⚠️ Writing asymmetric offsets into the projection removed the world while the HUD stayed, so
they shift the camera position only, which is what our `FSceneView` detour does `[reported]`. Source:
`external-research/topics/2026-09-23-a-ue3-d3d11-vr-mod-on-borderlands-enhanced-maps-the-seams.md`.

**2026-10-06 (`/lm`, dev PC): ⭐⭐ THE FIRST CAMERA EDIT WORKS.** With `dxgi.dll` `4fe9ee7d0b0a` the log says
`hook IN (status 0)`; numpad 6 x4 moves the eye +20 cm and `views edited` climbs from the first press. In Act 7
Chapter 2, standing still: near things (the held gun, a pillar at the right) slide left far more than the ceiling
lights and the enemy in the distance, the HUD text does not move, and numpad 5 snaps the view straight back. Done
twice, 0 -> 20 -> 0 -> 20 -> 0 cm, same result each time `[verified-live 2026-10-06, n=2 cycles]`. The held gun moves
with the world (it is drawn by the same view), as a near object should. Pictures and log:
`dev-archive/recon/2026-10-06-first-camera-edit-works/`.

**2026-10-06 (reader, static): the view family, mapped from the PDB.** RVAs from base `0x140000000`, all
`[inferred-static 2026-10-06]`:
- `FSceneViewFamily` (96 bytes): `+0x00 Views` is a `TArray<const FSceneView*>` (data, `+0x08` Num, `+0x0c` Max); then
  RenderTarget `+0x10`, Scene `+0x18`, ShowFlags `+0x20`.
- `UGameViewportClient::Draw` (`0x619630`) builds the family on its stack (`0x619c3f`), loops over the local players
  (`0x619c7b`..`0x61a239`), calls `CalcSceneView` once per player (`0x619d15`); `CalcSceneView` appends the new view
  pointer to `family.Views` (grow `0x616c1f`, store `0x616c6e`). One `BeginRenderingViewFamily` after the loop
  (`0x61a27f`). **So split-screen already puts N views in one family and one render command.** A second family path
  earlier in Draw (`0x619792`..`0x619a1c`) is unidentified `[hypothesis: an early-out path]`.
- `BeginRenderingViewFamily` (`0x968830`) builds `FSceneRenderer` (`0x963a20`), which copies the family (copy
  constructor `0x964cb0`, at `0x963aac`) and makes one `FViewInfo` per view (`0x964da0`, at `0x963cf9`) into renderer
  `+0x68`. The render command (`FDrawSceneCommand`, vftable `0x1360b20`) carries only the renderer pointer.
- Reading: the engine's own split-screen loop is the natural place to add a second eye (one more view appended to
  the same family before `BeginRenderingViewFamily`). That is a design choice for the `[PD]` two-views row, not
  decided here. Detail and disassembly listings: `dev-archive/recon/2026-10-06-first-camera-edit-works/` and
  `staging/bulletstorm-vr/tools/`.

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| `~` (Tilde) | opens the console: `ConsoleClassName=Engine.Console`, `ConsoleKey=Tilde`, `TypeKey=TAB` (`Engine/Config/BaseInput.ini:253`, no override in `StormGame/Config`); `UConsole` is compiled in `[inferred-static 2026-09-28]` | untested live: the `[FLAT]` row |

## 10. Autonomous harness recipe (this game)
- **Window:** `FullScreen=False`, `ResX=1280`, `ResY=720` in
  `Documents/My Games/Bulletstorm Full Clip Edition/StormGame/Config/StormSystemSettings.ini` (backup
  `*.bak-2026-10-06-pre-1280x720`). The `ResX/ResY` command-line switches are IGNORED on the dev PC when this file says
  1920x1080: the window came up at 1850x1041. With the file changed, client 1280x720 and the screen stays 1920x1080
  `[measured 2026-10-06, n=1]`. The setting survived a menu quit.
- **Launch:** `Binaries/Win64/StormGame-Win64-Shipping.exe -windowed`, working directory `Binaries/Win64`; title screen
  after about 45 s.
- **Input:** `SendInput` with SCANCODES. `keybd_event` with virtual-key codes does nothing here `[verified-live 2026-10-06]`.
  Enter `0x1C`, Space `0x39`, Esc `0x01`, arrows extended (`e048` up, `e050` down, `e04b` left), numpad 4/5/6 `0x4B/0x4C/0x4D`.
- **To gameplay:** Enter (title) -> Space (autosave notice) -> Space (Campaign) -> Space (Continue; the dev PC's save is
  Act 7 Chapter 2) -> wait about 40 s -> Space (chapter card) `[verified-live 2026-10-06, n=1]`.
- **Quit:** Esc -> pause menu, cursor on Resume; Down x5 to Exit to Main Menu (VERIFY: the cursor does not always
  start at the top after returning from Options) -> Space -> Space (confirm) -> main menu; Up x1 wraps to Quit ->
  Space -> Space `[verified-live 2026-10-06, n=2]`.
- **Capture:** BitBlt from the screen DC over the window's client rect.
- **Music:** only in the binary profile (`Steam/userdata/<id>/501590/remote/profile.bin`, Steam Cloud), not in any ini
  `[inferred-static 2026-10-06]` (reader). Set to zero in Options -> Audio -> Music Volume on 2026-10-06 (Left x25).
  Voice Volume was already at zero before this session; left as found.

## 11. Dead ends & false leads (save future time)
- none yet.

## 12. Open risks toward the North Star
- ⚠️ Not installed yet — no static work is possible until the download finishes.
