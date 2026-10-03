#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 画布 + 图层"""
import numpy as np

from core.config import KDAP_MAGIC, KDAP_VERSION, KDAP_THUMB_W, KDAP_THUMB_H


class Layer:
    def __init__(self, w, h, pixels=None):
        if pixels is not None:
            self.pixels = pixels
        else:
            self.pixels = np.full((h, w), 255, dtype=np.uint8)
        self.visible = True
        self.name = ""
        self.opacity = 1.0
        self.blend_mode = 0  # 0=normal

    def composite(self, bg=255):
        if not self.visible:
            return np.full(self.pixels.shape, bg, dtype=np.uint8)
        return self.pixels.copy()


class KDAPCanvas:
    def __init__(self, cfg):
        self.cfg = cfg
        self.w = cfg.canvas_w
        self.h = cfg.canvas_h
        self.layers = [Layer(self.w, self.h)]
        self.layers[0].name = "Layer 1"
        self.active = 0
        self.undo_stack = []

    def active_layer(self):
        return self.layers[self.active]

    def snapshot(self):
        if len(self.undo_stack) >= 30:
            self.undo_stack.pop(0)
        self.undo_stack.append({
            "layer_id": self.active,
            "pixels": self.active_layer().pixels.copy()
        })

    def undo(self):
        if self.undo_stack:
            entry = self.undo_stack.pop()
            lid = entry["layer_id"]
            if lid < len(self.layers):
                self.layers[lid].pixels = entry["pixels"]

    def composite(self):
        """所有可见图层合并"""
        result = np.full((self.h, self.w), 255, dtype=np.uint8)
        for layer in self.layers:
            if layer.visible:
                mask = layer.pixels < 255
                result[mask] = layer.pixels[mask]
        return result

    def composite_all(self):
        return self.composite()

    def flood_fill(self, x, y, fill_value=0):
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return
        pixels = self.active_layer().pixels
        target = int(pixels[y, x])
        if target == fill_value:
            return

        stack = [(y, x)]
        h, w = pixels.shape
        while stack:
            cy, cx = stack.pop()
            if cx < 0 or cx >= w or cy < 0 or cy >= h:
                continue
            if int(pixels[cy, cx]) != target:
                continue
            pixels[cy, cx] = fill_value
            stack.append((cy + 1, cx))
            stack.append((cy - 1, cx))
            stack.append((cy, cx + 1))
            stack.append((cy, cx - 1))




