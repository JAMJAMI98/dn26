#!/usr/bin/env bash
# usage: bash ~/dn/setup.sh [workspace]   (run from anywhere; kit stays in ~/dn, outside workspace)
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$PWD}"
[ -d "$WORK" ] || { echo "workspace not found: $WORK  (check with pwd)"; exit 1; }

if [ "$KIT" != "$HOME/dn" ]; then
  if [ ! -e "$HOME/dn" ]; then ln -s "$KIT" "$HOME/dn" && echo "linked ~/dn -> $KIT"
  else echo "WARNING: kit is at $KIT but ~/dn exists and is different. docs assume ~/dn"; fi
fi
mkdir -p "$HOME/.agents/skills"
for d in "$KIT"/.agents/skills/*/; do
  n="$(basename "$d")"
  rm -rf "$HOME/.agents/skills/$n"
  cp -r "$d" "$HOME/.agents/skills/$n"
  echo "skill: $n"
done

if [ -e "$WORK/AGENTS.md" ]; then
  cp "$KIT/AGENTS.md" "$WORK/AGENTS.kit.md"
  echo "AGENTS.md already exists -> saved kit rules as AGENTS.kit.md"
  echo "first prompt (use this instead of the one below):"
  echo "AGENTS.md(과제)와 AGENTS.kit.md(내 지침) 둘 다 읽고 세션 지침으로 써. 과제 쪽이 우선이고 과제 AGENTS.md는 수정하지 마. 종료 13:00, 첫 완주 11:05, 제출 시작 12:50. \$dn-kickoff 로 시작하고 아직 구현하지 마."
else
  cp "$KIT/AGENTS.md" "$WORK/AGENTS.md"
  echo "rules: $WORK/AGENTS.md"
fi
mkdir -p "$WORK/.codex/agents"
if [ -e "$WORK/.codex/agents/verifier.toml" ]; then echo "verifier agent exists -> skipped"
else cp "$KIT/.codex/agents/verifier.toml" "$WORK/.codex/agents/verifier.toml"; echo "agent: verifier (works only in a trusted folder)"; fi
echo "tools: python3 ~/dn/tools/{profile,joincheck,ev,mask}.py --demo   |  web skeleton: ~/dn/tools/webskel"
echo "done. restart codex, then check skills with /skills (or \$dn-kickoff)."

echo
echo "================ copy the line below into codex ================"
echo "AGENTS.md 읽고 세션 지침으로 써. 종료 13:00, 첫 완주 11:05, 제출 시작 12:50. \$dn-kickoff 로 시작하고 아직 구현하지 마."
echo "================================================================"
echo "(시작이 10:10보다 늦었으면 시각을 다시 계산: CARD 2절)"
