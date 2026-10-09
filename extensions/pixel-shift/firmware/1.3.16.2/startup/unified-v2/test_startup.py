"""Execute selector, ordering, readiness and failure contracts with host mocks."""
from pathlib import Path
import tempfile,subprocess,os,json
P=Path(__file__).parent/'build'
mock='''#!/usr/bin/python3
import sys,os,subprocess
from pathlib import Path
r=Path(os.environ['FIXTURE']);a=sys.argv[1:];n=Path(sys.argv[0]).name
with (r/'calls').open('a') as f:f.write(n+' '+' '.join(a)+'\\n')
case=os.environ['CASE']
if n=='getprop':
 if a[0]=='sys.powerctl':print('')
 elif a[0].endswith('camera-test'):print('stopped' if (r/'test-stopped').exists() else 'running')
 else:print('stopped')
elif n=='setprop':
 if a==['ctl.stop','camera-test']:(r/'test-stopped').touch()
 if a==['ctl.start','x2d2-capture-trial']:
  assert (r/'dev/x2d2-pregdc-trial/authorized.once').exists()
  assert (r/'dev/x2d2-unified-boot/mode').read_text()=='DIRECT\\n'
  (r/'dev/x2d2-album-refresh-v1/ready').touch()
 if a==['ctl.start','x2d2-trial-guard']:
  assert (r/'dev/x2d2-integrated-v1/integration-service').exists()
  (r/'dev/x2d2-direct-boot/adopted').touch()
elif n=='toybox':
 if a[0] in ('chcon','sync','sleep'):pass
 elif a[0]=='ln':
  if case=='mount-fail':sys.exit(1)
  assert Path(a[-2]).exists()
  sys.exit(subprocess.call(a))
 elif a[0]=='timeout':
  if case=='busy':print('busy');sys.exit(0)
  print('exposure_status = E_ExposureStatus_None(0)' if a[-1]=='exposure_status' else 'storage_processing_counter = 0')
 else:sys.exit(subprocess.call(a))
'''
def fixture(case,script='unified-start.sh'):
 with tempfile.TemporaryDirectory() as tmp:
  r=Path(tmp)
  for d in ('bin','dev','data/x2d2-full-v1','data/x2d2-integrated-v1','system/x2d2-boot-v2/ui'):(r/d).mkdir(parents=True,exist_ok=True)
  for n in ('toybox','setprop','getprop'):
   f=r/'bin'/n;f.write_text(mock);f.chmod(0o700)
  (r/'bin/sh').symlink_to('/bin/sh')
  b=r/'data/x2d2-full-v1';(b/'enabled').touch()
  (b/'direct-start.sh').write_text('echo LEGACY_PATH\n')
  (b/'direct-recover.sh').write_text('echo LEGACY_RECOVERY\n')
  if case not in ('legacy','resident','resident-pending','resident-disabled'):(b/'unified.once').touch()
  if case.startswith('resident'):(b/'unified.enabled').touch()
  if case in ('pending','resident-pending'):(r/'data/x2d2-integrated-v1/pending').touch()
  if case in ('disabled','resident-disabled'):(b/'disabled').touch()
  p=r/'system/x2d2-boot-v2'
  (p/'ui/PixelShiftState.qml').touch()
  for n in ('shutter.so','album-observer.so','diagnostic-iq.bin','native-color.conf','native-color.sp'):(p/n).touch()
  for line in (P/'unified-start.sh').read_text().splitlines():
   if line.startswith('for name in '):
    for n in line[len('for name in '):].split(';')[0].split():(p/n).touch()
  for f in P.glob('*.sh'):
   s=f.read_text()
   for old,new in [('/system/bin',str(r/'bin')),('/system/',str(r/'system')+'/'),('/data/',str(r/'data')+'/'),('/dev/',str(r/'dev')+'/')]:s=s.replace(old,new)
   (p/f.name).write_text(s)
  d=r/'dev/x2d2-unified-boot'
  if script!='unified-start.sh':
   d.mkdir();(d/'mode').write_text('LEGACY\n' if case=='legacy' else 'DIRECT\n')
   (r/'dev/x2d2-album-refresh-v1').mkdir()
  res=subprocess.run(['sh',str(p/script)],capture_output=True,env=dict(os.environ,FIXTURE=tmp,CASE=case),timeout=15)
  calls=(r/'calls').read_text() if (r/'calls').exists() else ''
  if script=='unified-start.sh':
   mode=(d/'mode').read_text()
   if case in ('legacy','pending','disabled','resident-pending','resident-disabled'):
    assert res.returncode==0 and mode=='LEGACY\n' and b'LEGACY_PATH' in res.stdout
    assert 'ctl.start' not in calls
   elif case=='mount-fail':
    assert res.returncode!=0 and mode=='FAILED\n' and 'ctl.start' not in calls
   else:
    assert res.returncode==0,(res.stderr,calls)
    assert mode=='DIRECT\n' and 'ctl.stop' not in calls
    assert calls.index('ctl.start x2d2-capture-trial')<calls.index('/integration-service')<calls.index('ctl.start x2d2-trial-guard')
    assert 'cp '+str(p/'gui') not in calls
  elif script=='unified-storage.sh':
   assert res.returncode==0,res.stderr
   if case=='legacy':assert 'ctl.start camera-storage' in calls and 'x2d2-storage-trial' not in calls
   else:assert 'ctl.start x2d2-storage-trial' in calls and 'ctl.start camera-storage' not in calls
  elif case=='busy':assert res.returncode!=0 and 'ctl.stop' not in calls
  else:
   assert res.returncode==0,res.stderr
   assert calls.index('ctl.stop x2d2-capture-trial')<calls.index('ctl.start camera-service')
for case in ('direct','legacy','pending','disabled','mount-fail','resident','resident-pending','resident-disabled'):fixture(case)
for case in ('direct','legacy'):fixture(case,'unified-storage.sh')
for case in ('direct','busy'):fixture(case,'unified-recover.sh')
for f in P.glob('*.sh'):subprocess.run(['sh','-n',str(f)],check=True)
life=(P/'unified_lifecycle.inc').read_text();guard=(P/'guard.c').read_text()
assert 'int child_count=unified?2:3;' in life
assert 'unified?observe(NULL):direct?' in guard
assert 'STOP_NATIVE_BEFORE_OWNER_V1' in life
assert 'DIRECT\\n")||ctl("stop","camera-storage")' in (P/'storage-guard.c').read_text()
j=json.loads((P/'package.json').read_text());j['tests_passed']=True;j['host_cases']=12
(P/'package.json').write_text(json.dumps(j,indent=2))
print('PASS 12 executed startup/fallback cases; startup-only binary changes')
