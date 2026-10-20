# Hasselblad X2D II Extensions

English | [简体中文](README_CN.md)

Maintained by Jimmy6Smiles. This is a distribution-only repository; source development is private.
Standalone and installer-bundled MODs carry attribution and provenance signatures; see [verification notes](PROVENANCE.md). Installer executables are unchanged.
**Unofficial project. X2D II 100C firmware 1.3.16.2 only.**

## Downloads

- [Windows manager: 2026-10-18 AF-C first-install fix](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/download/mod-manager-2026.10.18-afc-fix-1/X2DII-Offline-Windows-20261018-afc-first-install-1.zip)
- [macOS manager: 2026-10-18 AF-C first-install fix](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/download/mod-manager-2026.10.18-afc-fix-1/X2DII-Offline-macOS-20261018-afc-first-install-1.zip)
- [Stable Pixel Shift 1.2.4-rc2](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-1.2.4-rc2)
- [Standalone electronic-shutter AF-C 1.0.0](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/download/mod-manager-2026.10.17-preview/Electronic-Shutter-AFC.x2d2ext)
- [All releases, historical versions and checksums](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases)

Download actual attachments under **Assets**. GitHub's automatic “Source code” archives contain distribution documentation, not an installer or feature implementation. Download the manager and MOD separately.

**1.2.4-rc2 remains stable. 1.2.5-rc1 has known issues and is not recommended.**
[1.2.5-rc2](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-1.2.5-rc2) is a troubleshooting candidate for retained pre-capture tasks, mode-not-ready errors or immediate countdown cancellation. It adds recovery handling and cancellation evidence; device acceptance is pending and the countdown issue is not confirmed fixed. Working stable installations need no update.

## Features

- Pixel Shift: six-frame 400 MP RAW, optional JPEG, album integration, source-frame cleanup and assisted playback.
- Electronic-shutter AF-C: available separately and already included in Pixel Shift. **The two packages conflict; install only one.**
- RAW, JPEG and RAW+JPEG supported; HEIF unsupported.

## Installation and use

1. Check model and firmware, back up photographs and maintain battery charge.
2. Fully extract the manager and launch the Windows EXE or Mac application. Formal signing/notarization is not complete; do not globally disable security protections.
3. Put the desired `.x2d2ext` in the adjacent `mods` folder, or select a mods directory in the GUI. Do not extract MOD files. Keep one version per feature.
4. Quit Phocus and other managers. Connect USB, select charging/Phocus tethering mode and return to live view. Retain the working Phocus driver on Windows.
5. Read camera status, select the feature and install. Follow manual reboot prompts and wait for verification. Do not repeatedly install or interrupt power during writes.
6. Use a tripod and static scene for Pixel Shift; movement between frames affects the result.

For uninstall, click once and follow reboot prompts until completion. Stopping a wait does not undo completed writes. On timeout or checksum failure, stop, reconnect, read status and export diagnostics; do not force overwrites or remove recovery backups. Read candidate instructions before upgrading and use the matching old package to uninstall an old version. Updating the manager does not require reinstalling a working MOD.

Individual users have verified Windows/macOS operation, including installation on Mac followed by uninstallation on Windows. This does not cover every computer, camera or storage configuration. The manager does not automatically capture, reboot or upload diagnostics. Review private information before sharing diagnostics.

## Safety and notices

Experimental extensions may cause unresponsiveness, failed captures or data loss. Do not use for irreplaceable work. Do not upload photographs, full firmware, credentials or private diagnostics.
Changing repository visibility does not revoke previously granted licenses or recall existing clones and forks. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
