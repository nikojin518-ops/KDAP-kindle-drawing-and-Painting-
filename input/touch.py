#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 触摸输入"""
try:
    import evdev
    HAVE_EVDEV = True
except ImportError:
    evdev = None
    HAVE_EVDEV = False


def kdap_find_touch():
    if not HAVE_EVDEV:
        return None


def kdap_find_touch():
    for path in evdev.list_devices():
        try:
            d = evdev.InputDevice(path)
            caps = d.capabilities()
            if evdev.ecodes.EV_ABS in caps:
                abs_caps = caps[evdev.ecodes.EV_ABS]
                codes = [c[0] for c in abs_caps]
                if evdev.ecodes.ABS_MT_POSITION_X in codes:
                    return d
        except Exception:
            continue
    for path in evdev.list_devices():
        try:
            return evdev.InputDevice(path)
        except Exception:
            continue
    return None


def kdap_read_events(device):
    if device is None:
        return
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == evdev.ecodes.ABS_MT_POSITION_X:
                yield ("move", event.value, None)
            elif event.code == evdev.ecodes.ABS_MT_POSITION_Y:
                yield ("move", None, event.value)
        elif event.type == evdev.ecodes.EV_KEY:
            if event.code == evdev.ecodes.BTN_TOUCH:
                if event.value == 1:
                    yield ("down", None, None)
                elif event.value == 0:
                    yield ("up", None, None)
