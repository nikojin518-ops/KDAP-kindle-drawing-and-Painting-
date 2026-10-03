#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 左侧工具栏"""
from core.i18n import _


def _rect(draw, box, outline=0, fill=None, width=1):
    draw.rectangle(box, outline=outline, fill=fill, width=width)


def _draw_text(draw, pos, text, size=16):
    draw.text(pos, text, fill=0)


def kdap_draw_menu(draw, state, cfg):
    _rect(draw, [0, 0, cfg.menu_w, cfg.logic_h], outline=cfg.BLACK)
    icons = [
        (cfg.TOOL_PEN,    "\u270e", _("pen")),
        (cfg.TOOL_ERASER, "\u232b", _("eraser")),
        (cfg.TOOL_BUCKET, "\u25a3", _("bucket")),
        (cfg.TOOL_MOVE,   "\u2735", _("move")),
        (cfg.TOOL_TEXT,   "T",      _("text")),
        (cfg.TOOL_LAYERS, "\u2261", _("layers")),
    ]
    for i, (tid, icon, name) in enumerate(icons):
        y = 30 + i * 110
        if state.tool == tid:
            _rect(draw, [5, y, cfg.menu_w - 5, y + 90],
                  outline=cfg.BLACK, width=2, fill=200)
        _draw_text(draw, (cfg.menu_w // 2 - 8, y + 10), icon, size=28)
        _draw_text(draw, (cfg.menu_w // 2 - len(name) * 4, y + 60), name, size=14)
