# Hasselblad X2D II Extensions

English | [简体中文](README_CN.md)

Release and download repository maintained by Jimmy6Smiles. [Pixel Shift source](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-400MP-Source) is published separately; installer development remains private. This is an unofficial project.

**Current matched set: X2D II 100C, firmware 1.3.18.1, Windows manager/shared runtime 1.2.59, Pixel Shift 1.2.5-rc16, Multiple Exposure 0.1.2-rc47.** Filters 0.1.2-rc3 and Never Sleep 1.0.1 retain their payloads. Keep the runtime, MODs and firmware matched.

## What changed

This release fixes Pixel Shift's long-exposure wait budgets and signed shutter-value readiness checks. It also stops inactive Multiple Exposure UI searches from delaying the return to live view after Pixel Shift has finished. One RAW-only capture returned from the cleaning screen in about three seconds; backend source deletion took 2.757 seconds. Image processing, colour, lens correction and file-writing algorithms are unchanged by the UI fix.

The Windows manager is native-compiled, with installer source and generated build objects excluded. The distribution uses the existing project's Ed25519 origin signature. Camera runtime assets retain their tested bytes. See the [complete changes and validation scope](docs/RELEASE_1.2.59_EN.md).

The paired upgrade accepts only the **exact accepted public 1.2.43 set with all four MODs**. Before adding/removing/enabling/disabling MODs or uninstalling the runtime, perform the paired rollback to 1.2.43 and use its matching manager and supported rollback route. Arbitrary fresh installation/uninstall is not offered. No new Mac build is provided.

## Read before installing or updating firmware

Disconnects, installation failures and recovery issues across users' computers are not fully resolved. The author currently has limited spare time and cannot provide individual remote troubleshooting for every user. Early testing is recommended for users who can use AI tools to understand logs and recovery steps; users who prefer a trouble-free experience should wait. AI assistance is not a guarantee of correctness.

**Before updating the camera's OEM firmware, uninstall all old MODs, then the old shared runtime, reboot and complete verification. Check both `/data` and `/system` for old components, startup entries, installation records and unfinished transactions.** An “uninstalled” label or missing menu is not proof of a clean system. Firmware flashing may retain `/data`; it is not a substitute for uninstalling. Preserve photos and PC backups. Do not blindly delete unknown files or bypass verification.

See the [detailed installation / upgrade guide](INSTALL_UPGRADE_EN.md). If firmware has already been updated, inspect the actual state first; do not blindly run old-firmware uninstall commands.

## Downloads

| Download | Version |
|---|---|
| [Signed Windows manager + runtime + four MODs](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.59-20261127) | 1.2.59 |
| [45 in-camera filters (full bundle)](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.59-20261127) | 0.1.2-rc3; unchanged payload |
| [Pixel Shift 400 MP / AF-C (full bundle)](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.59-20261127) | 1.2.5-rc16 |
| [Multiple Exposure (full bundle)](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.59-20261127) | 0.1.2-rc47 |
| [Never Sleep (full bundle)](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.59-20261127) | 1.0.1; unchanged payload |
| [Rollback manager 1.2.43](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.43-20261107) | Use after a completed paired rollback; retain its own rollback materials |
| [Historical Mac Apple Silicon Test17](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.39-fm.3-20261028) | Older 1.2.39+fm.3; incompatible with the current set |

Extract the entire bundle and retain all attachments and `rollback-mods`. The manager owns the shared runtime; it is not a separate MOD. Do not rename fixed storage-ABI paths because they contain older version numbers.

Download Assets and check SHA256SUMS.txt; GitHub-generated Source code is not the installer. Historical releases remain for their matching environments; withdrawn versions stay withdrawn.

## Authors and scope

During live view, press and hold ⭕ to open the filter shortcut. Select your filter before entering Multiple Exposure mode; filters cannot be changed once you are in Multiple Exposure mode.

X2D2 in-camera filter author: [FarSails777](https://github.com/FarSails777). Distribution and integration by Jimmy6Smiles; third-party attribution is preserved. Pixel Shift includes AF-C and does not support HEIF. Multiple Exposure supports 2–9 frames, average/additive/bright/dark blending, accumulated overlays and a counter, all-images/result-only storage, and exit/stay after capture. Outputs are RAW, RAW+JPEG, RAW+HEIF and HEIF-only, with native 10-bit HEIF final output. RAW-only currently uses internal R+J compatible capture and cleans internal JPEGs. JPEG-only is not listed as supported. Zero-frame waiting stays in RAM; successful intermediates are cleaned in the background. Never Sleep controls screen timeout, not every power-management mechanism.

Offline tests and individual device tests do not establish universal compatibility. Back up photos; avoid irreplaceable shoots. No automatic capture, reboot or diagnostic upload is performed.
