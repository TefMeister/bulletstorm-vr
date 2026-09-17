# 2026-09-17 — first live look: Bulletstorm: Full Clip Edition

Home PC `RTX`, `/lm` session. The user asked for a first look at six games: does each run, and does it still run with our own file added.

## Does it run?

Runs and reaches the main-menu background `[verified-live 2026-09-17, n=3]`. Window title: `Bulletstorm: Full Clip Edition (64-bit, DX11)`. Via Steam it runs fullscreen and minimises whenever focus is lost.

## With our file added

A 64-bit `dxgi.dll` proxy in `Binaries\Win64\` loads and the game runs with it `[verified-live 2026-09-17, n=1]`: `CreateDXGIFactory`, `CompatValue`, `CreateDXGIFactory1`. ⭐ **The game ships `StormGame-Win64-Shipping.pdb`** — full debug symbols next to the exe `[measured 2026-09-17]`, which should make the camera search far cheaper than on any other UE3 project here. The proxy comes from the shared generator `staging/_shared/proxy-gen/` (every export of the real system dll re-exported with the same ordinals; first call of each export logged). 

## Windowed mode

Start `Binaries\Win64\StormGame-Win64-Shipping.exe -windowed ResX=1280 ResY=720` directly → 1280×720 client window `[verified-live 2026-09-17, n=2]`.

## How it was driven

Direct exe launch with the flags above (`steam_appid.txt` is present). `WM_CLOSE` exits cleanly.

## Not established

- Nothing past the menus: no gameplay was loaded, no camera data read.
- Every result is from one machine (`RTX`, 21:9 desktop) on one day.

## Next

- [PD] ⭐ first static look **using the shipped PDB**: camera/view classes, where the view-projection is built, UE3 console availability; fill in dossier §1–4 and §6
- [FLAT] check whether the UE3 console opens (direct launch, windowed)
