"""Create the redistributable source/prebuilt archive without vendor firmware."""
from pathlib import Path
import hashlib
import json
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VERSION = "1.0.0"
DEST = ROOT / "dist" / f"X2DII-Electronic-Shutter-AFC-{VERSION}.zip"
FILES = (
    "README.md",
    "build.py",
    "package.py",
    "src/afc_eshutter.c",
    "prebuilt/1.3.16.2/afc-electronic.so",
    "prebuilt/1.3.16.2/manifest.json",
)

DEST.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(DEST, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for relative in FILES:
        path = HERE / relative
        archive.write(path, f"X2DII-Electronic-Shutter-AFC-{VERSION}/{relative}")

print(json.dumps({"archive": str(DEST), "size": DEST.stat().st_size,
                  "sha256": hashlib.sha256(DEST.read_bytes()).hexdigest()}, indent=2))
