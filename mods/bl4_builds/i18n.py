# -*- coding: utf-8 -*-
"""UI-only Chinese labels. Never rewrites build files, item serials or protocol IDs."""
from functools import lru_cache
from importlib.resources import files
import json
import re

@lru_cache(maxsize=1)
def _data():
    return json.loads(files(__package__).joinpath("i18n.json").read_text(encoding="utf-8"))

@lru_cache(maxsize=1)
def _patterns():
    return [(re.compile(pattern), replacement) for pattern, replacement in _data()["patterns"]]

def translate(text):
    if not isinstance(text, str):
        return text
    data = _data()
    if text in data["phrases"]:
        return data["phrases"][text]
    if text in data["labels"]:
        return data["labels"][text]
    for pattern, replacement in _patterns():
        if pattern.fullmatch(text):
            result = pattern.sub(replacement, text)
            # Translate the generated slot prefix, not quoted item/build names.
            result = re.sub(r"^Weapon (\d+)：", r"武器 \1：", result)
            if "：" in result:
                prefix, rest = result.split("：", 1)
                result = data["labels"].get(prefix, prefix) + "：" + data["phrases"].get(rest, rest)
            return result
    return text

def equipment(text):
    result = translate(text)
    if result != text or not isinstance(text, str):
        return result
    # Only generated descriptions consisting entirely of known labels are split.
    remainder = text
    parts = []
    labels = sorted(_data()["labels"], key=len, reverse=True)
    while remainder:
        label = next((key for key in labels if remainder == key or remainder.startswith(key + " ")), None)
        if label is None:
            return text
        parts.append(_data()["labels"][label])
        remainder = remainder[len(label):].strip()
    return " ".join(parts)

def squares(rows):
    result = []
    for row in rows:
        shown = dict(row)
        shown["cn_action"] = translate(row.get("action"))
        shown["cn_specs"] = " · ".join(_spec(part) for part in (row.get("specs") or "").split(" · "))
        shown["gear"] = [dict(g, cn_slot=translate(g.get("slot")),
                                cn_label=equipment(g.get("label")), cn_desc=equipment(g.get("desc")))
                         for g in row.get("gear", [])]
        shown["trees"] = [dict(t, cn_name=translate(t.get("name"))) for t in row.get("trees", [])]
        result.append(shown)
    return result

def _spec(text):
    found = re.fullmatch(r"(.+) (\d+)", text)
    if found:
        return translate(found[1]) + " " + found[2]
    return translate(text)
