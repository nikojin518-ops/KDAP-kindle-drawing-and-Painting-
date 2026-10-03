#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 全局配置"""
import os
import json

BASE = "/mnt/us/kdap"

KDAP_MAGIC = b"KDAP"
KDAP_VERSION = 0x0108
KDAP_VERSION_STR = "v1.8"
# 历史版本集合：读取时兼容 v1.5 文件
KDAP_VERSIONS_SUPPORTED = (0x0105, 0x0108)

KDAP_THUMB_W = 144
KDAP_THUMB_H = 108


class KDAPConfig:
    # 工具 ID
    TOOL_PEN = "pen"
    TOOL_ERASER = "eraser"
    TOOL_BUCKET = "bucket"
    TOOL_MOVE = "move"
    TOOL_TEXT = "text"
    TOOL_LAYERS = "layers"
    TOOL_SELECT = "select"
    TOOL_SHAPE = "shape"

    # 灰度值
    WHITE = 255
    BLACK = 0

    # HTTP 默认
    HTTP_PORT = 8080
    HTTP_IP = "0.0.0.0"
    HTTP_USER = ""
    HTTP_PASS = ""

    # 最大值
    MAX_LAYERS = 8

    def __init__(self):
        self.base = BASE
        self.orientation = "landscape"
        self.lang = "en"
        self.font_name = "DejaVuSans.ttf"
        self.font_size = 24
        self.pen_size = 4
        self.eraser_size = 20
        self.brush_hardness = 0.7

        # 逻辑分辨率（横屏）
        self.logic_w = 952
        self.logic_h = 972
        self.menu_w = 80
        self.ui_top_h = 40
        self.canvas_x = self.menu_w
        self.canvas_y = self.ui_top_h
        self.canvas_w = self.logic_w - self.menu_w
        self.canvas_h = self.logic_h - self.ui_top_h

        self._load_conf()

    def _load_conf(self):
        path = os.path.join(self.base, "kdap.conf")
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    d = json.load(f)
                self.lang = d.get("lang", self.lang)
                self.orientation = d.get("orientation", self.orientation)
                self.font_name = d.get("font_name", self.font_name)
                self.font_size = d.get("font_size", self.font_size)
                self.pen_size = d.get("pen_size", self.pen_size)
                self.eraser_size = d.get("eraser_size", self.eraser_size)
                self.brush_hardness = d.get("brush_hardness", self.brush_hardness)
                self.HTTP_PORT = d.get("http_port", self.HTTP_PORT)
                self.HTTP_IP = d.get("http_ip", self.HTTP_IP)
                self.HTTP_USER = d.get("http_user", self.HTTP_USER)
                self.HTTP_PASS = d.get("http_pass", self.HTTP_PASS)
            except Exception:
                pass

    def save_conf(self):
        path = os.path.join(self.base, "kdap.conf")
        d = {
            "lang": self.lang,
            "orientation": self.orientation,
            "font_name": self.font_name,
            "font_size": self.font_size,
            "pen_size": self.pen_size,
            "eraser_size": self.eraser_size,
            "brush_hardness": self.brush_hardness,
            "http_port": self.HTTP_PORT,
            "http_ip": self.HTTP_IP,
            "http_user": self.HTTP_USER,
            "http_pass": self.HTTP_PASS,
        }
        with open(path, "w") as f:
            json.dump(d, f)
