#!/usr/bin/env bash
# environment check (read-only, prints no secret values)
# 사전 체험 전용. 당일 작업 중에는 돌리지 않는다 (외부 저장소 조회·다운로드 시도가 포함됨)
sec(){ printf '\n===== %s =====\n' "$1"; }

sec "1. location / git"
pwd; ls -la
git status 2>&1 | head -3
git log --oneline 2>&1 | head -5

sec "2. runtime / resources / time"
node -v 2>&1; npm -v 2>&1; python3 -V 2>&1; git --version
echo "cpu: $(nproc)"; free -h; df -h ~ | tail -1; date

sec "3. preinstalled python packages"
pip list 2>/dev/null | grep -iE "pandas|numpy|fastapi|flask|streamlit|pytest|uvicorn|plotly|scikit|sqlalchemy|pydantic" || echo "(none matched)"

sec "4. tools"
for t in rg jq sqlite3 uv pipx docker codex; do printf '%-8s %s\n' "$t" "$(command -v $t || echo '-')"; done
command -v codex >/dev/null && codex --version 2>&1 | head -1

sec "5. codex / agents config"
ls -a ~/.codex ~/.agents 2>/dev/null
[ -f ~/.codex/config.toml ] && grep -vEi "key|token|secret|password" ~/.codex/config.toml | head -40

sec "6. env var NAMES only (no values)"
env | cut -d= -f1 | grep -iE "proxy|codex|openai|port|host|sandbox" | sort

sec "7. network"
git ls-remote https://github.com/obra/superpowers HEAD >/dev/null 2>&1 && echo "GH_OK" || echo "GH_FAIL"
npm view express version >/dev/null 2>&1 && echo "NPM_OK" || echo "NPM_FAIL"
pip download --no-deps -q -d /tmp/_pipchk six >/dev/null 2>&1 && echo "PIP_OK" || echo "PIP_FAIL"
python3 -m venv /tmp/_venvchk >/dev/null 2>&1 && echo "VENV_OK" || echo "VENV_FAIL"

sec "8. git identity (commit needs this)"
echo "user.name : $(git config --global user.name || echo '(not set)')"
echo "user.email: $(git config --global user.email || echo '(not set)')"

sec "9. os / sudo / shell / locale"
head -2 /etc/os-release 2>/dev/null; echo "shell: $SHELL"; whoami
sudo -n true 2>/dev/null && echo "SUDO_OK" || echo "SUDO_NO"
locale 2>/dev/null | grep -E "LANG|LC_ALL" ; python3 -c "print('korean test: 한글 출력')"

sec "10. pip install possible? (dry-run, installs nothing)"
pip install --dry-run -q six >/dev/null 2>&1 && echo "PIP_INSTALL_OK" \
  || { pip install --dry-run -q --break-system-packages six >/dev/null 2>&1 && echo "PIP_INSTALL_NEEDS --break-system-packages" || echo "PIP_INSTALL_FAIL"; }
npm ls -g --depth=0 2>/dev/null | head -15

sec "11. codex commands / preset MCP"
if command -v codex >/dev/null; then codex --help 2>&1 | head -40; echo "--- mcp list ---"; codex mcp list 2>&1 | head -20; fi

sec "done"
echo "next: run preview server ->  python3 -m http.server 8000 --bind 0.0.0.0"
