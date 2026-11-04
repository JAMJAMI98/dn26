업무 부품: docs/05_design.md 화면 명세의 블록 1개 = 파일 1개 (예: entities/result/result-summary-card.js).
shared/ui/components.js 기본 부품만 조합하고, 데이터는 shared/api/client.js의 api()로 가져온다. 블록마다 처음·로딩·오류·결과 4상태를 보여 준다.
