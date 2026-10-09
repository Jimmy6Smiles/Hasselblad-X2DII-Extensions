# Boot Logo

Firmware-specific X2D II 100C boot-logo research. `build.py` converts a
1024x768 image to the `format:2` NV12 container used by firmware 1.3.16.2.
It does not install or overwrite camera files.

```powershell
python extensions\boot-logo\build.py input.png output-logo.bin
```

The rear boot logo is `/vendor/logo.bin`. Back up and verify the original file
before testing a replacement. The top display is a separate panel and must be
verified independently; do not assume the rear resource controls it.
