#!/system/bin/sh
# Bootstrap failure fallback. Never interrupt an exposure or active storage write.
set -eu
T=/system/bin/toybox
D=/dev/x2d2-unified-boot
mode=
if [ -f "$D/mode" ]; then read mode < "$D/mode"; fi
if [ "$mode" = LEGACY ]; then exec /system/bin/sh /data/x2d2-full-v1/direct-recover.sh; fi
[ ! -f /dev/x2d2-direct-boot/adopted ] || exit 0
[ -z "$(/system/bin/getprop sys.powerctl)" ] || exit 0
# Refuse overlapping fallback while either factory API cannot confirm idle.
attempt=0
while :; do
 exposure=$($T timeout -k 1 2 /system/bin/odindb-send -s camera -p exposure_status) || exposure=
 pending=$($T timeout -k 1 2 /system/bin/odindb-send -s storage -p storage_processing_counter) || pending=
 if [ "$exposure" = 'exposure_status = E_ExposureStatus_None(0)' ] && [ "$pending" = 'storage_processing_counter = 0' ]; then break; fi
 attempt=$((attempt+1)); [ "$attempt" -lt 30 ] || exit 1
 [ -z "$(/system/bin/getprop sys.powerctl)" ] || exit 0
 $T sleep 0.2
done
printf 'FAILED\n' > "$D/mode"
for service in camera-gui camera-test x2d2-capture-trial; do
 /system/bin/setprop ctl.stop "$service"
 attempt=0
 while [ "$(/system/bin/getprop init.svc.$service)" = running ]; do
  attempt=$((attempt+1)); [ "$attempt" -lt 100 ]; $T sleep 0.1
 done
done
# Leave a healthy storage service alone; capture and GUI are restored independently.
/system/bin/setprop ctl.start camera-service
/system/bin/setprop ctl.start camera-test
/system/bin/setprop ctl.start camera-gui
