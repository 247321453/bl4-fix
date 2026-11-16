# -*- coding: utf-8 -*-
"""
Build Presets for Borderlands 4: five build slots per character, right in the inventory.

Open the inventory: under the Reward Center button there are five squares. Click an empty one to
save your build into it; click a saved one to load it. Hover a square to see what's in it (each
item by name, and the skill trees your points are in, in the skill screen's colors), and use its
small buttons to save over it, name it (type, then Enter) or clear it.

A build is everything you have equipped (four weapons, shield, ordnance, repkit, enhancement,
class mod), your skill points, action skill, augments and capstone, and your specializations
(points and perks). Loading puts each saved item back into its slot, but only that exact item:
if it's no longer in your backpack the slot is left as it is. Skills are refunded and spent again
only where they differ (free, like the skill screen's own reset).

Hotkeys (none bound by default; set them in this mod's options): load build 1-5, next / previous
saved build. They work in gameplay too, where a notice at the top of the screen says what loaded.

The squares need no other mod: they run through the BL4 UI Link (uilink/, a pak our mods share
that replaces none of the game's pages). They show from the game start after the first one with
this mod (paks only load at startup), sooner if the BL4 Mod Menu is installed. Or use the console:
`build` lists the slots, `build save 2`, `build load 2`, `build clear 2`, `build rename 2 Boss killer`.

Co-op: saving works anywhere. Equipping and respeccing belong to the host, so a client's load is
done by the host's copy of this mod (BL4 Direct's co-op channel): the host needs Build Presets for
a friend to load theirs, and the friend needs it for the squares.

Everything but this file can be hot-reloaded (dev/reload_builds.py), and the squares' script and
styles reload themselves in the page.
"""

from __future__ import annotations

import argparse
import time
import traceback

from mods_base import SETTINGS_DIR, BoolOption, GroupedOption, KeybindOption, build_mod, command
from unrealsdk import logging

from . import builds, frametick, hotkeys, page
from .i18n import translate, equipment

__version__ = "0.2.1"
__version_info__ = (0, 2, 1)

GAME_DIR = SETTINGS_DIR.parent.parent


def log(msg: str) -> None:
    logging.info(f"[配装预设] {translate(msg)}")


skills_option = BoolOption(
    "Load skills",
    True,
    display_name="加载技能",
    description="加载配装时，同时恢复技能点、主动技能、强化技能和终极技能。",
    true_text="开启", false_text="关闭",
)
specs_option = BoolOption(
    "Load specializations",
    True,
    display_name="加载专精",
    description="加载配装时，同时恢复专精点数和专精天赋。",
    true_text="开启", false_text="关闭",
)

load_keys = [
    KeybindOption(f"Load build {n}", None, display_name=f"加载配装 {n}", description=f"加载配装 {n}，在游玩及游戏菜单中均可使用。")
    for n in range(1, builds.presets.SLOTS + 1)
]
next_key = KeybindOption("Next build", None, display_name="下一个配装", description="切换到当前配装之后的下一个已保存配装。")
previous_key = KeybindOption("Previous build", None, display_name="上一个配装", description="切换到当前配装之前的上一个已保存配装。")
hotkey_group = GroupedOption("Hotkeys", [*load_keys, next_key, previous_key], display_name="快捷键")


def _options() -> tuple[bool, bool]:
    return skills_option.value, skills_option.value and specs_option.value


page.S.options = _options
hotkeys.S.options = _options
# Rebinding takes effect within this long (the list was rebuilt every frame, unbound keys included)
HOTKEYS_CHECK_S = 1.0


class _Hotkeys:
    at = -1e9
    bound: list[tuple[str, str]] = []  # noqa: RUF012


def _bound_hotkeys() -> list[tuple[str, str]]:
    """The hotkeys that have a key (none by default): hotkeys.tick reads only those."""
    now = time.monotonic()
    if now - _Hotkeys.at >= HOTKEYS_CHECK_S:
        _Hotkeys.at = now
        pairs = [*((str(n), option.value) for n, option in enumerate(load_keys, 1)),
                 (hotkeys.NEXT, next_key.value), (hotkeys.PREVIOUS, previous_key.value)]  # fmt: skip
        _Hotkeys.bound = [(action, key) for action, key in pairs if key]
        # A key bound later starts as "held" (hotkeys.tick's default), so it needs a fresh press
        for action, key in pairs:
            if not key:
                hotkeys.S.down.pop(action, None)
    return _Hotkeys.bound


hotkeys.S.keys = _bound_hotkeys


class S:
    errors: set[str] = set()  # noqa: RUF012


@frametick.tick("bl4_builds")  # once per engine frame (the shared Frame Tick, frametick/)
def _tick() -> None:
    try:
        page.tick()
        # No hotkey bound (the default) and no notice up: only the 1 Hz look at the bindings
        if _Hotkeys.bound or hotkeys.Notice.hide_at or time.monotonic() - _Hotkeys.at >= HOTKEYS_CHECK_S:
            hotkeys.tick()
    except Exception as ex:  # noqa: BLE001 - never let our tick break the game's
        if repr(ex) not in S.errors:
            S.errors.add(repr(ex))
            logging.error("".join(traceback.format_exception(ex)))


@command("build", description="列出、保存、加载或清空配装预设。")
def build_command(args: argparse.Namespace) -> None:
    try:
        if args.action == "list":
            for square in builds.summaries():
                if square["empty"]:
                    log(f"{square['n']}.（空）")
                    continue
                title = " · ".join(x for x in (square["name"], square.get("action"), square["tree_text"]) if x)
                log(f"{square['n']}. {title} · 保存于 {square['saved']}")
                for gear in square["gear"]:
                    log(f"     {translate(gear['slot'])}：{equipment(gear['label'])}{'' if gear['have'] else '（不在背包中）'}")
            return
        if args.n is None or not 1 <= args.n <= builds.presets.SLOTS:
            log(f"请输入 1 到 {builds.presets.SLOTS} 之间的槽位编号。")
            return
        if args.action == "save":
            log(builds.save(args.n))
        elif args.action == "load":
            headline, details = builds.load(args.n, skills=skills_option.value,
                                            specializations=skills_option.value and specs_option.value)  # fmt: skip
            log(" ".join([translate(headline), *map(translate, details)]))
        elif args.action == "clear":
            log(builds.clear(args.n))
        elif args.action == "rename":
            log(builds.rename(args.n, " ".join(args.name)))
    except builds.Refused as ex:
        log(str(ex))


build_command.add_argument("action", nargs="?", default="list", choices=("list", "save", "load", "clear", "rename"))
build_command.add_argument("n", type=int, nargs="?", help="配装槽位（1—5）")
build_command.add_argument("name", nargs="*", help="重命名：输入新名称，留空则清除名称。")


def _enable() -> None:
    page.register(GAME_DIR)


def _disable() -> None:
    page.unregister()
    hotkeys.stop()


# A mod with no settings file loads switched off (a manual install, issue #5): start on
from .firston import ensure_on  # noqa: E402

ensure_on(__name__)

mod = build_mod(
    options=[skills_option, specs_option, hotkey_group],
    hooks=[_tick],
    commands=[build_command],
    on_enable=_enable,
    on_disable=_disable,
)

if builds.coop is not None:
    builds.coop.feature(builds.FEATURE, lambda: mod.is_enabled)
