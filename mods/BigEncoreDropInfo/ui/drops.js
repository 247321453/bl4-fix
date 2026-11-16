/* Event-only Cohtml receiver. No game actions or UObject access. */
(function () {
    'use strict';
    const endpoint = 'http://127.0.0.1:19386/big-encore-20261019-v1';

 const locale={"labels":{"Abyss":"深渊","Acey May":"艾西·梅","Adrenaline Pump":"肾上腺素泵","Aegon's Dream":"嗡嗡枪口","AeroDramatic":"空中戏剧","Alignment":"协调一致","Anarchy":"无政府主义","Anchor":"铁锚","Ancient":"古老","ARC-TAN":"正反切","Artificer":"军工技师","Artillery Sphere":"火炮球体","Asher's Rise":"亚瑟的崛起","Astonisher":"惊奇者","Atling Gun":"阿特林机枪","Augmenter AF1000":"义体AF1000","Avarice":"贪婪","Avatar":"神通","Barb'ara":"芭芭拉","Bio-Robot":"生化机器","Birt's Bees":"伯特的蜜蜂","Bismuth-Tipped Dagger":"飞刀","Blacksmith":"铁匠","Blockbuster":"一鸣惊人","Blood Analyzer":"血液分析仪","Blood Moon":"血月","Bloody Lumberjack":"血腥伐木工","Bod":"生化","Bombastic":"夸夸其谈","Bonnie and Clyde":"雌雄大盗","Boomer":"爆破手","Boomslang":"树蛇","Borstel Ballista":"博斯特尔弩炮","Bottled Lightning":"瓶装闪电","Brickhouse":"砖屋","Broken Wings":"折翼","Bubbles":"泡泡","Budget Deity":"预算之神","Bugbear":"熊熊虫","Bully":"霸凌","Buoy":"浮标","Buster":"破坏分子","Buzz Axe":"震颤斧","Buzzymuzz":"嗡嗡枪口","Chaumurky":"乔穆尔基","Chirurgeon":"外科医生","Chuck":"查克","Cindershelly":"灰烬壳","Clarity":"克拉里蒂","Cold Shoulder":"冷屁股","Collector":"收藏家","Compleation":"完成","Complex Root":"复杂根须","Configuration":"配置","Conflux":"汇流","Constable":"康斯特布尔","Convergence":"地狱猎犬","Cooler":"冷却器","Cooper Duper":"库珀欺诈者","Cormano":"科尔马诺","Countermeasure":"反制措施","Crazed Earl":"疯狂厄尔","Critical Decay":"暴击衰减","Crow-Sourced":"大众协作","Damned":"诅咒","Dancer":"舞者","Darkbeast":"暗兽","Decompiler":"反编译器","Defibrillator":"除颤仪","Destructo Disco":"毁灭迪斯科","Devourer":"吞噬者","Disc Jockey":"唱片骑师","Discy Business":"盘子生意","Divided Focus":"焦点分散","Divided Glow":"分裂光芒","Doeshot":"一命呼呼","Draupner":"德劳普纳","Driver":"司机","Eigenburst":"特征爆发","Elementalist":"元素使者","Enumeration":"枚举","Eradication":"根除","Esgrimidor":"击剑手","Exfoliatrix":"前任剥皮姬","Exhibition":"展览","Falke":"猎鹰","Faulty Detonator":"雷管故障","Fearstalker":"恐惧追猎者","Filántropo":"慈善家","Finnity XXX-L":"芬妮迪XXX-L","Firebreak":"防火线","Firepot":"火锅","Firewerks":"烟火表演","First Impression":"第一印象","Fisheye":"鱼眼","Fishward":"鱼群","Flak Cannon":"高射炮","Flash Cyclone":"闪电旋风","Flash Fuel":"闪光燃料","Fleabag":"跳蚤袋","Font of Life":"生命源泉","Forge Master":"锻造大师","Forsaken Chaos":"遗弃之混沌","Fourier's Malady":"傅里叶综合症","Functional Human":"功能性人类","Furnace":"熔炉","Fuse":"导火索","G.M.R.":"G.M.R.","Gamer":"玩家","Gamma Void":"伽马虚空","Generator":"发电机","Goalkeeper":"门将","GOAT":"史上最强","Golden God":"黄金之神","Gomie":"老铁","Goremaster":"血腥大师","Grenazerker":"掷弹狂战士","Grim Sister":"冷酷姐姐","Guardian Angel":"守护天使","Hair Trigger":"一触即发","Hand Frag":"破片手雷","Handcannon":"手铳","Hard Dark":"黑暗能量","Hardpoint":"承力点","Healthraiser":"生命值提升器","Heavyweight":"重量级","Heimdahl":"海姆达尔","Hellfire":"地狱火","Hellhound":"地狱猎犬","Hellwalker":"地狱行者","Hemorrhage":"出血","Herald":"赫拉德","Hippo Gun":"河马枪","Hoarder":"囤积者","Honey Badger":"蜜獾","Honeymooner":"蜜月期","Hooligan":"街头混混","Hopscotch":"跳房子","Hot Slugger":"强力重击手","Hotshot":"能人","Hugger":"拥抱者","Husky Friend":"哈士奇好友","Hydrowerks":"水力机械","Ichor":"灵液","Illusionist":"幻术师","Infection":"感染","Inkling":"迹象","Inscriber":"记录器","Instigator":"煽动者","Ishmael":"以实玛利","Jail-Broken Gatling":"越狱加特林","Jelly":"果冻","Jetsetter":"环球旅行家","Juliet's Sparkle":"朱丽叶之光","Kaleidosplode":"万花爆炸","Kaos":"混沌","Kaoson":"考森","Katagawa's Revenge":"片川的复仇","Kickballer":"踢球者","Kill Spring":"杀戮之春","Kindread Spirits":"契合知音","King's Gambit":"国王的策略","Lamplighter":"点灯行者","Laser Disker":"激光飞盘","Laser-Cutter":"激光切割器","Lead Balloon":"铅气球","Li'l Brudder":"小老弟","Light Gun":"轻型枪械","Linebacker":"钢铁后卫","Little Sister":"小妹妹","Living Weapon":"活体武器","Lockjaw":"锁喉","Loiter Sploiter":"徘徊剥削者","Lovelorn":"失恋者","Lucian's Flank":"卢西恩的侧攻","Lucky Clover":"幸运四叶草","Ludopath":"嗜赌如命","Luty Madlad":"疯小子卢迪","Mantra":"真言","Marshall's Claw":"马歇尔之爪","Martyr":"殉道者","Masochist":"受虐狂","Matador's Match":"斗牛大赛","Memory Hoarder":"记忆囤积者","Mercredi":"星期三","Mercurious":"水银好奇者","Midnight Defiance":"午夜之反抗","Misericorde":"慈悲为怀","Missilaser":"导弹激光","Montage Maker":"蒙太奇大师","Murmur":"轻柔低语","Noisy Cricket":"吵闹蟋蟀","Oak-Aged Cask":"陈年橡木桶","Ohm I Got":"我的天呐","Onion":"洋葱","Onslaught":"猛攻","Ordinance":"条例","Oscar Mike":"正在行动","Outburst":"爆发","Over Swarm":"蜂群过境","Overconsumption":"过度消耗","Overdriver":"超速驾驶","Oxidation":"氧化","Pacemaker":"起搏器","Pachonk":"帕琼克","Parasite":"寄生体","Petanque":"地滚球","Phantom Flame":"幻影火焰","Phlebotomist":"抽血师","Plague Engineer":"瘟疫工程师","Plasma Coil":"超导等离子线圈","Plasmaphile":"血浆爱好者","Plumb Bob":"铅垂线","Pocketshot":"微型射击","Potato Thrower IV":"土豆投掷者IV","Power-Puncher":"强力拳击手","Pragmate":"务实","Pressure Kettle":"高压锅","Prestidigitator":"魔术师","Prince Harming":"死马王子","Principal":"首要","PRISM":"棱镜","Programmer":"程序员","Protean Cell":"变形细胞","Prowler":"徘徊者","Puppetmaster":"傀儡师","Quadratus":"四方肌","Queen's Rest":"女王后宫","Raiden":"雷电","Rainbow Vomit":"彩虹呕吐物","Rainmaker":"造雨师","Rangefinder":"测距仪","Ravenfire":"渡鸦之火","Reactor":"反应堆","Reaparición":"重新显现","Recursive":"递归","Reminisce":"追忆","Rhythm":"韵律","Ripple":"涟漪","Roach":"蟑螂","Roil":"激怒","Rooker":"浪子","Roulette":"轮盘赌","Rounder":"巡回者","Rowan's Charge":"罗恩的冲锋","Rowdy Rider":"暴走骑士","Ruby's Grasp":"红宝石的触碰","San Saba Songbird":"圣萨巴鸣鸟","Scientist":"科学家","Scoot'n'Shoot":"疾行射击","Screwstonian":"糟糕烂人","Seeker":"探索者","Seventh Sense":"第七感","Shalashaska":"沙拉沙斯卡","Shammy Kablammy":"诈爆轰轰","Shardenfreude":"碎片狂欢","Sharkbait":"鲨鱼饵","Shatterwight":"碎尸者","Shield Overflow":"护盾泛滥","Shiny War Paint":"闪亮战妆","Sho Kunai":"翔苦无","Shoals":"浅滩","Sideshow":"余兴节目","Sidewinder":"响尾蛇","Silver Sliver":"银色碎片","Skeptic":"怀疑论者","Skully":"骷髅","Slippy":"滑溜溜","Solar Temper":"太阳怒焰","Soul Survivor":"灵魂幸存者","Sparky Shield":"电光护盾","Sprezzatura":"风流倜傥","Star Helix":"恒星螺旋","Stealth & Seek":"潜行与追踪","Stop Gap":"权宜之计","Stray":"偏离","Streamer":"直播网红","Sunspot":"太阳黑子","Super Soldier":"超级士兵","Superconducting Plasma Coil":"超导等离子线圈","Swan Song":"天鹅之歌","Swarm":"蜂群","Sweet Embrace":"甜蜜拥抱","Symmetry":"对称","T.K's Wave":"尊者波动","Table Hopper":"换桌客","Tankbuster":"反坦克炮","Technomancer":"科技术士","Teen Witch":"少女巫师","Tempered Essence":"淬炼精髓","Tempest":"风暴","Throwing Knife":"飞刀","Timekeeper's New Shield":"时间尊者新护盾","Trackstar":"田径明星","Trainer":"训练师","Transmitter":"发射器","Triple Bypass":"三重旁通","Triplicate":"三重复制","Trooper":"超级战士","Truck":"卡车","UAV":"无人机","Ultracapacitor":"超级电容","Undead Eye":"亡灵之眼","Undershield":"下部护盾","Unstable Kor":"不稳核心","Upgraded Finnity XXX-L":"升级版芬妮迪XXX-L","Urchin":"海胆","Vamoose":"闪人","Verce":"诗篇","Viking":"维京人","Virophile":"嗜毒者","Virtue":"美德","Vitae":"鲜血","Wastelander":"废土客","Waterfall":"瀑布","Watts 4 Dinner":"通电晚餐","Whale":"鲸鱼","Whiskey Foxtrot":"旺德发","Wind Skimmer":"风中飘舞","Windrider":"驭风者","Wombo Combo":"超杀连击","Zipper":"拉链","Aegon's Dream / Buzzymuzz":"伊耿的梦想 / 嗡嗡枪口","Alignment / Ancient / Seeker":"协调一致 / 古老 / 探索者","Bismuth-Tipped Dagger / Throwing Knife":"铋尖匕首 / 飞刀","Convergence / Hellhound":"汇聚 / 地狱猎犬","Elpis Star":"厄尔皮斯之星","Extra Medium":"超大中杯","Finnity XXX-L / Upgraded Finnity XXX-L":"芬妮迪XXX-L / 升级版芬妮迪XXX-L","Pandoran Memento":"潘多拉纪念品","Plasma Coil / Superconducting Plasma Coil":"等离子线圈 / 超导等离子线圈","Pocketshot / Sideshow":"微型射击 / 余兴节目","Spinning Blade":"旋转刀刃","Vile Lictor":"卑鄙鬼·里克托","Arjay":"阿杰","Primordial Guardian Radix":"原始护卫者·根源","Horace":"霍勒斯","Vile Grasp":"卑鄙鬼·格拉斯普","Brain Zane":"脑型赞恩","The Oppressor":"压迫者","Lieutenant Harmony":"哈莫妮中尉","Callous Harbinger of Annihilating Death":"冷酷的毁灭死亡先驱","Rocken Roller":"摇滚滚石","Vulkorr":"沃尔科尔","Primordial Guardian Inceptus":"原始护卫者·源始","Idolator Sol":"教主索尔","Sludgemaw":"淤泥巨口","Corporal Brennan":"布伦南下士","Colonel Crash":"克拉什上校","Sal the Engineer":"工程师萨尔","Axemaul":"斧锤","Directive-0":"零号指令","Bramblesong":"荆棘之歌","The Timekeeper":"时间尊者","Primordial Guardian Origo":"原始护卫者·发端","Stone Demon":"石魔","Chiselbella":"美凿","Bio-Bulkhead":"生化壁垒","Bio-Thresher Omega":"生化打谷机欧米伽","The Battle Wagon":"战车","Core Observer":"核心观察者","Voraxis":"沃拉克西斯","Frank the Furnace":"熔炉弗兰克","Hank the Welder":"焊工汉克","Fractis":"弗拉克提斯","The Backhive":"背巢","Subjugator the Invincible":"无敌镇压者","Mimicron":"拟态怪","Ten-Toes":"十趾","Slayowulf":"杀戮狼","Theylob":"瑟洛布","Tiny Bigs":"小大个","King Crosis":"克罗西斯王","Bloomreaper the Invincible":"无敌采花贼","CL34n.R":"清洁机器人","Logistics Manager Reyes":"后勤经理雷耶斯","Captain Willis":"威利斯队长","Blackgrin":"黑色笑靥","Ducky":"小黄鸭","Sidney Pointylegs":"尖腿西德尼","F1x.R":"维修机器人","Bore-Tex":"钻旋风","Test Zero":"零号试验体","Callis, the Ripper Queen":"开颅者女王凯莉丝","Blackspot Vilethorn":"黑斑恶棘","Gutslinger":"抛肠客","Grimebag Gilbert":"污秽者吉尔伯特","Unreal Steel Jayson":"虚幻之钢杰森","Cosmicreep":"宇宙怪客","Drilla Killa":"钻杀者","Ol' Thrash":"老特拉什","Kraggula":"克拉古拉","Fulgur":"富尔格","Krag'thulu":"克拉格苏鲁","Slithertongue":"滑舌","Skullfire":"颅火","Ice Maw":"冰颚","Bitterblight":"苦疫","Thresh O' War":"战争打谷机","Botpopper":"机器人爆破手","Bone Boogie":"骨骼布吉","Oldbeard Worldthroat":"老胡子世界之喉","Skull Orchid":"骷髅兰","Leader Willem":"头目威廉","Splashzone":"溅射区","Thol the Invincible":"无敌索尔","The Penitent Steel":"忏悔之钢","Volcanus":"伏尔坎努斯","Lieutenant Bume":"布姆中尉","Driller Hole":"钻洞者","Moon-Maddened Callis":"月狂凯莉丝","Vile Ted":"卑鄙鬼·泰德","Experiment 42":"42号实验体","Experiment 1709":"1709号实验体","Sturm":"狂飙","Drang":"怒涛","RelaxMech":"悠闲机甲","Minister Screw":"斯克鲁部长","Donk":"唐克","Vile Prototype":"卑鄙原型机","Skyspanner Kratch":"天穹扳手克拉奇","The Immortal Boneface":"不朽骨面","Kolavalin":"科拉瓦林","Big Oil":"大石油","Megan":"梅根","MAXXXSUPREMENOOLIVES":"至尊无橄榄麦克斯","Divisioner":"分割者","Child of Terramorphous":"特拉莫弗斯之子","Big Bada Boom Drone":"大爆炸无人机","Gilgathresh":"吉尔加什","Infamous Dave":"恶名戴夫","Dr. Elena Smith":"埃琳娜·史密斯博士","Saddleback":"鞍背兽","Crackclaw":"裂爪","Genone":"杰诺恩","BETAMAXXX":"贝塔麦克斯","Unreal Steel":"虚幻之钢","Pango":"潘戈","Bango":"班戈","Primordial Guardian Timekeeper":"原始护卫者·时间尊者","Skank Eyes":"臭眼","Gruntabulous Vork":"咕噜沃克","Li'l Grunt":"小咕噜","Baby Grunt":"小咕噜","Hybrid Thresher":"混种打谷机","Air Raider Scremulous":"空袭者斯克雷姆勒斯","Experiment C-23":"C-23号实验体","Jr. Manager Warrant Baggett":"初级经理沃伦特·巴吉特","Shadowpelt":"暗影皮毛","Tidebreaker":"破潮者","Bore-tex":"钻旋风","Sturmdrang":"狂飙怒涛","Logistics Manager":"后勤经理","Jayson and his Frame":"杰森与他的机甲","Biff Fistful":"铁拳比夫","Subjugator & Thol":"镇压者与索尔","The Reject Prototypes":"废弃原型机","Vile Ted & The Experiments":"卑鄙鬼·泰德与实验体","Battle Wagon":"战车","Oppressor":"压迫者","The Divisioner":"分割者","Rippa Roadbirds":"开颅者公路飞鸟","Foundry Freaks":"铸造厂怪人","Meathead Riders":"莽汉骑手","Pango Bango":"潘戈与班戈","Jason and his Frame":"杰森与他的机体","Subjugator  the Invincible":"无敌镇压者","Thol  the Invincible":"无敌索尔","Nightmare Rift Boss":"梦魇裂隙首领","Digi-Rift Boss":"数码裂隙首领","Takedown Loot":"猎杀行动战利品","Geiger-Roid":"盖革类固醇","Ordonite Processor":"奥矿处理器","Ordonite Processors":"奥矿处理器","Ordonite Up!":"奥矿处理器","Research Center B-0451":"研究中心B-0451","Silent Crisis: Time Scope 5":"无声危机：时间镜5","Bones of Sanctuary":"避难所遗骸","Fadefields":"隐没旷野","The Fadefields":"隐没旷野","Carcadia Burn":"卡尔卡迪亚火区","Terminus Range":"终点山脉","Dominion":"主宰之城","Elpis":"厄尔皮斯","Elpis Orbital Shatterfield":"厄尔皮斯轨道破碎区","Ministry of Culture":"文化部","The Demon's Domain":"恶魔领地","The Whispering Glacier":"低语冰川","Providence Island":"天意岛","The Toxic Scowl":"剧毒怒吼","Zane's Arcade":"赞恩的街机厅","Nuada Cove":"努阿达湾","The Bloom":"绽放之地","Lair of the Subjugator":"镇压者巢穴","Assault Rifle":"突击步枪","Class Mod":"职业模组","Shield":"护盾","Grenade":"手雷","Heavy Weapon":"炮械","Pistol":"手枪","Repkit":"修复套件","Shotgun":"霰弹枪","SMG":"冲锋枪","Sniper Rifle":"狙击步枪","Armor":"护甲","Flesh":"肉体","Overshield":"额外护盾","Special health":"特殊生命值","Corrosive":"腐蚀","Shock":"电击","Fire":"燃烧","Incendiary":"燃烧","Cryo":"冰冻","Radiation":"辐射","Kinetic":"动能","Standard":"生命源泉","Acey May ":"艾西·梅","Cooper Duper ":"库珀欺诈者"},"phrases":{"Other region":"其他地区","Raid Boss ":"突袭首领 ","Bounty Pack ":"悬赏包 ","Story Pack ":"剧情包 ","◀ Close list":"◀ 关闭列表","Regional bosses · Big Encore travel":"地区首领 · 盛大安可传送","Checking a safe destination…":"正在检查安全落点……","Waiting for the SDK connection… The list will appear automatically when connected.":"正在等待 SDK 连接……连接成功后将自动显示列表。","Retry now":"立即重试","Travelling to the destination map…":"正在前往目标地图……","At the boss room entrance. Close the map and enter manually.":"已到达首领房间入口，请关闭地图后手动进入。","Arrived at the station. Press Esc to close the map.":"已到达机器旁，按 Esc 关闭地图。","Loading terrain around the boss room entrance…":"正在加载首领房间入口周围的地形……","Loading terrain around the Encore station…":"正在加载盛大安可机器周围的地形……","Cancel travel":"取消传送","Unavailable: ":"当前不可用：","Possible bosses":"可能出现的首领","Dedicated drops":"专属掉落","No dedicated drop data is registered.":"暂无已收录的专属掉落信息。","Travel to the processor?":"是否传送至奥矿处理器？","Record the processor position with F10 first.":"请先站在奥矿处理器前，按 F10 记录位置。","Travel to the front of this boss’s Big Encore station?":"是否传送至此首领的盛大安可机器前？","Map travel and destination loading will be handled automatically.":"将自动完成地图切换和目标区域加载。","Confirm — Travel":"确认传送","Cancel":"取消","No Big Encore bosses are available.":"当前没有可用的盛大安可首领。","▼ More bosses below":"▼ 下方还有更多首领","Select a boss to travel to its map and then its Big Encore station.":"选择首领后，可前往对应地图及其盛大安可机器。","At the boss room entrance. Enter through the portal manually.":"已到达首领房间入口，请手动通过入口进入。","Travel complete.":"传送完成。","Travel cancelled: ":"传送已取消：","Refresh list":"刷新列表","Reopen the map.":"请重新打开地图。","Request expired or travel is blocked.":"请求已过期或当前无法传送。","Travel complete. Press Esc to close the map.":"传送完成，按 Esc 关闭地图。","Reopen the list to check travel progress.":"请重新打开列表查看传送进度。","Reading Encore stations…":"正在读取盛大安可机器……","Dedicated drops shared by the possible activity bosses.":"此活动可能出现的首领共享专属掉落。","Travel to the final Unknown boss-room entrance. Use the entrance manually after arrival.":"将传送至最终首领房间入口，到达后请手动使用入口。","Object unavailable":"对象不可用","Object expired":"对象已失效","Engine IsValid rejected object":"引擎检查判定对象无效","Default object is not a live target":"默认对象不能作为实时目标","Actor is being destroyed":"对象正在销毁","World not available":"当前世界不可用","Controller world changed":"玩家控制器所在世界已改变","Host / single-player only":"仅限房主或单人游戏","World or player changed; reopen map":"世界或角色已改变，请重新打开地图","Exit your vehicle first":"请先离开载具","Dead / respawning / fight for your life":"角色已死亡、正在重生或处于殊死一搏状态","Zone transition in progress":"正在切换区域","Travel is currently blocked":"当前无法传送","Seamless loading in progress":"正在无缝加载","Cinematic in progress":"正在播放过场动画","Player must be standing on the ground":"角色必须站在地面上","Encore discovery limit exceeded":"盛大安可机器扫描数量超出限制","Kismet system library unavailable":"引擎系统库不可用","No safe walkable position in front of station":"机器前没有安全可行走的落点","Map session expired or another teleport in progress":"地图会话已过期或另一次传送正在进行","Station not present in this map session":"此地图会话中不存在目标机器","Player region changed; reopen map":"角色所在区域已改变，请重新打开地图","Encore station unloaded":"盛大安可机器尚未加载","Encore station identity changed":"盛大安可机器标识已改变","Map closed during confirmation":"确认时地图已关闭","Engine safe teleport rejected destination":"引擎安全传送检查拒绝了目标落点","Invalid approved entrance destination":"已批准的入口目标无效","Recorded processor destination unavailable":"已记录的奥矿处理器位置不可用","Exact entrance destination not found in this world":"当前世界中找不到匹配的入口目标","Ambiguous loaded Encore station":"存在多个匹配的盛大安可机器，无法确定目标","Exact Encore destination not found in this world":"当前世界中找不到匹配的盛大安可目标","Another journey is running or map session expired":"另一次行程正在进行或地图会话已过期","Exact machine metadata unavailable":"目标机器的精确数据不可用","No native entry route for exact destination map":"目标地图没有可用的原生快速旅行入口","Travel cancelled by player":"玩家取消了传送","Destination loading timed out; native travel may be locked or unavailable":"目标加载超时，原生快速旅行可能尚未解锁或不可用","Local player identity changed during travel":"传送期间本地角色标识已改变","Unexpected destination world during travel":"传送到达了非预期的世界","Controller changed during local travel":"本地传送期间玩家控制器已改变","Safe teleport failed":"安全传送失败","First select a processor for recording in the Big Encore list.":"请先在盛大安可列表中选择要记录位置的奥矿处理器。","Cannot record a position during travel.":"传送期间无法记录位置。","Mod disabled":"Mod 已禁用","Unknown":"未知原因","closed":"地图已关闭","scanning":"正在扫描","disabled":"已禁用","failed":"操作失败"},"fragments":{": unavailable native function":"：原生函数不可用",": unsupported signature ":"：函数签名不受支持 ",": unexpected struct ":"：非预期的结构体 ",": unexpected Boolean return ABI":"：布尔返回值接口不符合预期","Unexpected trace output ABI: ":"碰撞检测返回值接口不符合预期：","Travel status is not known idle: ":"传送状态未确认为空闲：","Enter destination map first: ":"请先进入目标地图：","Enter the selected processor map before recording: ":"记录位置前请先进入所选奥矿处理器地图：","Current region does not match the selected recording target: ":"当前地区与所选记录目标不符："," processor position saved (F10).":"的奥矿处理器位置已保存（F10）。","Position recording failed: ":"位置记录失败："," selected. Close the map, stand at the processor and press F10.":"已选中。请关闭地图，站到奥矿处理器前并按 F10。"}};
 const tr=value=>{
  if(typeof value!=='string')return value;
  if(Object.prototype.hasOwnProperty.call(locale.phrases,value))return locale.phrases[value];
  if(Object.prototype.hasOwnProperty.call(locale.labels,value))return locale.labels[value];
  let result=value;
  for(const source of Object.keys(locale.fragments).sort((a,b)=>b.length-a.length))result=result.split(source).join(locale.fragments[source]);
  for(const source of Object.keys(locale.labels).sort((a,b)=>b.length-a.length))result=result.split(source).join(locale.labels[source]);
  return result;
 };
 const display=(row,key='name')=>row?.['cn_'+key]||tr(row?.[key]||'');
    const states = new WeakMap();
    const liveWidgets = new Set();
    const patches = [];
    const installed = new WeakSet();
    let alive = true;
    let observer = null;
    let scanTimer = null;

    let traces = 0;
    function trace(kind, data) {
        if (kind !== 'map_poi' && traces++ >= 80) return;
        try {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', endpoint + '/trace', true);
            xhr.setRequestHeader('Content-Type', 'text/plain');
            xhr.send(JSON.stringify({kind:kind, data:data}));
        } catch (_) {}
    }
    function normalize(text) {
        return String(text || '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim().toLowerCase();
    }
    function mapBoss(bosses, location) {
        const takedownIcon = "texture2d'/game/dlc/tuba/uiresources/hud_takedown_celeb_notif/assets/ui_art_celeb_takedown_icon.ui_art_celeb_takedown_icon'";
        if (String(location.typeiconpath || '').toLowerCase() === takedownIcon) return bosses.activity_takedown ? 'activity_takedown' : null;
        const labels = [normalize(location.title), normalize(location.poatype_title)];
        const activities = ['activity_champion', 'activity_nightmare', 'activity_digi'];
        for (const id of activities) {
            if (bosses[id] && (bosses[id].map_names || []).concat(bosses[id].cn_map_names || []).some(n => labels.indexOf(normalize(n)) !== -1)) return id;
        }
        const icon = String(location.typeiconpath || '').toLowerCase();
        const processor = "texture2d'/game/dlc/cello/uiresources/discovery_icons/ico_world_event_pearl_gen.ico_world_event_pearl_gen'";
        if (icon === processor) return bosses.activity_processor ? 'activity_processor' : null;
        const texture = "texture2d'/game/uiresources/_shared/assets/ico_ui_art_discovery/ico_boss_replay.ico_boss_replay'";
        const raid = "texture2d'/game/dlc/common/uiresources/_shared_dlc_icons/ico_mission_tracker_raid.ico_mission_tracker_raid'";
        const weekly = "texture2d'/game/uiresources/_shared/assets/ico_ui_art_discovery/ico_weekly_true_boss_replay.ico_weekly_true_boss_replay'";
        if (icon !== weekly && icon !== texture && icon !== raid && !/(^|\/)ico_boss_replay\.png$/.test(icon)) return null;
        const found = Object.keys(bosses).filter(id =>
            (bosses[id].map_names || []).concat(bosses[id].cn_map_names || []).some(n => labels.indexOf(normalize(n)) !== -1));
        return found.length === 1 ? found[0] : null;
    }
    function worldBoss(bosses, data) {
        // Only explicit identifiers or exact boss-bearing UI fields can match.
        // A generic "Buy Encore" prompt must never identify a boss.
        const keys = ['boss_id','bossname','bossdisplayname','station_id','locationdisplaydata'];
        if (/encore|앙코르|盛大安可|大返场/i.test(String(data.loc_prompttext || ''))) keys.push('title','name');
        const values = keys.filter(k => typeof data[k] === 'string').map(k => normalize(data[k]));
        const found = Object.keys(bosses).filter(id => {
            const row = bosses[id];
            return (row.world_keys || []).concat(row.station_ids || [], row.map_names || [], row.cn_map_names || []).some(n => values.indexOf(normalize(n)) !== -1);
        });
        return found.length === 1 ? found[0] : null;
    }
    function label(row, world) {
        const names = Array.from(new Set(row.drops.map(d => display(d))));
        return (world ? display(row) + '\n' : '') + names.map(n => '• ' + n).join('\n');
    }
    function state(widget) {
        if (!states.has(widget)) states.set(widget, {epoch:0, signature:null, node:null});
        liveWidgets.add(widget);
        return states.get(widget);
    }
    function clear(widget) {
        const s = state(widget); ++s.epoch; s.signature = null;
        if (s.node && s.node.parentNode) s.node.parentNode.removeChild(s.node);
        s.node = null;
    }
    function update(widget, world) {
        if (!alive) return;
        const d = widget.DataModel || {};
        const data = world ? d : (d.hoveredlocation || {});
        if (widget.IsActivated === false || (!world && !d.bhoveringpoi)) return clear(widget);
        const s = state(widget);
        const signature = JSON.stringify([world, data]);
        if (s.signature === signature) return;
        clear(widget); s.signature = signature;
        const epoch = s.epoch;
        const snapshot = JSON.stringify(data);
        trace(world ? 'world_prompt' : 'map_poi', snapshot.length <= 16000 ? JSON.parse(snapshot) :
            {keys:Object.keys(data), preview:snapshot.slice(0,12000)});
        const xhr = new XMLHttpRequest();
        xhr.open('GET', endpoint + '/catalog', true);
        xhr.timeout = 2000;
        xhr.onload = function () {
            if (!alive || s.epoch !== epoch || xhr.status !== 200 || !widget.parentNode) return;
            try {
                const config = JSON.parse(xhr.responseText);
                if (!config.enabled) return;
                const id = world ? worldBoss(config.bosses, data) : mapBoss(config.bosses, data);
                if (!id) return;
                const anchor = widget.querySelector(world ? '.user_prompt_content' : '.bm_poi_hover_info_description');
                if (!anchor || !anchor.parentNode) return;
                const node = document.createElement('div');
                node.className = world ? 'bedi_drops small_text_2' : 'bedi_drops tooltip_content_body_text small_text_2';
                node.style.display = 'block'; node.style.pointerEvents = 'none';
                node.style.marginTop = '0.6em'; node.style.marginBottom = '0.6em';
                if (world || id === 'activity_processor') {
                    const heading = document.createElement('p');
                    heading.style.display = 'block';
                    heading.textContent = display(config.bosses[id]);
                    node.appendChild(heading);
                }
                if (id === 'activity_processor' && config.bosses[id].boss_names) {
                    const names=document.createElement('p');names.style.display='block';
                    names.textContent=(config.bosses[id].cn_boss_names || config.bosses[id].boss_names.map(tr)).join(' / ');node.appendChild(names);
                }
                if (config.bosses[id].note && config.bosses[id].note_before) {
                    const condition = document.createElement('p'); condition.style.display = 'block';
                    condition.textContent = display(config.bosses[id],'note'); node.appendChild(condition);
                }
                config.bosses[id].drops.forEach(drop => {
                    const line = document.createElement('p');
                    line.style.display = 'flex';
                    line.style.flexDirection = 'row';
                    line.style.alignItems = 'center';
                    line.style.flexWrap = 'nowrap';
                    line.style.marginTop = '0'; line.style.marginBottom = '0';
                    line.title = display(drop,'kind_label');
                    const name = document.createElement('span');
                    name.style.display = 'block';
                    name.style.minWidth = '0';
                    name.style.flex = '1 1 auto';
                    name.textContent = display(drop);
                    if (drop.rarity === 'pearl') {
                        name.className = 'rarity pearl bright';
                        name.style.color = '#97ffd2';
                    }
                    const allowed = ['pistol','assault','smg','shotgun','sniper','ordnance',
                                     'energy_shields','grenade','classmod','repkit','enhancement'];
                    if (allowed.indexOf(drop.kind) !== -1) {
                        const icon = document.createElement('img');
                        icon.src = 'coui://uiresources/_shared/assets/ico_ui_art_distance_icons/ico_ui_art_dist_' + drop.kind + '.png';
                        icon.alt = '';
                        icon.style.width = '1.656em'; icon.style.height = '1.656em';
                        icon.style.flex = '0 0 auto';
                        icon.style.flexShrink = '0'; icon.style.flexGrow = '0';
                        icon.style.minWidth = '1.656em'; icon.style.maxWidth = '1.656em';
                        icon.style.minHeight = '1.656em'; icon.style.maxHeight = '1.656em';
                        icon.style.objectFit = 'contain';
                        icon.style.fontSize = 'inherit';
                        icon.style.display = 'inline-block'; icon.style.verticalAlign = 'middle';
                        icon.style.marginRight = '0.35em';
                        const fallback = document.createElement('span');
                        fallback.style.display = 'none';
                        icon.onerror = function () {
                            icon.style.display = 'none';
                            fallback.textContent = '[' + display(drop,'kind_label') + '] ';
                            fallback.style.display = 'inline';
                        };
                        line.appendChild(icon); line.appendChild(fallback);
                    }
                    line.appendChild(name);
                    node.appendChild(line);
                });
                if (config.bosses[id].note && !config.bosses[id].note_before) {
                    const note = document.createElement('p'); note.style.display = 'block';
                    note.textContent = display(config.bosses[id],'note'); node.appendChild(note);
                }
                anchor.parentNode.insertBefore(node, anchor.nextSibling);
                s.node = node;
                trace('displayed', {surface:world ? 'world':'map', boss:id, drops:config.bosses[id].drops.length});
            } catch (e) { trace('render_error', String(e)); }
        };
        xhr.send();
    }
    function wrap(cls, name, callback) {
        const original = cls.prototype[name];
        if (typeof original !== 'function') return;
        const own = Object.getOwnPropertyDescriptor(cls.prototype, name);
        const wrapped = function (...args) {
            const result = original.apply(this, args);
            if (alive) try { callback(this); } catch (e) { clear(this); trace('callback_error', String(e)); }
            return result;
        };
        cls.prototype[name] = wrapped;
        patches.push({prototype:cls.prototype, name, original, own, wrapped});
    }
    function install(cls) {
        if (!cls || installed.has(cls) || typeof cls.prototype.Event_DataUpdated !== 'function') return;
        installed.add(cls);
        wrap(cls, 'Event_DataUpdated', w => update(w, false));
        wrap(cls, 'Event_Activate', w => { clear(w); update(w, false); });
        for (const name of ['Event_Deactivate','BeginDeactivate','disconnectedCallback']) wrap(cls, name, clear);
        trace('receiver_ready', {surface:'map', version:'0.6.0-preview.18-zh-uilink'});
    }
    function scan() {
        if (!alive) return;
        // Constructors can finish loading after UILink. Retry without retaining widgets in the DOM.
        if (typeof Widget_BigMap !== 'undefined') install(Widget_BigMap);
        for (const widget of document.querySelectorAll('widget-bigmap')) {
            install(widget.constructor);
            update(widget, false);
        }
        for (const widget of liveWidgets) if (!widget.isConnected) {clear(widget);liveWidgets.delete(widget);}
    }
    function teardown() {
        if (!alive) return;alive=false;
        if(observer)observer.disconnect();
        if(scanTimer)window.clearInterval(scanTimer);
        for(const widget of liveWidgets)clear(widget);
        liveWidgets.clear();
        for(const patch of patches.reverse()) {
            if(patch.prototype[patch.name]!==patch.wrapped)continue;
            if(patch.own)Object.defineProperty(patch.prototype,patch.name,patch.own);
            else delete patch.prototype[patch.name];
        }
        if(window.BigEncoreDropInfoUI===api)delete window.BigEncoreDropInfoUI;
    }
    const api={mapBoss,worldBoss,label,teardown};
    window.BigEncoreDropInfoUI=api;
    scan();
    // A small map-only scan handles late custom-element upgrades and hovered-POI changes.
    scanTimer=window.setInterval(scan,500);
    if(typeof MutationObserver!=='undefined'){
        observer=new MutationObserver(()=>scan());
        observer.observe(document.documentElement,{childList:true,subtree:true});
    }
})();
