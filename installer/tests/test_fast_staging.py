import json
import tempfile
import unittest
from pathlib import Path

from installer.fast_staging import bundle_files
from installer.x2d2ext import build_bundle, verify_bundle


class FastStagingTests(unittest.TestCase):
    def test_bundle_files_preserve_bytes_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {
                "format": 1, "id": "sample", "name": "Sample", "version": "1.0.0",
                "target": {"model": "Hasselblad X2D II 100C", "firmware": "1.3.16.2"},
                "components": [{"path": "payload/a", "role": "config", "mode": "0600"}],
            }
            path = build_bundle(manifest, {"payload/a": b"hello"}, root / "a.x2d2ext")
            plan, files = bundle_files(verify_bundle(path))
            self.assertEqual(files[0].data, b"hello")
            self.assertEqual(files[0].mode, "0600")
            stage = json.loads(files[-1].data)
            self.assertEqual(stage["mapping"][0]["file"], "p000")
            self.assertEqual(plan.generation, verify_bundle(path).digest[:24])


if __name__ == "__main__":
    unittest.main()
