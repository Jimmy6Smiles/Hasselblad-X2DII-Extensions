"""Build pinned core binaries offline; never connect to a camera."""
from pathlib import Path
import argparse,subprocess,json,hashlib
p=argparse.ArgumentParser()
for n in ('ndk','jpeg-headers','camera-jpeg','out'):p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--zoom-jpeg-config',type=Path,required=True)
p.add_argument('--zoom-jpeg-headers',type=Path,required=True)
p.add_argument('--zoom-jpeg-static',type=Path,required=True)
a=p.parse_args();base=Path(__file__).resolve().parent;a.out.mkdir(parents=True,exist_ok=True)
cc=a.ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
assert cc.is_file() and (a.jpeg_headers/'jpeglib.h').is_file() and a.camera_jpeg.is_file()
flags=['--target=aarch64-linux-android28','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-misleading-indentation','-fPIE','-pie','-s']
jobs={
 'integrated-job':([base/'src/coordinator/integrated_job.c'],['-DPS_NATIVE_COLOR_JOB']),
 'overlap-container':([base/'src/merge/overlap_container_worker.c',base/'src/merge/auto_prepare.c'],['-pthread','-DPS_BATCH_BLACK','-DPS_PREPARE_LIBRARY','-DPS_PREPARE_CANCEL_HOOK','-DPS_CHUNK_PIPELINE']),
 'zoom-server':([base/'src/zoom/zoom_album_server.c'],['-Wl,--gc-sections']),
}
expected=json.loads((base/'release.json').read_text())['runtime_sha256'];result={}
for name,(sources,extra) in jobs.items():
 if name=='zoom-server':
  assert (a.zoom_jpeg_config/'jconfig.h').is_file() and a.zoom_jpeg_static.is_file()
  command=[str(cc),*flags,*extra,'-I'+str(a.zoom_jpeg_config),'-I'+str(a.zoom_jpeg_headers),*map(str,sources),str(a.zoom_jpeg_static),'-lm']
 else:
  command=[str(cc),*flags,*extra,'-I'+str(a.jpeg_headers),*map(str,sources)]
  if name!='integrated-job':command.extend([str(a.camera_jpeg),'-lm'])
 subprocess.run([*command,'-o',str(a.out/name)],check=True)
 digest=hashlib.sha256((a.out/name).read_bytes()).hexdigest()
 result[name]=dict(sha256=digest,matches_resident=digest==expected[name])
(a.out/'build-result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2));assert all(r['matches_resident'] for r in result.values())
