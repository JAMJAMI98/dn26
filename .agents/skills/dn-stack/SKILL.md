---
name: dn-stack
description: 시작 직후 작업 폴더에 서비스 골격(폴더·서버·인증·작업·배포·테스트)을 깔 때 쓴다.
---
# 골격 적용 (+10~30분, 창 A). 도메인 코드는 0줄, 과제가 정한 것이 있으면 그것이 우선

## 0. 선택 (최대 5분, 복사 전에 정한다)
- `python3 -c "import fastapi,uvicorn"`; 없으면 `pip install fastapi "uvicorn[standard]" pydantic-settings sqlalchemy httpx pytest` (승인). `npm view vite version` (승인).
- 둘 다 되면 **A안**(FastAPI + React/TS/Vite). 하나라도 5분 안에 안 되면 **B안**(표준 라이브러리 + 바닐라 JS, 설치 0). 화면 없는 과제면 frontend 생략. 선택과 이유를 LOG D에.
- 두 골격은 **폴더 구조·API·오류 형식·인증·역할·작업 잠금·화면 부품 이름이 같다.** 그래서 이후 스킬·docs·지시는 A/B 상관없이 그대로다. 다른 것은 명령뿐: A `make setup`·`make test`(pytest + tsc), B `make test`(unittest + node --check), 빌드 없음.
- git: `git config user.name Codex; git config user.email codex@localhost`(이 저장소만). .git 쓰기 승인 창은 "세션 동안 허용".

## 1. 골격 복사 (검증된 범용 코드, 도메인 코드 0줄)
- A안: `rsync -a --ignore-existing /tmp/dn/templates/skeleton-a/ ./ 2>/dev/null || cp -rn /tmp/dn/templates/skeleton-a/. ./` → `rm -f VERIFY.md` → `make setup`
- B안: `rsync -a --ignore-existing /tmp/dn/templates/skeleton-b/ ./ 2>/dev/null || cp -rn /tmp/dn/templates/skeleton-b/. ./` → `make setup`(설치 없음, .env만 만든다)
- (과제 파일은 덮어쓰지 않는다. cp의 -n 경고 문구는 무시)
- A를 복사한 뒤 B로 바꾸게 되면(도메인 코드를 쓰기 전에만): `rm -rf backend frontend Makefile Dockerfile .dockerignore` 후 B 복사.
- `cp /tmp/dn/templates/sub/backend.AGENTS.md backend/AGENTS.md`, frontend도 같이. docs/·PLAN.md는 setup이 이미 깔았다.
- 커밋 메시지에 출처를 밝힌다: `chore: 공개 키트 골격 적용(A안|B안, 인증·작업·배포, 도메인 코드 없음)`. HOW_TO_RUN에도 한 줄(업무 로직은 이번 과제에서 작성).
- 아래 2~4절은 골격의 명세다(키트에 골격이 없을 때 이대로 만든다). 골격이 있으면 5절 완료 기준만 확인하고 커밋.

## 2. backend (A안)
- `backend/pyproject.toml`(위 의존성, pytest 설정), `app/__main__.py`(uvicorn 0.0.0.0:PORT), `app/main.py`(create_app: 라우터·오류 핸들러·보안 헤더 미들웨어·/health·`frontend/dist` 정적 서빙 + SPA 대체 경로)
- `core/config.py`: Settings(PORT=3000, DB_URL=sqlite:///runtime/app.db, 초기 계정 ID·비밀번호는 환경변수, SESSION_TTL_MIN), 필수값 없으면 이름만 출력하고 종료
- `core/security.py`: hashlib.pbkdf2_hmac + 솔트, secrets 토큰 / `core/errors.py`: AppError → `{"code","message","details"}`
- `infrastructure/db.py`: 엔진·세션·init_db(create_all)·초기 계정 시드 / `models.py`: User(id, role, pw_hash), Session(token, user_id, expires_at), Job(id, kind, status, started_at, finished_at, result_ref, error)
- `infrastructure/jobs.py`: 같은 종류 작업이 running이면 409, 백그라운드 스레드 실행, 상태 갱신
- `presentation/deps.py`: Bearer → 현재 사용자, `require_role(*roles)` / `routes/auth.py`(login·logout·me), `routes/jobs.py`(GET /api/jobs/{id})
- `app/domains/__init__.py`만 두고 비워 둔다
- tests: health 200 / 로그인·토큰 없이 401·다른 역할 403 / 작업 중복 409 / domains가 infrastructure·presentation을 import하지 않음

## 3. frontend (A안)
- Vite React TS, 의존성: react, react-dom, react-router-dom, @tanstack/react-query. 스크립트: dev, build, typecheck(tsc --noEmit)
- `shared/ui/tokens.css`(색·간격·글자 CSS 변수) + 기본 부품: Layout, Button, Card, Table, Field, Badge, ConfirmDialog, Empty·Loading·ErrorBox, Graph(SVG)
- `shared/api/client.ts`: 토큰(메모리+sessionStorage) 첨부, 401 → 로그인, 오류 형식 해석
- `app/`: Router, AuthProvider, RequireRole(미로그인 → /login, 다른 역할 → 403 화면), 역할별 첫 화면
- `pages/`: LoginPage, ForbiddenPage, 역할별 빈 홈(“데이터를 적용하세요” 같은 처음 상태)

## 4. 배포·명령
- 루트 `Dockerfile`: node:22-slim에서 frontend build → python:3.12-slim에 backend + dist, 비루트 사용자, EXPOSE 3000, HEALTHCHECK(python urllib /health), `CMD ["python","-m","app"]`(WORKDIR backend)
- `.dockerignore`는 허용 목록 방식(`*` 후 `!backend` `!frontend` `!data` …, node_modules·runtime 제외)
- `.env.example`(자리표시만), `.gitignore`(.env, runtime/, node_modules/, dist/, __pycache__/)
- `Makefile`: setup / run(frontend build → 서버) / test(pytest -q + npm run typecheck) / verify(test + docker build, docker 없으면 NOT_RUN 표시) / experiment

## 5. 완료 기준 (전부 확인 후 커밋)
`make test` PASS · 서버 0.0.0.0:3000 기동(전용 터미널, `make run`) · `curl -s localhost:3000/health` 200 · curl로 로그인 → Bearer로 /api/auth/me 200, 토큰 없이 401 · 미리보기에서 로그인 화면 보임(사용자) · docs/05에 구조도 한 단락
- 초기 비밀번호: .env의 ADMIN_PASSWORD·USER_PASSWORD를 비워 두면 `backend/runtime/initial-credentials.txt`에 생성된다. 값을 화면·로그·문서에 출력하지 않는다(사용자가 그 파일을 직접 연다).
- 20분을 넘기면 멈추고 무엇이 막혔는지 보고. B안 전환은 사용자에게 한 줄로 알리고 진행.
