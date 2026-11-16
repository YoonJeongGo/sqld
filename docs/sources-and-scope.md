# SQLD 시험 근거와 범위 매핑

> 0.2.0의 콘텐츠 보강·중요도·현재 검증은 [priority-update.md](priority-update.md)를 참조하세요. 아래 초기 개발 기록은 당시 검증 범위를 보존합니다. 최신 콘텐츠 수량과 검수 집계는 coverage.md 및 evidence/content-review-summary.json에 있습니다.

확인일: 2026-09-14 (Asia/Seoul). 출처 레지스트리: [sources.json](../content/sources.json), 버전 2026.09.14.8.

## 판단과 검증 경계

현재 공식 SQLD 상세 안내, 최신 출제기준, 변경 공지, 자료실·정오표 원문을 확보하지 못했다. 따라서 시험 설정과 아래 범위는 **공식 원문 재확인이 필요한 잠정 설정**이다. 이것을 "현행 공식 검증 완료"로 표시할 수 없다. 접근 실패를 기능 개발 중단 이유로 삼지 않고, 사용자가 준 범위를 독자적 학습목표로 나누어 구현한다.

Oracle 19c SQL 문서 등 70개 자료는 실제 웹 열기를 통해 내용이 반환됨을 확인했다. DataQ 3개 레코드는 실패/과거 검색색인 상태로 별도 구분했다. 문서 접근 및 일반 개념 대조는 **개별 문항 정답·해설 검수와 다르다**. 이 조사에서 Oracle/SQL Server 엔진 실행, 사람 전문가 검수, 공식 공개문제 이용 허가 확보는 수행하지 않았다.

## 공식 원문 접근 기록

| 대상 | 실제 확인 경로 | 2026-09-14 결과 | 처리 |
|---|---|---|---|
| 공식 시작 페이지 | https://www.dataq.or.kr/ | 웹 도구 fetch 400 | 현재 공지 미확인 |
| SQLD 상세 | https://www.dataq.or.kr/www/sub/a_04.do | 웹 도구 fetch 400 | ExamSpec 잠정 상태 |
| 메인·공지·자료실 진입 | https://www.dataq.or.kr/www/main.do | 웹 도구 fetch 400; PowerShell HTTPS 소켓 접근 거부 | 최신 공지·정오표 미확인 |
| 자격 개요 | https://www.dataq.or.kr/www/sub/introduction.do | 웹 도구 fetch 400 | 검색 캐시를 현재 원문으로 대체하지 않음 |
| 2022 공식 브로슈어 | https://www.dataq.or.kr/www/dataq_brochure_2022.pdf | 직접 fetch 400; 과거 검색색인 텍스트만 반환 | 10/40 구성의 과거 교차자료만 사용 |
| 공식 사이트 한정 검색 | SQL 출제기준 개정/2024/정오표/자료실 검색 | 최신 원문 결과 확보 실패 | 공지나 정오표가 "없다"고 결론 내리지 않음 |

공식 사이트 변경 공지·자료실의 유효 게시물 URL을 추측하여 만들지 않았다. 재확인 시 공식 상세 페이지 → 출제기준의 적용일 → 개정 공지 → 교재/문제 정오표 순으로 열고, 확인한 문서의 버전과 적용일을 보존해야 한다. 시험 일정도 이번 조사에서 공식 확정하지 않았으며 사용자의 목표일과 구별해야 한다.

## 잠정 ExamSpec

| 설정 | 잠정 값 | 근거 상태 |
|---|---|---|
| 1과목 | 데이터 모델링의 이해, 10문항, 20점 | 사용자 초안 + 2022 공식 검색색인으로 과거 배분 확인 |
| 2과목 | SQL 기본 및 활용, 40문항, 80점 | 사용자 초안 + 2022 공식 검색색인으로 과거 배분 확인 |
| 전체 | 객관식 50문항, 문항당 2점, 90분 | [에듀윌 2026 대비 교재 안내](https://company.eduwill.net/pr/newsInfo?bIdx=315451&page=&searchTarget=all) 실제 열기 교차확인 |
| 합격 기준 | 총점 60점 이상 AND 각 과목 득점률 40% 이상 | 에듀윌 안내 및 과거 공식 색인 교차확인 |
| 과락 회피 | 1과목 4개, 2과목 16개 이상 정답 | 위 설정에서의 산술 결과; 이것만으로 합격 아님 |
| 출제기준 버전/적용일 | 미확인/null | 현재 공식 원문 확보 전 확정 금지 |
| 확인 상태 | provisional_official_unavailable | UI·백업·시험 세션에 보존 |

채점 경계값: (4,26)=60점 기준 충족; (4,25)=58점 총점 미달; (3,40)=86점 1과목 과락; (10,15)=50점 2과목 과락 및 총점 미달; (4,16)=40점 총점 미달; (10,40)=100점. 이는 설정의 계산 검증이며 실제 시험 합격 보장이 아니다.

에듀윌 게시물 등록일은 2025-07-10, 본문에 적힌 출간 사건일은 2025-06-10이다. 2026 대비라는 제목 때문에 2026년 시행기관 공지로 오인하지 않는다. 공식 2022 브로슈어 검색색인에는 구범위와 단답형 설명이 있으므로 그 부분을 현행 앱 시험 형식으로 가져오지 않는다.

## 34개 학습목표와 범위 대조

아래 ID는 앱의 교육 설계 단위이며 시행기관이 부여한 공식 목표 번호가 아니다. 사용자가 준 A~E 초안을 기준으로 1과목 10개, 2과목 24개로 세분했다. [위키북스 2026 교재 목차](https://wikibook.co.kr/sqld2026/)는 대략적인 항목 유무만 교차 확인했다. 출판사 목차 및 본문·예제·문제를 복제하지 않았다.

- A: 데이터 모델링의 이해
- B: 데이터 모델과 SQL
- C: SQL 기본
- D: SQL 활용
- E: 관리 구문

| objectiveId | 과목 | 영역 | 학습목표 | 선수 개념 | 검증 출처 ID |
|---|---:|---|---|---|---|
| M01 | 1 | A | 데이터 모델링의 목적과 단계: 현실의 업무를 추상화하여 개념·논리·물리 모델로 표현하는 이유를 설명한다. | 없음 | oracle-modeler243 |
| M02 | 1 | A | 엔터티와 인스턴스: 업무상 관리 대상인 엔터티와 그 개별 발생을 구분한다. | M01 | oracle-modeler243 |
| M03 | 1 | A | 속성·도메인: 속성의 의미, 허용 범위, 도출 속성과 원천 속성을 구분한다. | M02 | oracle-modeler243, oracle19-constraints |
| M04 | 1 | A | 관계·카디널리티·참여: 업무 규칙으로 1:1·1:N·N:M 및 선택·필수 참여를 읽는다. | M02 | oracle-modeler243 |
| M05 | 1 | A | 식별자와 식별 관계: 유일성과 최소성을 갖춘 후보 식별자 및 식별·비식별 관계를 구분한다. | M03, M04 | oracle-modeler243, oracle19-constraints |
| M06 | 1 | B | 정규화와 함수 종속: 명시된 후보키와 업무 함수 종속을 바탕으로 1NF·2NF·3NF 분해를 판단한다. | M05 | waterloo-normalization, sfu-normalization |
| M07 | 1 | B | 관계와 조인: 모델의 관계가 연결 조건 및 조인 결과의 행 수에 미치는 영향을 판단한다. | M04, M05 | oracle-modeler243, oracle19-joins |
| M08 | 1 | B | 모델이 표현하는 트랜잭션: 업무 완료 단위와 테이블 변경 단위의 차이를 설명한다. | M02, M04 | oracle19-transactions |
| M09 | 1 | B | NULL 속성: 미정·부재를 나타내는 NULL을 숫자 0과 구별한다. | M03 | oracle19-nulls |
| M10 | 1 | B | 본질식별자와 인조식별자: 업무 의미를 갖는 식별자와 대리키를 구별하고 업무 유일성 보존을 판단한다. | M05 | oracle-modeler243, oracle19-constraints |
| S01 | 2 | C | 관계형 데이터베이스: 행·열·키·제약조건과 SQL의 역할을 설명한다. | M02, M03 | oracle19-datatypes, oracle-modeler243 |
| S02 | 2 | C | SELECT와 처리 순서: 열 선택·별칭·중복 제거를 읽고 작성 순서와 논리·물리 실행을 구분한다. | S01 | oracle19-select, mssql-select |
| S03 | 2 | C | 문자·숫자 함수: 명시된 Oracle 단일행 함수의 입력과 출력을 해석한다. | S02 | oracle19-functions |
| S04 | 2 | C | 날짜·형 변환 함수: 날짜 리터럴·형식 모델·명시적 변환을 사용해 세션 의존성을 줄인다. | S02, S03 | oracle19-todate, oracle19-datatypes, oracle19-functions |
| S05 | 2 | C | CASE와 NULL 처리 함수: 조건 분기와 NULL 대체 위치의 차이를 해석한다. | M09, S02 | oracle19-case, oracle19-nulls |
| S06 | 2 | C | WHERE와 세 값 논리: TRUE·FALSE·UNKNOWN 및 비교·범위·논리 조건을 평가한다. | M09, S02 | oracle19-nulls, oracle19-in, oracle19-regexp |
| S07 | 2 | C | 집계와 NULL: COUNT(*)·COUNT(열)·SUM·AVG의 계산 대상을 추적한다. | S06 | oracle19-aggregate, oracle19-count |
| S08 | 2 | C | GROUP BY와 HAVING: 행 조건·그룹 형성·그룹 조건을 나누어 해석한다. | S07 | oracle19-aggregate, oracle19-select |
| S09 | 2 | C | ORDER BY와 결과 순서: 정렬 기준·동률·NULL 배치 및 정렬 없는 결과의 순서 비보장을 판단한다. | S02 | oracle19-select, oracle19-analytic |
| S10 | 2 | C | 조인과 행 수: 등가·비등가 조인의 매칭과 중복 행 증가를 추적한다. | M07, S06 | oracle19-joins |
| S11 | 2 | C | 표준 조인과 외부 조인: INNER·CROSS·LEFT·RIGHT·FULL 및 ON/WHERE 위치 차이를 설명한다. | S10 | oracle19-joins, oracle19-select |
| S12 | 2 | D | 서브쿼리: 단일행·다중행·상관 서브쿼리와 EXISTS/NOT IN의 전제를 판단한다. | S06, S10 | oracle19-select, oracle19-in, oracle19-exists |
| S13 | 2 | D | 집합 연산자: UNION·UNION ALL·INTERSECT·MINUS의 중복 처리와 열 대응을 판단한다. | S02, S09 | oracle19-setops |
| S14 | 2 | D | 그룹 함수: ROLLUP·CUBE·GROUPING SETS와 집계용 NULL을 해석한다. | S08 | oracle19-select, oracle19-grouping |
| S15 | 2 | D | 순위 함수: RANK·DENSE_RANK·ROW_NUMBER의 동률 처리와 비결정성을 구분한다. | S09 | oracle19-analytic |
| S16 | 2 | D | 윈도우 함수와 프레임: PARTITION·ROWS·RANGE·기본 프레임 및 LAG/LEAD를 구분한다. | S07, S15 | oracle19-analytic |
| S17 | 2 | D | Top N 쿼리: ROWNUM·FETCH·TOP의 DBMS별 의미와 동률을 판단한다. | S09, S15 | oracle19-rownum, oracle19-select, mssql-top |
| S18 | 2 | D | 계층형 질의·셀프 조인: 별칭 및 START WITH·CONNECT BY·PRIOR의 방향을 추적한다. | S10, S12 | oracle19-hierarchy, oracle19-joins |
| S19 | 2 | D | PIVOT·UNPIVOT: 집계 회전과 열의 행 전환, NULL 제외 전제를 해석한다. | S08 | oracle19-select |
| S20 | 2 | D | 정규 표현식: Oracle 패턴의 앵커·수량자·문자 집합을 적용한다. | S03, S06 | oracle19-regexp, oracle19-regexp-substr |
| S21 | 2 | E | DML: INSERT·UPDATE·DELETE·MERGE의 대상 행과 제약을 추적한다. | S06, S12 | oracle19-insert, oracle19-update, oracle19-delete, oracle19-merge |
| S22 | 2 | E | TCL: COMMIT·ROLLBACK·SAVEPOINT 및 자동 커밋 조건을 구분한다. | M08, S21 | oracle19-commit, oracle19-rollback, oracle19-transactions |
| S23 | 2 | E | DDL: 테이블 정의와 무결성 제약 및 DBMS별 트랜잭션 경계를 판단한다. | M05, S22 | oracle19-constraints, oracle19-commit |
| S24 | 2 | E | DCL: 사용자·객체 권한·역할 및 GRANT/REVOKE를 구분한다. | S23 | oracle19-grant, oracle19-revoke |

### 초안과 교차자료의 차이 및 제외 범위

- 위키북스 목차는 관계형 DB 개요를 1과목 내에 배치한다. 앱은 사용자가 준 초안의 C에 두고 M02/M03와 연결한다. 교재의 편집 순서를 공식 이동으로 해석하지 않는다.
- 함수는 문자·숫자(S03), 날짜·변환(S04), CASE·NULL(S05)로 분리했다. 윈도우는 순위(S15)와 프레임/행 순서(S16)로 나누었다. 이는 학습 설계 결정이다.
- 반정규화는 교재 소항목에 있으나 사용자 현행 초안의 독립 항목은 아니다. M06에서 비교를 위한 기초 보충으로만 다루고 공식 필수 범위 확정을 유보한다.
- SQL 최적화 기본 원리, 인덱스 상세, 실행 계획 튜닝, 조인 알고리즘 튜닝, 옵티마이저 힌트, 저장구조는 현행 필수 목표로 추가하지 않았다. 설명에 필요하면 범위 밖 참고로 명시한다.
- 대학 정규화 문서는 함수 종속·후보키·정규형의 수학적 정의 검증용이다. 해당 강의의 모든 고급 정규형이나 분해 알고리즘을 SQLD 필수 범위로 편입하지 않는다.

각 목표에는 noteId, concept quiz IDs, application question IDs, explanation references, review rules, source IDs가 연결되어야 한다. 작성 여부, 자동 구조 검사, 독립 풀이, SQL 문서/실행 검증, 렌더링 검수를 각각 별도 상태로 관리한다. 이 문서의 목표 목록만으로 실제 콘텐츠가 완성되었다고 집계하지 않는다.

## 문법 검증에서 고정할 위험 조건

| 고위험 개념 | 문항·해설에 적용할 조건 | 직접 확인한 출처 |
|---|---|---|
| NULL·UNKNOWN | = NULL은 일반 동등 비교로 참이 되지 않음. WHERE는 TRUE만 채택. NOT UNKNOWN은 UNKNOWN. Oracle19c 빈 문자열 처리는 다른 DBMS의 일반 규칙으로 확장하지 않음 | oracle19-nulls |
| COUNT·SUM·AVG | COUNT(*)는 행, COUNT(expr)는 비NULL 식. 집계 인자가 모두 NULL/빈 입력이면 COUNT는 0, SUM/AVG는 NULL. GROUP BY가 있으면 그룹 자체 부재를 구별 | oracle19-aggregate, oracle19-count |
| NOT IN·NOT EXISTS | 단일열 NOT IN 우측 NULL은 각 비교의 FALSE/UNKNOWN을 추적. "모두 FALSE"라고 일반화하지 않음. 빈 서브쿼리와 상관 조건도 구분 | oracle19-in, oracle19-exists |
| 조인 | ON 매칭 → 외부조인 NULL 확장 → WHERE 잔여 필터로 교육용 단계를 제시. 고유하지 않은 키의 매칭 증가를 보존 | oracle19-joins |
| SELECT 순서 | 작성 순서·논리적 바인딩·물리 실행 계획은 다름. 중간 해설 표는 실제 DB 실행 추적이라고 부르지 않음 | mssql-select |
| 집합 연산 | 열 위치/개수/타입 그룹 명시. UNION ALL은 중복 보존. Oracle19c 연산자 우선순위를 다른 버전에 일반화하지 않음 | oracle19-setops |
| 정렬 | 최종 ORDER BY 없으면 결과 순서 비보장. 동률 행의 순서까지 요구하려면 유일한 보조 키 필요 | oracle19-select, oracle19-analytic |
| 순위·프레임 | RANK·DENSE_RANK 동률과 ROW_NUMBER를 구분. ROWS의 유일하지 않은 정렬에 확정 결과를 부여하지 않음. 기본 프레임은 해당 함수와 ORDER BY 조건을 명시 | oracle19-analytic |
| 집계용 NULL | GROUPING 값으로 생성된 소계 자리와 실제 NULL 값을 구분. COALESCE 표시만으로 의미를 합치지 않음 | oracle19-grouping |
| Top N | 같은 레벨 ROWNUM 필터와 ORDER BY는 상위 정렬 후 N개와 다를 수 있음. ROWNUM>1 조건 반례. SQL Server TOP WITH TIES는 N개보다 늘 수 있음 | oracle19-rownum, oracle19-select, mssql-top |
| 날짜·문자 | TO_DATE 형식 모델과 세션 NLS 조건을 밝힘. 시스템 현재 날짜·문자 정렬·암묵변환에 따라 달라지는 정답을 고정하지 않음 | oracle19-todate, oracle19-datatypes |
| 계층형 | 부모/자식 방향과 시작 행, 순환 유무 명시. WHERE 제거와 하위 트리 제거를 혼동하지 않음 | oracle19-hierarchy |
| PIVOT·UNPIVOT | PIVOT 입력에 불필요한 열이 남으면 암묵적 그룹화 기준이 달라짐. UNPIVOT 기본값은 NULL 제외 | oracle19-select |
| 트랜잭션 | Oracle 일반 테이블 DDL의 암묵 COMMIT, SAVEPOINT 범위, 클라이언트 자동커밋을 명시. SQL Server TRUNCATE 롤백 가능성을 Oracle 규칙과 구분 | oracle19-commit, oracle19-rollback, mssql-truncate |
| 정규화 | 업무 규칙·후보키·함수 종속을 먼저 제공. 몇 개 예시 행의 우연한 유일성을 함수 종속 증거로 단정하지 않음 | waterloo-normalization, sfu-normalization |
| SQLite | SQLite 성공을 Oracle/SQL Server 정답 검증으로 보고하지 않음. 집계의 비그룹 열·유연한 타입 허용 차이에 주의 | sqlite-quirks |

## 출처 사용과 저작권 정책

모든 외부 자료는 사실 확인 및 링크 안내용이다. 별도 재수록 허가를 확보하지 않았고, 외부 책·강의·블로그의 본문·문제·해설·표를 앱에 복제하지 않는다. 공개된 URL이 있다는 사실은 자유로운 문제 재배포 허가를 뜻하지 않는다.

이번 기본 콘텐츠의 출처 유형은 original_practice/original_mock이다. 공식 공개 기출과 이용허락 복원 문제는 확보하지 않았으며, 생성 문항에 실제 시험 연도·회차를 붙이지 않는다. sourceId는 정답 확인에 실제 사용한 절만 가리켜야 하며, 실패 상태 DataQ나 출판사 목차를 SQL 정답 근거로 연결해서는 안 된다.

검증 라벨은 document_review, independent_ai_review, engine_verified 등을 별도로 기록한다. 공식 문서를 읽은 AI 검토는 사람 전문가 검수나 실제 DB 실행 검증을 뜻하지 않는다. SQL Server ver16 문서 접근이 실패하여 ver17을 읽은 두 자료는 해당 버전을 명시했다. 2022 특정 엔진 문항을 그 자료만으로 실행 확인했다고 주장할 수 없다.

## 독립 검토 방식

1. 저술 산출물에서 문제 ID·지문·보기·스키마·입력·환경만 추출한 blind-review 입력을 만든다. 정답 ID, 해설, 예상 출력, 정답을 드러내는 choice reason은 제외한다.
2. 독립 검토자는 그 입력만 보고 정답과 근거·조건 누락 여부를 기록한다. 독립 풀이 파일의 해시와 검토 시각을 먼저 보존한다.
3. 이후 원본 정답표·해설과 비교한다. 불일치와 모호성은 격리하며 단순히 원본 정답으로 덮어쓰지 않는다.
4. 같은 AI 계열 역할 분리는 독립 사고 패스를 제공하지만 인간 전문가 검수나 객관적 정답 보장으로 표시하지 않는다.
5. 구조 검사는 빈 해설·참조 누락을 검출하며 개념 정확성을 증명하지 않는다. 문서 검토와 앱 렌더링 검수를 별도로 마친다.

대표 20문항에 대해 정답을 숨긴 독립 풀이와 후속 원답·해설 대조를 수행했다. 전체 문항 검수와 구분하며 실제 범위·발견 사항·해시는 [content-review.md](content-review.md)에 기록했다.


## Android 접근성과 대비 근거

2026-09-14에 Google의 [Compose API defaults](https://developer.android.com/develop/ui/compose/accessibility/api-defaults) 원문을 직접 열었다. 페이지는 2026-07-21 갱신으로 표시되며, 터치 대상 최소48dp, 의미있는 아이콘 설명, 컴포넌트의 기본 semantics를 설명한다. 앱 UI 구현 점검의 근거이며 실제 TalkBack 사용성 시험의 대체물이 아니다. sourceId: `android-compose-accessibility-defaults`.

[W3C WCAG2.2 권고문](https://www.w3.org/TR/WCAG22/)은 현재 반환된 문서가 2024-12-12 Recommendation임을 확인했다. 일반 텍스트 대비4.5:1, 큰 텍스트3:1 등 선택된 기준을 UI 설계 참고로 사용한다. 팔레트 일부의 대비 계산을 전체앱 WCAG 적합성 인증으로 표시하지 않는다. sourceId: `w3c-wcag22`. 실제 앱 대비 측정은 별도 `evidence/accessibility-checks.json`에 기록되어야 하며 이 출처 조사는 측정 실행을 대신하지 않는다.


2026-09-14 추가 경계 재확인: [Oracle 19c SELECT](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/SELECT.html)의 row_limiting_clause 설명을 다시 읽었다. WITH TIES의 동점 추가 행을 정하려면 ORDER BY 정렬 키가 필요하며, 같은 문서에는 ORDER BY를 생략하면 추가 행을 반환하지 않는다고도 적혀 있다. 따라서 Oracle 문항에서 ORDER BY 생략을 곧바로 문법 오류·실행 불가로 단정하지 않는다. 동점 추가 반환 의도를 충족할 조건으로 질문을 한정한다. 이 확인은 실제 SQL 실행 결과가 아니다.


Android 백업 근거 `android-auto-backup`도 [Android 공식 Auto Backup 문서](https://developer.android.com/identity/data/autobackup)에서 실제 확인했다(페이지 갱신 2026-02-26). API31+ XML의 cloud-backup과 device-transfer 양쪽에 root/file/database/sharedpref/external 및 device_root/device_file/device_database/device_sharedpref 도메인이 허용된다. 각 모드는 별도 규칙을 가지므로 한 절의 제외가 다른 절로 자동 적용되지 않는다. 일부 제조사의 API31+ 앱에서는 allowBackup=false만으로 D2D 이전이 중단되지 않을 수 있다. 이 근거는 XML 구성 판단이며 실제 제조사 D2D 수행 검증과 다르다.
