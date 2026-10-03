#!/usr/bin/env python3
"""
test_kb.py - 测试软键盘布局渲染（不依赖 Kindle 硬件）
用法: python3 test_kb.py
"""
import sys
import os

sys.path.insert(0, "/mnt/us/kdap")

from core.config import KDAPConfig
from core.state import KDAPState
from ui.keyboard import kdap_draw_keyboard, kbd_rect, kbd_hit, kbd_on_key
from PIL import Image, ImageDraw

cfg = KDAPConfig()
state = KDAPState(cfg)

print(f"逻辑分辨率: {cfg.logic_w}x{cfg.logic_h}")
print(f"键盘区域: {kbd_rect(cfg)}")

# 测试渲染
img = Image.new("L", (cfg.logic_w, cfg.logic_h), 255)
d = ImageDraw.Draw(img)

# 模拟画布
for y in range(cfg.canvas_y, cfg.canvas_y + cfg.canvas_h, 40):
    d.line([cfg.canvas_x, y, cfg.canvas_x + cfg.canvas_w, y], fill=200, width=1)

state.kb_visible = True
state.kb_mode = "en"
kdap_draw_keyboard(d, state, cfg)

# 测试命中检测
test_points = [
    (50, cfg.logic_h - 290),
    (100, cfg.logic_h - 200),
    (400, cfg.logic_h - 100),
]
print("\n命中测试:")
for x, y in test_points:
    hit = kbd_hit(x, y, state, cfg)
    print(f"  ({x},{y}) -> {hit}")

out = "/mnt/us/kdap/drawings/kb_test.png"
img.save(out)
print(f"\n键盘预览已保存: {out}")
print("用电脑查看此图片确认布局是否正确。")
