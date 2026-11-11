# -*- coding: utf-8 -*-
"""
Performance Fixes for Borderlands 4: removes hitches we traced with an external stack sampler
(dev/perf/, findings in docs/game-performance.md).

- Faster Python hooks: one persistent Python thread state on the game thread instead of a new one
  per hook call, and a 0.5 ms GIL switch interval (python_state.py). Helps every SDK mod.
- Frame generation stays on in menus (off): no frame generation rebuild (a freeze with the RTX 30
  DlssgSm86 enabler) every time a menu closes (render.py).
- Keep DLSS loaded (experimental, off): keeps the DLSS upscaler's NVIDIA feature alive across menus
  instead of rebuilding it (render.py). Does not stop frame generation rebuilds.
- Keep game memory in RAM: a soft minimum working set so Windows trims other programs first
  (memory.py). Off by default; for PCs that run short of RAM.
- Python garbage collection without hitches: long-lived Python objects frozen out of the cycle
  collector after each world load (gc_tune.py), so a full collection no longer walks every mod's
  data inside a hook (35-209 ms measured).

Everything is put back when the mod is turned off. Local only: nothing here touches co-op.
"""

from __future__ import annotations

import threading
import time
from typing import Any

from mods_base import ENGINE, BoolOption, SliderOption, build_mod, get_pc
from unrealsdk import logging

from . import frametick, gc_tune, memory, python_state, render

__version__ = "0.2.1"
__version_info__ = (0, 2, 1)

CLEANUP_ID = "bl4_perf.cleanup"  # frametick key of the one-shot cleanup on the game thread
CHECK_INTERVAL = 5.0  # s between cvar checks
LOADING_CHECK_S = 1.0  # while there's no character (loading): the GC's moment, looked at more often


class _S:
    game_thread: int | None = None
    next_check = 0.0
    menu_seen = False  # a menu was up at the last check too (settled: not opening right now)


def _log(msg: str) -> None:
    logging.info(f"[Performance Fixes] {msg}")


def _python_changed(_opt: BoolOption, value: bool) -> None:
    if not value:
        _cleanup(cvars=False)  # unpins on the game thread


python_option = BoolOption(
    "Faster Python hooks",
    True,
    description=(
        "在游戏线程上保留一个 Python 线程状态，避免每次调用 Mod 钩子时反复创建和销毁（使用较多 Mod 时，每帧约可节省 1–2 毫秒），并让游戏线程更快地从后台线程取回 Python 锁。"
    ),
    on_change_while_enabled=_python_changed,
    display_name="加速 Python 钩子",
    true_text="开启",
    false_text="关闭",
)


def _gc_changed(_opt: BoolOption, value: bool) -> None:
    _S.next_check = 0.0
    if not value and gc_tune.restore():
        _log("Python objects unfrozen")


gc_option = BoolOption(
    "Python garbage collection without hitches",
    True,
    description=(
        "Python 垃圾回收器偶尔会在单个游戏帧内遍历所有 Mod 数据，导致 35–200 毫秒的卡顿。此选项在每次加载世界后将长期存活的数据冻结，使回收器仅检查新增数据，并尽量在菜单或加载期间执行回收，避免游玩中卡顿。不影响可见功能。"
    ),
    on_change_while_enabled=_gc_changed,
    display_name="减少 Python 垃圾回收卡顿",
    true_text="开启",
    false_text="关闭",
)


def _dlss_changed(_opt: BoolOption, value: bool) -> None:
    _S.next_check = 0.0
    if not value:
        _cleanup(python=False, cvars=list(render.DLSS))


def _framegen_changed(_opt: BoolOption, value: bool) -> None:
    _S.next_check = 0.0
    if not value:
        _cleanup(python=False, cvars=list(render.FRAMEGEN))


dlss_option = BoolOption(
    "Keep DLSS loaded (experimental)",
    False,
    description=(
        "菜单遮挡游戏画面时仍保留 DLSS 超分辨率组件，避免关闭菜单后重建。实验性：无法消除帧生成重建造成的较长卡顿。未使用 DLSS 时无效。"
    ),
    on_change_while_enabled=_dlss_changed,
    display_name="保持 DLSS 加载（实验性）",
    true_text="开启",
    false_text="关闭",
)


framegen_option = BoolOption(
    "Frame generation stays on in menus",
    False,
    description=(
        "游戏通常会在菜单与过场动画中关闭帧生成，重新开启时会重建组件。使用 RTX 30 系列帧生成 Mod 时，每次关闭菜单可能卡顿长达半秒。此选项让帧生成保持开启，但菜单或过场动画可能出现轻微的帧生成瑕疵。未开启帧生成时无效。"
    ),
    on_change_while_enabled=_framegen_changed,
    display_name="菜单中保持帧生成",
    true_text="开启",
    false_text="关闭",
)


def _memory_changed(_opt: SliderOption, value: float) -> None:
    try:
        _log(memory.apply(float(value)))
    except Exception as ex:  # noqa: BLE001
        logging.error(f"[Performance Fixes] {ex!r}")


memory_option = SliderOption(
    "Keep game memory in RAM (GB)",
    0,
    0,
    24,
    1,
    description=(
        "可用内存不足时，Windows 会将部分游戏数据移出物理内存；再次访问时会造成短暂卡顿。此选项请求 Windows 至少将指定容量的游戏数据保留在物理内存，并优先回收其他程序的内存。0 = 关闭。除非已确认低可用内存导致卡顿，否则请保持 0；切勿设置为接近电脑的总内存容量。"
    ),
    on_change_while_enabled=_memory_changed,
    display_name="保留在物理内存中的游戏数据（GB）",
)


@frametick.tick("bl4_perf")  # once per engine frame (shared/frametick: one hook for all our mods)
def tick() -> None:
    # every frame: the work below is gated, the rest is two compares
    try:
        if _S.game_thread is None:
            _S.game_thread = threading.get_ident()
        if python_option.value and not python_state.is_pinned():
            if python_state.pin_here():
                _log("game-thread Python state pinned")
        now = time.monotonic()
        if now < _S.next_check:
            return
        _S.next_check = now + CHECK_INTERVAL
        if gc_option.value:
            viewport = ENGINE.GameViewport
            world = viewport.World if viewport is not None else None
            pc = get_pc(possibly_loading=True)
            # No character: loading (nobody sees a frame). A menu (cursor) counts only once it was
            # up at the last check too: a pass as it opens stalls its opening animation
            loading = pc is None or pc.Pawn is None
            menu = not loading and bool(pc.bShowMouseCursor)
            settled, _S.menu_seen = menu and _S.menu_seen, menu
            if loading:
                _S.next_check = now + LOADING_CHECK_S
            address = world._get_address() if world is not None else None  # noqa: SLF001
            if done := gc_tune.step(address, quiet=settled, loading=loading):
                _log(f"Python objects frozen ({done})")
        if dlss_option.value:
            render.enforce(render.DLSS)
        if framegen_option.value:
            render.enforce(render.FRAMEGEN)
    except Exception as ex:  # noqa: BLE001 - never let our tick break the game's
        logging.error(f"[Performance Fixes] {ex!r}")


def _cleanup(*, python: bool = True, cvars: bool | list[str] = True) -> None:
    """Undoes our changes (all cvars, or the listed ones) on the game thread: now if we're on it,
    else on its next tick."""

    def run() -> None:
        if cvars:
            render.restore(None if cvars is True else cvars)
        if python and python_state.unpin_here():
            _log("game-thread Python state released")

    if threading.get_ident() == _S.game_thread or _S.game_thread is None:
        run()
        return

    def once(*_a: Any) -> None:
        try:
            frametick.remove(CLEANUP_ID)
            run()
        except Exception as ex:  # noqa: BLE001
            logging.error(f"[Performance Fixes] {ex!r}")

    frametick.add(CLEANUP_ID, once)


def _enable() -> None:
    _S.next_check = 0.0
    if memory_option.value:
        _memory_changed(memory_option, memory_option.value)


def _disable() -> None:
    try:
        _log(memory.restore())
    except Exception as ex:  # noqa: BLE001
        logging.error(f"[Performance Fixes] {ex!r}")
    if gc_tune.restore():
        _log("Python objects unfrozen")
    _cleanup()


# A mod with no settings file loads switched off (a manual install, issue #5): start on
from .firston import ensure_on  # noqa: E402

ensure_on(__name__)

mod = build_mod(
    options=[python_option, gc_option, framegen_option, dlss_option, memory_option],
    hooks=[tick],
    on_enable=_enable,
    on_disable=_disable,
)
