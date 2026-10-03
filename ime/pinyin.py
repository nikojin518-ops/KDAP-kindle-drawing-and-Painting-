#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDAP 拼音输入法"""
import os

BASE = "/mnt/us/kdap"
PINYIN_DB = os.path.join(BASE, "data", "pinyin.json")

_cache = None


def load_db():
    global _cache
    if _cache is None:
        if os.path.exists(PINYIN_DB):
            import json
            with open(PINYIN_DB, "r", encoding="utf-8") as f:
                _cache = json.load(f)
        else:
            _cache = {
                "ni": ["你", "呢", "尼"],
                "nihao": ["你好", "你号"],
                "wo": ["我", "窝"],
                "shi": ["是", "时", "十"],
                "de": ["的", "得"],
                "zhongguo": ["中国", "种过"],
                "huahua": ["画画", "花花"],
                "kindle": ["Kindle", "金读"],
                "ai": ["爱", "矮", "碍"],
                "hen": ["很", "痕"],
                "hao": ["好", "号", "豪"],
                "me": ["么", "吗", "嘛"],
                "xiexie": ["谢谢"],
                "qing": ["请", "青", "清"],
                "wen": ["问", "文", "闻"],
            }
    return _cache


def query(pinyin):
    db = load_db()
    if pinyin in db:
        val = db[pinyin]
        return val if isinstance(val, list) else [val]
    for k, v in db.items():
        if pinyin.startswith(k):
            return v[:5] if isinstance(v, list) else [v]
    return []
