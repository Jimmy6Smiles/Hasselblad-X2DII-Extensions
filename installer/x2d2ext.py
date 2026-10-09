"""Build and verify deterministic .x2d2ext extension bundles.

This module deliberately contains no camera transport.  A bundle must pass this
offline boundary before a future device installer is allowed to stage it.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

FORMAT_VERSION = 1
MAX_MEMBER_SIZE = 128 * 1024 * 1024
MAX_EXPANDED_SIZE = 256 * 1024 * 1024
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
REQUIRED_ROOT = {"extension.json", "manifest.sha256"}


class BundleError(ValueError):
    pass


@dataclass(frozen=True)
class VerifiedBundle:
    path: Path
    manifest: dict
    digest: str
    files: tuple[str, ...]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_name(name: str) -> str:
    if not name or "\\" in name or name.startswith("/"):
        raise BundleError(f"unsafe archive path: {name!r}")
    path = PurePosixPath(name)
    if any(part in ("", ".", "..") for part in path.parts):
        raise BundleError(f"unsafe archive path: {name!r}")
    normalized = path.as_posix()
    if normalized != name or name.endswith("/"):
        raise BundleError(f"non-canonical archive path: {name!r}")
    return normalized


def _validate_manifest(data: object) -> dict:
    if not isinstance(data, dict):
        raise BundleError("extension.json must contain an object")
    required = {"format", "id", "name", "version", "target", "components"}
    missing = required - data.keys()
    if missing:
        raise BundleError(f"extension.json is missing: {', '.join(sorted(missing))}")
    if data["format"] != FORMAT_VERSION:
        raise BundleError(f"unsupported package format: {data['format']!r}")
    if not isinstance(data["id"], str) or not ID_RE.fullmatch(data["id"]):
        raise BundleError("invalid extension id")
    if not isinstance(data["name"], str) or not data["name"].strip():
        raise BundleError("invalid extension name")
    if not isinstance(data["version"], str) or not VERSION_RE.fullmatch(data["version"]):
        raise BundleError("invalid extension version")
    target = data["target"]
    if not isinstance(target, dict) or set(("model", "firmware")) - target.keys():
        raise BundleError("target must provide model and firmware")
    if target["model"] != "Hasselblad X2D II 100C" or target["firmware"] != "1.3.16.2":
        raise BundleError("this manager build only accepts X2D II 100C firmware 1.3.16.2")
    components = data["components"]
    if not isinstance(components, list) or not components:
        raise BundleError("components must be a non-empty list")
    seen = set()
    for component in components:
        if not isinstance(component, dict):
            raise BundleError("invalid component record")
        if set(("path", "role", "mode")) - component.keys():
            raise BundleError("component must provide path, role and mode")
        path = _safe_name(component["path"])
        if not path.startswith("payload/") or path in seen:
            raise BundleError(f"invalid or duplicate component path: {path}")
        seen.add(path)
        if component["role"] not in ("preload-library", "runtime-gui", "binary-patch", "config", "boot-component"):
            raise BundleError(f"unsupported component role: {component['role']}")
        if not re.fullmatch(r"0[0-7]{3}", str(component["mode"])):
            raise BundleError(f"invalid component mode: {component['mode']!r}")
    return data


def _parse_hash_manifest(raw: bytes) -> dict[str, str]:
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise BundleError("manifest.sha256 must be ASCII") from exc
    records: dict[str, str] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise BundleError("malformed manifest.sha256")
        name = _safe_name(match.group(2))
        if name in records or name == "manifest.sha256":
            raise BundleError(f"duplicate or recursive hash entry: {name}")
        records[name] = match.group(1)
    return records


def verify_bundle(path: Path | str) -> VerifiedBundle:
    path = Path(path)
    digest = file_sha256(path)
    try:
        archive = zipfile.ZipFile(path, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise BundleError(f"not a valid extension bundle: {exc}") from exc
    with archive:
        infos = archive.infolist()
        names, expanded = set(), 0
        for info in infos:
            name = _safe_name(info.filename)
            if name in names:
                raise BundleError(f"duplicate archive member: {name}")
            names.add(name)
            if stat.S_ISLNK((info.external_attr >> 16) & 0xFFFF):
                raise BundleError(f"symbolic links are not allowed: {name}")
            if info.file_size > MAX_MEMBER_SIZE:
                raise BundleError(f"archive member too large: {name}")
            expanded += info.file_size
            if expanded > MAX_EXPANDED_SIZE:
                raise BundleError("expanded bundle exceeds size limit")
        if not REQUIRED_ROOT.issubset(names):
            raise BundleError("bundle is missing extension.json or manifest.sha256")
        try:
            manifest = _validate_manifest(json.loads(archive.read("extension.json")))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise BundleError("extension.json is not valid UTF-8 JSON") from exc
        hashes = _parse_hash_manifest(archive.read("manifest.sha256"))
        expected = names - {"manifest.sha256"}
        if set(hashes) != expected:
            missing = expected - set(hashes)
            extra = set(hashes) - expected
            raise BundleError(f"hash coverage mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
        for name, expected_hash in hashes.items():
            actual = hashlib.sha256(archive.read(name)).hexdigest()
            if actual != expected_hash:
                raise BundleError(f"SHA-256 mismatch: {name}")
        components = {item["path"] for item in manifest["components"]}
        payloads = {name for name in names if name.startswith("payload/")}
        if components != payloads:
            raise BundleError("component list does not exactly match payload files")
    return VerifiedBundle(path, manifest, digest, tuple(sorted(names)))


def build_bundle(manifest: dict, files: dict[str, Path | bytes], destination: Path | str) -> Path:
    manifest = _validate_manifest(manifest)
    canonical: dict[str, bytes] = {}
    for name, source in files.items():
        name = _safe_name(name)
        canonical[name] = source if isinstance(source, bytes) else Path(source).read_bytes()
    components = {item["path"] for item in manifest["components"]}
    if set(canonical) != components:
        raise BundleError("files must exactly match manifest components")
    extension_json = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    canonical["extension.json"] = extension_json
    hashes = "".join(f"{hashlib.sha256(canonical[name]).hexdigest()}  {name}\n" for name in sorted(canonical))
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False, suffix=".tmp") as stream:
        temp = Path(stream.name)
    try:
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(canonical):
                info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (0o100644 << 16)
                archive.writestr(info, canonical[name])
            info = zipfile.ZipInfo("manifest.sha256", (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100644 << 16)
            archive.writestr(info, hashes.encode("ascii"))
        os.replace(temp, destination)
    finally:
        temp.unlink(missing_ok=True)
    verify_bundle(destination)
    return destination


def extract_verified(bundle: VerifiedBundle, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle.path, "r") as archive:
        for name in bundle.files:
            target = destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))
