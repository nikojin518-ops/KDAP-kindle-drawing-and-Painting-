#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDAP 读取接口
统一从 kio.kdap_io 导入，避免与 core.canvas 内部函数重名冲突
"""
import os
from kio.kdap_io import load_kdap as _load_kdap


def kdap_list_files(cfg, ext=".kdap"):
    d = os.path.join(cfg.base, "drawings")
    if not os.path.exists(d):
        return []
    return sorted(
        [f for f in os.listdir(d) if f.endswith(ext)],
        key=lambda x: os.path.getmtime(os.path.join(d, x)),
        reverse=True,
    )


def kdap_load_kdap(path, canvas, state, cfg):
    return _load_kdap(path, canvas, state, cfg)
