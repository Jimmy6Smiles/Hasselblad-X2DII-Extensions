# Resident startup — no camera-test wait

## Current selected version (2026-10-09)

The user selected the previously tested no-camera-test-wait version as the
resident startup. The directory name is retained for compatibility. This
supersedes the historical one-boot status below.

- Batch early preparation, release GUI and dispatch capture, then prepare
  backend IQ/profile inputs.
- Wait for album readiness but not camera-test. Factory init still starts
  camera-test normally. Supervisor relaxation requires the exact DIRECT and
  no-camera-test-wait markers; capture readiness and recovery remain intact.
- No later UI timestamp instrumentation. RAW/JPEG, cleanup and zoom unchanged.
- `resident-entry.sh` runs this implementation every boot, without `.once`.

Build in order: `python build.py --installer-fallback --cc <NDK r27 clang>`,
`python3 test_prep.py` on Linux/WSL, then
`python build_nowait.py --cc <NDK r27 clang>`.

| Artifact | Device target |
| --- | --- |
| `build/boot-prep.so` | `/system/x2d2-fast-init-v1/boot-prep.so` |
| `build-nowait/unified-start.sh` | `/system/x2d2-nowait-v1/unified-start.sh` |
| `build-nowait/guard.so` | `/system/x2d2-nowait-v1/guard.so` |
| `build-nowait/x2d2-trial.rc` | `/system/etc/init/x2d2-trial.rc` |
| `resident-entry.sh` | `/system/x2d2-boot-v2/unified-start.sh` |

Requires the compatible existing resident bundle. Keep its normal GUI entry
and camera-gui.rc without diagnostic preloads. Back up, check idle state,
install atomically, and restore system read-only; never overwrite mapped
libraries. Existing enabled/disabled and pending-task controls remain in use.

Resident entry was installed and read back; first resident reboot is pending.
Earlier one-boot backend adoption was 3.23–3.56 seconds, not visible UI timing.
This local source update does not rebuild/publish the separate `.x2d2ext`
installer release; release tooling must include the mapping above.

## Historical initial test notes (not current installation status)

This isolated candidate batches boot filesystem work into two native helper calls.
The early phase creates runtime directories, copies the capture/storage preload
libraries, creates the capture constructor authorization and links GUI resources.
The late phase copies IQ/profile inputs and links worker executables, after GUI
release and capture dispatch but before the specialty backend starts.

The accepted unified-v2 resident source and release manifest are unchanged.
Build using `python build.py --cc <Android NDK r27 clang>`, then execute
`python3 test_prep.py` on Linux/WSL. Seven host cases cover phase ordering,
byte-preserving copies, missing inputs, duplicate initialization and symlink
rejection. Host tests do not establish device SELinux permissions or boot speed.

The installer testing session changed the disabled/pending branch to dispatch
the factory service and publish FACTORY, instead of invoking the legacy path.
After user coordination, `--installer-fallback` preserves that exact verified
base (SHA-256 92d53bd42ba1d872d3c40330746f8e69e235c3365af7f3c26176b312ad87a47c).

The candidate was installed for one boot only. The device helper probe passed
directory security labeling, a byte-identical library copy and link creation
in an isolated temporary directory; probe files were then removed. System was
restored read-only. No running services were replaced. Reboot timing, actual
startup domain behavior and functional acceptance remain pending. The next
subsequent boot uses the backed-up installer-compatible resident script.

The pre-install backend reported FAST_CAPTURE_GUARD_UNCONFIRMED while idle;
this predates the candidate and must be checked after reboot. No boot speedup
or successful image capture is claimed yet.
