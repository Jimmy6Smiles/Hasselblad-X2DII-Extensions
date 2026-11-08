# 1.2.43: Corrected in-camera filter colors · hardened Windows packaging

For **Hasselblad X2D II 100C / OEM firmware 1.3.18.1**.

This release corrects RGB/BGR interpretation in the filter conversion pipeline, restoring the intended cool/warm direction of CineStill 800T and Gold 200. It pairs **runtime 1.2.43** with **Filters 0.1.2-rc3**. Halation, RAW post-processing and experimental hooks are excluded.

Download and fully extract **X2DII-Mod-Manager-1.2.43-Windows-Hardened.zip**. It supplies the matched runtime, all 45 filter resources and four MODs. The installer manages the runtime; it is not a standalone MOD.

| Component | Version | Scope |
|---|---|---|
| Windows manager / shared runtime | 1.2.43 | Filter identity/resource approval; native-compiled Windows manager |
| In-camera filters | 0.1.2-rc3 | Channel correction for 26 CUBE conversions; 19 recipes unchanged |
| Pixel Shift 400 MP, including AF-C | 1.2.5-rc13 | Retains accepted 1.2.42 payload |
| Multiple Exposure | 0.1.2-rc42 | Unchanged payload |
| Never Sleep | 1.0.1 | Unchanged payload |

Corrected recipe IDs: 17–26, 29–34 and 36–45. FOTOS 1–15, classic monochrome 16, native GR Negative 27, GR Positive 28 and Portra 400 35 retain their exact recipe bytes. All 45 resource sources were reviewed; this is not a new physical film simulation or calibration of every look.

The existing hold-⭕ shortcut, strength control and hiding/restoring the original live-view UI are preserved. Select the group filter before entering Multiple Exposure. Pixel Shift/AF-C code is unchanged; Pixel Shift does not support HEIF.

## Supported upgrade and rollback

The upgrade accepts only the **exact accepted runtime 1.2.42 set with all four MODs correctly installed and registered**. Use `滤镜通道修正／恢复` (Filter Channel Correction / Recovery) without first uninstalling Filters. Other versions, missing MODs, unknown components and unfinished transactions are not force-upgrade baselines.

Close Phocus and other managers, keep USB Phocus mode and live view, read state and follow the prompts. Reboot manually when asked, then resume the owning transaction on the same computer. Preserve PC backups and logs; do not repeatedly install after a communication failure.

Old and new LUT libraries remain separate. Original controls, components and rollback materials are retained. The matched rollback target is **1.2.42 + Filters rc2**, which also removes this color correction. Keep the complete extracted directory and `rollback-mods`.

Installation/removal guards remain: to install, remove, enable or disable MODs, uninstall the runtime or clean its components, **first perform the paired rollback to 1.2.42, then use its matching manager**. This generation does not expose untested arbitrary-set 1.2.43 installation or general uninstall. It is not a universal rescue tool. An exact existing 1.2.43/rc3 installation does not need reinstalling. Automatic downgrade from early halation experiments is not supported.

## Hardening and validation

The Windows manager is compiled to native code with Nuitka. Installer Python source and a directly extractable installer PYZ/pyc archive are excluded. Generated headers/objects, tests, caches, device logs and private backups are excluded. Camera-native components, QML, scripts and LUTs retain the tested bytes; those runtime resources remain extractable and are not claimed to be encrypted or impossible to reverse engineer.

Hardening changes PC distribution only. Accepted camera payloads are not repacked or stripped. Required historical recovery resources, LUT libraries and MOD envelopes are hash-checked. See the published `PACKAGING_VERIFICATION.json`, `VERSIONS.json` and `SHA256SUMS.txt`. Third-party runtime/compiler licenses are retained in the bundle.

One development camera completed deployment, manual reboot, all 45 filter entries and matched identities for all four MODs. The user confirmed correct CineStill 800T / Gold 200 live view, and controlled JPG comparisons confirmed the channel correction. After withdrawing halation experiments, the stable combination passed actual loaded-component and read-only-system verification again.

This round did not repeat every look, HEIF capture, Multiple Exposure/Pixel Shift capture, arbitrary fresh installation or 1.2.43 uninstall. The hardened distribution receives offline self-tests and startup checks, without a new camera install/capture trial; this is not all-environment hardware acceptance. **No new macOS binary is provided**; historical Mac Test17 cannot manage this 1.2.43 set.

In-camera filters by [FarSails777](https://github.com/FarSails777); manager, runtime and other MODs maintained by Jimmy6Smiles. OEM/third-party rights are retained. GitHub-generated Source code archives contain the documentation repository, not the installer.
