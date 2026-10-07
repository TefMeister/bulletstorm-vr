# For the headset-output row: the simplest DX11 route binds OpenXR to the game's device

From `/gr`, 2026-10-07 (cross-project, from Metro Exodus). Topic in Metro's lane:
`metro-exodus-vr/external-research/topics/2026-10-07-skip-the-shared-texture-bind-the-headset-to-the-game-device.md`.

Board row: *"per-eye off-centre projection + headset output … the two halves sent to OpenXR"*.

When choosing between Hard Reset's and Metro's bridge as the model: Metro just found its DX11 device
refuses keyed-mutex shared textures, which TEW's bridge relies on. Whatever Bulletstorm's device accepts,
the route with no sharing at all is REFramework's: `XrGraphicsBindingD3D11KHR.device` = the game's own
device, then `CopyResource` each half into the swapchain image `[inferred-static 2026-10-07]`. Worth
checking first (one CreateTexture2D probe) whether Bulletstorm's device accepts `SHARED_KEYEDMUTEX`
before porting TEW's bridge.
