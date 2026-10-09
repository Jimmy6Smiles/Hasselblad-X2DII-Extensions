# X2D II 电子快门 AF-C

[English](README.md) | [简体中文](README_CN.md)

这是一个与像素位移完全独立的 X2D II 100C 扩展，使 AF-C 可在电子快门下使用。

## 适配范围

- 机型：Hasselblad X2D II 100C
- 固件：**1.3.16.2**
- 已验证：电子快门、单张驱动模式下可在机身选择 AF-C，并能连续跟踪
- 仍保留：镜头固件能力检查，以及自拍、间隔、曝光包围、景深包围等原厂限制

不要用于第一代 X2D、其他机型或其他固件。代码和 UI 资源位置均为固件固定地址，构建器会先检查完整文件摘要和关键指令，任何不匹配都会拒绝生成。

## 与像素位移的关系

没有依赖关系：

- 不包含像素位移采集、RAW 合成、相册或回放代码；
- 不引用 `/data/x2d2-full-v1`、像素位移服务或其启动脚本；
- 后端是独立的 `afc-electronic.so`；
- UI 适配直接从原厂 1.3.16.2 `camera-gui` 生成。

如果相机已经修改过 `camera-gui` 或 `camera-service` 启动项，不要直接覆盖。应从原厂固件重新构建，并由安装器合并现有改动；本包不会假装两个完整 GUI 文件可以安全互相覆盖。

## 构建

依赖 Python 3、`pyelftools` 和 Android NDK r27。原厂 `camera-service`、`camera-gui` 需由使用者从自己合法取得的 1.3.16.2 固件中提取，不随仓库或发布包提供。

```powershell
python -m pip install pyelftools
python build.py `
  --camera-service D:\path\to\system\bin\camera-service `
  --camera-gui D:\path\to\system\bin\camera-gui `
  --ndk D:\path\to\android-ndk-r27 `
  --out output
```

输出：

- `payload/afc-electronic.so`：只加载到 `camera-service` 的 ARM64 后端；
- `payload/camera-gui`：只包含电子快门 AF-C 菜单适配的完整 GUI；
- `payload/camera-service.env`：启动时所需的 `LD_PRELOAD` 值；
- `manifest.json`：输入、输出摘要及两个 UI 资源的修改范围。

仓库中的 `prebuilt/1.3.16.2/afc-electronic.so` 只含本项目自有代码；完整原厂 GUI 必须在本地生成。

## 安装边界

这不是 CIM，也不包含通用 USB 维护驱动或绕过相机权限的工具。安装程序至少必须完成以下操作：

1. 再次核对机型、固件和原厂文件摘要；
2. 备份原 `camera-gui` 与 `camera-service.rc`；
3. 安装本地生成的 `camera-gui` 与 `afc-electronic.so`；
4. 仅给 `camera-service` 增加 `LD_PRELOAD=/system/lib64/libx2d2-afc-electronic.so`；
5. 恢复系统分区只读并重启；
6. 检查 `/tmp/x2d2-afc-electronic.json` 的 `ready:true`，再验证原厂 AF-S、MF 和机械快门。

不要把像素位移启动项作为本功能的前提。若安装器不能原子备份、回读校验及失败恢复，请不要部署。

## 实现

后端仅做两项固件固定修改：保留 AF-C capability bit，并跳过 `updateFocusMode()` 中电子快门专属的 AF-C 回退分支。其余镜头与驱动模式判断仍由原厂逻辑执行。UI 同步开放控制屏和实时取景中的 AF-C 选项，并移除电子快门专属阻止提示。

这是非官方实验功能，可能造成相机无响应、失焦或无法拍摄。不要用于不可重拍的重要场景。
