# Hasselblad X2D II Extensions

[English](README.md) | [简体中文](README_CN.md)

Independent experimental extensions for the Hasselblad X2D II 100C, maintained by Jimmy6Smiles.

**Supported firmware: 1.3.16.2. This is not an official Hasselblad project.**

## Extensions

| Extension | Status | Description |
| --- | --- | --- |
| [Electronic Shutter AF-C](extensions/electronic-shutter-afc/README.md) | Device verified | Enables AF-C with the electronic shutter while preserving the original lens and drive-mode restrictions. Independent of Pixel Shift. |
| [Pixel Shift](extensions/pixel-shift/README.md) | Device verified | Six-frame 400 MP RAW capture, optional JPEG output, album integration, source-frame cleanup and assisted playback. |

New features should be added as peer directories under `extensions/`; feature-specific source, firmware versions, documentation and release packages stay inside their own directory.

The first offline foundation of the unified installer is available under [installer](installer/README.md). It can build and verify local `.x2d2ext` bundles and test atomic activation/rollback; camera transport is not implemented yet.

```text
extensions/
├── electronic-shutter-afc/
│   ├── src/
│   ├── prebuilt/
│   └── dist/
└── pixel-shift/
    └── firmware/
        └── 1.3.16.2/
```

## Safety

These extensions can make the camera unresponsive, cause failed captures or lose data. Back up all photographs and do not use experimental builds for irreplaceable work. Firmware-specific offsets and binaries must never be reused on another model or firmware version.

The repository does not contain Hasselblad firmware images, photographs, device credentials or vendor libraries. A source directory or release archive is not automatically a universal installer; follow the installation boundary documented by each extension.

## Sources and licensing

The X2D II implementations were developed from local research snapshots and reference processing ideas from Hasselblad Feature Extensions / Hasselblad Enhancement Research. Original notices are preserved in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Files without an explicit license are not automatically relicensed merely because the repository is publicly readable.
