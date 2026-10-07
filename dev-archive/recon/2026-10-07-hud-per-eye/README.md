# 2026-10-07 — the HUD in both eyes

`[verified-live 2026-10-07, n=1]`, dev PC, 1280x720 window. dxgi `899d7c9a8ade` (staging `71d906d`): stereo on
(numpad 7), then numpad 1 (HUD per eye). Log: HUD.PostRender 60/s, left passes drawn 60/s, nothing skipped, shift
(−640, 0) px. Before: the HUD only in the right half (`before-hud-right-only.png`); after: "DROPKIT DETECTED" and
"LEASH" in both halves, each in its own half (`after-hud-both-eyes.png`). No crash; popups not watched over time.
