"""Verify v2 distribution provenance using the independently pinned public key."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import zipfile
from cryptography.hazmat.primitives import serialization

PIN = '575dd226368fbc673611ebae5073be85af12abf5c5d4dfe77d5fb6e728f46cdf'

def verify(package, public_key):
    pem = Path(public_key).read_bytes()
    if hashlib.sha256(pem).hexdigest() != PIN:
        raise ValueError('Public key does not match the independent trust anchor')
    with zipfile.ZipFile(package) as z:
        envelope = json.loads(z.comment)
        if envelope['format'] != 'x2dii-signed-origin-v2':
            raise ValueError('Unsupported provenance version')
        raw = base64.b64decode(envelope['manifest_base64'], validate=True)
        signature = base64.b64decode(envelope['signature_base64'], validate=True)
        serialization.load_pem_public_key(pem).verify(signature, raw)
        manifest = json.loads(raw)
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != set(manifest['entries']):
            raise ValueError('ZIP member set differs from the signed manifest')
        for name, expected in manifest['entries'].items():
            if hashlib.sha256(z.read(name)).hexdigest() != expected:
                raise ValueError('Member digest mismatch: ' + name)
        return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('--public-key', type=Path,
                        default=Path(__file__).with_name('MOD_ORIGIN_PUBLIC_KEY.pem'))
    args = parser.parse_args()
    result = verify(args.package, args.public_key)
    print('Verified:', result['id'], result['version'], 'author:', result['feature_author'])
