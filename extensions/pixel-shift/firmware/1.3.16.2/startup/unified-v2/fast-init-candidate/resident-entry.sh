#!/system/bin/sh
# Resident no-camera-test-wait startup; not a one-boot token wrapper.
# Enabled/pending checks and factory fallback remain in the target script.
set -eu
exec /system/bin/sh /system/x2d2-nowait-v1/unified-start.sh
