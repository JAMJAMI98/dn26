# backend 규칙

## 계층 (의존 방향: presentation → domains ← infrastructure, scripts → domains)
| 계층 | 위치 | 책임 | 금지 |
|---|---|---|---|
| core | app/core/ | 설정(환경변수·기본값·시작 시 필수값 검사), 보안(비밀번호 해시·토큰), 오류 형식, 로깅 | 업무 로직 |
| domains | app/domains/<문제>/ | **순수 판단·계산**: 입력 값 → 출력 값. 규칙 검사(rules.py), 지표(metrics.py), 후보 알고리즘(solvers/ 또는 model.py) | 파일·DB·HTTP·환경변수 import |
| infrastructure | app/infrastructure/ | DB 연결·스키마 초기화, 저장소(repositories), 데이터 적재·검증·적용, 긴 작업 상태·잠금, 외부 연동 | 판단 로직 |
| presentation | app/presentation/ | API 라우터(역할별)·요청/응답 스키마, 또는 CLI | 계산·SQL |
| scripts | backend/scripts/ | 실험·독립 검증·데이터셋 생성. domains를 import | 서비스와 다른 계산 |

## 새 기능 추가 순서
domains(순수 함수 + 단위 테스트) → infrastructure(저장·적재) → presentation(라우터·스키마) → integration 테스트 → 커밋.

## 기본 동작 (골격이 보장, 바꿀 때는 이유를 LOG D에)
- 오류 응답 한 가지 형식 `{"code","message","details"}`. 422 입력 오류(파일·행·열·이유), 401 미인증, 403 권한, 404, 409 충돌(이미 실행 중 등). 내부 예외 메시지를 그대로 내보내지 않는다.
- 인증: 서버 세션(만료) + `Authorization: Bearer` 헤더. 쿠키에 의존하지 않는다(미리보기에서 쿠키가 막힐 수 있음). 권한은 라우터마다 서버에서 검사, 일반 사용자는 본인 데이터만.
- 데이터 교체가 있으면: 전체 검증 통과 후에만 트랜잭션으로 적용, 실패하면 기존 데이터·결과 그대로. 결과에는 만든 데이터 버전·설정을 저장하고, 데이터가 바뀐 뒤 재계산 전 결과는 "이전 데이터 기준"으로 표시·내보내기 차단.
- 긴 계산(수 초 이상)은 작업으로: 상태(queued/running/done/failed) 조회, 동시에 하나만(두 번째 요청 409).
- /health: DB 연결과 필수 데이터 상태, 200/503.
- 비밀값은 환경변수만. .env.example에는 자리표시만.

## 테스트
- `backend/tests/{domains,infrastructure,presentation,integration}` 계층과 같은 모양. pytest 표준 출력.
- 규칙 검사기는 규칙마다 일부러 깨뜨린 입력 1개로 잡히는지 확인. 회귀 테스트는 수정 전 실패를 먼저 본다.
- domains가 바깥 계층을 import하지 않는지 검사하는 테스트 1개를 유지한다.
