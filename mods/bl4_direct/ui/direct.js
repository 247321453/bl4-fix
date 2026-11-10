"use strict";

// BL4 Direct Connect's page in the BL4 Mod Menu screen (F6, or BL4 Direct Connect in MODS).
//
// The BL4 Mod Menu runs this file in the game's menu page (its extensions.js) and runs it again
// when it changes, so it tears its last copy down first. It registers ns.modPages[MOD]: when the
// Mod Menu shows this mod, it calls our render() to draw the page with its own parts (the game's
// Options rows, category dividers and list buttons), above the mod's remaining options. So the page
// looks and behaves like every other page of the Mod Menu: hover a row for its details on the right.
//
// Python (bl4_direct/page.py) serves the state through GET /ext?k=bl4direct (polled while the page
// shows) and takes clicks back as {op: "ext", ext: "bl4direct", do: ...}. Typing happens in Python
// (no key events reach this page): a click on a field starts it, and the text comes back in the state.

(function () {
    var ns = window.bl4ModMenu;
    if (!ns || !ns.ext) return;
    var ext = ns.ext;
    var KEY = "bl4direct";
    var MOD = "BL4 Direct Connect";
    var BASE = "coui://uiresources/bl4directconnect/";
    var POLL_SHOWN_MS = 250;
    var POLL_TYPING_MS = 50;
    var WATCH_MS = 500;
    var CSS_MS = 2000;

    if (ext.teardowns[KEY]) {
        try {
            ext.teardowns[KEY]();
        } catch (err) {}
    }
    // Survives reloads of this file; each copy takes a new, ever higher number
    var dc = ns.bl4dc || (ns.bl4dc = {});
    dc.counter = Math.max(dc.counter || 0, dc.gen || 0) + 1;
    var gen = dc.counter;
    dc.gen = gen;

    var timers = [];
    function alive() {
        return dc.gen === gen;
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
        if (ns.log) ns.log("[bl4direct] " + text);
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

    function pollSoon() {
        if (!polling) schedule(20);
    }

    // Only while the page shows: Python reads "it polled with open=1 just now" as "it's showing"
    function poll() {
        if (!showing()) return;
        polling = true;
        ext.get(KEY, true, function (snap) {
            polling = false;
            if (!alive()) return;
            if (snap && snap.state) onState(snap.state);
            if (showing()) schedule(dc.state && dc.state.typing ? POLL_TYPING_MS : POLL_SHOWN_MS);
        });
    }

    function onState(next) {
        var text = JSON.stringify(next);
        var first = !dc.state;
        dc.state = next;
        if (first) dc.lastToast = next.toast.id;
        if (next.toast.id !== dc.lastToast) {
            dc.lastToast = next.toast.id;
            if (ns.modToast && next.toast.text) ns.modToast(next.toast.text, next.toast.error);
        }
        if (text === dc.stateText) return;
        dc.stateText = text;
        if (ns.modPageRefresh) ns.modPageRefresh(MOD);
    }

    function send(payload) {
        ext.send(KEY, payload);
        pollSoon();
    }

    // Host / Stop / Leave / Join change the map: close the menus first (Python waits for that)
    function travel(payload) {
        send(payload);
        if (ns.modCloseScreen) ns.modCloseScreen(ns.context !== "main");
    }

    // The page shows: poll at once (the Mod Menu just opened it, or switched to it)
    function watch() {
        if (showing() && pollTimer === null && !polling) poll();
        later(watch, WATCH_MS);
    }

    // endregion
    // region Page

    function friendsText(n) {
        return n === 1 ? "1 位好友" : n + " 位好友";
    }

    function value(api, text, cls) {
        return api.el("p", "bl4dc_value" + (cls ? " " + cls : ""), text);
    }

    // wide: the row's only part (spans it, like the Mod Menu's Run buttons)
    function button(api, text, fn, enabled, wide) {
        var b = api.button(text, fn, wide ? "bl4mm_run" : "bl4dc_btn");
        if (enabled === false) b.classList.add("bl4mm_disabled");
        return b;
    }

    // The Mod Menu's own Off / On switch (the game's Options toggle); two buttons if it has none
    function toggle(api, on, fn, enabled) {
        var tpl = ns.templates && ns.templates.toggle;
        if (!tpl) {
            return button(api, on ? "开启" : "关闭", function () {
                fn(!on);
            }, enabled);
        }
        var t = tpl.cloneNode(true);
        var left = t.querySelector(".toggle_button_left");
        var right = t.querySelector(".toggle_button_right");
        var texts = t.querySelectorAll(".toggle_button_text");
        if (texts[0]) texts[0].textContent = "关闭";
        if (texts[1]) texts[1].textContent = "开启";
        if (left) left.classList.toggle("active", !on);
        if (right) right.classList.toggle("active", on);
        if (enabled !== false) {
            if (left) api.onClick(left, function () {
                if (on) fn(false);
            });
            if (right) api.onClick(right, function () {
                if (!on) fn(true);
            });
        } else {
            t.classList.add("bl4mm_disabled");
        }
        return t;
    }

    // A text field: click to type in it (Python reads the keys), or Paste
    function field(api, name, hint) {
        var s = dc.state;
        var text = s.fields[name] || "";
        var typing = s.typing === name;
        var f = api.el("div", "bl4dc_field" + (typing ? " bl4dc_typing" : ""));
        if (text) {
            f.appendChild(api.el("p", "bl4dc_field_text", text));
        } else if (!typing) {
            f.appendChild(api.el("p", "bl4dc_field_text bl4dc_field_hint", hint));
        }
        if (typing) f.appendChild(api.el("div", "bl4dc_caret"));
        api.hoverable(f);
        api.onClick(f, function () {
            send({ do: "type", field: typing ? null : name });
        });
        return f;
    }

    function render(api) {
        if (pollTimer === null && !polling) schedule(20);
        var s = dc.state;
        if (!s) {
            api.title("直连联机");
            api.row("正在加载……", "", []);
            return;
        }
        var hosting = s.mode === "hosting";
        var connected = s.mode === "connected";

        // The friend list or a firewall switch changed and Windows Firewall is behind: ask here
        // before Windows does (Python only sends ask_firewall while there's something to change)
        var ASKS = {
            friends: ["好友列表已更改", "防火墙规则仍使用旧的好友列表：新添加的好友无法连接到你创建的房间" +
                "，已移除的好友仍可连接。"],  // prettier-ignore
            on: ["启用防火墙规则", "将 BL4 Direct 规则添加到 Windows 防火墙：仅允许本机、好友以及已放行的" +
                "局域网连接到你创建的房间。"],  // prettier-ignore
            off: ["移除防火墙规则", "从 Windows 防火墙中删除 BL4 Direct 规则。"],
            lan: ["局域网设置已更改", "更改局域网和 VPN 中哪些设备可以连接到你创建的房间。"]
        };
        var ask = s.ask_firewall && ASKS[s.ask_firewall];
        if (ask) {
            api.title("是否更新防火墙？");
            api.row(ask[0], ask[1] + "点击“继续”：Windows 将询问是否允许 Network Command Shell 进行更改。这是 netsh，" +
                "即 Windows 自带的防火墙工具（“显示更多详细信息”中可查看规则），请选择“是”。点击“暂不更新”：稍后可在“防火墙”部分点击“更新”。", [  // prettier-ignore
                value(api, "接下来将显示 Windows 权限提示", "bl4dc_small"),
                button(api, "继续", function () {
                    send({ do: "firewall" });
                }, !s.asking),
                button(api, "暂不更新", function () {
                    send({ do: "firewall_later" });
                })
            ]);
        }

        api.title("你的游戏");
        var status, statusDesc, statusCls = "";
        if (hosting) {
            status = "房间已创建，" + friendsText(s.connected) + "已连接";
            statusDesc = "房间使用 UDP 端口 " + s.port + "。列表中的好友可在各自的 BL4 Direct 页面加入。";
            statusCls = "bl4dc_on";
        } else if (connected) {
            status = "正在好友的游戏中";
            statusDesc = "已直连到好友的游戏，无需经过 SHiFT。";
            statusCls = "bl4dc_on";
        } else if (s.intent) {
            status = s.in_game ? "正在重新开房……" : "进入游戏后自动开房";
            statusDesc = "切换地图后会自动恢复开房。点击“取消恢复”可取消。";
            statusCls = "bl4dc_warn";
        } else {
            status = "未进行直连联机";
            statusDesc = "创建房间供好友加入，或加入好友已创建的房间。";
        }
        api.row("状态", statusDesc, [value(api, status, statusCls)]);

        if (hosting) {
            api.row("停止开房", "重新加载地图并恢复为普通游戏，已连接的好友将断开连接。", [
                button(api, "停止", function () {
                    travel({ do: "stop" });
                }, true, true)
            ]);
        } else if (connected) {
            api.row("离开游戏", "返回主菜单，恢复普通在线联机。", [
                button(api, "离开", function () {
                    travel({ do: "leave" });
                }, true, true)
            ]);
        } else if (s.intent) {
            api.row("取消恢复", "取消开房：下次加载地图时将作为普通游戏运行。", [
                button(api, "取消", function () {
                    send({ do: "dont_resume" });
                }, true, true)
            ]);
        } else {
            var hostDesc = !s.in_game
                ? "请先选择“继续”进入游戏，再创建房间。"
                : s.firewall_off
                ? "重新加载当前地图，并通过 UDP 端口 " + s.port + " 创建联机房间。"
                : "重新加载当前地图，并通过 UDP 端口 " + s.port + " 创建联机房间。仅允许列表中的好友（及已放行的局域网）加入。" +
                  (s.firewall ? "" : " 防火墙规则与好友列表不一致，请在“防火墙”部分更新，否则新添加的好友无法加入。");  // prettier-ignore
            api.row("创建房间", hostDesc, [
                button(api, "创建", function () {
                    travel({ do: "host" });
                }, s.in_game, true)
            ]);
        }

        // Your address
        var ipName = hosting ? "好友连接地址" : "你的公网 IP";
        var ipDesc = "将此地址发给好友，让对方在各自的 BL4 Direct 页面中点击“添加好友”并填写。你也需要以同样方式添加对方的地址。";
        if (s.ip.state === "ok") {
            var shown = hosting ? s.ip.ip + ":" + s.port : s.ip.ip;
            api.row(ipName, ipDesc, [
                value(api, shown, "bl4dc_addr"),
                button(api, "复制", function () {
                    send({ do: "copy", what: hosting ? "address" : "ip" });
                })
            ]);
        } else if (s.ip.state === "failed") {
            api.row(ipName, "无法获取你的公网 IP，请检查网络。" + ipDesc, [
                value(api, "获取失败", "bl4dc_off"),
                button(api, "重试", function () {
                    send({ do: "retry_ip" });
                })
            ]);
        } else {
            api.row(ipName, ipDesc, [value(api, "正在获取……")]);
        }

        api.row("版本信息", "你与好友在此处看到的版本应一致，否则可能无法加入。", [
            value(api, s.compat, "bl4dc_small")
        ]);

        // Firewall: the switches (saved in the friends file, shared with BL4 Fix Setup) and what
        // Windows Firewall blocks or lets in right now
        var fw = s.fw;
        if (fw) {
            api.title("防火墙");
            api.row("防火墙规则", "开启：Windows 防火墙规则会限制联机端口（UDP " + s.port + "）的连接来源，仅允许本机、" +
                "列表中的好友以及已放行的局域网连接。此规则只阻止其他连接，不会开放任何端口。" +
                "关闭：不设置此规则，开房期间，Steam 自带的规则允许任何能访问该端口的人尝试连接。" +
                "更改时会先在页面中确认（点击“继续”），随后 Windows 会请求管理员权限。", [  // prettier-ignore
                toggle(api, fw.on, function (on) {
                    send({ do: "set_firewall", on: on });
                }, !s.asking)
            ]);
            api.row("允许局域网连接", "开启：家庭网络及 VPN（Tailscale、ZeroTier）中的设备" +
                "无需加入好友列表即可连接到你创建的房间。关闭：仅允许本机和好友连接。此设置仅在防火墙规则开启时生效。", [  // prettier-ignore
                toggle(api, fw.lan, function (on) {
                    send({ do: "set_lan", on: on });
                }, !s.asking)
            ]);
            var fwParts = [value(api, s.asking ? "等待 Windows 确认" : fw.summary, s.asking ? "bl4dc_warn" : fw.cls)];
            if (fw.action) {
                fwParts.push(button(api, fw.action === "remove" ? "移除" : "更新", function () {
                    send({ do: "firewall" });
                }, !s.asking));
            }
            api.row("状态", fw.details, fwParts);
        }

        api.title("好友");
        if (!s.friends.length) {
            api.row("暂无好友", "在下方填写好友的公网 IP 来添加好友，对方可在自己的 BL4 Direct 页面中查看该地址。", [
                value(api, "请在下方添加")
            ]);
        }
        s.friends.forEach(function (f) {
            var addr = f.address + (f.port !== 7777 ? ":" + f.port : "");
            // Joining before the main menu leaves you on a black screen (issue #2): Join waits for it
            var joinDesc = s.title
                ? "请先处理标题画面的所有提示，进入主菜单后再加入好友：" + f.name + "。"
                : "加入 " + f.name + " 的房间，地址：" + f.address + ":" + f.port + "。对方必须已创建房间，并将你的 IP 添加到好友列表。";
            api.row(f.name, joinDesc + " 点击“移除”将其从好友列表中删除，更新防火墙后也会取消对方的连接权限。", [  // prettier-ignore
                value(api, addr, "bl4dc_addr bl4dc_small"),
                button(api, "加入", function () {
                    travel({ do: "join", name: f.name });
                }, !connected && !s.title),
                button(api, "移除", function () {
                    send({ do: "remove", name: f.name });
                })
            ]);
        });

        api.title("添加好友");
        api.row("名称", "点击输入框并填写好友名称。按 Enter 或 Tab 切换到 IP 输入框。", [field(api, "name", "好友名称")]);
        api.row("IP 地址", "填写对方的公网 IP，例如 203.0.113.5（对方可在自己的 BL4 Direct 页面中查看）。点击输入框直接输入，" +
            "或复制地址后点击“粘贴”（输入时也可按 Ctrl+V）。按 Enter 添加好友。", [  // prettier-ignore
            field(api, "ip", "例如 203.0.113.5"),
            button(api, "粘贴", function () {
                send({ do: "paste", field: "ip" });
            })
        ]);
        api.row("添加好友", "将对方添加到好友列表。启用防火墙规则时，页面会随后询问是否放行对方的连接。", [
            button(api, "添加", function () {
                send({ do: "add" });
            }, !!(s.fields.name.trim() && s.fields.ip.trim()), true)
        ]);

    }

    // The mod's own options: the ones this page replaces are hidden
    function keep(node) {
        var hide = (dc.state && dc.state.hide) || [];
        return hide.indexOf(node.id) < 0 && hide.indexOf(node.name) < 0;
    }

    // endregion
    // region Stylesheet

    function checkCss() {
        ns.get(BASE + "direct.css", function (css) {
            if (!alive()) return;
            if (css && css !== dc.cssText) {
                dc.cssText = css;
                var style = document.getElementById("bl4dc_css");
                if (!style) {
                    style = document.createElement("style");
                    style.id = "bl4dc_css";
                    document.head.appendChild(style);
                }
                style.textContent = css;
            }
            // Only re-read while the page shows (a dev edit); otherwise rarely
            later(checkCss, showing() ? CSS_MS : CSS_MS * 5);
        });
    }

    // endregion

    // A click anywhere but the field being typed in stops typing (capture: rows stop propagation)
    function clickOff(evt) {
        if (!alive() || !dc.state || !dc.state.typing) return;
        for (var n = evt.target; n; n = n.parentNode) {
            if (n.classList && n.classList.contains("bl4dc_field")) return;
        }
        send({ do: "type", field: null });
    }
    document.addEventListener("click", clickOff, true);

    ext.teardowns[KEY] = function () {
        dc.gen = 0;
        document.removeEventListener("click", clickOff, true);
        timers.forEach(clearTimeout);
        if (pollTimer !== null) clearTimeout(pollTimer);
        if (ns.modPages && ns.modPages[MOD] && ns.modPages[MOD].gen === gen) delete ns.modPages[MOD];
    };

    ns.modPages = ns.modPages || {};
    ns.modPages[MOD] = { gen: gen, render: render, keep: keep, moreTitle: "更多" };
    dc.stateText = null;
    checkCss();
    watch();
    if (ns.modPageRefresh) ns.modPageRefresh(MOD);
    log("ready");
})();
