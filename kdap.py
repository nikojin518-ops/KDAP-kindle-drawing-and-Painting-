#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDAP - Kindle Drawing & Painting
主入口
"""
import sys
sys.path.insert(0, "/mnt/us/kdap")

from core.config import KDAPConfig
from core.state import KDAPState
from core.canvas import KDAPCanvas
from core.brush import kdap_stroke
from core.text_tool import render_text_to_layer, get_pipe_text
from core.i18n import kdap_i18n_init, _, set_language

from ui.render import kdap_render
from ui.menu import kdap_draw_menu
from ui.panels import (
    kdap_handle_settings, kdap_handle_size_panel,
    kdap_handle_text_panel, kdap_handle_text_input,
    kdap_handle_save_dialog, kdap_handle_load_dialog,
    kdap_handle_lang_picker, kdap_handle_layers_panel,
    kdap_handle_http_panel, kdap_draw_http_panel,
)
from ui.keyboard import (
    kbd_rect, kbd_hit, kbd_on_key,
    kdap_draw_keyboard, kbd_is_visible,
)

from input.touch import kdap_find_touch, kdap_read_events
from input.events import kdap_handle_menu_tap, kdap_tap_tool

from kio.save import kdap_save_png, kdap_save_kdap
from kio.load import kdap_load_kdap, kdap_list_files

from core.fb import kdap_init_fb, kdap_blit_full, kdap_blit_partial
import numpy as np
import time
import os


def kdap_map_touch(rx, ry, cfg):
    if cfg.orientation == "landscape":
        return (int(ry * cfg.logic_w / 1072),
                int(rx * cfg.logic_h / 1448))
    return (int(rx * cfg.logic_w / 1448),
            int(ry * cfg.logic_h / 1072))


def main():
    kdap_init_fb()
    cfg = KDAPConfig()
    state = KDAPState(cfg)
    canvas = KDAPCanvas(cfg)
    kdap_i18n_init(state)

    # 启动自检：依赖缺失时清屏提示并退出，避免黑屏卡死
    from core.fb import fbink_available
    ok, info = fbink_available()
    if not ok:
        print(f"[KDAP] {info}", flush=True)
        try:
            import subprocess
            fb = "/mnt/us/kdap/bin/fbink"
            if not os.access(fb, os.X_OK):
                fb = shutil.which("fbink") or shutil.which("FBInk") or fb
            subprocess.run([fb, "-c", "-f", "-W", "GC16",
                            "-m",
                            "KDAP: fbink missing. Place K5/bin/fbink at /mnt/us/kdap/bin/fbink"],
                           check=False, capture_output=True)
        except Exception:
            pass
        return 2

    device = kdap_find_touch()
    if device is None:
        print("No touch device found!", file=sys.stderr)
        return 1

    # 首次启动语言选择
    if state.first_run:
        state.show_lang_picker = True

    kdap_blit_full(kdap_render(canvas, state, cfg))

    last_pos = None
    drawing = False
    http_wait_start = None

    for ev_type, rx, ry in kdap_read_events(device):
        # 坐标映射
        if rx is not None and ry is not None:
            lx, ly = kdap_map_touch(rx, ry)
        else:
            lx, ly = None, None

        # 软键盘优先处理
        if state.kb_visible:
            if ev_type == "down" and lx is not None and ly is not None:
                kid = kbd_hit(lx, ly, state, cfg)
                if kid:
                    kbd_on_key(kid, state, cfg, canvas)
                    if kid == "enter" and state.kb_mode != "cn":
                        canvas.snapshot()
                        render_text_to_layer(
                            canvas.active_layer().pixels,
                            state.insert_x, state.insert_y,
                            state._pending_commit_text, state)
                        state._pending_commit_text = ""
                    kdap_blit_full(kdap_render(canvas, state, cfg))
            continue

        # 浮层面板优先
        if state.show_lang_picker:
            if ev_type == "down":
                kdap_handle_lang_picker(lx, ly, state, cfg)
            continue
        if state.show_save_dialog:
            if ev_type == "down":
                kdap_handle_save_dialog(lx, ly, state, canvas, cfg)
            continue
        if state.show_load_dialog:
            if ev_type == "down":
                kdap_handle_load_dialog(lx, ly, state, canvas, cfg)
            continue
        if state.show_text_input:
            if ev_type == "down":
                kdap_handle_text_input(lx, ly, state, canvas, cfg)
            continue
        if state.show_http_panel:
            if ev_type == "down":
                kdap_handle_http_panel(lx, ly, state, cfg)
            continue
        if state.show_text_panel:
            if ev_type == "down":
                from ui.panels import kdap_handle_text_panel
                kdap_handle_text_panel(lx, ly, state, cfg)
            continue
        if state.show_size_panel:
            if ev_type == "down":
                kdap_handle_size_panel(lx, ly, state, cfg)
            continue
        if state.show_layers_panel:
            if ev_type == "down":
                kdap_handle_layers_panel(lx, ly, state, cfg, canvas)
            continue
        if state.show_settings:
            if ev_type == "down":
                kdap_handle_settings(lx, ly, state, cfg)
            continue

        # HTTP 等待模式
        if getattr(state, 'waiting_http_text', False):
            from kio.httpd import kdap_get_http_text
            http_text = kdap_get_http_text()
            if http_text:
                canvas.snapshot()
                render_text_to_layer(
                    canvas.active_layer().pixels,
                    state.text_insert_pos[0], state.text_insert_pos[1],
                    http_text, state)
                state.waiting_http_text = False
                http_wait_start = None
                kdap_blit_full(kdap_render(canvas, state, cfg))
                continue
            if http_wait_start is None:
                http_wait_start = time.time()
            elif time.time() - http_wait_start > 30:
                state.waiting_http_text = False
                http_wait_start = None
                kdap_blit_full(kdap_render(canvas, state, cfg))
            continue

        # 设置图标
        if ly is not None and ly < cfg.ui_top_h and lx is not None and lx > cfg.logic_w - 80:
            if ev_type == "down":
                state.show_settings = True
                kdap_blit_full(kdap_render(canvas, state, cfg))
            continue

        # 菜单区
        if lx is not None and lx < cfg.menu_w:
            if ev_type == "down":
                kdap_handle_menu_tap(lx, ly, state, cfg, canvas)
                kdap_blit_full(kdap_render(canvas, state, cfg))
            continue

        # 画布区
        if lx is None or ly is None:
            continue

        cx = lx - cfg.canvas_x
        cy = ly - cfg.canvas_y

        if ev_type == "down":
            if state.tool == cfg.TOOL_TEXT:
                state.text_insert_pos = (cx, cy)
                state.insert_x = cx
                state.insert_y = cy
                state.show_text_input = True
                kdap_blit_full(kdap_render(canvas, state, cfg))
                continue
            drawing = True
            last_pos = (cx, cy)
            canvas.snapshot()

        elif ev_type == "move" and drawing and last_pos:
            layer = canvas.active_layer()
            if state.tool == cfg.TOOL_PEN:
                kdap_stroke(layer.pixels, last_pos[0], last_pos[1], cx, cy,
                            state.pen_size, state.brush_hardness)
            elif state.tool == cfg.TOOL_ERASER:
                kdap_stroke(layer.pixels, last_pos[0], last_pos[1], cx, cy,
                            state.eraser_size, erase=True)
            elif state.tool == cfg.TOOL_MOVE:
                dx, dy = cx - last_pos[0], cy - last_pos[1]
                layer.pixels = np.roll(np.roll(layer.pixels, dy, axis=0), dx, axis=1)
            last_pos = (cx, cy)
            kdap_blit_partial(kdap_render(canvas, state, cfg),
                              x=cfg.canvas_x, y=cfg.canvas_y,
                              w=cfg.canvas_w, h=cfg.canvas_h)

        elif ev_type == "up":
            drawing = False
            if state.tool == cfg.TOOL_BUCKET:
                canvas.flood_fill(cx, cy, cfg.BLACK)
            kdap_blit_full(kdap_render(canvas, state, cfg))
            last_pos = None

    return 0


if __name__ == "__main__":
    sys.exit(main())
