# Firmware upgrade and installation guide

English | [简体中文](INSTALL_UPGRADE_CN.md)

## Installation reliability and support

Disconnections, installation failures and recovery issues across different users' setups have not been fully resolved. The author currently has limited spare time and cannot provide individual remote troubleshooting for every user. Early adoption is recommended for users who can use AI tools to read logs, verify files and understand recovery procedures. If you prefer to avoid troubleshooting, please wait for a later version. AI assistance does not guarantee correctness: bypassing checks, forcing overwrites or deleting whole directories is not a substitute for diagnosis.

This is unofficial, experimental software. Its GitHub Release status does not imply universal compatibility or trouble-free operation. Back up your photos and keep the battery adequately charged. The manager does not automatically take photos or restart the camera; follow its explicit instructions for manual actions.

## Before updating the camera's OEM firmware

**Uninstall the old MODs and shared runtime before updating firmware.**

1. While the old firmware still works, use the matching manager to uninstall all old MODs. Reboot when prompted and complete uninstall verification. Disabling a MOD, deleting its package from your computer or seeing its menu disappear does not constitute a completed uninstall.
2. After all MODs have been removed, uninstall the old shared runtime, reboot and verify. Do not forcibly remove a runtime that installed features still depend on.
3. Read the camera state again. Use **Detect / Clean Residues** (`检测 / 清理残留`) and **Export Read-only Diagnostics** (`导出只读诊断`) to inspect old installation traces. Check **both `/data` and `/system`** for old feature directories, installation records, unfinished transactions, staging files, backups and startup configuration. Check whether processes still load old components. Startup entries and libraries can remain even when the list says “Not installed.”
4. Detection covers known locations; it does not certify that the entire filesystem is free of residues. If files are unknown, hashes differ, a transaction is unfinished or a check fails, preserve PC backups and logs, establish ownership and complete recovery first. Do not proceed with the firmware update or bulk-delete paths based on their names. Photos and SSD/CFE image directories are not cleanup targets.
5. Once the old MODs, runtime and startup-affecting residues have been handled, confirm that factory live view and ordinary shooting work. Then update firmware using Hasselblad's official procedure. **Flashing OEM firmware is not a substitute for uninstalling: `/data` may survive the update.**

If you already updated firmware, do not blindly run uninstall commands intended for the old firmware. Start with read-only diagnostics and recover according to the actual firmware and residue state.

## Installing this release set

- Supported camera and firmware: **X2D II 100C / OEM firmware 1.3.18.1 only**. Historical 1.3.16.2 downloads are for their original environment, not this set.
- Download the current Windows ZIP and fully extract it to a writable folder. There is no matching macOS binary yet; do not use a historical Mac manager to install this set.
- Close Phocus and other camera utilities. Run only one manager. Connect USB, select the camera's Phocus tethering mode and return to live view.
- Read the camera state, then select **Detect Shared Runtime** (`检测公共接口`). Follow the prompts to install the embedded **1.2.31** runtime, manually reboot and complete verification. Then install the matched MODs. The installer owns the common startup configuration; MODs register their own components. Do not put the shared runtime in the `mods` folder as a separate MOD.
- The Windows archive includes all four matched MODs, which are also available as separate Release assets. Keep one version per feature. Do not mix files from different runtime sets merely because their displayed feature versions match.
- **Paired Upgrade / Recovery** (`配套升级 / 恢复`) accepts only the exact reviewed **1.2.30** baseline. Rollback is likewise limited to its matching 1.2.30 / Multiple Exposure rc33 set. This is not a forced upgrade mechanism for arbitrary old versions. Other old environments must first follow the uninstall and inspection procedure above.
- If a disconnect, timeout, “Task needs verification” or hash mismatch occurs, stop repeatedly clicking Install and preserve the logs. Reconnect or reboot as instructed, read state again and use **Resume Interrupted Operation** (`恢复中断`). Do not let AI tooling, Phocus and another manager compete for the USB connection.

## Versions and validation limits

| Component | Version |
|---|---|
| Shared runtime | 1.2.31 |
| In-camera filters | 0.1.1-rc5 |
| Pixel Shift 400 MP, including AF-C | 1.2.5-rc4 |
| Multiple Exposure | 0.1.2-rc34 |
| Never Sleep | 1.0.1 |

The earlier paired test run passed 515 tests. Source-export verification passed 532 tests, and four rebuilt Multiple Exposure components matched the tested payload hashes. These results do not establish compatibility with every computer and camera combination.

On the developer's camera, rc34 was checked for exiting without taking a frame, two-frame RAW+JPEG composition and playback. This does not establish acceptance of every mode, storage medium or platform. Updated Mac packaging rules exist, but the corresponding Mac build and camera installation have not been completed.

## Authors

X2D2 in-camera filter author: [FarSails777](https://github.com/FarSails777). Manager, shared runtime, other MODs and repository distribution are maintained by Jimmy6Smiles. Third-party and OEM rights remain with their respective owners.
