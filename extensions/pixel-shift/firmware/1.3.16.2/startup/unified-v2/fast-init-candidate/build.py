"""Build isolated startup candidate, leaving the accepted resident package intact."""
import argparse, hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    p = argparse.ArgumentParser(); p.add_argument('--cc', required=True)
    p.add_argument('--installer-fallback', action='store_true', help='Preserve the verified installer factory fallback')
    args = p.parse_args()
    out = ROOT / 'build'; out.mkdir(exist_ok=True)
    subprocess.run([args.cc, '--target=aarch64-linux-android28', '-std=c11', '-O2', '-s',
                    '-Wall', '-Wextra', '-Werror', '-fPIC', '-shared', str(ROOT/'boot-prep.c'),
                    '-o', str(out/'boot-prep.so')], check=True)
    source = (ROOT.parent/'unified-start.sh').read_text()
    if args.installer_fallback:
        old = ' printf \'LEGACY\\n\' > "$D/mode"\n exec /system/bin/sh "$B/direct-start.sh"'
        new = ' /system/bin/setprop ctl.start camera-service\n printf \'FACTORY\\n\' > "$D/mode"\n exit 0'
        assert source.count(old) == 1
        source = source.replace(old, new)
        assert hashlib.sha256(source.encode()).hexdigest() == '92d53bd42ba1d872d3c40330746f8e69e235c3365af7f3c26176b312ad87a47c'
    base_sha256 = hashlib.sha256(source.encode()).hexdigest()
    start = source.index('$T mkdir "$R"')
    end = source.index("printf 'DIRECT\\n' > /dev/x2d2-direct-boot/result", start)
    source = source[:start] + 'X2D2_BOOT_PREP=early LD_PRELOAD=/system/x2d2-fast-init-v1/boot-prep.so $T true\n' + source[end:]
    start = source.index('for name in ')
    end = source.index('mark BACKEND_FILES_READY', start)
    source = source[:start] + 'X2D2_BOOT_PREP=late LD_PRELOAD=/system/x2d2-fast-init-v1/boot-prep.so $T true\n' + source[end:]
    (out/'unified-start.sh').write_bytes(source.encode())
    hashes = {f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.suffix in ('.so','.sh')}
    (out/'package.json').write_text(json.dumps({'hashes':hashes,'tests_passed':False,'base_sha256':base_sha256,'installer_fallback':args.installer_fallback},indent=2))
    print(out)

if __name__ == '__main__':main()
