PY ?= python3
PIP_FLAGS ?=

.PHONY: setup build run test verify experiment

setup:
	cd backend && $(PY) -m pip install $(PIP_FLAGS) -e ".[dev]"
	cd frontend && (npm ci || npm install)

build:
	cd frontend && npm run build

run: build
	cd backend && $(PY) -m app

test:
	cd backend && $(PY) -m pytest -q
	cd frontend && npm run typecheck

verify: test
	@if command -v docker >/dev/null 2>&1; then docker build -t app-local . ; else echo "docker: NOT_RUN (not installed)"; fi

experiment:
	cd backend && $(PY) scripts/experiment.py
