#!/usr/bin/env python3
"""Evidence runner: run a check command, save the log, append a V entry to LOG.md.

usage:
  python3 /tmp/dn/tools/ev.py "pytest -q" --claim "핵심 계산이 손계산과 일치" [--src "src/calc.py:12"] [--log LOG.md]
  python3 /tmp/dn/tools/ev.py --demo

- Status is PASS only when the command exits 0. Otherwise FAIL.
- Records time, git commit (and whether the tree was dirty), command, exit code, log path.
- Output tail goes to outputs/logs/V<n>.log. Secrets are not printed by this tool; do not pass them in the command.
"""
import argparse, os, re, subprocess, sys, tempfile, datetime


def git(*args, cwd="."):
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def next_id(log_path):
    if not os.path.exists(log_path):
        return 1
    ids = [int(m) for m in re.findall(r"^## V(\d+)\.", open(log_path, encoding="utf-8").read(), re.M)]
    return max(ids) + 1 if ids else 1


def run(cmd, claim, src, log_path, timeout, cwd="."):
    os.makedirs(os.path.join(cwd, "outputs", "logs"), exist_ok=True)
    lp = os.path.join(cwd, log_path)
    vid = next_id(lp)
    commit = git("rev-parse", "--short", "HEAD", cwd=cwd) or "no-git"
    dirty = bool(git("status", "--porcelain", cwd=cwd))
    t0 = datetime.datetime.now()
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        code, out = p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired as e:
        code, out = 124, f"TIMEOUT after {timeout}s\n{e.stdout or ''}"
    secs = (datetime.datetime.now() - t0).total_seconds()
    status = "PASS" if code == 0 else "FAIL"
    rel_log = os.path.join("outputs", "logs", f"V{vid}.log")
    with open(os.path.join(cwd, rel_log), "w", encoding="utf-8") as f:
        f.write(f"# V{vid} {status}\ncmd: {cmd}\ncommit: {commit}{' (dirty)' if dirty else ''}\n"
                f"time: {t0:%Y-%m-%d %H:%M:%S} ({secs:.1f}s)\nexit: {code}\n\n{out}")
    tail = [l for l in out.strip().splitlines() if l.strip()][-1:] or ["(no output)"]
    entry = (f"\n## V{vid}. {claim}\n- 상태: {status} (exit {code}, {secs:.1f}s)\n- 방법: `{cmd}`\n"
             f"- 근거: {rel_log}, commit {commit}{' (커밋 안 된 변경 있음)' if dirty else ''}"
             f"{', ' + src if src else ''}\n- 마지막 출력: {tail[0][:160]}\n")
    with open(lp, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())
    if dirty:
        print("※ 커밋 안 된 변경이 있습니다. 증거로 쓰려면 커밋 후 다시 실행하세요.")
    return code


def demo():
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q"], cwd=d)
    assert run("python3 -c \"print(2+2)\"", "덧셈 확인", "", "LOG.md", 30, cwd=d) == 0
    assert run("python3 -c \"import sys; sys.exit(3)\"", "실패 기록 확인", "", "LOG.md", 30, cwd=d) == 3
    log = open(os.path.join(d, "LOG.md"), encoding="utf-8").read()
    assert "## V1. 덧셈 확인" in log and "PASS" in log and "## V2." in log and "FAIL" in log
    assert os.path.exists(os.path.join(d, "outputs", "logs", "V2.log"))
    print("\nDEMO OK:", d)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?")
    ap.add_argument("--claim", default="")
    ap.add_argument("--src", default="")
    ap.add_argument("--log", default="LOG.md")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.demo:
        demo(); sys.exit(0)
    if not a.cmd or not a.claim:
        ap.error("cmd and --claim are required")
    sys.exit(run(a.cmd, a.claim, a.src, a.log, a.timeout))
