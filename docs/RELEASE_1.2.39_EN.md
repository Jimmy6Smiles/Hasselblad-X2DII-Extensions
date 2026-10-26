# Corrected matched set 1.2.39 — 2026-10-26

For Hasselblad X2D II 100C / OEM firmware **1.3.18.1**. This is a published release; feature rc/experimental labels still apply.

## Changes

- **Shared Runtime 1.2.39** fixes the capture host's stale reference to the 1.2.35 sensor-profile directory and binds it to its own version. The broken 1.2.38 set is withdrawn.
- **Pixel Shift 1.2.5-rc12** preserves accepted rc8 behavior with version/host-path changes only. No rc9/rc10 timing diagnostics, new image algorithms or new speed improvements.
- **Multiple Exposure 0.1.2-rc42** preserves rc41's live-preview LUT red/blue correction and rebinds to 1.2.39. Final-image processing is unchanged.
- **Filters 0.1.1-rc5 / Never Sleep 1.0.1** retain identical packages.
- The Windows manager defaults to the reverse network transfer used successfully on the developer camera. Rollback to withdrawn 1.2.38 is disabled. The manager owns shared startup configuration; MODs only register their own components.

## Install and recover

Fully extract the Windows ZIP containing the runtime and all four MODs. **No matching macOS binary is available.** Do not substitute older Mac packages. Close Phocus and other managers, use USB Phocus mode, return to live view and read state before following prompts. Capture and reboot are manual.

**Direct paired upgrade accepts only the exact recognized 1.2.38 set with its expected registration and startup plans.** A camera rescued by renaming plans or restoring factory startup entries is not a normal upgrade baseline. Unknown or unfinished transactions need state-specific recovery; this public installer is not a universal rescue tool. For 1.2.35 and other older environments, finish uninstall, reboot acceptance and residue checks using the matching manager before installing.

Rollback to 1.2.38 is unavailable. Keep PC backups and logs; do not repeatedly overwrite an unfinished installation. The 1.2.38 downloads are withdrawn; other historical releases remain for their original environments.

**Before updating OEM firmware, uninstall all MODs and the shared runtime, reboot and inspect /data and /system for old components, startup entries, registration and unfinished transactions. Flashing is not an uninstall.** Never bulk-delete photos or unknown directories.

Installation, disconnect and recovery issues are not resolved for every computer. The author currently has limited spare time and cannot provide individual remote troubleshooting for every user. Early testing is recommended for users able to use AI tools to interpret logs and verify state; those seeking a trouble-free experience should wait. AI does not replace verification.

## Validation scope

The developer camera completed deployment, reboot loading, both backend readiness checks and PC-backed old-component cleanup, returning the system to read-only. The user reports normal operation. Packaged camera components match this accepted build. The release GUI's transport default and withdrawn-rollback policy were tested offline separately.

120 paired tests, 2 release-policy tests and 3 sensor-profile-path regression tests passed. EXE startup self-test and embedded-resource comparisons passed. This round did not rerun every shooting mode, format, fresh installation or uninstall scenario, and is not an all-device guarantee.

## Features and authors

Multiple Exposure offers 2–9 frames, average/additive/bright/dark modes, accumulated live overlays, a frame counter, all-images/result-only storage and exit/stay after shooting. Outputs: RAW, RAW+JPEG, RAW+HEIF and HEIF-only. HEIF final output uses the native 10-bit pipeline; overlays may use lower-depth previews. RAW-only still uses internal R+J compatible capture, then restores format and removes internal JPEGs. JPEG-only is not advertised as available in this release. Waiting without a frame creates no card job directory; successful intermediate files are cleaned in the background.

Choose filters in single-shot mode before entering Multiple Exposure. Hold ⭕ in live view for the filter shortcut. Filters cannot yet be changed inside Multiple Exposure. Pixel Shift supports RAW/JPEG/RAW+JPEG, not HEIF, and includes AF-C; do not install the old separate AF-C package alongside it.


In-camera filters by [FarSails777](https://github.com/FarSails777); manager/runtime/other MODs maintained by Jimmy6Smiles. OEM and third-party rights retained. No private source, device logs, photos or recovery scripts are included.
