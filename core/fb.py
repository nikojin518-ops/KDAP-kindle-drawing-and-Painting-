#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDAP 帧缓冲输出（FBInk）
v1.8：自动探测 fbink 路径（优先小写，兼容大写 FBInk），结果缓存，
      启动时一次性自检，失败时给出明确日志而不是静默崩溃。
"""
import subprocess
import os
import shutil

# 探测结果缓存：None 表示尚未探测，"<missing>" 表示探测失败
_fbink_path = None
_fbink_checked = False


def _detect_fbink():
    """按顺序探测 fbink 可执行文件，返回路径或 None。"""
    # 1) 项目自带（最高优先级，解压即用的关键）
    local = os.path.join(os.path.dirname(__file__), "..", "bin", "fbink")
    local = os.path.abspath(local)
    if os.path.isfile(local) and os.access(local, os.X_OK):
        return local

    # 2) PATH 里的小写 fbink（NiLuJe 实际安装名）
    found = shutil.which("fbink")
    if found:
        return found

    # 3) 大写 FBInk 兼容（老脚本习惯）
    found = shutil.which("FBInk")
    if found:
        return found

    # 4) 常见手动安装位置兜底
    for p in ("/usr/local/bin/fbink", "/usr/bin/fbink", "/mnt/us/fbink"):
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None


def get_fbink():
    """返回 fbink 可执行路径；已探测过则直接返回缓存结果。"""
    global _fbink_path, _fbink_checked
    if _fbink_checked:
        return None if _fbink_path == "<missing>" else _fbink_path
    _fbink_path = _detect_fbink() or "<missing>"
    _fbink_checked = True
    return None if _fbink_path == "<missing>" else _fbink_path


def reset_fbink_cache():
    """调试用：清空缓存，重新探测（比如用户中途补装了 fbink）。"""
    global _fbink_path, _fbink_checked
    _fbink_path = None
    _fbink_checked = False


def fbink_available():
    """返回 (bool, path_or_reason)，供启动自检显示。"""
    path = get_fbink()
    if path:
        return True, path
    return False, "fbink not found in PATH or /mnt/us/kdap/bin/"


def _run(args):
    """内部调用：跑 fbink，失败不抛异常，写入日志。"""
    path = get_fbink()
    if not path:
        print("[fb] fbink unavailable, skipping blit", flush=True)
        return False
    try:
        subprocess.run([path, *args], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"[fb] fbink error: {e}", flush=True)
        return False


def kdap_init_fb():
    """初始化帧缓冲：自检 fbink，清屏一次确认可用。"""
    ok, info = fbink_available()
    if not ok:
        print(f"[fb] WARNING: {info} —— KDAP 将无法输出画面。"
              f"请安装 FBInk（NiLuJe/FBInk 的 FBInk-x.x.x-Kindle.zip，"
              f"取 K5/bin/fbink 放到 /mnt/us/kdap/bin/fbink 并 chmod +x）",
              flush=True)
        return False
    print(f"[fb] using fbink: {info}", flush=True)
    # 显示版本并清屏，验证真的能画出来
    _run(["--version"])
    _run(["-c", "-f", "-W", "GC16", "-m", "KDAP v1.8 Ready"])
    return True


def _to_ppm(img, path):
    """把灰度图保存为 PPM（FBInk 的 -g 能直接吃 PPM）。"""
    if img.mode != "L":
        img = img.convert("L")
    img.save(path, "PPM")


def kdap_blit_full(img):
    """全刷：完整画面，GC16 波形保证灰度到位。"""
    path = "/tmp/kdap_frame.ppm"
    _to_ppm(img, path)
    _run(["-c", "-f", "-W", "GC16", "-g", f"0,0,{path}"])
    try:
        os.remove(path)
    except OSError:
        pass


def kdap_blit_partial(img, x=0, y=0, w=0, h=0):
    """局部刷：A2 快速波形，适合跟手绘制。"""
    if w <= 0 or h <= 0:
        kdap_blit_full(img)
        return
    path = "/tmp/kdap_partial.ppm"
    _to_ppm(img, path)
    _run(["-c", "-a", "-g", f"{x},{y},{path}"])
    try:
        os.remove(path)
    except OSError:
        pass
