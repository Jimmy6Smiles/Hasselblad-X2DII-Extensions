import hashlib
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from installer.transaction import GenerationStore
from installer.staging import plan_bundle
from installer.x2d2ext import BundleError, build_bundle, verify_bundle


def manifest(version="1.0.0", firmware="1.3.16.2"):
    return {"format": 1, "id": "test-extension", "name": "Test Extension", "version": version,
            "target": {"model": "Hasselblad X2D II 100C", "firmware": firmware},
            "components": [{"path": "payload/module.so", "role": "preload-library", "mode": "0755"}]}


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def bundle(self, name="valid.x2d2ext", version="1.0.0"):
        path = self.root / name
        build_bundle(manifest(version), {"payload/module.so": b"arm64-test"}, path)
        return path

    def test_valid_bundle_and_deterministic_output(self):
        first, second = self.bundle("one.x2d2ext"), self.bundle("two.x2d2ext")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(verify_bundle(first).manifest["id"], "test-extension")

    def test_tampered_payload_is_rejected(self):
        original = self.bundle()
        tampered = self.root / "tampered.x2d2ext"
        with zipfile.ZipFile(original) as source, zipfile.ZipFile(tampered, "w") as target:
            for info in source.infolist():
                data = source.read(info.filename)
                if info.filename == "payload/module.so": data += b"tampered"
                target.writestr(info, data)
        with self.assertRaisesRegex(BundleError, "SHA-256 mismatch"):
            verify_bundle(tampered)

    def test_traversal_is_rejected(self):
        path = self.root / "traversal.x2d2ext"
        with zipfile.ZipFile(path, "w") as archive: archive.writestr("../extension.json", b"{}")
        with self.assertRaisesRegex(BundleError, "unsafe archive path"): verify_bundle(path)

    def test_duplicate_member_is_rejected(self):
        path = self.root / "duplicate.x2d2ext"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("extension.json", b"{}")
                archive.writestr("extension.json", b"{}")
        with self.assertRaisesRegex(BundleError, "duplicate archive member"): verify_bundle(path)

    def test_unlisted_payload_is_rejected(self):
        original = self.bundle()
        changed = self.root / "extra.x2d2ext"
        with zipfile.ZipFile(original) as source, zipfile.ZipFile(changed, "w") as target:
            entries = {info.filename: source.read(info.filename) for info in source.infolist()}
            entries["payload/extra.bin"] = b"extra"
            lines = entries["manifest.sha256"].decode("ascii")
            lines += f"{hashlib.sha256(b'extra').hexdigest()}  payload/extra.bin\n"
            entries["manifest.sha256"] = lines.encode("ascii")
            for name, data in entries.items(): target.writestr(name, data)
        with self.assertRaisesRegex(BundleError, "component list"):
            verify_bundle(changed)

    def test_wrong_firmware_is_rejected(self):
        with self.assertRaisesRegex(BundleError, "only accepts"):
            build_bundle(manifest(firmware="1.3.16.3"), {"payload/module.so": b"x"}, self.root / "bad.x2d2ext")

    def test_failed_activation_preserves_previous_state(self):
        store = GenerationStore(self.root / "camera")
        old = store.install(self.bundle("v1.x2d2ext", "1.0.0"))
        with self.assertRaisesRegex(RuntimeError, "injected"):
            store.install(self.bundle("v2.x2d2ext", "1.1.0"), fail_before_activate=True)
        self.assertEqual(store.state(), old)

    def test_remove_only_changes_active_state(self):
        store = GenerationStore(self.root / "camera")
        store.install(self.bundle())
        self.assertEqual(store.remove("test-extension")["extensions"], {})
        self.assertTrue(any(store.generations.iterdir()))

    def test_camera_staging_plan_is_bounded_and_deterministic(self):
        verified = verify_bundle(self.bundle())
        first, second = plan_bundle(verified), plan_bundle(verified)
        self.assertEqual(first, second)
        self.assertTrue(first.commands)
        self.assertTrue(all(len(command.encode("ascii")) <= 231 for command in first.commands))
        self.assertEqual(first.files[0][2], len(b"arm64-test"))


if __name__ == "__main__": unittest.main()
