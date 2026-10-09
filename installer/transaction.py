"""Atomic generation store used by offline tests and the future USB frontend."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

from .x2d2ext import VerifiedBundle, extract_verified, verify_bundle


class GenerationStore:
    def __init__(self, root: Path | str):
        self.root = Path(root)
        self.generations = self.root / "generations"
        self.active = self.root / "active.json"
        self.generations.mkdir(parents=True, exist_ok=True)

    def state(self) -> dict:
        if not self.active.exists():
            return {"format": 1, "extensions": {}}
        return json.loads(self.active.read_text("utf-8"))

    def _replace_state(self, state: dict) -> None:
        fd, temp_name = tempfile.mkstemp(prefix="active-", suffix=".json", dir=self.root)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(state, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, self.active)
        finally:
            Path(temp_name).unlink(missing_ok=True)

    def install(self, path: Path | str, fail_before_activate: bool = False) -> dict:
        bundle = verify_bundle(path)
        extension_id = bundle.manifest["id"]
        generation = bundle.digest[:24]
        destination = self.generations / generation
        if not destination.exists():
            staging = self.generations / f".{generation}.staging"
            shutil.rmtree(staging, ignore_errors=True)
            try:
                extract_verified(bundle, staging)
                verify_bundle(path)
                os.replace(staging, destination)
            finally:
                shutil.rmtree(staging, ignore_errors=True)
        if fail_before_activate:
            raise RuntimeError("injected activation failure")
        state = self.state()
        previous = state["extensions"].get(extension_id)
        state["extensions"][extension_id] = {
            "generation": generation,
            "version": bundle.manifest["version"],
            "previous": previous,
        }
        self._replace_state(state)
        return state

    def remove(self, extension_id: str) -> dict:
        state = self.state()
        state["extensions"].pop(extension_id, None)
        self._replace_state(state)
        return state

