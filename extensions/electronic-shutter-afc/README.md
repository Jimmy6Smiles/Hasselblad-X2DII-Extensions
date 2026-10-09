# X2D II Electronic Shutter AF-C

[English](README.md) | [简体中文](README_CN.md)

An X2D II 100C extension that enables AF-C with the electronic shutter. It is completely independent of Pixel Shift.

## Compatibility

- Camera: Hasselblad X2D II 100C
- Firmware: **1.3.16.2**
- Device verified: AF-C can be selected and continuously tracks in electronic-shutter, single-drive mode
- Preserved restrictions: lens-firmware capability checks and the original Self-Timer, Interval, Exposure Bracketing and Focus Bracketing restrictions

Do not use this build on the first-generation X2D, another camera model or another firmware version. Code and UI resource locations are firmware-pinned. The builder validates complete file hashes and critical instructions and rejects every mismatch.

## Independence from Pixel Shift

There is no runtime dependency:

- no pixel-shift capture, RAW merge, album or playback code is included;
- `/data/x2d2-full-v1`, Pixel Shift services and Pixel Shift startup scripts are not referenced;
- the backend is the standalone `afc-electronic.so` library;
- the UI adaptation is generated directly from the factory 1.3.16.2 `camera-gui`.

Do not overwrite a camera whose `camera-gui` or `camera-service` startup entry has already been modified. Rebuild from the factory firmware and make the installer merge existing changes. This package does not assume that two complete patched GUI binaries can safely overwrite each other.

## Build

Python 3, `pyelftools` and Android NDK r27 are required. Users must extract `camera-service` and `camera-gui` from a legally obtained 1.3.16.2 firmware image. Vendor files are not distributed in this repository or release archive.

```powershell
python -m pip install pyelftools
python build.py `
  --camera-service D:\path\to\system\bin\camera-service `
  --camera-gui D:\path\to\system\bin\camera-gui `
  --ndk D:\path\to\android-ndk-r27 `
  --out output
```

Outputs:

- `payload/afc-electronic.so`: ARM64 backend loaded only into `camera-service`;
- `payload/camera-gui`: complete GUI containing only the electronic-shutter AF-C UI adaptation;
- `payload/camera-service.env`: required `LD_PRELOAD` value;
- `manifest.json`: input/output hashes and the exact two modified UI resources.

`prebuilt/1.3.16.2/afc-electronic.so` contains only project-owned code. The complete patched vendor GUI must be generated locally.

## Installation boundary

This is not a CIM image and does not include a generic USB maintenance driver or a tool for bypassing camera permissions. An installer must at least:

1. verify the camera model, firmware and factory file hashes again;
2. back up the original `camera-gui` and `camera-service.rc`;
3. install the locally generated `camera-gui` and `afc-electronic.so`;
4. add only `LD_PRELOAD=/system/lib64/libx2d2-afc-electronic.so` to `camera-service`;
5. restore the system partition to read-only and reboot;
6. require `ready:true` in `/tmp/x2d2-afc-electronic.json`, then verify factory AF-S, MF and mechanical-shutter behavior.

Do not make the Pixel Shift startup entry a prerequisite. Do not deploy through an installer that lacks atomic backup, readback verification and failure recovery.

## Implementation

The backend makes two firmware-pinned changes: it preserves the AF-C capability bit and skips the electronic-shutter-only AF-C fallback branch in `updateFocusMode()`. All other original lens and drive-mode checks remain active. The UI enables AF-C in the control screen and live view under the same conditions and removes only the electronic-shutter-specific blocked message.

This is an unofficial experimental feature. It can make the camera unresponsive, lose focus or prevent capture. Do not use it for irreplaceable work.
