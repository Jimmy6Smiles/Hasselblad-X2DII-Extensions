"""Bounded WinUSB transport for the X2D II official Phocus interface.

Importing this module never enumerates or opens a device.  Call ``snapshot``
explicitly; it performs two read-only protocol requests and closes the handle.
"""
from __future__ import annotations

import ctypes
import os
from ctypes import wintypes

from .protocol import ReadReply, ProtocolError, read_request, shell_reply, shell_request, validate_snapshot

INTERFACE_GUID_TEXT = "CC135687-5267-4313-B0C7-C344609D6EF0"
DEVICE_PREFIX = r"\\?\usb#vid_2756&pid_000b&mi_04#"
ERROR_NO_MORE_ITEMS = 259
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class UsbError(RuntimeError):
    def __init__(self, code: str, win32: int = 0):
        super().__init__(f"{code}" + (f" (Win32 {win32})" if win32 else ""))
        self.code, self.win32 = code, win32


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD),
                ("Data4", ctypes.c_ubyte * 8)]

    @classmethod
    def parse(cls, value: str):
        import uuid
        raw = uuid.UUID(value).bytes_le
        result = cls()
        result.Data1, result.Data2, result.Data3 = int.from_bytes(raw[:4], "little"), int.from_bytes(raw[4:6], "little"), int.from_bytes(raw[6:8], "little")
        result.Data4[:] = raw[8:]
        return result


class InterfaceData(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("InterfaceClassGuid", GUID),
                ("Flags", wintypes.DWORD), ("Reserved", ctypes.c_void_p)]


class UsbInterface(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("Length", ctypes.c_ubyte), ("DescriptorType", ctypes.c_ubyte),
                ("Number", ctypes.c_ubyte), ("Alternate", ctypes.c_ubyte),
                ("EndpointCount", ctypes.c_ubyte), ("Class", ctypes.c_ubyte),
                ("Subclass", ctypes.c_ubyte), ("Protocol", ctypes.c_ubyte),
                ("StringIndex", ctypes.c_ubyte)]


class PipeInfo(ctypes.Structure):
    _fields_ = [("Type", ctypes.c_int), ("Id", ctypes.c_ubyte),
                ("PacketSize", wintypes.WORD), ("Interval", ctypes.c_ubyte)]


class WinUsbSession:
    def __init__(self):
        if os.name != "nt":
            raise UsbError("WINDOWS_REQUIRED")
        self.setupapi = ctypes.WinDLL("setupapi", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.winusb = ctypes.WinDLL("winusb", use_last_error=True)
        self.file = None
        self.usb = ctypes.c_void_p()
        self.pipe_in = self.pipe_out = 0
        self._declare()

    def _declare(self):
        self.setupapi.SetupDiGetClassDevsW.argtypes = [ctypes.POINTER(GUID), wintypes.LPCWSTR, wintypes.HWND, wintypes.DWORD]
        self.setupapi.SetupDiGetClassDevsW.restype = ctypes.c_void_p
        self.setupapi.SetupDiEnumDeviceInterfaces.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(GUID), wintypes.DWORD, ctypes.POINTER(InterfaceData)]
        self.setupapi.SetupDiEnumDeviceInterfaces.restype = wintypes.BOOL
        self.setupapi.SetupDiGetDeviceInterfaceDetailW.argtypes = [ctypes.c_void_p, ctypes.POINTER(InterfaceData), ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        self.setupapi.SetupDiGetDeviceInterfaceDetailW.restype = wintypes.BOOL
        self.setupapi.SetupDiDestroyDeviceInfoList.argtypes = [ctypes.c_void_p]
        self.setupapi.SetupDiDestroyDeviceInfoList.restype = wintypes.BOOL
        self.kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self.kernel32.CreateFileW.restype = wintypes.HANDLE
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL
        self.winusb.WinUsb_Initialize.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p)]
        self.winusb.WinUsb_Initialize.restype = wintypes.BOOL
        self.winusb.WinUsb_Free.argtypes = [ctypes.c_void_p]
        self.winusb.WinUsb_Free.restype = wintypes.BOOL
        self.winusb.WinUsb_QueryInterfaceSettings.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.POINTER(UsbInterface)]
        self.winusb.WinUsb_QueryInterfaceSettings.restype = wintypes.BOOL
        self.winusb.WinUsb_QueryPipe.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.POINTER(PipeInfo)]
        self.winusb.WinUsb_QueryPipe.restype = wintypes.BOOL
        self.winusb.WinUsb_SetPipePolicy.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
        self.winusb.WinUsb_SetPipePolicy.restype = wintypes.BOOL
        self.winusb.WinUsb_WritePipe.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        self.winusb.WinUsb_WritePipe.restype = wintypes.BOOL
        self.winusb.WinUsb_ReadPipe.argtypes = self.winusb.WinUsb_WritePipe.argtypes
        self.winusb.WinUsb_ReadPipe.restype = wintypes.BOOL

    @staticmethod
    def _check(ok, code):
        if not ok:
            raise UsbError(code, ctypes.get_last_error())

    def _set_read_timeout(self, milliseconds: int):
        timeout = wintypes.DWORD(milliseconds)
        self._check(self.winusb.WinUsb_SetPipePolicy(
            self.usb, self.pipe_in, 3, 4, ctypes.byref(timeout)), "USB_TIMEOUT_POLICY")

    def _discard_stale_replies(self):
        """Clear only replies left by a previously timed-out host process."""
        self._set_read_timeout(50)
        try:
            for _ in range(64):
                try:
                    self._read()
                except UsbError as error:
                    if error.win32 == 121:
                        return
                    raise
            raise UsbError("USB_STALE_REPLY_LIMIT")
        finally:
            self._set_read_timeout(10000)

    def _enumerate(self) -> list[str]:
        guid = GUID.parse(INTERFACE_GUID_TEXT)
        device_set = self.setupapi.SetupDiGetClassDevsW(ctypes.byref(guid), None, None, 0x12)
        if device_set == INVALID_HANDLE_VALUE:
            raise UsbError("USB_ENUMERATE", ctypes.get_last_error())
        paths = []
        try:
            for index in range(128):
                item = InterfaceData(cbSize=ctypes.sizeof(InterfaceData))
                if not self.setupapi.SetupDiEnumDeviceInterfaces(device_set, None, ctypes.byref(guid), index, ctypes.byref(item)):
                    error = ctypes.get_last_error()
                    if error == ERROR_NO_MORE_ITEMS: break
                    raise UsbError("USB_ENUMERATE", error)
                required = wintypes.DWORD()
                self.setupapi.SetupDiGetDeviceInterfaceDetailW(device_set, ctypes.byref(item), None, 0, ctypes.byref(required), None)
                if not 8 <= required.value <= 4096:
                    raise UsbError("USB_ENUMERATE_SIZE")
                detail = ctypes.create_string_buffer(required.value)
                ctypes.c_ulong.from_buffer(detail).value = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
                self._check(self.setupapi.SetupDiGetDeviceInterfaceDetailW(device_set, ctypes.byref(item), detail, required, ctypes.byref(required), None), "USB_ENUMERATE")
                path = ctypes.wstring_at(ctypes.addressof(detail) + 4)
                lower = path.lower()
                if lower.startswith(DEVICE_PREFIX) and lower.endswith("#{" + INTERFACE_GUID_TEXT.lower() + "}"):
                    paths.append(path)
        finally:
            self.setupapi.SetupDiDestroyDeviceInfoList(device_set)
        return paths

    def open(self):
        try:
            paths = self._enumerate()
            if not paths: raise UsbError("USB_NOT_PRESENT")
            if len(paths) != 1: raise UsbError("USB_AMBIGUOUS")
            self.file = self.kernel32.CreateFileW(paths[0], 0xC0000000, 3, None, 3, 0x40000080, None)
            if self.file == INVALID_HANDLE_VALUE:
                self.file = None
                raise UsbError("USB_OPEN", ctypes.get_last_error())
            self._check(self.winusb.WinUsb_Initialize(self.file, ctypes.byref(self.usb)), "USB_INITIALIZE")
            descriptor = UsbInterface()
            self._check(self.winusb.WinUsb_QueryInterfaceSettings(self.usb, 0, ctypes.byref(descriptor)), "USB_INTERFACE")
            if (descriptor.Number, descriptor.Alternate, descriptor.Class, descriptor.Subclass, descriptor.Protocol, descriptor.EndpointCount) != (4, 0, 255, 0, 0, 4):
                raise UsbError("USB_INTERFACE_MISMATCH")
            order = []
            for index in range(4):
                pipe = PipeInfo()
                self._check(self.winusb.WinUsb_QueryPipe(self.usb, 0, index, ctypes.byref(pipe)), "USB_PIPE")
                if pipe.Type != 2: raise UsbError("USB_PIPE_MISMATCH")
                order.append(pipe.Id)
            if len(set(order)) != 4 or any((pipe & 0x0F) == 0 for pipe in order) or any(bool(order[i] & 0x80) != (i >= 2) for i in range(4)):
                raise UsbError("USB_PIPE_MISMATCH")
            self.pipe_in, self.pipe_out = order[3], order[1]
            # Device-side file and mount operations can legitimately take
            # longer than a parameter read. Keep the request count bounded,
            # but allow one slow flash operation to return its framed reply.
            self._set_read_timeout(10000)
            timeout = wintypes.DWORD(10000)
            self._check(self.winusb.WinUsb_SetPipePolicy(self.usb, self.pipe_out, 3, 4, ctypes.byref(timeout)), "USB_TIMEOUT_POLICY")
            self._discard_stale_replies()
            return self
        except Exception:
            self.close()
            raise

    def _write(self, pipe, data: bytes):
        buffer = ctypes.create_string_buffer(data)
        transferred = wintypes.DWORD()
        self._check(self.winusb.WinUsb_WritePipe(self.usb, pipe, buffer, len(data), ctypes.byref(transferred), None), "USB_WRITE")
        if transferred.value != len(data): raise UsbError("USB_SHORT_WRITE")

    def _read(self) -> bytes:
        buffer = ctypes.create_string_buffer(1024)
        transferred = wintypes.DWORD()
        self._check(self.winusb.WinUsb_ReadPipe(self.usb, self.pipe_in, buffer, 1024, ctypes.byref(transferred), None), "USB_READ")
        return buffer.raw[:transferred.value]

    def read_parameter(self, parameter_id: int, sequence: int) -> bytes:
        self._write(self.pipe_out, read_request(parameter_id, sequence))
        reply = ReadReply(sequence)
        timeouts = 0
        for _ in range(8):
            try:
                packet = self._read()
            except UsbError as error:
                if error.win32 == 121 and timeouts < 2:
                    timeouts += 1
                    continue
                raise
            value = reply.add(packet)
            if value is not None: return value
        raise UsbError("USB_REPLY_LIMIT")

    def shell(self, command: str, tag: int) -> str:
        """Run one internally generated command; callers must not accept raw user text."""
        self._write(self.pipe_out, shell_request(command, tag))
        output = bytearray()
        timeouts = 0
        for _ in range(68):
            try:
                packet = self._read()
            except UsbError as error:
                if error.win32 == 121 and timeouts < 3:
                    timeouts += 1
                    continue
                raise
            complete, payload = shell_reply(packet, tag)
            output.extend(payload)
            if len(output) > 8192: raise UsbError("SHELL_OUTPUT_LIMIT")
            if complete: return output.decode("ascii")
        raise UsbError("SHELL_FRAME_LIMIT")

    def close(self):
        if self.usb.value:
            self.winusb.WinUsb_Free(self.usb)
            self.usb = ctypes.c_void_p()
        if self.file not in (None, INVALID_HANDLE_VALUE):
            self.kernel32.CloseHandle(self.file)
            self.file = None

    def __enter__(self): return self.open()
    def __exit__(self, *_): self.close()


def snapshot() -> dict:
    with WinUsbSession() as session:
        return validate_snapshot(session.read_parameter(27, 1), session.read_parameter(28, 2))
