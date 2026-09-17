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

**🎮 2026-09-17 (home PC `RTX`, `/lm`) — FIRST LIVE LOOK.**
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
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):

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
| | | |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- none yet.

## 12. Open risks toward the North Star
- ⚠️ Not installed yet — no static work is possible until the download finishes.
