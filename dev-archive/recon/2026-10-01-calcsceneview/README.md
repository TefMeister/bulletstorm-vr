# 2026-10-01 /pd: CalcSceneView and the FSceneView layout

`FSceneView-layout.txt`: data members of `FSceneView` with byte offsets, read from the shipped PDB with
`../../tools/pdb_types.py` (dbghelp). Interface metadata only; no game code is kept here.
The reading of `ULocalPlayer::CalcSceneView` itself is summarised in
`modding-notes/2026-10-01-pd-calcsceneview-hands-the-view-and-projection-to-fsceneview.md`.
