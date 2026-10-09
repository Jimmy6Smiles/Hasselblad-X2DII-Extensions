"""离线替换自写 QML 片段；原厂资源由使用者自行提供，不随源码分发。"""
from pathlib import Path
import argparse,hashlib,struct,zlib
p=argparse.ArgumentParser()
p.add_argument('--base-patch',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();base=a.base_patch.read_bytes()
assert hashlib.sha256(base).hexdigest()=='73ed44075089d44e279398cfcbdc884d5b4951032958293b1db3400146a55db2'
qml=zlib.decompress(base[4:]).decode();root=Path(__file__).resolve().parent
for name,start,end in [('AlbumBinding.qml','Item {\nid: psAlbumBinding','property BrowseViewViewModel'),('DetailLayer.qml','Item {\nid: psZoomLayer','TiledImage {\nid: fastFullRawImage')]:
 i=qml.index(start);j=qml.index(end,i);qml=qml[:i]+(root/'ui'/name).read_text()+qml[j:]
raw=qml.encode();v=struct.pack('>I',len(raw))+zlib.compress(raw,9)
assert len(v)<=len(base)
v+=bytes(len(base)-len(v))
assert hashlib.sha256(v).hexdigest()=='6d11be377f124d627779c12059bad523bf77a7396f3a70ee3cc7f68678fb5cc2'
with a.out.open('xb') as f:f.write(v)
print('QML_PATCH_VERIFIED')
