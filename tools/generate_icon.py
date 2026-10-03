#!/usr/bin/env python3
"""
generate_icon.py - 生成 KDAP 图标（Kindle 轮廓 + 画笔）
用法: python3 generate_icon.py
"""
from PIL import Image, ImageDraw

ICON_PATH = "/mnt/us/kdap/icons/kdap_icon.png"


def generate_kdap_icon(path=ICON_PATH, size=200):
    img = Image.new("L", (size, size), color=255)
    d = ImageDraw.Draw(img)

    margin = 15
    body = size - margin * 2

    # Kindle 机身（圆角矩形）
    d.rounded_rectangle([margin, margin, margin + body, margin + body],
                        radius=18, outline=0, width=3, fill=255)

    # 屏幕
    sx, sy = margin + 18, margin + 25
    sw, sh = body - 36, int(body * 0.65)
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh],
                        radius=6, outline=0, width=2, fill=245)

    # 屏幕内：画布内容（模拟线条）
    d.line([sx + 15, sy + 20, sx + sw - 15, sy + sh - 20], fill=180, width=2)
    d.line([sx + 20, sy + sh - 10, sx + sw - 20, sy + 20], fill=180, width=2)
    d.ellipse([sx + sw // 2 - 15, sy + sh // 2 - 15,
               sx + sw // 2 + 15, sy + sh // 2 + 15],
              outline=0, width=2)

    # 画笔（斜放右下角）
    px = sx + sw - 35
    py = sy + sh - 15
    d.line([px, py, px + 30, py - 35], fill=0, width=5)
    d.polygon([px + 30, py - 35, px + 38, py - 28, px + 25, py - 25], fill=0)
    d.line([px - 5, py + 5, px, py], fill=120, width=4)

    # 底部按钮条
    by = margin + body - 18
    d.rounded_rectangle([margin + 30, by, margin + body - 30, by + 10],
                        radius=5, outline=0, width=1, fill=240)

    img.save(path, "PNG")
    print(f"Icon saved: {path}")


if __name__ == "__main__":
    import os
    os.makedirs(os.path.dirname(ICON_PATH), exist_ok=True)
    generate_kdap_icon()
