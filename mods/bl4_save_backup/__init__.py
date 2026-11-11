# -*- coding: utf-8 -*-
"""
Save Backups for Borderlands 4: a copy of every save each time the game starts, with a history
per character and for the bank, and restores of a character, the bank or everything.

- At launch (once per game process, on a worker thread) every .sav of every Steam account
  (profile.sav and each character) is copied into
  `Documents/My Games/Borderlands 4/Saved/BL4Fix Save Backups/<Steam ID>/<date>/`, each file read
  until it decrypts whole. Nothing changed since the last backup = no new one.
- The oldest backups go past the "Backups to keep" count, and past 1 GB in all; ones marked Keep
  never do.
- The page (MODS > BL4 Save Backups) shows each character's versions (level, playtime, cash, items,
  what changed), the bank's, and every backup. Restores are staged and applied by a hidden helper
  after the game closes (restore.py), with a "before restore" backup first.

Co-op: local only (saves are on each player's own PC).

Everything but this file can be hot-reloaded (dev/reload_save_backup.py).
"""

from __future__ import annotations

import os
import sys
import traceback
import types

from mods_base import SETTINGS_DIR, BoolOption, ButtonOption, SpinnerOption, build_mod, command
from unrealsdk import logging

from . import backups, frametick, page

__version__ = "0.1.0"
__version_info__ = (0, 1, 0)

MOD_NAME = page.MOD_NAME

# Survives hot reloads: the launch backup runs once per game process
_state = sys.modules.get("_bl4_save_backup_state")
if _state is None:
    _state = types.ModuleType("_bl4_save_backup_state")
    _state.launch_pid = 0
    sys.modules["_bl4_save_backup_state"] = _state


def _log(text: str, error: bool = False) -> None:
    (logging.error if error else logging.info)(f"[Save Backups] {text}")


def _keep_changed(_: SpinnerOption, value: str) -> None:
    backups.W.keep = value
    backups.submit("prune", backups.prune)


keep_option = SpinnerOption(
    "Backups to keep",
    backups.DEFAULT_KEEP,
    backups.KEEP_CHOICES,
    wrap_enabled=False,
    description=(
        "存档发生变化时，每次启动游戏都会生成备份。超过指定数量的旧备份会被清理。无论选择多少，总容量上限均为 1 GB；每份通常只有几百 KB，1 GB 可容纳数千份。标记为“保留”的备份不会被自动删除。"
    ),
    on_change_while_enabled=_keep_changed,
    display_name="保留备份数量",
)
launch_option = BoolOption(
    "Back up when the game starts",
    True,
    description="游戏启动时复制所有角色存档与个人档案（包含银行）。",
    display_name="启动游戏时备份",
    true_text="开启",
    false_text="关闭",
)


def _backup_now(_: ButtonOption) -> None:
    backups.submit("backup", lambda: backups.backup("manual"), "正在备份存档……")


backup_button = ButtonOption(
    "Back up now",
    description="立即复制所有存档。游戏会在游玩时持续保存，因此可备份截至当前的游戏进度。",
    on_press=_backup_now,
    display_name="立即备份",
)
folder_button = ButtonOption(
    "Open the backup folder",
    description="在资源管理器中显示备份。每个备份文件夹都包含存档文件的原样副本。",
    on_press=lambda _: backups.submit("folder", backups.open_folder),
    display_name="打开备份文件夹",
)


@frametick.tick("bl4_save_backup", every=0.25)
def _tick() -> None:
    try:
        page.tick()
    except Exception as ex:  # noqa: BLE001 - never let our tick break the game's
        if repr(ex) != getattr(_tick, "_last", None):
            _tick._last = repr(ex)  # type: ignore[attr-defined]
            logging.error("".join(traceback.format_exception(ex)))


def _enable() -> None:
    # Mods are enabled on another thread than the game thread: only files and threads here
    backups.W.log = _log
    backups.W.changed = page.changed
    backups.W.keep = keep_option.value if keep_option.value in backups.KEEP_CHOICES else backups.DEFAULT_KEEP
    backups.configure(SETTINGS_DIR.parent.parent, SETTINGS_DIR, page.UI_DIR)
    launch = launch_option.value and _state.launch_pid != os.getpid()
    _state.launch_pid = os.getpid()
    backups.at_enable(launch)


def _disable() -> None:
    page.unregister()
    backups.submit("cancel all", backups.cancel_all_accounts)


def backup_now(reason: str, timeout: float = 10.0) -> bool:
    """For other mods (the Mod Menu, before another modder's mod loads): copies the saves now and
    waits up to `timeout` s. True once they're in a backup. Worker threads only (backups.backup_now)."""
    return backups.backup_now(reason, timeout)


@command("savebackup", description="立即复制所有存档。请在 MODS 菜单的存档备份页面查看备份。")
def backup_command(_: object) -> None:
    _backup_now(backup_button)


# A mod with no settings file loads switched off (a manual install, issue #5): start on
from .firston import ensure_on  # noqa: E402

ensure_on(__name__)

mod = build_mod(
    options=[keep_option, launch_option, backup_button, folder_button],
    hooks=[_tick],
    commands=[backup_command],
    on_enable=_enable,
    on_disable=_disable,
)
