# A UE3 D3D11 VR mod on Borderlands Enhanced maps the seams this project will need

**Found:** 2026-09-23, `/gr` estate sweep, through phunkaeg's *VR Modding Playbook* (`sources.yml` →
`BL1GOTYVR`).
**Source:** Mastersellz, *BL1GOTYVR* — <https://github.com/Mastersellz/BL1GOTYVR>, `docs/HOOK_RESEARCH.md`
(no licence found; study only, nothing copied). Full write-up for its own game:
`borderlands-goty-vr/external-research/topics/2026-09-23-bl1gotyvr-a-working-vr-mod-for-this-exact-build.md`.

## Why this project should know about it

Bulletstorm Full Clip is **UE3 on D3D11, 64-bit** — the same combination as Borderlands GOTY Enhanced,
the closest match any VR mod in the playbook has to this game. Everything below is UE3 behaviour
reported on *Borderlands*, so it is a lead for Bulletstorm, not a fact about it `[hypothesis]`.

What they found `[reported]`:

- **Find the camera through the engine's own reflection, not fixed offsets.** They scan for UE3's
  name table and object list, then read camera fields by their property metadata. Our shipped PDB
  should make the same fields easier to name.
- **The standard `PlayerCamera` may be empty.** In Borderlands the live view sat on the game's own
  player controller subclass. Look there first.
- **Class-default objects (`Default__…`) look like cameras and are not.**
- **Never call `GameViewportClient::Draw` twice in one frame**: in their build it corrupted the heap.
- **A second eye can be asked of the engine instead.** They hand UE3's render-command constructor a
  view family holding two views, so the engine allocates, copies and destroys both itself. It ran
  3,900+ frames with no corruption.
- **Writing into the scene view after its render command runs crashes**; the view may already be
  gone.
- **Queue all hooks and switch them on together**; enabling them one at a time while the render thread
  ran caused intermittent crashes.

## Next step

Fold into the `[PD]` first-static-look row: while reading the PDB, look for the player controller's
cached view fields, the viewport client's `Draw`, and the render-command constructor that copies the
view family.

## Credits

Mastersellz (BL1GOTYVR); phunkaeg (*VR Modding Playbook*).
