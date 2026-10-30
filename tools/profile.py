#!/usr/bin/env python3
"""Read-only CSV profiler (standard library only).

usage:
  python3 /tmp/dn/tools/profile.py data/*.csv            # summary per file
  python3 /tmp/dn/tools/profile.py data/a.csv --out outputs/profile.md
  python3 /tmp/dn/tools/profile.py --demo

Reports: rows/cols, empty rate, exact duplicate rows, key candidates,
time-like columns (format and timezone marker), numeric min/median/max with
impossible-value hints, top values of code columns, and ID notation variants
(values that collide after removing case, '-', '_', spaces and leading zeros).
"""
import argparse, csv, glob, io, os, re, statistics, sys, tempfile
from collections import Counter, defaultdict

TIME_RE = re.compile(r"^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}([ T]\d{1,2}:\d{2}(:\d{2})?(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$")
NUM_RE = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
EMPTY = {"", "na", "n/a", "nan", "null", "none", "-"}


def canon(v):
    s = re.sub(r"[\s_\-./]", "", v.upper())
    return re.sub(r"(?<=[A-Z])0+(?=\d)", "", s)


def profile(path, max_rows=200000):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        sample = f.read(4096); f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        r = csv.reader(f, dialect)
        header = next(r, [])
        rows = [row for _, row in zip(range(max_rows), r)]
    out = io.StringIO(); w = out.write
    n = len(rows)
    w(f"## {os.path.basename(path)}\n- rows: {n}{' (truncated)' if n == max_rows else ''}, cols: {len(header)}\n")
    bad = sum(1 for x in rows if len(x) != len(header))
    if bad: w(f"- ⚠ 열 개수가 헤더와 다른 행: {bad}\n")
    dup = n - len(set(map(tuple, rows)))
    w(f"- 완전 중복 행: {dup}\n")
    w("\n| 열 | 빈값% | 고유수 | 유형 | 요약 |\n|---|---|---|---|---|\n")
    for i, col in enumerate(header):
        vals = [x[i].strip() if i < len(x) else "" for x in rows]
        nonempty = [v for v in vals if v.lower() not in EMPTY]
        uniq = len(set(nonempty))
        empty_pct = 100 * (n - len(nonempty)) / n if n else 0
        nums = [float(v) for v in nonempty if NUM_RE.match(v)]
        times = [v for v in nonempty if TIME_RE.match(v)]
        if nonempty and len(times) >= 0.9 * len(nonempty):
            tz = Counter("Z" if v.endswith("Z") else ("offset" if re.search(r"[+-]\d{2}:?\d{2}$", v) else "없음") for v in times)
            kind, summ = "시간", f"{min(times)} ~ {max(times)}, 시간대표기 {dict(tz)}"
        elif nonempty and len(nums) >= 0.95 * len(nonempty):
            kind = "수치"
            neg = sum(1 for x in nums if x < 0); zero = sum(1 for x in nums if x == 0)
            summ = f"min {min(nums):g} / med {statistics.median(nums):g} / max {max(nums):g}"
            if neg: summ += f" / 음수 {neg}"
            if zero: summ += f" / 0값 {zero}"
            if len(nums) < len(nonempty): summ += f" / 비수치 {len(nonempty) - len(nums)}"
        else:
            kind = "범주/ID"
            top = Counter(nonempty).most_common(4)
            summ = ", ".join(f"{k}({c})" for k, c in top)
            groups = defaultdict(set)
            for v in set(nonempty):
                groups[canon(v)].add(v)
            variants = [sorted(g) for g in groups.values() if len(g) > 1]
            if variants:
                summ += f" / ⚠ 표기 변형 {len(variants)}그룹 예: {variants[0][:4]}"
        if n and uniq == n and empty_pct == 0:
            summ = "🔑 키 후보(전부 고유) / " + summ
        w(f"| {col} | {empty_pct:.1f} | {uniq} | {kind} | {summ[:220]} |\n")
    return out.getvalue()


def demo():
    d = tempfile.mkdtemp(); p = os.path.join(d, "t.csv")
    with open(p, "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(["id", "equip", "ts", "val"])
        cw.writerows([["1", "ETCH-02B", "2026-09-01 10:00", "3"], ["2", "etch_2b", "2026-09-01 11:00Z", "-1"],
                      ["3", "ETCH02B", "2026-09-02 09:00", ""], ["3", "ETCH02B", "2026-09-02 09:00", ""]])
    rep = profile(p); print(rep)
    assert "완전 중복 행: 1" in rep and "표기 변형" in rep and "시간대표기" in rep and "음수 1" in rep
    print("DEMO OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="*"); ap.add_argument("--out"); ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo: demo(); sys.exit(0)
    files = [g for pat in a.files for g in (glob.glob(pat) or [pat])]
    if not files: ap.error("give CSV files")
    rep = "\n".join(profile(p) for p in files)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        open(a.out, "w", encoding="utf-8").write("# 데이터 프로파일\n\n" + rep); print(f"saved: {a.out}")
    print(rep)
