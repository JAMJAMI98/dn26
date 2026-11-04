// Read-only SVG charts (no library). Numbers are formatted for people; colors come from tokens.
// LineChart: values over an ordered axis (time, sequence) + optional horizontal reference lines (limits, targets)
//            and flagged points (e.g. rule hits). BarChart: grouped bars per category.
import { fmtNumber } from "../lib/format";

export type Series = { name: string; values: (number | null)[]; flags?: boolean[] };
export type RefLine = { y: number; label: string; tone?: "danger" | "warn" | "muted" };

const W = 960, H = 320, L = 56, R = 16, T = 16, B = 40;
const PALETTE = ["var(--c-primary)", "var(--c-warn)", "var(--c-ok)", "var(--c-muted)", "var(--c-danger)"];
const TONE = { danger: "var(--c-danger)", warn: "var(--c-warn)", muted: "var(--c-muted)" };

function range(nums: number[], fromZero: boolean): [number, number] {
  if (!nums.length) return [0, 1];
  let lo = Math.min(...nums), hi = Math.max(...nums);
  if (fromZero) { lo = Math.min(0, lo); hi = Math.max(0, hi); }
  if (lo === hi) { lo -= 1; hi += 1; }
  const pad = (hi - lo) * 0.06;
  return [fromZero && lo === 0 ? 0 : lo - pad, hi + pad];
}

function YAxis({ lo, hi, digits }: { lo: number; hi: number; digits: number }) {
  const ticks = [0, 1, 2, 3, 4].map((i) => lo + ((hi - lo) * i) / 4);
  const y = (v: number) => T + (H - T - B) * (1 - (v - lo) / (hi - lo));
  return (
    <g>
      {ticks.map((v, i) => (
        <g key={i}>
          <line x1={L} x2={W - R} y1={y(v)} y2={y(v)} stroke="var(--c-border)" />
          <text x={L - 6} y={y(v) + 4} textAnchor="end">{fmtNumber(Math.abs(v) < 10 ** -digits / 2 ? 0 : v, digits)}</text>
        </g>
      ))}
    </g>
  );
}

function XLabels({ labels, x }: { labels: string[]; x: (i: number) => number }) {
  const every = Math.max(1, Math.ceil(labels.length / 10));
  return (
    <g>
      {labels.map((lab, i) => (i % every === 0 ? <text key={i} x={x(i)} y={H - B + 18} textAnchor="middle">{lab}</text> : null))}
    </g>
  );
}

function Legend({ names }: { names: string[] }) {
  if (names.length < 2) return null;
  return (
    <div className="ui-row-end">
      {names.map((n, i) => <span key={n} className="ui-hint"><span style={{ color: PALETTE[i % PALETTE.length] }}>■</span> {n}</span>)}
    </div>
  );
}

export function LineChart({ labels, series, refLines = [], digits = 0, title }: {
  labels: string[]; series: Series[]; refLines?: RefLine[]; digits?: number; title: string;
}) {
  const nums = series.flatMap((s) => s.values.filter((v): v is number => v !== null)).concat(refLines.map((r) => r.y));
  const [lo, hi] = range(nums, false);
  const n = Math.max(1, labels.length - 1);
  const x = (i: number) => L + ((W - L - R) * i) / n;
  const y = (v: number) => T + (H - T - B) * (1 - (v - lo) / (hi - lo));
  return (
    <figure className="ui-card">
      <svg className="ui-graph" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title}>
        <YAxis lo={lo} hi={hi} digits={digits} />
        <XLabels labels={labels} x={x} />
        {refLines.map((r, i) => (
          <g key={`r${i}`}>
            <line x1={L} x2={W - R} y1={y(r.y)} y2={y(r.y)} stroke={TONE[r.tone ?? "muted"]} strokeDasharray="6 4" />
            <text x={W - R} y={y(r.y) - 4} textAnchor="end" fill={TONE[r.tone ?? "muted"]}>{r.label}</text>
          </g>
        ))}
        {series.map((s, si) => {
          const color = PALETTE[si % PALETTE.length];
          const d = s.values.map((v, i) => (v === null ? null : `${x(i)},${y(v)}`));
          const segs: string[][] = [[]];
          d.forEach((p) => (p === null ? segs.push([]) : segs[segs.length - 1].push(p)));
          return (
            <g key={s.name}>
              {segs.filter((sg) => sg.length > 1).map((sg, k) => <polyline key={k} points={sg.join(" ")} fill="none" stroke={color} strokeWidth={2} />)}
              {s.values.map((v, i) => (v === null ? null : (
                <circle key={i} cx={x(i)} cy={y(v)} r={s.flags?.[i] ? 5 : 2.5} fill={s.flags?.[i] ? "var(--c-danger)" : color}>
                  <title>{`${labels[i] ?? i}: ${fmtNumber(v, digits)}`}</title>
                </circle>
              )))}
            </g>
          );
        })}
      </svg>
      <figcaption className="ui-hint">{title}</figcaption>
      <Legend names={series.map((s) => s.name)} />
    </figure>
  );
}

export function BarChart({ categories, series, digits = 0, title }: {
  categories: string[]; series: { name: string; values: number[] }[]; digits?: number; title: string;
}) {
  const [lo, hi] = range(series.flatMap((s) => s.values), true);
  const band = (W - L - R) / Math.max(1, categories.length);
  const bw = (band * 0.8) / Math.max(1, series.length);
  const y = (v: number) => T + (H - T - B) * (1 - (v - lo) / (hi - lo));
  return (
    <figure className="ui-card">
      <svg className="ui-graph" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title}>
        <YAxis lo={lo} hi={hi} digits={digits} />
        <XLabels labels={categories} x={(i) => L + band * i + band / 2} />
        {series.map((s, si) => s.values.map((v, i) => {
          const x0 = L + band * i + band * 0.1 + bw * si;
          const top = Math.min(y(v), y(0)), h = Math.abs(y(v) - y(0));
          return (
            <rect key={`${si}-${i}`} x={x0} y={top} width={bw - 2} height={h} fill={PALETTE[si % PALETTE.length]}>
              <title>{`${categories[i]} · ${s.name}: ${fmtNumber(v, digits)}`}</title>
            </rect>
          );
        }))}
      </svg>
      <figcaption className="ui-hint">{title}</figcaption>
      <Legend names={series.map((s) => s.name)} />
    </figure>
  );
}
