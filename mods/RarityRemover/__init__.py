# -*- coding: utf-8 -*-
from typing import Any 
from mods_base import hook, build_mod, SliderOption, BoolOption, get_pc
from unrealsdk import find_class
from unrealsdk.hooks import Type
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct 

statics = find_class("GameplayStatics").ClassDefaultObject
@hook("/Script/Engine.PlayerController:ServerAcknowledgePossession",Type.POST)
def SetRarityMods(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) ->  None:
    set_rarities()


@hook("/Script/OakGame.OakCharacter:BroadcastLevelUp",Type.POST)
def LevelUpRarities(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) ->  None:
    if obj.IsPlayerControlled():
        set_rarities()


def set_rarities(option = None, new_value = None):
    if not get_pc():
        return
    
    game_state = statics.GetGameState(get_pc())
    player_level = get_pc().PlayerState.ExperienceState[0].ExperienceLevel
    if oidWhiteEnable.value:
        if player_level >= 5:
            game_state.RarityState.CommonModifier.Value = 0.75
        if player_level >= 10:
            game_state.RarityState.CommonModifier.Value = 0.5
        if player_level >= 15:
            game_state.RarityState.CommonModifier.Value = 0
    else:
        game_state.RarityState.CommonModifier.Value = 1

    if oidGreenEnable.value:
        if player_level >= 20:
            game_state.RarityState.UncommonModifier.Value = 0.5
        if player_level >= 25:
            game_state.RarityState.UncommonModifier.Value = 0
    else:
        game_state.RarityState.UncommonModifier.Value = 1

    if oidBlueEnable.value:
        if player_level >= 30:
            game_state.RarityState.RareModifier.Value = 0.9
        if player_level >= 40:
            game_state.RarityState.RareModifier.Value = 0.7
        if player_level >= 50:
            game_state.RarityState.RareModifier.Value = 0.5
        if player_level >= 60:
            game_state.RarityState.RareModifier.Value = 0.3
        if player_level >= 70:
            game_state.RarityState.RareModifier.Value = 0.1
    else:
        game_state.RarityState.RareModifier.Value = 1


oidWhiteEnable = BoolOption(
    "White Items",
    True,
    "On",
    "Off",
    display_name="白色品质",
    description="角色等级小于15级才会掉落白色品质",
    on_change=set_rarities
)
oidGreenEnable = BoolOption(
    "Green Items",
    True,
    "On",
    "Off",
    display_name="绿色品质",
    description="角色等级小于25级才会掉落绿色品质",
    on_change=set_rarities
)
oidBlueEnable = BoolOption(
    "Blue Items",
    True,
    "On",
    "Off",
    display_name="蓝色品质",
    description="角色等级小于50级才会掉落蓝色品质",
    on_change=set_rarities
)

mod_options = [
    oidWhiteEnable,
    oidGreenEnable,
    oidBlueEnable,
]

build_mod(options=mod_options)