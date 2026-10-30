#!/usr/bin/env python3
"""Join / ID-mapping checker (standard library only).

usage:
  python3 /tmp/dn/tools/joincheck.py left.csv:equip right.csv:equip_id [--alias right.csv:aliases] [--sep ";"]
  python3 /tmp/dn/tools/joincheck.py --demo

Normalizes IDs (case, '-', '_', spaces, leading zeros inside numbers), then reports:
matched / unmatched counts, unmatched examples, ambiguous mappings (one left value
-> several right keys), and the row count change a naive join would cause.
Goal: prove "unmatched = 0" (or list what is left) before using the join.
"""
import argparse, csv, re, sys, tempfile, os
from collections import Counter, defaultdict


def norm(v):
    s = re.sub(r"[\s_\-./]", "", v.strip().upper())
    return re.sub(r"(?<=[A-Z])0+(?=\d)", "", s)


def read_col(spec):
    path, col = spec.rsplit(":", 1)
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        if col not in (r.fieldnames or []):
            sys.exit(f"column '{col}' not in {path}: {r.fieldnames}")
        return [row for row in r], col


def check(left_spec, right_spec, alias_spec=None, sep=";"):
    lrows, lc = read_col(left_spec)
    rrows, rc = read_col(right_spec)
    index = defaultdict(set)
    for row in rrows:
        key = row[rc].strip()
        index[norm(key)].add(key)
        if alias_spec:
            ac = alias_spec.rsplit(":", 1)[1]
            for a in (row.get(ac) or "").split(sep):
                if a.strip():
                    index[norm(a)].add(key)
    lvals = Counter(r[lc].strip() for r in lrows)
    matched, unmatched, ambiguous = Counter(), Counter(), {}
    for v, c in lvals.items():
        keys = index.get(norm(v), set())
        if len(keys) == 1: matched[v] += c
        elif len(keys) > 1: ambiguous[v] = sorted(keys)
        else: unmatched[v] += c
    rcount = Counter(norm(r[rc]) for r in rrows)
    dup_keys = [k for k, c in rcount.items() if c > 1]
    naive_rows = sum(c * max(1, rcount.get(norm(v), 0)) for v, c in lvals.items())
    print(f"left rows: {len(lrows)}, distinct values: {len(lvals)}")
    print(f"matched rows: {sum(matched.values())}  unmatched rows: {sum(unmatched.values())}  ambiguous values: {len(ambiguous)}")
    if unmatched: print("unmatched examples:", unmatched.most_common(8))
    if ambiguous: print("ambiguous examples:", list(ambiguous.items())[:5])
    if dup_keys: print(f"⚠ right key duplicates after normalize: {dup_keys[:5]} → join will multiply rows")
    print(f"naive join row count: {len(lrows)} → {naive_rows}")
    ok = not unmatched and not ambiguous and not dup_keys
    print("RESULT:", "OK (unmatched=0, ambiguous=0)" if ok else "CHECK NEEDED")
    return 0 if ok else 1


def demo():
    d = tempfile.mkdtemp()
    L, R = os.path.join(d, "l.csv"), os.path.join(d, "r.csv")
    with open(L, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["equip"]); w.writerows([["ETCH-02B"], ["etch_2b"], ["ETCH02B"], ["DEPO-9Z"]])
    with open(R, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["equip_id", "aliases"]); w.writerows([["ETCH-02B", "E02-B"], ["DEPO-01A", ""]])
    code = check(f"{L}:equip", f"{R}:equip_id", f"{R}:aliases")
    assert code == 1  # DEPO-9Z must be reported as unmatched
    print("DEMO OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("left", nargs="?"); ap.add_argument("right", nargs="?")
    ap.add_argument("--alias"); ap.add_argument("--sep", default=";"); ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo: demo(); sys.exit(0)
    if not (a.left and a.right): ap.error("left.csv:col right.csv:col required")
    sys.exit(check(a.left, a.right, a.alias, a.sep))
