#!/usr/bin/env python3
"""本地打包：不用 Gradle / aapt2，直接拼 APK。

组成：二进制清单 + classes.dex + resources.arsc（图标资源表）+ assets/index.html。
resources.arsc 按 Android 11+ 的要求「不压缩 + 4 字节对齐」，
对齐用一条 res/raw/pad.bin 占位项做微调，反复构建直到偏移满足要求。
"""
import os
import struct
import sys
import zipfile

sys.path.insert(0, "/workspace/临时/apkbuild")
from axmlwrite import build_manifest  # noqa: E402

ROOT = "/workspace/项目/落筒录入APK"
OUT = os.path.join(ROOT, "out")
APK = os.path.join(OUT, "落筒录入_v1.89.apk")

PKG = "io.github.mcool.luotong"
VERSION_CODE = 189
VERSION_NAME = "1.89"
LABEL = "落筒录入"
ACTIVITY = "io.github.mcool.luotong.MainActivity"
ICON_RID = 0x7F010000

ICON_PATH = "res/mipmap-xhdpi/ic_launcher.png"
PAD_NAME = "res/raw/pad.bin"


def data_offset(zf_path, entry_name):
    with zipfile.ZipFile(zf_path) as z:
        info = z.getinfo(entry_name)
    with open(zf_path, "rb") as f:
        f.seek(info.header_offset)
        hdr = f.read(30)
        nlen, elen = struct.unpack_from("<HH", hdr, 26)
    return info.header_offset + 30 + nlen + elen


def assemble(manifest, dex, html, arsc, icon, pad_size):
    with zipfile.ZipFile(APK, "w") as z:
        z.writestr(zipfile.ZipInfo(ICON_PATH), icon, compress_type=zipfile.ZIP_DEFLATED)
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
    icon = open(os.path.join(OUT, ICON_PATH), "rb").read()

    pad = 0
    for _ in range(8):
        assemble(manifest, dex, html, arsc, icon, pad)
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
            print("  %-34s %8d -> %8d" % (i.filename, i.file_size, i.compress_size))
        print("  testzip:", z.testzip())


if __name__ == "__main__":
    main()
