# Unified resident startup v2 — firmware 1.3.16.2

This startup-only layer was accepted on the development camera. It does not
change capture workers, RAW/JPEG encoding, image registration or cleanup logic.
The resident selector has been installed and read back; a reboot after promotion
to resident mode is still pending. One-boot operation, menus and auxiliary zoom
were confirmed on camera. No new photo test is claimed for this startup revision.

## What changed

- Capture and storage extensions load on their first service start.
- The prepatched GUI and immutable helpers live in a versioned system directory.
  Boot no longer copies the 64 MB GUI. Helpers/UI use links; the small preload
  libraries retain their established RAM paths to preserve runtime identity checks.
- The factory GUI service entry executes the prepared GUI in the original camera
  security domain. It does not wait for the specialty backend.
- The existing backend readiness checks keep pixel shift unavailable until ready;
  normal viewfinding does not wait for backend adoption.
- `/data/x2d2-full-v1/unified.enabled` selects resident startup. `unified.once`
  remains available for one-boot testing. Disabled extensions or pending jobs use
  the prior recovery/startup route. No SELinux policy modification is required.

Observed boot-relative milestones (not a screen-ready or first-shot measurement):

| Milestone | Seconds |
| --- | ---: |
| GUI released for execution | 1.43 |
| Capture service started | 1.56 |
| Storage service started | 2.21 |
| Backend adopted | 4.24 |

## Build and test

Use Android NDK r27 clang on Windows or Linux:

```text
python build.py --cc <NDK>/toolchains/llvm/prebuilt/<host>/bin/clang
```

On Linux/WSL, run `python3 test_startup.py`. It executes 12 selector, dependency
ordering and fallback scenarios using mocks; it does not establish hardware
readiness or image correctness. The build contains only self-authored libraries
and scripts. No proprietary GUI, firmware, IQ tables or device logs are included.

## Installation contract — not a universal installer

This requires the already installed resident payload and legacy recovery scripts.
Do not install these files alone on an unprepared camera. The public installer
still stages bundles only; it does not activate this boot integration.

1. Back up the existing init definitions. Verify firmware and idle/no-pending-job
   state. Stage the prepared GUI, unchanged runtime helpers/UI and the required
   on-device IQ/profile files under `/system/x2d2-boot-v2`. Verify their hashes
   once at installation. Do not replace a library mapped by a running process.
2. Use the supplied self-authored `x2d2-*.rc` service definitions. In the original
   GUI service, select `LD_PRELOAD=/system/x2d2-boot-v2/entry.so` and
   `X2D2_UNIFIED_MODE=gui`, retaining other original properties. Explicitly disable
   the original capture/storage services from automatic class startup; they
   remain available for explicit fallback starts.
3. In the device's original `init.services.rc`, replace the capture dispatch with
   `start x2d2-direct-bootstrap`, and both explicit storage dispatches with
   `start x2d2-unified-storage`. Preserve hardware waits and all unrelated lines.
4. Restore `/system` read-only before arming. Validate a one-boot trial before
   creating the resident selector. Keep the original programs and prior startup
   route intact. Disabling the selector reverts to that route on the next boot;
   it is not a complete uninstall.

Startup definitions in the parent directory are the legacy fallback snapshot.
Its release inventory is not silently replaced by this supplemental startup
package. `resident.json` records this layer separately. Preserve original notices.
