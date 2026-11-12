"""Free Golden Chest through its original success flow."""
import copy
import unrealsdk
from mods_base import build_mod
from unrealsdk import logging
from unrealsdk.hooks import Type, add_hook, remove_hook

_backups = []
_idle_function = "/Game/GameData/Lootables/ActorScripts/Script_Lootable_GoldenChest.Script_Lootable_GoldenChest_C:Idle__OnStateEnabled"
_hook_id = "golden_chest_repeat.auto_apply"

def apply_loaded_chests():
    #count = 0
    try:
        for chest in unrealsdk.find_all("LootableObject"):
            if "Lootable_GoldenChest" not in str(chest):
                continue
            if any(saved == chest for saved, _ in _backups):
                continue
            config = chest.UsabilityConfigInfo
            response = next(r for r in config.UsabilityData.PrimaryUseInfo.UseResponses
                            if "UsePrompt_GoldenKey" in str(r.Prompt))
            if not response.StateChanges:
                continue
            _backups.append((chest, copy.deepcopy(config)))
            #response.CostRequirements.bUseAttributeCost = False
            response.CostRequirements.CostAmount.constant = 0.0
            response.StateChanges[0].StateMachine = "shifttransaction"
            response.StateChanges[0].State = "success"
            #count += 1
        #if count:
            #logging.info(f"Golden Chest: free interaction applied to {count} loaded chest(s).")
    except Exception as exc:
        logging.error(f"Golden Chest: {type(exc).__name__}: {exc}")

def on_idle(obj, args, ret, func):
    apply_loaded_chests()

def on_end_play(obj, args, ret, func):
    _backups[:] = [(chest, config) for chest, config in _backups if chest != obj]

def on_enable():
    add_hook(_idle_function, Type.POST, _hook_id, on_idle)
    add_hook("/Script/Engine.Actor:ReceiveEndPlay", Type.PRE, _hook_id, on_end_play)
    apply_loaded_chests()
    logging.info("Golden Chest: automatic application enabled; waiting for chest Idle events.")

def on_disable():
    remove_hook(_idle_function, Type.POST, _hook_id)
    remove_hook("/Script/Engine.Actor:ReceiveEndPlay", Type.PRE, _hook_id)
    while _backups:
        chest, config = _backups.pop()
        try:
            chest.UsabilityConfigInfo = config
        except Exception:
            logging.warning("Golden Chest: could not restore an unloaded chest.")

build_mod(name="Golden Chest Repeat", author="Cissa", version="0.3.0",
          description="Free Golden Chest Openings. "
                      "Automatically applies on chest Idle events.",
          keybinds=[], auto_enable=True, on_enable=on_enable, on_disable=on_disable)
