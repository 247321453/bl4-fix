# -*- coding: utf-8 -*-
"""Reroll the item in Mod Menu's retained subpage while the inventory is open."""

from __future__ import annotations

import sys
import time
from collections.abc import Callable
from typing import Any

from . import uilink

KEY = "reroll_menu"
SCRIPT_URL = "coui://uiresources/bl4reroll/menu_reroll.js"
MOD_NAME = "BL4 Reroll"
VIEW_TTL = 0.4
REQUEST_TTL = 0.4
COOLDOWN = 0.25


class S:
    enabled = False
    pages: dict[int, str] = {}  # handle -> serial captured by an actual whole-item button
    context: dict[str, Any] | None = None
    context_at = -1e9
    inventory = False
    inventory_at = -1e9
    operation = 0
    closed = -1
    down = True  # a held key on enable must be released before it can activate
    busy = False
    ready_at = 0.0
    sequence = 0
    pending: dict[str, Any] | None = None
    key: Callable[[], str | None] = lambda: None
    allowed: Callable[[], bool] = lambda: False
    execute: Callable[[int, str, Callable[[], None]], None] | None = None


def clear_pages() -> None:
    S.pages = {}
    uilink.changed(KEY)


def remember(handle: int, serial: str) -> None:
    S.pages[handle] = serial


def _context(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    handle, serial, page = value.get("handle"), value.get("serial"), value.get("page")
    if type(handle) is not int or not isinstance(serial, str) or not isinstance(page, str):
        return None
    if not page or len(page) > 160 or S.pages.get(handle) != serial:
        return None
    return {"handle": handle, "serial": serial, "page": page}


def _web_ready() -> bool:
    web = sys.modules.get("bl4_mod_menu.web")
    try:
        # page_open only describes the overlay's visibility, not its retained navigation.
        return bool(web and web.connected() and web.Link.capture is None)
    except Exception:  # another Mod Menu version: do nothing rather than guess a page
        return False


def _inventory_ready() -> bool:
    return S.inventory and time.monotonic() - S.inventory_at <= VIEW_TTL


def _native_context() -> dict[str, Any] | None:
    menu = sys.modules.get("bl4_mod_menu.menu")
    state = getattr(menu, "S", None)
    if not state or not state.is_open or state.mod_name != MOD_NAME or state.capture is not None:
        return None
    nested = state.nested
    if len(nested) != 1 or not isinstance(nested[0], str):
        return None
    ident = nested[0]
    if not ident.startswith("item") or not ident[4:].isdigit():
        return None
    handle = int(ident[4:])
    serial = S.pages.get(handle)
    return {"handle": handle, "serial": serial, "page": "native:" + ident} if serial else None


def active() -> bool:
    """The inventory is open and a supported item page is retained, visible or hidden."""
    if not S.enabled or not _inventory_ready():
        return False
    if _native_context() is not None:
        return True
    return bool(_web_ready() and S.context is not None
                and time.monotonic() - S.context_at <= VIEW_TTL
                and S.closed == uilink.menus_closed()
                and _context(S.context) == S.context)


def state() -> dict[str, Any]:
    return {"pages": {"item" + str(h): s for h, s in S.pages.items()}, "request": S.pending}


def _done(operation: int) -> None:
    if operation != S.operation:
        return
    S.busy = False
    S.ready_at = time.monotonic() + COOLDOWN


def _execute(context: dict[str, Any]) -> None:
    if (not S.enabled or S.busy or not _inventory_ready() or not uilink.game_focused()
            or time.monotonic() < S.ready_at
            or not S.allowed() or S.execute is None
            or S.pages.get(context["handle"]) != context["serial"]):
        return
    S.busy = True
    S.operation += 1
    operation = S.operation
    try:
        S.execute(context["handle"], context["serial"], lambda: _done(operation))
    except Exception:
        _done(operation)
        raise


def act(action: dict[str, Any]) -> None:
    if not S.enabled:
        return
    now = time.monotonic()
    if action.get("do") == "view":
        S.inventory = action.get("inventory") is True
        S.inventory_at = now
        context = _context(action.get("context")) if _inventory_ready() and _web_ready() else None
        if context != S.context:
            S.pending = None
            uilink.changed(KEY)
        S.context, S.context_at = context, now
        S.closed = uilink.menus_closed()
    elif action.get("do") == "reroll":
        request = S.pending
        if request is None or type(action.get("id")) is not int or action["id"] != request["id"]:
            return
        # Consume before validating/executing: retries or two page-link copies cannot charge twice.
        S.pending = None
        uilink.changed(KEY)
        context = _context(action.get("context"))
        if (now > request["until"] or now - S.context_at > VIEW_TTL
                or not _inventory_ready() or not _web_ready()
                or S.closed != uilink.menus_closed() or not uilink.game_focused()
                or context is None or context != request["context"] or context != S.context):
            return
        _execute(context)


def tick() -> None:
    if not S.enabled or not uilink.game_focused():
        S.down = True  # holding a key while returning from another window must not activate
        if S.pending is not None:
            S.pending = None
            uilink.changed(KEY)
        return
    down = bool(uilink.key_down(S.key()))
    pressed = down and not S.down
    S.down = down
    now = time.monotonic()
    if S.pending is not None and now > S.pending["until"]:
        S.pending = None
        uilink.changed(KEY)
    if (not S.enabled or not pressed or S.busy or not _inventory_ready()
            or now < S.ready_at or not S.allowed()):
        return
    native = _native_context()
    if native is not None:
        _execute(native)
        return
    if (not _web_ready() or S.context is None or now - S.context_at > VIEW_TTL
            or S.closed != uilink.menus_closed()):
        return
    # Ask the live HTML page to re-check the exact same subpage before doing anything.
    S.sequence += 1
    S.pending = {"id": S.sequence, "context": dict(S.context), "until": now + REQUEST_TTL}
    uilink.changed(KEY)


def register() -> None:
    S.enabled = True
    S.down = True
    S.context = S.pending = None
    S.inventory = False
    S.inventory_at = -1e9
    S.operation += 1
    S.busy = False
    S.ready_at = 0.0
    uilink.register(KEY, SCRIPT_URL, state, act, views=(uilink.MENUS,), mod="Reroll")


def unregister() -> None:
    S.enabled = False
    S.operation += 1
    S.inventory = False
    S.context = S.pending = None
    S.down = True
    clear_pages()
    uilink.unregister(KEY)
