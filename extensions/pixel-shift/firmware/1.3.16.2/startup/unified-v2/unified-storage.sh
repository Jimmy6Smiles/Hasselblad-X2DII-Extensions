#!/system/bin/sh
set -eu
T=/system/bin/toybox
D=/dev/x2d2-unified-boot
attempt=0
while [ ! -f "$D/mode" ]; do
 attempt=$((attempt+1)); [ "$attempt" -lt 100 ]; $T sleep 0.05
done
read mode < "$D/mode"
if [ "$mode" = DIRECT ]; then
 printf 'AUTHORIZED_STORAGE_INIT_NO_CAPTURE\n' > /dev/x2d2-album-refresh-v1/load.once
 /system/bin/setprop ctl.start x2d2-storage-trial
 /system/bin/setprop ctl.start x2d2-storage-guard
else
 /system/bin/setprop ctl.start camera-storage
fi
