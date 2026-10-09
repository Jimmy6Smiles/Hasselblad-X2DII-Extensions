"""Export the verified resident Pixel Shift payload for manager migration.

This reads extension files only. It never reads photographs, settings or user
data and it never changes the camera.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import tempfile
from pathlib import Path, PurePosixPath

from .remote_files import read_file_verified
from .windows_usb import WinUsbSession

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "extensions" / "pixel-shift" / "firmware" / "1.3.16.2" / "release.json"
REMOTE = "/data/x2d2-full-v1/payload"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    release = json.loads(RELEASE.read_text("utf-8"))
    expected = release["runtime_sha256"]
    args.out.mkdir(parents=True, exist_ok=True)
    tag = secrets.randbelow(0x10000000) + 1000
    written = []
    with WinUsbSession() as session:
        for name, digest in expected.items():
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError("unsafe release path")
            data, tag = read_file_verified(session, f"{REMOTE}/{name}", digest, tag)
            destination = args.out.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix=destination.name + ".", dir=destination.parent)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, destination)
            finally:
                Path(temporary).unlink(missing_ok=True)
            written.append({"path": name, "bytes": len(data), "sha256": digest})
    (args.out / "export.json").write_text(json.dumps({"firmware": release["firmware"], "files": written}, indent=2) + "\n", "utf-8")
    print(json.dumps({"files": len(written), "bytes": sum(item["bytes"] for item in written),
                      "output": str(args.out.resolve())}, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())

