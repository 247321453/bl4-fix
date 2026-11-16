# 掉落地图与盛大安可传送（中文 / UILink 版）

基于用户提供的 BigEncoreDropInfo 0.6.0-preview.18，保留原版首领识别、传送检查、确认流程和 F10 位置记录。

## 安装

1. 退出游戏，把 `BigEncoreDropInfo.sdkmod` 放入游戏的 `sdk_mods`，替换同名旧版本。不要同时保留源代码目录和同名 sdkmod。
2. **如果以前安装过原版配套 PAK**，退出游戏后，移除 `OakGame/Content/Paks` 或其子目录中的 `BigEncoreMapTeleport_UI_1000_P.pak`。不要保留多份或改名留在 Paks 内。新版会检测这个原文件名并在 SDK 日志中提醒，但不会在游戏运行时删除/覆盖已挂载的 PAK。
3. 开始游戏并启用本 Mod。如果首次生成共享 UILink 入口 PAK，需退出并重新启动游戏后界面才能显示。

**无需安装本 Mod 专用 PAK，也不依赖 bl4_mod_menu。** 已有其他使用 UILink 的 Mod 时，复用同一个共享入口 `OakGame/Content/Paks/~mods/BL4Fix_UILink_4251_P.pak`。

此方案不是完全零 PAK：游戏原生页面需要共享入口来加载 Python Mod 的脚本。共享入口由原有 UILink 自动检查、生成和安全更新，只有它存在于 PAK 中；本 Mod 不再替换游戏的地图 HTML、地图 JS 或交互提示 JS。如果游戏更新改变了共享入口的基础文件，UILink 会暂停，而不是强行覆盖。

## 自动发布的松散文件

启用时，从 sdkmod 中复制三个界面脚本到：

- `OakGame/Content/uiresources/bl4bigencore/entry.js`：UILink 入口。
- `OakGame/Content/uiresources/bl4bigencore/encore.js`：首领列表、传送确认和状态显示。
- `OakGame/Content/uiresources/bl4bigencore/drops.js`：地图图标的专属掉落提示。

脚本只在菜单页面加载。禁用时，UILink 调用清理函数，关闭面板、移除掉落提示、解绑观察器/计时器和本 Mod 添加的地图方法包装。不会删除其他 Mod 使用的共享 PAK。磁盘上的松散脚本保留，但不再加载。

## 中文与原始数据

- 保留英文 `name`、原始 `map_names` 顺序、物品/首领 ID、路径、坐标、传送请求字段和会话检查。
- JSON 增加 `cn_name`、`cn_map_names` 等展示字段；中文地图标题匹配采用精确别名，不进行首领名模糊猜测。
- 界面使用中文首领、物品、装备类型、地区、生命值构成、推荐属性、确认按钮和常见错误提示。已知物品/首领优先复用已有汉化及游戏文本，没有现成译名的新增地点/活动名采用补充译名，可能需要按游戏内名称微调。
- F10 仍只记录所选奥矿处理器的位置，传送仍需要确认，房主/单人、载具、战斗状态、落地和加载等限制仍由原版代码处理。

## 验证范围

已进行离线语法、资源/PAK、数据不变性及模拟菜单界面测试；未连接真实游戏或 oak_sdk Python 3.11 运行时。原版仍为预览版本，跨图传送需要在游戏中验证。

## 开发维护

`uilink/`、`frametick/`、`gamekeys/` 来自仓库 `shared/`，与其他 Mod 使用相同副本。不要单独修改这些副本，维护入口为仓库 `tools/sync_shared.py`。
原作者代码的署名保持不变，新增共享依赖的版权信息见 `NOTICE.txt` 和 `LICENSE-BL4Fix-shared`。
