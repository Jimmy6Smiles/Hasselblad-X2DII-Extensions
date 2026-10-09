"""Convert a 1024x768 image to the X2D II boot-logo NV12 container."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from PIL import Image, ImageOps

WIDTH, HEIGHT = 1024, 768
HEADER = b"width:1024 height:768 offset-x:0 offset-y:0 format:2;"


def _limited(value: int, scale: int, center: bool = False) -> int:
    if center:
        return max(16, min(240, round(128 + scale * (value - 128) / 255)))
    return max(16, min(235, round(16 + scale * value / 255)))


def encode(source: Path) -> bytes:
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        if image.size != (WIDTH, HEIGHT):
            image = ImageOps.pad(image, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS,
                                 color=(0, 0, 0), centering=(0.5, 0.5))
        ycbcr = image.convert("YCbCr")
    y, cb, cr = (channel.tobytes() for channel in ycbcr.split())
    y_plane = bytes(_limited(value, 219) for value in y)
    uv_plane = bytearray(WIDTH * HEIGHT // 2)
    for row in range(0, HEIGHT, 2):
        base0, base1, target = row * WIDTH, (row + 1) * WIDTH, (row // 2) * WIDTH
        for column in range(0, WIDTH, 2):
            indexes = (base0 + column, base0 + column + 1, base1 + column, base1 + column + 1)
            u = sum(cb[index] for index in indexes) // 4
            v = sum(cr[index] for index in indexes) // 4
            uv_plane[target + column] = _limited(u, 224, True)
            uv_plane[target + column + 1] = _limited(v, 224, True)
    result = HEADER + y_plane + bytes(uv_plane)
    if len(result) != len(HEADER) + WIDTH * HEIGHT * 3 // 2:
        raise RuntimeError("unexpected boot-logo size")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    data = encode(args.source)
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_bytes(data)
    print(f"{len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
