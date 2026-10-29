#!/usr/bin/env python3
"""
MT7920 firmware embedder for SimpleMtkWlan.

Usage (run on the PC where you downloaded the firmware files):
  python3 embed_mt7920_fw.py WIFI_RAM_CODE_MT7961_1a.bin WIFI_MT7961_patch_mcu_1a_2_hdr.bin path/to/include/FwBinary.cpp

Takes the two linux-firmware blobs (mediatek/ folder) and adds them to
include/FwBinary.cpp as C arrays, plus the fwList entries that
MtkMwx.cpp looks up by name:
  "mwx-mt7961_ram_code_1a"           (MT7920_FIRMWARE_WM)
  "mwx-mt7961_patch_mcu_1a_2_hdr"    (MT7920_ROM_PATCH)
The script edits the file in place and keeps a .bak copy.
"""
import re
import sys
import pathlib

RAM_NAME = "mwx-mt7961_ram_code_1a"
PATCH_NAME = "mwx-mt7961_patch_mcu_1a_2_hdr"
RAM_SYM = "mwx_mt7961_ram_code_1a"
PATCH_SYM = "mwx_mt7961_patch_mcu_1a_2_hdr"


def c_array(sym, data):
    lines = []
    for i in range(0, len(data), 12):
        chunk = data[i:i + 12]
        lines.append("  " + ", ".join("0x%02x" % b for b in chunk) + ",")
    body = "\n".join(lines)
    return (f"unsigned char {sym}[] = {{\n{body}\n}};\n"
            f"unsigned int {sym}_len = {len(data)};\n\n")


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    ram = pathlib.Path(sys.argv[1]).read_bytes()
    patch = pathlib.Path(sys.argv[2]).read_bytes()
    fw_path = pathlib.Path(sys.argv[3])
    src = fw_path.read_text(encoding="utf-8", errors="surrogateescape")

    if RAM_NAME in src or PATCH_NAME in src:
        sys.exit("FwBinary.cpp already contains MT7920 firmware. Nothing changed.")

    anchor = "const struct FwDesc fwList[] = {\n"
    if src.count(anchor) != 1:
        sys.exit("Could not find fwList anchor exactly once.")

    arrays = c_array(RAM_SYM, ram) + c_array(PATCH_SYM, patch)
    src = src.replace(anchor, arrays + anchor, 1)

    entries = (
        f'    {{MTK_FW_DESC("{PATCH_NAME}", {PATCH_SYM}, (int){PATCH_SYM}_len)}},\n'
        f'    {{MTK_FW_DESC("{RAM_NAME}", {RAM_SYM}, (int){RAM_SYM}_len)}},\n'
    )
    src = src.replace(anchor, anchor + entries, 1)

    # Update fwNumber to the real number of fwList entries.
    start = src.index("const struct FwDesc fwList[] = {")
    end = src.index("};", start)
    count = src[start:end].count("MTK_FW_DESC(")
    src, n = re.subn(r"const int fwNumber = \d+;", f"const int fwNumber = {count};", src)
    if n != 1:
        sys.exit("Could not find fwNumber exactly once.")

    backup = fw_path.with_suffix(fw_path.suffix + ".bak")
    backup.write_bytes(fw_path.read_bytes())
    fw_path.write_text(src, encoding="utf-8", errors="surrogateescape")
    print(f"OK: added {RAM_NAME} ({len(ram)} bytes) and {PATCH_NAME} ({len(patch)} bytes).")
    print(f"fwNumber set to {count}. Backup: {backup}")


if __name__ == "__main__":
    main()
