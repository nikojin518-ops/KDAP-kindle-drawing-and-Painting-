#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 国际化"""
import json
import os

BASE = "/mnt/us/kdap"
LANG_DIR = os.path.join(BASE, "lang")

_current_lang = "en"
_strings = {}


def kdap_i18n_init(state):
    global _current_lang, _strings
    lang = state.cfg.lang
    path = os.path.join(LANG_DIR, f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join(LANG_DIR, "en.json")
    with open(path, "r", encoding="utf-8") as f:
        _strings = json.load(f)


def set_language(lang):
    global _current_lang, _strings
    _current_lang = lang
    path = os.path.join(LANG_DIR, f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join(LANG_DIR, "en.json")
    with open(path, "r", encoding="utf-8") as f:
        _strings = json.load(f)
    cfg_path = os.path.join(BASE, "kdap.conf")
    try:
        with open(cfg_path, "r") as f:
            d = json.load(f)
    except Exception:
        d = {}
    d["lang"] = lang
    with open(cfg_path, "w") as f:
        json.dump(d, f)


def _(key):
    return _strings.get(key, key)
