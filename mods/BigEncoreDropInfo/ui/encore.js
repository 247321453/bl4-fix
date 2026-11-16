/* Additive panel, plain JSON bridge only. No native map input/prototype replacement. */
(function(global){
 'use strict';
 const KEY='__BigEncoreTravel_v1'; if(global[KEY])return;

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

 const text=(_ko,en)=>tr(en);
 const regionLabel=name=>tr(name);
 const groupOrder=['grasslands','shatteredlands','mountains','city','elpis',
  'banjo','cello','mandolin','harp','viola','cowbell','harmonica','raid1','raid2'];
 const packs={banjo:1,cello:2,mandolin:3,harp:4,viola:5};
 const stories={cowbell:1,harmonica:2};
 const finalBosses=new Set(['grasslands_commander','shatterlandscommanderfortress','mountaincommander',
  'timekeeper_tkboss','shatterlandscommanderelpis','ministerscrew','ordonite_pangolin',
  'murderer','betamaxxx','viledave','dahlfather','main_villianess','bloomreaper','encore_dlc_raid2']);
 const guardians=new Set(['grasslands_guardian','shatterlandsguardian','mountainguardian']);
 const bossOrder=id=>finalBosses.has(id)?2:guardians.has(id)?1:0;
 function groupLabel(row,key){
  const base=display(row,'region_name')||tr('Other region');
  if(key==='raid1'||key==='raid2')return base+' ('+tr('Raid Boss ')+(key==='raid1'?'1':'2')+')';
  if(packs[key])return base+' ('+tr('Bounty Pack ')+packs[key]+')';
  if(stories[key])return base+' ('+tr('Story Pack ')+stories[key]+')';
  return base;
 }
 const endpoint='http://127.0.0.1:19386/big-encore-20261019-v1/encore';
 const states=new WeakMap();
 const liveWidgets=new Set();
 let alive=true;
 function request(data,done){
  if(!alive)return;
  const deliver=value=>{if(alive)done(value);};
  try{
   const x=new XMLHttpRequest();x.open(data?'POST':'GET',endpoint,true);x.timeout=data?2200:30000;
   if(data)x.setRequestHeader('Content-Type','text/plain');
   x.onload=()=>{try{deliver(x.status===200?JSON.parse(x.responseText):null);}catch(_){deliver(null);}};
   x.onerror=x.ontimeout=()=>deliver(null);x.send(data?JSON.stringify(data):null);
  }catch(_){deliver(null);}
 }
 function close(w){
  const s=states.get(w);if(!s)return;
  ++s.epoch;s.closed=true;
  if(s.timer)global.clearTimeout(s.timer);
  if(s.panel?.parentNode)s.panel.parentNode.removeChild(s.panel);
  s.panel=null;
  if(s.launcher?.parentNode)s.launcher.parentNode.removeChild(s.launcher);
  s.launcher=null;
  if(s.blocked&&typeof w.Event_BlockMapHover==='function')w.Event_BlockMapHover(false);
  s.blocked=false;
 }
 function hide(w){
  const s=states.get(w);if(!s)return;
  ++s.epoch;s.closed=true;if(s.timer)global.clearTimeout(s.timer);
  if(s.panel?.parentNode)s.panel.parentNode.removeChild(s.panel);s.panel=null;
  if(s.blocked&&typeof w.Event_BlockMapHover==='function')w.Event_BlockMapHover(false);
  s.blocked=false;
 }
 function valid(w,s,epoch){return alive&&!s.closed&&s.epoch===epoch&&w.IsActivated&&w.parentNode;}
 function button(label,action){
  const b=document.createElement('button');b.type='button';b.textContent=label;
  b.style.cssText='font-family:"Microsoft YaHei","Noto Sans SC","Industry-Normal",sans-serif;font-size:22px;min-height:48px;text-align:left;color:#82d9ff;background:rgba(8,25,38,.92);border:1px solid #284d5e;padding:8px;flex-shrink:0;';
  b.addEventListener('click',e=>{e.stopPropagation();action();});return b;
 }
 function message(node,value){const p=document.createElement('p');p.textContent=value;p.style.cssText='margin:6px 0;font-family:"Microsoft YaHei","Noto Sans SC","Industry-Normal",sans-serif;font-size:'+(global.innerHeight<900?18:22)+'px;white-space:normal;padding:6px 10px;flex-shrink:0;';node.appendChild(p);}
 function load(w,s,tries=0){
  const epoch=s.epoch;
  request(null,data=>{
   if(!valid(w,s,epoch))return;
   if(!data||data.status==='scanning'||data.status==='closed'){
    s.data=null;s.busy=false;s.connecting=true;s.connectionAttempts=tries+1;render(w,s);
    const delay=data?.status==='scanning'?500:Math.min(5000,1000+tries*500);
    s.timer=global.setTimeout(()=>{if(valid(w,s,epoch))load(w,s,tries+1);},delay);return;
   }
   s.connecting=false;s.data=data;s.busy=false;render(w,s);
  });
 }
 function render(w,s){
  const p=s.panel;if(!p)return;
  while(p.firstChild)p.removeChild(p.firstChild);
  const panelHeight=global.innerHeight>0?Math.max(360,Math.floor(global.innerHeight*.72))+'px':'72vh';
  p.style.width='82%';p.style.height=panelHeight;p.style.maxHeight=panelHeight;p.style.minHeight='360px';
  p.appendChild(button(tr('◀ Close list'),()=>hide(w)));
  message(p,tr('Regional bosses · Big Encore travel'));
  if(s.busy){message(p,tr('Checking a safe destination…'));return;}
  const d=s.data;
  if(!d){
   message(p,tr('Waiting for the SDK connection… The list will appear automatically when connected.'));
   p.appendChild(button(tr('Retry now'),()=>{
    if(s.timer)global.clearTimeout(s.timer);++s.epoch;load(w,s);
   }));return;
  }
  if(d.journey){
   const entrance=d.journey.destination_kind==='boss_room_entrance';
   const waypoint=d.journey.destination_kind==='native_waypoint';
   const stage=d.journey.stage==='map_loading'?tr('Travelling to the destination map…'):
    d.journey.stage==='arrival'?(entrance?tr('At the boss room entrance. Close the map and enter manually.'):tr('Arrived at the station. Press Esc to close the map.')):
    (entrance?tr('Loading terrain around the boss room entrance…'):tr('Loading terrain around the Encore station…'));
   message(p,waypoint?(d.journey.stage==='arrival'?'已到达快速旅行站。':'正在使用游戏快速旅行……'):stage);
   if(d.journey.stage!=='arrival')p.appendChild(button(tr('Cancel travel'),()=>{
    request({action:'cancel',map_session:d.map_session,journey_id:d.journey.id},()=>load(w,s));
   }));
   s.timer=global.setTimeout(()=>load(w,s),500);return;
  }
  if(d.status!=='ready'){
   message(p,tr('Unavailable: ')+(display(d,'reason')||tr(d.status)));
  }else if(s.selected){
   const row=(d.bosses||[]).concat(d.waypoints||[],d.processors||[]).find(b=>b.id===s.selected);
   if(!row){s.selected=null;return render(w,s);}
   const processor=row.kind==='saved_processor';
   const summary=document.createElement('div');summary.id='BigEncoreTravel_Confirmation_v1';
   summary.style.cssText='display:flex;flex-direction:row;align-items:flex-start;flex-shrink:0;padding:10px;';
   const boss=document.createElement('div');boss.style.cssText='width:30%;min-width:220px;flex-shrink:0;';
   const bossName=document.createElement('div');bossName.id='BigEncoreTravel_BossName_v1';bossName.textContent=display(row);
   bossName.style.cssText='font-family:"Microsoft YaHei","Noto Sans SC","Industry-Normal",sans-serif;font-size:32px;line-height:1.25;white-space:normal;padding:8px 10px 14px;';boss.appendChild(bossName);
   if(processor){
    const names=document.createElement('div');names.style.cssText='font-family:"Microsoft YaHei","Noto Sans SC","Industry-Normal",sans-serif;font-size:20px;line-height:1.3;padding:0 10px;white-space:pre-line;';
    names.textContent=tr('Possible bosses')+'\n'+(row.cn_boss_names||row.boss_names?.map(tr)||[]).join('\n');boss.appendChild(names);
   }else if(row.kind!=='native_waypoint'){
   const health=row.health||{};
   message(boss,'基础生命值构成：'+((health.cn_labels||health.labels?.map(tr)||[]).join(' / ')||'未知'));
   if(health.variant_dependent)message(boss,'不同首领形态的生命值构成可能不同。');
   const recommendations=health.recommendations||[];
   message(boss,'推荐属性（基础克制关系）：'+(recommendations.length?recommendations.map(r=>display(r,'element')+'（'+display(r,'health_label')+'）').join(' / '):'未知'));
   }
   summary.appendChild(boss);
   if(row.kind!=='native_waypoint'||row.drops?.length){
   const drops=document.createElement('div');drops.id='BigEncoreTravel_Drops_v1';
   drops.style.cssText='width:66%;margin-left:2%;flex-shrink:0;';
   message(drops,tr('Dedicated drops'));
   const names=new Set(),entries=[];
   for(const drop of (row.drops||[]).slice().sort((a,b)=>(a.rarity==='pearl'?0:1)-(b.rarity==='pearl'?0:1))){
    if(!drop.name||names.has(drop.name))continue;names.add(drop.name);entries.push(drop);
   }
   const grid=document.createElement('div');grid.style.cssText='display:flex;flex-direction:row;align-items:flex-start;width:100%;';drops.appendChild(grid);
   const columnCount=entries.length>8?3:entries.length>3?2:1;
   const perColumn=Math.max(1,Math.ceil(entries.length/columnCount)),columns=[];
   for(let i=0;i<columnCount;i++){
    const column=document.createElement('div');column.className='BigEncoreTravel_DropColumn';
    column.style.cssText='display:flex;flex-direction:column;min-width:0;flex-shrink:0;box-sizing:border-box;';
    column.style.width=(100/columnCount)+'%';grid.appendChild(column);columns.push(column);
   }
   entries.forEach((drop,index)=>{
    const item=document.createElement('div');item.className='BigEncoreTravel_Drop';
    item.style.cssText='display:flex;flex-direction:row;align-items:center;font-family:"Microsoft YaHei","Noto Sans SC","Industry-Normal",sans-serif;font-size:22px;white-space:normal;padding:4px 10px;color:'+
     (drop.rarity==='pearl'?'#97ffd2':'#d1dadd')+';';
    if(row.kind==='native_waypoint')item.style.cssText+='font-size:20px;padding:3px 10px;';
    const allowed=['pistol','assault','smg','shotgun','sniper','ordnance','energy_shields','grenade','classmod','repkit','enhancement'];
    if(allowed.includes(drop.kind)){
     const icon=document.createElement('img');icon.src='coui://uiresources/_shared/assets/ico_ui_art_distance_icons/ico_ui_art_dist_'+drop.kind+'.png';icon.alt='';
     icon.style.cssText='width:1.656em;height:1.656em;min-width:1.656em;max-width:1.656em;min-height:1.656em;max-height:1.656em;flex:0 0 auto;object-fit:contain;margin-right:0.35em;';
     const fallback=document.createElement('span');fallback.style.display='none';
     icon.onerror=()=>{icon.style.display='none';fallback.textContent='['+(display(drop,'kind_label')||'装备')+'] ';fallback.style.display='inline';};
     item.appendChild(icon);item.appendChild(fallback);
    }
    const name=document.createElement('span');name.textContent=display(drop);name.style.cssText='min-width:0;flex:1 1 auto;';item.appendChild(name);
    item.title=display(drop,'kind_label');columns[Math.floor(index/perColumn)].appendChild(item);
   });
   if(!names.size)message(drops,tr('No dedicated drop data is registered.'));
   summary.appendChild(drops);
   }
   p.appendChild(summary);
   if(processor){
    message(p,display(row,'note')+' '+(row.recorded?tr('Travel to the processor?'):tr('Record the processor position with F10 first.')));
   }else message(p,row.kind==='native_waypoint'?'是否传送至此快速旅行站？':display(row,'destination_note')||tr('Travel to the front of this boss’s Big Encore station?'));
   if(row.kind==='native_waypoint'&&!row.drops?.length)message(p,'使用游戏原生快速旅行功能，仍需满足解锁条件。');
   else if(!processor&&row.cross_map)message(p,tr('Map travel and destination loading will be handled automatically.'));
   const actions=document.createElement('div');
   actions.style.cssText='display:flex;flex-direction:row;flex-shrink:0;';
   actions.className='BigEncoreTravel_Actions';p.appendChild(actions);
   if(!processor||row.recorded)actions.appendChild(button(tr('Confirm — Travel'),()=>travel(w,s,row.id)));
   actions.appendChild(button(tr('Cancel'),()=>{s.selected=null;render(w,s);}));
   for(const control of actions.children)control.style.flex='1 1 0';
  }else{
   const list=document.createElement('div');list.id='BigEncoreTravel_List_v1';list.style.cssText='display:flex;flex-direction:row;flex-wrap:wrap;align-content:flex-start;align-items:flex-start;overflow-y:auto;overflow-x:hidden;min-height:120px;flex:1 1 auto;';
   const initialHeight=Math.max(120,Math.floor((global.innerHeight||1080)*.65)-360);
   list.style.height=initialHeight+'px';list.style.flex='0 0 '+initialHeight+'px';
   const groups=new Map();
   for(const row of d.bosses||[]){const key=row.region_key||row.region_name||'Big Encore';if(!groups.has(key))groups.set(key,[]);groups.get(key).push(row);}
   const rank=k=>groupOrder.includes(k)?groupOrder.indexOf(k):100;
   const columns=new Map();
   for(const [key,rows] of Array.from(groups).sort((a,b)=>rank(a[0])-rank(b[0]))){
    const column=document.createElement('div');column.className='BigEncoreTravel_Group';column.style.cssText='display:flex;flex-direction:column;width:24%;min-width:210px;flex-shrink:0;margin-right:1%;padding-bottom:20px;box-sizing:border-box;';
    column.id='BigEncoreTravel_Group_'+key;
    const first=rows[0];message(column,groupLabel(first,key));
    for(const row of rows.slice().sort((a,b)=>bossOrder(a.id)-bossOrder(b.id))){
     const b=button(display(row),()=>{s.selected=row.id;render(w,s);});
     b.id='BigEncoreTravel_Boss_'+row.id;
     column.appendChild(b);
    }
    const points=(d.waypoints||[]).filter(row=>row.region_key===key);
    if(points.length){
     const shortcuts=document.createElement('div');shortcuts.className='BigEncoreTravel_Waypoints';
     shortcuts.style.cssText='padding-top:48px;display:flex;flex-direction:column;';
     for(const row of points){
      const b=button(display(row),()=>{s.selected=row.id;render(w,s);});b.id='BigEncoreTravel_Waypoint_'+row.id;shortcuts.appendChild(b);
     }
     column.appendChild(shortcuts);
    }
    const processors=key==='city'?(d.processors||[]).filter(row=>row.id!=='processor_cello'):[];
    if(processors.length){
     const area=document.createElement('div');area.className='BigEncoreTravel_Processors';area.style.cssText='padding-top:80px;display:flex;flex-direction:column;';
     message(area,'奥矿处理器');
     for(const row of processors){
      area.appendChild(button(display(row).replace(' · 奥矿处理器','')+(row.recorded?'':'（按 F10 记录）'),()=>{s.selected=row.id;render(w,s);}));
     }
     column.appendChild(area);
    }
    columns.set(key,column);
    const raidParent=columns.get(key==='raid1'?'elpis':key==='raid2'?'banjo':'');
    if(raidParent){
     column.className+=' BigEncoreTravel_Raid';
     column.style.width='100%';column.style.minWidth='0';column.style.marginRight='0';
     column.style.paddingTop='24px';
     raidParent.appendChild(column);
    }else list.appendChild(column);
   }
   if(!d.bosses?.length)message(list,tr('No Big Encore bosses are available.'));
   p.appendChild(list);
   const more=document.createElement('div');more.id='BigEncoreTravel_More_v1';
   more.style.cssText='height:28px;min-height:28px;flex-shrink:0;color:#78d7ff;font-family:"Microsoft YaHei","Noto Sans SC","Industry-Normal",sans-serif;font-size:22px;text-align:center;';
   const updateMore=()=>{more.textContent=list.scrollHeight-list.scrollTop-list.clientHeight>4?tr('▼ More bosses below'):'';};
   list.addEventListener('scroll',updateMore);list.updateEncoreMore=updateMore;p.appendChild(more);
   message(p,tr('Select a boss to travel to its map and then its Big Encore station.'));
  }
  if(!s.selected||!s.selected.startsWith('processor_')){
  if(d.processor_notice)message(p,display(d,'processor_notice'));
  if(s.notice)message(p,s.notice);
  else if(d.result)message(p,d.result['Teleport Success']?(d.result['Destination Kind']==='boss_room_entrance'?tr('At the boss room entrance. Enter through the portal manually.'):tr('Travel complete.')):
    tr('Travel cancelled: ')+(d.result.cn_failure_reason||tr(d.result['Teleport Failed Reason']||'Unknown')));
  }
  p.appendChild(button(tr('Refresh list'),()=>{
   if(s.busy)return;
   const epoch=s.epoch;s.busy=true;render(w,s);
   request({action:'refresh',map_session:d.map_session},r=>{
    if(!valid(w,s,epoch))return;
    if(!r?.queued){s.busy=false;s.notice=tr('Reopen the map.');render(w,s);return;}
    s.timer=global.setTimeout(()=>load(w,s),300);
   });
  }));
  if(typeof p.getBoundingClientRect==='function'){
   ++s.layoutReports;const epoch=s.epoch;
   global.setTimeout(()=>{
    if(!valid(w,s,epoch))return;
    try{
     const bounds=n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
     const nav=p.querySelector('#BigEncoreTravel_List_v1'),xhr=new XMLHttpRequest();
     if(nav){
      const reference=nav.querySelector('.BigEncoreTravel_Group button');
      const rowHeight=reference?reference.getBoundingClientRect().height:0;
      if(rowHeight>0&&rowHeight<128)for(const shortcuts of Array.from(nav.querySelectorAll('.BigEncoreTravel_Waypoints')))shortcuts.style.paddingTop=rowHeight+'px';
      if(rowHeight>0&&rowHeight<128){
       const top=reference.getBoundingClientRect().top;
       for(const section of Array.from(nav.querySelectorAll('.BigEncoreTravel_Processors,.BigEncoreTravel_Raid'))){
        const first=section.querySelector('button');if(!first)continue;
        const beside=section.className.includes('BigEncoreTravel_Raid')?nav.querySelector('#BigEncoreTravel_Group_cello > button'):null;
        const origin=beside?beside.getBoundingClientRect().top:top;
        const offset=first.getBoundingClientRect().top-origin;
        const adjustment=Math.round(offset/rowHeight)*rowHeight-offset;
        const padding=parseFloat(section.style.paddingTop)||0;
        section.style.paddingTop=Math.max(0,padding+adjustment)+'px';
       }
      }
      const height=p.getBoundingClientRect().height;
      let controls=24;for(const child of Array.from(p.children))if(child!==nav)controls+=child.getBoundingClientRect().height+8;
      const listHeight=Math.max(120,height-controls);
      nav.style.height=listHeight+'px';nav.style.flex='0 0 '+listHeight+'px';
      if(nav.updateEncoreMore)nav.updateEncoreMore();
     }
     if(s.layoutReports>12)return;
     xhr.open('POST',endpoint.replace(/\/encore$/,'/trace'),true);xhr.setRequestHeader('Content-Type','text/plain');
     xhr.send(JSON.stringify({kind:'encore_layout',data:{panel:bounds(p),list:nav?bounds(nav):null,
      boss_count:s.data?.bosses?.length||0,selected:s.selected||null}}));
    }catch(_){}
   },100);
  }
 }
 function travel(w,s,id){
  if(s.busy||s.data?.status!=='ready')return;
  const token=s.data.map_session,epoch=s.epoch,sequence=++s.sequence;
  s.busy=true;render(w,s);
  request({action:'teleport',boss_id:id,map_session:token,sequence,confirmed:true},r=>{
   if(!valid(w,s,epoch))return;
   if(!r?.queued){s.busy=false;s.notice=tr('Request expired or travel is blocked.');render(w,s);return;}
   function poll(attempt){
    request(null,d=>{
     if(!valid(w,s,epoch))return;
     if(d?.map_session!==token){close(w);return;}
     if(d?.result?.['Selected Boss']===id&&d.result['Request Sequence']===sequence){
      s.data=d;s.busy=false;s.selected=null;
      s.notice=d.result['Teleport Success']?(d.result['Destination Kind']==='boss_room_entrance'?tr('At the boss room entrance. Close the map and enter manually.'):tr('Travel complete. Press Esc to close the map.')):
       tr('Travel cancelled: ')+(d.result.cn_failure_reason||tr(d.result['Teleport Failed Reason']||'Unknown'));render(w,s);return;
     }
     if(d?.journey){s.data=d;s.busy=false;s.selected=null;render(w,s);return;}
     if(attempt>=50){s.busy=false;s.notice=tr('Reopen the list to check travel progress.');render(w,s);return;}
     s.timer=global.setTimeout(()=>poll(attempt+1),200);
    });
   }
   s.timer=global.setTimeout(()=>poll(0),200);
  });
 }
 function open(w,collapsed=false){
  if(!alive||!w?.IsActivated||!w.parentNode)return;
  close(w);
  let s=states.get(w);
  if(!s){
   s={epoch:0,sequence:0};states.set(w,s);
   if(global.engine&&typeof w.MakeEventName==='function'){
    s.deactivate=engine.on(w.MakeEventName('Deactivate'),()=>close(w));
   }
  }
  ++s.epoch;s.closed=false;s.selected=null;s.notice=null;s.busy=false;s.data=null;s.collapsed=false;s.layoutReports=0;
  const launcher=button('盛大安可',()=>open(w));s.launcher=launcher;launcher.id='BigEncoreTravel_Open_v1';
  launcher.className='bm_mouseblocking small_text_2';
  launcher.style.cssText+='position:absolute;left:2%;top:18%;z-index:26;pointer-events:auto;';w.appendChild(launcher);
  if(collapsed){s.collapsed=true;return;}
  const p=document.createElement('div');s.panel=p;p.id='BigEncoreTravel_Panel_v1';
  p.className='bm_mouseblocking small_text_2';
  p.style.cssText='position:absolute;left:2%;top:22%;width:82%;height:72%;min-height:360px;max-height:72%;overflow-y:auto;overflow-x:hidden;display:flex;flex-direction:column;color:#d1dadd;background:rgba(8,25,38,.98);border:1px solid #68b5cd;font-family:"Microsoft YaHei","Noto Sans SC","Industry-Normal",sans-serif;z-index:25;pointer-events:auto;padding:12px;box-sizing:border-box;';
  p.addEventListener('mouseenter',()=>{if(!s.closed&&typeof w.Event_BlockMapHover==='function'){s.blocked=true;w.Event_BlockMapHover(true);}});
  p.addEventListener('mouseleave',()=>{if(s.blocked&&typeof w.Event_BlockMapHover==='function')w.Event_BlockMapHover(false);s.blocked=false;});
  w.appendChild(p);message(p,tr('Reading Encore stations…'));load(w,s);
 }
 const api={open,close,teardown};
 global[KEY]=Object.freeze(api);
 let observer=null;
 const pending=new Set();
 function teardown(){
  if(!alive)return;alive=false;
  if(observer)observer.disconnect();
  for(const timer of pending)global.clearTimeout(timer);
  pending.clear();
  for(const w of liveWidgets)destroy(w);
  liveWidgets.clear();
  if(global[KEY]===api)delete global[KEY];
 }

 // Replaces the old regional waypoint list. It does not replace map prototypes,
 // remove native handlers, or consume the game's zoom/pin/legend/back actions.
 const attachments=new WeakMap();
 function destroy(w){
  close(w);const s=states.get(w);
  if(s){if(s.activate)s.activate.clear();if(s.deactivate)s.deactivate.clear();states.delete(w);}
  const a=attachments.get(w);if(a)for(const h of a.handlers)h.clear();attachments.delete(w);liveWidgets.delete(w);
 }
 function attach(w){
  if(!alive||!w.WidgetIdent||typeof w.MakeEventName!=='function'||!global.engine)return;
  const key=w.MakeEventName('Activate'),old=attachments.get(w);
  if(old?.key===key)return;
  if(old)destroy(w);
  const reopen=(attempt=0)=>{
   if(!alive||attachments.get(w)?.key!==key)return;
   if(w.IsActivated&&w.parentNode){open(w,true);return;}
   if(attempt<20){const t=global.setTimeout(()=>{pending.delete(t);reopen(attempt+1);},50);pending.add(t);}
  };
  const handlers=[engine.on(key,()=>Promise.resolve().then(()=>reopen()))];
  attachments.set(w,{key,handlers});liveWidgets.add(w);
  if(w.IsActivated)open(w,true);
 }
 function scan(node){
  if(node.nodeType!==1)return;
  if(node.tagName.toLowerCase()==='widget-bigmap')attach(node);
  for(const w of node.querySelectorAll('widget-bigmap'))attach(w);
 }
 if(typeof MutationObserver!=='undefined'){
  observer=new MutationObserver(records=>{
   for(const r of records){
    if(r.type==='attributes'&&r.target.tagName.toLowerCase()==='widget-bigmap')attach(r.target);
    for(const n of r.addedNodes||[])scan(n);
    for(const n of r.removedNodes||[]){
     if(n.nodeType!==1)continue;
     const removed=n.tagName.toLowerCase()==='widget-bigmap'?[n]:Array.from(n.querySelectorAll('widget-bigmap'));
     for(const w of removed)destroy(w);
    }
   }
  });
  observer.observe(document.documentElement,{childList:true,subtree:true,attributes:true,attributeFilter:['class','data-inst-id']});
  scan(document.documentElement);
 }
})(globalThis);
