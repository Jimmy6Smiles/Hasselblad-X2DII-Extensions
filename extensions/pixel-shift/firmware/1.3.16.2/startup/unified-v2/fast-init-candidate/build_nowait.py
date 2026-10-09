"""One-boot dependency experiment. Image workers and readiness checks unchanged."""
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parent
TOKEN='NO_CAMERA_TEST_BOOT_WAIT_V1\\n'
def replace_once(source,old,new):
    assert source.count(old)==1,old
    return source.replace(old,new)
def main():
    p=argparse.ArgumentParser();p.add_argument('--cc',required=True);a=p.parse_args()
    out=ROOT/'build-nowait';out.mkdir(exist_ok=True)
    base=ROOT.parent
    script=(ROOT/'build/unified-start.sh').read_text()
    script=replace_once(script,'while [ "$(/system/bin/getprop init.svc.camera-test)" != running ] || [ ! -f "$A/ready" ]; do','while [ ! -f "$A/ready" ]; do')
    script=replace_once(script,'mark BACKEND_FILES_READY','printf \'NO_CAMERA_TEST_BOOT_WAIT_V1\\n\' > "$D/no-camera-test-wait"\nmark BACKEND_FILES_READY')
    (out/'unified-start.sh').write_bytes(script.encode())
    guard=(base/'guard.c').read_text()
    flag='(exact_file("/dev/x2d2-unified-boot/mode","DIRECT\\n") && exact_file("/dev/x2d2-unified-boot/no-camera-test-wait","'+TOKEN+'"))'
    guard=replace_once(guard,'if(!capture_ok||!state("camera-test","running")||!state("camera-gui","running")||interrupted)',
                      'if(!capture_ok||(!'+flag+'&&!state("camera-test","running"))||!state("camera-gui","running")||interrupted)')
    life=(base/'unified_lifecycle.inc').read_text()
    life=replace_once(life,'if(!set_state(NULL,"start","camera-test"))return 0;',
                      'if(!'+flag+'&&!set_state(NULL,"start","camera-test"))return 0;')
    (out/'guard.c').write_text(guard);(out/'unified_lifecycle.inc').write_text(life)
    subprocess.run([a.cc,'--target=aarch64-linux-android28','-std=c11','-O2','-s','-Wall','-Wextra','-Werror','-Wno-unused-function','-fPIC','-shared','-DPS_NATIVE_COLOR_JOB','-DPS_INTEGRATION_BUILD','-DIP_BOOT="/data/x2d2-full-v1"','-I'+str(base/'include'),'-I'+str(base),str(out/'guard.c'),'-o',str(out/'guard.so')],check=True)
    rc=(base/'x2d2-trial.rc').read_text().replace('/system/x2d2-boot-v2/guard.so','/system/x2d2-nowait-v1/guard.so')
    assert rc.count('/system/x2d2-nowait-v1/guard.so')==2
    (out/'x2d2-trial.rc').write_bytes(rc.encode())
    # Structural contracts: precisely scoped gate change, no recovery changes.
    original=(base/'guard.c').read_text()
    assert guard.split('static int recover(',1)[1].split('static int guard_main(',1)[0]==original.split('static int recover(',1)[1].split('static int guard_main(',1)[0]
    assert 'state("camera-test"' not in script and 'getprop init.svc.camera-test' not in script
    assert script.index('no-camera-test-wait')<script.index('ctl.start x2d2-trial-guard')
    files=('unified-start.sh','guard.so','x2d2-trial.rc')
    (out/'package.json').write_text(json.dumps({'hashes':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in files},'tests_passed':True,'scope':'boot wait only; capture readiness binaries unchanged'},indent=2))
    print(out)
if __name__=='__main__':main()
