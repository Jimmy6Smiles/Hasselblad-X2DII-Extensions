"""Build a local, installable AF-C bundle from pristine vendor binaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from .x2d2ext import build_bundle, file_sha256

ROOT = Path(__file__).resolve().parents[1]
AFC = ROOT / "extensions" / "electronic-shutter-afc"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera-service", required=True, type=Path)
    parser.add_argument("--camera-gui", required=True, type=Path)
    parser.add_argument("--ndk", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    with tempfile.TemporaryDirectory(prefix="x2d2-afc-build-") as temp:
        output = Path(temp) / "output"
        subprocess.run([
            sys.executable, str(AFC / "build.py"),
            "--camera-service", str(args.camera_service),
            "--camera-gui", str(args.camera_gui),
            "--ndk", str(args.ndk), "--out", str(output),
        ], check=True)
        build_record = json.loads((output / "manifest.json").read_text("utf-8"))
        patched_gui = output / "payload" / "camera-gui"
        ui_changes = build_record["ui_changes"]
        patch_files = {}
        for index, change in enumerate(ui_changes):
            name = f"payload/gui-patch-{index:02d}.bin"
            with patched_gui.open("rb") as stream:
                stream.seek(change["offset"])
                patch_files[name] = stream.read(change["size"])
        reconstructed = bytearray(args.camera_gui.read_bytes())
        for index, change in enumerate(ui_changes):
            patch = patch_files[f"payload/gui-patch-{index:02d}.bin"]
            start = change["offset"]
            reconstructed[start:start + len(patch)] = patch
        if hashlib.sha256(reconstructed).hexdigest() != build_record["payload"]["camera-gui"]:
            raise RuntimeError("GUI delta reconstruction does not match the verified build output")
        components = [
            {"path": "payload/afc-electronic.so", "role": "preload-library", "mode": "0755"},
            {"path": "payload/camera-service.env", "role": "config", "mode": "0644"},
        ]
        for index, change in enumerate(ui_changes):
            components.append({"path": f"payload/gui-patch-{index:02d}.bin", "role": "binary-patch",
                               "mode": "0644", "target": "/system/bin/camera-gui",
                               "offset": change["offset"], "size": change["size"],
                               "resource": change["resource"]})
        manifest = {
            "format": 1, "id": "electronic-shutter-afc", "name": "Electronic Shutter AF-C",
            "version": build_record["version"],
            "target": {"model": "Hasselblad X2D II 100C", "firmware": "1.3.16.2",
                       "factory": build_record["factory"]},
            "components": components,
            "runtime": {"preload": "payload/afc-electronic.so", "factory_gui": "/system/bin/camera-gui",
                        "environment": "payload/camera-service.env", "patch_count": len(ui_changes)},
            "independent": True,
            "notes": "Locally built from pristine firmware; contains vendor-derived camera-gui and must not be redistributed.",
        }
        files = {"payload/afc-electronic.so": output / "payload" / "afc-electronic.so",
                 "payload/camera-service.env": output / "payload" / "camera-service.env", **patch_files}
        destination = build_bundle(manifest, files, args.out)
    print(json.dumps({"bundle": str(destination.resolve()), "sha256": file_sha256(destination)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
