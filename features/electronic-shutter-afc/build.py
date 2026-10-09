"""Build the standalone electronic-shutter AF-C package for X2D II 1.3.16.2."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import re
import shutil
import struct
import subprocess
import zlib

from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
SERVICE_SHA = "51b9e02f8bfebf388be8dfa163c8e512bee19aeb8ae37a6712727ccc6f26a52d"
GUI_SHA = "b1b643cb36176cd5a49129dd9bb2be480aa045a96ed1c35c30a779ab5af0801b"
TARGETS = (
    "controlscreen/ControlScreenViewModel.qml",
    "viewmodels/LiveviewViewModel.qml",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trim_line_comments(text):
    assert "`" not in text and not re.search(r"(?:\(|=|return)\s*/(?![/*])", text)
    out, quote, block, i = [], None, False, 0
    while i < len(text):
        ch, pair = text[i], text[i:i + 2]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < len(text):
                out.append(text[i + 1]); i += 2; continue
            if ch == quote: quote = None
        elif block:
            if pair == "*/": out.extend(pair); block = False; i += 2; continue
            out.append(ch)
        elif pair == "/*": out.extend(pair); block = True; i += 2; continue
        elif pair == "//":
            end = text.find("\n", i); i = len(text) if end < 0 else end; continue
        else:
            out.append(ch)
            if ch in ('"', "'"): quote = ch
        i += 1
    assert not quote and not block
    return "".join(out)


def qml_resources(gui):
    with gui.open("rb") as stream:
        elf = ELFFile(stream)
        groups, group = [], {}
        for symbol in elf.get_section_by_name(".symtab").iter_symbols():
            if symbol["st_info"]["type"] == "STT_FILE":
                if group: groups.append(group)
                group = {"unit": symbol.name}
            if symbol.name in ("_ZL16qt_resource_data", "_ZL16qt_resource_name", "_ZL18qt_resource_struct"):
                group[symbol.name] = symbol
        if group: groups.append(group)
        group = next(g for g in groups if g.get("unit") == "qrc_camera-gui_raw_qml_0.cpp")

        def section_bytes(key):
            symbol = group[key]
            section = elf.get_section(symbol["st_shndx"])
            offset = symbol["st_value"] - section["sh_addr"]
            return section.data()[offset:offset + symbol["st_size"]], section["sh_offset"] + offset

        payload, payload_file_offset = section_bytes("_ZL16qt_resource_data")
        names, _ = section_bytes("_ZL16qt_resource_name")
        tree, _ = section_bytes("_ZL18qt_resource_struct")
        found = {}

        def walk(node, parent):
            name_offset, flags = struct.unpack_from(">IH", tree, node * 22)
            length = struct.unpack_from(">H", names, name_offset)[0]
            name = names[name_offset + 6:name_offset + 6 + length * 2].decode("utf-16-be") if node else ""
            path = parent + "/" + name if name else parent
            if flags & 2:
                count, first = struct.unpack_from(">II", tree, node * 22 + 6)
                for child in range(first, first + count): walk(child, path)
            elif any(path.endswith("/" + wanted) for wanted in TARGETS):
                start = struct.unpack_from(">I", tree, node * 22 + 10)[0]
                size = struct.unpack_from(">I", payload, start)[0]
                found[next(w for w in TARGETS if path.endswith("/" + w))] = (
                    payload_file_offset + start + 4, size, flags
                )

        walk(0, "")
        assert set(found) == set(TARGETS), found
        return found


def patch_gui(source, destination):
    original = source.read_bytes()
    image = bytearray(original)
    changes = []
    for relative, (offset, size, flags) in qml_resources(source).items():
        blob = original[offset:offset + size]
        raw = zlib.decompress(blob[4:]) if flags & 1 else blob
        text = raw.decode("utf-8")
        assert text.count("valid: CameraUI.canChangeAfc") == 1
        allow = "(CameraUI.canChangeAfc || (root.eShutter && CameraUI.supportAfc && root.driveMode === HblmTypes.E_DriveModes_Single))"
        text = text.replace("valid: CameraUI.canChangeAfc", "valid: " + allow, 1)
        if relative.startswith("controlscreen/"):
            pattern = (r'}\s*else if \(root\.eShutter\) \{\s*'
                       r'return qsTranslate\("AfcBlocked", "AF-C not supported by electronic shutter"\)\s*'
                       r'}\s*else if \(root\.driveMode === HblmTypes\.E_DriveModes_SelfTimer\) \{')
            text, count = re.subn(pattern, '} else if (root.driveMode === HblmTypes.E_DriveModes_SelfTimer) {', text, count=1)
            assert count == 1
        compact = "\n".join(line.lstrip() for line in trim_line_comments(text).splitlines() if line.strip()) + "\n"
        output = compact.encode("utf-8")
        encoded = struct.pack(">I", len(output)) + zlib.compress(output, 9) if flags & 1 else output
        if len(encoded) > size:
            raise ValueError(f"patched resource exceeds fixed capacity: {relative}")
        encoded += (b"\0" if flags & 1 else b" ") * (size - len(encoded))
        image[offset:offset + size] = encoded
        changes.append({"resource": relative, "offset": offset, "size": size,
                        "sha256": hashlib.sha256(encoded).hexdigest()})
    destination.write_bytes(image)
    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera-service", required=True, type=Path)
    parser.add_argument("--camera-gui", required=True, type=Path)
    parser.add_argument("--ndk", required=True, type=Path,
                        help="Android NDK r27 root")
    parser.add_argument("--out", type=Path, default=HERE / "output")
    args = parser.parse_args()
    if sha(args.camera_service) != SERVICE_SHA or sha(args.camera_gui) != GUI_SHA:
        raise SystemExit("Only pristine X2D II 100C firmware 1.3.16.2 inputs are accepted")
    firmware = args.camera_service.read_bytes()
    assert firmware[0x1d0f60:0x1d0f64] == struct.pack("<I", 0x37000160)
    assert struct.unpack_from("<Q", firmware, 0x8bfa30 - 0x1000 + 0x2b0)[0] == 0x1e4658

    output = args.out.resolve()
    if output == HERE or HERE in output.parents and output.name in {"src", "prebuilt"}:
        raise SystemExit("refusing to replace a source or prebuilt directory")
    if output.parent == output:
        raise SystemExit("refusing to use a filesystem root as output")
    if output.exists(): shutil.rmtree(output)
    payload = output / "payload"
    payload.mkdir(parents=True)
    clang = args.ndk / "toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe"
    library = payload / "afc-electronic.so"
    subprocess.run([str(clang), "--target=aarch64-linux-android28", "-std=c11", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-fPIC", "-shared", "-s",
                    "-Wl,-z,noexecstack", "-Wl,-z,relro", "-Wl,-z,now",
                    str(HERE / "src/afc_eshutter.c"), "-ldl", "-o", str(library)], check=True)
    elf = ELFFile(io.BytesIO(library.read_bytes()))
    assert elf["e_machine"] == "EM_AARCH64"
    assert not any((segment["p_flags"] & 3) == 3 for segment in elf.iter_segments())
    imports = sorted(s.name for s in elf.get_section_by_name(".dynsym").iter_symbols()
                     if s.name and s["st_shndx"] == "SHN_UNDEF")
    allowed = {"__cxa_atexit", "__cxa_finalize", "__register_atfork", "__stack_chk_fail",
               "close", "dl_iterate_phdr", "getpid", "mprotect", "open", "readlink",
               "snprintf", "write"}
    assert set(imports) <= allowed, imports
    gui = payload / "camera-gui"
    changes = patch_gui(args.camera_gui, gui)
    (payload / "camera-service.env").write_text(
        "LD_PRELOAD=/system/lib64/libx2d2-afc-electronic.so\n", encoding="ascii")
    manifest = {
        "package": "x2d2-electronic-shutter-afc",
        "version": "1.0.0",
        "firmware": "X2D II 100C 1.3.16.2",
        "factory": {"camera-service": SERVICE_SHA, "camera-gui": GUI_SHA},
        "payload": {p.name: sha(p) for p in sorted(payload.iterdir())},
        "ui_changes": changes,
        "independent_of_pixel_shift": True,
        "passed": True,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    shutil.copy2(HERE / "README.md", output / "README.md")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
