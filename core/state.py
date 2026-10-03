#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 全局状态"""
import time


class KDAPState:
    def __init__(self, cfg):
        self.cfg = cfg
        self.tool = cfg.TOOL_PEN
        self.pen_size = cfg.pen_size
        self.eraser_size = cfg.eraser_size
        self.brush_hardness = cfg.brush_hardness
        self.font_size = cfg.font_size
        self.font_name = cfg.font_name

        # 面板开关
        self.show_settings = False
        self.show_size_panel = False
        self.show_text_panel = False
        self.show_text_input = False
        self.show_save_dialog = False
        self.show_load_dialog = False
        self.show_lang_picker = False
        self.show_layers_panel = False
        self.show_http_panel = False

        self.size_panel_target = cfg.TOOL_PEN
        self.text_insert_pos = (0, 0)
        self.insert_x = 0
        self.insert_y = 0
        self.first_run = True

        # 三连击检测
        self._last_tap_tool = None
        self._last_tap_time = 0
        self._tap_count = 0

        # 软键盘
        self.kb_visible = False
        self.kb_mode = "en"
        self.kb_shift = False
        self.compose = ""
        self.candidates = []
        self.candidate_page = 0
        self.text_buffer = ""
        self._pending_commit_text = ""
        self._ip_idx = 0

        # HTTP 等待
        self.waiting_http_text = False

        # 文本对象（元数据）
        self.text_objects = []

    def check_triple_tap(self, tool_id, now):
        if self._last_tap_tool != tool_id:
            self._last_tap_tool = tool_id
            self._tap_count = 1
            self._last_tap_time = now
            return False
        if now - self._last_tap_time < 0.5:
            self._tap_count += 1
        else:
            self._tap_count = 1
        self._last_tap_time = now
        return self._tap_count >= 3
