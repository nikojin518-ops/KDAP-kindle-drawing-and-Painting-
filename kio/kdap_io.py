#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDAP - Kindle Drawing & Painting
io/kdap_io.py - .kdap v1.5 文件格式（唯一真源）
save/load 的统一实现，禁止在其他模块重复定义同名函数。
"""

import struct
import zlib
import json
import os
import time
import numpy as np

from core.config import (KDAP_MAGIC, KDAP_VERSION, KDAP_VERSIONS_SUPPORTED,
                        KDAP_THUMB_W, KDAP_THUMB_H)
from core.canvas import Layer
from kio.thumbnail import generate_thumbnail, parse_thumbnail


def save_kdap(path, canvas, state, cfg):
    """保存 .kdap 格式（v1.8）。文件格式与 v1.5 完全兼容，
    header 版本号字段从 0x0105 升到 0x0108，新增字段均放在尾部 metadata，
    旧版读取器即使不识别也会忽略。"""
    with open(path, "wb") as f:
        # Header
        f.write(KDAP_MAGIC)                        # 4 bytes
        f.write(struct.pack("<H", KDAP_VERSION))   # 2 bytes, v1.8

        flags = 0x0001  # bit0 = has_thumbnail
        f.write(struct.pack("<H", flags))           # 2 bytes

        f.write(struct.pack("<I", canvas.w))        # 4 bytes
        f.write(struct.pack("<I", canvas.h))        # 4 bytes

        f.write(struct.pack("<B", len(canvas.layers)))     # 1 byte
        f.write(struct.pack("<B", canvas.active))         # 1 byte
        f.write(struct.pack("<B", 0 if cfg.orientation == "landscape" else 1))  # 1 byte
        f.write(b"\x00" * 7)                        # 7 bytes reserved

        # Thumbnail (4-bit grayscale)
        thumb = generate_thumbnail(canvas, cfg)
        f.write(thumb)

        # Layers
        for layer in canvas.layers:
            f.write(struct.pack("<B", 1 if layer.visible else 0))
            f.write(struct.pack("<B", int(layer.opacity * 255)))
            f.write(struct.pack("<B", layer.blend_mode))
            f.write(b"\x00")                        # reserved

            pixels = layer.pixels.flatten().tobytes()
            compressed = zlib.compress(pixels, level=1)
            f.write(struct.pack("<I", len(compressed)))
            f.write(compressed)

        # Undo Stack (最多 30 条)
        f.write(struct.pack("<H", len(canvas.undo_stack)))
        for entry in canvas.undo_stack[-30:]:
            f.write(struct.pack("<B", entry["layer_id"]))
            snap_pixels = entry["pixels"].flatten().tobytes()
            compressed = zlib.compress(snap_pixels, level=1)
            f.write(struct.pack("<I", len(compressed)))
            f.write(compressed)

        # Metadata JSON（尾部以 KDAP_END 标记结束）
        metadata = {
            "version": "1.8",
            "app": "KDAP",
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "text_objects": getattr(state, 'text_objects', []),
            "config": {
                "pen_size": cfg.pen_size,
                "font": cfg.font_name,
                "lang": cfg.lang,
            }
        }
        meta_json = json.dumps(metadata, ensure_ascii=False)
        f.write(meta_json.encode("utf-8"))
        f.write(b"KDAP_END")

    return True


def load_kdap(path, canvas, state, cfg):
    """读取 .kdap v1.5 格式，失败返回 (False, reason)"""
    if not os.path.exists(path):
        return False, f"File not found: {path}"

    with open(path, "rb") as f:
        magic = f.read(4)
        if magic != KDAP_MAGIC:
            return False, "Invalid file: not a KDAP file"

        version = struct.unpack("<H", f.read(2))[0]
        if version not in KDAP_VERSIONS_SUPPORTED:
            return False, (f"Unsupported version 0x{version:04X} "
                           f"(supported: {[hex(v) for v in KDAP_VERSIONS_SUPPORTED]})")
        # v1.5 文件在 v1.8 中照常打开；v1.8 保存时才会写成 0x0108
        if version != KDAP_VERSION:
            print(f"[io] loading legacy {version:#06x} file as v1.8 (read-only compat)")

        flags = struct.unpack("<H", f.read(2))[0]
        has_thumb = bool(flags & 0x0001)

        cw = struct.unpack("<I", f.read(4))[0]
        ch = struct.unpack("<I", f.read(4))[0]
        layer_count = struct.unpack("<B", f.read(1))[0]
        active_idx = struct.unpack("<B", f.read(1))[0]
        orient = struct.unpack("<B", f.read(1))[0]
        f.read(7)  # reserved

        cfg.orientation = "landscape" if orient == 0 else "portrait"

        # 重新初始化画布尺寸
        canvas.w = cw
        canvas.h = ch

        # 缩略图
        if has_thumb:
            thumb_data = f.read(KDAP_THUMB_W * KDAP_THUMB_H // 2)
            state._thumb = parse_thumbnail(thumb_data)

        # Layers
        canvas.layers.clear()
        for i in range(layer_count):
            visible = struct.unpack("<B", f.read(1))[0]
            opacity = struct.unpack("<B", f.read(1))[0]
            blend = struct.unpack("<B", f.read(1))[0]
            f.read(1)  # reserved

            data_len = struct.unpack("<I", f.read(4))[0]
            compressed = f.read(data_len)
            pixels = zlib.decompress(compressed)
            arr = np.frombuffer(pixels, dtype=np.uint8).reshape(ch, cw)

            layer = Layer(cw, ch, arr.copy())
            layer.visible = bool(visible)
            layer.opacity = opacity / 255.0
            layer.blend_mode = blend
            if not layer.name:
                layer.name = f"L{i+1}"
            canvas.layers.append(layer)

        canvas.active = min(active_idx, len(canvas.layers) - 1) if canvas.layers else 0
        if not canvas.layers:
            canvas.layers.append(Layer(cw, ch))

        # Undo Stack
        undo_count = struct.unpack("<H", f.read(2))[0]
        canvas.undo_stack.clear()
        for _ in range(undo_count):
            lid = struct.unpack("<B", f.read(1))[0]
            data_len = struct.unpack("<I", f.read(4))[0]
            compressed = f.read(data_len)
            pixels = zlib.decompress(compressed)
            arr = np.frombuffer(pixels, dtype=np.uint8).reshape(ch, cw)
            canvas.undo_stack.append({"layer_id": lid, "pixels": arr.copy()})

        # Metadata
        remaining = f.read()
        if b"KDAP_END" in remaining:
            meta_raw = remaining.split(b"KDAP_END")[0]
            try:
                metadata = json.loads(meta_raw.decode("utf-8"))
                if "text_objects" in metadata:
                    state.text_objects = metadata["text_objects"]
            except Exception:
                pass

    return True, "OK"
