// Read-only SVG graph. layout="sequence": nodes left->right in given order, wrapped into rows (no overlap).
// layout="coords": nodes placed by x/y (data coordinates) scaled into the box. Labels never show raw coordinates.
export type GraphNode = { id: string; label: string; sub?: string; x?: number; y?: number; kind?: "start" | "end" | "normal" | "highlight" };
export type GraphEdge = { from: string; to: string; label?: string };

const W = 960, ROW_H = 110, PAD = 40, PER_ROW = 6;

export function Graph({ nodes, edges, layout = "sequence" }: { nodes: GraphNode[]; edges: GraphEdge[]; layout?: "sequence" | "coords" }) {
  const pos = new Map<string, { x: number; y: number }>();
  let height = 240;
  if (layout === "sequence") {
    const step = (W - PAD * 2) / (PER_ROW - 1);
    nodes.forEach((n, i) => {
      const row = Math.floor(i / PER_ROW);
      const col = i % PER_ROW;
      const x = row % 2 === 0 ? PAD + col * step : W - PAD - col * step; // snake rows keep edges short
      pos.set(n.id, { x, y: PAD + row * ROW_H });
    });
    height = PAD * 2 + Math.max(0, Math.ceil(nodes.length / PER_ROW) - 1) * ROW_H + 20;
  } else {
    const xs = nodes.map((n) => n.x ?? 0), ys = nodes.map((n) => n.y ?? 0);
    const [minX, maxX, minY, maxY] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
    height = 520;
    nodes.forEach((n) => pos.set(n.id, {
      x: PAD + ((n.x ?? 0) - minX) / (maxX - minX || 1) * (W - PAD * 2),
      y: height - PAD - ((n.y ?? 0) - minY) / (maxY - minY || 1) * (height - PAD * 2),
    }));
  }
  const color = (k?: GraphNode["kind"]) => (k === "end" ? "var(--c-text)" : k === "highlight" ? "var(--c-warn)" : "var(--c-primary)");
  return (
    <svg className="ui-graph" viewBox={`0 0 ${W} ${height}`} role="img">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="16" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="var(--c-muted)" />
        </marker>
      </defs>
      {edges.map((e, i) => {
        const a = pos.get(e.from), b = pos.get(e.to);
        if (!a || !b) return null;
        return (
          <g key={`e${i}`}>
            <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="var(--c-muted)" strokeWidth={1.5} markerEnd="url(#arrow)" />
            {e.label && <text className="edge-label" x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 6} textAnchor="middle">{e.label}</text>}
          </g>
        );
      })}
      {nodes.map((n, i) => {
        const p = pos.get(n.id)!;
        const below = layout === "coords" && i % 2 === 1; // alternate label side to reduce overlap
        return (
          <g key={n.id}>
            <circle cx={p.x} cy={p.y} r={9} fill={color(n.kind)} />
            <text x={p.x} y={below ? p.y + 24 : p.y - 16} textAnchor="middle">{n.label}</text>
            {n.sub && <text x={p.x} y={below ? p.y + 36 : p.y + 26} textAnchor="middle" className="edge-label">{n.sub}</text>}
          </g>
        );
      })}
    </svg>
  );
}
