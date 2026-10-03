#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 事件分发"""
import time
from core.config import KDAPConfig


def kdap_tap_tool(state, tool_id):
    if state.tool == tool_id:
        now = time.time()
        if tool_id in (KDAPConfig.TOOL_PEN, KDAPConfig.TOOL_ERASER):
            if state.check_triple_tap(tool_id, now):
                state.show_size_panel = True
                state.size_panel_target = tool_id
        elif tool_id == KDAPConfig.TOOL_TEXT:
            if state.check_triple_tap(tool_id, now):
                state.show_text_panel = True
    else:
        state.tool = tool_id
        state.show_size_panel = False
        state.show_text_panel = False


def kdap_handle_menu_tap(lx, ly, state, cfg, canvas):
    slots = [
        (30,  cfg.TOOL_PEN),
        (140, cfg.TOOL_ERASER),
        (250, cfg.TOOL_BUCKET),
        (360, cfg.TOOL_MOVE),
        (470, cfg.TOOL_TEXT),
        (580, cfg.TOOL_LAYERS),
    ]
    for ytop, tid in slots:
        if ytop <= ly <= ytop + 90:
            if tid == cfg.TOOL_LAYERS:
                state.show_layers_panel = not state.show_layers_panel
                state.show_settings = False
                state.show_text_panel = False
            else:
                kdap_tap_tool(state, tid)
            return
