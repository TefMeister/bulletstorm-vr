# 2026-10-01 (`/pd`, dev PC): CalcSceneView hands the view and the projection to FSceneView

**The game was not launched, and nothing here has been run.** Read from `StormGame-Win64-Shipping.exe` and its
shipped PDB on disk. VAs are for image base `0x140000000` (RVA = VA − 0x140000000).

## The layout

New tool `dev-archive/tools/pdb_types.py` reads struct layouts from the PDB (the 130 MB PDB carries full type
information). `FSceneView` is 1,520 bytes; the parts that matter for VR `[inferred-static 2026-10-01]`:

| offset | member |
| --- | --- |
| +0x80 | `ViewMatrix` (FMatrix) |
| +0xc0 | `ProjectionMatrix` |
| +0x200 / +0x240 / +0x280 | `TranslatedViewMatrix`, `TranslatedViewProjectionMatrix`, its inverse |
| +0x2c0 | `PreViewTranslation` |
| +0x2e0 / +0x320 / +0x360 / +0x3a0 | `ViewProjectionMatrix`, `InvProjectionMatrix`, `InvViewMatrix`, `InvViewProjectionMatrix` |
| +0x3e0 | `ViewOrigin` |
| +0x3f0 | `ViewFrustum` |

The derived matrices are all computed inside the constructor, so editing the view after it is built would mean
recomputing nine things. Editing what goes **in** is the clean route.

## What CalcSceneView does (RVA `0x615bb0`)

In order `[inferred-static 2026-10-01]`:
1. Asks the player controller for the view point (virtual calls; `APlayerController::eventGetFOVAngle` at
   `0x140615d38` for the field of view).
2. Builds the **view matrix in its own frame at `[rbp+0x60]`**: a translation row of −ViewLocation at
   `[rbp+0x90]` (`0x140615e8c`–`0x140615e9f`), multiplied by `FInverseRotationMatrix(ViewRotation)`
   (`0x140615ead`), stored back at `0x1406160db`–`0x1406160ea`.
3. Builds the **projection at `[rbp+0xb0]`** from `FPerspectiveMatrix` (`0x140616282`, after `tanf` of the half
   FOV and `FViewport::CalculateViewExtents`), then overwrites one entry, `[rbp+0xd0]` (row 1 / column 0 area),
   from screen extents (`0x1406162eb`): the engine's own off-centre term `[hypothesis]` — the slot an asymmetric
   headset frustum would also use.
4. Calls **`FSceneView::FSceneView` (`0x140938680`) at `0x140616bac`** with: `rcx` = the new view, `rdx` = family,
   `r9d` = −1 (parent index), six floats X/Y/ClipX/ClipY/SizeX/SizeY at `[rsp+0x50..0x78]`, then
   **`&ViewMatrix` (`[rbp+0x60]`) at `[rsp+0x80]`** and **`&ProjectionMatrix` (`[rbp+0xb0]`) at `[rsp+0x88]`**,
   then the background/overlay/scale colours and the hidden-primitive set. That order matches the struct
   exactly, which is the strongest check that the reading is right.

## The hook this gives

Detour `FSceneView::FSceneView` and act only when the return address is `0x140616bb1` (the CalcSceneView call).
Before calling the original, replace:
- the view matrix with `ViewMatrix · T(−eye_offset)` (UE3 view space, row vectors; x = right), and
- the projection with the headset eye's off-centre projection.

The constructor then derives every other matrix, the frustum and `ViewOrigin` consistently. A second eye needs a
second view per frame (UE3 draws one view per player; split-screen shows the engine can draw two). How to get
two views is the next design question.

## Not established

- Anything live. Units: UE3 uses centimetres, so a 64 mm eye distance is 6.4 units `[hypothesis]`.
- What exactly `[rbp+0xd0]` gets (traced to one store, formula not decoded).
- Whether `GViewProjectionMatrix` (`0x3991580`) is read by anything that would then disagree with the per-eye view.
