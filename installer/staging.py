"""Generate bounded, idempotent shell commands for staging verified bundles."""
from __future__ import annotations

import base64
import hashlib
import json
import re
import zipfile
from dataclasses import dataclass

from .protocol import shell_request
from .x2d2ext import VerifiedBundle

REMOTE_ROOT = "/data/x2d2-extension-manager"
# The shell frame accepts at most 231 ASCII bytes. Keep enough headroom for the
# fixed manager path instead of relying on a path-length-dependent calculation.
CHUNK_BYTES = 48


@dataclass(frozen=True)
class StagingPlan:
    extension_id: str
    generation: str
    commands: tuple[str, ...]
    files: tuple[tuple[str, str, int], ...]
    temporary: str
    final: str


def _check_command(command: str) -> str:
    shell_request(command, 1)
    return command


def _file_commands(directory: str, name: str, data: bytes, mode: str) -> list[str]:
    if not re.fullmatch(r"p\d{3}|stage\.json", name):
        raise ValueError("unsafe remote staging name")
    final = f"{directory}/{name}"
    temporary = final + ".tmp"
    commands = [_check_command(f"/system/bin/toybox rm -f {temporary}")]
    for offset in range(0, len(data), CHUNK_BYTES):
        encoded = base64.b64encode(data[offset:offset + CHUNK_BYTES]).decode("ascii")
        commands.append(_check_command(f"printf %s {encoded}|/system/bin/toybox base64 -d >>{temporary}"))
    digest = hashlib.sha256(data).hexdigest()
    commands.append(_check_command(
        f"test \"$(/system/bin/toybox sha256sum {temporary}|/system/bin/toybox cut -c1-64)\" = {digest}"))
    commands.append(_check_command(f"/system/bin/toybox chmod {mode} {temporary}"))
    commands.append(_check_command(f"/system/bin/toybox mv {temporary} {final}"))
    return commands


def plan_bundle(bundle: VerifiedBundle) -> StagingPlan:
    generation = bundle.digest[:24]
    temporary = f"{REMOTE_ROOT}/staging/.{generation}.tmp"
    final = f"{REMOTE_ROOT}/generations/{generation}"
    commands = [
        _check_command(f"umask 077;/system/bin/toybox mkdir -p {REMOTE_ROOT}/staging {REMOTE_ROOT}/generations"),
        _check_command(f"/system/bin/toybox rm -rf {temporary};/system/bin/toybox mkdir {temporary}"),
    ]
    records = []
    mapping = []
    with zipfile.ZipFile(bundle.path, "r") as archive:
        for index, component in enumerate(bundle.manifest["components"]):
            remote_name = f"p{index:03d}"
            data = archive.read(component["path"])
            commands.extend(_file_commands(temporary, remote_name, data, component["mode"]))
            digest = hashlib.sha256(data).hexdigest()
            records.append((remote_name, digest, len(data)))
            mapping.append({"file": remote_name, "component": component})
    stage = (json.dumps({"format": 1, "bundle_sha256": bundle.digest,
                         "manifest": bundle.manifest, "mapping": mapping},
                        sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    commands.extend(_file_commands(temporary, "stage.json", stage, "0600"))
    records.append(("stage.json", hashlib.sha256(stage).hexdigest(), len(stage)))
    commands.append(_check_command(
        f"F={final};S={temporary};test -e $F&&/system/bin/toybox rm -rf $S||/system/bin/toybox mv $S $F"))
    return StagingPlan(bundle.manifest["id"], generation, tuple(commands), tuple(records), temporary, final)


def execute_plan(session, plan: StagingPlan, first_tag: int) -> dict:
    if not 0 < first_tag <= 0x7FFFFFFF - len(plan.commands):
        raise ValueError("invalid shell tag range")
    completed = 0
    try:
        for completed, command in enumerate(plan.commands, start=1):
            session.shell(command, first_tag + completed - 1)
    except Exception:
        try:
            session.shell(f"/system/bin/toybox rm -rf {plan.temporary}", first_tag + len(plan.commands))
        except Exception:
            pass
        raise
    return {"id": plan.extension_id, "generation": plan.generation,
            "commands": completed, "files": len(plan.files), "activated": False}
