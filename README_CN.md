# Hasselblad X2D II 扩展

[English](README.md) | 简体中文

由 Jimmy6Smiles 维护；本仓库用于发布说明和下载。[像素超频源码](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-400MP-Source)单独公开，安装器源码在私有库维护。非哈苏官方项目。

**当前配套：X2D II 100C / 固件 1.3.18.1 / Windows 管理器与公共运行时 1.2.42 / 像素超频 1.2.5-rc13。不要与旧运行时或旧固件包混用。**

## 本次更新

本次修正新版公共接口下四亿 JPEG 显影／校准会话的路径兼容问题，并更新完整启动与采集准入。四亿更新为 **1.2.5-rc13**；机内滤镜0.1.2-rc2、多重曝光0.1.2-rc42、永不息屏1.0.1保留原载荷。

[完整更新、升级范围与验证说明](docs/RELEASE_1.2.42_CN.md)。只对精确匹配的正式1.2.41配套提供本轮自动迁移；按提示手动重启后继续验收。**RC13必须与1.2.42配套安装，不能单独覆盖到1.2.41或更旧公共接口。** 本轮未发布新版Mac包；历史Mac Test17属于旧fm.3环境。

## 安装前请先读

目前尚未完全解决不同用户安装时出现的断线、失败和恢复问题。作者最近空闲时间有限，无法为每位用户单独远程排障。建议有能力借助 AI 阅读日志、核对状态和处理恢复的用户先尝试；怕麻烦、不想折腾的用户可以等待。AI 不能保证操作正确，不要让它跳过校验或盲目删除文件。

**更新相机原厂固件前，必须先卸载旧 MOD 和旧公共接口，重启验收，再检查 `/data` 与 `/system` 的旧组件、启动项和未完成事务。** 显示“未安装”或菜单消失不代表已清理干净，刷固件也不能代替卸载。检查失败或残留归属不明时先处理，不要继续刷机。

完整流程：[固件升级、残留核对和安装说明](INSTALL_UPGRADE_CN.md)。不删除照片，未知文件不能按名称批量清理。

## 最新测试版下载

| 下载 | 版本 |
|---|---|
| [Windows 安装器 + 公共运行时 + 四个配套MOD](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.42-20261107) | 1.2.42 |
| [像素超频 400 MP（含 AF-C）](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/pixel-shift-400mp-1.2.5-rc13-fw-1.3.18.1-runtime-1.2.42) | 1.2.5-rc13；须配套1.2.42 |
| [机内滤镜 45 款（完整包内）](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.42-20261107) | 0.1.2-rc2；载荷不变 |
| [多重曝光（完整包内）](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.42-20261107) | 0.1.2-rc42；载荷不变 |
| [永不息屏（完整包内）](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.42-20261107) | 1.0.1；载荷不变 |
| [历史Mac Apple Silicon Test17](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-Extensions/releases/tag/mod-manager-runtime-1.2.39-fm.3-20261028) | 旧1.2.39+fm.3；不适用于本轮1.2.42／RC13 |

Windows完整包内附四个MOD；公共接口由安装器管理，不作为独立MOD。原生组件的固定存储ABI目录仍可含`1.2.39`，当前逻辑版本是1.2.42；不要自行替换路径中的数字。

在Release的Assets下载附件并核对SHA256SUMS.txt；GitHub自动生成的Source code不是安装器。旧版保留供对应环境恢复，已撤回的版本不重新发布。

## 功能及署名

实时取景时，长按 ⭕ 可打开滤镜快捷入口。使用多重曝光时，请先选好滤镜，再进入多重曝光模式；进入多重曝光后不能更改滤镜。

- 机内滤镜 45 款：作者 [FarSails777](https://github.com/FarSails777)。本仓库负责配套分发，不能将其原创署名归于分发者。
- 像素超频：六帧四亿 RAW／JPEG、辅助回放，包含 AF-C；不要重复安装旧独立 AF-C 包。四亿不支持 HEIF。
- 多重曝光：2–9 张；平均／叠加／亮部／暗部；累计取景蒙版与计数；所有图像／仅限结果；拍后退出／保持。支持 RAW、RAW＋JPEG、RAW＋HEIF、仅 HEIF，最终 HEIF 为10位。仅 RAW 使用内部 R＋J 兼容采集并自动清理内部 JPEG；仅 JPEG 暂不列为支持。零帧不落盘，成功后后台清理中间文件。
- 永不息屏：提供屏幕超时“永不息屏”选项，不等于取消全部电源管理。

管理器、公共运行时和其他 MOD 由 Jimmy6Smiles 维护。保留第三方权利与署名，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 测试范围

离线测试和开发者单机实测不代表所有环境均兼容。请先备份照片，不用于无法重拍的重要场景；分享诊断前检查隐私。项目不自动上传诊断，也不自动拍照或重启。
