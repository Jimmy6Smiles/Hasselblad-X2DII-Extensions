# Hasselblad X2D II Extensions

English | [简体中文](README_CN.md)

Release and download repository maintained by Jimmy6Smiles. Source development is private. This is an unofficial project.

**Current experimental set: X2D II 100C, firmware 1.3.18.1, shared runtime 1.2.38.** Do not mix it with the historical 1.3.16.2 packages.

## What changed

**Multiple Exposure rc41 fixes swapped red/blue channels in unfiltered live view.** Final image processing is unchanged. Color live view, focus-zoom overlay recovery, two-frame composition and playback passed on the developer camera. Pixel Shift rc11 only updates host paths; filters and Never Sleep are unchanged.

[Release notes and validation scope](docs/RELEASE_1.2.38_EN.md). Direct paired upgrade supports only exact 1.2.35; other environments must follow the installation guide.

## Read before installing or updating firmware

Disconnects, installation failures and recovery issues across users' computers are not fully resolved. The author currently has limited spare time and cannot provide individual remote troubleshooting for every user. Early testing is recommended for users who can use AI tools to understand logs and recovery steps; users who prefer a trouble-free experience should wait. AI assistance is not a guarantee of correctness.

**Before updating the camera's OEM firmware, uninstall all old MODs, then the old shared runtime, reboot and complete verification. Check both `/data` and `/system` for old components, startup entries, installation records and unfinished transactions.** An “uninstalled” label or missing menu is not proof of a clean system. Firmware flashing may retain `/data`; it is not a substitute for uninstalling. Preserve photos and PC backups. Do not blindly delete unknown files or bypass verification.

See the [detailed installation / upgrade guide](INSTALL_UPGRADE_EN.md). If firmware has already been updated, inspect the actual state first; do not blindly run old-firmware uninstall commands.

## Downloads

| Download | Version |
|---|---|
| [Windows installer + shared runtime](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.38-20261026) | 1.2.38 |
| [Shared runtime identity and documentation](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/common-runtime-1.2.38) | 1.2.38 |
| [45 in-camera filters](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/in-camera-filters-0.1.1-rc5-fw-1.3.18.1-runtime-1.2.38) | 0.1.1-rc5 |
| [Pixel Shift 400 MP (including AF-C)](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-400mp-1.2.5-rc11-fw-1.3.18.1-runtime-1.2.38) | 1.2.5-rc11 |
| [Multiple Exposure](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/multiple-exposure-0.1.2-rc41-fw-1.3.18.1-runtime-1.2.38) | 0.1.2-rc41 |
| [Never Sleep](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/never-sleep-1.0.1-fw-1.3.18.1-runtime-1.2.38) | 1.0.1 |

The Windows archive includes the four matched MODs. They are also released separately. Shared runtime binaries are embedded in the installer and managed by it; the runtime release provides identity metadata and links, not a standalone MOD. **No matching macOS binary is available yet.** Historical Mac downloads are not compatible with this new set.

Download Release Assets, not GitHub's automatic Source code archive. Check SHA256SUMS.txt. Previous releases are retained for their original firmware environments. The paired upgrade path accepts only the exact reviewed 1.2.35 baseline; it is not an arbitrary-version upgrade mechanism.

## Authors and scope

During live view, press and hold ⭕ to open the filter shortcut. Select your filter before entering Multiple Exposure mode; filters cannot be changed once you are in Multiple Exposure mode.

X2D2 in-camera filter author: [FarSails777](https://github.com/FarSails777). Distribution and integration by Jimmy6Smiles; third-party attribution is preserved. Pixel Shift includes AF-C and does not support HEIF. Multiple Exposure supports 2–9 frames, average/additive/bright/dark blending, accumulated overlays and a counter, all-images/result-only storage, and exit/stay after capture. Outputs are RAW, RAW+JPEG, RAW+HEIF and HEIF-only, with native 10-bit HEIF final output. RAW-only currently uses internal R+J compatible capture and cleans internal JPEGs. JPEG-only is not listed as supported. Zero-frame waiting stays in RAM; successful intermediates are cleaned in the background. Never Sleep controls screen timeout, not every power-management mechanism.

Offline tests and individual device tests do not establish universal compatibility. Back up photos; avoid irreplaceable shoots. No automatic capture, reboot or diagnostic upload is performed.
