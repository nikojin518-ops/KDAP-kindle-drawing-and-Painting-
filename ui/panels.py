#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 所有浮层面板"""
import os
import subprocess
import time

from core.i18n import _
from core.config import KDAPConfig, KDAP_VERSION_STR
from kio.httpd import (kdap_http_running, kdap_http_start, kdap_http_stop,
                      kdap_http_configure)


def _rect(draw, box, outline=0, fill=None, width=1):
    if isinstance(box, tuple):
        box = list(box)
    draw.rectangle(box, outline=outline, fill=fill, width=width)


def _draw_text(draw, pos, text, size=16):
    draw.text(pos, text, fill=0)


# ==================== 设置面板 ====================

def kdap_draw_settings_panel(draw, state, cfg):
    pw, ph = 400, 500
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2
    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=cfg.BLACK, fill=230)
    _draw_text(draw, (x0 + 140, y0 + 15), _("settings"), size=24)

    buttons = [
        ("Save",   "\u2714  " + _("save")),
        ("Load",   "\u2261  " + _("load")),
        ("Orient", "\u21B7  " + _("orient")),
        ("Lang",   "\U0001F310" + "  " + _("language")),
        ("Font",   "T  " + _("text_settings")),
        ("HTTP",   "\U0001F310" + "  HTTP"),
        ("Exit",   "\u2716  " + _("exit")),
    ]
    for i, (key, label) in enumerate(buttons):
        by = y0 + 60 + i * 60
        _rect(draw, [x0 + 40, by, x0 + pw - 40, by + 50], outline=cfg.BLACK)
        _draw_text(draw, (x0 + 60, by + 14), label, size=18)

    _draw_text(draw, (x0 + 20, y0 + ph - 30), f"KDAP {KDAP_VERSION_STR}", size=14)


def kdap_handle_settings(lx, ly, state, cfg):
    pw, ph = 400, 500
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2

    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        state.show_settings = False
        return

    buttons = ["Save", "Load", "Orient", "Lang", "Font", "HTTP", "Exit"]
    for i, key in enumerate(buttons):
        by = y0 + 60 + i * 60
        if x0 + 40 <= lx <= x0 + pw - 40 and by <= ly <= by + 50:
            if key == "HTTP":
                state.show_http_panel = True
                state.show_settings = False
            elif key == "Save":
                state.show_save_dialog = True
                state.show_settings = False
            elif key == "Load":
                state.show_load_dialog = True
                state.show_settings = False
            elif key == "Orient":
                cfg.orientation = "portrait" if cfg.orientation == "landscape" else "landscape"
                cfg.save_conf()
                state.show_settings = False
            elif key == "Lang":
                state.show_lang_picker = True
                state.show_settings = False
            elif key == "Font":
                state.show_text_panel = True
                state.show_settings = False
            elif key == "Exit":
                subprocess.run(["killall", "python3"])
                subprocess.run(["start", "lab126_gui"])
            return


# ==================== 粗细面板 ====================

def kdap_draw_size_panel(draw, state, cfg):
    pw, ph = 260, 320
    x0 = cfg.menu_w + 10
    y0 = 120
    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=cfg.BLACK, fill=235)
    label = _("pen_size") if state.size_panel_target == cfg.TOOL_PEN else _("eraser_size")
    _draw_text(draw, (x0 + 60, y0 + 10), label, size=18)

    sz = state.pen_size if state.size_panel_target == cfg.TOOL_PEN else state.eraser_size
    _draw_text(draw, (x0 + 20, y0 + 45), f"{sz}px", size=16)

    _rect(draw, [x0 + 20, y0 + 70, x0 + 100, y0 + 115], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 45, y0 + 80), "+", size=28)
    _rect(draw, [x0 + 130, y0 + 70, x0 + 210, y0 + 115], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 155, y0 + 80), "-", size=28)

    for i, s in enumerate([2, 4, 8, 16, 32]):
        sy = y0 + 130 + i * 32
        _draw_text(draw, (x0 + 20, sy), f"{s}px", size=14)
        if sz == s:
            _rect(draw, [x0 + 80, sy - 2, x0 + 100, sy + 18], outline=cfg.BLACK)

    _rect(draw, [x0 + 70, y0 + 280, x0 + 190, y0 + 315], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 100, y0 + 286), _("close"), size=16)


def kdap_handle_size_panel(lx, ly, state, cfg):
    pw, ph = 260, 320
    x0 = cfg.menu_w + 10
    y0 = 120
    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        state.show_size_panel = False
        return
    if x0 + 20 <= lx <= x0 + 100 and y0 + 70 <= ly <= y0 + 115:
        if state.size_panel_target == cfg.TOOL_PEN:
            state.pen_size = min(64, state.pen_size + 2)
        else:
            state.eraser_size = min(128, state.eraser_size + 4)
    elif x0 + 130 <= lx <= x0 + 210 and y0 + 70 <= ly <= y0 + 115:
        if state.size_panel_target == cfg.TOOL_PEN:
            state.pen_size = max(1, state.pen_size - 2)
        else:
            state.eraser_size = max(2, state.eraser_size - 4)
    for i, s in enumerate([2, 4, 8, 16, 32]):
        sy = y0 + 130 + i * 32
        if x0 + 10 <= lx <= x0 + 140 and sy - 5 <= ly <= sy + 25:
            if state.size_panel_target == cfg.TOOL_PEN:
                state.pen_size = s
            else:
                state.eraser_size = s
    if x0 + 70 <= lx <= x0 + 190 and y0 + 280 <= ly <= y0 + 315:
        state.show_size_panel = False


# ==================== 文字面板 ====================

def kdap_draw_text_panel(draw, state, cfg):
    pw, ph = 280, 380
    x0 = cfg.menu_w + 10
    y0 = 120
    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=cfg.BLACK, fill=235)
    _draw_text(draw, (x0 + 70, y0 + 10), _("text_settings"), size=20)
    _draw_text(draw, (x0 + 20, y0 + 45), f"Size: {state.font_size}px", size=18)

    _rect(draw, [x0 + 20, y0 + 75, x0 + 100, y0 + 125], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 45, y0 + 88), "+", size=28)
    _rect(draw, [x0 + 140, y0 + 75, x0 + 220, y0 + 125], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 165, y0 + 88), "-", size=28)

    for i, s in enumerate([12, 16, 24, 32, 48, 64]):
        sy = y0 + 140 + i * 32
        _draw_text(draw, (x0 + 20, sy), f"{s}px", size=16)
        if state.font_size == s:
            _rect(draw, [x0 + 100, sy - 2, x0 + 120, sy + 18], outline=cfg.BLACK)

    _rect(draw, [x0 + 80, y0 + 340, x0 + 200, y0 + 375], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 110, y0 + 346), _("close"), size=16)


def kdap_handle_text_panel(lx, ly, state, cfg):
    pw, ph = 280, 380
    x0 = cfg.menu_w + 10
    y0 = 120
    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        state.show_text_panel = False
        return
    if x0 + 20 <= lx <= x0 + 100 and y0 + 75 <= ly <= y0 + 125:
        state.font_size = min(96, state.font_size + 2)
    elif x0 + 140 <= lx <= x0 + 220 and y0 + 75 <= ly <= y0 + 125:
        state.font_size = max(8, state.font_size - 2)
    for i, s in enumerate([12, 16, 24, 32, 48, 64]):
        sy = y0 + 140 + i * 32
        if x0 + 10 <= lx <= x0 + 140 and sy - 5 <= ly <= sy + 25:
            state.font_size = s
    if x0 + 80 <= lx <= x0 + 200 and y0 + 340 <= ly <= y0 + 375:
        state.show_text_panel = False


# ==================== 预设文字选择 ====================

def kdap_draw_text_input_panel(draw, state, cfg):
    from core.text_tool import load_preset_texts
    pw, ph = 420, 440
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2
    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=cfg.BLACK, fill=230)
    _draw_text(draw, (x0 + 140, y0 + 15), _("insert_text"), size=22)

    texts = load_preset_texts(cfg.lang)
    for i, txt in enumerate(texts[:7]):
        by = y0 + 55 + i * 38
        _rect(draw, [x0 + 30, by, x0 + pw - 30, by + 32], outline=cfg.BLACK)
        _draw_text(draw, (x0 + 45, by + 7), txt, size=18)

    # Keyboard
    kby = y0 + 55 + 7 * 38
    _rect(draw, [x0 + 30, kby, x0 + pw - 30, kby + 32], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 45, kby + 7), "\u2328 Keyboard", size=18)

    # HTTP Input
    hby = y0 + 55 + 8 * 38
    _rect(draw, [x0 + 30, hby, x0 + pw - 30, hby + 32], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 45, hby + 7), "\U0001F310 HTTP Input", size=18)

    _draw_text(draw, (x0 + 30, y0 + ph - 35), _("ssh_hint"), size=12)

    _rect(draw, [x0 + pw - 100, y0 + 15, x0 + pw - 20, y0 + 45], outline=cfg.BLACK)
    _draw_text(draw, (x0 + pw - 90, y0 + 22), _("cancel"), size=16)


def kdap_handle_text_input(lx, ly, state, cfg, canvas):
    pw, ph = 420, 440
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2

    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        state.show_text_input = False
        return

    if x0 + pw - 100 <= lx <= x0 + pw - 20 and y0 + 15 <= ly <= y0 + 45:
        state.show_text_input = False
        return

    from core.text_tool import load_preset_texts, render_text_to_layer

    texts = load_preset_texts(cfg.lang)

    for i in range(min(7, len(texts))):
        by = y0 + 55 + i * 38
        if x0 + 30 <= lx <= x0 + pw - 30 and by <= ly <= by + 32:
            canvas.snapshot()
            render_text_to_layer(canvas.active_layer().pixels,
                                 state.text_insert_pos[0], state.text_insert_pos[1],
                                 texts[i], state)
            state.show_text_input = False
            from core.fb import kdap_blit_full
            from ui.render import kdap_render
            kdap_blit_full(kdap_render(canvas, state, cfg))
            return

    # Keyboard
    kby = y0 + 55 + 7 * 38
    if x0 + 30 <= lx <= x0 + pw - 30 and kby <= ly <= kby + 32:
        state.kb_visible = True
        state.kb_mode = "en"
        state.text_buffer = ""
        state.compose = ""
        state.candidates = []
        state.show_text_input = False
        from core.fb import kdap_blit_full
        from ui.render import kdap_render
        kdap_blit_full(kdap_render(canvas, state, cfg))
        return

    # HTTP Input
    hby = y0 + 55 + 8 * 38
    if x0 + 30 <= lx <= x0 + pw - 30 and hby <= ly <= hby + 32:
        state.waiting_http_text = True
        state.show_text_input = False
        from core.fb import kdap_blit_full
        from ui.render import kdap_render
        kdap_blit_full(kdap_render(canvas, state, cfg))
        return


# ==================== 保存对话框 ====================

def _kdap_default_filename():
    now = time.localtime()
    return f"kdap{now.tm_mon:02d}{now.tm_mday:02d}.kdap"


def kdap_draw_save_dialog(draw, state, cfg):
    pw, ph = 420, 220
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2
    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=0, fill=230)

    _draw_text(draw, (x0 + 150, y0 + 15), _("save"), size=22)

    _draw_text(draw, (x0 + 20, y0 + 60), "Name:", size=18)
    fname = getattr(state, 'save_filename', _kdap_default_filename())
    state.save_filename = fname
    _rect(draw, [x0 + 80, y0 + 55, x0 + pw - 20, y0 + 85], outline=0)
    _draw_text(draw, (x0 + 90, y0 + 62), fname, size=16)

    _rect(draw, [x0 + 20, y0 + 100, x0 + 160, y0 + 130], outline=0)
    _draw_text(draw, (x0 + 40, y0 + 107), "Today", size=16)

    _rect(draw, [x0 + pw - 120, y0 + 100, x0 + pw - 20, y0 + 130], outline=0)
    _draw_text(draw, (x0 + pw - 105, y0 + 107), _("ok"), size=18)

    _rect(draw, [x0 + 170, y0 + 100, x0 + 270, y0 + 130], outline=0)
    _draw_text(draw, (x0 + 190, y0 + 107), _("cancel"), size=18)


def kdap_handle_save_dialog(lx, ly, state, cfg, canvas):
    pw, ph = 420, 220
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2

    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        state.show_save_dialog = False
        return

    if x0 + 20 <= lx <= x0 + 160 and y0 + 100 <= ly <= y0 + 130:
        state.save_filename = _kdap_default_filename()
        return

    if x0 + pw - 120 <= lx <= x0 + pw - 20 and y0 + 100 <= ly <= y0 + 130:
        fname = getattr(state, 'save_filename', _kdap_default_filename())
        if not fname.endswith(".kdap"):
            fname += ".kdap"
        path = f"{cfg.base}/drawings/{fname}"
        from core.canvas import save_kdap
        save_kdap(path, canvas, state, cfg)
        state.show_save_dialog = False
        return

    if x0 + 170 <= lx <= x0 + 270 and y0 + 100 <= ly <= y0 + 130:
        state.show_save_dialog = False
        return


# ==================== 读取对话框 ====================

def kdap_draw_load_dialog(draw, state, cfg):
    from kio.load import kdap_list_files
    pw, ph = 420, 400
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2
    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=cfg.BLACK, fill=230)
    _draw_text(draw, (x0 + 150, y0 + 15), _("load_title"), size=22)

    files = kdap_list_files(cfg, ".kdap")
    if not files:
        _draw_text(draw, (x0 + 60, y0 + 80), _("no_files"), size=18)
    for i, fname in enumerate(files[:8]):
        fy = y0 + 55 + i * 38
        _rect(draw, [x0 + 30, fy, x0 + pw - 30, fy + 32], outline=cfg.BLACK)
        _draw_text(draw, (x0 + 45, fy + 7), fname[:30], size=14)

    _rect(draw, [x0 + pw - 100, y0 + 15, x0 + pw - 20, y0 + 45], outline=cfg.BLACK)
    _draw_text(draw, (x0 + pw - 90, y0 + 22), _("cancel"), size=16)


def kdap_handle_load_dialog(lx, ly, state, cfg, canvas):
    from kio.load import kdap_list_files
    pw, ph = 420, 400
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2

    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        state.show_load_dialog = False
        return

    if x0 + pw - 100 <= lx <= x0 + pw - 20 and y0 + 15 <= ly <= y0 + 45:
        state.show_load_dialog = False
        return

    files = kdap_list_files(cfg, ".kdap")
    for i, fname in enumerate(files[:8]):
        fy = y0 + 55 + i * 38
        if x0 + 30 <= lx <= x0 + pw - 30 and fy <= ly <= fy + 32:
            path = f"{cfg.base}/drawings/{fname}"
            from core.canvas import load_kdap
            ok, msg = load_kdap(path, canvas, state, cfg)
            state.show_load_dialog = False
            return


# ==================== 语言选择 ====================

def kdap_draw_lang_picker(draw, state, cfg):
    pw, ph = 400, 300
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2
    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=cfg.BLACK, fill=230)
    title = _("select_language") if not state.first_run else "Welcome / " + _("select_language")
    _draw_text(draw, (x0 + 60, y0 + 20), title, size=22)

    _rect(draw, [x0 + 40, y0 + 80, x0 + pw - 40, y0 + 140], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 110, y0 + 100), "中文 / " + _("chinese"), size=22)
    _rect(draw, [x0 + 40, y0 + 160, x0 + pw - 40, y0 + 220], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 110, y0 + 180), "English / " + _("english"), size=22)


def kdap_handle_lang_picker(lx, ly, state, cfg):
    pw, ph = 400, 300
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2

    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        return

    if x0 + 40 <= lx <= x0 + pw - 40 and y0 + 80 <= ly <= y0 + 140:
        from core.i18n import set_language
        set_language("zh")
        cfg.lang = "zh"
        from core.i18n import kdap_i18n_init
        kdap_i18n_init(state)
        state.show_lang_picker = False
        state.first_run = False
    elif x0 + 40 <= lx <= x0 + pw - 40 and y0 + 160 <= ly <= y0 + 220:
        from core.i18n import set_language
        set_language("en")
        cfg.lang = "en"
        from core.i18n import kdap_i18n_init
        kdap_i18n_init(state)
        state.show_lang_picker = False
        state.first_run = False


# ==================== 图层列表面板 ====================

def kdap_draw_layers_panel(draw, state, cfg, canvas):
    pw = 200
    ph = cfg.logic_h - cfg.ui_top_h
    x0 = cfg.logic_w - pw
    y0 = cfg.ui_top_h

    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=cfg.BLACK, fill=235)
    _draw_text(draw, (x0 + 60, y0 + 10), _("layers"), size=20)
    _rect(draw, [x0 + pw - 40, y0 + 5, x0 + pw - 5, y0 + 35], outline=cfg.BLACK)
    _draw_text(draw, (x0 + pw - 30, y0 + 12), "X", size=18)

    layer_h = 55
    max_visible = (ph - 120) // layer_h
    for i in range(min(len(canvas.layers), max_visible)):
        layer_idx = len(canvas.layers) - 1 - i
        ly = y0 + 45 + i * layer_h
        layer = canvas.layers[layer_idx]
        if layer_idx == canvas.active:
            _rect(draw, [x0 + 3, ly, x0 + pw - 3, ly + layer_h - 3],
                  outline=cfg.BLACK, width=2, fill=200)
        else:
            _rect(draw, [x0 + 3, ly, x0 + pw - 3, ly + layer_h - 3],
                  outline=cfg.BLACK, fill=245)

        vis_icon = "\u25a0" if layer.visible else "\u25a1"
        _draw_text(draw, (x0 + 10, ly + 8), vis_icon, size=20)
        name = layer.name if layer.name else f"L{layer_idx + 1}"
        _draw_text(draw, (x0 + 35, ly + 8), name, size=16)

        thumb_x = x0 + pw - 40
        thumb_y = ly + 8
        _rect(draw, [thumb_x, thumb_y, thumb_x + 30, thumb_y + 20], outline=cfg.BLACK)
        if layer.visible:
            step_x = max(1, layer.pixels.shape[1] // 30)
            step_y = max(1, layer.pixels.shape[0] // 20)
            for ty in range(20):
                for tx in range(30):
                    py = ty * step_y
                    px = tx * step_x
                    if py < layer.pixels.shape[0] and px < layer.pixels.shape[1]:
                        v = layer.pixels[py, px]
                        if v < 200:
                            _rect(draw,
                                  [thumb_x + tx, thumb_y + ty,
                                   thumb_x + tx + 1, thumb_y + ty + 1],
                                  fill=v)

    by = y0 + ph - 55
    _rect(draw, [x0 + 10, by, x0 + 50, by + 40], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 22, by + 10), "+", size=24)
    _rect(draw, [x0 + 60, by, x0 + 100, by + 40], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 72, by + 10), "-", size=24)
    _rect(draw, [x0 + 110, by, x0 + 150, by + 40], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 118, by + 10), "\u2191", size=20)
    _rect(draw, [x0 + 160, by, x0 + 195, by + 40], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 168, by + 10), "\u2193", size=20)


def kdap_handle_layers_panel(lx, ly, state, cfg, canvas):
    pw = 200
    ph = cfg.logic_h - cfg.ui_top_h
    x0 = cfg.logic_w - pw
    y0 = cfg.ui_top_h

    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        state.show_layers_panel = False
        return

    if x0 + pw - 40 <= lx <= x0 + pw - 5 and y0 + 5 <= ly <= y0 + 35:
        state.show_layers_panel = False
        return

    layer_h = 55
    max_visible = (ph - 120) // layer_h

    for i in range(min(len(canvas.layers), max_visible)):
        layer_idx = len(canvas.layers) - 1 - i
        lby = y0 + 45 + i * layer_h
        if lby <= ly <= lby + layer_h - 3:
            if x0 + 10 <= lx <= x0 + 30:
                canvas.layers[layer_idx].visible = not canvas.layers[layer_idx].visible
            else:
                canvas.active = layer_idx
            return

    by = y0 + ph - 55

    if x0 + 10 <= lx <= x0 + 50 and by <= ly <= by + 40:
        if len(canvas.layers) < cfg.MAX_LAYERS:
            from core.canvas import Layer
            new_layer = Layer(canvas.w, canvas.h)
            new_layer.name = f"L{len(canvas.layers) + 1}"
            canvas.layers.append(new_layer)
            canvas.active = len(canvas.layers) - 1
        return

    if x0 + 60 <= lx <= x0 + 100 and by <= ly <= by + 40:
        if len(canvas.layers) > 1:
            canvas.layers.pop(canvas.active)
            canvas.active = min(canvas.active, len(canvas.layers) - 1)
            canvas.undo_stack.clear()
        return

    if x0 + 110 <= lx <= x0 + 150 and by <= ly <= by + 40:
        if canvas.active < len(canvas.layers) - 1:
            canvas.layers[canvas.active], canvas.layers[canvas.active + 1] = \
                canvas.layers[canvas.active + 1], canvas.layers[canvas.active]
            canvas.active += 1
        return

    if x0 + 160 <= lx <= x0 + 195 and by <= ly <= by + 40:
        if canvas.active > 0:
            canvas.layers[canvas.active], canvas.layers[canvas.active - 1] = \
                canvas.layers[canvas.active - 1], canvas.layers[canvas.active]
            canvas.active -= 1
        return


# ==================== HTTP 面板 ====================

def _get_ip_presets(cfg):
    presets = ["0.0.0.0"]
    try:
        out = subprocess.check_output(["ip", "addr", "show", "wlan0"],
                                      stderr=subprocess.DEVNULL).decode()
        for line in out.split("\n"):
            if "inet " in line:
                ip = line.strip().split()[1].split("/")[0]
                if ip not in presets:
                    presets.append(ip)
    except Exception:
        pass
    if "127.0.0.1" not in presets:
        presets.append("127.0.0.1")
    return presets


def kdap_draw_http_panel(draw, state, cfg):
    pw, ph = 460, 460
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2
    _rect(draw, [x0, y0, x0 + pw, y0 + ph], outline=cfg.BLACK, fill=230)
    _draw_text(draw, (x0 + 160, y0 + 15), "HTTP Input", size=22)

    running = kdap_http_running()
    status = "Running" if running else "Stopped"
    _draw_text(draw, (x0 + 20, y0 + 50), f"Status: {status}", size=18)

    _draw_text(draw, (x0 + 20, y0 + 85), "IP:", size=16)
    _draw_text(draw, (x0 + 60, y0 + 85), cfg.HTTP_IP, size=16)
    _rect(draw, [x0 + 200, y0 + 80, x0 + 235, y0 + 105], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 208, y0 + 83), "<", size=18)
    _rect(draw, [x0 + 240, y0 + 80, x0 + 275, y0 + 105], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 248, y0 + 83), ">", size=18)

    _draw_text(draw, (x0 + 20, y0 + 120), "Port:", size=16)
    _draw_text(draw, (x0 + 80, y0 + 118), str(cfg.HTTP_PORT), size=18)
    _rect(draw, [x0 + 140, y0 + 115, x0 + 175, y0 + 140], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 152, y0 + 120), "+", size=20)
    _rect(draw, [x0 + 180, y0 + 115, x0 + 215, y0 + 140], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 192, y0 + 120), "-", size=20)

    _draw_text(draw, (x0 + 20, y0 + 160), "User:", size=16)
    user_display = cfg.HTTP_USER if cfg.HTTP_USER else "(none)"
    _draw_text(draw, (x0 + 70, y0 + 160), user_display[:16], size=14)

    _draw_text(draw, (x0 + 20, y0 + 185), "Presets:", size=14)
    users = ["", "kdap", "kindle", "admin"]
    ux = x0 + 90
    for u in users:
        label = "off" if u == "" else u
        _rect(draw, [ux, y0 + 182, ux + 55, y0 + 200], outline=cfg.BLACK)
        _draw_text(draw, (ux + 5, y0 + 185), label[:6], size=12)
        ux += 60

    _draw_text(draw, (x0 + 20, y0 + 215), "Pass:", size=16)
    if cfg.HTTP_PASS:
        pwd_display = "*" * min(len(cfg.HTTP_PASS), 12)
    else:
        pwd_display = "(none)"
    _draw_text(draw, (x0 + 70, y0 + 215), pwd_display, size=14)

    _draw_text(draw, (x0 + 20, y0 + 240), "Presets:", size=14)
    pwds = ["", "kdap123", "kindle", "admin123"]
    px = x0 + 90
    for p in pwds:
        label = "off" if p == "" else "*" * min(len(p), 5)
        _rect(draw, [px, y0 + 237, px + 55, y0 + 255], outline=cfg.BLACK)
        _draw_text(draw, (px + 3, y0 + 240), label, size=12)
        px += 60

    _draw_text(draw, (x0 + 20, y0 + 275),
               f"URL: http://{cfg.HTTP_IP}:{cfg.HTTP_PORT}", size=14)

    btn_label = "Stop" if running else "Start"
    _rect(draw, [x0 + 40, y0 + 310, x0 + 220, y0 + 360], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 90, y0 + 325), btn_label, size=22)

    _rect(draw, [x0 + 240, y0 + 310, x0 + 420, y0 + 360], outline=cfg.BLACK)
    _draw_text(draw, (x0 + 290, y0 + 325), "Test", size=22)

    _draw_text(draw, (x0 + 20, y0 + 380),
               "SSH to set custom IP/user/pwd", size=12)

    _rect(draw, (x0 + 180, y0 + 410, x0 + 280, y0 + 445), outline=cfg.BLACK)
    _draw_text(draw, (x0 + 215, y0 + 416), _("close"), size=18)


def kdap_handle_http_panel(lx, ly, state, cfg):
    pw, ph = 460, 460
    x0 = (cfg.logic_w - pw) // 2
    y0 = (cfg.logic_h - ph) // 2

    if not (x0 <= lx <= x0 + pw and y0 <= ly <= y0 + ph):
        state.show_http_panel = False
        return

    if x0 + 180 <= lx <= x0 + 280 and y0 + 410 <= ly <= y0 + 445:
        state.show_http_panel = False
        return

    if x0 + 40 <= lx <= x0 + 220 and y0 + 310 <= ly <= y0 + 360:
        if kdap_http_running():
            kdap_http_stop()
        else:
            kdap_http_start(cfg)
        return

    if x0 + 240 <= lx <= x0 + 420 and y0 + 310 <= ly <= y0 + 360:
        pipe = os.path.join(cfg.base, "kdap_http_pipe")
        if not os.path.exists(pipe):
            os.mkfifo(pipe)
        try:
            fd = os.open(pipe, os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, b"HTTP Test\n")
            os.close(fd)
        except Exception:
            pass
        return

    # 端口
    if x0 + 140 <= lx <= x0 + 175 and y0 + 115 <= ly <= y0 + 140:
        kdap_http_configure(cfg, port=min(65535, cfg.HTTP_PORT + 1))
    if x0 + 180 <= lx <= x0 + 215 and y0 + 115 <= ly <= y0 + 140:
        kdap_http_configure(cfg, port=max(1, cfg.HTTP_PORT - 1))

    # IP
    ip_presets = _get_ip_presets(cfg)
    if x0 + 200 <= lx <= x0 + 235 and y0 + 80 <= ly <= y0 + 105:
        idx = getattr(state, '_ip_idx', 0)
        idx = (idx - 1) % len(ip_presets)
        state._ip_idx = idx
        kdap_http_configure(cfg, ip=ip_presets[idx])
    if x0 + 240 <= lx <= x0 + 275 and y0 + 80 <= ly <= y0 + 105:
        idx = getattr(state, '_ip_idx', 0)
        idx = (idx + 1) % len(ip_presets)
        state._ip_idx = idx
        kdap_http_configure(cfg, ip=ip_presets[idx])

    # 用户名
    users = ["", "kdap", "kindle", "admin"]
    ux = x0 + 90
    for u in users:
        if ux <= lx <= ux + 55 and y0 + 182 <= ly <= y0 + 200:
            kdap_http_configure(cfg, user=u)
        ux += 60

    # 密码
    pwds = ["", "kdap123", "kindle", "admin123"]
    px = x0 + 90
    for p in pwds:
        if px <= lx <= px + 55 and y0 + 237 <= ly <= y0 + 255:
            kdap_http_configure(cfg, pwd=p)
        px += 60
