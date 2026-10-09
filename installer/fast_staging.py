"""Fast, verified staging over the camera's USB RNDIS link.

The control command still travels over the bounded Phocus WinUSB channel.  File
bytes use the point-to-point 192.168.42.0/24 link and are committed only after
the camera verifies their SHA-256 digest.
"""
from __future__ import annotations

import hashlib
import json
import socket
import threading
import zipfile
from dataclasses import dataclass

from .staging import REMOTE_ROOT, StagingPlan, _check_command
from .x2d2ext import VerifiedBundle

HOST_IP = "192.168.42.1"
CAMERA_IP = "192.168.42.2"


@dataclass(frozen=True)
class StagedFile:
    name: str
    data: bytes
    digest: str
    mode: str


def bundle_files(bundle: VerifiedBundle) -> tuple[StagingPlan, tuple[StagedFile, ...]]:
    generation = bundle.digest[:24]
    temporary = f"{REMOTE_ROOT}/staging/.{generation}.tmp"
    final = f"{REMOTE_ROOT}/generations/{generation}"
    files, mapping, records = [], [], []
    with zipfile.ZipFile(bundle.path, "r") as archive:
        for index, component in enumerate(bundle.manifest["components"]):
            name = f"p{index:03d}"
            data = archive.read(component["path"])
            digest = hashlib.sha256(data).hexdigest()
            files.append(StagedFile(name, data, digest, component["mode"]))
            records.append((name, digest, len(data)))
            mapping.append({"file": name, "component": component})
    stage = (json.dumps({"format": 1, "bundle_sha256": bundle.digest,
                         "manifest": bundle.manifest, "mapping": mapping},
                        sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    digest = hashlib.sha256(stage).hexdigest()
    files.append(StagedFile("stage.json", stage, digest, "0600"))
    records.append(("stage.json", digest, len(stage)))
    plan = StagingPlan(bundle.manifest["id"], generation, (), tuple(records), temporary, final)
    return plan, tuple(files)


def _send_one(session, remote: str, item: StagedFile, tag: int,
              host_ip: str = HOST_IP, camera_ip: str = CAMERA_IP) -> int:
    temporary = f"{remote}/{item.name}.tmp"
    final = f"{remote}/{item.name}"
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((host_ip, 0))
    listener.listen(1)
    listener.settimeout(12)
    port = listener.getsockname()[1]
    outcome: dict[str, object] = {}

    def receive_command() -> None:
        try:
            # Android toybox netcat otherwise keeps waiting for the peer's
            # receive half to close.  A one-second idle bound makes completion
            # deterministic while the SHA check still catches truncation.
            command = _check_command(f"/system/bin/toybox nc -W 1 {host_ip} {port} >{temporary}")
            outcome["output"] = session.shell(command, tag)
        except BaseException as error:  # re-raised on the controlling thread
            outcome["error"] = error

    worker = threading.Thread(target=receive_command, name="x2d2-rndis-receive", daemon=True)
    worker.start()
    try:
        connection, address = listener.accept()
        with connection:
            if address[0] != camera_ip:
                raise RuntimeError(f"unexpected RNDIS peer: {address[0]}")
            connection.settimeout(12)
            connection.sendall(item.data)
            connection.shutdown(socket.SHUT_WR)
    finally:
        listener.close()
    worker.join(15)
    if worker.is_alive():
        raise TimeoutError("camera netcat command did not finish")
    if "error" in outcome:
        raise outcome["error"]  # type: ignore[misc]
    session.shell(_check_command(
        f"test \"$(/system/bin/toybox sha256sum {temporary}|/system/bin/toybox cut -c1-64)\" = {item.digest}"), tag + 1)
    session.shell(_check_command(f"/system/bin/toybox chmod {item.mode} {temporary}"), tag + 2)
    session.shell(_check_command(f"/system/bin/toybox mv {temporary} {final}"), tag + 3)
    return tag + 4


def execute_fast(session, bundle: VerifiedBundle, first_tag: int,
                 host_ip: str = HOST_IP, camera_ip: str = CAMERA_IP) -> dict:
    plan, files = bundle_files(bundle)
    tag = first_tag
    session.shell(_check_command(
        f"umask 077;/system/bin/toybox mkdir -p {REMOTE_ROOT}/staging {REMOTE_ROOT}/generations"), tag)
    tag += 1
    session.shell(_check_command(
        f"/system/bin/toybox rm -rf {plan.temporary};/system/bin/toybox mkdir {plan.temporary}"), tag)
    tag += 1
    try:
        for item in files:
            tag = _send_one(session, plan.temporary, item, tag, host_ip, camera_ip)
        session.shell(_check_command(
            f"F={plan.final};S={plan.temporary};test -e $F&&/system/bin/toybox rm -rf $S||/system/bin/toybox mv $S $F"), tag)
    except Exception:
        try:
            session.shell(_check_command(f"/system/bin/toybox rm -rf {plan.temporary}"), tag + 1)
        except Exception:
            pass
        raise
    return {"id": plan.extension_id, "generation": plan.generation,
            "files": len(files), "bytes": sum(len(item.data) for item in files),
            "transport": "usb-rndis-tcp", "activated": False}
