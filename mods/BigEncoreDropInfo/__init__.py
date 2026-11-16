# -*- coding: utf-8 -*-
"""Loot Map drop presentation with an additive, guarded Encore travel preview."""
from mods_base import build_mod, Game, CoopSupport, keybind, command
from unrealsdk import logging
from .probe import capture
from .transport import start, stop
from . import encore_runtime, ui_page, uilink, frametick

__version__ = '0.6.0-preview.18'


@keybind('BigEncoreDropInfo_Capture', 'F10',
         display_name='记录奥矿处理器位置',
         description='在盛大安可列表中选择奥矿处理器，站到处理器前并按 F10 记录位置。')
def capture_key():
    encore_runtime.request_processor_record()


@command('bedi_capture')
def capture_command(_args):
    capture()


@frametick.tick('BigEncoreDropInfo.UILink')
def ui_tick():
    # Shared dispatch runs at most once per game frame across all carrying mods.
    uilink.tick()


def ready():
    start()
    try:
        ui_page.start()
    except Exception as exc:
        logging.error('[BigEncoreDropInfo] 界面接入失败：' + str(exc))
    try:
        encore_runtime.start()
    except Exception as exc:
        # Travel failure must not disable the existing dedicated-drop tooltips.
        logging.error('[BigEncoreMapTeleport] travel disabled: ' + str(exc))
    logging.info('[BigEncoreDropInfo] READY 0.6.0-preview.18; dedicated drops retained; Encore preview enabled')


def disable():
    ui_page.stop()
    encore_runtime.stop()
    stop()


mod = build_mod(name='Loot Map + Big Encore Travel (Preview)', author='BigEncoreDropInfo',
                version=__version__, supported_games=Game.BL4,
                coop_support=CoopSupport.ClientSide, auto_enable=True,
                description='显示专属掉落信息和各地区盛大安可首领列表，提供常驻重开按钮、自动跨图旅行与目标区域加载。仅房主或单人游戏可传送，需确认并通过地面及角色碰撞体检查。通过共享 UILink 加载界面，无需安装本 Mod 专用 PAK；首次生成共享入口后需重启游戏。预览版本，尚待游戏内验证。',
                keybinds=[capture_key], commands=[capture_command], hooks=[ui_tick], options=[],
                on_enable=ready, on_disable=disable)

# auto_enable restores saved state; it does not enable a newly installed mod.
# Establish the first-run default, while respecting a subsequent saved disable.
if not mod.settings_file.exists():
    mod.enable()
