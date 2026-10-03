#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 主渲染"""
import numpy as np
from PIL import Image, ImageDraw

from core.config import KDAPConfig, KDAP_VERSION_STR
from core.state import KDAPState
from core.canvas import KDAPCanvas
from core.i18n import _
from ui.menu import kdap_draw_menu
from ui.panels import (
    kdap_draw_settings_panel, kdap_draw_size_panel,
    kdap_draw_text_panel, kdap_draw_text_input_panel,
    kdap_draw_save_dialog, kdap_draw_load_dialog,
    kdap_draw_lang_picker, kdap_draw_layers_panel,
    kdap_draw_http_panel,
)
from ui.keyboard import kdap_draw_keyboard


def _rect(draw, box, outline=0, fill=None, width=1):
    draw.rectangle(box, outline=outline, fill=fill, width=width)


def _draw_text(draw, pos, text, size=16):
    draw.text(pos, text, fill=0)


def kdap_render(canvas, state, cfg):
    img = Image.new("L", (cfg.logic_w, cfg.logic_h), 255)
    draw = ImageDraw.Draw(img)

    # 画布区
    comp = canvas.composite_all()
    cimg = Image.fromarray(comp)
    img.paste(cimg, (cfg.canvas_x, cfg.canvas_y))

    # 顶部栏
    _rect(draw, [0, 0, cfg.logic_w, cfg.ui_top_h], fill=240)
    _draw_text(draw, (cfg.menu_w + 10, 10),
               f"{_('app_name')} | L:{canvas.active + 1}/{len(canvas.layers)}", size=16)
    _draw_text(draw, (cfg.logic_w - 30, 8), "\u2699", size=22)

    # 左侧菜单
    kdap_draw_menu(draw, state, cfg)

    # 软键盘（覆盖底部）
    if state.kb_visible:
        kdap_draw_keyboard(draw, state, cfg)

    # 浮层面板
    if state.show_settings:
        kdap_draw_settings_panel(draw, state, cfg)
    if state.show_size_panel:
        kdap_draw_size_panel(draw, state, cfg)
    if state.show_text_panel:
        kdap_draw_text_panel(draw, state, cfg)
    if state.show_text_input:
        kdap_draw_text_input_panel(draw, state, cfg)
    if state.show_save_dialog:
        kdap_draw_save_dialog(draw, state, cfg)
    if state.show_load_dialog:
        kdap_draw_load_dialog(draw, state, cfg)
    if state.show_lang_picker:
        kdap_draw_lang_picker(draw, state, cfg)
    if state.show_layers_panel:
        kdap_draw_layers_panel(draw, state, cfg, canvas)
    if state.show_http_panel:
        kdap_draw_http_panel(draw, state, cfg)

    # 版本号
    _draw_text(draw, (cfg.logic_w - 70, cfg.logic_h - 22), KDAP_VERSION_STR, size=13)

    return img
