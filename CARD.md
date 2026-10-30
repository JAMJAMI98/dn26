# 당일 카드

보기: 다른 터미널에서 `less /tmp/dn/CARD.md` (q 종료, /단어 검색)

## 1. 시작 (10:00, 시작 절차가 끝난 뒤)
```bash
pwd; ls
cat ~/.codex/AGENTS.md    # 플랫폼 지침 (읽기만. 체험에서 /status의 Agents.md 항목에 이 파일이 보였다)
git clone https://github.com/JAMJAMI98/dn26.git /tmp/dn
bash /tmp/dn/setup.sh
codex
```
- 한 줄씩 치고 결과를 본다. `pwd`·`ls`로 README가 보이는 **과제 폴더**인지 먼저 확인 (체험에서는 홈 `/home/user`가 작업 폴더였다).
- 키트는 **`/tmp/dn`**(작업 폴더 밖)에 받는다. 경로에 `~`를 쓰지 않는다. 받은 키트가 작업 폴더에 보이면 잘못 받은 것.
- setup은 과제 폴더에서 친다. AGENTS.md가 거기 놓이고 codex도 그 폴더에서 켠다.
- 도구 확인(20초, 선택): `for t in ev profile joincheck mask; do python3 /tmp/dn/tools/$t.py --demo >/dev/null 2>&1 && echo "$t OK" || echo "$t FAIL"; done`
- clone은 **터미널에서 직접** 친다 (체험: 터미널 clone 성공, Codex에게 시킨 clone은 "could not read Username"으로 실패).
- clone이 Username을 물으면 주소 오타다 (저장소는 공개). `JAMJAMI98/dn26` 철자 확인 후 다시. 그래도 안 되면 CARD 5절 "키트 없이 시작"
- Codex 안: `/status` → `/model` → **안내받은 권장 1순위 모델** (금지 모델 쓰지 않기, 업데이트 금지)
- setup 출력에 `AGENTS.kit.md`가 보이면(과제가 AGENTS.md를 줌): 첫 입력은 setup이 찍어 준 문장을 쓴다. 고유 규칙은 `AGENTS.kit.md` 끝에 쌓인다.
- `/skills` → **List skills**로 dn- 7개 확인 (꺼져 있으면 **Enable/Disable skills**에서 켠다)
- `/skills`에 dn-가 안 보이면: Codex 재시작. 그래도 없으면 `/tmp/dn/.agents/skills/dn-kickoff/SKILL.md 읽고 따라 해줘`

## 2. 첫 입력 (README를 내가 먼저 읽고, 내 이해 2줄을 앞에 붙인다)
```
내 이해: (누가 무엇 때문에 곤란한지 한 줄) / (만들 것 한 줄)
AGENTS.md 읽고 세션 지침으로 써. 종료 13:00, 첫 완주 11:05, 제출 시작 12:50. $dn-kickoff 로 시작하고 아직 구현하지 마.
```
(시작 절차가 끝난 **실제 시각**이 10:10을 넘으면 첫 입력의 시각을 다시 계산해서 친다: 종료 = 과제 시작 + 180분(현장 안내 우선), 첫 완주 = 35%, 70%에 새 기능 중단, 제출 시작 = 종료 − 10분)

## 3. 시간표 (10:00 시작 기준)
| 시각 | 단계 | 입력 |
|---|---|---|
| 10:00–10:08 | 시작 절차, 키트, 보안 스킬 설치, /status·/model | |
| 10:08–10:30 | 파악·질문·합의 | `$dn-kickoff` → `$dn-interview` 질문을 담당자에게(내가 직접) → 답 붙여넣기 → BRIEF는 **내 말로** |
| 10:30–10:45 | 데이터 점검 | `$dn-data 원본 수정 금지` |
| ~11:05 | **첫 완주** | `PLAN.md 작업 1번만. 끝나면 확인 방법대로 확인하고 커밋해.` · 웹 화면이면 먼저 `$dn-web` |
| 11:05–12:05 | 반복 | 작업 2, 3 … 결과마다 "이 숫자 어느 파일 몇 줄? 다른 방법 안 쓴 이유?" · LLM 기능은 `$dn-llm` · 같은 절차 2번째면 `$skill-creator`로 과제 스킬 1개 |
| 12:05 (70%) | 새 기능 멈춤 | |
| 12:05–12:33 | 검증 | `$dn-verify` → `$security-best-practices` 1회 (+ 여유 있으면 새 터미널 리뷰 세션) |
| 12:33–12:45 | 마무리 | `$dn-wrap` |
| 12:45–12:50 | **내가 직접 읽기** | LOG.md, HANDOFF.md 핵심 5줄 |
| 12:50 | **제출 시작** | 저장 상태 확인 → 제출 → 제출 화면 확인 |
| 13:00~ | 후속 문답 | AI 없이 직접 답 |

## 4. 진행 요령
- 응답이 멈춘 것 같으면 **승인 대기인지** 먼저 본다. 같은 요청을 다시 보내지 않는다.
- 기다리는 동안: 담당자 질문, 결과 읽기, LOG.md 확인.
- **AI 결과를 내가 고치면 바로** (후속 문답 ②번 재료): `LOG.md에 [수정] E 항목으로 남겨. AI가 처음 한 것 → 내가 바꾼 것 ← 이유.`
- 대화가 길어지면: `$dn-wrap A` → 새 세션: `AGENTS.md와 HANDOFF.md 읽고 현재 상태부터 이어서 해줘.`
- Codex가 꺼졌으면 `codex resume`.
- 추론 강도(`/model`에서 모델 고른 뒤 선택): 기본 **high**. 문서·정리·반복 작업은 **medium**. 원인 모를 버그·설계 막힘에만 **xhigh** 잠깐 → 해결되면 high로. low는 쓰지 않는다
- Codex 기본 스킬(체험에서 확인, 모두 켜져 있음): **Skill Creator**(과제 스킬 만들기) · **Skill Installer**(공개 스킬 설치) · **Review Agent**(변경 코드 버그 찾기, 검증 때 1회) · **OpenAI Docs**(OpenAI API 사용법 확인) · Image Gen(쓰지 않음)
- **보안 스킬은 시작할 때 설치해 둔다**: codex 켜자마자 `$skill-installer security-best-practices` → 승인 → `/quit` → `codex` (새 스킬은 다시 켜야 보인다) → `/skills`에 security-best-practices 확인. 실패하면 건너뛴다(키트의 기본 보안 규칙으로 충분). 검증 단계에서 1회 쓴다.
- 그 밖의 공개 스킬(필요할 때만, 설치 이유를 LOG D 항목에): 문서 입력이면 `pdf`·`doc`. 화면 자동 점검은 Browser 수동 확인으로 충분 (playwright는 설치가 무거움)
- 기본 슬래시 명령: `/status`(모델·승인·사용량) · `/diff`(바뀐 내용) · `/review`(자체 리뷰, 검증 단계에서 1회) · `/compact`(대화 요약으로 줄이기) · `/new`(새 대화) · `/permissions`(승인 모드) · `/mcp`
- Codex 안의 네트워크 명령(git clone·pip·npm 설치 등)은 샌드박스가 **처음엔 막는다**(exit 128 등) → Codex가 승인을 요청 → 승인하면 된다. 실패 메시지에 당황하지 않는다 (체험 확인). 서버 띄우기도 승인이 필요할 수 있다
- 승인 창: 반복되는 안전한 명령(python3, pytest, curl localhost, git add/commit)은 창에서 **"이 세션 동안 다시 묻지 않기"** 쪽을 고른다. 홈 밖 쓰기·외부 전송·삭제는 내용을 읽고 판단. 모드는 체험 기본(Workspace, Ask for approval) 유지, 승인·샌드박스 완전 끄기는 하지 않는다
- 시작 시 맨 아래 상태 줄에 기본 모델이 보인다 (체험: 권장 1순위 모델이 기본)
- 과제 스킬 만들기 (11:30 전까지, 10분 이내): `$skill-creator 방금 반복한 [절차]를 이 과제 전용 스킬로 .agents/skills/에 만들어. 이 과제에서 확인한 규칙과 확인 명령만 넣고, 만든 이유를 LOG.md D 항목에 남겨.` · `$skill-creator`가 없으면: `.agents/skills/<이름>/SKILL.md 를 직접 써. frontmatter는 name, description 두 줄, 본문은 절차 5~10줄.`
- 단순 작업(정리, 요약, 반복 코드)은 `/model`로 가벼운 모델에 맡기고 다시 기본 모델로.

## 4-1. 도구 (각각 --demo로 자체 점검)
- 데이터 첫 점검: `python3 /tmp/dn/tools/profile.py data/*.csv --out outputs/profile.md`
- 조인 매칭: `python3 /tmp/dn/tools/joincheck.py a.csv:열 b.csv:열 --alias b.csv:별칭열`
- 증거 남기기: `python3 /tmp/dn/tools/ev.py "python3 -m pytest -q" --claim "성공 기준 1 통과"`
- 민감정보 가리기: `mkdir -p app && cp /tmp/dn/tools/mask.py app/ && python3 app/mask.py --demo` (모듈: `from mask import mask_text, unmask_text`)
- 웹 뼈대: `cp -r /tmp/dn/tools/webskel app && git add app && git commit -m "chore: 웹 뼈대 복사(dn webskel)"` → 그다음 과제에 맞게 수정
- 도메인 틀: `cp /tmp/dn/templates/DOMAIN.md DOMAIN.md`
- 도메인 리뷰(반복 중 1회): "reviewer 서브에이전트로 PLAN.md 기준 src/ 도메인 오류 찾아줘"
- **웹 서버 포트는 3000** (Browser 기본 PORT). 미리보기: 왼쪽 지구본 → 상단 PORT 칸이 서버 포트와 같은지 → 새로고침. "포트 N에 응답하는 서버가 없어요"면 포트 불일치나 서버 꺼짐
- 서브에이전트는 말로 시키면 Codex가 바로 띄운다 (체험: "reviewer 서브에이전트로 …" → Started → Completed, 33초). toml이 없어도 된다. 지침은 이렇게 넘긴다: `verifier 서브에이전트를 띄워서 /tmp/dn/.codex/agents/verifier.toml 의 developer_instructions 를 그대로 지침으로 주고, 다음 항목을 독립 검증시켜: …`
- 독립 검증: "verifier 서브에이전트로 다음 항목을 원자료에서 다시 계산해: …" (안 되면 dn-verify 5절의 새 세션 리뷰)

## 4-2. MCP (기본 0개, 막힐 때만 1개)
- 왼쪽 MCP 탭의 JSON을 이걸로 바꿔 저장 → Codex 재시작 → `/mcp`로 연결 확인
- 라이브러리 문법·최신 사용법이 막힐 때: `{"mcpServers": {"context7": {"url": "https://mcp.context7.com/mcp"}}}`
- 보내는 건 라이브러리 이름과 일반 질문만. 과제 데이터·문장·회사명은 넣지 않는다 (외부 전송 감시)
- 쓴 이유를 LOG.md D 항목에 한 줄

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
