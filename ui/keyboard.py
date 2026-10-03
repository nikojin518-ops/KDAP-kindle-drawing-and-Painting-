#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 软键盘"""
import numpy as np
from PIL import ImageDraw
from core.config import KDAPConfig
from ime.pinyin import query

ROWS_EN = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
    ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
]

ROWS_SYM = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")"],
    ["-", "=", "_", "+", "/", "\\", ":", ";", "'", "\""],
    ["[", "]", "{", "}", "<", ">", "?", "~", "|", "`"],
]


def _rect(draw, box, outline=0, fill=None, width=1):
    draw.rectangle(box, outline=outline, fill=fill, width=width)


def _draw_text(draw, pos, text, size=18):
    draw.text(pos, text, fill=0)


def kbd_rect(cfg):
    if cfg.orientation == "landscape":
        kw = cfg.logic_w
        kh = 300
        kx = 0
        ky = cfg.logic_h - kh
    else:
        kw = cfg.logic_w
        kh = 280
        kx = 0
        ky = cfg.logic_h - kh
    return kx, ky, kw, kh


def kbd_is_visible(state):
    return state.kb_visible


def kdap_draw_keyboard(d, state, cfg):
    kx, ky, kw, kh = kbd_rect(cfg)
    _rect(d, [kx, ky, kx + kw, ky + kh], outline=0, fill=245)

    # 状态栏
    mode_label = "EN" if state.kb_mode == "en" else "中" if state.kb_mode == "cn" else "#"
    _draw_text(d, (kx + 10, ky + 6), mode_label, size=18)
    _draw_text(d, (kx + 60, ky + 6), state.compose, size=18)
    _draw_text(d, (kx + kw - 70, ky + 6), "Done", size=18)

    # 候选条
    if state.kb_mode == "cn" and state.compose:
        cands = state.candidates[:9]
        cx = kx + 10
        cy = ky + 30
        for i, w in enumerate(cands):
            label = f"{i+1}.{w}"
            _draw_text(d, (cx, cy), label, size=16)
            cx += 20 + len(label) * 9
            if cx > kx + kw - 120:
                break

    # 键行
    if state.kb_mode == "sym":
        rows = ROWS_SYM
    else:
        rows = ROWS_EN

    top = ky + 60
    row_h = (kh - 70) // (len(rows) + 1)
    key_h = row_h - 6

    for ri, row in enumerate(rows):
        n = len(row)
        gap = 4
        key_w = (kw - gap * (n + 1)) / n
        y = top + ri * row_h
        for ci, key in enumerate(row):
            x = kx + gap + ci * (key_w + gap)
            ch = key.upper() if state.kb_shift else key
            _rect(d, [x, y, x + key_w, y + key_h], outline=0, fill=255)
            _draw_text(d, (x + key_w / 2 - 6, y + key_h / 2 - 10), ch, size=20)

    # 功能键
    fy = top + len(rows) * row_h
    fw = kw // 7
    labels = ["Shift", "Del", "Space", "中/EN", "123", "Enter", "Hide"]
    fx = kx
    for label in labels:
        _rect(d, [fx, fy, fx + fw - 4, fy + row_h - 6], outline=0, fill=230)
        _draw_text(d, (fx + 6, fy + 10), label, size=14)
        fx += fw


def kbd_hit(lx, ly, state, cfg):
    kx, ky, kw, kh = kbd_rect(cfg)
    if not (ky <= ly <= ky + kh):
        return None

    if state.kb_mode == "cn" and state.compose:
        if ky + 25 <= ly <= ky + 55:
            return "cand:0"

    if state.kb_mode == "sym":
        rows = ROWS_SYM
    else:
        rows = ROWS_EN

    top = ky + 60
    row_h = (kh - 70) // (len(rows) + 1)
    key_h = row_h - 6

    for ri, row in enumerate(rows):
        n = len(row)
        gap = 4
        key_w = (kw - gap * (n + 1)) / n
        y = top + ri * row_h
        if y <= ly <= y + key_h:
            for ci in range(n):
                x = kx + gap + ci * (key_w + gap)
                if x <= lx <= x + key_w:
                    return "char:" + row[ci]

    fy = top + len(rows) * row_h
    fw = kw // 7
    labels = ["shift", "back", "space", "mode", "sym", "enter", "hide"]
    fx = kx
    for kid in labels:
        if fx <= lx <= fx + fw - 4 and fy <= ly <= fy + row_h - 6:
            return kid
        fx += fw

    # Done
    if kx + kw - 80 <= lx <= kx + kw and ky <= ly <= ky + 30:
        return "hide"

    return None


def _commit_candidate(state, idx):
    if idx < len(state.candidates):
        state.text_buffer += state.candidates[idx]
    state.compose = ""
    state.candidates = []


def kbd_on_key(kid, state, cfg, canvas=None):
    if kid == "shift":
        state.kb_shift = not state.kb_shift
    elif kid == "mode":
        state.kb_mode = {"en": "cn", "cn": "en", "sym": "en"}[state.kb_mode]
    elif kid == "sym":
        state.kb_mode = "sym" if state.kb_mode != "sym" else "en"
    elif kid == "back":
        if state.kb_mode == "cn" and state.compose:
            state.compose = state.compose[:-1]
            state.candidates = query(state.compose)
        else:
            state.text_buffer = state.text_buffer[:-1]
    elif kid == "space":
        if state.kb_mode == "cn" and state.compose:
            _commit_candidate(state, 0)
        else:
            state.text_buffer += " "
    elif kid == "enter":
        if state.kb_mode == "cn" and state.compose:
            _commit_candidate(state, 0)
        else:
            state._pending_commit_text = state.text_buffer
            state.text_buffer = ""
            state.kb_visible = False
    elif kid == "hide":
        state.kb_visible = False
        if state.kb_mode == "cn" and state.compose:
            _commit_candidate(state, 0)
    elif kid and kid.startswith("cand:"):
        idx = int(kid.split(":")[1])
        _commit_candidate(state, idx)
    elif kid and kid.startswith("char:"):
        ch = kid[5:]
        if state.kb_mode == "cn":
            state.compose += ch
            state.candidates = query(state.compose)
        else:
            state.text_buffer += ch.upper() if state.kb_shift else ch
        state.kb_shift = False
