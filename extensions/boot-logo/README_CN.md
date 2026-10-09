# 开机 Logo

这里保存 X2D II 100C 固件固定的开机 Logo 研究。`build.py` 可将 1024×768
图片转换成 1.3.16.2 固件使用的 `format:2` NV12 容器；脚本本身不会连接相机
或覆盖文件。

```powershell
python extensions\boot-logo\build.py input.png output-logo.bin
```

后屏资源位于 `/vendor/logo.bin`。测试替换前必须备份并校验原文件。肩屏是独立
面板，需要单独验证，不能直接假定与后屏共用资源。
