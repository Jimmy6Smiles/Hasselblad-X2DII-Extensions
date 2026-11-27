# 1.2.59: Pixel Shift exposure handling and completion UI fix


For **Hasselblad X2D II 100C, factory firmware 1.3.18.1, Windows**. This set pairs common runtime **1.2.59**, Pixel Shift **1.2.5-rc16**, and Multiple Exposure **0.1.2-rc47**. In-camera Filters **0.1.2-rc3** and Never Sleep **1.0.1** retain their existing payloads.

| Component | Version | Scope |
|---|---|---|
| Windows manager / common runtime | 1.2.59 | Matched identities, upgrade/recovery and rollback binding |
| 400 MP Pixel Shift, including AF-C | 1.2.5-rc16 | Exposure-aware capture waits, recovery/finalization and signed shutter-value readiness checks |
| Multiple Exposure | 0.1.2-rc47 | Early exits for inactive UI; existing active-mode and focus restoration behavior retained |
| 45 in-camera filters | 0.1.2-rc3 | Existing payload and recipes retained |
| Never Sleep | 1.0.1 | Existing payload retained |

## Changes

Pixel Shift derives capture and abnormal-recovery wait budgets from the actual shutter time, and corrects the standalone readiness check's handling of negative Tv values for long exposures. While waiting for the factory capture service's release acknowledgement, finalization keeps status requests and input gating responsive. Task completion is committed after confirmation. Factory file deletion, metadata and album registration remain in place.

Previously, the inactive Multiple Exposure UI could still recursively search factory scene objects during a Pixel Shift shot. This could leave the rear display on “Cleaning source images” after the backend had finished. Preview lookup now checks mode selection and live-view state first. Focus lookup runs when Multiple Exposure is selected or still owns/restores focus. Active Multiple Exposure target lookup and focus restoration retain their previous logic.

The UI fix preserves the verified image processing, colour, lens correction, container and filter-recipe bytes. It adds no sharpening, halation or other image effect. Pixel Shift does not support HEIF.

## Download and upgrade

Download and fully extract this release's complete Windows package. Retain its resources, MODs, rollback material and PC transaction backups. Check `SHA256SUMS.txt`, `VERSIONS.json` and the distribution-origin signature. The manager maintains the common runtime; it is not a separate MOD. Do not install ME47 or PS16 by overwriting an older matched set.

This automatic upgrade targets the **exact accepted public 1.2.43 set with all four MODs installed and registered**: Filters rc3, Multiple Exposure rc42, Pixel Shift rc13 and Never Sleep 1.0.1. Other sources, private trial builds, missing MODs or incomplete transactions must follow their supported procedures. Do not force an overwrite.

1. Exit Phocus and other managers. Keep the camera powered and connected by USB, return to live view, and wait for image saving to finish.
2. Read camera state in the new manager and select the matched upgrade/recovery action.
3. Shut down and restart normally when prompted. Continue verification on the same PC using the owning transaction.
4. Retain backups and logs. Stop further writes if components or command completion are uncertain; preserve the evidence rather than repeating installation.

Matched rollback targets the verified and backed-up **public 1.2.43 four-MOD set**. This release does not claim device validation of arbitrary-source installation, arbitrary MOD removal or every rollback environment. Where the final build protects feature changes/removal, restore the source set through matched rollback and use its corresponding manager; follow the final package instructions.

Logical runtime versions and native storage ABI versions are separate. Some paths still contain `common-runtime/1.2.39`; do not edit those directory numbers.

## Device evidence for this release

The target 1.2.59 camera set passed deployment, restart and the capture checks below using a private 1.2.58→1.2.59 transaction. The new public manager's public 1.2.43→1.2.59, recovery and rollback-to-1.2.43 routes receive separate offline tests; this public migration route was not rerun on the camera in this round.

One development camera completed the 1.2.59 update, manual restart, loaded-component checks and backend verification, then captured **one RAW-only group with exit-after-capture selected (actual keep=false)**. The result was `B0004178.3FR`; all six source images were deleted. The backend is ready without recovery or a pending task, and the system partition is read-only.

- Source deletion: **2.757 seconds**; cleanup stage start to task finalization: **2.864 seconds**.
- Six inputs verified to task finalization: **20.813 seconds**, excluding capture of those six frames.
- The user reported about **3 seconds** on the cleaning screen before live view returned. Earlier individual tests had reported waits of roughly 30–90 seconds.
- The main-thread observation did not reproduce the old trace's roughly 90 seconds of sustained scene-walk work after backend completion. This is supporting evidence from one group, without an exact timestamp for the displayed exit frame.

About 37.078 seconds elapsed from the first observed new-job snapshot to backend completion, including capture and other stages. That has a different scope from the post-capture figure above. These are single-camera, single-group observations, not cross-device performance promises. The old CPU comparison used keep=true whereas this run used keep=false. An earlier keep=false long-exposure group also had a reported long display delay, but no equivalent main-thread trace.

**This run does not cover keep=true, a consecutive second group, JPEG/RAW+JPEG, a complete long-exposure regression, ME47 Multiple Exposure captures, arbitrary installation/removal combinations or a new macOS build.** Offline tests, loaded-component verification and this RAW result do not replace those checks. No new Mac package is provided; historical Mac packages cannot manage this 1.2.59 set.

## Compilation and origin verification

The Windows manager follows the Nuitka native-compiled distribution approach. Installer Python source, directly extractable installer bytecode, build objects, device logs and private backups are excluded from the public package. Required camera native programs, QML, scripts, LUTs and historical recovery resources retain their verified bytes. Runtime resources remain extractable; absolute resistance to reverse engineering is not claimed.

Distribution origin and integrity are checked with the existing project's Ed25519 public key. This signature is not Windows Authenticode certification, Hasselblad certification or functional acceptance. The pinned SHA-256 fingerprint of the raw Ed25519 public key is `1288c2a763f2807df826e9266267c19f58c81e4f541543f15fa9ac6083b87c4c`. Check this fixed value and the final verification inventory; do not trust a key merely because it accompanies a download.

In-camera filters by [FarSails777](https://github.com/FarSails777). The manager, common runtime and other MODs are maintained by Jimmy6Smiles. Third-party and factory rights remain reserved; licenses are included. GitHub's automatically generated Source code archives contain the documentation repository, not the installer.
