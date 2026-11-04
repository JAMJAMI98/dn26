// Basic parts (same set as skeleton A): Layout, Card, Button, Field, Table, Badge, states, ConfirmDialog, Graph.
// Colors/spacing come only from tokens.css. Business blocks go to entities/, built from these.
import { h, mount } from "./dom.js";

export function Button(label, { variant, onClick, type = "button", disabled } = {}) {
  return h("button", { className: "ui-btn", type, disabled, onClick, dataset: variant ? { variant } : undefined }, label);
}

export function Card(title, ...children) {
  return h("section", { className: "ui-card" }, title ? h("h2", {}, title) : null, ...children);
}

export function Metric(value, unit) {
  return h("div", { className: "ui-metric" }, value, unit ? h("small", {}, unit) : null);
}

export function Layout({ title, nav = [], user, onLogout }, ...children) {
  return h("div", { className: "ui-layout" },
    h("header", { className: "ui-header" },
      h("h1", {}, title),
      h("nav", { className: "ui-nav" }, nav.map((n) => h("a", { href: n.to, "data-link": true }, n.label))),
      user ? h("span", {}, user) : null,
      onLogout ? Button("로그아웃", { onClick: onLogout }) : null),
    h("main", { className: "ui-main" }, ...children));
}

/** Field({label, name, type, value, error, required, autocomplete, options}) -> label wrapper with input/select */
export function Field({ label, name, type = "text", value = "", error, required, autocomplete, options }) {
  const input = options
    ? h("select", { name, required }, options.map((o) => h("option", { value: o.value, selected: o.value === value }, o.label)))
    : h("input", { name, type, value, required, autocomplete });
  return h("label", { className: "ui-field" }, h("span", {}, label), input, error ? h("span", { className: "ui-error" }, error) : null);
}

/** Table(columns=[{key,label,num,render}], rows) — numbers right-aligned. */
export function Table(columns, rows) {
  return h("table", { className: "ui-table" },
    h("thead", {}, h("tr", {}, columns.map((c) => h("th", { "data-num": c.num ? "" : undefined }, c.label)))),
    h("tbody", {}, rows.map((r) => h("tr", {}, columns.map((c) =>
      h("td", { "data-num": c.num ? "" : undefined }, c.render ? c.render(r) : r[c.key]))))));
}

export function Badge(text, tone = "neutral") {
  return h("span", { className: "ui-badge", dataset: { tone } }, text);
}

// Four states every block shows: first(empty) / loading / error / result.
export const Empty = (message, action) => h("div", { className: "ui-state", dataset: { kind: "empty" } }, h("p", {}, message), action);
export const Loading = (message = "불러오는 중입니다…") => h("div", { className: "ui-state", role: "status", dataset: { kind: "loading" } }, message);
export const ErrorBox = (message, action) => h("div", { className: "ui-state", role: "alert", dataset: { kind: "error" } }, h("p", {}, message), action);

/** In-page confirm (never window.confirm). Resolves true/false. */
export function ConfirmDialog(message, { confirmLabel = "확인", danger = false } = {}) {
  return new Promise((resolve) => {
    const close = (v) => { overlay.remove(); resolve(v); };
    const overlay = h("div", { className: "ui-dialog-backdrop", role: "dialog", "aria-modal": "true" },
      h("div", { className: "ui-dialog" },
        h("p", {}, message),
        h("div", { className: "ui-row-end" },
          Button("취소", { onClick: () => close(false) }),
          Button(confirmLabel, { variant: danger ? "danger" : "primary", onClick: () => close(true) }))));
    document.body.append(overlay);
  });
}

/**
 * Graph({nodes:[{id,x,y,label}], edges:[{from,to,label}], width, height}) — simple SVG for node-edge diagrams.
 * Coordinates are data units; they are scaled to fit.
 */
export function Graph({ nodes, edges = [], width = 640, height = 360, pad = 24 }) {
  const NS = "http://www.w3.org/2000/svg";
  const s = (tag, attrs, text) => {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
    if (text !== undefined) el.textContent = text;
    return el;
  };
  const xs = nodes.map((n) => n.x), ys = nodes.map((n) => n.y);
  const [minX, maxX, minY, maxY] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const sx = (x) => pad + ((x - minX) / (maxX - minX || 1)) * (width - pad * 2);
  const sy = (y) => pad + ((y - minY) / (maxY - minY || 1)) * (height - pad * 2);
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const svg = s("svg", { viewBox: `0 0 ${width} ${height}`, class: "ui-graph", role: "img" });
  for (const e of edges) {
    const a = byId[e.from], b = byId[e.to];
    if (!a || !b) continue;
    svg.append(s("line", { x1: sx(a.x), y1: sy(a.y), x2: sx(b.x), y2: sy(b.y), stroke: "var(--c-border)", "stroke-width": 2 }));
  }
  for (const n of nodes) {
    svg.append(s("circle", { cx: sx(n.x), cy: sy(n.y), r: 6, fill: "var(--c-primary)" }));
    svg.append(s("text", { x: sx(n.x) + 9, y: sy(n.y) + 4 }, n.label ?? n.id));
  }
  return svg;
}

export { h, mount };
