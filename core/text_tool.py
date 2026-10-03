#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 文字工具"""
import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from core.config import BASE, KDAPConfig
WHITE = KDAPConfig.WHITE
BLACK = KDAPConfig.BLACK

FONTS_DIR = os.path.join(BASE, "fonts")
TEXTS_FILE = os.path.join(BASE, "texts.json")
INPUT_PIPE = os.path.join(BASE, "input_pipe")

DEFAULT_TEXTS = {
    "en": ["Hello", "Note", "Important!", "TODO", "Review", "Sign here", "Draft"],
    "zh": ["笔记", "重要！", "待办", "审阅", "签名处", "草稿", "已阅"],
}


def _get_font(state):
    font_path = os.path.join(FONTS_DIR, state.font_name)
    if not os.path.exists(font_path):
        font_path = None
        if os.path.isdir(FONTS_DIR):
            for f in sorted(os.listdir(FONTS_DIR)):
                if f.endswith(".ttf"):
                    font_path = os.path.join(FONTS_DIR, f)
                    break
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, state.font_size)
        except Exception:
            pass
    return ImageFont.load_default()


def render_text_to_layer(layer_pixels, x, y, text, state):
    """把文字渲染到图层"""
    h, w = layer_pixels.shape
    font = _get_font(state)
    tmp = Image.new("L", (w, h), WHITE)
    draw = ImageDraw.Draw(tmp)
    draw.text((x, y), text, fill=BLACK, font=font)
    tmp_arr = np.array(tmp)
    mask = tmp_arr < WHITE
    layer_pixels[mask] = tmp_arr[mask]


def load_preset_texts(lang="en"):
    if os.path.exists(TEXTS_FILE):
        with open(TEXTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(lang, DEFAULT_TEXTS.get(lang, []))
    return DEFAULT_TEXTS.get(lang, [])


def save_preset_texts(texts_dict):
    with open(TEXTS_FILE, "w", encoding="utf-8") as f:
        json.dump(texts_dict, f, ensure_ascii=False, indent=2)


def get_pipe_text():
    """从 FIFO 读取 SSH 输入的文字"""
    if not os.path.exists(INPUT_PIPE):
        try:
            os.mkfifo(INPUT_PIPE)
        except OSError:
            pass
    try:
        with open(INPUT_PIPE, "r") as f:
            text = f.readline().strip()
            return text if text else None
    except Exception:
        return None
