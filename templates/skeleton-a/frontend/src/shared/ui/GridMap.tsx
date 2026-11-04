// Read-only grid map (no library): rows × cols cells with a state color, optional point markers and a legend.
// Use for plans/layouts split into cells (covered vs not, zones, occupancy). Cell/marker labels must be human names.
export type CellState = "normal" | "ok" | "warn" | "danger" | "blocked" | "highlight";
export type Cell = { r: number; c: number; state?: CellState; label?: string };
export type Marker = { r: number; c: number; label: string };

const FILL: Record<CellState, string> = {
  normal: "var(--c-surface)", ok: "#e3f4ea", warn: "#fdf1dc", danger: "#fbe3e1", blocked: "var(--c-border)", highlight: "#dfe8f5",
};
const MARK: Record<CellState, string> = {
  normal: "var(--c-muted)", ok: "var(--c-ok)", warn: "var(--c-warn)", danger: "var(--c-danger)", blocked: "var(--c-muted)", highlight: "var(--c-primary)",
};
const LEGEND: Record<CellState, string> = { normal: "기본", ok: "충족", warn: "주의", danger: "미충족", blocked: "제외", highlight: "선택" };

export function GridMap({ rows, cols, cells = [], markers = [], title, legend }: {
  rows: number; cols: number; cells?: Cell[]; markers?: Marker[]; title: string; legend?: Partial<Record<CellState, string>>;
}) {
  const size = Math.max(14, Math.min(48, Math.floor(900 / Math.max(rows, cols))));
  const W = cols * size, H = rows * size;
  const byKey = new Map(cells.map((c) => [`${c.r},${c.c}`, c]));
  const used = Array.from(new Set(cells.map((c) => c.state ?? "normal")));
  const names = { ...LEGEND, ...legend };
  return (
    <figure className="ui-card">
      <svg className="ui-graph" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title}>
        {Array.from({ length: rows * cols }, (_, k) => {
          const r = Math.floor(k / cols), c = k % cols, cell = byKey.get(`${r},${c}`);
          return (
            <rect key={k} x={c * size} y={r * size} width={size} height={size} fill={FILL[cell?.state ?? "normal"]} stroke="var(--c-border)">
              {cell?.label && <title>{cell.label}</title>}
            </rect>
          );
        })}
        {markers.map((m, i) => (
          <g key={i}>
            <circle cx={m.c * size + size / 2} cy={m.r * size + size / 2} r={size * 0.28} fill="var(--c-primary)" />
            <title>{m.label}</title>
          </g>
        ))}
      </svg>
      <figcaption className="ui-hint">{title}</figcaption>
      <div className="ui-row-end">
        {used.map((s) => <span key={s} className="ui-hint"><span style={{ color: MARK[s] }}>■</span> {names[s]}</span>)}
      </div>
    </figure>
  );
}
