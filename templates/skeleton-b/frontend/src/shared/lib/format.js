// Display rules: HH:MM, units, thousands separators. Never show raw ISO strings or internal IDs to users.
export function fmtTime(iso, withDate = false) {
  const d = typeof iso === "string" ? new Date(iso) : iso;
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  if (!withDate) return `${hh}:${mm}`;
  return `${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")} ${hh}:${mm}`;
}

export function fmtNumber(n, digits = 0) {
  return n.toLocaleString("ko-KR", { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

export function fmtMinutes(min) {
  if (min < 60) return `${Math.round(min)}분`;
  const h = Math.floor(min / 60);
  const m = Math.round(min % 60);
  return m ? `${h}시간 ${m}분` : `${h}시간`;
}
