#!/usr/bin/env python3
"""민감정보 가리기 (표준 라이브러리만).

사용:
  python3 mask.py 입력.txt [--out 결과.txt] [--map map.json] [--mode tag|star] [--names 이름목록.txt]
  python3 mask.py data.csv --cols 이름,연락처 --out masked.csv     # CSV 열 단위로 가리기 (+ 텍스트 패턴)
  echo "010-1234-5678" | python3 mask.py -
  python3 mask.py --demo
모듈로:
  from mask import mask_text, unmask_text
  masked, mapping = mask_text(text)           # LLM에 masked만 보낸다
  restored = unmask_text(llm_answer, mapping) # 필요할 때만 화면에서 복원

mode=tag  : 값마다 [PHONE_1] 같은 꼬리표 (같은 값은 같은 꼬리표, 복원 가능)
mode=star : 앞뒤 일부만 남기고 * 처리 (복원 불가)
주의: 패턴 기반이라 놓치는 형식이 있다. 결과 건수를 보고, 과제 데이터로 예시를 직접 확인할 것.
"""
import argparse, csv, json, re, sys

# 순서가 중요: 긴/구체적인 패턴 먼저
PATTERNS = [
    ("RRN",   r"(?<!\d)\d{6}[- ]?[1-8]\d{6}(?!\d)"),                    # 주민·외국인등록번호
    ("CARD",  r"(?<!\d)\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}(?!\d)|(?<!\d)\d{16}(?!\d)"),
    ("EMAIL", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    ("PHONE", r"(?<!\d)01[016789][- .]?\d{3,4}[- .]?\d{4}(?!\d)"),
    ("TEL",   r"(?<!\d)0(?:2|[3-6][1-5])[- .)]?\d{3,4}[- .]?\d{4}(?!\d)"),
    ("KEY",   r"\b(?:sk|pk|api|key|token)[-_][A-Za-z0-9_\-]{16,}\b"),     # API 키 모양
    ("IP",    r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)"),
    ("ACCT",  r"(?<!\d)\d{3,6}-\d{2,6}-\d{2,7}(?:-\d{1,3})?(?!\d)"),     # 계좌 모양 (오탐 가능)
]


def _star(v):
    s = re.sub(r"\s", "", v)
    if len(s) <= 4:
        return "*" * len(v)
    return v[:2] + re.sub(r"[^\s\-.@]", "*", v[2:-2]) + v[-2:]


def mask_text(text, mode="tag", names=(), mapping=None, kinds=None):
    """text를 가리고 (masked, mapping) 반환. mapping: {꼬리표: 원래값}."""
    mapping = {} if mapping is None else mapping
    rev = {v: k for k, v in mapping.items()}
    counts = {}
    for k in mapping:
        kind = k.strip("[]").rsplit("_", 1)[0]
        counts[kind] = counts.get(kind, 0) + 1

    def repl_factory(kind):
        def repl(m):
            v = m.group(0)
            if kind == "ACCT" and (len(re.sub(r"\D", "", v)) < 10 or re.fullmatch(r"(19|20)\d\d-\d\d-\d\d", v)):
                return v  # 날짜·짧은 코드는 계좌로 보지 않음
            if mode == "star":
                return _star(v)
            if v not in rev:
                counts[kind] = counts.get(kind, 0) + 1
                tag = f"[{kind}_{counts[kind]}]"
                rev[v] = tag
                mapping[tag] = v
            return rev[v]
        return repl

    pats = list(PATTERNS)
    if names:
        pats.insert(0, ("NAME", "|".join(re.escape(n) for n in sorted(set(names), key=len, reverse=True) if n)))
    for kind, pat in pats:
        if kinds and kind not in kinds:
            continue
        text = re.sub(pat, repl_factory(kind), text)
    return text, mapping


def unmask_text(text, mapping):
    for tag in sorted(mapping, key=len, reverse=True):
        text = text.replace(tag, mapping[tag])
    return text


def summarize(mapping):
    out = {}
    for k in mapping:
        kind = k.strip("[]").rsplit("_", 1)[0]
        out[kind] = out.get(kind, 0) + 1
    return out


def mask_csv(src, dst, cols, mode, names):
    mapping = {}
    with open(src, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    head, body = rows[0], rows[1:]
    idx = [head.index(c) for c in cols if c in head]
    missing = [c for c in cols if c not in head]
    for r in body:
        for i, v in enumerate(r):
            if i in idx and v:
                if mode == "star":
                    r[i] = _star(v)
                else:
                    tag_kind = re.sub(r"\W", "", head[i]).upper() or "COL"
                    rev = {vv: kk for kk, vv in mapping.items()}
                    if v not in rev:
                        n = sum(1 for k in mapping if k.startswith(f"[{tag_kind}_")) + 1
                        rev[v] = f"[{tag_kind}_{n}]"
                        mapping[rev[v]] = v
                    r[i] = rev[v]
            else:
                r[i], mapping = mask_text(v, mode, names, mapping)
    w = open(dst, "w", newline="", encoding="utf-8") if dst else sys.stdout
    csv.writer(w).writerows([head] + body)
    if dst:
        w.close()
    return mapping, missing


def demo():
    t = ("홍길동(010-1234-5678, hong.gd@example.com) 주민 900101-1234567, "
         "카드 1234-5678-9012-3456, 사무실 02-345-6789, 서버 10.0.0.12, "
         "키 sk-abcdefghijklmnop1234, 계좌 110-123-456789. 다시 010-1234-5678.")
    m, mp = mask_text(t, names=["홍길동"])
    ok = True
    for raw in ["010-1234-5678", "hong.gd@example.com", "900101-1234567", "1234-5678-9012-3456",
                "02-345-6789", "10.0.0.12", "sk-abcdefghijklmnop1234", "110-123-456789", "홍길동"]:
        if raw in m:
            print("FAIL 남아 있음:", raw); ok = False
    if m.count("[PHONE_1]") != 2:
        print("FAIL 같은 값 같은 꼬리표"); ok = False
    if unmask_text(m, mp) != t:
        print("FAIL 복원"); ok = False
    s, _ = mask_text("lot L2309-01 wafer 12 수율 93.5% 2026-10-31 10:00 EQ-123-45")
    if s != "lot L2309-01 wafer 12 수율 93.5% 2026-10-31 10:00 EQ-123-45":
        print("FAIL 오탐:", s); ok = False
    st, _ = mask_text("010-1234-5678", mode="star")
    if "1234-5678" in st or not st.startswith("01"):
        print("FAIL star:", st); ok = False
    print(m)
    print("종류별 건수:", summarize(mp))
    print("DEMO", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="민감정보 가리기")
    ap.add_argument("src", nargs="?", help="입력 파일, '-'면 표준입력")
    ap.add_argument("--out")
    ap.add_argument("--map", help="꼬리표→원래값 JSON 저장 경로 (.gitignore에 넣을 것)")
    ap.add_argument("--mode", choices=["tag", "star"], default="tag")
    ap.add_argument("--names", help="가릴 이름 목록 파일 (한 줄에 하나)")
    ap.add_argument("--cols", help="CSV에서 통째로 가릴 열 이름, 쉼표 구분")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo:
        return demo()
    if not a.src:
        ap.error("입력 파일이 필요합니다")
    names = [l.strip() for l in open(a.names, encoding="utf-8")] if a.names else []
    if a.cols:
        mapping, missing = mask_csv(a.src, a.out, [c.strip() for c in a.cols.split(",")], a.mode, names)
        if missing:
            print("경고: 없는 열", missing, file=sys.stderr)
    else:
        text = sys.stdin.read() if a.src == "-" else open(a.src, encoding="utf-8").read()
        masked, mapping = mask_text(text, a.mode, names)
        if a.out:
            open(a.out, "w", encoding="utf-8").write(masked)
        else:
            sys.stdout.write(masked)
    if a.map:
        json.dump(mapping, open(a.map, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n가린 건수:", summarize(mapping) if a.mode == "tag" else "(star 모드: 집계 없음)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
