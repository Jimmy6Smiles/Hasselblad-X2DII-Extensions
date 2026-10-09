"""Command-line entry point for the offline Extension Manager foundation."""
from __future__ import annotations

import argparse
import json
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
    args = parser.parse_args(argv)
    bundle = verify_bundle(args.bundle)
    if args.command == "verify":
        result = {"ok": True, "id": bundle.manifest["id"], "version": bundle.manifest["version"],
                  "sha256": bundle.digest}
    elif args.command == "plan":
        result = {"target": bundle.manifest["target"], "components": bundle.manifest["components"],
                  "camera_write": False, "note": "offline plan only"}
    else:
        result = GenerationStore(args.root).install(args.bundle)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

