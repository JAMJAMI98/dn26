# 골격 A 검증 지시 (로컬 Claude Code용)

이 폴더는 범용 서비스 골격이다(도메인 코드 0줄). 목표: 아래 완료 기준을 모두 통과시키는 것. **구조(폴더·계층·파일 역할)는 바꾸지 말고, 실패하는 부분만 최소 수정**한다. 수정한 내용은 이 파일 맨 아래 "수정 기록"에 한 줄씩 남긴다.

## 순서
1. `cp .env.example .env` 후 ADMIN_PASSWORD, USER_PASSWORD에 임의 값
2. `make setup` (Python 3.10+, Node 20+)
3. `make test` → pytest 전부 통과 + `tsc --noEmit` 오류 0
4. `make build` → frontend/dist 생성
5. 서버: `cd backend && python3 -m app` → 다른 터미널에서
   - `curl -s localhost:3000/health` → `{"status":"ok","db":true}`
   - `curl -s -X POST localhost:3000/api/auth/login -H 'Content-Type: application/json' -d '{"id":"admin","password":"<값>"}'` → token
   - `curl -s localhost:3000/api/auth/me -H "Authorization: Bearer <token>"` → 200, 토큰 없이 401
   - 브라우저 localhost:3000 → 로그인 화면 → admin 로그인 → "운영" 화면, user 로그인 → "내 정보" 화면, user로 /admin 접근 → 권한 없음 화면
6. Docker: `docker build -t app-local .` → `docker run --rm -p 3000:3000 app-local` → health 200, 비밀번호 미설정이면 컨테이너 안 `/srv/backend/runtime/initial-credentials.txt` 생성 확인
7. 동시 작업: admin 토큰으로 `POST /api/jobs/example?seconds=5`를 연달아 두 번 → 두 번째 409

## 완료 기준
- [x] make test PASS (pytest 개수, tsc 0)
- [x] make build PASS
- [x] curl 4종 기대대로
- [x] 브라우저 두 역할·403 화면
- [x] docker build·run·health
- [x] 409

## 수정 기록
- 2026-11-04: 코드 수정 없음. 전 항목 통과(pytest 11 passed, tsc 0, build, curl 4종, 브라우저 admin/user/403, docker health·initial-credentials, 409). 참고: 로컬 python3가 3.9라 `make setup PY=<3.12 venv python>`로 실행. frontend/package-lock.json 신규 생성.
