# -*- coding: utf-8 -*-
"""Publish loose UI files and register them with the shared BL4 UI Link.

No native page is replaced, and this module never creates a BigEncore-specific PAK.
UILink owns its one shared, version-checked bootstrap PAK, including safe restart staging.
File I/O and stale-PAK discovery run on a worker; UILink.tick runs on the game thread.
"""
from __future__ import annotations

import threading
from importlib import resources
from pathlib import Path

from . import uilink

LINK_KEY = "bigencore"
SCRIPT_URL = "coui://uiresources/bl4bigencore/entry.js"
ASSETS = resources.files(__package__).joinpath("ui")
FILES = ("encore.js", "drops.js", "entry.js")
LEGACY_PAK = "BigEncoreMapTeleport_UI_1000_P.pak"
_lock = threading.Lock()
_generation = 0
_status = "尚未启用"


def publish(game_dir: Path) -> None:
    """Pure file I/O; importlib.resources also works inside an .sdkmod ZIP."""
    root = game_dir / "OakGame/Content/uiresources/bl4bigencore"
    root.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        data = ASSETS.joinpath(name).read_bytes()
        target = root / name
        if target.is_file() and target.read_bytes() == data:
            continue
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(target)


def legacy_paks(game_dir: Path) -> list[Path]:
    """Detect the supplied old PAK in any Paks subfolder; never delete a mounted PAK."""
    root = game_dir / "OakGame/Content/Paks"
    if not root.exists():
        return []
    return [path for path in root.rglob("*.pak") if path.name.casefold() == LEGACY_PAK.casefold()]


def _sync(game_dir: Path, generation: int) -> None:
    global _status
    from unrealsdk import logging

    try:
        with _lock:
            if generation != _generation:
                return
            publish(game_dir)
            # Publish every dependency before announcing entry.js to the page.
            # register() is pure Python; the SDK work remains in ui_tick().
            uilink.register(LINK_KEY, SCRIPT_URL, lambda: {"enabled": True}, lambda _action: None,
                            views=(uilink.MENUS,), mod=__package__)
            old = legacy_paks(game_dir)
            _status = "界面脚本已发布；共享 UILink 负责加载。"
            if old:
                _status = "检测到旧版 UI PAK；请退出游戏后移除，再重启：" + ", ".join(map(str, old))
                logging.warning("[BigEncoreDropInfo] " + _status)
            else:
                logging.info("[BigEncoreDropInfo] " + _status)
    except Exception as exc:
        with _lock:
            if generation == _generation:
                _status = "界面文件发布失败：" + str(exc)
        logging.error("[BigEncoreDropInfo] " + str(exc))


def start() -> None:
    global _generation
    from mods_base import SETTINGS_DIR

    with _lock:
        _generation += 1
        generation = _generation
    # Match the other mods: SETTINGS_DIR == <game>/sdk_mods/settings.
    game_dir = SETTINGS_DIR.parent.parent
    threading.Thread(target=_sync, args=(game_dir, generation),
                     name="BigEncoreDropInfo.ui", daemon=True).start()


def stop() -> None:
    global _generation, _status
    with _lock:
        _generation += 1
        _status = "界面已禁用"
    # UILink invokes the script's teardown: removes buttons/tooltips and restores native methods.
    # Leave harmless loose files on disk; never change the shared PAK on disable.
    uilink.unregister(LINK_KEY)


def status() -> str:
    return _status
