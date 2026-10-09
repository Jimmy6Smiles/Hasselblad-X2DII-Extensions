"""Execute real initialization syscalls in temporary host fixtures, never on camera."""
import json, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
names='integrated-job integration-service native-auto6 worker raw-pack full-jpeg zoom-server overlap-prepare overlap-container readiness-check reboot-reconcile native-first-frame-scoped native-job-cache native-job-render native-preview-commit native-stream-render jpeg-stream-join first-frame-jpeg jpeg-flow-pack'.split()
with tempfile.TemporaryDirectory() as build:
    exe=Path(build)/'prep'
    subprocess.run(['cc','-std=c11','-DHOST_TEST','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',str(ROOT/'boot-prep.c'),'-o',str(exe)],check=True)
    for case in ('success','missing-shutter','missing-ui','missing-iq','missing-worker','duplicate','symlink-input'):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp);p=r/'system/x2d2-boot-v2';(p/'ui').mkdir(parents=True);(r/'dev').mkdir()
            for n in [*names,'shutter.so','album-observer.so','diagnostic-iq.bin','native-color.conf','native-color.sp','ui/test.qml']:
                (p/n).write_bytes((n+'\n').encode()*17000)
            if case=='missing-shutter':(p/'shutter.so').unlink()
            if case=='missing-ui':(p/'ui/test.qml').unlink();(p/'ui').rmdir()
            if case=='missing-iq':(p/'diagnostic-iq.bin').unlink()
            if case=='missing-worker':(p/'worker').unlink()
            if case=='symlink-input':(p/'shutter.so').unlink();(p/'shutter.so').symlink_to(p/'album-observer.so')
            def run(phase):return subprocess.run([str(exe),phase],env=dict(os.environ,FIXTURE=tmp),capture_output=True)
            early=run('early')
            if case in ('missing-shutter','missing-ui','symlink-input'):
                assert early.returncode!=0;continue
            assert early.returncode==0,early.stderr
            n=r/'dev/x2d2-pregdc-trial';s=r/'dev/x2d2-shutter-v1';runtime=r/'dev/x2d2-integrated-v1'
            assert (n/'authorized.once').exists() and not (n/'diagnostic-iq.bin').exists()
            assert not (s/'load.once').exists() and not (runtime/'worker').exists()
            assert (s/'shutter.so').read_bytes()==(p/'shutter.so').read_bytes()
            if case=='duplicate':assert run('early').returncode!=0;continue
            late=run('late')
            if case in ('missing-iq','missing-worker'):
                assert late.returncode!=0 and not (s/'load.once').exists();continue
            assert late.returncode==0,late.stderr
            assert (n/'diagnostic-iq.bin').read_bytes()==(p/'diagnostic-iq.bin').read_bytes()
            assert (s/'load.once').read_text()=='AUTHORIZED_NO_CAPTURE\n'
            for name in names:assert (runtime/name).resolve()==p/name
script=(ROOT/'build/unified-start.sh').read_text()
assert script.index('X2D2_BOOT_PREP=early')<script.index('mark GUI_RELEASED')<script.index('ctl.start x2d2-capture-trial')<script.index('X2D2_BOOT_PREP=late')<script.index('ctl.start x2d2-trial-guard')
assert 'for name in ' not in script and '$T cp ' not in script
subprocess.run(['sh','-n',str(ROOT/'build/unified-start.sh')],check=True)
p=ROOT/'build/package.json';data=json.loads(p.read_text());data.update(tests_passed=True,host_cases=7);p.write_text(json.dumps(data,indent=2))
print('PASS 7 native helper cases and generated startup ordering/syntax')
