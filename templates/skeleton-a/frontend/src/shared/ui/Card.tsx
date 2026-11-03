import { ReactNode } from "react";

export function Card({ title, children }: { title?: string; children: ReactNode }) {
  return <section className="ui-card">{title && <h2>{title}</h2>}{children}</section>;
}

/** Metric card: value + unit, optional before→after comparison. */
export function MetricCard({ title, value, unit, before, hint }: {
  title: string; value: string; unit?: string; before?: string; hint?: string;
}) {
  return (
    <Card title={title}>
      <div className="ui-metric">{value}{unit && <small>{unit}</small>}</div>
      {before && <div>이전 {before}{unit ? ` ${unit}` : ""}</div>}
      {hint && <div className="ui-hint">{hint}</div>}
    </Card>
  );
}
