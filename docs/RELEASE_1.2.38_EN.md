# Matched set 1.2.38 — 2026-10-26

For Hasselblad X2D II 100C OEM firmware **1.3.18.1** only. Unofficial extensions; existing rc/test labels and tested executable bytes are retained.

Multiple Exposure **0.1.2-rc41** corrects native BGR LUT output decoding for the RGB live-preview texture. This fixes red-to-blue and yellow-to-cyan live view with no filter. Final RAW/JPEG/HEIF processing is unchanged. Runtime **1.2.38** updates bindings. Pixel Shift **1.2.5-rc11** is only a path rebind of accepted rc8; algorithms/UI are unchanged and rc9/rc10 timing diagnostics are excluded. Filters **0.1.1-rc5** and Never Sleep **1.0.1** retain their payloads.

Multiple Exposure offers 2–9 frames, average/additive/bright/dark modes, accumulated live overlays, a frame counter, all-images/result-only storage and exit/stay after shooting. Outputs: RAW, RAW+JPEG, RAW+HEIF and HEIF-only. HEIF final output uses the native 10-bit pipeline; overlays may use lower-depth previews. RAW-only still uses internal R+J compatible capture, then restores format and removes internal JPEGs. JPEG-only is not advertised as available in this release. Waiting without a frame creates no card job directory; successful intermediate files are cleaned in the background.

Choose filters in single-shot mode before entering Multiple Exposure. Hold ⭕ in live view for the filter shortcut. Filters cannot yet be changed inside Multiple Exposure. Pixel Shift supports RAW/JPEG/RAW+JPEG, not HEIF, and includes AF-C; do not install the old separate AF-C package alongside it.

## Install and upgrade

Extract the Windows ZIP fully. It contains the manager, shared runtime and four matched MODs. No matching macOS build exists. Close Phocus and other managers, connect USB and return to live view. Read state and follow the manager's install or paired upgrade/recovery prompts. Reboots and capture are manual.

**Direct paired upgrade and rollback support only the exact reviewed 1.2.35 set.** Other versions, including 1.2.31/1.2.36/1.2.37, are not force-upgrade targets. Use the matching older manager to finish uninstall/reboot/residue checks before a clean installation. Preserve PC backups and logs. Do not overwrite an unfinished transaction or manually delete unknown state. Before OEM firmware updates, uninstall MODs/runtime and inspect both /data and /system; flashing does not replace uninstalling. Existing releases remain available.

Installation and recovery issues remain possible; individual remote support is limited. AI assistance does not replace verification. See the repository installation guide.

## Validation

The developer camera completed 1.2.35-to-1.2.38 upgrade, reboot acceptance and cleanup. The user confirmed rc41 color live view without filters, overlay recovery after focus magnification, two-frame RAW+JPEG composition and full/zoomed/panned playback. Earlier versions validated 10-bit RAW+HEIF/HEIF-only output, filter integration, 3/4-frame accumulated previews, zero-frame storage and background cleanup. Not all formats, frame counts or modes were rerun in this build. 120 offline tests and 620 embedded-resource checks do not establish all-device/fresh-install/uninstall/rollback compatibility. Pixel Shift was rebound only; no new capture acceptance or speed fix is claimed.

In-camera filters by [FarSails777](https://github.com/FarSails777); manager/runtime/other MODs maintained by Jimmy6Smiles. OEM and third-party rights retained. No private source, device logs, photos or recovery scripts are included.
