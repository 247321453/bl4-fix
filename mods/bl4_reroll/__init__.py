# -*- coding: utf-8 -*-
"""
Reroll for Borderlands 4: reroll the modifiers at the bottom of a class mod or enhancement (the
stat lines like "+12% Gun Damage"), or a whole legendary or pearl, for Eridium.

- Reroll all: 25 Eridium. Every modifier rolls again.
- Replace one: 50 Eridium. Pick a modifier; it changes to a different one, the rest stay.
- Reroll a legendary or pearl: 100 Eridium. A fresh drop of the same item at its level: every part
  the game rolls (element, barrel and body accessories, grip, scope, magazine, licensed parts,
  firmware, a class mod's skills) rolls again with the game's own weights, so rare parts stay
  rare (legendary.py). Its level and an applied cosmetic stay.

The prices are options (the host's count in co-op: its copy makes and charges every reroll).

The skills, manufacturer perks, firmware, level and rarity never change, and a legendary keeps the
stat it always comes with. New modifiers follow the game's own rules (see reroll.py), so a
rerolled item is one the game could have dropped.

The quickest way is from the item card (card.py): hover a class mod or enhancement in your
backpack and press T to reroll all its modifiers, or G to pick one (G again for the next) and then T
to replace just that one. On a legendary or pearl, T (twice) rerolls the whole item. The card plays
it as a slot machine. The card's script runs in the game's menu page through the BL4 UI Link
(uilink/, no Mod Menu needed).

Or open it from the mod menu (F7, or MODS in the pause menu): each class mod, enhancement,
legendary and pearl you carry has a page (a legendary class mod has both). Or from the console:
`reroll` lists them, `reroll 2` rerolls all of item 2's modifiers (a whole legendary), `reroll 2 1`
replaces its first one.

How the item changes is in native.py (in place, with the game's own functions, the way its
Firmware Transfer does it) and game.py (the fallback for other game builds: sell + mail); which
lines can change, and to what, is in reroll.py, from game data in parts.json
(tools/gen_reroll_parts.py); legendary rolls are in legendary.py + serialgen.py, from
legendaries.json (tools/gen_reroll_legendaries.py). If a game patch changes that data, rerolling
turns itself off until both are regenerated, rather than making items from stale tables.
"""

from __future__ import annotations

import argparse
import random
import sys
import threading
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from mods_base import (
    SETTINGS_DIR,
    BaseOption,
    ButtonOption,
    KeybindOption,
    NestedOption,
    SliderOption,
    ValueOption,
    build_mod,
    command,
)
from unrealsdk import logging

from . import card, firmware, frametick, game, legendary, menu_reroll, pak, reroll
from .i18n import item_label, item_name, rarity_name, stat_name

try:
    from bl4_direct import coop
except Exception:  # noqa: BLE001 - BL4 Direct missing or broken: solo/host only
    coop = None

__version__ = "0.2.0"
__version_info__ = (0, 2, 0)

FEATURE = "reroll"
SERVICE = "reroll.apply"
SYNC_LEVEL_SERVICE = "reroll.sync_level"
FIRMWARE_SERVICE = "reroll.firmware"
TARGET_FIRMWARE_SERVICE = "reroll.firmware_target"

GAME_DIR = SETTINGS_DIR.parent.parent
REFRESH_S = 0.5
# Whether the Mod Menu's screen shows is checked this often (it was every frame); its item pages
# are rebuilt at most this much later after it opens
MENU_CHECK_S = 0.1


def log(msg: str) -> None:
    logging.info(f"[Reroll] {msg}")


def tell(text: str, *, error: bool = False) -> None:
    """Shows a message in the mod menu if it's there, and in the console."""
    web = sys.modules.get("bl4_mod_menu.web")
    if web is not None:
        try:
            web.say(text, error=error)
            return
        except Exception:  # noqa: BLE001
            pass
    (logging.error if error else logging.info)(f"[Reroll] {text}")


# region Game data check

_data_ok: bool | None = None
_data_thread: threading.Thread | None = None


def _check_data() -> None:
    """On a worker thread (only files: reading 360 pak indexes takes most of a second)."""
    global _data_ok
    try:
        paks = sorted((GAME_DIR / "OakGame" / "Content" / "Paks").glob("*.pak"))
        # The class mod / enhancement tables and the legendary rules (the same inv files)
        prints = {**(reroll.data().get("source_data") or {}), **legendary.source_data()}
        ok = bool(prints) and all(
            (entry := pak.winning_entry(paks, path)) is not None and entry.sha1 == sha1
            for path, sha1 in prints.items()
        )
    except Exception as ex:  # noqa: BLE001 - can't tell: stay off rather than guess
        logging.error(f"[Reroll] Checking the game files failed: {ex!r}")
        ok = False
    if not ok:
        log("This game version changed the item data Reroll was made from, so it's off until it's updated.")
    _data_ok = ok


def start_data_check() -> None:
    global _data_thread
    if _data_ok is None and (_data_thread is None or not _data_thread.is_alive()):
        _data_thread = threading.Thread(target=_check_data, name="bl4_reroll.data_ok", daemon=True)
        _data_thread.start()


def data_ok() -> bool | None:
    """
    Whether the game files parts.json and legendaries.json were made from are unchanged (checked once per session, off
    the game thread), or None while that's still being checked.
    """
    if _data_ok is None:
        start_data_check()
    return _data_ok


# endregion
# region Rerolling


def _blocked() -> str | None:
    ok = data_ok()
    if ok is None:
        return "正在检查游戏文件，请稍后重试。"
    if not ok:
        return "当前游戏版本需要更新 BL4 Reroll 后才能使用。"
    if not game.is_host() and not _host_rerolls():
        return "联机时，房主也需要安装并启用 BL4 Reroll，才能重掷你的装备。"
    return None


def _host_rerolls() -> bool:
    """As a co-op client: the host's copy of this mod makes our rerolls."""
    return coop is not None and coop.is_client() and coop.host_has(FEATURE)


class Refused(Exception):
    """Why a reroll didn't happen (nothing was changed or paid)."""


@dataclass
class Plan:
    """A reroll that's been rolled but not made yet."""

    slot: game.Slot
    after: reroll.Item | legendary.Legend
    cost: int
    what: str  # "Rerolled: X is now Y."
    # What rolled it: the host rolls the same again for a co-op client's reroll and checks it matches
    kind: str = "all"
    line: int | None = None
    seed: int = field(default_factory=lambda: random.getrandbits(48))
    firmware_target: int | None = None  # actual child part ID, never a display-list index


@dataclass
class Outcome:
    before: reroll.Item | legendary.Legend
    after: reroll.Item | legendary.Legend
    equipped: bool  # it was equipped and now sits unequipped in the backpack (the slow swap)
    handle: int  # the new item's
    cost: int
    left: int
    message: str


def _slot(handle: int, serial: str | None) -> game.Slot:
    if (why := _blocked()) is not None:
        raise Refused(why)
    # Read live from the backpack (never the cache the menu and card show)
    slot = game.find(handle)
    if slot is None or (serial is not None and slot.item.serial != serial):
        S.signature = None
        game.invalidate(handle)
        raise Refused("该装备已发生变化，请重新查看后再试。")
    return slot


def _check(cost: int) -> None:
    have = game.balance()
    if have < cost:
        raise Refused(f"镒矿不足：需要 {cost}，当前拥有 {have}。")
    if _host_rerolls():
        return  # the host checks how it can swap
    if (why := game.can_replace()) is not None:
        raise Refused(why)


def plan_all(handle: int, serial: str | None = None, seed: int | None = None) -> Plan:
    """Rolls every free modifier again. Raises Refused if it can't."""
    slot = _slot(handle, serial)
    if isinstance(slot.item, legendary.Legend):
        raise Refused("传奇装备的部件需要整体重掷，无法逐个替换。")
    _check(cost_all())
    seed = random.getrandbits(48) if seed is None else seed
    new_serial = reroll.reroll_all(slot.item, random.Random(seed))
    after = reroll.read(new_serial) if new_serial else None
    if after is None:
        raise Refused("该装备没有可重掷的词条。")
    changes = [f"{stat_name(a.name)} → {stat_name(b.name)}" for a, b in zip(slot.item.lines, after.lines, strict=True) if a.part != b.part]
    return Plan(slot, after, cost_all(), f"重掷完成：{'；'.join(changes) if changes else '本次得到的词条与原来相同'}。",
                "all", None, seed)  # fmt: skip


def plan_one(handle: int, line: int, serial: str | None = None, seed: int | None = None) -> Plan:
    """Rolls one modifier into a different one. Raises Refused if it can't."""
    slot = _slot(handle, serial)
    if isinstance(slot.item, legendary.Legend):
        raise Refused("传奇装备的部件需要整体重掷，无法逐个替换。")
    if not 0 <= line < len(slot.item.lines):  # a negative line from a co-op request indexes from the end
        S.signature = None
        raise Refused("该装备已发生变化，请重新查看后再试。")
    old = slot.item.lines[line]
    if old.locked:
        raise Refused(f"{stat_name(old.name)} 是传奇装备自带的固定词条，无法单独重掷。")
    _check(cost_one())
    seed = random.getrandbits(48) if seed is None else seed
    new_serial = reroll.reroll_one(slot.item, line, random.Random(seed))
    after = reroll.read(new_serial) if new_serial else None
    if after is None:
        raise Refused(f"该装备上的 {stat_name(old.name)} 没有其他可替换词条。")
    return Plan(slot, after, cost_one(), f"已将 {stat_name(old.name)} 替换为 {stat_name(after.lines[line].name)}。", "one", line, seed)


def plan_legendary(handle: int, serial: str | None = None, seed: int | None = None) -> Plan:
    """Rolls a legendary or pearl again, as a fresh drop at its level. Raises Refused if it can't."""
    slot = _slot(handle, serial)
    item = legendary.read(slot.item.serial)
    if item is None:
        raise Refused("只有传奇和珠光装备可以整体重掷。")
    _check(cost_legendary())
    seed = random.getrandbits(48) if seed is None else seed
    try:
        new_serial = legendary.reroll(item, random.Random(seed), game.Values.resolve)
    except (ValueError, KeyError, IndexError) as ex:
        raise Refused(f"无法重掷 {item_name(item.name)}（{ex}），未进行任何更改。") from ex
    after = game.decode(new_serial)
    if after is None:
        raise Refused(f"无法重掷 {item_name(item.name)}，未进行任何更改。")
    kind = "pearl" if item.pearl else "legendary"
    return Plan(slot, after, cost_legendary(), f"已重掷 {item_name(item.name)}：重新生成了一件 {item.level} 级{'珠光' if kind == 'pearl' else '传奇'}装备。",
                "legendary", None, seed)  # fmt: skip


def plan_firmware(handle: int, serial: str | None = None, seed: int | None = None) -> Plan:
    """Replace just the firmware with another valid candidate, never reroll the other parts."""
    slot = _slot(handle, serial)
    seed = random.getrandbits(48) if seed is None else seed
    try:
        new_serial = firmware.reroll(slot.item.serial, random.Random(seed), game.Values.resolve)
        after = game.decode(new_serial)
    except (ValueError, KeyError, IndexError) as ex:
        raise Refused(f"无法随机固件：{ex}") from ex
    if after is None:
        raise Refused("无法读取更换固件后的装备，未进行任何更改。")
    cost = cost_legendary()
    _check(cost)
    before_fw = firmware.options(slot.item.serial, game.Values.resolve)
    after_fw = firmware.options(after.serial, game.Values.resolve)
    before_name = firmware.part_name(before_fw.base, before_fw.current)
    after_name = firmware.part_name(after_fw.base, after_fw.current)
    return Plan(slot, after, cost, f"已随机更换固件：{before_name} → {after_name}，装备等级及其他部件保持不变。",
                "firmware", None, seed)


def plan_firmware_target(handle: int, target: int, serial: str | None = None) -> Plan:
    """Pick a permitted firmware explicitly for ten times the random firmware fee."""
    slot = _slot(handle, serial)
    cost = cost_firmware_target()
    _check(cost)
    try:
        new_serial = firmware.set_firmware(slot.item.serial, target, game.Values.resolve)
        after = game.decode(new_serial)
        before_fw = firmware.options(slot.item.serial, game.Values.resolve)
        before_name = firmware.part_name(before_fw.base, before_fw.current)
        after_name = firmware.part_name(before_fw.base, target)
    except (ValueError, KeyError, IndexError) as ex:
        raise Refused(f"无法定向修改固件：{ex}") from ex
    if after is None:
        raise Refused("无法读取更换固件后的装备，未进行任何更改。")
    return Plan(slot, after, cost,
                f"已定向修改固件：{before_name} → {after_name}，装备等级及其他部件保持不变。",
                kind="firmware_target", firmware_target=target)


def plan_sync_level(handle: int, serial: str | None = None) -> Plan | None:
    """Raise this item's level to its owner's character level; never lower or reroll it."""
    slot = _slot(handle, serial)
    level = game.player_level()
    if level <= slot.item.level:
        return None
    cost = cost_legendary()
    _check(cost)
    try:
        new_serial = reroll.set_item_level(slot.item, level)
        after = game.decode(new_serial) if new_serial else None
    except (ValueError, KeyError, IndexError) as ex:
        raise Refused(f"无法同步装备等级（{ex}），未进行任何更改。") from ex
    if after is None or after.level != level:
        raise Refused("无法重新读取升级后的装备，未进行任何更改。")
    return Plan(slot, after, cost, f"已同步玩家等级：装备从 {slot.item.level} 级提升至 {level} 级。",
                "sync_level")


def apply(plan: Plan) -> Outcome:
    """Pays for and makes a planned reroll. Raises Refused or game.RerollError if it can't."""
    slot = _slot(plan.slot.handle, plan.slot.item.serial)
    if plan.kind == "sync_level":
        level = game.player_level()
        if plan.cost != cost_legendary() or level <= slot.item.level or plan.after.level != level:
            raise Refused("玩家等级或装备已发生变化，请重新查看后再试。")
    elif plan.kind == "firmware" and plan.cost != cost_legendary():
        raise Refused("整件重掷费用已发生变化，请重新查看后再试。")
    elif plan.kind == "firmware_target":
        # Recheck the live candidate rules and price immediately before replacement, including
        # on the host. A stale menu or forged target/result must never install an invalid part.
        expected = plan_firmware_target(slot.handle, plan.firmware_target, slot.item.serial)
        if expected.cost != plan.cost or expected.after.serial != plan.after.serial:
            raise Refused("固件候选、费用或装备已发生变化，请重新查看后再试。")
    _check(plan.cost)
    handle, equipped = game.replace(slot, plan.after.serial)
    left = game.set_balance(game.ERIDIUM, game.balance() - plan.cost)
    note = "装备现已放入背包，请重新装备。" if slot.equipped and not equipped else ""
    log(f"{slot.item.label} (handle {slot.handle} -> {handle}): {slot.item.serial} -> {plan.after.serial}")
    S.signature = None
    message = f"{plan.what} 本次消耗 {plan.cost} 镒矿，剩余 {left}。{note}"
    return Outcome(slot.item, plan.after, slot.equipped and not equipped, handle, plan.cost, left, message)


def _outcome_dict(outcome: Outcome) -> dict[str, Any]:
    return {"ok": True, "left": outcome.left, "equipped": outcome.equipped, "message": outcome.message}


def apply_async(plan: Plan, done: Callable[[dict[str, Any]], None]) -> None:
    """
    Makes a planned reroll. done() gets {"ok": True, "left", "equipped", "message"} or
    {"ok": False, "error"}: at once in solo or as host; later as a co-op client, whose rerolls the
    host's copy of this mod makes (the item and the Eridium belong to the host).
    """
    if not _host_rerolls():
        try:
            result = _outcome_dict(apply(plan))
        except (Refused, game.RerollError) as ex:
            result = {"ok": False, "error": str(ex)}
        done(result)
        return
    # Nothing is charged or changed here: the host rolls the same again from the seed, checks it
    # matches, then pays from our Eridium and swaps our item
    # Separate services fail safely on older hosts without level sync or firmware-only rerolls.
    service = (SYNC_LEVEL_SERVICE if plan.kind == "sync_level" else
               TARGET_FIRMWARE_SERVICE if plan.kind == "firmware_target" else
               FIRMWARE_SERVICE if plan.kind == "firmware" else SERVICE)
    payload = {
        "kind": plan.kind,
        "line": plan.line,
        "serial": plan.slot.item.serial,
        "seed": plan.seed,
        "after": plan.after.serial,
    }
    if plan.kind == "firmware_target":
        payload["firmware_target"] = plan.firmware_target
        payload["cost"] = plan.cost
    coop.request(service, payload,
                 lambda reply: (game.invalidate(plan.slot.handle), done(reply)), timeout=15.0)


def _serve(req: Any) -> dict[str, Any]:
    """On the host: a co-op friend's reroll, rolled again here from their seed."""
    if not mod.is_enabled:
        return {"ok": False, "error": "房主未启用 BL4 Reroll"}
    data = req.data
    with game.acting_for(req.pc):
        try:
            slot = game.find_serial(str(data["serial"]))
            if slot is None:
                return {"ok": False, "error": "该装备已发生变化，请重新查看后再试。"}
            seed = int(data["seed"])
            if data.get("kind") == "one":
                plan = plan_one(slot.handle, int(data["line"]), slot.item.serial, seed)
            elif data.get("kind") == "legendary":
                plan = plan_legendary(slot.handle, slot.item.serial, seed)
            elif data.get("kind") == "firmware":
                plan = plan_firmware(slot.handle, slot.item.serial, seed)
            elif data.get("kind") == "firmware_target":
                plan = plan_firmware_target(slot.handle, data["firmware_target"], slot.item.serial)
                if type(data.get("cost")) is not int or data["cost"] != plan.cost:
                    raise Refused("房主的定向修改费用与当前显示不同，请同步费用设置后再试。")
            elif data.get("kind") == "sync_level":
                plan = plan_sync_level(slot.handle, slot.item.serial)
                if plan is None:
                    raise Refused("玩家等级不高于装备等级，无需同步。")
            else:
                plan = plan_all(slot.handle, slot.item.serial, seed)
            if plan.after.serial != data.get("after"):
                return {"ok": False, "error": "房主的 BL4 Reroll 版本不同，未进行任何更改。"}
            outcome = apply(plan)
        except (Refused, game.RerollError, KeyError, TypeError, ValueError) as ex:
            return {"ok": False, "error": str(ex) or type(ex).__name__}
    log(f"rerolled a friend's {slot.item.label}")
    return _outcome_dict(outcome)


def _tell_result(result: dict[str, Any]) -> None:
    if result.get("ok"):
        tell(result["message"])
    else:
        tell(str(result.get("error")), error=True)


def reroll_all(handle: int, serial: str | None = None) -> None:
    try:
        apply_async(plan_all(handle, serial), _tell_result)
    except (Refused, game.RerollError) as ex:
        tell(str(ex), error=True)


def reroll_one(handle: int, line: int, serial: str | None = None) -> None:
    try:
        apply_async(plan_one(handle, line, serial), _tell_result)
    except (Refused, game.RerollError) as ex:
        tell(str(ex), error=True)


def reroll_legendary(handle: int, serial: str | None = None) -> None:
    try:
        apply_async(plan_legendary(handle, serial), _tell_result)
    except (Refused, game.RerollError) as ex:
        tell(str(ex), error=True)


def sync_item_level(handle: int, serial: str) -> None:
    if not mod.is_enabled or S.sync_pending is not None or menu_reroll.S.busy or card.S.pending is not None:
        return
    try:
        plan = plan_sync_level(handle, serial)
        if plan is None:
            return
        token = object()
        S.sync_pending = token

        def completed(result: dict[str, Any]) -> None:
            if S.sync_pending is token:
                S.sync_pending = None
                _tell_result(result)

        try:
            apply_async(plan, completed)
        except Exception:
            # Scheduling can fail before a callback exists; do not leave the button locked.
            if S.sync_pending is token:
                S.sync_pending = None
            raise
    except (Refused, game.RerollError) as ex:
        tell(str(ex), error=True)


def randomize_firmware(handle: int, serial: str) -> None:
    if not mod.is_enabled or S.sync_pending is not None or menu_reroll.S.busy or card.S.pending is not None:
        return
    try:
        plan = plan_firmware(handle, serial)
        token = object()
        S.sync_pending = token

        def completed(result: dict[str, Any]) -> None:
            if S.sync_pending is token:
                S.sync_pending = None
                _tell_result(result)

        try:
            apply_async(plan, completed)
        except Exception:
            if S.sync_pending is token:
                S.sync_pending = None
            raise
    except (Refused, game.RerollError) as ex:
        tell(str(ex), error=True)


def select_firmware(handle: int, serial: str, target: int) -> None:
    if not mod.is_enabled or S.sync_pending is not None or menu_reroll.S.busy or card.S.pending is not None:
        return
    try:
        plan = plan_firmware_target(handle, target, serial)
        token = object()
        S.sync_pending = token

        def completed(result: dict[str, Any]) -> None:
            if S.sync_pending is token:
                S.sync_pending = None
                _tell_result(result)

        try:
            apply_async(plan, completed)
        except Exception:
            if S.sync_pending is token:
                S.sync_pending = None
            raise
    except (Refused, game.RerollError) as ex:
        tell(str(ex), error=True)


def _quick_menu_reroll(handle: int, serial: str, done: Callable[[], None]) -> None:
    """The same whole-item transaction as the button, without a second confirmation."""
    try:
        plan = plan_legendary(handle, serial)
    except (Refused, game.RerollError):
        done()  # unsupported, stale, blocked or unaffordable: no transaction
        return

    def completed(result: dict[str, Any]) -> None:
        try:
            _tell_result(result)
        finally:
            done()

    apply_async(plan, completed)


# endregion
# region Menu


class S:
    signature: Any = None
    sync_pending: object | None = None  # suppress duplicate clicks while a host request is pending
    refreshed_at = 0.0
    errors: set[str] = set()  # noqa: RUF012
    # Whether the mod menu's screen was showing last tick (the options are only rebuilt then)
    showing = False
    # When _menu_showing() is asked next (MENU_CHECK_S)
    menu_check_at = 0.0
    # The "You have N Eridium" row, updated in place (a pickup mustn't rebuild every page)
    balance_option: ButtonOption | None = None
    balance: int | None = None


def _title(slot: game.Slot) -> str:
    item = slot.item
    if isinstance(item, legendary.Legend):
        text = f"{item_name(item.name)}（{'珠光' if item.pearl else '传奇'} {item_label(item.label)}），{item.level} 级"
    else:
        text = f"{rarity_name(item.rarity)} {item_label(item.label)}，{item.level} 级".strip()
    return text + ("（已装备）" if slot.equipped else "")


def _legendary_button(slot: game.Slot, item: legendary.Legend, display_name: str) -> ButtonOption:
    handle, serial = slot.handle, slot.item.serial
    menu_reroll.remember(handle, serial)
    return ButtonOption(
        "legendary",
        display_name=f"{display_name}（{cost_legendary()} 镒矿）",
        description=(
            f"保持 {item_name(item.name)} 的 {item.level} 级，像重新掉落一样整体重掷：元素、配件、授权部件、固件、技能和词条等所有可随机生成的内容，均按游戏原有概率重新生成，稀有部件仍然稀有。装备等级和已应用的外观保持不变。"
            "背包打开且 Mod 菜单停留在本物品子界面时（包括按 Esc 隐藏菜单后），也可使用“子界面快速整件重掷”快捷键直接执行。"
        ),
        on_press=lambda _: reroll_legendary(handle, serial),
    )


def _sync_level_button(slot: game.Slot) -> ButtonOption:
    handle, serial = slot.handle, slot.item.serial
    return ButtonOption(
        "sync_level",
        display_name=f"同步玩家等级（{cost_legendary()} 镒矿）",
        description=(
            "仅在玩家等级高于此装备时，将装备等级提升至玩家当前等级；相等或更低时不处理。"
            "成功升级时消耗与整件重掷相同的镒矿费用；未升级时不扣费。"
            "不重新随机部件、固件、技能或词条，已应用的外观保持不变。装备数值由游戏按新等级重新计算。"
        ),
        on_press=lambda _: sync_item_level(handle, serial),
    )


@dataclass
class FirmwareUnavailable(ValueOption[str]):
    """A read-only value: Mod Menu renders it as text, with no Execute/Open control."""

    def _to_json(self) -> Any:
        return ...  # derived UI text, not a persistent setting

    def _from_json(self, value: Any) -> None:
        pass  # derived from the live item, never restored from saved settings

    def reset(self) -> None:
        pass


def _firmware_option(slot: game.Slot) -> BaseOption:
    try:
        choices = firmware.options(slot.item.serial, game.Values.resolve)
        current = firmware.part_name(choices.base, choices.current) if choices.base is not None else ""
        detail = f"当前固件：{current}。" if current else ""
        reason = detail + choices.reason
    except (ValueError, KeyError, IndexError, game.RerollError):
        choices = None
        reason = "无法读取固件候选表，未进行任何修改。"
    if choices is None or not choices.choices:
        return FirmwareUnavailable("firmware_unavailable", "无法修改", display_name="随机固件", description=reason)
    handle, serial = slot.handle, slot.item.serial
    candidates = "、".join(dict.fromkeys(firmware.part_name(choices.base, index) for index in choices.choices))
    return ButtonOption(
        "firmware",
        display_name=f"固件: {current}（{cost_legendary()} 镒矿）",
        description=(
            detail + f"可随机到的固件：{candidates}。"
            "仅更换手雷、炮械、修复套件、职业模组、护盾或强化组件的固件。"
            "从其他有效候选中随机选择，不会选回当前固件。原本没有固件时，在规则允许的空槽中添加。"
            "等级、种子、外观、技能、词条和其他部件保持不变。费用与整件重掷共用设置，替换失败不扣费。"
        ),
        on_press=lambda _: randomize_firmware(handle, serial),
    )


def _target_firmware_option(slot: game.Slot) -> NestedOption | None:
    try:
        choices = firmware.options(slot.item.serial, game.Values.resolve)
    except (ValueError, KeyError, IndexError, game.RerollError):
        return None
    if not choices.choices:
        return None
    current = firmware.part_name(choices.base, choices.current)
    cost = cost_firmware_target()
    handle, serial = slot.handle, slot.item.serial
    children = []
    for target in choices.choices:
        name = firmware.part_name(choices.base, target)
        children.append(ButtonOption(
            f"firmware_target_{target}",
            display_name=f"{name}（{cost} 镒矿）",
            description=(
                f"将固件从“{current}”定向修改为“{name}”，消耗 {cost} 镒矿。"
                "费用为随机固件的 10 倍，随整件重掷费用设置变化。"
                "等级、种子、外观、技能、词条和其他部件保持不变。"
                "执行时重新检查候选及费用；目标不可用或替换失败时不扣费。联机时以房主设置为准。"
            ),
            on_press=lambda _, target=target: select_firmware(handle, serial, target),
        ))
    return NestedOption(
        "firmware_target", children,
        display_name=f"定向修改固件（{cost} 镒矿）",
        description=(f"当前固件：{current}。选择一个可用固件直接替换，费用为随机固件的 10 倍。"
                     "只列出这件装备当前有效且不同于现有固件的候选，点击目标后执行修改。"),
    )


def _legendary_page(slot: game.Slot, item: legendary.Legend) -> NestedOption:
    kind = "pearl" if item.pearl else "legendary"
    children: list[BaseOption] = [_legendary_button(slot, item, f"重掷这件{'珠光' if kind == 'pearl' else '传奇'}装备"),
                                  _sync_level_button(slot), _firmware_option(slot)]
    if (target_option := _target_firmware_option(slot)) is not None:
        children.append(target_option)
    return NestedOption(f"item{slot.handle}", children, display_name=_title(slot),
                        description=f"{item.maker} {item_label(item.label)}。重掷以重新随机生成该装备的部件。".strip())  # fmt: skip


def _item_page(slot: game.Slot) -> NestedOption:
    if isinstance(slot.item, legendary.Legend):
        return _legendary_page(slot, slot.item)
    item, handle, serial = slot.item, slot.handle, slot.item.serial
    children: list[BaseOption] = [
        ButtonOption(
            "all",
            display_name=f"重掷全部词条（{cost_all()} 镒矿）",
            description="重新随机生成全部可重掷词条，也可能得到原有词条。"
            + ("传奇装备自带的固定词条保持不变。" if any(line.locked for line in item.lines) else ""),
            on_press=lambda _: reroll_all(handle, serial),
        ),
    ]
    for i, line in enumerate(item.lines):
        if line.locked:
            children.append(ButtonOption(
                f"line{i}",
                display_name=f"{stat_name(line.name)}（固定：传奇装备自带）",
                description="这是传奇装备自带的固定词条，无法单独重掷。",
                on_press=lambda _, i=i: reroll_one(handle, i, serial),
            ))  # fmt: skip
        else:
            children.append(ButtonOption(
                f"line{i}",
                display_name=f"替换 {stat_name(line.name)}（{cost_one()} 镒矿）",
                description=f"将 {stat_name(line.name)} 替换为另一个随机词条，其他词条保持不变。",
                on_press=lambda _, i=i: reroll_one(handle, i, serial),
            ))  # fmt: skip
    if (whole := legendary.read(serial)) is not None:
        # A legendary class mod: its skills, modifiers and firmware can also roll again together
        children.append(_legendary_button(slot, whole, "重掷整件装备"))
    children.append(_sync_level_button(slot))
    children.append(_firmware_option(slot))
    if (target_option := _target_firmware_option(slot)) is not None:
        children.append(target_option)
    names = "、".join(stat_name(line.name) for line in item.lines) or "无"
    return NestedOption(f"item{handle}", children, display_name=_title(slot), description=f"词条：{names}。")


def _info(text: str, description: str = "") -> ButtonOption:
    return ButtonOption("info", display_name=text, description=description, on_press=lambda _: _refresh(force=True))


def _balance_text(eridium: int) -> str:
    return f"当前拥有 {eridium} 镒矿"


def _build() -> list[BaseOption]:
    menu_reroll.clear_pages()
    settings: list[BaseOption] = [reroll_key, pick_key, menu_reroll_key, cost_all_option, cost_one_option, cost_legendary_option]
    S.balance_option = S.balance = None
    if (why := _blocked()) is not None:
        return [_info(why), *settings]
    try:
        # Showing only: the buttons carry handle + serial, and a press reads the item live (_slot)
        slots = game.cached_items()
        eridium = game.balance()
    except game.RerollError as ex:
        return [_info(str(ex)), *settings]
    info = _info(
        _balance_text(eridium),
        f"重掷全部词条需要 {cost_all()} 镒矿，替换单个词条需要 {cost_one()} 镒矿，整体重掷传奇或珠光装备需要 {cost_legendary()} 镒矿。也可将鼠标悬停在背包装备上，使用下方快捷键操作。",
    )
    S.balance_option, S.balance = info, eridium
    options: list[BaseOption] = [info, *settings]
    if not slots:
        options.append(_info("背包中没有职业模组、强化装置、传奇或珠光装备"))
    options += [_item_page(slot) for slot in slots]
    return options


def _signature() -> Any:
    """What the pages are built from, without the Eridium balance (that row is updated in place)."""
    ok = data_ok()
    host = game.is_host() or _host_rerolls()
    if not ok or not host:
        return ("blocked", ok, host)
    try:
        return cost_all(), cost_one(), cost_legendary(), tuple((s.handle, s.item.serial, s.equipped) for s in game.cached_items())
    except game.RerollError as ex:
        return str(ex)


def _update_balance() -> None:
    option = S.balance_option
    if option is None:
        return
    try:
        eridium = game.balance()
    except game.RerollError:
        return
    if eridium != S.balance:
        S.balance = eridium
        option.display_name = _balance_text(eridium)


def _attach(options: list[BaseOption]) -> None:
    for option in options:
        option.mod = mod
        if isinstance(option, NestedOption):
            _attach(list(option.children))


def _refresh(*, force: bool = False) -> None:
    if force:
        game.invalidate()
    signature = _signature()
    if force or signature != S.signature:
        S.signature = signature
        options = _build()
        _attach(options)
        mod.options = options
    else:
        _update_balance()


def _menu_showing() -> bool:
    """The BL4 Mod Menu's screen (its page, or its UMG panel) is showing: the only reader of our pages."""
    web = sys.modules.get("bl4_mod_menu.web")
    try:
        # page_open goes stale while the page sleeps (no game menu up), so only with connected()
        if web is not None and web.Link.page_open and web.connected():
            return True
        # F7 asked the page to open its screen (it sends the mods list from then on)
        fresh = getattr(web, "_open_fresh", None)
        if fresh is not None and fresh():
            return True
    except Exception:  # noqa: BLE001 - another Mod Menu version: fall through
        pass
    menu = sys.modules.get("bl4_mod_menu.menu")
    try:
        return menu is not None and bool(menu.S.is_open)
    except Exception:  # noqa: BLE001
        return False


@frametick.tick("bl4_reroll")  # once per engine frame (shared/frametick: one hook for all our mods)
def _tick() -> None:
    try:
        card.tick()
        menu_reroll.tick()
    except Exception as ex:  # noqa: BLE001 - never let our tick break the game's
        _report(ex)
    # Refresh visible pages or a hidden retained item page while inventory is open. The latter
    # must also get the new serial after a reroll, so another press can reroll the same item.
    # Asked MENU_CHECK_S apart, not every frame (it looks through the Mod Menu's modules)
    now = time.monotonic()
    if now < S.menu_check_at:
        return
    S.menu_check_at = now + MENU_CHECK_S
    showing = _menu_showing() or menu_reroll.active()
    opened = showing and not S.showing
    S.showing = showing
    if not showing:
        return
    if not opened and now - S.refreshed_at < REFRESH_S:
        return
    S.refreshed_at = now
    try:
        _refresh()
    except Exception as ex:  # noqa: BLE001
        _report(ex)


def _report(ex: Exception) -> None:
    """The tick runs every frame; report each distinct problem once."""
    if repr(ex) not in S.errors:
        S.errors.add(repr(ex))
        logging.error("".join(traceback.format_exception(ex)))


# endregion
# region Console


@command("reroll", description="列出背包中的职业模组、强化装置、传奇和珠光装备，或对其进行重掷。")
def reroll_command(args: argparse.Namespace) -> None:
    try:
        slots = game.items()
    except game.RerollError as ex:
        log(str(ex))
        return
    if args.item is None:
        log(f"当前拥有 {game.balance()} 镒矿。reroll <装备编号> 重掷全部词条（{cost_all()} 镒矿；整件传奇或珠光装备为 {cost_legendary()} 镒矿），reroll <装备编号> <词条编号> 替换单个词条（{cost_one()} 镒矿）。")
        for n, slot in enumerate(slots, 1):
            log(f"{n}. {_title(slot)}")
            for m, line in enumerate(slot.item.lines, 1):
                log(f"     {m}. {stat_name(line.name)}{'（传奇装备自带）' if line.locked else ''}")
        return
    if not 1 <= args.item <= len(slots):
        log(f"没有编号为 {args.item} 的装备，请使用 reroll 命令查看列表。")
        return
    slot = slots[args.item - 1]
    if isinstance(slot.item, legendary.Legend):
        reroll_legendary(slot.handle)
    elif args.modifier is None:
        reroll_all(slot.handle)
    elif 1 <= args.modifier <= len(slot.item.lines):
        reroll_one(slot.handle, args.modifier - 1)
    else:
        log(f"该装备没有编号为 {args.modifier} 的词条。")


reroll_command.add_argument("item", type=int, nargs="?", help="使用 reroll 命令列出的装备编号")
reroll_command.add_argument("modifier", type=int, nargs="?", help="仅替换指定编号的词条")

# endregion


# region Card keys

reroll_key = KeybindOption(
    "Reroll key",
    "T",
    display_name="重掷快捷键",
    description=(
        "将鼠标悬停在背包中的职业模组或强化装置上，按此键可重掷全部词条，或替换通过选择键选中的词条。对于传奇或珠光装备，会重掷整件装备。重掷全部内容前需要再次按键确认。"
    ),
)
menu_reroll_key = KeybindOption(
    "Menu whole-item reroll key",
    "R",
    display_name="子界面快速整件重掷",
    description=(
        "仅在角色背包打开，且 Mod 菜单停留在本 Mod 的物品子界面时生效。按 Esc 隐藏菜单后仍有效；关闭背包或离开该子界面后无效。按一次直接执行“重掷整件装备”，无需再次确认，消耗现有设置的整件重掷费用。"
        "只处理数据表收录且该子界面提供整件重掷按钮的物品；其他页面、不支持的物品或正在改键时不处理。长按不会连续重掷。"
    ),
)
pick_key = KeybindOption(
    "Pick modifier key",
    "G",
    display_name="选择词条快捷键",
    description=(
        "将鼠标悬停在职业模组或强化装置上，按此键可选择要替换的词条，再按重掷键执行。重复按下可选择下一条，越过最后一条后恢复为重掷全部词条。"
    ),
)


# The item pages show the prices: they're in _signature, so changing one rebuilds the pages

cost_all_option = SliderOption(
    "Reroll all cost",
    25,
    0,
    1000,
    5,
    display_name="重掷全部词条费用",
    description=(
        "重掷一件装备全部词条所需的镒矿。联机时以房主设置的价格为准，由房主端执行重掷并扣除镒矿。"
    ),
)
cost_one_option = SliderOption(
    "Replace one cost",
    50,
    0,
    1000,
    5,
    display_name="替换单个词条费用",
    description=(
        "替换一个选定词条所需的镒矿。联机时以房主设置的价格为准，由房主端执行重掷并扣除镒矿。"
    ),
)


cost_legendary_option = SliderOption(
    "Legendary / pearl reroll cost",
    100,
    0,
    1000,
    5,
    display_name="传奇 / 珠光装备重掷费用",
    description=(
        "整体重掷传奇或珠光装备所需的镒矿。保持装备等级，按游戏原有概率重新生成各部件。联机时以房主设置的价格为准，由房主端执行重掷并扣除镒矿。"
    ),
)


def cost_all() -> int:
    return int(cost_all_option.value)


def cost_one() -> int:
    return int(cost_one_option.value)


def cost_legendary() -> int:
    return int(cost_legendary_option.value)


def cost_firmware_target() -> int:
    return cost_legendary() * 10


card.S.plan_all = plan_all
card.S.plan_one = plan_one
card.S.plan_legendary = plan_legendary
card.S.apply = apply_async
card.S.keys = lambda: (reroll_key.value, pick_key.value)
card.S.costs = lambda: (cost_all(), cost_one(), cost_legendary())
card.S.blocked = _blocked


menu_reroll.S.key = lambda: menu_reroll_key.value
menu_reroll.S.allowed = lambda: (mod.is_enabled and _blocked() is None and card.S.pending is None
                               and S.sync_pending is None)
menu_reroll.S.execute = _quick_menu_reroll
# Preserve the old hover-card bindings when the overlay is hidden, unless a binding collides:
# the retained-page shortcut then owns that key, rather than rerolling a different hovered item.
card.S.suspend_keys = lambda: (S.sync_pending is not None or menu_reroll.S.busy or _menu_showing()
                             or (menu_reroll.active() and menu_reroll_key.value is not None
                                 and menu_reroll_key.value in (reroll_key.value, pick_key.value)))


def _enable() -> None:
    start_data_check()
    card.register(GAME_DIR)
    menu_reroll.register()


def _disable() -> None:
    S.sync_pending = None
    menu_reroll.unregister()
    card.unregister()


# endregion

# A mod with no settings file loads switched off (a manual install, issue #5): start on
from .firston import ensure_on  # noqa: E402

ensure_on(__name__)

mod = build_mod(
    # The rest of the options are built from the backpack (_refresh); these are listed here so
    # their saved values load
    options=[reroll_key, pick_key, menu_reroll_key, cost_all_option, cost_one_option, cost_legendary_option],
    hooks=[_tick],
    commands=[reroll_command],
    on_enable=_enable,
    on_disable=_disable,
)


if coop is not None:
    coop.feature(FEATURE, lambda: mod.is_enabled)
    coop.handle(SERVICE, _serve)
    coop.handle(SYNC_LEVEL_SERVICE, _serve)
    coop.handle(FIRMWARE_SERVICE, _serve)
    coop.handle(TARGET_FIRMWARE_SERVICE, _serve)
