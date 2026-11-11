"use strict";

// BL4 Save Backups' page in the BL4 Mod Menu screen (MODS > BL4 Save Backups).
//
// Run by the Mod Menu's extensions.js in the game's menu page (and again when this file changes),
// so it retires its last copy first. Like BL4 Direct Connect's page (direct.js), it registers
// ns.modPages[MOD]: the Mod Menu calls render(api) to draw the page with its own rows and buttons,
// above the mod's options. Four views, switched here: the overview, one character's history, the
// bank's history, and every backup.
//
// Python (bl4_save_backup/page.py) serves a small state through GET /ext?k=bl4savebackup (polled
// while the page shows); the big view is a loose file (view.json) fetched when state.rev moves.
// Clicks go back as {op: "ext", ext: "bl4savebackup", do: ...}. A restore asks for a second click.

(function () {
    var ns = window.bl4ModMenu;
    if (!ns || !ns.ext) return;
    var ext = ns.ext;
    var KEY = "bl4savebackup";
    var MOD = "BL4 Save Backups";
    var BASE = "coui://uiresources/bl4savebackup/";
    var POLL_MS = 500;
    var WATCH_MS = 500;
    var CSS_MS = 2000;
    var CONFIRM_MS = 4000;

    if (ext.teardowns[KEY]) {
        try {
            ext.teardowns[KEY]();
        } catch (err) {}
    }
    // Survives reloads of this file; each copy takes a new, ever higher number
    var sb = ns.bl4sb || (ns.bl4sb = {});
    sb.counter = Math.max(sb.counter || 0, sb.gen || 0) + 1;
    var gen = sb.counter;
    sb.gen = gen;
    sb.page = sb.page || { view: "home" };

    var timers = [];
    function alive() {
        return sb.gen === gen;
    }
    function later(fn, ms) {
        var id = setTimeout(function () {
            var at = timers.indexOf(id);
            if (at >= 0) timers.splice(at, 1);
            if (alive()) fn();
        }, ms);
        timers.push(id);
    }
    function log(text) {
        if (ns.log) ns.log("[bl4savebackup] " + text);
    }

    // region Link

    var pollTimer = null;
    var polling = false;

    function showing() {
        var v = ns.view;
        return !!(v && v.open && v.mod === MOD && !(v.nested && v.nested.length));
    }

    function schedule(ms) {
        if (pollTimer !== null) clearTimeout(pollTimer);
        pollTimer = setTimeout(function () {
            pollTimer = null;
            if (alive()) poll();
        }, ms);
    }

    function poll() {
        if (!showing()) return;
        polling = true;
        ext.get(KEY, true, function (snap) {
            polling = false;
            if (!alive()) return;
            if (snap && snap.state) onState(snap.state);
            if (showing()) schedule(POLL_MS);
        });
    }

    function onState(next) {
        var first = !sb.state;
        sb.state = next;
        if (first) sb.lastToast = next.toast.id;
        if (next.toast.id !== sb.lastToast) {
            sb.lastToast = next.toast.id;
            if (ns.modToast && next.toast.text) ns.modToast(next.toast.text, next.toast.error);
        }
        if (next.rev !== sb.viewRev) loadView(next);
        var text = JSON.stringify(next) + "|" + sb.viewRev;
        if (text === sb.stateText) return;
        sb.stateText = text;
        refresh();
    }

    function loadView(s) {
        if (sb.loading === s.rev) return;
        sb.loading = s.rev;
        ns.get(s.view, function (text) {
            if (!alive()) return;
            sb.loading = null;
            if (!text) return;
            try {
                sb.data = JSON.parse(text);
                sb.viewRev = s.rev;
            } catch (err) {
                return;  // half a file: the next poll tries again
            }
            refresh();
        });
    }

    function refresh() {
        if (ns.modPageRefresh) ns.modPageRefresh(MOD);
    }

    function send(payload) {
        ext.send(KEY, payload);
        if (!polling) schedule(30);
    }

    function watch() {
        if (showing() && pollTimer === null && !polling) poll();
        later(watch, WATCH_MS);
    }

    // endregion
    // region Formatting

    function plural(n, one, many) {
        var labels = { item: "件物品", backup: "份备份", version: "个版本" };
        return n + " " + (labels[one] || (n === 1 ? one : many || one + "s"));
    }

    function commas(n) {
        var s = String(Math.round(Math.abs(n)));
        var out = "";
        while (s.length > 3) {
            out = "," + s.slice(-3) + out;
            s = s.slice(0, -3);
        }
        return (n < 0 ? "-" : "") + s + out;
    }

    function short(n) {
        var a = Math.abs(n);
        if (a >= 1e9) return (n / 1e9).toFixed(1) + "B";
        if (a >= 1e6) return (n / 1e6).toFixed(1) + "M";
        if (a >= 1e4) return Math.round(n / 1e3) + "K";
        return commas(n);
    }

    function hours(s) {
        var h = Math.floor(s / 3600);
        var m = Math.floor((s % 3600) / 60);
        return h ? h + " 小时 " + m + " 分钟" : m + " 分钟";
    }

    function signed(n, unit) {
        return (n > 0 ? "+" : "") + n + (unit || "");
    }

    var DIFFICULTY = { Easy: "简单", Normal: "普通", Hard: "困难" };

    // "Level 52, 66 h 33 m, $33.2M"
    function brief(i) {
        if (i.ok === false) return "已损坏";
        var parts = [];
        if (i.level !== undefined) parts.push("等级 " + i.level + (i.uvh ? " 终极秘藏猎人 " + i.uvh : ""));
        if (i.playtime !== undefined) parts.push(hours(i.playtime));
        if (i.cash !== undefined) parts.push("$" + short(i.cash));
        return parts.join(", ");
    }

    function details(i) {
        if (i.ok === false) return "此副本未能完整读取（" + (i.error || "损坏") + "），无法还原。";
        if (i.ok !== true) return "Mod 无法打开并读取此存档（" + (i.error || "缺少密钥") + "），但副本已保留。";
        var lines = [];
        var level = "等级 " + i.level;
        if (i.spec) level += "，专精 " + i.spec;
        if (i.difficulty) level += ", " + (DIFFICULTY[i.difficulty] || i.difficulty);
        if (i.uvh) level += "，终极秘藏猎人 " + i.uvh;
        lines.push(level + ".");
        lines.push("游戏时长 " + hours(i.playtime || 0) + (i.story_done ? "，主线已完成。" : "."));
        lines.push("现金 $" + commas(i.cash || 0) + "，镒矿 " + commas(i.eridium || 0) + ".");
        lines.push(plural(i.backpack || 0, "item") + " (" + (i.equipped || 0) + " 件已装备），失物招领 " + (i.lost_loot || 0) + ".");
        return lines.join(" ");
    }

    function changes(d) {
        if (!d) return "";
        var out = [];
        if (d.level) out.push("等级 " + signed(d.level));
        if (d.uvh) out.push("终极秘藏猎人 " + signed(d.uvh));
        if (d.items_added) out.push(plural(d.items_added, "item") + " 新获得");
        if (d.items_removed) out.push(plural(d.items_removed, "item") + " 已失去");
        if (d.cash) out.push("现金 " + (d.cash > 0 ? "+$" : "-$") + commas(Math.abs(d.cash)));
        if (d.playtime > 60) out.push(hours(d.playtime) + " 游戏时长");
        return out.length ? "与上一版本相比：" + out.join(", ") + "." : "";
    }

    function versusNow(v, thing) {
        if (v.current) return "这就是当前存档。";
        if (v.gone_now === undefined) return "";
        var out = [];
        if (v.gone_now) out.push(plural(v.gone_now, "item") + " 存在于此版本，但当前已不在" + thing + "中");
        if (v.new_now) out.push(plural(v.new_now, "item") + " 位于" + thing + "中，但此版本中没有（还原后将失去）");
        return out.length ? "与当前相比：" + out.join("; ") + "." : "物品与当前相同。";
    }

    // endregion
    // region Parts

    function value(api, text, cls) {
        return api.el("p", "bl4sb_value" + (cls ? " " + cls : ""), text);
    }

    function button(api, text, fn, enabled, wide) {
        var b = api.button(text, fn, wide ? "bl4mm_run" : "bl4sb_btn");
        if (enabled === false) b.classList.add("bl4mm_disabled");
        return b;
    }

    // A restore button: the first click arms it ("确认还原？"), the second within CONFIRM_MS restores
    function restoreButton(api, id, text, payload, enabled) {
        var armed = sb.armed && sb.armed.id === id && Date.now() - sb.armed.at < CONFIRM_MS;
        return button(api, armed ? "确认还原？" : text, function () {
            if (sb.state && sb.state.busy) return;
            if (sb.armed && sb.armed.id === id && Date.now() - sb.armed.at < CONFIRM_MS) {
                sb.armed = null;
                send(payload);
            } else {
                sb.armed = { id: id, at: Date.now() };
                later(refresh, CONFIRM_MS + 50);
            }
            refresh();
        }, enabled);
    }

    function go(view, arg) {
        sb.page = { view: view, arg: arg };
        sb.armed = null;
        refresh();
    }

    function back(api, title) {
        api.title(title);
        api.row("返回", "返回角色与备份列表。", [button(api, "返回", function () {
            go("home");
        }, true, true)]);
    }

    // endregion
    // region Views

    function render(api) {
        if (pollTimer === null && !polling) schedule(20);
        var s = sb.state;
        var d = sb.data;
        if (!s || !d) {
            api.title("存档备份");
            api.row("正在加载……", "", []);
            return;
        }
        var page = sb.page;
        if (page.view === "char") {
            var ch = null;
            d.characters.forEach(function (c) {
                if (c.guid === page.arg) ch = c;
            });
            if (ch) return renderCharacter(api, s, d, ch);
        } else if (page.view === "bank") {
            return renderBank(api, s, d);
        } else if (page.view === "backups") {
            return renderBackups(api, s, d);
        }
        renderHome(api, s, d);
    }

    function renderStatus(api, s) {
        if (s.busy) api.row("处理中", s.busy, [value(api, s.busy, "bl4sb_warn")]);
        if (s.result) {
            api.title("上次还原结果");
            s.result.results.forEach(function (r) {
                api.row(r.what || r.target || "还原", r.ok
                    ? "已在退出游戏后还原。如需找回还原前的存档，可在“全部备份”中查找标记为“还原前备份”的版本。"
                    : "未还原：" + (r.error || "未知错误") + "。此项未做任何更改。",  // prettier-ignore
                    [value(api, r.ok ? "已还原" : "失败：" + (r.error || "错误"), r.ok ? "bl4sb_on" : "bl4sb_off")]);
            });
            api.row("知道了", "隐藏此结果，直到下次还原。", [button(api, "确定", function () {
                send({ do: "dismiss" });
            }, true, true)]);
        }
        if (s.pending && s.pending.length) {
            api.title("将在退出游戏后还原");
            s.pending.forEach(function (p) {
                api.row(p.what, "游戏会将存档保留在内存中，并在游玩和退出时再次保存，因此" +
                    "还原会在游戏关闭后立即执行。届时会先备份现有存档（标记为“还原前备份”）。", [  // prettier-ignore
                    value(api, p.target, "bl4sb_small"),
                    button(api, "移除", function () {
                        send({ do: "cancel", target: p.target });
                    })
                ]);
            });
            api.row("立即退出游戏", "正常退出游戏（先保存存档），随后执行还原。完成后请重新启动游戏。", [
                button(api, s.quitting ? "正在退出……" : "退出游戏", function () {
                    send({ do: "quit" });
                }, !s.quitting),
                button(api, "全部取消", function () {
                    send({ do: "cancel" });
                })
            ]);
        }
    }

    function renderHome(api, s, d) {
        renderStatus(api, s);
        api.title("备份");
        var last = d.last;
        api.row("上次备份", last
            ? "创建于 " + last.created_text + " (" + last.label.toLowerCase() + "): " + last.files.length + " 个存档文件，" + last.size + "。每次启动游戏时，若存档与上次相比有变化，就会创建一份备份。"
            : "暂无备份。每次启动游戏时会自动备份。",  // prettier-ignore
            [value(api, last ? last.created_text : "暂无"),
             button(api, "立即备份", function () {
                 send({ do: "backup" });
             }, !s.busy)]);  // prettier-ignore
        var fit = d.fit_1gb ? " 按每份 " + d.per_backup + " 计算，1 GB 约可容纳 " + commas(d.fit_1gb) + " 份备份。" : "";
        api.row("已保留备份", "保留 " + (s.keep === "All that fit in 1 GB" ? "1 GB 以内尽可能多的备份" : "最新的 " + s.keep) +
            "（可在下方“保留备份数量”中设置），总容量上限为 1 GB。标记为“保留”的备份不会被自动删除。" + fit, [  // prettier-ignore
            value(api, plural(d.count, "backup") + ", " + d.size),
            button(api, "查看全部", function () {
                go("backups");
            })
        ]);

        api.title("角色");
        if (!d.characters.length) api.row("暂无角色", "", []);
        d.characters.forEach(function (c) {
            var n = c.versions.length;
            api.row(c.name + (c.exists ? "" : "（已删除）"),
                (c.exists ? "当前位于槽位 " + c.slot + "。" : "当前存档中已无此角色，但其备份仍保留。") + details(c.now) +
                " " + plural(n, "version") + " 位于备份中。可通过“历史版本”查看并还原。",  // prettier-ignore
                [value(api, brief(c.now) + ", " + plural(n, "version"), "bl4sb_small"),
                 button(api, "历史版本", function () {
                     go("char", c.guid);
                 })]);  // prettier-ignore
        });

        api.title("银行");
        var bank = d.bank;
        api.row("银行", "银行由所有角色共享（位于 profile.sav 中）。可在历史版本中查看各个版本，并还原" +
            "银行或整个个人档案。", [  // prettier-ignore
            value(api, (bank.now !== null && bank.now !== undefined ? plural(bank.now, "item") + ", " : "") + plural(bank.versions.length, "version"), "bl4sb_small"),
            button(api, "历史版本", function () {
                go("bank");
            })
        ]);
        api.row("备份文件夹", "在资源管理器中打开备份文件夹。每份备份单独存放，内含存档文件的原样副本。" + d.folder, [
            button(api, "打开文件夹", function () {
                send({ do: "folder" });
            }, true, true)
        ]);
    }

    function renderCharacter(api, s, d, c) {
        renderStatus(api, s);
        back(api, c.name + "的历史版本");
        if (c.exists) api.row("当前", "当前存档（槽位 " + c.slot + "）。" + details(c.now), [value(api, brief(c.now), "bl4sb_small")]);
        c.versions.forEach(function (v) {
            var desc = [details(v.info), changes(v.vs_older), versusNow(v, "背包"),
                v.current ? "" : "退出游戏后还原此版本（会先备份届时的现有存档）。共享进度与银行保持不变。"]  // prettier-ignore
                .filter(function (x) { return x; }).join(" ");
            api.row((v.current ? "当前：" : "") + "保存于 " + v.saved_text, desc, [
                value(api, brief(v.info), "bl4sb_small" + (v.ok === false ? " bl4sb_off" : "")),
                restoreButton(api, "c" + v.id, "还原", { do: "restore", kind: "character", backup: v.backup, file: v.file },
                    !v.current && v.ok !== false && !s.busy)  // prettier-ignore
            ]);
        });
    }

    function renderBank(api, s, d) {
        renderStatus(api, s);
        back(api, "银行历史版本");
        var bank = d.bank;
        if (bank.now !== null && bank.now !== undefined) api.row("当前", "当前银行内容。", [value(api, plural(bank.now, "item"), "bl4sb_small")]);
        if (!bank.versions.length) api.row("暂无历史版本", "", []);
        bank.versions.forEach(function (v) {
            var since = v.added || v.removed ? "与上一版本相比：" + v.added + " 件新增，" + v.removed + " 件移除。" : "";
            var desc = since + versusNow(v, "银行") +
                " 点击“银行”仅还原银行（个人档案的其他内容不变）。点击“个人档案”则还原当时的整个 profile.sav：" +
                "包括银行、共享进度、秘藏卡和设置。两种还原都会在退出游戏后执行。";  // prettier-ignore
            api.row((v.current ? "当前：" : "") + "保存于 " + v.saved_text, desc, [
                value(api, plural(v.items, "item"), "bl4sb_small"),
                restoreButton(api, "b" + v.id, "银行", { do: "restore", kind: "bank", backup: v.backup }, !v.current && !s.busy),
                restoreButton(api, "p" + v.id, "个人档案", { do: "restore", kind: "profile", backup: v.backup }, !s.busy)
            ]);
        });
    }

    function renderBackups(api, s, d) {
        renderStatus(api, s);
        back(api, "全部备份");
        d.sessions.forEach(function (b) {
            var who = b.files.map(function (f) {
                return f.who + (f.level ? "（等级 " + f.level + ")" : "") + (f.ok === false ? "（损坏）" : "");
            }).join(", ");
            var desc = b.label + ", " + b.created_text + ", " + b.size + ": " + who + "。标记为“保留”可防止备份被自动删除。" +
                "“全部还原”会在退出游戏后还原备份内的所有存档（角色还原到其当前所在的槽位）。";  // prettier-ignore
            api.row(b.created_text + (b.keep ? "（已保留）" : ""), desc, [
                value(api, b.label + ", " + b.files.length + " 个文件", "bl4sb_small" + (b.bad ? " bl4sb_warn" : "")),
                button(api, b.keep ? "取消保留" : "保留", function () {
                    send({ do: "keep", backup: b.name, keep: !b.keep });
                }),
                restoreButton(api, "a" + b.name, "全部还原", { do: "restore", kind: "all", backup: b.name }, !s.busy)
            ]);
        });
    }

    // The options the page already has as rows (they stay in the console's mod menu)
    var HIDDEN = ["Back up now", "Open the backup folder"];
    function keep(node) {
        return HIDDEN.indexOf(node.id) < 0 && HIDDEN.indexOf(node.name) < 0;
    }

    // endregion
    // region Stylesheet

    function checkCss() {
        ns.get(BASE + "backups.css", function (css) {
            if (!alive()) return;
            if (css && css !== sb.cssText) {
                sb.cssText = css;
                var style = document.getElementById("bl4sb_css");
                if (!style) {
                    style = document.createElement("style");
                    style.id = "bl4sb_css";
                    document.head.appendChild(style);
                }
                style.textContent = css;
            }
            if (ns.dev !== false) later(checkCss, showing() ? CSS_MS : CSS_MS * 5);
        });
    }

    // endregion

    ext.teardowns[KEY] = function () {
        sb.gen = 0;
        timers.forEach(clearTimeout);
        if (pollTimer !== null) clearTimeout(pollTimer);
        if (ns.modPages && ns.modPages[MOD] && ns.modPages[MOD].gen === gen) delete ns.modPages[MOD];
    };

    ns.modPages = ns.modPages || {};
    ns.modPages[MOD] = { gen: gen, render: render, keep: keep, moreTitle: "设置" };
    sb.stateText = null;
    checkCss();
    watch();
    refresh();
    log("ready");
})();
