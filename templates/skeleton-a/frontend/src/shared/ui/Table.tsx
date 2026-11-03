import { ReactNode, useMemo, useState } from "react";

export type Column<T> = { key: string; label: string; numeric?: boolean; render?: (row: T) => ReactNode; sortValue?: (row: T) => number | string };

export function Table<T>({ columns, rows, rowKey, onRowClick }: {
  columns: Column<T>[]; rows: T[]; rowKey: (row: T) => string; onRowClick?: (row: T) => void;
}) {
  const [sort, setSort] = useState<{ key: string; asc: boolean } | null>(null);
  const sorted = useMemo(() => {
    if (!sort) return rows;
    const col = columns.find((c) => c.key === sort.key);
    if (!col?.sortValue) return rows;
    const v = col.sortValue;
    return [...rows].sort((a, b) => (v(a) < v(b) ? -1 : v(a) > v(b) ? 1 : 0) * (sort.asc ? 1 : -1));
  }, [rows, sort, columns]);
  return (
    <table className="ui-table">
      <thead>
        <tr>
          {columns.map((c) => (
            <th key={c.key} data-num={c.numeric || undefined} data-sortable={c.sortValue ? "" : undefined}
              onClick={() => c.sortValue && setSort((s) => ({ key: c.key, asc: s?.key === c.key ? !s.asc : true }))}>
              {c.label}{sort?.key === c.key ? (sort.asc ? " ▲" : " ▼") : ""}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sorted.map((r) => (
          <tr key={rowKey(r)} onClick={() => onRowClick?.(r)} style={onRowClick ? { cursor: "pointer" } : undefined}>
            {columns.map((c) => (
              <td key={c.key} data-num={c.numeric || undefined}>{c.render ? c.render(r) : String((r as unknown as Record<string, unknown>)[c.key] ?? "")}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
