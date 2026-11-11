"use strict";

// The Performance page of the MODS screen (with Updates, Discover, Repositories): a benchmark of
// what every mod costs. Was the separate BL4 Mod Profiler's page until 2026-10-29.
//
// The Mod Menu runs this file in its menu page as one of its own extensions (extensions.js) and again
// whenever it changes, so it tears its last copy down first, then registers ns.modPages[MOD], where
// MOD is menu.js's key for this page: render() draws it with the Mod Menu's own rows and buttons.
// Python (bl4_mod_menu/perf/page.py) serves the state through GET /ext?k=bl4perf while the page
// shows and takes clicks as {op: "ext", ext: "bl4perf", do}.

(function () {
    var ns = window.bl4ModMenu;
    if (!ns || !ns.ext) return;
    var ext = ns.ext;
    var KEY = "bl4perf";
    var MOD = "\u0002perf"; // menu.js's PERF
    var BASE = "coui://uiresources/bl4modmenu/";
    var POLL_SHOWN_MS = 500;
    var WATCH_MS = 500;
    var CSS_MS = 2000;

    if (ext.teardowns[KEY]) {
        try {
            ext.teardowns[KEY]();
        } catch (err) {}
    }
    // Survives reloads of this file; each copy takes a new, ever higher number
    var pf = ns.bl4perfPage || (ns.bl4perfPage = {});
    pf.counter = Math.max(pf.counter || 0, pf.gen || 0) + 1;
    var gen = pf.counter;
    pf.gen = gen;

    var timers = [];
    function alive() {
        return pf.gen === gen;
    }
    function later(fn, ms) {
        var id = setTimeout(function () {
            var at = timers.indexOf(id);
            if (at >= 0) timers.splice(at, 1);
            if (alive()) fn();
        }, ms);
        timers.push(id);
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
            if (showing()) schedule(POLL_SHOWN_MS);
        });
    }

    function onState(next) {
        var text = JSON.stringify(next);
        var first = !pf.state;
        pf.state = next;
        if (first) pf.lastToast = next.toast.id;
        if (next.toast.id !== pf.lastToast) {
            pf.lastToast = next.toast.id;
            if (ns.modToast && next.toast.text) ns.modToast(next.toast.text, next.toast.error);
        }
        if (text === pf.stateText) return;
        pf.stateText = text;
        if (ns.modPageRefresh) ns.modPageRefresh(MOD);
    }

    function send(payload) {
        ext.send(KEY, payload);
        if (!polling) schedule(20);
    }

    function watch() {
        if (showing() && pollTimer === null && !polling) poll();
        later(watch, WATCH_MS);
    }

    // endregion
    // region Page

    function fixed(n, digits) {
        return (Math.round(n * Math.pow(10, digits)) / Math.pow(10, digits)).toFixed(digits);
    }

    function value(api, text, cls) {
        return api.el("p", "bl4pf_value" + (cls ? " " + cls : ""), text);
    }

    function button(api, text, fn, wide) {
        return api.button(text, fn, wide ? "bl4mm_run" : "bl4pf_btn");
    }

    var VERDICT = {
        free: ["几乎无开销", "bl4pf_free"],
        light: ["轻量", "bl4pf_light"],
        heavy: ["高开销", "bl4pf_heavy"],
        hitches: ["卡顿", "bl4pf_bad"]
    };

    function modDesc(m) {
        var lines = [];
        lines.push(fixed(m.ms_frame, 3) + " 毫秒 Python / 帧（平均），最慢单次调用 " + fixed(m.own_worst_ms, 2) + " 毫秒" +
            (m.own_over_5ms ? ", " + m.own_over_5ms + " 的调用超过 5 毫秒（每次都可能造成可见卡顿）" : "") + ".");  // prettier-ignore
        if (m.outside_slow) {
            lines.push(m.outside_slow + " 次慢调用（最长 " + fixed(m.worst_ms, 2) + " 毫秒）并非由该模组导致：可能是 Python 垃圾回收暂停，或" +
                "同一帧中影响多个模组的停顿。");  // prettier-ignore
        }
        if (m.hooks.length) {
            lines.push("");
            lines.push("钩子（毫秒/帧、最长耗时、调用次数/秒）：");
            m.hooks.slice(0, 8).forEach(function (h) {
                lines.push("  " + h.label + ":  " + fixed(h.ms_frame, 3) + ",  " + fixed(h.worst_ms, 2) + ",  " + Math.round(h.calls_s));
            });
            if (m.hooks.length > 8) lines.push("  另有 " + (m.hooks.length - 8) + " 项（详见报告）");
        } else {
            lines.push("未检测到钩子：可能采用其他工作方式，或相关事件在测试期间未触发。");
        }
        if (m.threads.length) {
            lines.push("");
            lines.push("后台线程（CPU 毫秒/秒）：");
            m.threads.forEach(function (t) {
                lines.push("  " + t.name + ":  " + fixed(t.cpu_ms_s, 1));
            });
        }
        return lines.join("\n");
    }

    function render(api) {
        if (pollTimer === null && !polling) schedule(20);
        var s = pf.state;
        api.title("基准测试");
        if (!s) {
            api.row("加载中…", "", []);
            return;
        }
        var busy = s.phase !== "idle";
        var runDesc = "关闭菜单并正常游玩 " + Math.round(s.length) + " 秒：将统计所有已启用的模组，" +
            "包括其他作者的模组。战斗或开放世界场景更有参考价值。测试开始和结束时会显示屏幕提示。";  // prettier-ignore
        if (!busy) {
            api.row("开始基准测试", runDesc, [
                button(api, "执行", function () {
                    send({ do: "run" });
                    // Measure play, not this screen: close the menus (Python waits for that)
                    if (ns.modCloseScreen && ns.context !== "main") ns.modCloseScreen(true);
                }, true)
            ]);
        } else {
            var status = s.phase === "running" ? "测量中，剩余 " + Math.ceil(s.left) + " 秒" :
                s.phase === "settling" ? "即将开始…" : "关闭菜单后开始";  // prettier-ignore
            api.row("基准测试", runDesc, [
                value(api, status, "bl4pf_warn"),
                button(api, "停止", function () {
                    send({ do: "stop" });
                })
            ]);
        }
        api.row("时长", "基准测试的测量时长。更长的测试可获得更稳定的平均值，并捕获较少出现的卡顿。", [
            value(api, Math.round(s.length) + " 秒"),
            button(api, "更改", function () {
                send({ do: "length" });
            })
        ]);
        if (s.message) api.row("最新消息", s.message, [value(api, s.message, "bl4pf_small")]);

        var r = s.result;
        if (!r) return;
        api.title("上次测试：" + r.at + (r.world ? ", " + r.world : ""));
        api.row("帧耗时", Math.round(r.seconds) + " 秒，" + r.frames + " 帧。中位数 " + fixed(r.median_ms, 2) + " 毫秒，99% 的帧低于 " +
            fixed(r.p99_ms, 2) + " 毫秒，最差 " + fixed(r.worst_ms, 1) + " 毫秒。卡顿阈值：帧耗时超过 " + Math.round(r.hitch_ms) +
            " 毫秒（中位数的两倍，且至少为 33 毫秒）。", [  // prettier-ignore
            value(api, Math.round(r.fps) + " FPS，中位数 " + fixed(r.median_ms, 1) + " 毫秒，" + r.hitches + " 次卡顿")
        ]);
        var slow = r.slowest.map(function (f) {
            return "  " + fixed(f.ms, 1) + " 毫秒/帧：模组 " + fixed(f.mods_ms, 2) + " 毫秒" + (f.top ? " 毫秒，最高 " + f.top + " " + fixed(f.top_ms, 2) : "");
        });
        api.row("全部模组", "所有模组的钩子合计每帧耗时，及其占一帧中位耗时的比例。测试工具自身的" +
            "计时开销约为 " + fixed(r.overhead_ms_frame, 3) + " 毫秒/帧（不计入结果）。" +
            (r.dispatch_us ? "\n\n同样不计入：SDK 调用每个钩子的开销，约 " + fixed(r.dispatch_us, 1) + " 微秒/次，" +
                Math.round(r.calls_frame) + " 次调用/帧 ≈ " + fixed(r.dispatch_ms_frame, 2) + " 毫秒/帧。" : "") +
            "\n\n最慢的帧：\n" +
            slow.join("\n") + (r.other_threads_ms_s > 0.05 ? "\n\n未关联到模组的 Python 线程：" + fixed(r.other_threads_ms_s, 1) + " 毫秒 CPU / 秒。" : ""), [  // prettier-ignore
            value(api, fixed(r.mods_ms_frame, 2) + " 毫秒/帧（" + fixed(r.share * 100, 1) + "%)", r.mods_ms_frame >= 1 ? "bl4pf_heavy" : "")
        ]);
        if (r.gc.length) {
            var worst = 0, count = 0;
            r.gc.forEach(function (g) {
                worst = Math.max(worst, g.worst_ms);
                count += g.count;
            });
            api.row("Python 垃圾回收", r.gc.map(function (g) {
                return "第 " + g.gen + ": " + g.count + " 次，平均 " + fixed(g.avg_ms, 2) + " 毫秒，最差 " + fixed(g.worst_ms, 2) + " 毫秒";
            }).join("\n") + "\n\n由所有模组共享。“性能修复”会尽量避免耗时较长的完整回收。", [  // prettier-ignore
                value(api, count + " 次，最长 " + fixed(worst, 1) + " 毫秒", worst > 5 ? "bl4pf_bad" : "")
            ]);
        }

        api.title("各模组（开销从高到低）");
        r.mods.forEach(function (m) {
            var v = VERDICT[m.verdict] || VERDICT.free;
            var text = fixed(m.ms_frame, 3) + " 毫秒/帧，最长 " + fixed(m.own_worst_ms, 1) + " 毫秒";
            if (m.threads_ms_s >= 1) text += "，线程 " + fixed(m.threads_ms_s, 0) + " 毫秒/秒";
            api.row(ns.displayName ? ns.displayName(m) : m.name, modDesc(m), [value(api, text, "bl4pf_small"), value(api, v[0], "bl4pf_tag " + v[1])]);
        });
        api.row("报告文件", "完整文本报告（所有钩子、慢调用、最慢的帧），可保存或发送给模组作者：\n" + s.report +
            "\n\n" + r.mods_off + " 个已关闭的模组未参与测量。" + r.notes.map(function (note) { return ns.tr ? ns.tr(note) : note; }).join(" "), [  // prettier-ignore
            button(api, "打开", function () {
                send({ do: "open" });
            })
        ]);
    }

    // endregion
    // region Stylesheet

    function checkCss() {
        ns.get(BASE + "perf.css", function (css) {
            if (!alive()) return;
            if (css && css !== pf.cssText) {
                pf.cssText = css;
                var style = document.getElementById("bl4pf_css");
                if (!style) {
                    style = document.createElement("style");
                    style.id = "bl4pf_css";
                    document.head.appendChild(style);
                }
                style.textContent = css;
            }
            later(checkCss, showing() ? CSS_MS : CSS_MS * 5);
        });
    }

    // endregion

    ext.teardowns[KEY] = function () {
        pf.gen = 0;
        timers.forEach(clearTimeout);
        if (pollTimer !== null) clearTimeout(pollTimer);
        if (ns.modPages && ns.modPages[MOD] && ns.modPages[MOD].gen === gen) delete ns.modPages[MOD];
    };

    ns.modPages = ns.modPages || {};
    ns.modPages[MOD] = { gen: gen, render: render };
    pf.stateText = null;
    checkCss();
    watch();
    if (ns.modPageRefresh) ns.modPageRefresh(MOD);
})();
