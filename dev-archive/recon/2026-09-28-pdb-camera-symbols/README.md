# 2026-09-28 — /pd: the shipped PDB names the camera path; console and 3D Vision are both in

Dev PC, `/pd`, no game launched, nothing run. Game at `E:\SteamLibrary\steamapps\common\Bulletstorm Full Clip Edition`.

## How

`Binaries\Win64\StormGame-Win64-Shipping.pdb` (125 MB) ships beside the exe. `llvm-pdbutil` refuses it ("Too many
directory blocks"), so `dev-archive/tools/pdb_symbols.py` reads it through Windows' own `dbghelp`. The symbol list
this note is built on is `symbols.txt` here (names and RVAs only: interface metadata, not game content).

## What the PDB says `[inferred-static 2026-09-28]`

RVAs are offsets from the exe's load address (ASLR decides the base each run).

| RVA | size | symbol | why it matters |
| --- | --- | --- | --- |
| `0x00615bb0` | 4438 | `ULocalPlayer::CalcSceneView` | **the per-frame view builder** in UE3: player view point + projection → `FSceneView`. The natural place to shift the eye and swap the projection |
| `0x003e23d0` | 435 | `APlayerController::GetPlayerViewPoint` | where the camera position/rotation is read from the controller |
| `0x003f1680` | 407 | `APlayerController::UpdateViewTarget` | camera update |
| `0x003c0e20` | 56 | `ACamera::GetCameraViewPoint` | the camera actor's current view |
| `0x00938680`, `0x009382d0`, `0x00964110` | ~1–3 KB | `FSceneView::FSceneView` (three overloads) | the view object the renderer consumes |
| `0x00964da0`, `0x00965330` | ~1.1–1.4 KB | `FViewInfo::FViewInfo` | renderer's per-view data |
| `0x03991580` | 64 | `GViewProjectionMatrix` | a global 4×4 view-projection |
| `0x0394c8ac` | 4 | `GAllowNvidiaStereo3d` | the 3D Vision switch (`BaseEngine.ini:297` `AllowNvidiaStereo3d=True`) |
| `0x00c35820`, `0x00c44560` | | `FD3D11DynamicRHI::CreateStereoFixTexture` / `UpdateStereoFixTexture` | UE3's 3D Vision support in the D3D11 renderer |
| `0x001b9f80` | 3 | `UEngine::IsStereoscopic3D` | 3 bytes: returns a constant |
| `0x0099b010` | 244 | `StereoizedDrawNullTarget` | stereo-aware draw helper |
| `0x0082ff10` … | | `UConsole::*` (constructor, vtable, autocomplete, `eventOutputText`) | the console class is compiled in |

Config: `Engine/Config/BaseEngine.ini:33` `ConsoleClassName=Engine.Console`; `BaseInput.ini:253-254`
`ConsoleKey=Tilde`, `TypeKey=TAB`; no override in `StormGame/Config/Default*Input.ini` `[inferred-static 2026-09-28]`.

## What it means

- The hard part of most games — *finding* the camera — is done: every UE3 function on the path has its name and
  address. A VR hook goes at `ULocalPlayer::CalcSceneView` (after the view is built, offset it per eye, replace the
  projection), exactly the shape UE3 VR work takes elsewhere.
- The console is present and configured on `~`, so the FLAT row "does the console open" is a direct test, not a
  hunt. Whether a shipping build ignores console commands is the thing it answers.
- UE3's own 3D Vision path is compiled in and switched on in the config. It gives binocular depth, not head
  tracking, but it shows the renderer can draw two eyes.

## NOT established

- Anything about the running game. The exe's code was not disassembled, only its symbols listed.
- That `CalcSceneView` runs once per frame per player here (it does in stock UE3; Bulletstorm is People Can Fly's
  modified UE3).
- Which constant buffer carries the matrices to the GPU (dossier §6's other half).
