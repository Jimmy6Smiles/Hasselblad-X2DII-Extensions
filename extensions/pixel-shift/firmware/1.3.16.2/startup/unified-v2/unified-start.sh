#!/system/bin/sh
# Resident integrated startup, with optional one-boot trial authorization.
# Never issues an exposure or deletes an image.
set -eu
T=/system/bin/toybox
B=/data/x2d2-full-v1
D=/dev/x2d2-unified-boot
P=/system/x2d2-boot-v2
R=/dev/x2d2-integrated-v1
S=/dev/x2d2-shutter-v1
N=/dev/x2d2-pregdc-trial
A=/dev/x2d2-album-refresh-v1
umask 077
$T mkdir "$D"
$T chcon u:object_r:sel_device:s0 "$D"
mark() { read elapsed rest < /proc/uptime; printf '%s %s\n' "$elapsed" "$1" >> "$B/unified-timing.log"; }
: > "$B/unified-timing.log"
mark BEGIN
trial=0
if [ -f "$B/unified.enabled" ]; then trial=1; fi
if [ -f "$B/unified.once" ]; then
 $T mv "$B/unified.once" "$B/unified.consumed"
 $T sync
 trial=1
fi
if [ "$trial" -eq 0 ] || [ ! -f "$B/enabled" ] || [ -e "$B/disabled" ] || [ -e /data/x2d2-integrated-v1/pending ]; then
 printf 'LEGACY\n' > "$D/mode"
 exec /system/bin/sh "$B/direct-start.sh"
fi
# Publish DIRECT only after minimal paths exist; GUI does not wait for workers.
trap 'rc=$?; if [ "$rc" -ne 0 ]; then printf "FAILED\n" > "$D/mode"; fi' EXIT
$T mkdir "$R" "$S" "$N" "$A" /dev/x2d2-menu-session-v1 /dev/x2d2-direct-boot /dev/x2d2-storage-prepare-once
$T chcon u:object_r:sel_device:s0 "$R" "$S" "$N" "$A" /dev/x2d2-menu-session-v1 /dev/x2d2-direct-boot
$T mkdir "$R/jobs" "$R/cache" "$R/scratch"
# Small libraries retain exact mapped paths required by the existing runtime ABI.
$T cp "$P/shutter.so" "$S/shutter.so"
$T cp "$P/album-observer.so" "$A/album-observer.so"
$T cp "$P/diagnostic-iq.bin" "$N/diagnostic-iq.bin"
$T cp "$P/native-color.conf" "$N/candidate.conf"
$T cp "$P/native-color.sp" "$N/candidate.sp"
printf 'PREGDC_JOB_SCOPED_NATIVE_COLOR_V1\n' > "$N/authorized.once"
for source in "$P"/ui/*; do
 $T ln -s "$source" "/dev/x2d2-menu-session-v1/${source##*/}"
done
printf 'DIRECT\n' > /dev/x2d2-direct-boot/result
printf 'DIRECT\n' > "$D/mode"
mark GUI_RELEASED
/system/bin/setprop ctl.start x2d2-capture-trial
mark CAPTURE_DISPATCHED
# Only preparation of the specialty backend follows. It cannot block GUI main.
for name in integrated-job integration-service native-auto6 worker raw-pack full-jpeg zoom-server overlap-prepare overlap-container readiness-check reboot-reconcile native-first-frame-scoped native-job-cache native-job-render native-preview-commit native-stream-render jpeg-stream-join first-frame-jpeg jpeg-flow-pack; do
 $T ln -s "$P/$name" "$R/$name"
done
printf 'AUTHORIZED_RETAIN_INPUTS_INTEGRATION\n' > "$S/integration.once"
printf 'AUTHORIZED_NO_CAPTURE\n' > "$S/load.once"
mark BACKEND_FILES_READY
attempt=0
while [ "$(/system/bin/getprop init.svc.camera-test)" != running ] || [ ! -f "$A/ready" ]; do
 attempt=$((attempt+1)); [ "$attempt" -lt 300 ]; $T sleep 0.1
done
mark DEPENDENCIES_READY
/system/bin/setprop ctl.start x2d2-trial-guard
attempt=0
while [ ! -f /dev/x2d2-direct-boot/adopted ]; do
 attempt=$((attempt+1)); [ "$attempt" -lt 150 ]; $T sleep 0.1
done
mark BACKEND_ADOPTED
