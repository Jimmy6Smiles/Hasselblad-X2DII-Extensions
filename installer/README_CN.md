# X2D II 扩展管理器（离线基础版）

[English](README.md) | [简体中文](README_CN.md)

这里实现统一安装器的第一层安全边界：生成、校验 `.x2d2ext` 扩展包，并在电脑上模拟不可变版本、原子启用与失败回滚。**当前版本不会连接或修改相机。**

首个可完整构建的目标是“电子快门 AF-C”。像素超频需要先把运行时文件和构建规则完整整理进公开仓库，再接入同一个管理器。

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
python -m unittest discover -s installer\tests -v
```

校验器会拒绝固件不符、目录穿越、符号链接、重复路径、未登记文件、超大文件和哈希不匹配。`stage-camera` 只上传并校验不可变版本，不会启用扩展。正式启用采用原子状态切换；暂存失败不会覆盖此前启用的版本。

## 尚未实现

- 官方 `.cim` 导入（等待采用许可证边界清晰的接入方式）；
- Windows 图形界面与写入部署（命令行现已提供受限的只读 WinUSB 握手）；
- 相机端公共启动管理器；
- 真机安装、升级、卸载与恢复；
- 像素超频扩展包生成。
