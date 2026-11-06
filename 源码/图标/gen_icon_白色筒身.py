"""生成应用图标：深蓝渐变圆角底 + 白色筒身与卷线，尺寸按密度输出。"""
import os
from PIL import Image, ImageDraw

OUT_DIR = "/workspace/项目/落筒录入APK/out/res/mipmap-xhdpi"
SIZE = 192  # mipmap-xhdpi 的常规尺寸

BG_TOP = (58, 141, 255)
BG_BOTTOM = (13, 99, 214)
WHITE = (255, 255, 255, 255)
SOFT = (255, 255, 255, 60)


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

    # 竖向渐变底
    grad = Image.new("RGB", (1, SIZE))
    for y in range(SIZE):
        t = y / (SIZE - 1)
        grad.putpixel((0, y), (
            int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t),
            int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t),
            int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t),
        ))
    grad = grad.resize((SIZE, SIZE))
    img.paste(grad, (0, 0))
    img.putalpha(rounded_mask(SIZE, int(SIZE * 0.22)))

    d = ImageDraw.Draw(img)

    # 筒身（竖直圆角矩形）
    tube_w = int(SIZE * 0.42)
    tube_h = int(SIZE * 0.50)
    x0 = (SIZE - tube_w) // 2
    y0 = int(SIZE * 0.26)
    d.rounded_rectangle(
        [x0, y0, x0 + tube_w, y0 + tube_h],
        radius=int(tube_w * 0.22), outline=WHITE, width=max(6, SIZE // 22)
    )

    # 上下两端封口线
    lw = max(5, SIZE // 26)
    d.line([x0 + 4, y0 + int(tube_h * 0.22), x0 + tube_w - 4, y0 + int(tube_h * 0.22)], fill=WHITE, width=lw)
    d.line([x0 + 4, y0 + int(tube_h * 0.78), x0 + tube_w - 4, y0 + int(tube_h * 0.78)], fill=WHITE, width=lw)

    # 中段缠绕的纱线（三条横线，中间那条更短，形成层次）
    cx = SIZE // 2
    for i, ratio in enumerate((0.44, 0.50, 0.56)):
        half = int(tube_w * (0.34 if i == 1 else 0.26))
        yy = y0 + int(tube_h * ratio)
        d.line([cx - half, yy, cx + half, yy], fill=WHITE, width=max(5, SIZE // 30))

    # 落下的单根丝线
    d.line([cx, y0 + tube_h, cx, int(SIZE * 0.86)], fill=WHITE, width=max(5, SIZE // 30))

    path = os.path.join(OUT_DIR, "ic_launcher.png")
    img.save(path, "PNG")
    print("icon:", path, os.path.getsize(path), "bytes", img.size)


if __name__ == "__main__":
    main()
