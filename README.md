# Hasselblad X2D II Extensions

English | [简体中文](README_CN.md)

Release and download repository maintained by Jimmy6Smiles. Source development is private. This is an unofficial project.

**Current experimental set: X2D II 100C, firmware 1.3.18.1, shared runtime 1.2.31.** Do not mix it with the historical 1.3.16.2 packages.

## Read before installing or updating firmware

Disconnects, installation failures and recovery issues across users' computers are not fully resolved. The author currently has limited spare time and cannot troubleshoot each installation individually. Early testing is recommended for users who can use AI tools to understand logs and recovery steps; users who prefer a trouble-free experience should wait. AI assistance is not a guarantee of correctness.

**Before updating the camera's OEM firmware, uninstall all old MODs, then the old shared runtime, reboot and complete verification. Check both `/data` and `/system` for old components, startup entries, installation records and unfinished transactions.** An “uninstalled” label or missing menu is not proof of a clean system. Firmware flashing may retain `/data`; it is not a substitute for uninstalling. Preserve photos and PC backups. Do not blindly delete unknown files or bypass verification.

See the [detailed installation / upgrade guide (Chinese)](INSTALL_UPGRADE_CN.md). If firmware has already been updated, inspect the actual state first; do not blindly run old-firmware uninstall commands.

## Downloads

| 下载 | 版本 |
|---|---|
| [Windows 安装器 + 公共运行时](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.31-preview-20261026) | 1.2.31 |
| [公共运行时身份与说明](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/common-runtime-1.2.31) | 1.2.31 |
| [机内滤镜 45 款](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/in-camera-filters-0.1.1-rc5-fw-1.3.18.1-runtime-1.2.31) | 0.1.1-rc5 |
| [像素超频 400 MP（含 AF-C）](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-400mp-1.2.5-rc4-fw-1.3.18.1-runtime-1.2.31) | 1.2.5-rc4 |
| [多重曝光](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/multiple-exposure-0.1.2-rc34-fw-1.3.18.1-runtime-1.2.31) | 0.1.2-rc34 |
| [永不息屏](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/never-sleep-1.0.1-fw-1.3.18.1-runtime-1.2.31) | 1.0.1 |


The Windows archive includes the four matched MODs. They are also released separately. Shared runtime binaries are embedded in the installer and managed by it; the runtime release provides identity metadata and links, not a standalone MOD. **No matching macOS binary is available yet.** Historical Mac downloads are not compatible with this new set.

Download Release Assets, not GitHub's automatic Source code archive. Check SHA256SUMS.txt. Previous releases are retained for their original firmware environments. The paired upgrade path accepts only the exact reviewed 1.2.30 baseline; it is not an arbitrary-version upgrade mechanism.

## Authors and scope

X2D2 in-camera filter author: **farsails777@gmail.com**, the supplied Git account email. Distribution and integration by Jimmy6Smiles; third-party attribution is preserved. Pixel Shift includes AF-C and does not support HEIF. Multiple Exposure rc34 adds lazy job creation and background cleanup of successful jobs. Never Sleep controls screen timeout, not every power-management mechanism.

The MOD archives contain signed provenance in their ZIP comments with detached manifests and signatures. Executable and camera payload bytes remain unchanged. See [provenance verification](PROVENANCE.md) and [third-party notices](THIRD_PARTY_NOTICES.md). This is not DRM or an anti-reverse-engineering guarantee.

Offline tests and individual device tests do not establish universal compatibility. Back up photos; avoid irreplaceable shoots. No automatic capture, reboot or diagnostic upload is performed.
