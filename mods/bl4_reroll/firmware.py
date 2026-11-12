# -*- coding: utf-8 -*-
"""Replace only firmware using the existing equipment catalogs, never weapon parts."""
from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from functools import cache
from importlib import resources

from . import legendary, reroll as stats, serial as sn, serialgen

# Class mod, repkit, ordnance, grenade, shield, enhancement. Heavy ordnance is a gadget,
# unlike firearms (whose inherited weapon table is deliberately not on this allowlist).
BASES = frozenset({234, 243, 244, 245, 246, 247})


# Enhancement is not in legendaries.json. Its firmware child IDs were checked against
# the serial part identities in Borderlands4-SaveEditor's data/item/item_name_index.json.
# These are real serial IDs, NOT zero-based positions in firmware_names.json.
_ENHANCEMENT_KEYS = {
    1: "fw_god_killer", 2: "fw_reel_big_fist", 3: "fw_lifeblood", 4: "fw_airstrike",
    5: "fw_high_caliber", 6: "fw_gadget_ahoy", 7: "fw_baker", 8: "fw_oscar_mike",
    9: "fw_rubberband_man", 10: "fw_deadeye", 11: "fw_action_fist", 12: "fw_goojfc",
    13: "fw_atlas_ex", 14: "fw_atlas_infinum", 15: "fw_trickshot", 16: "fw_jacked",
    17: "fw_get_throwin", 18: "fw_heating_up", 19: "fw_bullets_to_spare", 20: "fw_daeddy_o",
    103: "fw_risky_boots", 248: "fw_raid1_skillcraft", 249: "fw_raid2_activefire", 250: "fw_tuba_bruiser",
}
_WEIGHT_ALIASES = {
    "getthrowd": "fw_get_throwin", "skillcraft": "fw_raid1_skillcraft",
    "activefire": "fw_raid2_activefire", "bruiser": "fw_tuba_bruiser",
}
_OWNERS = {234: "classmod", 243: "repair_kit", 244: "heavy_weapon_gadget",
           245: "grenade_gadget", 246: "shield"}


@cache
def names() -> dict:
    """Ordered display catalog only; never use its labels to generate or identify parts."""
    try:
        data = json.loads(resources.files(__package__).joinpath("firmware_names.json").read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _label(key: str | None, fallback: str) -> str:
    entry = names().get(key, {})
    if isinstance(entry, dict):
        for field in ("cn_name", "name"):
            text = entry.get(field)
            if isinstance(text, str) and text.strip():
                return text.strip()
    return fallback


def name(ordinal: int) -> str:
    """Zero-based catalog position: 0 is fw_action_fist in the supplied JSON."""
    keys = tuple(names())
    if type(ordinal) is not int or not 0 <= ordinal < len(keys):
        return f"未知固件（序号 {ordinal}）"
    return _label(keys[ordinal], keys[ordinal])


def _normalized(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalnum())


@cache
def _part_keys(base: int) -> dict[int, str]:
    if base == 247:
        return _ENHANCEMENT_KEYS.copy()
    if base not in _OWNERS:
        return {}
    # Attribute identity, rather than candidate position: raid firmware ordering differs
    # from the display JSON, and each equipment family has its own part IDs.
    weights = {_normalized(key.removeprefix("fw_")): key for key in names()}
    weights.update(_WEIGHT_ALIASES)
    out = {}
    for row in serialgen._table(_OWNERS[base])["parts"]["firmware"]:
        if len(row) < 5 or type(row[4]) is not int:
            continue
        attr = serialgen._file()["values"][row[4]].get("a", "")
        token = _normalized(attr.removeprefix("firmware_").removesuffix("_weight"))
        key = weights.get(token)
        if key:
            out[row[0]] = key
    return out


def part_name(base: int | None, index: int | None) -> str:
    """Resolve a real (table, child ID) to the display catalog; never index JSON by child ID."""
    if index is None:
        return "无固件"
    fallback = f"固件（{base}:{index}）"
    try:
        key = _part_keys(base).get(index)
    except (KeyError, IndexError, TypeError, ValueError):
        return fallback
    return _label(key, fallback)


@dataclass
class Options:
    parsed: sn.Serial
    base: int | None = None
    current: int | None = None
    location: tuple[int, int | None] | None = None
    choices: tuple[int, ...] = ()
    reason: str = ""


def _number(spec: float | int, resolve: serialgen.Resolve) -> float:
    value = float(resolve(serialgen._file()["values"][spec]) if type(spec) is int else spec)
    if not math.isfinite(value):
        raise ValueError("invalid firmware weight or level gate")
    return value


def options(serial: str, resolve: serialgen.Resolve) -> Options:
    """Other valid firmware indices, or a non-actionable explanation. Never mutate a cached item."""
    parsed = sn.decode(serial)
    out = Options(parsed)
    legend = legendary.read(serial)
    info = stats.data()["types"].get(str(parsed.item_type))
    rows = []
    allow = None
    if legend is not None:
        inv = legend.key.partition(".")[0]
        typ = serialgen._type(inv)
        bases = [serialgen._table(owner)["ti"] for owner in typ["chain"]
                 if serialgen._table(owner)["ti"] in BASES]
        if len(bases) != 1 or "firmware" not in typ["slots"]:
            out.reason = "枪械或此物品类型不支持随机固件。"
            return out
        out.base = bases[0]
        rule = typ["items"][legend.key]["rules"].get("firmware", [1, 1, None, None])
        if rule[1] < 1:
            out.reason = "此装备的生成规则不允许安装固件。"
            return out
        allow = rule[3]
        rows = list(serialgen._candidates(inv, "firmware"))
    elif info is not None and info["base"] in (234, 247):
        out.base = info["base"]
        if out.base == 234:
            # Regular class mods share the exact same firmware table as legendary class mods.
            for row in serialgen._table("classmod")["parts"]["firmware"]:
                full = row + [[], [], [], 1.0, 0.0][len(row) - 1:]
                rows.append((234, full[0], *full[1:]))
        else:
            # parts.json explicitly enumerates enhancement firmware. It has no per-entry
            # weights, so this dedicated action picks uniformly from that authoritative list.
            gate = float(resolve({"a": "Att_MinGameStage_Firmware"}))
            if not math.isfinite(gate):
                raise ValueError("invalid firmware level gate")
            rows = [(247, i, 0, 0, 0, 1.0, gate) for i in stats.data()["bases"]["247"]["firmware"]]
    else:
        out.reason = "枪械或此物品类型不支持随机固件。"
        return out

    if any(table != out.base or type(index) is not int or add or dep or exc
           for table, index, add, dep, exc, _, _ in rows):
        # Current firmware rows have no tags. Don't guess how a future tagged firmware would
        # affect preserved skills/stats/other parts; require updated rules instead.
        out.reason = "固件表包含未支持的规则，无法安全修改。"
        return out
    known = {row[1] for row in rows}
    found = []
    for token_index, token in enumerate(parsed.tokens):
        if not isinstance(token, sn.Part) or token.index != out.base:
            continue
        if token.values is not None:
            found.extend((token_index, i, value.value) for i, value in enumerate(token.values) if value.value in known)
        elif token.value in known:
            found.append((token_index, None, token.value))
    if len(found) > 1:
        out.reason = "检测到多个固件，无法安全修改。"
        return out
    if found:
        token_index, value_index, out.current = found[0]
        out.location = (token_index, value_index)
    choices = []
    for i in range(len(rows)) if allow is None else allow:
        _, index, _, _, _, weight, gate = rows[i]
        if index == out.current or _number(gate, resolve) > parsed.level or _number(weight, resolve) <= 0:
            continue
        choices.append(index)
    out.choices = tuple(sorted(set(choices)))
    if not out.choices:
        out.reason = "该装备没有其他可用固件（固定固件、候选为空或未达到等级要求）。"
    return out


def reroll(serial: str, rng: random.Random, resolve: serialgen.Resolve) -> str:
    """Change exactly one firmware (or add one in an allowed empty slot); keep the entire rest."""
    choice = options(serial, resolve)
    if not choice.choices:
        raise ValueError(choice.reason or "没有其他可用固件。")
    index = rng.choice(choice.choices)
    parsed = choice.parsed
    if choice.location is None:
        first = next((i for i, t in enumerate(parsed.tokens) if isinstance(t, sn.Part)), None)
        if first is None:
            raise ValueError("装备没有有效的部件列表。")
        end = next((i for i in range(first, len(parsed.tokens))
                    if isinstance(parsed.tokens[i], sn.Sep) and parsed.tokens[i].hard), len(parsed.tokens))
        parsed.tokens.insert(end, sn.Part(choice.base, value=index))
    else:
        token_index, value_index = choice.location
        token = parsed.tokens[token_index]
        if value_index is None:
            token.value, token.value_groups = index, None
        else:
            old = token.values[value_index]
            token.values[value_index] = sn.Num(index, varbit=old.varbit)
    result = sn.encode(parsed)
    if str(sn.decode(result)) != str(parsed):
        raise ValueError("更换固件后的序列号校验失败。")
    return result
