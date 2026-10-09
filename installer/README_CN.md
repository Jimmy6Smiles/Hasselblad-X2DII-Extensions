# X2D II 扩展管理器（开发基础版）

[English](README.md) | [简体中文](README_CN.md)

这里实现统一安装器的安全边界：生成、校验 `.x2d2ext` 扩展包，在电脑上模拟不可变版本、原子启用与失败回滚，并通过固定固件版本的 WinUSB 协议探测相机、暂存已校验版本。暂存不会启用扩展。

当前可构建目标包括“电子快门 AF-C”和已验证的像素超频常驻快照。公共启动管理器、卸载和恢复链完成前，暂存与启用仍保持分离。

## 构建本地 AF-C 扩展包

需要从 X2D II 1.3.16.2 原厂固件提取、且未经修改的 `camera-service` 与 `camera-gui`。生成包只保存本地编译模块和两段定长 GUI 补丁，不再复制一份 64 MB GUI。文件已被 Git 忽略；在厘清原厂派生补丁的许可边界前请勿分发。

```powershell
python -m installer.build_afc_bundle `
  --camera-service D:\path\to\system\bin\camera-service `
  --camera-gui D:\path\to\system\bin\camera-gui `
  --ndk D:\path\to\android-ndk-r27 `
  --out .local-only\electronic-shutter-afc-1.0.0.x2d2ext
```

## 校验与本地安装模拟

```powershell
python -m installer.manager verify .local-only\electronic-shutter-afc-1.0.0.x2d2ext
python -m installer.manager plan .local-only\electronic-shutter-afc-1.0.0.x2d2ext
python -m installer.manager simulate-install .local-only\electronic-shutter-afc-1.0.0.x2d2ext .local-only\simulated-camera
python -m installer.manager probe-camera
python -m installer.manager stage-camera .local-only\electronic-shutter-afc-1.0.0.x2d2ext
python -m installer.manager stage-camera .local-only\pixel-shift-400mp-1.0.0.x2d2ext --fast
python -m unittest discover -s installer\tests -v
```

校验器会拒绝固件不符、目录穿越、符号链接、重复路径、未登记文件、超大文件和哈希不匹配。`stage-camera` 只上传并校验不可变版本，不会启用扩展。`--fast` 仍通过 WinUSB 发控制命令，只把文件内容经 USB RNDIS 点对点链路传输；相机会逐文件校验 SHA-256 后再提交。

## 构建已验证的像素超频扩展包

常驻负载导出和 GUI 启动库属于本地构建输入，本仓库不直接分发。

```powershell
python -m installer.build_pixel_shift_bundle `
  --payload D:\path\to\verified-resident-export `
  --gui-entry D:\path\to\libx2d2-gui-early.so `
  --out .local-only\pixel-shift-400mp-1.0.0.x2d2ext
```

## 尚未实现

- 官方 `.cim` 导入（等待采用许可证边界清晰的接入方式）；
- Windows 图形界面；
- 相机端公共启动管理器；
- 真机安装、升级、卸载与恢复；
- 已暂存版本的正式启用。
