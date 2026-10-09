"""Pure framing rules for the reviewed Hasselblad control channel."""
from __future__ import annotations

import re
import struct


class ProtocolError(ValueError):
    pass


def crc_hqx(data: bytes) -> int:
    value = 0
    for byte in data:
        value ^= byte << 8
        for _ in range(8):
            value = ((value << 1) ^ 0x1021) & 0xFFFF if value & 0x8000 else (value << 1) & 0xFFFF
    return value


def read_request(parameter_id: int, sequence: int) -> bytes:
    if parameter_id not in (27, 28) or not 0 < sequence <= 0xFFFF:
        raise ProtocolError("read request denied")
    return struct.pack("<BBBBBHBH", 4, 0, 8, 5, 5, sequence, 2, parameter_id)


class ReadReply:
    def __init__(self, sequence: int):
        self.sequence = sequence
        self.inner = bytearray()
        self.completed = False

    def add(self, packet: bytes) -> bytes | None:
        if self.completed or not 5 <= len(packet) <= 1024 or packet[:4] != b"\x03\x00\x05\x08":
            raise ProtocolError("invalid read reply frame")
        length = packet[4] or 255
        if len(packet) < 5 + length or len(self.inner) + length > 603:
            raise ProtocolError("invalid read reply length")
        self.inner.extend(packet[5:5 + length])
        if packet[4] == 0:
            return None
        self.completed = True
        if len(self.inner) < 3 or struct.unpack_from("<H", self.inner)[0] != self.sequence:
            raise ProtocolError("read reply sequence mismatch")
        if self.inner[2] != 0x82:
            raise ProtocolError("read reply type mismatch")
        return bytes(self.inner[3:])


def shell_request(command: str, tag: int) -> bytes:
    try:
        encoded = command.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ProtocolError("shell command must be ASCII") from exc
    if not encoded or len(encoded) > 231 or "\0" in command:
        raise ProtocolError("shell command length is outside the reviewed boundary")
    if any(byte < 32 or byte > 126 for byte in encoded):
        raise ProtocolError("shell command contains an unreviewed character")
    packet = bytearray(257)
    packet[:5] = b"\x0a\x00\x08\x05\xfc"
    struct.pack_into("<I", packet, 5, 65)
    struct.pack_into("<I", packet, 13, tag)
    packet[25:25 + len(encoded)] = encoded
    struct.pack_into("<I", packet, 17, crc_hqx(packet[21:257]))
    return bytes(packet)


def shell_reply(packet: bytes, tag: int) -> tuple[bool, bytes]:
    if len(packet) not in (260, 1024) or packet[:5] != b"\x09\x00\x05\x08\xfc":
        raise ProtocolError("invalid shell reply frame")
    if struct.unpack_from("<I", packet, 5)[0] != 65 or struct.unpack_from("<I", packet, 13)[0] != tag:
        raise ProtocolError("shell reply header mismatch")
    if struct.unpack_from("<I", packet, 17)[0] != crc_hqx(packet[21:257]):
        raise ProtocolError("shell reply CRC mismatch")
    function = struct.unpack_from("<I", packet, 9)[0]
    if function not in (0, 4) or struct.unpack_from("<I", packet, 21)[0] != 0:
        raise ProtocolError("remote shell command failed")
    payload = packet[25:257].split(b"\0", 1)[0]
    if any(byte not in (9, 10, 13) and not 32 <= byte <= 126 for byte in payload):
        raise ProtocolError("shell output is not reviewed ASCII")
    return function == 0, payload


def validate_snapshot(firmware: bytes, running: bytes) -> dict:
    firmware_text = firmware.decode("ascii", "strict")
    running_text = running.decode("ascii", "strict")
    if not re.fullmatch(r"S\d+,v?\d+(?:\.\d+){1,4}", firmware_text):
        raise ProtocolError("unrecognized firmware reply")
    if firmware_text not in ("S5,4.2.0", "S6,v4.2.0"):
        raise ProtocolError("unsupported camera protocol version")
    if running_text != "i1":
        raise ProtocolError("camera service is not running")
    return {"protocol": firmware_text, "camera_running": True}

