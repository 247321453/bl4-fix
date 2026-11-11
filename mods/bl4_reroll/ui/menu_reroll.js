"use strict";

// Use Mod Menu's retained navigation, even when Esc has hidden its overlay.
// Never retarget to whichever inventory card happens to be hovered.
(function () {
    var ns = (typeof bl4linkNs !== "undefined" && bl4linkNs) || window.bl4ModMenu;
    if (!ns || !ns.ext) return;
    var ext = ns.ext;
    var KEY = "reroll_menu";
    if (ext.teardowns[KEY]) ext.teardowns[KEY]();
    var live = true, timer = null, snap = null, last = null;
    var version = 0, handled = null, page = String(Date.now()) + ":" + String(Math.random());

    function inventoryOpen() {
        var menu = document.querySelector("widget-menu-equip");
        if (!menu || menu.Active === false) return false;
        var rect = menu.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) return false;
        var style = window.getComputedStyle(menu);
        return style.display !== "none" && style.visibility !== "hidden" && style.visibility !== "collapse";
    }

    function current() {
        var menu = window.bl4ModMenu;
        var view = menu && menu.view;
        var link = menu && menu.link;
        var data = link && link.state;
        var active = document.activeElement;
        if (!inventoryOpen() || !view || view.mod !== "BL4 Reroll" || !data || data.capture
                || !view.nested || view.nested.length !== 1
                || (active && (active.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(active.tagName)))) return null;
        var ident = view.nested[0];
        if (typeof ident !== "string" || !/^item[0-9]+$/.test(ident)) return null;
        var mods = data.mods || [], mod = null, node = null, button = false;
        for (var i = 0; i < mods.length; i++) if (mods[i].name === "BL4 Reroll") mod = mods[i];
        if (!mod || mod.enabled === false) return null;
        var options = mod.options || [];
        for (var j = 0; j < options.length; j++) if (options[j].id === ident) node = options[j];
        if (!node || node.kind !== "nested") return null;
        var children = node.children || [];
        for (var k = 0; k < children.length; k++) {
            if (children[k].id === "legendary" && children[k].kind === "button") button = true;
        }
        var serial = snap && snap.pages && snap.pages[ident];
        if (!button || typeof serial !== "string" || !serial) return null;
        return { handle: Number(ident.slice(4)), serial: serial };
    }

    function context() {
        var value = current();
        var key = JSON.stringify(value);
        if (key !== last) { last = key; version++; }
        if (!value) return null;
        value.page = page + ":" + version;
        return value;
    }

    function report() {
        var value = context();
        // Heartbeats expire quickly on Python's side when the page sleeps.
        ext.send(KEY, { do: "view", inventory: inventoryOpen(), context: value });
        return value;
    }

    function receive(value) {
        if (!live) return;
        snap = value && value.state ? value.state : {};
        var view = report();
        var request = snap.request;
        if (request && request.id !== handled) {
            handled = request.id;
            // Re-check now, not when a key press was queued; navigation invalidates the token.
            if (view && JSON.stringify(view) === JSON.stringify(request.context)) {
                ext.send(KEY, { do: "reroll", id: request.id, context: view });
            }
        }
        timer = setTimeout(poll, view ? 60 : 180);
    }

    function poll() {
        timer = null;
        if (!live) return;
        // Publish leaving/changing the page before requesting another action.
        report();
        ext.get(KEY, !!current(), receive);
    }

    ext.teardowns[KEY] = function () {
        live = false;
        if (timer !== null) clearTimeout(timer);
        ext.send(KEY, { do: "view", inventory: false, context: null });
    };
    poll();
})();
