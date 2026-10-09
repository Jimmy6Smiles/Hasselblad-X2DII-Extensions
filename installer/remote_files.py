"""Bounded file transfer helpers over the reviewed shell transport."""
from __future__ import annotations

import base64
import hashlib
import re

READ_CHUNK = 3072
ALLOWED_ROOTS = ("/data/x2d2-extension-manager/", "/data/x2d2-full-v1/")


def _path(path: str) -> str:
    if not path.startswith(ALLOWED_ROOTS) or not re.fullmatch(r"/[A-Za-z0-9._/-]+", path) or "/../" in path:
        raise ValueError("remote path is outside the reviewed extension roots")
    return path


def read_file(session, path: str, tag: int, max_size: int = 128 * 1024 * 1024) -> tuple[bytes, int]:
    path = _path(path)
    raw_size = session.shell(f"/system/bin/toybox stat -c %s {path}", tag).strip()
    if not raw_size.isdigit():
        raise RuntimeError("remote file size is not numeric")
    size = int(raw_size)
    if not 0 <= size <= max_size:
        raise RuntimeError("remote file exceeds download limit")
    output = bytearray()
    sequence = tag + 1
    for offset in range(0, size, READ_CHUNK):
        count = min(READ_CHUNK, size - offset)
        text = session.shell(
            f"/system/bin/toybox dd if={path} bs=1 skip={offset} count={count} 2>/dev/null|/system/bin/toybox base64",
            sequence)
        sequence += 1
        compact = "".join(text.split())
        block = base64.b64decode(compact, validate=True)
        if len(block) != count:
            raise RuntimeError("remote file chunk length mismatch")
        output.extend(block)
    return bytes(output), sequence


def read_file_verified(session, path: str, expected_sha256: str, tag: int,
                       max_size: int = 128 * 1024 * 1024) -> tuple[bytes, int]:
    data, next_tag = read_file(session, path, tag, max_size)
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise RuntimeError("remote file SHA-256 mismatch")
    return data, next_tag

