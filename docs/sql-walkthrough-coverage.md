# SQL 따라 읽기 자료 적용표

대상은 기존 앱의 독자 문항 661개이며 SQL이 있는 217개를 전수 분류했다. PDF 기출문항을 복제하거나 기존 문제의 정답·ID·난이도·보기·원본 표를 고치지 않았다. PDF 페이지 정보는 현재 원본 문항에 없어 만들어 적지 않았다.

- 새 단계 해설 적용: **133 / 217문항**. 전체 SQL 문항 적용 완료가 아니다.
- 기존 해설 유지: **84문항**. 미적용 이유는 아래 문항별 목록에 기록했다.
- SQL 없는 개념 문항 444개: 기존 개념·표 해설 유지. 가짜 SQL 실행 단계를 생성하지 않았다.
- 사용자 EMPLOYEE 기준 예제 1개: 기존 문제와 별개의 가상 학습 예제. note-S06 및 note-S12에 연결할 수 있다. 6명의 양쪽 조건과 UNKNOWN AND FALSE까지 계산하고 끝에 정답을 제시한다.
- 기존 63강·95예제·189확인문제는 수정하지 않았다. 새 자료를 기존 예제와 같은 데이터라고 합치지 않았다.

## 적용 내용

단순 행 수 요약 대신 WHERE 각 행의 실값 대입, JOIN 후보 쌍과 일치/미일치, 그룹별 원본 값과 집계 대상, COUNT(*)/COUNT(식), NVL 적용 시점, HAVING 판단, SELECT 계산값, DISTINCT 조합, 정렬을 별도 단계로 만든다. 필요한 절만 포함한다. 서브쿼리는 안쪽 값이 어디에서 나오는지, 상관 서브쿼리는 현재 바깥 행이 어떤 안쪽 조건값을 제공하는지 보여 준다. 분석 함수는 현재 행마다 실제 파티션/프레임을 표시한다.

| 유형 | 적용 문항 수 (중복 집계) |
|---|---:|
| aggregate | 36 |
| correlated | 1 |
| distinct | 6 |
| filter | 26 |
| group | 16 |
| having | 7 |
| join | 15 |
| set | 6 |
| sort | 36 |
| subquery | 9 |
| window | 15 |

## 검증과 한계

- 빌드: `python scripts/build_walkthroughs.py`. 각 적용 원문의 값 결과를 기존 fixture와 대조한다. 순서가 명시된 경우 순서까지, 아니면 중복을 보존하는 bag으로 비교한다.
- 검증: `python scripts/validate_walkthroughs.py`. 13개 경계 검사, 원본 스냅샷 동일성, SQL 강조 위치, 단계 ID, 표의 행/열 크기, 셀 범위, 최종 예상표, 앱 자산 미러를 검사한다. 실제 결과는 `evidence/sql-walkthroughs-20261006/validation.json`에 기록한다.
- 실제 비교 엔진은 **SQLite 3.50.4**다. **Oracle 19c 실행은 하지 않았다.** Oracle 공식 문서 의미 대조·SQLite 검산·Python 독립 값 계산을 구별한다. SQLite 통과를 Oracle 전체 호환 증명으로 쓰지 않는다.
- SQLite에서 Oracle 기본 NULL 정렬 위치를 ASC NULLS LAST / DESC NULLS FIRST로 명시하고, 숫자 NVL/MOD 함수를 등록했다. ANY는 현재 실제 목록의 OR로, 빈 ALL은 TRUE로, MINUS는 EXCEPT로 명시 변환한다. 원본 SQL은 보존하며 실행한 비교 SQL은 engine-checks.json에 따로 남긴다.
- 윈도 15문항의 프레임·순위·참조값은 Python으로 다시 계산해 SQLite와 비교했다. 범위 밖 DESC/NULL RANGE 또는 동점을 끝내지 못하는 행 위치 함수는 자동 적용하지 않는다.
- Oracle 전용 함수·계층·PIVOT·그룹 확장·상태 변경 등의 미적용 사유는 기능 삭제가 아니다. 원래 해설을 그대로 읽을 수 있다. SQL 없는 문항에 새 SQL 과정을 붙이지 않는다.
- 이 자료는 학습용 논리 설명이며 물리 실행 계획, 실제 엔진 임시표, 사람 전문가 검수, 학습 효과 검증 결과가 아니다. 앱 UI/필기/회전/실물 Galaxy 검증은 별도 QA가 맡는다.
- 자산 크기 실측: 인덱스와 134개 개별 JSON 합계 **1,448,306 bytes**. APK 압축 증가량·읽기 속도·메모리 개선은 이 숫자로 주장하지 않는다.

## 문항별 적용/미적용

| 문제 ID | 단원 | 상태 | 근거 |
|---|---|---|---|
| S07-A01 | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S07-A02 | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S07-A03 | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S06-A01 | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S08-A01 | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S02-A01 | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S02-A02 | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S02-A03 | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S02-A04 | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S02-A05 | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S02-A06 | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S03-A01 | S03 | 기존 해설 유지 | SUBSTR의 시작 위치/문자 길이 DBMS 차이를 별도 확인해야 함 |
| S03-A02 | S03 | 기존 해설 유지 | ROUND/TRUNC의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S03-A03 | S03 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S03-A04 | S03 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S03-A05 | S03 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S03-A06 | S03 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S04-A01 | S04 | 기존 해설 유지 | TO_CHAR/TO_DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S04-A02 | S04 | 기존 해설 유지 | DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S04-A03 | S04 | 기존 해설 유지 | TO_CHAR/DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S04-A04 | S04 | 기존 해설 유지 | TO_CHAR/ADD_MONTHS/DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S04-A05 | S04 | 기존 해설 유지 | MONTHS_BETWEEN/DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S04-A06 | S04 | 기존 해설 유지 | TO_DATE/DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S05-A01 | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S05-A02 | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S05-A03 | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S05-A04 | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S05-A05 | S05 | 기존 해설 유지 | 빈 문자열·문자 결합·나눗셈의 DBMS 차이를 별도 검증하지 않아 기존 해설 유지 |
| S05-A06 | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S06-A02 | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S06-A03 | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S06-A04 | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S06-A05 | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S06-A06 | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S07-A04 | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S07-A05 | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S07-A06 | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S07-A07 | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S07-A08 | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S08-A02 | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S08-A03 | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S08-A04 | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S08-A05 | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S08-A06 | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S08-A07 | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S02-mock-coalesced-distinct | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S02-mock-distinct-constant-tuple | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S03-mock-nested-clean | S03 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S03-mock-negative-round | S03 | 기존 해설 유지 | ROUND/TRUNC의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-1-S04-mock-format-month-minute | S04 | 기존 해설 유지 | TO_CHAR/TO_DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-1-S05-mock-case-count-else-zero | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S05-mock-nullif-coalesce | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S06-mock-null-or-false | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S06-mock-like-escape-literal | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S07-mock-count-sum-expression | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S07-mock-avg-zero-sum | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-1-S08-mock-two-stage-group | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S02-mock-distinct-null-two-cols | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S02-mock-star-vs-expression | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S03-mock-round-then-mod | S03 | 기존 해설 유지 | ROUND의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-2-S03-mock-substr-beyond | S03 | 기존 해설 유지 | SQLite는 범위 밖 SUBSTR을 빈 문자열로 반환하지만 원본 Oracle 예상값은 NULL: 다른 엔진 결과를 채택하지 않고 기존 해설 유지 |
| mock-2-S04-mock-half-open-day | S04 | 기존 해설 유지 | TO_DATE/DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-2-S05-mock-case-null-arithmetic | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S05-mock-nullif-different | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S06-mock-not-parenthesized | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S06-mock-in-subset-null | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S07-mock-count-distinct-expression | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S07-mock-sum-vs-summed-columns | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-2-S08-mock-having-average-zero | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-3-S02-mock-arithmetic-precedence | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-3-S02-mock-projection-retains-input | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-3-S03-mock-substr-zero-length | S03 | 기존 해설 유지 | SUBSTR 길이 0의 Oracle NULL 반환과 SQLite 빈 문자열 차이 |
| mock-3-S03-mock-replace-removal | S03 | 기존 해설 유지 | Oracle REPLACE의 생략 인자 동작을 SQLite 원문으로 검증할 수 없어 기존 해설 유지 |
| mock-3-S04-mock-date-fraction-difference | S04 | 기존 해설 유지 | DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-3-S05-mock-case-range-gap | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-3-S05-mock-empty-coalesce | S05 | 기존 해설 유지 | 빈 문자열·문자 결합·나눗셈의 DBMS 차이를 별도 검증하지 않아 기존 해설 유지 |
| mock-3-S06-mock-between-reversed | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-3-S06-mock-impossible-or-null | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-3-S07-mock-distinct-null-replacement-count | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-3-S07-mock-conditional-sum-amount | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-3-S08-mock-complete-group | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S02-mock-unary-null | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S02-mock-where-expression-equality | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S03-mock-case-normalization | S03 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S03-mock-substr-zero-start | S03 | 기존 해설 유지 | SUBSTR의 시작 위치/문자 길이 DBMS 차이를 별도 확인해야 함 |
| mock-4-S04-mock-year-boundary | S04 | 기존 해설 유지 | TO_CHAR/DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-4-S05-mock-zero-conflation-case | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S05-mock-case-negative-fallback | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S06-mock-like-intersection | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S06-mock-not-and-priority | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S07-mock-distinct-constant-counts | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S07-mock-null-aggregate-subtract | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-4-S08-mock-group-computed-band | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-5-S02-mock-quoted-alias | S02 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-5-S02-mock-number-division | S02 | 기존 해설 유지 | TRUNC의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-5-S03-mock-double-rounding | S03 | 기존 해설 유지 | ROUND의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-5-S03-mock-concat-null-space | S03 | 기존 해설 유지 | 빈 문자열·문자 결합·나눗셈의 DBMS 차이를 별도 검증하지 않아 기존 해설 유지 |
| mock-5-S04-mock-trunc-month-date | S04 | 기존 해설 유지 | TO_CHAR/TRUNC/TO_DATE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-5-S05-mock-space-not-null | S05 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-5-S05-mock-rounded-nullif | S05 | 기존 해설 유지 | ROUND의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| mock-5-S06-mock-negated-between-null | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-5-S06-mock-null-equality-disjunction | S06 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-5-S07-mock-count-quotient-nullif | S07 | 기존 해설 유지 | 빈 문자열·문자 결합·나눗셈의 DBMS 차이를 별도 검증하지 않아 기존 해설 유지 |
| mock-5-S07-mock-average-vs-nonzero | S07 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| mock-5-S08-mock-empty-versus-grouped | S08 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S25-A01-explicit-char-length | S25 | 기존 해설 유지 | CAST의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S25-A02-numeric-cast-scales | S25 | 기존 해설 유지 | CAST의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S26-A01-add-null-existing-row | S26 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S26-A02-rename-retains-values | S26 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S03-A07-instr-occurrence-missing | S03 | 기존 해설 유지 | INSTR의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S03-A08-padding-final-length | S03 | 기존 해설 유지 | LPAD/RPAD의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S03-A09-negative-integer-directions | S03 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S03-A10-lower-uppercase-sequence | S03 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S05-A07-decode-null-versus-case | S05 | 기존 해설 유지 | DECODE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S05-A08-decode-default-omitted | S05 | 기존 해설 유지 | DECODE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S09-A01-mixed-sort | S09 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S09-A02-case-priority | S09 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S09-A03-alias-derived | S09 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S09-A04-null-explicit-desc | S09 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S09-A05-group-sort-total | S09 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S09-A06-distinct-position | S09 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S10-A01-duplicate-multiplication | S10 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S10-A02-null-pair-filter | S10 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S10-A03-overlap-band | S10 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S10-A04-cross-filter | S10 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S10-A05-aggregate-after-join | S10 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S10-A06-two-key-matching | S10 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S10-A07-empty-cross | S10 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S11-A01-on-paid-preserve | S11 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S11-A02-where-paid-remove | S11 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S11-A03-count-outer-null | S11 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S11-A04-full-both-unmatched | S11 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S11-A05-using-key-result | S11 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S11-A06-natural-extra-key | S11 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S11-A07-anti-exists-key | S11 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S12-A01-above-own-dept-average | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S12-A02-exists-no-multiply | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S12-A03-null-safe-not-exists | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S12-A04-not-in-empty | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S12-A05-scalar-aggregate-empty | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S12-A06-any-null-mixed | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S12-A07-all-empty | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S12-A08-tuple-in | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S13-A01-union-null-combined | S13 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S13-A02-all-count | S13 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S13-A03-intersection-two-columns | S13 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S13-A04-minus-dedup | S13 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S13-A05-parenthesized-difference | S13 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S13-A06-difference-count-empty | S13 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S14-A01-rollup-original-null | S14 | 기존 해설 유지 | GROUPING/ROLLUP의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S14-A02-rollup-two-keys | S14 | 기존 해설 유지 | ROLLUP의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S14-A03-cube-cross-subtotals | S14 | 기존 해설 유지 | CUBE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S14-A04-chosen-grouping-sets | S14 | 기존 해설 유지 | GROUPING의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S14-A05-having-total-only | S14 | 기존 해설 유지 | ROLLUP/GROUPING의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S14-A06-repeated-sets | S14 | 기존 해설 유지 | GROUPING의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S15-A01-ranks-side-by-side | S15 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S15-A02-unique-number-with-tie-key | S15 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S15-A03-partition-sum-maintains-rows | S15 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S15-A04-lag-null-default | S15 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S15-A05-lead-gap-not-id | S15 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S15-A06-ntile-unequal | S15 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S16-A01-range-peer-cumulative | S16 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S16-A02-rows-two-window | S16 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S16-A03-range-value-distance | S16 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S16-A04-last-value-full | S16 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S16-A05-future-count-boundary | S16 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S16-A06-partition-boundaries | S16 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S17-A01-fetch-only-key | S17 | 기존 해설 유지 | FETCH의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S17-A02-fetch-ties-last-score | S17 | 기존 해설 유지 | FETCH의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S17-A03-offset-page | S17 | 기존 해설 유지 | OFFSET/FETCH의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S17-A04-per-dept-top | S17 | 기존 해설 유지 | 분석 함수 앞의 필터·집계가 있는 조합은 중간 입력 별도 작성 필요 |
| S17-A05-rownum-lower-bound-empty | S17 | 기존 해설 유지 | ROWNUM의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S17-A06-rank-versus-dense-cut | S17 | 기존 해설 유지 | 분석 함수 앞의 필터·집계가 있는 조합은 중간 입력 별도 작성 필요 |
| S18-A01-hierarchy-levels | S18 | 기존 해설 유지 | START/CONNECT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S18-A02-self-manager-name | S18 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S18-A03-subtree-start | S18 | 기존 해설 유지 | START/CONNECT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S18-A04-ancestor-direction | S18 | 기존 해설 유지 | START/CONNECT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S18-A05-where-after-path | S18 | 기존 해설 유지 | START/CONNECT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S18-A06-leaf-flags | S18 | 기존 해설 유지 | START/CONNECT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S19-A01-pivot-sum-groups | S19 | 기존 해설 유지 | PIVOT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S19-A02-pivot-count-missing | S19 | 기존 해설 유지 | PIVOT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S19-A03-pivot-extra-id | S19 | 기존 해설 유지 | PIVOT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S19-A04-unpivot-default | S19 | 기존 해설 유지 | UNPIVOT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S19-A05-unpivot-include-count | S19 | 기존 해설 유지 | UNPIVOT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S19-A06-conditional-pivot | S19 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S20-A01-regexp-whole-digits | S20 | 기존 해설 유지 | REGEXP_LIKE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-A02-regexp-second-token | S20 | 기존 해설 유지 | REGEXP_SUBSTR의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-A03-regexp-clean-replace | S20 | 기존 해설 유지 | REGEXP_REPLACE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-A04-regexp-class-group-difference | S20 | 기존 해설 유지 | REGEXP_LIKE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-A05-regexp-case-insensitive | S20 | 기존 해설 유지 | REGEXP_LIKE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-A06-regexp-no-match-null | S20 | 기존 해설 유지 | REGEXP_SUBSTR의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S21-A01-update-filter-rows | S21 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S21-A02-delete-null-condition | S21 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S21-A03-insert-column-order | S21 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S21-A04-update-all-original-expressions | S21 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S21-A05-insert-select-filter | S21 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S21-A06-merge-update-insert | S21 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S22-A01-partial-then-commit | S22 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S22-A02-full-after-partial | S22 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S22-A03-commit-boundary | S22 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S22-A04-savepoint-name-reuse | S22 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S22-A05-ddl-commits-prior | S22 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S22-A06-delete-insert-rollback | S22 | 기존 해설 유지 | DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지 |
| S27-SUP-A01-base-change-visible | S27 | 기존 해설 유지 | 초기 설정에 뷰·UPDATE·COMMIT이 포함되어 세션/트랜잭션 의미를 Oracle에서 검증하지 못함 |
| S12-SUP-A01-paired-membership | S12 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S15-SUP-A01-percent-rank-top-tie | S15 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S15-SUP-A02-cume-desc-peers | S15 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S16-SUP-A01-first-value-null-frame | S16 | 기존 해설 유지 | 분석 함수의 NULL 무시/비율 전용 의미를 독립 실행으로 확인하지 못하여 기존 해설 유지 |
| S16-SUP-A02-first-value-moving-frame | S16 | 적용 | 현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시. |
| S16-SUP-A03-ratio-partition-null | S16 | 기존 해설 유지 | 분석 함수의 NULL 무시/비율 전용 의미를 독립 실행으로 확인하지 못하여 기존 해설 유지 |
| S18-SUP-A01-root-to-node-path | S18 | 기존 해설 유지 | START/CONNECT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S18-SUP-A02-cycle-current-parent | S18 | 기존 해설 유지 | START/CONNECT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-SUP-A01-instr-after-end | S20 | 기존 해설 유지 | REGEXP_INSTR의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-SUP-A02-instr-subexpression | S20 | 기존 해설 유지 | REGEXP_INSTR의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-SUP-A03-count-nonoverlap | S20 | 기존 해설 유지 | REGEXP_COUNT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-SUP-A04-flags-newline-dot | S20 | 기존 해설 유지 | REGEXP_COUNT의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |
| S20-SUP-A05-replace-captured-parts | S20 | 기존 해설 유지 | REGEXP_REPLACE의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지 |

## 자료 관리와 되돌리기

`content/sql-walkthroughs/`가 새 자료의 기준이며 `scripts/build_walkthroughs.py`로 만든다. `app/src/main/assets/sql-walkthroughs/`는 동일한 배포 미러다. 원본 content-pack/course-pack 빌더를 실행하지 않는다. 원본 질문 ID와 source 전체 스냅샷이 다르면 앱은 잘못된 단계 연결을 거절해야 한다.
되돌릴 때는 새 UI 연결을 끄고 새 sql-walkthroughs 인덱스/자산만 이전 백업으로 복원한다. 학습 DB·답안·필기·기존 콘텐츠는 이 스크립트의 입력 대상도 수정 대상도 아니다.

## 공식 의미 참고

- [SELECT](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/SELECT.html)
- [Nulls](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Nulls.html)
- [Aggregate-Functions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Aggregate-Functions.html)
- [Joins](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Joins.html)
- [Using-Subqueries](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Using-Subqueries.html)
- [Analytic-Functions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Analytic-Functions.html)
- [IN-Condition](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/IN-Condition.html)
- [Comparison-Conditions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Comparison-Conditions.html)
- [Logical-Conditions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Logical-Conditions.html)
