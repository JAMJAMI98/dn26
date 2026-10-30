# 당일 카드

보기: 다른 터미널에서 `less ~/dn/CARD.md` (q 종료, /단어 검색)

## 1. 시작 (10:00, 시작 절차가 끝난 뒤)
```bash
git clone https://github.com/JAMJAMI98/dn26.git ~/dn && bash ~/dn/setup.sh "$(pwd)"
codex
```
- **반드시 홈(~/dn)에 받는다.** 작업 폴더에 받으면 키트가 제출물에 섞인다.
- **과제 파일이 있는 폴더에서** 친다 (`ls`로 README가 보이는 곳). `$(pwd)`가 그 폴더라 AGENTS.md가 거기 놓이고, codex도 그 폴더에서 실행한다.
- 붙여넣기가 막히면 직접 친다. 타이핑이 길면 Codex에게 말로 시킨다:
  `https://github.com/JAMJAMI98/dn26.git 를 ~/dn 에 clone하고 bash ~/dn/setup.sh 를 현재 작업 폴더 기준으로 실행해. 작업 폴더 안에는 clone하지 마.`
- Codex 안: `/status` → `/model` → **안내받은 권장 1순위 모델** (금지 모델 쓰지 않기, 업데이트 금지)
- setup 출력에 `AGENTS.kit.md`가 보이면(과제가 AGENTS.md를 줌): 첫 입력은 setup이 찍어 준 문장을 쓴다. 고유 규칙은 `AGENTS.kit.md` 끝에 쌓인다.
- `/skills`에 dn-가 안 보이면: Codex 재시작. 그래도 없으면 `~/dn/.agents/skills/dn-kickoff/SKILL.md 읽고 따라 해줘`

## 2. 첫 입력
```
AGENTS.md 읽고 세션 지침으로 써. 종료 13:00, 첫 완주 11:05, 제출 시작 12:50. $dn-kickoff 로 시작하고 아직 구현하지 마.
```
(시작 절차가 끝난 **실제 시각**이 10:10을 넘으면 첫 입력의 시각을 다시 계산해서 친다: 종료 = 과제 시작 + 180분(현장 안내 우선), 첫 완주 = 35%, 70%에 새 기능 중단, 제출 시작 = 종료 − 10분)

## 3. 시간표 (10:00 시작 기준)
| 시각 | 단계 | 입력 |
|---|---|---|
| 10:00–10:08 | 시작 절차, 키트, /status·/model | |
| 10:08–10:30 | 파악·질문·합의 | `$dn-kickoff` → `$dn-interview` 질문을 담당자에게(내가 직접) → 답 붙여넣기 → BRIEF는 **내 말로** |
| 10:30–10:45 | 데이터 점검 | `$dn-data 원본 수정 금지` |
| ~11:05 | **첫 완주** | `PLAN.md 작업 1번만. 끝나면 확인 방법대로 확인하고 커밋해.` · 웹 화면이면 먼저 `$dn-web` |
| 11:05–12:05 | 반복 | 작업 2, 3 … 결과마다 "이 숫자 어느 파일 몇 줄? 다른 방법 안 쓴 이유?" · LLM 기능은 `$dn-llm` · 같은 절차 2번째면 `$skill-creator`로 과제 스킬 1개 |
| 12:05 (70%) | 새 기능 멈춤 | |
| 12:05–12:33 | 검증 | `$dn-verify` (+ 여유 있으면 새 터미널 리뷰 세션) |
| 12:33–12:45 | 마무리 | `$dn-wrap` |
| 12:45–12:50 | **내가 직접 읽기** | LOG.md, HANDOFF.md 핵심 5줄 |
| 12:50 | **제출 시작** | 저장 상태 확인 → 제출 → 제출 화면 확인 |
| 13:00~ | 후속 문답 | AI 없이 직접 답 |

## 4. 진행 요령
- 응답이 멈춘 것 같으면 **승인 대기인지** 먼저 본다. 같은 요청을 다시 보내지 않는다.
- 기다리는 동안: 담당자 질문, 결과 읽기, LOG.md 확인.
- AI가 틀린 걸 잡으면 바로: `LOG.md에 E 항목으로 남겨. 무엇이 틀렸고 어떻게 확인했고 어떻게 고쳤는지.`
- 대화가 길어지면: `$dn-wrap A` → 새 세션: `AGENTS.md와 HANDOFF.md 읽고 현재 상태부터 이어서 해줘.`
- Codex가 꺼졌으면 `codex resume`.
- 과제 스킬 만들기 (11:30 전까지, 10분 이내): `$skill-creator 방금 반복한 [절차]를 이 과제 전용 스킬로 .agents/skills/에 만들어. 이 과제에서 확인한 규칙과 확인 명령만 넣고, 만든 이유를 LOG.md D 항목에 남겨.` · `$skill-creator`가 없으면: `.agents/skills/<이름>/SKILL.md 를 직접 써. frontmatter는 name, description 두 줄, 본문은 절차 5~10줄.`
- 단순 작업(정리, 요약, 반복 코드)은 `/model`로 가벼운 모델에 맡기고 다시 기본 모델로.

## 4-1. 도구 (각각 --demo로 자체 점검)
- 데이터 첫 점검: `python3 ~/dn/tools/profile.py data/*.csv --out outputs/profile.md`
- 조인 매칭: `python3 ~/dn/tools/joincheck.py a.csv:열 b.csv:열 --alias b.csv:별칭열`
- 증거 남기기: `python3 ~/dn/tools/ev.py "python3 -m pytest -q" --claim "성공 기준 1 통과"`
- 민감정보 가리기: `mkdir -p app && cp ~/dn/tools/mask.py app/ && python3 app/mask.py --demo` (모듈: `from mask import mask_text, unmask_text`)
- 웹 뼈대: `cp -r ~/dn/tools/webskel app && git add app && git commit -m "chore: 웹 뼈대 복사(dn webskel)"` → 그다음 과제에 맞게 수정
- 도메인 틀: `cp ~/dn/templates/DOMAIN.md DOMAIN.md`
- 도메인 리뷰(반복 중 1회): "reviewer 서브에이전트로 PLAN.md 기준 src/ 도메인 오류 찾아줘"
- 독립 검증: "verifier 서브에이전트로 다음 항목을 원자료에서 다시 계산해: …" (안 되면 dn-verify 5절의 새 세션 리뷰)

## 5. 키트 없이 시작할 때 (clone 실패)
첫 입력을 이렇게 친다:
```
구현 전에 README와 데이터를 읽고 담당자 질문 후보, PLAN.md(문제·성공기준·범위·작업목록)를 차례로 만들고 단계마다 멈춰. 결정은 LOG.md에 D, AI 오류 수정은 E, 검증은 V로 한 줄씩. 실행 안 한 건 NOT_RUN. 핵심 숫자는 두 방법으로 계산. 서버는 0.0.0.0. push 금지, 키 출력 금지.
```

## 6. 후속 문답 답 틀 (짧은 글)
1. 결론 1줄: "저는 ○○로 했습니다." (전제가 틀렸으면 먼저 바로잡기)
2. 근거: 담당자 말, 데이터 사실, 파일명, 수치
3. 약점·위험: 어디서 틀릴 수 있나
4. 다음: 추가로 확인하거나 개선할 것
