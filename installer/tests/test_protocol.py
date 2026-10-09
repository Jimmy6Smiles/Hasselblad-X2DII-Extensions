import struct
import unittest

from installer.protocol import (ProtocolError, ReadReply, crc_hqx, read_request,
                                shell_reply, shell_request, validate_snapshot)


class ProtocolTests(unittest.TestCase):
    def test_crc_reference_vector(self):
        self.assertEqual(crc_hqx(b"123456789"), 0x31C3)

    def test_read_request_is_fixed_to_reviewed_parameters(self):
        self.assertEqual(read_request(27, 0x1234), bytes.fromhex("04000805053412021b00"))
        with self.assertRaises(ProtocolError): read_request(99, 1)

    def test_read_reply_reassembles_frames(self):
        reply = ReadReply(7)
        self.assertIsNone(reply.add(b"\x03\x00\x05\x08\x00" + bytes(255)))
        # A realistic short reply is tested independently because a 255-byte first
        # fragment cannot be followed by arbitrary text under the protocol limit.
        reply = ReadReply(7)
        self.assertEqual(reply.add(b"\x03\x00\x05\x08\x05\x07\x00\x82i1"), b"i1")

    def test_shell_frame_and_reply_validation(self):
        request = shell_request("printf OK", 99)
        self.assertEqual(len(request), 257)
        self.assertEqual(struct.unpack_from("<I", request, 17)[0], crc_hqx(request[21:257]))
        packet = bytearray(260)
        packet[:5] = b"\x09\x00\x05\x08\xfc"
        struct.pack_into("<I", packet, 5, 65)
        struct.pack_into("<I", packet, 9, 0)
        struct.pack_into("<I", packet, 13, 99)
        packet[25:27] = b"OK"
        struct.pack_into("<I", packet, 17, crc_hqx(packet[21:257]))
        self.assertEqual(shell_reply(bytes(packet), 99), (True, b"OK"))
        packet[30] ^= 1
        with self.assertRaisesRegex(ProtocolError, "CRC"): shell_reply(bytes(packet), 99)

    def test_snapshot_accepts_only_reviewed_version(self):
        self.assertTrue(validate_snapshot(b"S6,v4.2.0", b"i1")["camera_running"])
        with self.assertRaises(ProtocolError): validate_snapshot(b"S6,v4.3.0", b"i1")


if __name__ == "__main__": unittest.main()
