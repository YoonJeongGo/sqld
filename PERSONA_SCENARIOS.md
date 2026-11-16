# 사용자 목적별 기능 시나리오

실제 사용자 연구가 아닌 목적 기반 휴리스틱 및 에뮬레이터 검증이다. 단계 수/망설임은 실제 기록된 경우만 보고한다.

| ID | 유형 | 시작/목표 | 단계 | 기대 | 실제/상태 | 근거 |
|---|---|---|---|---|---|---|
| N1 | 첫 학습 | 빈 기록→오늘 범위 시작 | 홈→계획→강의→자기점검 | 연결된 자료와 답안 저장 | PASS 자동 및 대표 UI; 자기점검 입력의 수동 실행은 기준선 debug | 전체64, runtime-checklist selfcheck-and-new-memo |
| N2 | 첫 학습 | 원하는 개념 찾기 | 검색 ANSI→강의→뒤로 | 결과/검색어 유지 | PASS FT-02 수정 후 release 실제 실행 | release-061-ansi-search.png, FunctionalRecoveryUiTest |
| R1 | 빠른 반복 | 같은 범위 다음 문제 | 계획→10문항→다시 시작 | 범위를 순환 | PASS 실제 두 세트 중복0, 단위검사로 전체 범위 순환 | release-selection-grading-evidence.json, StudyPlanTest |
| R2 | 빠른 반복 | 채점 중 연타 | 보기→채점 연타→제출 | 한 번만 기록 | PASS 연속 채점1개, 전체10개·중복0 | release-selection-grading-evidence.json |
| B1 | 쉬었다 복귀 | 미완 답안 이어보기 | 선택→종료→재실행→이어보기 | 답/위치/시간 보존 | PASS 기준선 debug와 최종 release 강제종료/재실행 전체 payload 동일 | baseline-restart-comparison.json, final-user10-preservation.json |
| B2 | 쉬었다 복귀 | 오답/메모 다시보기 | 복습/필기→원문 | 기록과 연결 유지 | PASS 실제 오답9개/별표·메모 수정·자기점검 복습 연결 | runtime-checklist.json |
| E1 | 오류/취소 | 저장 실패 후 재시도 | 실패 주입→오류확인→재시도 | 초안/기존기록 보존 | PASS 격리 DB 실패주입·초안·재시도·취소·저장중 상태복원 | 전체64에 신규 FunctionalRecovery8 포함 |
| E2 | 오류/취소 | 백업 복원 | export→잘못된파일→정상검사→취소→복원 | 검증·미리보기·복구점·원자성 | PASS release 11→1→11, revision 외 기록 동일 | release-restore-recovery-comparison.json |
| A1 | 작은 화면/확대 | 200% 글자로 학습 | 홈→계획→문제→뒤로 | 스크롤/주버튼 접근 | PASS 수동 대표 메모 및 자동 고유12(후속 재실행 포함) | phone320/font200 로그, AFTER 확정란 |
| A2 | 태블릿 | 가로 큰 자료 보기 | 그림 확대→축소→닫기/목록접기 | 도표/강의 사용 가능 | PASS release 그림 보기 + 기존 그림/목록 자동검사 | release-061-diagram-viewer.png, 전체64 |
| D1 | 누적 기록 | 많은 기록 찾기 | 검색/필터→기록→세션 | 올바른 선택/복귀 | PASS 테스트 표본; 장기간 대규모 기록 성능은 미검증 | 전체64 중 UsabilityUiTest/PersistenceTest |
| D2 | 누적 기록 | 버전 업데이트 | user0백업→install-r→백업 비교 | 기존 기록 보존 | PASS user10 및 원래 user0 전체 payload 동일 | release-upgrade-user10-comparison.json, final-user0-preservation.json |

권한 거부: 앱 요청 런타임 권한 없음. 시스템 파일 선택 취소를 검증한다. 외부 서비스 장애/결제/광고/로그인은 실제 구현이 없어 N/A. 인터넷 없는 상태에서도 로컬 핵심 기능은 실행 가능해야 한다. 원문 웹사이트 버튼만 외부 브라우저에 위임하며 앱 학습의 필수 경로가 아니다.
