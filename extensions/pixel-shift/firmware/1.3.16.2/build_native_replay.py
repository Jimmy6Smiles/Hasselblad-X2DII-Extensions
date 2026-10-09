"""离线构建新增原厂回放模块；不连接相机，不包含厂商库。"""
from pathlib import Path
import argparse,subprocess,json,hashlib
p=argparse.ArgumentParser()
for n in ('ndk','camera-libs','out'):p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();B=Path(__file__).resolve().parent;a.out.mkdir(parents=True,exist_ok=True)
cc=a.ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
flags=['--target=aarch64-linux-android28','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-misleading-indentation','-fPIE','-pie']
jobs={
 'native-stream-render':('native-renderer/native_merged_tile_trial.c',['-s','-Wno-unused-variable','-DNATIVE_JPEG_QUALITY=80','-DNATIVE_JOB_RUNTIME','-DNATIVE_CACHE_INPUT','-DNATIVE_MERGED_CONTAINER_INPUT','-DNATIVE_FULL_PREVIEW','-DNATIVE_REQUEST_ID_TEST'],['libdbus.so','libduml_hal.so','libduml_vcodec.so']),
 'jpeg-stream-join':('native-join/join.c',[],[]),
 'jpeg-flow-pack':('jpeg-pack/jpeg_first_frame_pack.c',['-s'],[]),
 'first-frame-jpeg':('jpeg-pack/first_frame_jpeg.c',['-s'],[]),
 'native-auto6':('capture/native_auto6.c',['-s'],[]),
 'integration-service':('service/integration_service.c',['-s'],[]),
}
expected=json.loads((B/'release.json').read_text())['runtime_sha256'];result={}
for n,(src,extra,libs) in jobs.items():
 args=[str(cc),*flags,*extra,str(B/'src'/src),*[str(a.camera_libs/l) for l in libs]]
 if n in ('native-stream-render','jpeg-stream-worker'):args+=['-lm']
 subprocess.run([*args,'-o',str(a.out/n)],check=True)
 digest=hashlib.sha256((a.out/n).read_bytes()).hexdigest();result[n]=dict(sha256=digest,matches_resident=digest==expected[n])
(a.out/'native-build-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert all(x['matches_resident'] for x in result.values())
