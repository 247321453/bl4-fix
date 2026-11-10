"""Simplified Chinese labels for display only; never change item data or card matching names."""

from __future__ import annotations

# Known modifier labels. Internal keys, part IDs, weights and serials remain untranslated.
STAT_NAMES: dict[str, str] = {
    "Action Skill Cooldown Rate": "主动技能冷却速率",
    "Action Skill Damage": "主动技能伤害",
    "Action Skill Duration": "主动技能持续时间",
    "Attunement Skill Duration": "调谐技能持续时间",
    "Command Skill Cooldown Rate": "指令技能冷却速率",
    "Critical Hit Damage": "暴击伤害",
    "Cryo Damage": "冰冻伤害",
    "Damage Dealt": "造成的伤害",
    "Damage Reduction": "伤害减免",
    "Detonation Damage": "引爆伤害",
    "Elemental Damage": "元素伤害",
    "Energy Shield Regeneration Rate": "能量护盾恢复速率",
    "Fire Rate": "射速",
    "Forgedrone Duration": "锻造无人机持续时间",
    "Forgeskill Damage": "锻造技能伤害",
    "Hazard Damage": "危害伤害",
    "Health Regen per second": "每秒生命恢复",
    "Incendiary Damage": "燃烧伤害",
    "Kinetic Damage": "动能伤害",
    "Lifesteal": "生命偷取",
    "Maximum Health Capacity": "最大生命值",
    "Maximum Shield Capacity": "最大护盾容量",
    "Melee Critical Hit Chance": "近战暴击率",
    "Melee Damage": "近战伤害",
    "Minion Damage": "召唤物伤害",
    "Movement Speed": "移动速度",
    "Ordnance Cooldown Rate": "军械冷却速率",
    "Ordnance Critical Hit Chance": "军械暴击率",
    "Ordnance Damage": "军械伤害",
    "Phase Clone Health loss over time": "相位分身持续生命损耗",
    "Reload Speed": "换弹速度",
    "Skill Critical Hit Chance": "技能暴击率",
    "Skill Damage": "技能伤害",
    "Splash Damage": "溅射伤害",
    "Stasis Damage": "停滞伤害",
    "Status Effect Application Chance": "状态效果施加概率",
    "Status Effect Damage": "状态效果伤害",
    "Submachine Gun Damage": "冲锋枪伤害",
    "Gun Critical Hit Chance": "枪械暴击率",
}

_WEAPONS = {
    "Gun": "枪械",
    "Assault Rifle": "突击步枪",
    "Pistol": "手枪",
    "SMG": "冲锋枪",
    "Shotgun": "霰弹枪",
    "Sniper Rifle": "狙击步枪",
}
_WEAPON_STATS = {
    "ADS Proficiency": "瞄准熟练度",
    "Accuracy": "精准度",
    "Critical Damage": "暴击伤害",
    "Damage": "伤害",
    "Equip Speed": "切换速度",
    "Fire Rate": "射速",
    "Magazine Size": "弹匣容量",
    "Reload Speed": "换弹速度",
    "Splash Damage": "溅射伤害",
    "Splash Radius": "溅射半径",
    "Status Effect Chance": "状态效果触发概率",
    "Status Effect Damage": "状态效果伤害",
}
STAT_NAMES.update({
    f"{weapon} {stat}": f"{weapon_zh}{stat_zh}"
    for weapon, weapon_zh in _WEAPONS.items()
    for stat, stat_zh in _WEAPON_STATS.items()
})

_ITEM_LABELS = {
    **_WEAPONS,
    "Class Mod": "职业模组",
    "Enhancement": "强化装置",
    "Grenade": "手雷",
    "Heavy": "重型武器",
    "Repkit": "修复套件",
    "Shield": "护盾",
}
_RARITIES = {
    "common": "普通",
    "uncommon": "优秀",
    "rare": "稀有",
    "epic": "史诗",
    "legendary": "传奇",
    "pearl": "珠光",
    "pearlescent": "珠光",
}


def stat_name(name: str) -> str:
    """Translate a known label, preserving unknown labels from future game versions."""
    return STAT_NAMES.get(name, name)


def item_label(label: str) -> str:
    """Translate item types, retaining manufacturer and class proper names."""
    if label in _ITEM_LABELS:
        return _ITEM_LABELS[label]
    for suffix in (" Class Mod", " Enhancement"):
        if label.endswith(suffix):
            return label[:-len(suffix)] + " " + _ITEM_LABELS[suffix.strip()]
    return label


def rarity_name(name: str) -> str:
    return _RARITIES.get(name.lower(), name)
