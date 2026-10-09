# X2D II Extension Manager (development foundation)

[English](README.md) | [简体中文](README_CN.md)

This directory contains the safety boundary for a unified X2D II extension installer. It builds and verifies `.x2d2ext` bundles, exercises atomic generation activation and rollback locally, performs a firmware-pinned WinUSB handshake, and can stage an immutable generation without activating it.

The current package targets are Electronic Shutter AF-C and the tested Pixel Shift resident snapshot. Camera activation, removal and recovery remain intentionally separate from staging while the common boot manager is completed.

## Build a local AF-C bundle

Use pristine `camera-service` and `camera-gui` files extracted from X2D II firmware 1.3.16.2. The generated bundle stores only the locally built module and the two fixed-size GUI patch regions, not a second 64 MB GUI image. It is ignored by Git; do not redistribute it without first resolving the vendor-derived patch licensing boundary.

```powershell
python -m installer.build_afc_bundle `
  --camera-service D:\path\to\system\bin\camera-service `
  --camera-gui D:\path\to\system\bin\camera-gui `
  --ndk D:\path\to\android-ndk-r27 `
  --out .local-only\electronic-shutter-afc-1.0.0.x2d2ext
```

## Verify and simulate

```powershell
python -m installer.manager verify .local-only\electronic-shutter-afc-1.0.0.x2d2ext
python -m installer.manager plan .local-only\electronic-shutter-afc-1.0.0.x2d2ext
python -m installer.manager simulate-install .local-only\electronic-shutter-afc-1.0.0.x2d2ext .local-only\simulated-camera
python -m installer.manager probe-camera
python -m installer.manager stage-camera .local-only\electronic-shutter-afc-1.0.0.x2d2ext
python -m installer.manager stage-camera .local-only\pixel-shift-400mp-1.0.0.x2d2ext --fast
python -m unittest discover -s installer\tests -v
```

The verifier rejects unsupported firmware, path traversal, symbolic links, duplicate paths, unlisted payloads, oversized members and hash mismatches. `stage-camera` uploads and verifies an immutable generation but deliberately does not activate it. `--fast` keeps control on WinUSB and transfers bytes over the camera's point-to-point USB RNDIS link; the camera verifies every SHA-256 before committing each file.

## Build a verified Pixel Shift bundle

The resident payload export and GUI startup library are local build inputs and are not redistributed by this repository.

```powershell
python -m installer.build_pixel_shift_bundle `
  --payload D:\path\to\verified-resident-export `
  --gui-entry D:\path\to\libx2d2-gui-early.so `
  --out .local-only\pixel-shift-400mp-1.0.0.x2d2ext
```

## Not implemented yet

- official `.cim` import (kept separate pending a licensing-safe integration);
- Windows GUI;
- installation of the common device-side boot manager;
- real camera install, update, remove and recovery operations;
- activation of staged generations.
