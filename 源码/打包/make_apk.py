#!/usr/bin/env python3
"""本地打包：不用 Gradle / aapt2，直接拼 APK。

组成：二进制清单 + classes.dex + resources.arsc（多密度图标资源表）+ assets/index.html。
resources.arsc 按 Android 11+ 要求「不压缩 + 4 字节对齐」，
对齐用一条 res/raw/pad.bin 占位项微调，反复构建直到偏移满足要求。
"""
import os
import struct
import sys
import zipfile

sys.path.insert(0, "/tmp/apk")
from axmlwrite import build_manifest  # noqa: E402

ROOT = "/tmp/apk"
OUT = os.path.join(ROOT, "out")
APK = os.path.join(OUT, "落筒录入.apk")

PKG = "io.github.mcool.luotong"
VERSION_CODE = 40
VERSION_NAME = "1.40"
LABEL = "落筒录入"
ACTIVITY = "io.github.mcool.luotong.MainActivity"
ICON_RID = 0x7F010000

DENSITIES = ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]
PAD_NAME = "res/raw/pad.bin"


def icon_entries():
    """返回 [(zip 内路径, 字节)]，按密度顺序，与 resources.arsc 里全局池顺序一致。"""
    out = []
    for d in DENSITIES:
        path = os.path.join(OUT, "res", "mipmap-" + d, "ic_launcher.png")
        out.append(("res/mipmap-%s/ic_launcher.png" % d, open(path, "rb").read()))
    return out


def data_offset(zf_path, entry_name):
    with zipfile.ZipFile(zf_path) as z:
        info = z.getinfo(entry_name)
    with open(zf_path, "rb") as f:
        f.seek(info.header_offset)
        hdr = f.read(30)
        nlen, elen = struct.unpack_from("<HH", hdr, 26)
    return info.header_offset + 30 + nlen + elen


def assemble(manifest, dex, html, arsc, icons, pad_size):
    with zipfile.ZipFile(APK, "w") as z:
        for name, data in icons:
            z.writestr(zipfile.ZipInfo(name), data, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo(PAD_NAME), b"\x00" * pad_size, compress_type=zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("resources.arsc"), arsc, compress_type=zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("AndroidManifest.xml"), manifest, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("classes.dex"), dex, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("assets/index.html"), html, compress_type=zipfile.ZIP_DEFLATED)


def main():
    manifest = build_manifest(PKG, VERSION_CODE, VERSION_NAME, LABEL, ACTIVITY, icon_rid=ICON_RID)
    dex = open(os.path.join(OUT, "dex", "classes.dex"), "rb").read()
    html = open(os.path.join(ROOT, "assets", "index.html"), "rb").read()
    arsc = open(os.path.join(OUT, "resources.arsc"), "rb").read()
    icons = icon_entries()

    pad = 0
    for _ in range(8):
        assemble(manifest, dex, html, arsc, icons, pad)
        off = data_offset(APK, "resources.arsc")
        if off % 4 == 0:
            break
        pad += 4 - (off % 4)
    else:
        raise SystemExit("对齐失败")

    off = data_offset(APK, "resources.arsc")
    print("apk:", APK, os.path.getsize(APK), "bytes")
    print("resources.arsc data offset:", off, "(4 字节对齐:", off % 4 == 0, ")")
    with zipfile.ZipFile(APK) as z:
        for i in z.infolist():
            print("  %-38s %8d -> %8d" % (i.filename, i.file_size, i.compress_size))
        print("  testzip:", z.testzip())


if __name__ == "__main__":
    main()
