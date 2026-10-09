# X2D II Extension Manager (offline foundation)

[English](README.md) | [简体中文](README_CN.md)

This directory contains the first safety boundary for a unified X2D II extension installer. It builds and verifies `.x2d2ext` bundles and exercises atomic generation activation and rollback locally. **It does not communicate with or modify a camera yet.**

The initial working package target is Electronic Shutter AF-C. Pixel Shift will be added after all of its runtime payloads and build recipes are represented in the public tree.

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
python -m unittest discover -s installer\tests -v
```

The verifier rejects unsupported firmware, path traversal, symbolic links, duplicate paths, unlisted payloads, oversized members and hash mismatches. Activation uses immutable generations and an atomic `active.json` switch, so a failed staging operation cannot replace the previous active state.

## Not implemented yet

- official `.cim` import (kept separate pending a licensing-safe integration);
- the Windows GUI and WinUSB transport;
- installation of the common device-side boot manager;
- real camera install, update, remove and recovery operations;
- Pixel Shift bundle generation.
