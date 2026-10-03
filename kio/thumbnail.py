#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 缩略图生成/解析"""
import numpy as np
from PIL import Image
from core.config import KDAP_THUMB_W, KDAP_THUMB_H


def generate_thumbnail(canvas, cfg):
    """生成 144x108 4-bit 灰度缩略图"""
    composite = canvas.composite()
    img = Image.fromarray(composite, mode="L")
    img = img.resize((KDAP_THUMB_W, KDAP_THUMB_H), Image.LANCZOS)

    arr = np.array(img, dtype=np.uint8)
    arr = arr >> 4  # 8-bit -> 4-bit

    packed = bytearray(KDAP_THUMB_W * KDAP_THUMB_H // 2)
    for i in range(0, KDAP_THUMB_W * KDAP_THUMB_H, 2):
        hi = arr.flat[i] & 0x0F
        lo = arr.flat[i + 1] if i + 1 < arr.size else 0
        packed[i // 2] = (hi << 4) | lo

    return bytes(packed)


def parse_thumbnail(data):
    """解析 4-bit 缩略图"""
    arr = bytearray(KDAP_THUMB_W * KDAP_THUMB_H)
    for i in range(len(data)):
        arr[i * 2] = (data[i] >> 4) & 0x0F
        arr[i * 2 + 1] = data[i] & 0x0F

    arr = np.array(arr, dtype=np.uint8) * 16
    arr = arr.reshape(KDAP_THUMB_H, KDAP_THUMB_W)
    return Image.fromarray(arr, mode="L")
