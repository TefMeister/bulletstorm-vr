# The OPEN block reads as empty, so /gates cannot see Bulletstorm's top job

From `/gs`, 2026-10-08.

`gate-scan.sh --check` reports `bulletstorm-vr: OPEN block has no rows`. The block does have rows, but its
first line is `  ✅ CLOSED 2026-10-07: the HUD in both eyes …`. The parser stops the block at the first line
that does not start with `  [`, so the `[PD]` per-eye projection row and the `[FLAT]` shader-layout row
below it are never read `[inferred-static 2026-10-08]` (read from `gate-scan.sh`, the row loop).

Effect: `/gates` and `--next` show Bulletstorm as having no open work while its top job is a `[PD]` row.

Fix: move the `✅ CLOSED` line out of the OPEN block (into the log below it), so the block starts with a
tagged row. Re-run `gate-scan.sh --check` to confirm.
