PY ?= python3

.PHONY: setup build run test verify experiment

setup:
	@test -f .env || cp .env.example .env
	@echo "B안: 설치할 패키지 없음 (표준 라이브러리 + 바닐라 JS)"

build:
	@echo "B안: 빌드 단계 없음 (frontend/ 파일을 서버가 그대로 제공)"

run:
	cd backend && $(PY) -m app

test:
	cd backend && $(PY) -m unittest discover -s tests -t .
	@for f in $$(find frontend/src -name '*.js'); do node --check "$$f" || exit 1; done && echo "frontend: node --check OK"

verify: test
	@if command -v docker >/dev/null 2>&1; then docker build -t app-local . ; else echo "docker: NOT_RUN (not installed)"; fi

experiment:
	cd backend && $(PY) scripts/experiment.py
