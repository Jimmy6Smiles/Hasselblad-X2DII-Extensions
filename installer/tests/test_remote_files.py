import base64
import hashlib
import unittest

from installer.remote_files import READ_CHUNK, read_file, read_file_verified


class FakeSession:
    def __init__(self, data): self.data = data
    def shell(self, command, tag):
        if "stat -c %s" in command: return str(len(self.data)) + "\n"
        offset = int(command.split("skip=")[1].split()[0])
        count = int(command.split("count=")[1].split()[0])
        return base64.encodebytes(self.data[offset:offset + count]).decode("ascii")


class RemoteFileTests(unittest.TestCase):
    def test_chunked_read_and_hash(self):
        data = bytes(range(256)) * (READ_CHUNK // 128 + 3)
        session = FakeSession(data)
        result, next_tag = read_file(session, "/data/x2d2-full-v1/payload/test.bin", 100)
        self.assertEqual(result, data)
        self.assertGreater(next_tag, 101)
        result, _ = read_file_verified(session, "/data/x2d2-full-v1/payload/test.bin",
                                       hashlib.sha256(data).hexdigest(), 200)
        self.assertEqual(result, data)

    def test_rejects_unreviewed_path(self):
        with self.assertRaises(ValueError): read_file(FakeSession(b"x"), "/mnt/media_rw/ssd/photo.3FR", 1)


if __name__ == "__main__": unittest.main()

