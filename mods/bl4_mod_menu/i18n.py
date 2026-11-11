# -*- coding: utf-8 -*-
"""Chinese presentation only. Status checks, setting values and actions stay untouched."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib import resources


@lru_cache(maxsize=1)
def _catalog() -> tuple[dict[str, str], list[tuple[re.Pattern[str], str]]]:
    try:
        data = json.loads((resources.files(__package__) / "ui" / "zh.json").read_text("utf-8"))
    except (OSError, ValueError):
        return {}, []
    rules = []
    for source, target in data.get("templates", {}).items():
        pieces = re.split(r"(\{\d+\})", source)
        pattern = "".join(r"([\s\S]*?)" if re.fullmatch(r"\{\d+\}", p) else re.escape(p) for p in pieces)
        rules.append((re.compile(pattern), target))
    return data.get("exact", {}), rules


def _translate(value: str, depth: int) -> str:
    exact, rules = _catalog()
    if value in exact:
        return exact[value]
    if depth < 4 and len(value) <= 16384:
        for regex, target in rules:
            match = regex.fullmatch(value)
            if match:
                values = [_translate(part, depth + 1) for part in match.groups()]
                return re.sub(r"\{(\d+)\}", lambda m: values[int(m[1])], target)
        if "\n" in value:
            return "\n".join(_translate(line, depth + 1) for line in value.split("\n"))
    return value


@lru_cache(maxsize=1024)
def text(value: str) -> str:
    return _translate(value, 0)
