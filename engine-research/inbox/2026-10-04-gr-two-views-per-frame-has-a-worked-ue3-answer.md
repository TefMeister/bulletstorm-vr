# For the `[PD]` "how to get TWO views per frame" row: a UE3 D3D11 64-bit mod has a worked answer

From: `/gr`, 2026-10-04. Points the open Fable row at prior art already in this lane
(`external-research/topics/2026-09-23-a-ue3-d3d11-vr-mod-on-borderlands-enhanced-maps-the-seams.md`), with the
details from BL1GOTYVR's `docs/HOOK_RESEARCH.md` that the topic summarised in one line. Read only; nothing copied.

- **Their same-frame route** (`SameFrameStereo=1`) `[reported 2026-10-04]`: the validated render-command
  constructor is handed a view family with **two owned views**; `RenderScene` applies both eye positions from one
  frozen OpenXR snapshot; the frame loop splits the resulting side-by-side backbuffer into the two eye swapchains.
  A missing or mismatched frame falls back to alternate-eye rendering. Their commit "Enable stable native multiview
  stereo" is dated 2026-09-07; "Stabilize native SFR submission" 2026-09-10.
- **Their two failures, both on this engine generation** `[reported]`: calling `GameViewportClient::Draw` twice in
  one frame corrupts the UE3 heap (`0xC0000374`); writing into the scene view after its render command has run
  crashes, because the view may already be gone.
- **A warning for this project's current `[FLAT]` edit** `[reported]`: on BL1 Enhanced, writing asymmetric offsets
  into a reciprocal projection-like matrix on the renderer's view object removed the world while the HUD stayed, so
  they disabled engine projection writes and shift the camera position only. Our `FSceneView` detour shifts the view
  position, which is the shape that worked for them.
- **Why it fits Bulletstorm closely:** Borderlands GOTY Enhanced is UE3, D3D11 and 64-bit, like Bulletstorm Full
  Clip; Enslaved and Alice are 32-bit D3D9.
- Suggested: cite this in the two-views row so the Fable session starts from it, and look in the PDB for the
  render-command constructor that copies the view family.
