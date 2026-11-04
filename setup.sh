#!/usr/bin/env bash
# usage: END=13:00 bash /tmp/dn/setup.sh [workspace]   (END = 과제 종료 시각, 없으면 지금+180분)
# kit stays in /tmp/dn (outside the workspace). Never overwrites existing PLAN.md / docs files.
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$PWD}"
[ -d "$WORK" ] || { echo "workspace not found: $WORK  (check with pwd)"; exit 1; }
[ "$KIT" = "/tmp/dn" ] || echo "WARNING: kit is at $KIT, docs assume /tmp/dn"
[ -e "$WORK/README.md" ] || echo "WARNING: no README.md in $WORK -- is this the task folder? (ls / pwd)"

# 1) skills -> ~/.agents/skills (old dn-* removed first)
mkdir -p "$HOME/.agents/skills"
rm -rf "$HOME"/.agents/skills/dn-*
for d in "$KIT"/.agents/skills/*/; do
  n="$(basename "$d")"; cp -r "$d" "$HOME/.agents/skills/$n"; echo "skill: $n"
done

# 2) times (G gates from END)
END="${END:-}"
read -r T_END T_G1 T_G2 T_G3 T_HALF T_G4 T_COMMIT T_G5 T_SUB < <(python3 - "$END" <<'PY'
import sys, datetime as dt
now = dt.datetime.now().replace(second=0, microsecond=0)
a = sys.argv[1]
end = now + dt.timedelta(minutes=180)
if a:
    h, m = map(int, a.split(":")); end = now.replace(hour=h, minute=m)
    if end < now: end += dt.timedelta(days=1)
start = end - dt.timedelta(minutes=180)
f = lambda mins: (start + dt.timedelta(minutes=mins)).strftime("%H:%M")
print(end.strftime("%H:%M"), f(25), f(45), f(75), f(90), f(125), f(160), f(165), f(170))
PY
)
TIMES="종료 $T_END, G1 $T_G1, G2 $T_G2, G3 첫 완주 $T_G3, 과제 스킬 생성 마감 $T_HALF, G4 기능 동결 $T_G4, 최종 커밋 $T_COMMIT, G5 $T_G5, 제출 시작 $T_SUB."

# 3) rules + plan + docs templates (no overwrite)
if [ -e "$WORK/AGENTS.md" ] && ! cmp -s "$KIT/AGENTS.md" "$WORK/AGENTS.md"; then
  cp "$KIT/AGENTS.md" "$WORK/AGENTS.kit.md"; RULES="AGENTS.md(과제)와 AGENTS.kit.md(내 지침) 둘 다 읽고 세션 지침으로 써. 과제 쪽이 우선이고 과제 AGENTS.md는 수정하지 마."
  echo "AGENTS.md already exists -> kit rules saved as AGENTS.kit.md"
else
  cp "$KIT/AGENTS.md" "$WORK/AGENTS.md"; RULES="AGENTS.md 읽고 세션 지침으로 써."; echo "rules: $WORK/AGENTS.md"
fi
[ -e "$WORK/PLAN.md" ] || { cp "$KIT/templates/PLAN.md" "$WORK/PLAN.md"; echo "plan: PLAN.md"; }
mkdir -p "$WORK/docs/evidence"
for f in "$KIT"/templates/docs/*.md; do n="$(basename "$f")"; [ -e "$WORK/docs/$n" ] || cp "$f" "$WORK/docs/$n"; done
echo "docs: docs/01~08, LOG.md, evidence/"
[ -e "$WORK/docs/evidence/.gitkeep" ] || touch "$WORK/docs/evidence/.gitkeep"

# 4) git: local exclude for kit/platform folders, local author if missing
if git -C "$WORK" rev-parse --git-dir >/dev/null 2>&1; then
  EX="$(git -C "$WORK" rev-parse --git-path info/exclude)"; case "$EX" in /*) ;; *) EX="$WORK/$EX";; esac
  mkdir -p "$(dirname "$EX")"; touch "$EX"
  for p in ".agents/" ".codex/" "AGENTS.kit.md" "docs/evidence/.ev.lock"; do grep -qxF "$p" "$EX" || echo "$p" >> "$EX"; done
  git -C "$WORK" config user.name >/dev/null 2>&1 || git -C "$WORK" config user.name "Codex"
  git -C "$WORK" config user.email >/dev/null 2>&1 || git -C "$WORK" config user.email "codex@localhost"
  echo "git: local exclude set; author = $(git -C "$WORK" config user.name)"
fi

# 5) sub-agents only into a non-HOME project folder
if [ "$(cd "$WORK" && pwd)" = "$(cd "$HOME" && pwd)" ]; then
  echo "agents: workspace is HOME -> not copied (~/.codex is platform config). 서브에이전트는 말로: '/tmp/dn/.codex/agents/verifier.toml 지침대로 …'"
else
  mkdir -p "$WORK/.codex/agents"
  for f in "$KIT"/.codex/agents/*.toml; do n="$(basename "$f")"; [ -e "$WORK/.codex/agents/$n" ] || cp "$f" "$WORK/.codex/agents/$n"; done
fi

echo "tools test: for t in ev profile joincheck mask schemacheck langcheck; do python3 /tmp/dn/tools/\$t.py --demo >/dev/null 2>&1 && echo \"\$t OK\" || echo \"\$t FAIL\"; done"
echo
echo "================ 창 A(메인)에 복사 ================"
echo "$RULES $TIMES \$dn-kickoff 로 시작하고 아직 구현하지 마."
echo "================ 창 B(보조)에 복사 ================"
echo "너는 창 B(보조)야. $RULES 쓰기는 docs/와 backend/scripts/만, git과 앱 코드 수정은 하지 마. 지금 할 일: README와 데이터 설명을 읽고 \$dn-interview 1차 질문 초안 5개를 docs/03_interview.md에 써. $TIMES"
echo "================ 창 C(화면)는 G2 이후 ================"
echo "너는 창 C(화면)야. $RULES frontend/AGENTS.md도 읽어. 쓰기는 frontend/만, git 금지. docs/05_design.md의 화면 명세와 API 계약대로 \$dn-ui 로 구현해."
echo "==================================================="
echo "(시각이 틀리면: END=종료시각 bash /tmp/dn/setup.sh)"
