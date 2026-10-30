#!/usr/bin/env bash
# usage: bash /tmp/dn/setup.sh [workspace]   (default: current folder). Kit stays in /tmp/dn, outside the workspace.
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$PWD}"
[ -d "$WORK" ] || { echo "workspace not found: $WORK  (check with pwd)"; exit 1; }
[ "$KIT" = "/tmp/dn" ] || echo "WARNING: kit is at $KIT, docs assume /tmp/dn (re-clone: git clone <url> /tmp/dn)"
[ -e "$WORK/README.md" ] || echo "WARNING: no README.md in $WORK -- is this the task folder? (ls / pwd)"

mkdir -p "$HOME/.agents/skills"
for d in "$KIT"/.agents/skills/*/; do
  n="$(basename "$d")"
  rm -rf "$HOME/.agents/skills/$n"
  cp -r "$d" "$HOME/.agents/skills/$n"
  echo "skill: $n"
done

FIRST="AGENTS.md 읽고 세션 지침으로 써. 종료 13:00, 첫 완주 11:05, 제출 시작 12:50. \$dn-kickoff 로 시작하고 아직 구현하지 마."
if [ -e "$WORK/AGENTS.md" ]; then
  cp "$KIT/AGENTS.md" "$WORK/AGENTS.kit.md"
  echo "AGENTS.md already exists -> saved kit rules as AGENTS.kit.md"
  FIRST="AGENTS.md(과제)와 AGENTS.kit.md(내 지침) 둘 다 읽고 세션 지침으로 써. 과제 쪽이 우선이고 과제 AGENTS.md는 수정하지 마. 종료 13:00, 첫 완주 11:05, 제출 시작 12:50. \$dn-kickoff 로 시작하고 아직 구현하지 마."
else
  cp "$KIT/AGENTS.md" "$WORK/AGENTS.md"
  echo "rules: $WORK/AGENTS.md"
fi

# keep kit/platform folders out of the task repo (local exclude only, tracked files untouched)
if git -C "$WORK" rev-parse --git-dir >/dev/null 2>&1; then
  EX="$(git -C "$WORK" rev-parse --git-path info/exclude)"; case "$EX" in /*) ;; *) EX="$WORK/$EX";; esac
  mkdir -p "$(dirname "$EX")"; touch "$EX"
  for p in ".agents/" ".codex/" "AGENTS.kit.md"; do grep -qxF "$p" "$EX" || echo "$p" >> "$EX"; done
  echo "git: added .agents/ .codex/ AGENTS.kit.md to local exclude ($EX)"
fi

# sub-agents: only into a project folder, never into ~/.codex (platform config)
if [ "$(cd "$WORK" && pwd)" = "$(cd "$HOME" && pwd)" ]; then
  echo "agents: workspace is HOME -> not copied (~/.codex is platform config). use: new terminal + codex + '/tmp/dn/.codex/agents/verifier.toml 지침대로 검증해'"
else
  mkdir -p "$WORK/.codex/agents"
  for f in "$KIT"/.codex/agents/*.toml; do
    n="$(basename "$f")"
    if [ -e "$WORK/.codex/agents/$n" ]; then echo "agent $n exists -> skipped"
    else cp "$f" "$WORK/.codex/agents/$n"; echo "agent: ${n%.toml} (trusted folder only)"; fi
  done
fi
echo "tools test: for t in ev profile joincheck mask; do python3 /tmp/dn/tools/\$t.py --demo >/dev/null 2>&1 && echo \"\$t OK\" || echo \"\$t FAIL\"; done"
echo "done. start codex in this folder, then /skills (or \$dn-kickoff)."
echo
echo "================ copy the line below into codex ================"
echo "$FIRST"
echo "================================================================"
echo "(시작이 10:10보다 늦었으면 시각을 다시 계산: CARD 2절)"
