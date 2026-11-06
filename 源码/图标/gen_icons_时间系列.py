"""第二套图标：以「时间 / 计算」为主视觉，筒只是配角。"""
import os
from PIL import Image, ImageDraw

S = 512
PREVIEW = 192
OUT = "/workspace/临时/icons2"

BLUE = (22, 119, 255)
DEEP = (13, 71, 161)
INK = (23, 32, 46)
WHITE = (255, 255, 255)


def bg(top, bottom=None, radius=0.22, fill=None):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if fill is not None:
        img.paste(Image.new("RGBA", (S, S), fill), (0, 0))
    elif bottom is None:
        img.paste(Image.new("RGBA", (S, S), top), (0, 0))
    else:
        grad = Image.new("RGB", (1, S))
        for y in range(S):
            t = y / (S - 1)
            grad.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
        img.paste(grad.resize((S, S)), (0, 0))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * radius), fill=255)
    img.putalpha(mask)
    return img


def dial(d, cx, cy, r, ring, face, tick=None, tick_w=None):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=face, outline=ring, width=tick_w or S // 26)
    if tick:
        for i in range(12):
            import math
            a = math.radians(i * 30 - 90)
            r1, r2 = r * 0.78, r * 0.90
            d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                    cx + r2 * math.cos(a), cy + r2 * math.sin(a)], fill=tick, width=S // 56)


# 1 秒表：蓝底白盘，顶部按钮
def icon1():
    img = bg((45, 132, 255), (13, 87, 214))
    d = ImageDraw.Draw(img)
    cx, cy, r = S // 2, int(S * 0.56), int(S * 0.30)
    d.rounded_rectangle([cx - S * 0.06, S * 0.14, cx + S * 0.06, S * 0.26], radius=S * 0.02, fill=WHITE)
    d.line([cx, S * 0.20, cx, S * 0.26], fill=WHITE, width=S // 34)
    dial(d, cx, cy, r, WHITE, WHITE, tick=(BLUE[0], BLUE[1], BLUE[2], 160), tick_w=S // 20)
    d.line([cx, cy, cx, cy - r * 0.62], fill=DEEP, width=S // 22)          # 分针
    d.line([cx, cy, cx + r * 0.52, cy], fill=BLUE, width=S // 26)          # 时针
    d.ellipse([cx - S * 0.022, cy - S * 0.022, cx + S * 0.022, cy + S * 0.022], fill=DEEP)
    return img


# 2 时钟 + 绕线外环
def icon2():
    img = bg(WHITE, radius=0.22)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), outline=(219, 228, 240), width=S // 64)
    cx, cy, r = S // 2, S // 2, int(S * 0.31)
    d.ellipse([cx - r * 1.28, cy - r * 1.28, cx + r * 1.28, cy + r * 1.28], outline=(198, 219, 250), width=S // 46)
    dial(d, cx, cy, r, BLUE, WHITE, tick=(120, 160, 210), tick_w=S // 22)
    d.line([cx, cy, cx, cy - r * 0.66], fill=DEEP, width=S // 22)
    d.line([cx, cy, cx + r * 0.56, cy + r * 0.2], fill=BLUE, width=S // 26)
    d.ellipse([cx - S * 0.024, cy - S * 0.024, cx + S * 0.024, cy + S * 0.024], fill=DEEP)
    return img


# 3 计算器 + 小表盘
def icon3():
    img = bg((248, 250, 253), radius=0.22)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), outline=(214, 224, 236), width=S // 64)
    # 计算器机身
    x0, y0, x1, y1 = int(S * 0.20), int(S * 0.16), int(S * 0.80), int(S * 0.86)
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(S * 0.07), fill=WHITE, outline=(203, 214, 229), width=S // 70)
    # 小表盘
    cx, cy, r = S // 2, int(S * 0.34), int(S * 0.115)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 241, 255), outline=BLUE, width=S // 40)
    d.line([cx, cy, cx, cy - r * 0.6], fill=DEEP, width=S // 34)
    d.line([cx, cy, cx + r * 0.5, cy], fill=DEEP, width=S // 38)
    # 按键
    for row in range(2):
        for col in range(3):
            bx = x0 + S * 0.045 + col * S * 0.145
            by = y0 + S * 0.30 + row * S * 0.14
            d.rounded_rectangle([bx, by, bx + S * 0.115, by + S * 0.10], radius=S * 0.02,
                                fill=(226, 236, 250) if (row, col) != (1, 2) else BLUE)
    return img


# 4 满卷进度环 + 中心筒
def icon4():
    img = bg((16, 24, 40), (10, 15, 26))
    d = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    r = int(S * 0.33)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, 270, fill=(38, 52, 74), width=int(S * 0.075))
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, 250, fill=(64, 196, 255), width=int(S * 0.075))
    w, h = int(S * 0.16), int(S * 0.24)
    d.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                        radius=int(w * 0.3), outline=WHITE, width=S // 40)
    for ratio in (0.3, 0.5, 0.7):
        yy = cy - h // 2 + int(h * ratio)
        d.line([cx - w // 2 + S * 0.012, yy, cx + w // 2 - S * 0.012, yy], fill=WHITE, width=S // 60)
    return img


# 5 沙漏 + 丝线
def icon5():
    img = bg((126, 87, 255), (49, 84, 226))
    d = ImageDraw.Draw(img)
    cx = S // 2
    top, bot = int(S * 0.24), int(S * 0.76)
    half = int(S * 0.15)
    # 上下横梁
    d.rounded_rectangle([cx - half * 1.5, top - S * 0.045, cx + half * 1.5, top], radius=S * 0.02, fill=WHITE)
    d.rounded_rectangle([cx - half * 1.5, bot, cx + half * 1.5, bot + S * 0.045], radius=S * 0.02, fill=WHITE)
    # 沙漏轮廓
    d.polygon([(cx - half, top), (cx + half, top), (cx, S // 2)], outline=WHITE, width=S // 30)
    d.polygon([(cx - half, bot), (cx + half, bot), (cx, S // 2)], outline=WHITE, width=S // 30)
    # 流下的丝线
    d.line([cx, S // 2 + S * 0.02, cx, bot - S * 0.02], fill=WHITE, width=S // 60)
    d.ellipse([cx - S * 0.03, bot - S * 0.09, cx + S * 0.03, bot - S * 0.03], fill=WHITE)
    return img


# 6 表盘 + 纺锤指针
def icon6():
    img = bg((236, 243, 253), radius=0.22)
    d = ImageDraw.Draw(img)
    cx, cy, r = S // 2, S // 2, int(S * 0.33)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE)
    d.ellipse([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], outline=(255, 255, 255, 90), width=S // 60)
    for i in range(12):
        import math
        a = math.radians(i * 30 - 90)
        r1, r2 = r * 0.80, r * 0.90
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + r2 * math.cos(a), cy + r2 * math.sin(a)], fill=(255, 255, 255, 150), width=S // 64)
    # 指针：一根粗白针 + 一根细针
    d.line([cx, cy, cx, cy - r * 0.58], fill=WHITE, width=S // 20)
    d.line([cx, cy, cx + r * 0.46, cy + r * 0.34], fill=(255, 255, 255, 220), width=S // 32)
    d.ellipse([cx - S * 0.026, cy - S * 0.026, cx + S * 0.026, cy + S * 0.026], fill=WHITE)
    return img


BUILDERS = [icon1, icon2, icon3, icon4, icon5, icon6]


def main():
    os.makedirs(OUT, exist_ok=True)
    smalls = []
    for i, fn in enumerate(BUILDERS, 1):
        img = fn()
        img.resize((PREVIEW, PREVIEW), Image.LANCZOS).save(os.path.join(OUT, f"icon{i}.png"), "PNG")
        smalls.append(img.resize((PREVIEW, PREVIEW), Image.LANCZOS).copy())

    pad, label_h = 24, 40
    cell_w, cell_h = PREVIEW + pad * 2, PREVIEW + pad * 2 + label_h
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 2), (246, 247, 249))
    d = ImageDraw.Draw(sheet)
    for idx, im in enumerate(smalls):
        col, row = idx % 3, idx // 3
        ox = col * cell_w + (cell_w - PREVIEW) // 2
        oy = row * cell_h + pad
        sheet.paste(im, (ox, oy), im)
        label = str(idx + 1)
        bb = d.textbbox((0, 0), label)
        d.text((ox + (PREVIEW - (bb[2] - bb[0])) // 2, oy + PREVIEW + 10), label, fill=(70, 78, 90))
    sheet.save(os.path.join(OUT, "icons_compare.png"), "PNG")
    print("sheet:", os.path.getsize(os.path.join(OUT, "icons_compare.png")), "bytes")


if __name__ == "__main__":
    main()
