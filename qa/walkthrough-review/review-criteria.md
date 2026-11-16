# SQL 따라읽기 독립 검토 기준

검토일: 2026-10-06. 코드/원문/공식 문서의 독립 AI 검토이며 사람 검수나 Oracle 실행 증거가 아니다.

## 기존 구조와 보존 경계

- `content/part-a.json`, `part-b.json`: 문제 661개 중 SQL이 있는 문제 217개이며 모두 Oracle 19c를 명시한다. SQL이 없는 나머지 444개에 가짜 실행 과정을 만들지 않는다.
- 기존 `SessionScreen`은 `submission != null`인 경우에만 해설을 표시한다. 새 설명, 현재 구문 강조, 중간 결과표도 이 공개 조건을 따라야 한다.
- 문제 세션은 `Question` 전체 snapshot을 보존한다. 새 자료 연결은 ID만으로 충분하지 않으며 원문 SQL, 표, 문제 조건이 다르면 거부해야 한다.
- 기존 `Annotation`은 개념노트 문구에 대한 강조/메모다. SQL 필기는 별도 자료이며, 같은 문제 ID라도 SQL 또는 입력표가 달라지면 좌표를 공유하면 안 된다. 회전/스크롤/확대는 같은 문서 좌표를 표시하는 방식만 바꿔야 한다.

## 실제 Oracle 환경 읽기 검사

- `Get-Command sqlplus,sql,sqlcl,tnsping,docker,podman`: 모두 발견되지 않았다.
- Oracle/Docker 이름의 Windows 서비스: 발견되지 않았다.
- `C:\app`, `D:\app`, `C:\Oracle`, `D:\Oracle`, 두 Program Files의 Oracle 디렉터리: 존재하지 않았다.
- `HKLM:\SOFTWARE\Oracle`, `HKLM:\SOFTWARE\WOW6432Node\Oracle`: 존재하지 않았다.
- 한정된 설치 흔적 검사다. 전체 디스크 조사 또는 모든 원격 DB의 부재 증거는 아니다. Oracle 19c SQL 실제 실행은 **미실행**. 새 DB 설치/다운로드/로그인/전송은 하지 않았다.

## 적용 유형별 검토 원칙

| 유형 | 값/순서 검증 | 피할 오류 | 공식 근거 |
|---|---|---|---|
| WHERE와 NULL | 각 행의 값을 조건에 대입하고 TRUE만 남기는지 검사한다. UNKNOWN과 FALSE를 구분한다. | NULL=0, NULL=NULL, NOT UNKNOWN=TRUE로 단순화 | [Nulls](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Nulls.html) |
| 집계 | COUNT(*)의 모든 행, COUNT(expr)의 NULL 제외, AVG의 분모, 빈 집계 입력을 대조한다. | 외부 조인의 NULL 확장행을 COUNT(*)에서 지움, AVG에서 NULL을 0으로 계산 | [COUNT](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/COUNT.html), [Aggregate Functions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Aggregate-Functions.html) |
| JOIN | 일치하는 모든 왼쪽/오른쪽 행쌍을 세며 중복을 유지한다. 미일치 외부 행은 상대 열을 NULL로 채운다. ON 결과와 후속 WHERE를 구별한다. | PK를 선언하지 않은 열을 유일하다고 가정, ON과 WHERE를 교환해 동일 결과라 단정 | [Joins](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Joins.html) |
| GROUP BY/HAVING | 그룹 구성원, 그룹별 실제 계산, HAVING 통과값을 각각 검사한다. | GROUP BY만으로 정렬 보장, HAVING을 원본 개별 행 필터처럼 설명 | [SELECT](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/SELECT.html), [Aggregate Functions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Aggregate-Functions.html) |
| 서브쿼리 | 외부 행별 상관값 또는 독립 서브쿼리 결과를 명시한다. 스칼라는 0행→NULL, 1행→값, 2행 이상→오류를 구분한다. | 개념적 행별 계산을 실제 물리 실행 횟수로 표현 | [Using Subqueries](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Using-Subqueries.html), [Scalar Subquery](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Scalar-Subquery-Expressions.html) |
| IN/NOT IN | 목록에 일치값이 있는지, NULL로 UNKNOWN이 남는지 각 행별 대조한다. 빈 목록/서브쿼리도 구별한다. | NOT IN 목록에 NULL이 있으면 모든 행이 UNKNOWN이라고 단정. 일치하는 행은 FALSE일 수 있다. | [IN Condition](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/IN-Condition.html) |
| 윈도 함수 | JOIN/WHERE/GROUP BY/HAVING 뒤의 입력, partition, 정렬키, frame, 동률을 각각 검사한다. | OVER ORDER BY가 최종 행 순서를 보장, ROW_NUMBER 동률을 항상 고정 순위라 설명 | [Analytic Functions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Analytic-Functions.html) |
| 집합 연산 | 양쪽 SELECT 결과, 중복 제거 여부, 열 위치/타입을 대조한다. Oracle 19c의 우선순위와 괄호를 따른다. | UNION ALL 중복 제거, SQL 결과를 값 집합으로만 비교해 중복 개수를 잃음 | [Set Operators](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/The-UNION-ALL-INTERSECT-MINUS-Operators.html) |
| 최종 결과 | 최상위 ORDER BY가 없으면 bag(중복을 포함한 행 묶음)으로 비교한다. 정렬키가 같은 행의 상대순서를 확정하지 않는다. | SQLite의 우연한 출력순서나 GROUP BY 정렬을 Oracle 보장처럼 제시 | [SELECT](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/SELECT.html) |

공식 웹페이지는 위 URL을 실제 열어 대조했다. 외부 사이트 SQL 예제를 복사한 새 문제는 만들지 않는다.

## SQLite 독립 검산 범위

SQLite로 실행할 경우 실제 엔진명/버전을 별도 표시하고 Oracle 19c 미실행을 유지한다. Oracle 전용 문법을 바꿔 실행하거나 함수 어댑터/정렬 보정을 썼다면 변환 쿼리와 변환 이유를 기록한다. 결과가 원본 fixture와 같아도 Oracle 문법/타입/빈 문자열/NLS/NULL 정렬까지 검증되었다고 할 수 없다. 불확실한 문항은 기존 해설을 유지하고 새 단계 해설 적용에서 제외한다.

## UI/기록 검토 항목

- 태블릿 최종 사용자 지시인 **왼쪽 해설·오른쪽 SQL**을 우선하며 작은 화면에서도 해당 단계 SQL과 설명을 동시에 확인할 수 있어야 한다.
- 일반 객관식 한 화면화는 화면/글꼴 크기 안에서 가능한 경우에만 적용한다. 최소 터치영역 또는 가독성을 희생해 억지로 전부 넣지 않는다.
- 단계/기초 펼침 상태는 saveable key가 세션+문항+자료 버전에 묶이는지 확인한다. 이전/다음과 회전 후 같은 단계로 복원되어야 한다.
- 강조는 원문을 변경하지 않는 범위 참조로 연결한다. 구문 부분 강조가 실제 문자열 위치에 존재해야 하며 정답 공개 전에는 결과를 암시하지 않아야 한다.
- 펜 저장은 원문 fingerprint, 문서 좌표, stroke 순서, 지우기/되돌리기, 저장 실패 시 초안 보존, 백업 검증과 원자 복원을 검사한다.
- 최종 실제 화면/기기 터치/실물 S Pen 검증은 root 실행 결과와 구분한다. 이 문서만으로 UI 동작 완료를 주장하지 않는다.
