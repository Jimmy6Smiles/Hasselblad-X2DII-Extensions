# Hasselblad X2D II 扩展

[English](README.md) | [简体中文](README_CN.md)

由 Jimmy6Smiles 维护的 Hasselblad X2D II 100C 独立实验性扩展。

**适配固件：1.3.16.2。本项目并非哈苏官方项目。**

## 扩展功能

| 扩展 | 状态 | 功能 |
| --- | --- | --- |
| [电子快门 AF-C](extensions/electronic-shutter-afc/README_CN.md) | 已通过实机验证 | 在保留原厂镜头与拍摄模式限制的前提下，让电子快门支持 AF-C。独立于像素位移。 |
| [像素位移](extensions/pixel-shift/README_CN.md) | 已通过实机验证 | 六帧四亿像素 RAW、可选 JPEG、相册登记、原片清理和辅助回放。 |

新增功能应作为 `extensions/` 下的同级目录；每项扩展自己的源码、固件版本、文档和发布包都保存在对应目录内。

统一安装器的首个离线基础版位于 [installer](installer/README_CN.md)：目前可以生成并校验本地 `.x2d2ext` 扩展包，以及测试原子启用和失败回滚；尚未接入相机通信。

```text
extensions/
├── electronic-shutter-afc/
│   ├── src/
│   ├── prebuilt/
│   └── dist/
└── pixel-shift/
    └── firmware/
        └── 1.3.16.2/
```

## 安全提示

这些扩展可能造成相机无响应、拍摄失败或数据丢失。请提前备份照片，不要将实验版本用于无法重拍的重要场景。任何固件固定地址或二进制文件都不能直接用于其他机型或固件版本。

本仓库不包含哈苏固件镜像、照片、设备凭据或厂商库。源码目录或发布压缩包不等于通用安装器；请遵守各扩展文档中列出的安装边界。

## 来源与许可

X2D II 实现来自本地研究快照，并参考 Hasselblad Feature Extensions / Hasselblad Enhancement Research 的处理思路。原有声明保留在 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。公开可读不代表未明确声明许可的文件被自动重新授权。
