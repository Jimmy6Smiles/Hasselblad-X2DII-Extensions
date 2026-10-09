"""Command-line entry point for the offline Extension Manager foundation."""
from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

from .transaction import GenerationStore
from .x2d2ext import verify_bundle


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="x2d2-extension-manager")
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="verify an .x2d2ext bundle")
    verify.add_argument("bundle", type=Path)
    plan = commands.add_parser("plan", help="show the verified install plan")
    plan.add_argument("bundle", type=Path)
    simulate = commands.add_parser("simulate-install", help="exercise atomic install locally")
    simulate.add_argument("bundle", type=Path)
    simulate.add_argument("root", type=Path)
    commands.add_parser("probe-camera", help="perform a read-only X2D II USB handshake")
    stage = commands.add_parser("stage-camera", help="upload a verified bundle without activating it")
    stage.add_argument("bundle", type=Path)
    args = parser.parse_args(argv)
    if args.command == "probe-camera":
        from .windows_usb import UsbError, snapshot
        try:
            result = snapshot()
        except UsbError as error:
            print(json.dumps({"ok": False, "error": error.code, "win32": error.win32}, indent=2))
            return 2
    elif args.command == "verify":
        bundle = verify_bundle(args.bundle)
        result = {"ok": True, "id": bundle.manifest["id"], "version": bundle.manifest["version"],
                  "sha256": bundle.digest}
    elif args.command == "plan":
        bundle = verify_bundle(args.bundle)
        result = {"target": bundle.manifest["target"], "components": bundle.manifest["components"],
                  "camera_write": False, "note": "offline plan only"}
    elif args.command == "stage-camera":
        from .protocol import validate_snapshot
        from .staging import execute_plan, plan_bundle
        from .windows_usb import WinUsbSession
        bundle = verify_bundle(args.bundle)
        staging = plan_bundle(bundle)
        with WinUsbSession() as session:
            validate_snapshot(session.read_parameter(27, 1), session.read_parameter(28, 2))
            result = execute_plan(session, staging, secrets.randbelow(0x3FFFFFFF) + 100)
    else:
        result = GenerationStore(args.root).install(args.bundle)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
