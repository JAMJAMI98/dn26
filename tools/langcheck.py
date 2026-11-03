#!/usr/bin/env python3
"""Find non-Korean CJK characters (Japanese kana, CJK ideographs, full-width 。) mixed into Korean docs/UI text.

usage:  python3 langcheck.py [paths...]   (default: *.md docs/ frontend/src backend/app)
        python3 langcheck.py --demo
exit:   0 clean, 1 found
Skips: node_modules, .git, dist, docs/evidence, data/provided.
"""
import os, re, sys

BAD = re.compile(r"[぀-ヿㇰ-ㇿ一-鿿。｡-ﾟ]")
EXT = {".md", ".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".json", ".txt"}
SKIP = {"node_modules", ".git", "dist", "evidence", "provided", "__pycache__", ".venv"}


def files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, dirs, fs in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP]
                for f in fs:
                    if os.path.splitext(f)[1] in EXT:
                        yield os.path.join(root, f)


def scan(paths):
    hits = []
    for f in files(paths):
        try:
            for i, line in enumerate(open(f, encoding="utf-8"), 1):
                if BAD.search(line):
                    hits.append(f"{f}:{i}: {line.strip()[:100]}")
        except (UnicodeDecodeError, OSError):
            pass
    return hits


def main(argv):
    if argv[1:2] == ["--demo"]:
        import tempfile
        d = tempfile.mkdtemp()
        open(os.path.join(d, "ok.md"), "w", encoding="utf-8").write("정상 한국어 문장입니다.\n")
        open(os.path.join(d, "bad.md"), "w", encoding="utf-8").write("요구사항を 확인했다。\n")
        h = scan([d])
        ok = len(h) == 1 and "bad.md:1" in h[0]
        print("[demo]", "PASS" if ok else f"FAIL {h}")
        return 0 if ok else 1
    paths = argv[1:] or [p for p in ["docs", "frontend/src", "backend/app"] if os.path.exists(p)] + [f for f in os.listdir(".") if f.endswith(".md")]
    hits = scan(paths)
    for h in hits[:50]:
        print(h)
    print(f"langcheck: {'PASS' if not hits else 'FAIL'} ({len(hits)} lines)")
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
