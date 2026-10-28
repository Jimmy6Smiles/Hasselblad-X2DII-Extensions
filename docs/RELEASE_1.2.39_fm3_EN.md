# 1.2.39+fm.3: matched Windows / macOS release

For X2D II 100C, OEM firmware **1.3.18.1**. Only the in-camera filter MOD changes in this release; the installer and shared runtime also change. The revision is **1.2.39+fm.3**, not 1.2.40.

## Downloads and MOD versions

- Windows: `X2DII-Offline-Windows-Runtime-Preview-1239-fm3-Test2.zip`, including automatic migration.
- Apple Silicon macOS / arm64: `X2DII-1.2.39-macOS-arm64-Test17-Full.zip`, Test17/build21, distributed byte-for-byte as supplied. No Intel Mac build is provided.
- Both full bundles include the runtime, 45-filter library and four matched MODs. Keep the extracted bundle intact, including the `mods` folder beside the Mac App.

| MOD | Version | Change |
|---|---|---|
| 45 in-camera filters | 0.1.2-rc1 | Updated from0.1.1-rc5 |
| Pixel Shift 400 MP, including AF-C | 1.2.5-rc12 | Byte-identical to the original1.2.39 release; no separate reinstall needed |
| Multiple Exposure | 0.1.2-rc42 | Byte-identical; no separate reinstall needed |
| Never Sleep | 1.0.1 | Byte-identical; no separate reinstall needed |

## Filter changes

Select which filters to install, physically delete deselected resources to reclaim space, and reinstall them later. Adds HDR/image-postprocessing guidance, fixes flickering deletion controls, and improves touch/joystick guidance and long-press confirmation. Turn off HDR/image postprocessing before using filters.

During live view, **press and hold ⭕** for the shortcut. Select the filter before entering Multiple Exposure; it cannot be changed while in Multiple Exposure.

X2D2 filter author: [FarSails777](https://github.com/FarSails777). Manager, shared runtime, other MODs and distribution maintained by Jimmy6Smiles. Third-party and OEM rights are preserved.

## Installer and runtime changes

The distribution identity is **1.2.39+fm.3**; the wire version remains1.2.39. Matching version text alone does not establish compatibility. Camera payloads are the exact fm.3 set; the other three MODs were not rebuilt.

Both platforms inherit fixes for stale uninstall-cache reports and interrupted uploads after the installed MOD combination changes. Unknown files, mismatched identities and unfinished transactions still stop the operation; this does not fix every disconnect.

**Windows Test2:** original Windows1.2.39 users do not need to uninstall first. Close the old manager, open this bundle, read camera status and select the paired update/resume button. Reboot manually when prompted, return to live view, and continue acceptance. The installer handles two conflicting paths, keeps backups on the PC and preserves installed MODs, settings and photographs without adding absent MODs. Resume the same interrupted transaction instead of reinstalling. Only exact approved baselines are admitted.

**Mac Test17 has a different migration scope:** its fm.3 camera payloads match Windows, but it does NOT include the Windows Test2 migration from original Windows1.2.39. It contains reviewed original1.2.35/fm.2 baselines and the fm.3 set. Use Windows Test2 first for original-Windows1.2.39 migration; do not force an overwrite using the Mac bundle. The App is ad-hoc signed and not notarized. Its legacy restore helper supports firmware1.3.16.2 ONLY, never1.3.18.1.

## Validation and important notes

Windows: 205 offline tests passed, including16 MOD subsets, interrupted/lost-reply publication, atomic replacement and cleanup boundaries. EXE startup and1017 embedded resources were checked. **Automatic Windows migration still needs hardware acceptance; no camera was accessed during this build.**

Mac: the build author reports156 offline tests plus6 subtests and Test17 version-label, frozen-resource, signature and extraction checks. These are supplied build records, not new hardware acceptance performed for this publication. Neither platform is claimed compatible with every computer.

Disconnects, installation failures and recovery issues across users' computers are not fully resolved. The author currently has limited spare time and cannot provide individual remote troubleshooting for every user. Early testing is recommended for users who can use AI tools to understand logs and recovery steps; users who prefer a trouble-free experience should wait.

**No-uninstall migration applies only to this supported MOD update. Before updating OEM camera firmware, uninstall all MODs and the shared runtime, reboot and verify, and check both `/data` and `/system` for old components, startup entries and unfinished transactions.** Preserve photographs, unknown files and PC backups. Quit desktop Phocus; reboot manually when instructed. No automatic capture or reboot.

Download complete bundles from Assets and check SHA256SUMS.txt. GitHub-generated Source code archives contain public documentation, not the installer. This is a normal Release for discoverability, not a claim of completed hardware acceptance. Withdrawn1.2.38 and Mac Test16 releases remain withdrawn.
