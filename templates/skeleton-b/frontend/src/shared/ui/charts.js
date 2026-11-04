// Read-only SVG charts and grid map (no library). Same props as skeleton A (Chart.tsx, GridMap.tsx).
// LineChart: values over an ordered axis + reference lines (limits, targets) + flagged points (rule hits).
// BarChart: grouped bars per category. GridMap: rows × cols cells with a state color and point markers.
import { h } from "./dom.js";
import { fmtNumber } from "../lib/format.js";

const NS = "http://www.w3.org/2000/svg";
const W = 960, H = 320, L = 56, R = 16, T = 16, B = 40;
const PALETTE = ["var(--c-primary)", "var(--c-warn)", "var(--c-ok)", "var(--c-muted)", "var(--c-danger)"];
const TONE = { danger: "var(--c-danger)", warn: "var(--c-warn)", muted: "var(--c-muted)" };

function s(tag, attrs = {}, text) {
  const el = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) el.setAttribute(k, String(v));
  if (text !== undefined) { const t = document.createElementNS(NS, "title"); t.textContent = text; el.append(t); }
  return el;
}
function label(x, y, text, anchor = "middle", fill) {
  const el = s("text", { x, y, "text-anchor": anchor, fill });
  el.textContent = text;
  return el;
}
function range(nums, fromZero) {
  if (!nums.length) return [0, 1];
  let lo = Math.min(...nums), hi = Math.max(...nums);
  if (fromZero) { lo = Math.min(0, lo); hi = Math.max(0, hi); }
  if (lo === hi) { lo -= 1; hi += 1; }
  const pad = (hi - lo) * 0.06;
  return [fromZero && lo === 0 ? 0 : lo - pad, hi + pad];
}
function frame(title) { return s("svg", { viewBox: `0 0 ${W} ${H}`, class: "ui-graph", role: "img", "aria-label": title }); }
function yAxis(svg, lo, hi, digits) {
  const y = (v) => T + (H - T - B) * (1 - (v - lo) / (hi - lo));
  for (let i = 0; i <= 4; i++) {
    const v = lo + ((hi - lo) * i) / 4;
    svg.append(s("line", { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: "var(--c-border)" }), label(L - 6, y(v) + 4, fmtNumber(Math.abs(v) < 10 ** -digits / 2 ? 0 : v, digits), "end"));
  }
  return y;
}
function xLabels(svg, labels, x) {
  const every = Math.max(1, Math.ceil(labels.length / 10));
  labels.forEach((lab, i) => { if (i % every === 0) svg.append(label(x(i), H - B + 18, lab)); });
}
function legend(names) {
  if (names.length < 2) return null;
  return h("div", { className: "ui-row-end" }, names.map((n, i) => h("span", { className: "ui-hint" }, h("span", { style: `color:${PALETTE[i % PALETTE.length]}` }, "■"), ` ${n}`)));
}
const figure = (svg, title, names) => h("figure", { className: "ui-card" }, svg, h("figcaption", { className: "ui-hint" }, title), legend(names));

/** LineChart({labels, series:[{name, values:(number|null)[], flags?:boolean[]}], refLines:[{y,label,tone}], digits, title}) */
export function LineChart({ labels, series, refLines = [], digits = 0, title }) {
  const nums = series.flatMap((se) => se.values.filter((v) => v !== null)).concat(refLines.map((r) => r.y));
  const [lo, hi] = range(nums, false);
  const n = Math.max(1, labels.length - 1);
  const x = (i) => L + ((W - L - R) * i) / n;
  const svg = frame(title);
  const y = yAxis(svg, lo, hi, digits);
  xLabels(svg, labels, x);
  for (const r of refLines) {
    const c = TONE[r.tone ?? "muted"];
    svg.append(s("line", { x1: L, x2: W - R, y1: y(r.y), y2: y(r.y), stroke: c, "stroke-dasharray": "6 4" }), label(W - R, y(r.y) - 4, r.label, "end", c));
  }
  series.forEach((se, si) => {
    const color = PALETTE[si % PALETTE.length];
    let seg = [];
    const flush = () => { if (seg.length > 1) svg.append(s("polyline", { points: seg.join(" "), fill: "none", stroke: color, "stroke-width": 2 })); seg = []; };
    se.values.forEach((v, i) => (v === null ? flush() : seg.push(`${x(i)},${y(v)}`)));
    flush();
    se.values.forEach((v, i) => {
      if (v === null) return;
      const flag = se.flags?.[i];
      svg.append(s("circle", { cx: x(i), cy: y(v), r: flag ? 5 : 2.5, fill: flag ? "var(--c-danger)" : color }, `${labels[i] ?? i}: ${fmtNumber(v, digits)}`));
    });
  });
  return figure(svg, title, series.map((se) => se.name));
}

/** BarChart({categories, series:[{name, values:number[]}], digits, title}) */
export function BarChart({ categories, series, digits = 0, title }) {
  const [lo, hi] = range(series.flatMap((se) => se.values), true);
  const band = (W - L - R) / Math.max(1, categories.length);
  const bw = (band * 0.8) / Math.max(1, series.length);
  const svg = frame(title);
  const y = yAxis(svg, lo, hi, digits);
  xLabels(svg, categories, (i) => L + band * i + band / 2);
  series.forEach((se, si) => se.values.forEach((v, i) => {
    svg.append(s("rect", { x: L + band * i + band * 0.1 + bw * si, y: Math.min(y(v), y(0)), width: bw - 2, height: Math.abs(y(v) - y(0)), fill: PALETTE[si % PALETTE.length] },
      `${categories[i]} · ${se.name}: ${fmtNumber(v, digits)}`));
  }));
  return figure(svg, title, series.map((se) => se.name));
}

const FILL = { normal: "var(--c-surface)", ok: "#e3f4ea", warn: "#fdf1dc", danger: "#fbe3e1", blocked: "var(--c-border)", highlight: "#dfe8f5" };
const MARK = { normal: "var(--c-muted)", ok: "var(--c-ok)", warn: "var(--c-warn)", danger: "var(--c-danger)", blocked: "var(--c-muted)", highlight: "var(--c-primary)" };
const LEGEND = { normal: "기본", ok: "충족", warn: "주의", danger: "미충족", blocked: "제외", highlight: "선택" };

/** GridMap({rows, cols, cells:[{r,c,state,label}], markers:[{r,c,label}], title, legend:{state:"이름"}}) */
export function GridMap({ rows, cols, cells = [], markers = [], title, legend: names = {} }) {
  const size = Math.max(14, Math.min(48, Math.floor(900 / Math.max(rows, cols))));
  const svg = s("svg", { viewBox: `0 0 ${cols * size} ${rows * size}`, class: "ui-graph", role: "img", "aria-label": title });
  const byKey = new Map(cells.map((c) => [`${c.r},${c.c}`, c]));
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const cell = byKey.get(`${r},${c}`);
    svg.append(s("rect", { x: c * size, y: r * size, width: size, height: size, fill: FILL[cell?.state ?? "normal"], stroke: "var(--c-border)" }, cell?.label));
  }
  for (const m of markers) svg.append(s("circle", { cx: m.c * size + size / 2, cy: m.r * size + size / 2, r: size * 0.28, fill: "var(--c-primary)" }, m.label));
  const used = [...new Set(cells.map((c) => c.state ?? "normal"))];
  const all = { ...LEGEND, ...names };
  return h("figure", { className: "ui-card" }, svg, h("figcaption", { className: "ui-hint" }, title),
    h("div", { className: "ui-row-end" }, used.map((st) => h("span", { className: "ui-hint" }, h("span", { style: `color:${MARK[st]}` }, "■"), ` ${all[st]}`))));
}
