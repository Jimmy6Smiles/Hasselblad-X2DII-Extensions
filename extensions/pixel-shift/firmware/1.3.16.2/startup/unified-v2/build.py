"""Build self-authored boot libraries; never package proprietary GUI/IQ files."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cc',required=True,help='Android NDK clang executable')
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    out=root/'build';out.mkdir(exist_ok=True)
    flags=[args.cc,'--target=aarch64-linux-android28','-std=c11','-O2','-s',
           '-Wall','-Wextra','-Werror','-Wno-unused-function','-fPIC','-shared',
           '-I'+str(root/'include')]
    for source,name,extra in (
        ('unified-entry.c','entry.so',['-ldl']),
        ('guard.c','guard.so',['-DPS_NATIVE_COLOR_JOB','-DPS_INTEGRATION_BUILD',
                             '-DIP_BOOT="/data/x2d2-full-v1"']),
        ('storage-guard.c','storage-guard.so',[]),
    ):
        compile_flags=[x for x in extra if not x.startswith('-l')]
        libraries=[x for x in extra if x.startswith('-l')]
        subprocess.run(flags+compile_flags+[str(root/source)]+libraries+['-o',str(out/name)],check=True)
    for pattern in ('*.sh','*.rc','*.c','*.inc','*.h'):
        for source in root.glob(pattern):shutil.copyfile(source,out/source.name)
    files=[p for p in out.iterdir() if p.suffix in ('.so','.sh','.rc')]
    manifest={'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              'tests_passed':False,'automatic_device_install':False}
    (out/'package.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(out)

if __name__=='__main__':main()
