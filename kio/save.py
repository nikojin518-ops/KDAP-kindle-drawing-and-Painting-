#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDAP 保存接口
统一从 kio.kdap_io 导入，避免与 core.canvas 内部函数重名冲突
"""
from PIL import Image
from kio.kdap_io import save_kdap as _save_kdap


def kdap_save_png(canvas, path, cfg):
    """保存为 PNG"""
    img = Image.fromarray(canvas.composite()).convert("L")
    img.save(path)


def kdap_save_kdap(canvas, path, state, cfg):
    """保存为 .kdap v1.5"""
    return _save_kdap(path, canvas, state, cfg)
