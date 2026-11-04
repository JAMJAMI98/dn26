업무 부품: docs/05_design.md 화면 명세의 블록 1개 = 파일 1개 (예: entities/result/ResultSummaryCard.tsx).
shared/ui 기본 부품만 조합하고, 데이터는 shared/api/client의 api()와 @tanstack/react-query의 useQuery/useMutation으로 가져온다.
