"""用用户指定的母版图标生成 5 档密度资源。

母版：/storage/emulated/0/共享目录/代码/图标方案2/icon2_512.png（512×512）
5 档全部由这一张 LANCZOS 缩小得到，保证各密度都是原始细节，不做放大。
"""
import os

from PIL import Image

SRC = "/storage/emulated/0/共享目录/代码/图标方案2/icon2_512.png"
OUT_DIR = "/tmp/apk/res"

DENSITIES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}


def main():
    src = Image.open(SRC).convert("RGBA")
    print("母版:", SRC, src.size)

    for name, px in DENSITIES.items():
        folder = os.path.join(OUT_DIR, "mipmap-" + name)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "ic_launcher.png")
        if src.size[0] == px:
            out = src.copy()
        else:
            out = src.resize((px, px), Image.LANCZOS)
        out.save(path, "PNG", optimize=True)
        print("%-9s %3dpx  %6d bytes" % (name, px, os.path.getsize(path)))


if __name__ == "__main__":
    main()
