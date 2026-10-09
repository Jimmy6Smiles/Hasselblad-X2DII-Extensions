"""Build a Pixel Shift bundle from a verified resident payload export."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .x2d2ext import build_bundle, file_sha256

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "extensions" / "pixel-shift" / "firmware" / "1.3.16.2" / "release.json"


def _role(name: str) -> str:
    if name.endswith(".so"):
        return "preload-library"
    if name.endswith(".patch"):
        return "binary-patch"
    if name.startswith("ui/"):
        return "runtime-gui"
    if name.endswith((".conf", ".sp")):
        return "config"
    return "boot-component"


def _mode(name: str) -> str:
    return "0700" if _role(name) in ("preload-library", "boot-component") else "0600"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True, type=Path)
    parser.add_argument("--gui-entry", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    release = json.loads(RELEASE.read_text("utf-8"))
    export = json.loads((args.payload / "export.json").read_text("utf-8"))
    exported = {item["path"]: item for item in export["files"]}
    expected = release["runtime_sha256"]
    if export["firmware"] != release["firmware"] or set(exported) != set(expected):
        raise RuntimeError("resident export does not match the release inventory")
    files, components = {}, []
    for name in expected:
        path = args.payload / Path(name)
        digest = file_sha256(path)
        if digest != expected[name] or exported[name]["sha256"] != digest or exported[name]["bytes"] != path.stat().st_size:
            raise RuntimeError(f"resident export verification failed: {name}")
        package_path = f"payload/{name}"
        files[package_path] = path
        components.append({"path": package_path, "role": _role(name), "mode": _mode(name)})
    manifest = {
        "format": 1,
        "id": "pixel-shift-400mp",
        "name": "400 MP Pixel Shift",
        "version": "1.0.0",
        "target": {
            "model": "Hasselblad X2D II 100C",
            "firmware": "1.3.16.2",
            "factory": {
                "camera-gui": "b1b643cb36176cd5a49129dd9bb2be480aa045a96ed1c35c30a779ab5af0801b",
                "camera-service": "51b9e02f8bfebf388be8dfa163c8e512bee19aeb8ae37a6712727ccc6f26a52d",
            },
        },
        "components": components,
        "runtime": {"entry": "payload/boot.sh", "gui_entry": "payload/system/libx2d2-gui-early.so",
                    "resident_files": len(components) + 1},
        "formats": {"supported": release["supported_formats"], "unsupported": release["unsupported_formats"]},
        "notes": "Built from a byte-verified export of the tested resident runtime for firmware 1.3.16.2.",
    }
    entry_digest = file_sha256(args.gui_entry)
    if entry_digest != release["gui_startup_library_sha256"]:
        raise RuntimeError("GUI startup library does not match the tested release")
    entry_name = "payload/system/libx2d2-gui-early.so"
    manifest["components"].append({"path": entry_name, "role": "preload-library", "mode": "0644"})
    files[entry_name] = args.gui_entry
    destination = build_bundle(manifest, files, args.out)
    print(json.dumps({"bundle": str(destination.resolve()), "sha256": file_sha256(destination),
                      "components": len(manifest["components"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
