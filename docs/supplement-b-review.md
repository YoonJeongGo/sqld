# B 콘텐츠 보강 저자 검토 기록

2026-09-14. 저술 파일 `content/part-b.json`의 보강 내용을 기록한다. 아래 내용은 저자 자체 검토이며 Oracle 실제 실행, 사람 전문가 검수, 독립 문항 풀이 결과를 대신하지 않는다.

## 실제 작성 범위

- 새 목표 및 노트: S27 VIEW, S28 관계대수.
- 기존 노트의 추가 블록: S12 서브쿼리 분류·다중컬럼 조합, S15 분포 함수, S16 FIRST_VALUE·RATIO_TO_REPORT, S18 경로·순환, S20 정규식 함수와 플래그.
- 새 노트 두 개의 블록을 포함하여 총 53블록 추가. 기존 블록의 ID·본문을 보존하고 해당 기존 노트 버전만 올렸다. 회상 문항 링크는 새 문항을 추가했다.
- 신규 문항 26개: 회상 9, 적용 17. 전체 B는 목표 18, 노트 18, 문항 341이다.
- 신규 문항은 모두 `quarantined`, `document_review`로 저장했다. 기존 모의고사 또는 기존 315문항의 본문·선택지·정답 ID·검수 상태를 변경하지 않았다.

| 목표 | 노트 버전 | 새 회상 | 새 적용 |
|---|---:|---:|---:|
| S27 | 1 | 3 | 2 |
| S28 | 1 | 3 | 2 |
| S12 | 3 | 1 | 1 |
| S15 | 3 | 0 | 2 |
| S16 | 2 | 1 | 3 |
| S18 | 2 | 1 | 2 |
| S20 | 2 | 0 | 5 |

## 작성 및 확인 방법

Oracle Database 19c 공식 SQL Language Reference와 대학 관계대수 자료를 직접 열어 해당 정의를 확인했다. 원문 문항과 도표를 복제하지 않았고 입력 데이터·보기·해설은 독자 작성했다. 신규 출처 14개는 `content/supplement-b-sources.json`에 분리 저장했다. 중앙 `sources.json`, 우선순위, 앱 코드, validator는 수정하지 않았다.

신규 26문항 모두 네 보기 이유, 단일 정답, 조건, 단계별 해설을 작성했다. 계산형 SQL 14개에는 입력 DDL·설정·질의·예상 결과 fixture를 넣었다. VIEW의 CHECK OPTION 실패 문제는 오류와 기존 데이터 유지 여부를 묻는 개념 적용 문제로, 성공 SELECT 결과 fixture로 가장하지 않았다. 관계대수 적용 2개는 고전 집합의 직접 계산 문제다.

정규식은 검색 회차·끝 다음 위치·부분식·비중첩·줄바꿈 플래그·치환 역참조를 서로 다른 판단 과제로 나눴다. 윈도우 함수는 분포의 동률과 방향, NULL 처리, 이동 프레임, 합계의 파티션 범위, 함수별 구문을 분리했다. 같은 숫자·이름 치환만으로 별도 family를 늘리지 않았다. 시험 출제 빈도나 출제 확률은 주장하지 않았다.

## 검증과 경계

- 저장할 때 기존 315문항의 canonical JSON SHA256 불변을 확인했다.
- 기존 16노트는 최초 보강 저장 시 모든 기존 블록을 배열 prefix로 직접 비교하여 보존을 확인했다. 후속 작성은 새 블록 문구 하나와 회상 링크 추가만 다뤘다.
- 신규 문항의 고유 ID, 네 선택지 ID, 단일 정답, 격리 상태, 출처 참조, 표 열 수를 자체 검사했다.
- SQL 14개는 표시 SQL과 fixture 질의 일치, fixture 예상 결과와 해설의 마지막 표 일치를 검사했다. 이 검사는 SQL 실행이나 정답 증명이 아니다.
- 별도 검토 담당자가 신규 노트 53블록을 읽고 CUME_DIST의 내림차순 설명 모호성을 지적했다. 해당 신규 블록을 '현재 행보다 앞서거나 동률인 행'으로 수정했다. 관련 독립 노트 검수는 `evidence/priority-note-review-b.json`에서 별도로 관리한다.
- 신규 문항은 부모가 정답·선택지 ID·순서를 가린 독립 풀이를 진행한 후 공개 여부를 결정한다. 이 문서 작성 시 저자는 독립 풀이 통과를 주장하지 않는다.
- Oracle 19c 실제 실행, SQL Server 호환 실행, 사람 전문가 검수는 수행하지 않았다. 노트·문항 모두 저자 예상 결과와 문서 규칙 기반이다.
- 전체 통합 validator는 자산/문서를 쓰므로 저자 담당 범위를 넘지 않도록 실행하지 않았다. 출처 병합 및 앱 빌드·배포 확인은 부모 담당이다.

## 회수한 근거

- [Oracle CREATE VIEW](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CREATE-VIEW.html): 일반 뷰, 정의 교체, 갱신 및 권한 조건.
- [Oracle FIRST_VALUE](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/FIRST_VALUE.html), [RATIO_TO_REPORT](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/RATIO_TO_REPORT.html), [PERCENT_RANK](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/PERCENT_RANK.html), [CUME_DIST](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CUME_DIST.html): 이번 함수 보강의 기준.
- [Oracle 계층 의사열](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Hierarchical-Query-Pseudocolumns.html): NOCYCLE과 현재 행의 순환 표시.
- [Oracle REGEXP_INSTR](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/REGEXP_INSTR.html), [REGEXP_COUNT](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/REGEXP_COUNT.html), [REGEXP_REPLACE](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/REGEXP_REPLACE.html): 함수 인자·반환 규칙.
- [Wisconsin CS564](https://pages.cs.wisc.edu/~paris/cs564-s18/lectures/lecture-08.pdf), [Cornell CS4320](https://www.cs.cornell.edu/courses/cs4320/2008fa/slides/20080915_Algebra.pdf), [Wellesley CS304](https://cs.wellesley.edu/~cs304flask/lectures/relational-algebra/division.html): 집합 의미·기본 연산·디비전.

Oracle concepts의 추정 경로와 Rochester 강의 PDF 한 곳은 회수 실패하여 출처로 등록하지 않았다. 출처 레코드의 checkedAt은 실제 확인일이며 원문 발행일과 구분했다.

## 동결 시점 해시

- 보강 전·후 기존 315문항 canonical SHA256: `a0038acbb54aded508eadc62744c3d1477c20fbf417be8579fc00f90d7329cd9`
- 신규 26문항 canonical SHA256: `64de9544e86628e3113a11fde32621fa33d5bae1b5bb4dafa740a950238a7728`
- part-b.json 파일 SHA256: `7f6b3f923af8c9f9893959e097feabd83402f9ad7da088960252b9c50b2f1d29`
- supplement-b-sources.json 파일 SHA256: `89cc4e967303ce33ddcc71c06ad32e8382c3324f51c10e7343017a2f0122e74f`

## 신규 문항 ID

- `S27-SUP-R01-logical-definition`
- `S27-SUP-R02-drop-definition`
- `S27-SUP-R03-check-readonly`
- `S27-SUP-A01-base-change-visible`
- `S27-SUP-A02-check-option-exit`
- `S28-SUP-R01-selection-projection`
- `S28-SUP-R02-union-compatible`
- `S28-SUP-R03-division-universal`
- `S28-SUP-A01-project-after-select`
- `S28-SUP-A02-division-required-courses`
- `S12-SUP-R01-classification-axes`
- `S12-SUP-A01-paired-membership`
- `S15-SUP-A01-percent-rank-top-tie`
- `S15-SUP-A02-cume-desc-peers`
- `S16-SUP-A01-first-value-null-frame`
- `S16-SUP-A02-first-value-moving-frame`
- `S16-SUP-A03-ratio-partition-null`
- `S16-SUP-R01-ratio-over-syntax`
- `S18-SUP-A01-root-to-node-path`
- `S18-SUP-A02-cycle-current-parent`
- `S18-SUP-R01-nocycle-query-scope`
- `S20-SUP-A01-instr-after-end`
- `S20-SUP-A02-instr-subexpression`
- `S20-SUP-A03-count-nonoverlap`
- `S20-SUP-A04-flags-newline-dot`
- `S20-SUP-A05-replace-captured-parts`
