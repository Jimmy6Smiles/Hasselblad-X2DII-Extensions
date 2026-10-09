#!/system/bin/sh
# 自写私有体验版启动器；入口须由安装器备份后明确选择，不默认覆盖旧放大启动。
set -eu
umask 077
B=/data/x2d2-full-v1
R=/dev/x2d2-integrated-v1
S=/dev/x2d2-shutter-v1
U=/dev/x2d2-menu-session-v1
T=/system/bin/toybox
[ -f "$B/enabled" ] && [ ! -e "$B/disabled" ] && [ -f "$B/boot.pending" ]
cd "$B/payload"
$T sha256sum -c manifest.sha256 >/dev/null
hash=$($T sha256sum /system/bin/camera-gui)
[ "${hash%% *}" = b1b643cb36176cd5a49129dd9bb2be480aa045a96ed1c35c30a779ab5af0801b ]
hash=$($T sha256sum /system/bin/camera-service)
[ "${hash%% *}" = 51b9e02f8bfebf388be8dfa163c8e512bee19aeb8ae37a6712727ccc6f26a52d ]
hash=$($T sha256sum /system/lib64/librcam.so)
[ "${hash%% *}" = 3dd5b37b3db18b3e6b54271e1501b4dd337e101c06cdd386a896b1547b662f66 ]
hash=$($T sha256sum /system/lib64/libdcam_fcali.so)
[ "${hash%% *}" = dd28fa5829aa3a2b118ddefd14c2283845b9993784a28d954d81d2ee7bd3af05 ]
attempt=0
while [ "$(/system/bin/getprop init.svc.camera-gui)" != running ] || [ "$(/system/bin/getprop init.svc.camera-test)" != running ]; do
 attempt=$((attempt+1)); [ "$attempt" -lt 80 ]; $T sleep 0.1
done
# 相册未实际就绪，不停止任何拍摄服务。
attempt=0
while [ ! -f /dev/x2d2-album-refresh-v1/ready ] || [ "$(/system/bin/getprop init.svc.x2d2-storage-trial)" != running ]; do
 attempt=$((attempt+1)); [ "$attempt" -lt 100 ]; $T sleep 0.1
done
$T mkdir "$R" "$S" "$U"
$T chcon u:object_r:sel_device:s0 "$R" "$S" "$U"
$T mkdir "$R/jobs" "$R/cache" "$R/scratch"
for name in integrated-job integration-service native-auto6 worker raw-pack full-jpeg zoom-server overlap-prepare overlap-container readiness-check reboot-reconcile native-first-frame-scoped native-job-cache native-job-render native-preview-commit native-stream-render jpeg-stream-join first-frame-jpeg jpeg-flow-pack; do
 $T cp "$B/payload/$name" "$R/$name"
 $T chmod 700 "$R/$name"
done
$T cp "$B/payload/shutter.so" "$S/shutter.so"
# Native job profile is private; all unmarked original requests stay original.
NATIVE=/dev/x2d2-pregdc-trial
$T mkdir "$NATIVE"
$T chcon u:object_r:sel_device:s0 "$NATIVE"
hash=$($T sha256sum /system/etc/iq/hb722_config.bin)
[ "${hash%% *}" = ce58c7e668fd41af0547e0df7d8545159a3ab2619ad4eabb8931544dadb81436 ]
$T cp /system/etc/iq/hb722_config.bin "$NATIVE/diagnostic-iq.bin"
$T cp "$B/payload/native-color.conf" "$NATIVE/candidate.conf"
$T cp "$B/payload/native-color.sp" "$NATIVE/candidate.sp"
printf 'PREGDC_JOB_SCOPED_NATIVE_COLOR_V1\n' > "$NATIVE/authorized.once"

# 仅在 RAM 中应用全部已校验定长资源补丁。
$T cp /system/bin/camera-gui "$R/gui"
$T dd if="$B/payload/ui/menu.patch" of="$R/gui" bs=1 seek=35484537 conv=notrunc 2>/dev/null
$T dd if="$B/payload/ui/zoom.patch" of="$R/gui" bs=1 seek=35427246 conv=notrunc 2>/dev/null
$T dd if="$B/payload/ui/liveview.patch" of="$R/gui" bs=1 seek=35168548 conv=notrunc 2>/dev/null
$T dd if="$B/payload/ui/capture-hold-0.patch" of="$R/gui" bs=1 seek=35032266 conv=notrunc 2>/dev/null
$T dd if="$B/payload/ui/capture-hold-1.patch" of="$R/gui" bs=1 seek=35022891 conv=notrunc 2>/dev/null
$T dd if="$B/payload/ui/capture-hold-2.patch" of="$R/gui" bs=1 seek=35025297 conv=notrunc 2>/dev/null
$T dd if="$B/payload/ui/capture-hold-3.patch" of="$R/gui" bs=1 seek=35087820 conv=notrunc 2>/dev/null
for name in PixelShiftBracketing.qml PixelShiftBusyLayer.qml PixelShiftDriveBadge.qml PixelShiftDriveGrid.qml PixelShiftDrivePopup.qml PixelShiftFramedImage.qml PixelShiftFramedItem.qml PixelShiftLiveBadge.qml PixelShiftModeController.qml PixelShiftSelector.qml PixelShiftSettings.qml PixelShiftState.qml PixelShiftStateAccess.qml PixelShiftTransport.qml pixel-shift.svg qmldir; do
 $T cp "$B/payload/ui/$name" "$U/$name"
done
$T chmod 700 "$R/gui"
# 对应 manifest 的重建摘要由打包器写入；不以仅存在性验收 GUI。
hash=$($T sha256sum "$R/gui")
[ "${hash%% *}" = fa2fbdc89648909f29d6a55bf0d2a40fb3cfdf187ac94c1bf615add03de347dd ]
# 每块实际挂载卷只建私有中间目录，不改变相机默认存储设置。
for volume in ssd cfe; do
 if $T grep -q " /mnt/media_rw/$volume " /proc/mounts; then
  [ -d "/mnt/media_rw/$volume/.x2d2-pixelshift" ] || $T mkdir "/mnt/media_rw/$volume/.x2d2-pixelshift"
 fi
done
# boot.pending 已由首次 GUI 入口先行落盘。
printf 'AUTHORIZED_RETAIN_INPUTS_INTEGRATION\n' > "$S/integration.once"
printf 'AUTHORIZED_NO_CAPTURE\n' > "$S/load.once"
$T sync
/system/bin/setprop ctl.stop x2d2-capture-trial
attempt=0
while [ "$(/system/bin/getprop init.svc.x2d2-capture-trial)" != stopped ]; do
 attempt=$((attempt+1)); [ "$attempt" -lt 5 ]; $T sleep 1
done
/system/bin/setprop ctl.start x2d2-trial-guard
# 不创建 accepted、不清除 boot.pending；首次人工验收后才由安装器确认常驻。
