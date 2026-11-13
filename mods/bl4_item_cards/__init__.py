# -*- coding: utf-8 -*-
"""
Detailed item cards for Borderlands 4.

- Class mods: each skill's name, your rank out of the most it can reach with the mod (its max plus
  the mod's +N), its description and, as an option, its exact numbers as "now -> with this mod".
- Secondary stats get their names, and banner/flavour text renders properly.
- Firmware: every bonus tier with its numbers, which tiers you have now, and which this item would
  unlock or cost you if you equipped it.
- Legendaries: who drops them and how often at your UVH level, with keys to set a waypoint to (or
  travel to) that boss's Moxxi's Big Encore machine.
- Inventory: each legendary's own name on the equip slots and in the switch grid (option).

How it fits together:

- card_page/: our script and stylesheet (loose files) and the generated game data the cards
  read. The BL4 UI Link (uilink/, shared by our mods) runs the script in the game's pages; it
  hooks the game's own card (no replaced page, so it works next to other mods' pages).
- skill_stats.py: works out every skill's numbers for your character (a little each frame, a pass
  a second in menus) and leaves them in a loose file the card reads.
- encore_waypoint.py: the Big Encore keys, and the messages the card sends back through UI sounds.
- Card size and "fit to screen" go to the script in a loose settings file. A card taller than the
  screen scrolls with the mouse wheel (the script handles that on its own).

Turning the mod off stops the script and takes everything it drew off the cards at once.
"""

from __future__ import annotations

import sys
import threading
import types
from typing import Any

from mods_base import SETTINGS_DIR, BoolOption, ButtonOption, KeybindOption, SliderOption, build_mod, hook
from unrealsdk import logging
from unrealsdk.hooks import Type
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

from . import card_page, encore_waypoint, frametick, health, skill_stats, uilink

__version__ = "0.2.2"
__version_info__ = (0, 2, 2)

# The page script's key in the BL4 UI Link
LINK_KEY = "itemcards"

GAME_DIR = SETTINGS_DIR.parent.parent

_status = "Detailed item cards: not checked yet."
_errors: set[str] = set()


def log(msg: str) -> None:
    for original, translated in (
        ("Detailed item cards: not checked yet.", "详细物品卡片：尚未检查。"),
        ("Detailed item cards: couldn't update", "详细物品卡片：无法更新"),
        ("Detailed item cards are off.", "详细物品卡片已关闭。"),
        ("Detailed item cards are on.", "详细物品卡片已开启。"),
        ("Detailed item cards paused: this game version changed the item card, so they need a mod update.",
         "详细物品卡片已暂停：当前游戏版本更改了物品卡片，需要更新 Mod。"),
        ("Detailed item cards paused:", "详细物品卡片已暂停："),
        (" also changes the item card.", "也修改了物品卡片。"),
        (" The old item card page (", " 旧物品卡片页面（"),
        (") goes when the game exits.", "）将在退出游戏后移除。"),
    ):
        msg = msg.replace(original, translated)
    logging.info(f"[物品卡片] {msg}")


def _report_error(ex: Exception) -> None:
    """The tick runs every frame; report each distinct problem only once."""
    message = repr(ex)
    if message not in _errors:
        _errors.add(message)
        logging.error(f"[Item Cards] {message}")


# Shared by every copy of this module (a hot reload imports a new one while the old copy's
# disable may still be syncing): one sync at a time, and the newest wish wins
_SYNC = sys.modules.setdefault("_bl4_item_cards_sync", types.ModuleType("_bl4_item_cards_sync"))
if not hasattr(_SYNC, "lock"):
    _SYNC.lock = threading.Lock()
    _SYNC.want = None  # (sync function, enabled) not done yet


def sync_page(enabled: bool) -> None:
    """
    card_page.sync reads the game's pak indexes (~0.7 s) and writes files: a worker does it, so
    turning the mod on mid-game (installed from the Mod Menu's Discover, which loads it on the
    game thread) doesn't freeze the game. At startup the SDK enables mods off the game thread
    anyway. The cards show once it's done.
    """
    _SYNC.want = (_sync_now, enabled)
    threading.Thread(target=_sync_latest, name="bl4_item_cards.sync", daemon=True).start()


def _sync_latest() -> None:
    with _SYNC.lock:
        want, _SYNC.want = _SYNC.want, None
        if want is not None:
            want[0](want[1])


def _sync_now(enabled: bool) -> None:
    global _status
    try:
        _status = card_page.sync(GAME_DIR, enabled)
    except Exception as ex:  # noqa: BLE001 - never let a file problem break the mod
        _status = f"Detailed item cards: couldn't update ({ex})."
    log(_status)
    # The script runs in every game page with an item card (HUD ground loot, menus, vendors...)
    # while the game's card is the one it was written for. Nothing to poll: it reads loose files
    if enabled and card_page.page_current:
        uilink.register(
            LINK_KEY, card_page.SCRIPT_URL, dict, lambda _action: None, views=(uilink.ANY,), mod=__name__
        )
    else:
        uilink.unregister(LINK_KEY)


@frametick.tick("bl4_item_cards")  # once per engine frame (shared/frametick: one hook for all our mods)
def tick() -> None:
    # Every frame: the Big Encore keys and trips in progress (cheap, see encore_waypoint.py)
    try:
        health.tick()  # "needs an update" statuses for all our mods (shared/health; a clock compare most calls)
        uilink.tick()  # the BL4 UI Link's server (once a frame overall, whichever of our mods calls it)
        encore_waypoint.poll_keys(GAME_DIR, waypoint_key.value, travel_key.value)
    except Exception as ex:  # noqa: BLE001 - never let this break the game's tick
        _report_error(ex)
    # skill_stats throttles itself too (a pass is sliced across frames, under 1 ms each)
    try:
        skill_stats.tick(GAME_DIR)
    except Exception as ex:  # noqa: BLE001
        _report_error(ex)


@hook(encore_waypoint.CHANNEL_FUNCS[0], Type.PRE)
def encore_waypoint_from_inventory(_obj: UObject, args: WrappedStruct, _ret: Any, _func: BoundFunction) -> Any:
    return encore_waypoint.on_channel(GAME_DIR, args)


@hook(encore_waypoint.CHANNEL_FUNCS[1], Type.PRE)
def encore_waypoint_from_hud(_obj: UObject, args: WrappedStruct, _ret: Any, _func: BoundFunction) -> Any:
    return encore_waypoint.on_channel(GAME_DIR, args)


waypoint_key = KeybindOption(
    "Big Encore waypoint key",
    "J",
    description=(
        "在背包等菜单中，将鼠标悬停在首领掉落的传奇装备上，按此键将导航点（及地图标记）设为对应首领的莫西“大返场”机器。地上掉落物不响应此键。"
    ),
    display_name="大返场导航点快捷键",
)

travel_key = KeybindOption(
    "Big Encore travel key",
    "K",
    description=(
        "在背包等菜单中，将鼠标悬停在首领掉落的传奇装备上，按此键打开确认框，确认后前往对应首领的莫西“大返场”机器（必要时先快速旅行至对应地图）。地上掉落物不响应此键。仅限单人游戏或房主使用。"
    ),
    display_name="大返场传送快捷键",
)

def card_settings(
    scale: float | None = None,
    fit: bool | None = None,
    firmware: bool | None = None,
    slot_names: bool | None = None,
    full_names: bool | None = None,
    skill_numbers: bool | None = None,
) -> dict:
    return {
        "scale": (scale_option.value if scale is None else scale) / 100,
        "fit": fit_option.value if fit is None else fit,
        "firmware": firmware_option.value if firmware is None else firmware,
        "slot_names": slot_names_option.value if slot_names is None else slot_names,
        "full_names": full_names_option.value if full_names is None else full_names,
        "skill_numbers": skill_numbers_option.value if skill_numbers is None else skill_numbers,
    }


def publish_settings(settings: dict | None) -> None:
    try:
        card_page.write_settings(GAME_DIR, settings)
    except OSError as ex:
        _report_error(ex)


# Option callbacks run before the new value is stored, so pass it along
scale_option = SliderOption(
    "Card size",
    100,
    50,
    150,
    5,
    description="调整物品卡片的缩放比例（相对于游戏默认大小的百分比）。几秒内生效。",
    on_change_while_enabled=lambda _, value: publish_settings(card_settings(scale=value)),
    display_name="物品卡片大小",
)

fit_option = BoolOption(
    "Shrink tall cards to fit",
    False,
    description=(
        "物品卡片高于屏幕时，自动缩小至可完整显示。关闭后，菜单中的过高卡片可用鼠标滚轮滚动；HUD 中只显示顶部。"
    ),
    on_change_while_enabled=lambda _, value: publish_settings(card_settings(fit=value)),
    display_name="自动缩小过高的卡片",
    true_text="开启",
    false_text="关闭",
)

def set_skill_numbers(on: bool) -> None:
    skill_stats.set_numbers(on)
    publish_settings(card_settings(skill_numbers=on))


skill_numbers_option = BoolOption(
    "Exact skill numbers",
    False,
    description=(
        "在职业模组的各项技能下列出精确数值（例如“枪械伤害：+14% → +35%”），对比当前技能点效果与装备此模组后的效果。关闭时，仅显示技能、当前等级、装备后的等级上限及技能说明。"
    ),
    on_change_while_enabled=lambda _, value: set_skill_numbers(value),
    display_name="显示精确技能数值",
    true_text="开启",
    false_text="关闭",
)

firmware_option = BoolOption(
    "Detailed firmware",
    True,
    description=(
        "列出各档固件加成及其数值，标记当前生效的档位，并显示装备此物品后会解锁或失去的档位。"
    ),
    on_change_while_enabled=lambda _, value: publish_settings(card_settings(firmware=value)),
    display_name="详细固件信息",
    true_text="开启",
    false_text="关闭",
)

slot_names_option = BoolOption(
    "Legendary names in the inventory",
    True,
    description=(
        "在背包的武器和装备槽位，以及可切换物品列表中，显示传奇装备本名（例如将带前缀的“Churned Aching Golden God”显示为“Golden God”）。"
    ),
    on_change_while_enabled=lambda _, value: publish_settings(card_settings(slot_names=value)),
    display_name="背包中显示传奇本名",
    true_text="开启",
    false_text="关闭",
)

full_names_option = BoolOption(
    "Full legendary names",
    False,
    description=(
        "显示包含随机前缀的完整名称（如“Churned Aching Golden God”），而非仅传奇本名。过长的名称会缩小字号，必要时分为两行。"
    ),
    on_change_while_enabled=lambda _, value: publish_settings(card_settings(full_names=value)),
    display_name="显示完整传奇名称",
    true_text="开启",
    false_text="关闭",
)

status_button = ButtonOption(
    "Show status",
    description="在控制台输出详细物品卡片是否已启用，或无法启用的原因。",
    on_press=lambda _: log(_status),
    display_name="显示状态",
)


# A mod with no settings file loads switched off (a manual install, issue #5): start on
from .firston import ensure_on  # noqa: E402

ensure_on(__name__)

mod = build_mod(
    options=[scale_option, fit_option, skill_numbers_option, firmware_option, slot_names_option, full_names_option, waypoint_key, travel_key, status_button],
    hooks=[tick, encore_waypoint_from_inventory, encore_waypoint_from_hud],
    on_enable=lambda: (sync_page(True), skill_stats.set_numbers(skill_numbers_option.value), publish_settings(card_settings())),
    on_disable=lambda: (sync_page(False), publish_settings(None), encore_waypoint.cancel_trip()),
)
