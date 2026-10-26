# Hasselblad X2D II 扩展

[English](README.md) | 简体中文

由 Jimmy6Smiles 维护；本仓库用于发布说明和下载，源码在私有库维护。非哈苏官方项目。

**最新公开测试配套：X2D II 100C / 固件 1.3.18.1 / 公共运行时 1.2.31。不要与旧 1.3.16.2 包混用。**

## 安装前请先读

目前尚未完全解决不同用户安装时出现的断线、失败和恢复问题。作者最近空闲时间有限，无法为每位用户单独远程排障。建议有能力借助 AI 阅读日志、核对状态和处理恢复的用户先尝试；怕麻烦、不想折腾的用户可以等待。AI 不能保证操作正确，不要让它跳过校验或盲目删除文件。

**更新相机原厂固件前，必须先卸载旧 MOD 和旧公共接口，重启验收，再检查 `/data` 与 `/system` 的旧组件、启动项和未完成事务。** 显示“未安装”或菜单消失不代表已清理干净，刷固件也不能代替卸载。检查失败或残留归属不明时先处理，不要继续刷机。

完整流程：[固件升级、残留核对和安装说明](INSTALL_UPGRADE_CN.md)。不删除照片，未知文件不能按名称批量清理。

## 最新测试版下载

| 下载 | 版本 |
|---|---|
| [Windows 安装器 + 公共运行时](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.31-preview-20261026) | 1.2.31 |
| [公共运行时身份与说明](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/common-runtime-1.2.31) | 1.2.31 |
| [机内滤镜 45 款](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/in-camera-filters-0.1.1-rc5-fw-1.3.18.1-runtime-1.2.31) | 0.1.1-rc5 |
| [像素超频 400 MP（含 AF-C）](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-400mp-1.2.5-rc4-fw-1.3.18.1-runtime-1.2.31) | 1.2.5-rc4 |
| [多重曝光](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/multiple-exposure-0.1.2-rc34-fw-1.3.18.1-runtime-1.2.31) | 0.1.2-rc34 |
| [永不息屏](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/never-sleep-1.0.1-fw-1.3.18.1-runtime-1.2.31) | 1.0.1 |

Windows ZIP 已内附这四个 MOD，也可从对应 Release 单独下载。公共接口内置于安装器，由“检测公共接口”及配套事务管理，不作为独立 MOD 安装。**同版本 macOS 包尚未构建，不要用历史 Mac 管理器安装这套新包。**

在 Release 的 Assets 下载附件并核对 SHA256SUMS.txt。GitHub 自动生成的 Source code ZIP/TAR 仅包含发布说明，不是安装器。旧 Release 保留用于对应旧环境恢复；[历史固件 1.3.16.2 资料](docs/HISTORICAL_1.3.16.2_CN.md)。

## 功能及署名

实时取景时，长按 ⭕ 可打开滤镜快捷入口。使用多重曝光时，请先选好滤镜，再进入多重曝光模式；进入多重曝光后不能更改滤镜。

- 机内滤镜 45 款：作者 [FarSails777](https://github.com/FarSails777)。本仓库负责配套分发，不能将其原创署名归于分发者。
- 像素超频：六帧四亿 RAW／JPEG、辅助回放，包含 AF-C；不要重复安装旧独立 AF-C 包。四亿不支持 HEIF。
- 多重曝光：拍摄合成、取景叠加和结果保存；rc34 延迟建立任务目录，并在成功后后台清理中间文件。以界面支持选项及已验证场景为准。
- 永不息屏：提供屏幕超时“永不息屏”选项，不等于取消全部电源管理。

管理器、公共运行时和其他 MOD 由 Jimmy6Smiles 维护。保留第三方权利与署名，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 测试范围

离线测试和开发者单机实测不代表所有环境均兼容。请先备份照片，不用于无法重拍的重要场景；分享诊断前检查隐私。项目不自动上传诊断，也不自动拍照或重启。
