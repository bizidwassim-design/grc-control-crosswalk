/* GRC Control Crosswalk explorer. No dependencies, no network. MIT License. */
(function () {
  "use strict";
  var X = window.CROSSWALK;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var FW_KEYS = Object.keys(X.frameworks).filter(function (k) { return k !== "iso27001_2022"; });
  var OV_KEYS = Object.keys(X.overlays);
  var byIso = {}; X.controls.forEach(function (c) { byIso[c.iso27001_2022] = c; });
  var domains = []; X.controls.forEach(function (c) { if (domains.indexOf(c.domain) < 0) domains.push(c.domain); });

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { if (k === "text") n.textContent = attrs[k]; else if (k === "class") n.className = attrs[k]; else n.setAttribute(k, attrs[k]); });
    (children || []).forEach(function (c) { if (c != null) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function pill(v, data) { return el("span", { class: "pill", "data-v": data || "", text: v }); }
  function isoLink(ref) {
    var b = el("button", { type: "button", class: "pill link", text: ref, title: byIso[ref] ? byIso[ref].iso27001_title : "" });
    b.addEventListener("click", function () { showTab("tab-iso"); $("#iso-search").value = ref; filters.q = ref.toLowerCase(); renderIso(); });
    return b;
  }
  function say(m) { $("#status").textContent = m; }
  function cell(v) { v = String(v == null ? "" : v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
  function download(name, text) { var b = new Blob([text], { type: "text/csv" }); var a = el("a", { href: URL.createObjectURL(b), download: name }); document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  function showTab(id) { document.querySelectorAll('[role="tab"]').forEach(function (t) { var on = t.id === id; t.setAttribute("aria-selected", String(on)); $("#" + t.getAttribute("aria-controls")).hidden = !on; }); }
  function hay(c) { return [c.iso27001_2022, c.iso27001_title, c.domain, c.notes].concat(FW_KEYS.map(function (k) { return c[k]; })).concat(OV_KEYS.map(function (k) { return c.overlays[k].join(" "); })).join(" ").toLowerCase(); }

  /* ---------- From ISO ---------- */
  var filters = { q: "", domain: "", cols: {} };
  FW_KEYS.forEach(function (k) { filters.cols[k] = true; }); OV_KEYS.forEach(function (k) { filters.cols[k] = k === "uae_iar"; });
  function isoColumns() {
    var cols = [["iso27001_2022", "ISO 27001:2022"], ["iso27001_title", "Control"]];
    FW_KEYS.forEach(function (k) { if (filters.cols[k]) cols.push([k, X.frameworks[k].header]); });
    OV_KEYS.forEach(function (k) { if (filters.cols[k]) cols.push([k, X.overlays[k].label]); });
    cols.push(["notes", "Notes"]);
    return cols;
  }
  function isoRows() { var q = filters.q; return X.controls.filter(function (c) { return (!filters.domain || c.domain === filters.domain) && (!q || hay(c).indexOf(q) >= 0); }); }
  function renderIso() {
    var head = $("#iso-head"), body = $("#iso-body"); head.textContent = ""; body.textContent = "";
    var cols = isoColumns();
    cols.forEach(function (c) { head.appendChild(el("th", { scope: "col", text: c[1] })); });
    var rows = isoRows(), lastDomain = null;
    rows.forEach(function (c) {
      if (c.domain !== lastDomain) { body.appendChild(el("tr", { class: "domain-row" }, [el("td", { colspan: String(cols.length), text: c.domain })])); lastDomain = c.domain; }
      var tr = el("tr");
      cols.forEach(function (col) {
        var k = col[0];
        if (k === "iso27001_2022") tr.appendChild(el("td", { class: "id", text: c[k] }));
        else if (OV_KEYS.indexOf(k) >= 0) tr.appendChild(el("td", null, c.overlays[k].length ? c.overlays[k].map(function (r) { return pill(r); }) : [el("span", { class: "muted", text: "—" })]));
        else tr.appendChild(el("td", { class: FW_KEYS.indexOf(k) >= 0 ? "ref" : "", text: c[k] || "—" }));
      });
      body.appendChild(tr);
    });
    $("#iso-meta").textContent = rows.length + " of " + X.controls.length + " controls" + (filters.domain ? " · " + filters.domain : "") + (filters.q ? " · “" + filters.q + "”" : "");
  }
  function renderIsoColumns() {
    var box = $("#iso-columns"); Array.from(box.querySelectorAll("label")).forEach(function (l) { l.remove(); });
    FW_KEYS.concat(OV_KEYS).forEach(function (k) {
      var cb = el("input", { type: "checkbox" }); cb.checked = !!filters.cols[k];
      cb.addEventListener("change", function () { filters.cols[k] = cb.checked; renderIso(); });
      box.appendChild(el("label", { class: "check" }, [cb, X.frameworks[k] ? X.frameworks[k].header : X.overlays[k].label]));
    });
  }
  function exportIso() {
    var cols = isoColumns();
    var lines = [cols.map(function (c) { return c[1]; }).join(",")];
    isoRows().forEach(function (c) { lines.push(cols.map(function (col) { var k = col[0]; return cell(OV_KEYS.indexOf(k) >= 0 ? c.overlays[k].join("; ") : c[k]); }).join(",")); });
    download("crosswalk-view.csv", lines.join("\n")); say("CSV exported: " + isoRows().length + " rows.");
  }

  /* ---------- From a framework ---------- */
  function identifiers(fw) {
    if (OV_KEYS.indexOf(fw) >= 0) return X.overlayItems[fw].map(function (it) { return { id: it.ref, label: it.ref + " · " + it.title, item: it }; });
    var seen = {}, out = [];
    X.controls.forEach(function (c) { var v = c[fw]; if (!v) return; v.split(/\s*[;,]\s*/).forEach(function (id) { if (id && !seen[id]) { seen[id] = true; out.push({ id: id, label: id }); } }); });
    return out.sort(function (a, b) { return a.id.localeCompare(b.id, undefined, { numeric: true }); });
  }
  function controlsFor(fw, id, item) {
    if (item) return item.iso27001_2022.map(function (r) { return byIso[r]; }).filter(Boolean);
    return X.controls.filter(function (c) { return c[fw] && c[fw].split(/\s*[;,]\s*/).indexOf(id) >= 0; });
  }
  function renderFrom() {
    var fw = $("#from-fw").value, id = $("#from-id").value, box = $("#from-result"); box.textContent = "";
    if (!fw || !id) { box.appendChild(el("p", { class: "muted", text: "Pick a framework and an identifier." })); return; }
    var ids = identifiers(fw), sel = ids.filter(function (x) { return x.id === id; })[0], ctrls = controlsFor(fw, id, sel && sel.item);
    var title = (X.frameworks[fw] ? X.frameworks[fw].header : X.overlays[fw].label) + " " + id + (sel && sel.item ? " · " + sel.item.title : "");
    box.appendChild(el("h3", { text: title }));
    if (sel && sel.item) {
      var it = sel.item, meta = [];
      if (it.group) meta.push(it.group); if (it.priority) meta.push("Priority " + it.priority); if (it.articles) meta.push("Articles " + it.articles);
      box.appendChild(el("p", { class: "muted" }, [meta.join(" · ") + " ", pill(it.confidence, it.confidence), " ", pill(it.verification, it.verification)]));
      if (it.iso27001_clauses.length) box.appendChild(el("p", { class: "muted", text: "ISMS clauses: " + it.iso27001_clauses.join(", ") }));
      if (it.notes) box.appendChild(el("p", { text: it.notes }));
    }
    if (!ctrls.length) { box.appendChild(el("p", { class: "muted", text: "No Annex A control is mapped to this identifier (it may rely on ISMS clauses only)." })); return; }
    var cols = [["iso27001_2022", "ISO 27001:2022"], ["iso27001_title", "Control"]].concat(FW_KEYS.filter(function (k) { return k !== fw; }).map(function (k) { return [k, X.frameworks[k].header]; }));
    var t = el("table", null, [el("thead", null, [el("tr", null, cols.map(function (c) { return el("th", { scope: "col", text: c[1] }); }).concat([el("th", { scope: "col", text: "Overlays" })]))])]);
    var tb = el("tbody");
    ctrls.forEach(function (c) {
      var tr = el("tr", null, cols.map(function (col) { return col[0] === "iso27001_2022" ? el("td", null, [isoLink(c.iso27001_2022)]) : el("td", { class: FW_KEYS.indexOf(col[0]) >= 0 ? "ref" : "", text: c[col[0]] || "—" }); }));
      var ov = []; OV_KEYS.forEach(function (k) { if (k !== fw && c.overlays[k].length) ov.push(X.overlays[k].label + ": " + c.overlays[k].join(", ")); });
      tr.appendChild(el("td", { class: "muted", text: ov.join(" · ") || "—" })); tb.appendChild(tr);
    });
    t.appendChild(tb); box.appendChild(el("div", { class: "table-wrap" }, [t]));
    box.appendChild(el("p", { class: "muted", text: ctrls.length + " ISO 27001 control(s). Each target cell holds the single closest equivalent; real relationships are many-to-many." }));
  }
  function fillFromIds() {
    var fw = $("#from-fw").value, s = $("#from-id"), q = $("#from-search").value.trim().toLowerCase(); s.textContent = "";
    var ids = identifiers(fw).filter(function (x) { return !q || x.label.toLowerCase().indexOf(q) >= 0; });
    s.appendChild(el("option", { value: "", text: ids.length + " identifier(s)" }));
    ids.forEach(function (x) { s.appendChild(el("option", { value: x.id, text: x.label })); });
    if (ids.length === 1) { s.value = ids[0].id; }
    renderFrom();
  }

  /* ---------- Overlays ---------- */
  function renderOverlay() {
    var k = $("#ov-select").value, meta = X.overlays[k], q = $("#ov-search").value.trim().toLowerCase();
    var head = $("#ov-head"), body = $("#ov-body"); head.textContent = ""; body.textContent = "";
    var extra = meta.extra || [];
    var cols = ["Ref", "Title", "Group"].concat(extra.map(function (e) { return e.charAt(0).toUpperCase() + e.slice(1); })).concat(["ISO 27001 controls", "ISMS clauses", "Confidence", "Verification", "Notes"]);
    cols.forEach(function (c) { head.appendChild(el("th", { scope: "col", text: c })); });
    var items = X.overlayItems[k].filter(function (it) { return !q || [it.ref, it.title, it.group, it.notes, it.iso27001_2022.join(" "), it.iso27001_2022.map(function (r) { return byIso[r] ? byIso[r].iso27001_title : ""; }).join(" ")].join(" ").toLowerCase().indexOf(q) >= 0; });
    items.forEach(function (it) {
      var tr = el("tr", null, [el("td", { class: "id", text: it.ref }), el("td", { text: it.title }), el("td", { class: "muted", text: it.group })]);
      extra.forEach(function (e) { tr.appendChild(el("td", { text: it[e] || "—" })); });
      tr.appendChild(el("td", null, it.iso27001_2022.length ? it.iso27001_2022.map(isoLink) : [el("span", { class: "muted", text: "—" })]));
      tr.appendChild(el("td", { class: "muted", text: it.iso27001_clauses.join(", ") || "—" }));
      tr.appendChild(el("td", null, [pill(it.confidence, it.confidence)])); tr.appendChild(el("td", null, [pill(it.verification, it.verification)]));
      tr.appendChild(el("td", { class: "muted", text: it.notes })); body.appendChild(tr);
    });
    $("#ov-meta").textContent = meta.name + " · " + meta.edition + " · " + meta.granularity + " · " + items.length + " of " + X.overlayItems[k].length + " items";
  }
  function exportOverlay() {
    var k = $("#ov-select").value, extra = X.overlays[k].extra || [];
    var lines = [["ref", "title", "group"].concat(extra).concat(["iso27001_2022", "iso27001_clauses", "confidence", "verification", "notes"]).join(",")];
    X.overlayItems[k].forEach(function (it) { lines.push([it.ref, it.title, it.group].concat(extra.map(function (e) { return it[e]; })).concat([it.iso27001_2022.join("; "), it.iso27001_clauses.join("; "), it.confidence, it.verification, it.notes]).map(cell).join(",")); });
    download(k + "-overlay.csv", lines.join("\n")); say("CSV exported.");
  }

  /* ---------- Coverage ---------- */
  function bar(label, n, d, suffix) {
    var p = d ? Math.round((n / d) * 100) : 0, fill = el("div", { class: "fill" }); fill.style.width = p + "%";
    return el("div", { class: "bar" }, [el("span", { text: label }), el("div", { class: "track", role: "img", "aria-label": label + " " + p + "%" }, [fill]), el("span", { class: "pct", text: n + "/" + d + (suffix || "") })]);
  }
  function renderCoverage() {
    var fw = $("#cov-fw"), ov = $("#cov-ov"), dm = $("#cov-dom"); fw.textContent = ""; ov.textContent = ""; dm.textContent = "";
    FW_KEYS.forEach(function (k) { fw.appendChild(bar(X.frameworks[k].header + " (" + identifiers(k).length + " identifiers)", X.controls.filter(function (c) { return c[k]; }).length, X.controls.length)); });
    OV_KEYS.forEach(function (k) { var items = X.overlayItems[k], high = items.filter(function (i) { return i.confidence === "high"; }).length; ov.appendChild(bar(X.overlays[k].label + " · " + high + " high, " + (items.length - high) + " medium", items.filter(function (i) { return i.iso27001_2022.length; }).length, items.length, " with Annex A controls")); });
    domains.forEach(function (d) { dm.appendChild(bar(d, X.controls.filter(function (c) { return c.domain === d; }).length, X.controls.length)); });
  }

  /* ---------- theme / init ---------- */
  function applyTheme(t) { if (t) document.documentElement.setAttribute("data-theme", t); else document.documentElement.removeAttribute("data-theme"); var dark = t === "dark" || (!t && window.matchMedia("(prefers-color-scheme: dark)").matches); $("#theme-toggle").textContent = dark ? "Light theme" : "Dark theme"; $("#theme-toggle").setAttribute("aria-pressed", String(dark)); }
  function init() {
    var kp = $("#kpis"), total = OV_KEYS.reduce(function (n, k) { return n + X.overlayItems[k].length; }, 0);
    [["ISO 27001 controls", String(X.controls.length), "Annex A, 2022"], ["Target frameworks", String(FW_KEYS.length), FW_KEYS.map(function (k) { return X.frameworks[k].header; }).join(" · ")], ["Overlays", String(OV_KEYS.length), OV_KEYS.map(function (k) { return X.overlays[k].label; }).join(" · ")], ["Overlay items", String(total), "mapped to Annex A controls and ISMS clauses"]]
      .forEach(function (k) { kp.appendChild(el("div", { class: "kpi" }, [el("small", { text: k[0] }), el("b", { text: k[1] }), el("small", { text: k[2] })])); });
    domains.forEach(function (d) { $("#iso-domain").appendChild(el("option", { value: d, text: d })); });
    renderIsoColumns(); renderIso();
    $("#iso-search").addEventListener("input", function (e) { filters.q = e.target.value.trim().toLowerCase(); renderIso(); });
    $("#iso-domain").addEventListener("change", function (e) { filters.domain = e.target.value; renderIso(); });
    $("#iso-export").addEventListener("click", exportIso);
    var ffw = $("#from-fw");
    FW_KEYS.forEach(function (k) { ffw.appendChild(el("option", { value: k, text: X.frameworks[k].header })); });
    OV_KEYS.forEach(function (k) { ffw.appendChild(el("option", { value: k, text: X.overlays[k].label + " (overlay)" })); });
    ffw.addEventListener("change", function () { $("#from-search").value = ""; fillFromIds(); });
    $("#from-id").addEventListener("change", renderFrom); $("#from-search").addEventListener("input", fillFromIds);
    fillFromIds();
    var ovs = $("#ov-select"); OV_KEYS.forEach(function (k) { ovs.appendChild(el("option", { value: k, text: X.overlays[k].label + " · " + X.overlays[k].name })); });
    ovs.addEventListener("change", renderOverlay); $("#ov-search").addEventListener("input", renderOverlay); $("#ov-export").addEventListener("click", exportOverlay);
    renderOverlay(); renderCoverage();
    document.querySelectorAll('[role="tab"]').forEach(function (t) { t.addEventListener("click", function () { showTab(t.id); }); });
    $("#btn-print").addEventListener("click", function () { window.print(); });
    var saved = null; try { saved = localStorage.getItem("crosswalk-theme"); } catch (e) { /* ignore */ }
    applyTheme(saved);
    $("#theme-toggle").addEventListener("click", function () { var cur = document.documentElement.getAttribute("data-theme"); var dark = cur === "dark" || (!cur && window.matchMedia("(prefers-color-scheme: dark)").matches); var next = dark ? "light" : "dark"; try { localStorage.setItem("crosswalk-theme", next); } catch (e) { /* ignore */ } applyTheme(next); });
    var m = /[?&]q=([^&]+)/.exec(location.search); if (m) { $("#iso-search").value = decodeURIComponent(m[1]); filters.q = $("#iso-search").value.toLowerCase(); renderIso(); }
  }
  document.addEventListener("DOMContentLoaded", init);
})();
