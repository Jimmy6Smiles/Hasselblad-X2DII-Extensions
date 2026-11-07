# 1.2.42: Pixel Shift RC13 and matched Windows release

For **Hasselblad X2D II 100C / OEM firmware 1.3.18.1**.

This release fixes Pixel Shift stopping during JPEG processing with the newer shared runtime. The old rendering/calibration session checks rejected the new GUI host subdirectory; the menu could subsequently report that capture integration was incomplete. Both the processing-side and calibration-hook path parsers are corrected, with matching boot-entry and capture-host approval bindings. Install the complete matched set rather than replacing a single rendering program or MOD.

## Downloads and versions

- [Windows manager/shared runtime 1.2.42 full bundle](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.42-20261107): download `X2DII-Mod-Manager-1.2.42-Windows.zip` from Assets.
- [Separate Pixel Shift MOD](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-400mp-1.2.5-rc13-fw-1.3.18.1-runtime-1.2.42): `pixel-shift-400mp-1.2.5-rc13.x2d2ext`, requiring this release's 1.2.42 manager and shared runtime.
- The full bundle includes four MODs. Check `SHA256SUMS.txt` and the bundled version list. GitHub-generated Source code archives contain the public documentation repository, not the installer.

| Component | Version | Scope |
|---|---|---|
| Windows manager/shared runtime | 1.2.42 | Matched approval, migration and recovery bindings |
| Pixel Shift 400 MP, including AF-C | 1.2.5-rc13 | JPEG rendering/calibration session path compatibility |
| 45 in-camera filters | 0.1.2-rc2 | Existing payload retained |
| Multiple Exposure | 0.1.2-rc42 | Existing payload retained |
| Never Sleep | 1.0.1 | Existing payload retained |

**No new Mac build is provided.** [Historical Mac Test17](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.39-fm.3-20261028) belongs to the older 1.2.39+fm.3 set and cannot install, upgrade or verify this 1.2.42/RC13 set. Windows results do not establish Mac build or hardware acceptance.

## Upgrading from formal 1.2.41

1. Close Phocus and the old manager. Fully extract the new Windows bundle, keep the camera powered and connected by USB, and return to live view.
2. Read state in the new manager and choose **Paired Upgrade / Recovery** (`配套升级／恢复`). This migration accepts only the exact formal 1.2.41 matched set and valid installation records. Keep the original manager and PC backups.
3. Reboot normally when prompted, return to live view, then resume recovery/verification until the manager confirms completion.
4. Other installed MODs, settings and photographs are preserved; absent features are not automatically added. On timeout, identity mismatch or an unfinished transaction, preserve logs and resume the owning transaction instead of repeatedly installing or forcing an overwrite.

Other older sources must follow their existing supported upgrade/recovery paths; arbitrary direct migration is not claimed. The full uninstall requirement before updating OEM camera firmware remains in the [installation guide](../INSTALL_UPGRADE_EN.md).

**Do not independently install RC13 over 1.2.41 or older shared runtimes.** The logical runtime version is 1.2.42, while native components retain fixed storage-ABI paths that may contain `common-runtime/1.2.39`. These are different version fields. Renaming a directory does not create a matched runtime.

## Known upgrade finalization case

During this hardware upgrade, the final command restoring the system partition to read-only failed after the complete files had been written and read back. The manager stopped without marking the upgrade complete. After a normal reboot, resuming the original transaction on the same computer verified the read-only system, actual loaded components and backend readiness. This release retains that workflow; it does not claim to fix the underlying remount cause.

If the same finalization failure occurs, preserve the technical log and PC backups. After photo saving has finished, reboot normally, read state and resume the owning transaction. Do not repeatedly reinstall or edit completion markers. Other failures require their own log review; a generic failure message alone does not establish this case.

## Hardware result and limits

One development camera completed the matched upgrade, manual reboot and loaded-generation verification, followed by one 400 MP RAW+JPEG capture. The output was visible; the user confirmed playback, zoom and color/distortion appearance. The six source frames were deleted.

The camera returned to live view about 59 seconds after the six-frame capture completed. This is a reference for that camera and group, not a cross-device performance promise.

**A second consecutive capture, JPEG-only output, physical 1.2.42 uninstall/rollback and a new Mac build have not completed this round of acceptance.** Offline binding, fault-injection and recovery tests do not replace those hardware tests or establish compatibility with every lens, storage combination or computer.

In-camera filter author: [FarSails777](https://github.com/FarSails777). Manager, shared runtime and other MODs maintained by Jimmy6Smiles. Third-party and OEM component rights are preserved.
