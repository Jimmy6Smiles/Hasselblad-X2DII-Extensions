# Hasselblad X2D II 扩展

[English](README.md) | 简体中文

由 Jimmy6Smiles 维护。本仓库仅用于发布说明和下载，源码在私有仓库维护。
**非哈苏官方项目；仅适配 X2D II 100C、固件 1.3.16.2。**

## 下载

- [Windows 管理器：2026-10-18 AF-C 首次安装修复版](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/download/mod-manager-2026.10.18-afc-fix-1/X2DII-Offline-Windows-20261018-afc-first-install-1.zip)
- [macOS 管理器：2026-10-18 AF-C 首次安装修复版](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/download/mod-manager-2026.10.18-afc-fix-1/X2DII-Offline-macOS-20261018-afc-first-install-1.zip)
- [像素超频稳定版 1.2.4-rc2](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-1.2.4-rc2)
- [独立电子快门 AF-C 1.0.0](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/download/mod-manager-2026.10.17-preview/Electronic-Shutter-AFC.x2d2ext)
- [全部 Release、历史版本与校验值](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases)

在 Release 的 **Assets** 下载实际附件。GitHub 自动生成的 “Source code” ZIP/TAR 仅含本发布库说明，不是安装器，也不包含功能源码。管理器与 MOD 分开下载。

**稳定版仍为 1.2.4-rc2。1.2.5-rc1 存在已知问题，不建议使用。**
[1.2.5-rc2](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-1.2.5-rc2) 仅供遇到未拍摄任务残留、尚未接入或倒计时立即退出的用户协助排查。它增加恢复处理及取消原因记录，尚未完成实机验收，不保证解决倒计时退出；稳定版正常使用者无需升级。

## 功能

- 像素超频：六帧四亿像素 RAW、可选 JPEG、相册登记、原片清理和辅助回放。
- 电子快门 AF-C：独立功能包。像素超频已包含此功能，**两包互斥，只安装一个**。
- 支持 RAW、JPEG、RAW＋JPEG，不支持 HEIF。

## 安装与使用

1. 核对机型和固件，备份照片，保持充足电量。
2. 完整解压管理器。Windows 打开 EXE；Mac 打开应用。程序未完成正式签名／公证，不要全局关闭安全防护。
3. 将需要的 `.x2d2ext` 放入程序旁的 `mods` 文件夹，或在界面选择 mods 目录。不要解压 MOD；同一功能只保留一个版本。
4. 退出 Phocus 及其他管理器，用 USB 连接相机，选择仅充电／Phocus 联机模式并回到取景。Windows 保留正常工作的 Phocus 驱动。
5. 读取相机状态，选择功能并安装。按明确提示手动关机再开机，等待管理器继续验收；不要重复安装或写入中断电。
6. 像素超频使用三脚架和静止场景，六帧间移动会影响成片。

卸载只需点击一次并按提示重启、等待流程完成。停止等待不撤销已完成写入。通信超时或校验失败时停止，重新连接读取状态并导出诊断，不要强行覆盖或删除恢复备份。升级候选版前阅读该版本说明，旧版卸载需使用对应旧包。更换管理器不必重装正常工作的 MOD。

已收到 Windows/macOS 可用及 Mac 安装后 Windows 卸载的个人设备验证反馈，不代表所有电脑、相机或存储组合均已覆盖。程序不自动拍摄、重启或上传诊断；分享诊断前请检查隐私。

## 安全及许可

实验性扩展可能造成相机无响应、拍摄失败或数据丢失，不用于无法重拍的重要场景。不要上传照片、完整固件、凭据或私人诊断。
本次调整只改变公开仓库的源码可见方式，不撤销已授予的许可，也不能收回已被他人克隆或 Fork 的内容。第三方声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
