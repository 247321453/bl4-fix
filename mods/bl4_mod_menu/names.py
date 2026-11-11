# -*- coding: utf-8 -*-
"""Read optional Chinese labels without ever changing a Mod's canonical name."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from . import hotload


def display_name(mod: Any) -> str:
    """Both unpacked and .sdkmod sources; malformed/missing metadata falls back to English."""
    settings = getattr(mod, "settings_file", None)
    mod_id = Path(settings).stem.split(".", 1)[0] if settings is not None else ""
    if not mod_id or mod_id not in sys.modules:
        mod_id = type(mod).__module__.split(".", 1)[0]
    path = hotload.module_file(mod_id)
    if path is not None:
        info = hotload.read_info(path)
        # A package can register multiple Mod objects: only its declared name gets this label.
        if info.get("name") == mod.name and info.get("cn_name"):
            return info["cn_name"]
    return mod.name
