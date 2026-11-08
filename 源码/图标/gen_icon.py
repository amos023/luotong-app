"""由母版图标生成 5 档密度资源。

母版：本脚本同目录下的 ic_launcher_master_512.png（512×512）
      （若放在 res/ 子目录里也能自动找到）
5 档全部由这一张 LANCZOS 缩小得到，保证各密度都是原始细节，不做放大。

输出到 res/mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher.png，
与 res_table.py 里的密度列表一一对应。

路径均相对本脚本定位，避免换机器或换工作目录后失效。
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = HERE

# 母版可能在脚本同目录，也可能在同目录的 res/ 下
_CANDIDATES = [
    os.path.join(HERE, "ic_launcher_master_512.png"),
    os.path.join(HERE, "res", "ic_launcher_master_512.png"),
]
SRC = next((p for p in _CANDIDATES if os.path.exists(p)), _CANDIDATES[0])

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
