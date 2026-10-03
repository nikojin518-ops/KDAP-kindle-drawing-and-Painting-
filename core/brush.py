#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 笔刷/橡皮"""
import numpy as np
from core.config import KDAPConfig
WHITE = KDAPConfig.WHITE
BLACK = KDAPConfig.BLACK


def _brush_kernel(size, hardness):
    """生成笔刷核（圆形，带硬度）"""
    radius = size / 2.0
    y, x = np.ogrid[-radius:radius, -radius:radius]
    dist = np.sqrt(x*x + y*y)
    mask = dist <= radius
    kernel = np.where(mask, np.clip(1.0 - dist / radius * (1.0 - hardness), 0, 1), 0)
    return kernel


def kdap_stroke(pixels, x0, y0, x1, y1, size, erase=False):
    """在像素数组上画一条线"""
    h, w = pixels.shape
    color = WHITE if erase else BLACK

    # Bresenham + 笔刷
    dx = x1 - x0
    dy = y1 - y0
    steps = int(max(abs(dx), abs(dy))) + 1

    if size <= 2:
        # 细线，直接画
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            px = int(x0 + dx * t)
            py = int(y0 + dy * t)
            if 0 <= px < w and 0 <= py < h:
                pixels[py, px] = color
        return

    kernel = _brush_kernel(size, 0.7)
    kh, kw = kernel.shape
    ky0 = kh // 2
    kx0 = kw // 2

    for i in range(steps + 1):
        t = i / steps if steps > 0 else 0
        px = int(x0 + dx * t)
        py = int(y0 + dy * t)

        for ky in range(kh):
            for kx in range(kw):
                if kernel[ky, kx] <= 0:
                    continue
                yy = py + (ky - ky0)
                xx = px + (kx - kx0)
                if 0 <= xx < w and 0 <= yy < h:
                    v = float(kernel[ky, kx])
                    cur = int(pixels[yy, xx])          # 转 int 避免 uint8 下溢
                    if erase:
                        # 橡皮：向白色混合
                        pixels[yy, xx] = int(cur + (WHITE - cur) * v)
                    else:
                        # 画笔：向黑色混合
                        pixels[yy, xx] = int(cur + (BLACK - cur) * v)


def kdap_brush_preset(name):
    """笔刷预设"""
    presets = {
        "pencil":   {"size": 2, "hardness": 0.9},
        "pen":      {"size": 4, "hardness": 0.7},
        "brush":    {"size": 12, "hardness": 0.4},
        "marker":   {"size": 8, "hardness": 0.6},
    }
    return presets.get(name, {"size": 4, "hardness": 0.7})
