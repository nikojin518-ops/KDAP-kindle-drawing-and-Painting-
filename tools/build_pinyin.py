#!/usr/bin/env python3
"""
build_pinyin.py - 从 cc-cedict / 自定义词库生成 pinyin.json
用法: python3 build_pinyin.py [--cedict path] [--output data/pinyin.json] [--limit 30000]
"""
import os
import sys
import json
import re
import argparse
from collections import defaultdict

try:
    from pypinyin import lazy_pinyin, Style
    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False

# 内置拼音映射（Kindle 友好，无外部依赖时使用）
PINYIN_MAP = {
    "你": "ni", "好": "hao", "我": "wo", "是": "shi", "的": "de",
    "了": "le", "在": "zai", "和": "he", "有": "you", "大": "da",
    "这": "zhe", "中": "zhong", "国": "guo", "人": "ren", "他": "ta",
    "她": "ta", "它": "ta", "们": "men", "来": "lai", "到": "dao",
    "时": "shi", "间": "jian", "上": "shang", "下": "xia", "不": "bu",
    "要": "yao", "就": "jiu", "也": "ye", "对": "dui", "能": "neng",
    "会": "hui", "为": "wei", "以": "yi", "个": "ge", "可": "ke",
    "说": "shuo", "想": "xiang", "看": "kan", "去": "qu", "过": "guo",
    "起": "qi", "子": "zi", "而": "er", "么": "me", "什": "shen",
    "没": "mei", "还": "hai", "都": "dou", "把": "ba", "那": "na",
    "画": "hua", "笔": "bi", "图": "tu", "色": "se", "彩": "cai",
    "黑": "hei", "白": "bai", "红": "hong", "绿": "lv", "蓝": "lan",
    "黄": "huang", "青": "qing", "紫": "zi", "灰": "hui", "橙": "cheng",
    "字": "zi", "体": "ti", "文": "wen", "本": "ben", "删": "shan",
    "除": "chu", "移": "yi", "动": "dong", "复": "fu", "制": "zhi",
    "粘": "zhan", "贴": "tie", "选": "xuan", "区": "qu", "层": "ceng",
    "透": "tou", "明": "ming", "度": "du", "显": "xian", "隐": "yin",
    "新": "xin", "建": "jian", "打": "da", "开": "kai", "保": "bao",
    "存": "cun", "导": "dao", "出": "chu", "入": "ru", "设": "she",
    "置": "zhi", "退": "tui", "助": "zhu", "关": "guan", "于": "yu",
    "版": "ban", "本": "ben", "软": "ruan", "件": "jian", "硬": "ying",
    "系": "xi", "统": "tong", "语": "yu", "言": "yan",
}


def char_to_pinyin(char):
    if HAS_PYPINYIN:
        return lazy_pinyin(char, style=Style.NORMAL)[0]
    return PINYIN_MAP.get(char, char)


def word_to_pinyin(word):
    if HAS_PYPINYIN:
        return "".join(lazy_pinyin(word, style=Style.NORMAL))
    return "".join(PINYIN_MAP.get(ch, ch) for ch in word)


def load_cedict(path):
    entries = []
    if not os.path.exists(path):
        return entries
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"(\S+)\s+(\S+)\s+\[(.+?)\]\s+/(.+?)/", line)
            if m:
                trad, simp, pinyin_str, trans = m.groups()
                word = simp
                py = re.sub(r'\d', '', pinyin_str).replace(' ', '')
                entries.append((word, py))
    return entries


def load_custom_words(path):
    entries = []
    if not os.path.exists(path):
        return entries
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                word, py = parts[0], parts[1]
                entries.append((word, py))
            elif len(parts) == 1:
                word = parts[0]
                py = word_to_pinyin(word)
                entries.append((word, py))
    return entries


def build_pinyin_json(cedict_path=None, custom_path=None, output_path="data/pinyin.json", limit=30000):
    db = defaultdict(list)

    if cedict_path and os.path.exists(cedict_path):
        print(f"Loading cc-cedict from {cedict_path}...")
        entries = load_cedict(cedict_path)
        for word, py in entries:
            if len(word) <= 4:
                db[py].append(word)
        print(f"  Loaded {len(entries)} entries")

    if custom_path and os.path.exists(custom_path):
        print(f"Loading custom words from {custom_path}...")
        entries = load_custom_words(custom_path)
        for word, py in entries:
            if word not in db[py]:
                db[py].append(word)
        print(f"  Loaded {len(entries)} entries")

    print("Adding built-in character mapping...")
    for char, py in PINYIN_MAP.items():
        if char not in db[py]:
            db[py].insert(0, char)

    result = {}
    for py, words in db.items():
        seen = set()
        unique_words = []
        for w in words:
            if w not in seen:
                seen.add(w)
                unique_words.append(w)
        result[py] = unique_words[:10]

    sorted_result = dict(sorted(result.items(), key=lambda x: (len(x[0]), x[0])))

    if len(sorted_result) > limit:
        items = list(sorted_result.items())[:limit]
        sorted_result = dict(items)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sorted_result, f, ensure_ascii=False, separators=(',', ':'))

    print(f"Done! Generated {len(sorted_result)} pinyin entries -> {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    return sorted_result


def main():
    parser = argparse.ArgumentParser(description="Build pinyin.json for KDAP")
    parser.add_argument("--cedict", help="Path to cc-cedict file")
    parser.add_argument("--custom", help="Path to custom words file")
    parser.add_argument("--output", default="data/pinyin.json", help="Output path")
    parser.add_argument("--limit", type=int, default=30000, help="Max entries")
    args = parser.parse_args()

    build_pinyin_json(
        cedict_path=args.cedict,
        custom_path=args.custom,
        output_path=args.output,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
