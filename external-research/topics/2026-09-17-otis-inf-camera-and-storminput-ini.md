# Otis_Inf's camera tools work on Full Clip Edition, and StormInput.ini takes console-command bindings

**Status:** 🆕 new · **Priority:** medium.

## What is public

- **Otis_Inf's camera tools** support Bulletstorm: Full Clip Edition, with a free camera and FOV control,
  injected by **IGCSInjector** (FRAMED's guide recommends running both as administrator, injecting shortly
  after the game starts) `[reported]`. The camera disables bloom and depth of field while active
  `[reported]`.
- FRAMED's guide adds bindings in
  `Documents\My Games\Bulletstorm Full Clip Edition\StormGame\Config\StormInput.ini`, under
  `[StormGame.BSPlayerInput]` — for example a "Players Only" time-stop and resolution switches
  `[reported]`. That is the standard UE3 way to run console commands from keys.
- The Steam tweak guide and PCGamingWiki document the rest of the ini set `[reported]`.

## Why it matters here

1. **The `[FLAT]` "does the console open" row may not need the console**: any UE3 console command can be
   bound to a key in `StormInput.ini` `[hypothesis]`, which is testable in one launch.
2. A working third-party free camera means the camera's position and rotation are found and writable in
   this build; combined with the shipped PDB (board row), the camera classes should be quick to locate.

## Next step

Bind a harmless command (for example `stat fps`) in `StormInput.ini` and see whether it runs.

## Sources

- FRAMED, Bulletstorm: Full Clip Edition — <https://framedsc.com/GameGuides/bulletstorm.htm>
- Steam tweak guide — <https://steamcommunity.com/sharedfiles/filedetails/?id=904933469>
- PCGamingWiki — <https://www.pcgamingwiki.com/wiki/Bulletstorm:_Full_Clip_Edition>
