# 그림과 강의 연결표

작성일: 2026-09-29. 상태: **정본에 적용 완료**. `content/course-visuals.json`의 `2026.09.29.1`을 현재 표시 기준으로 사용하고, [제공 manifest](../content/visual-source/manifest.json)의 그림별 `lesson_ids`와 정확히 대조했다.

그림은 **27개**, 그림→강의 연결은 **45건**, 연결된 서로 다른 강의는 **40강**이다. 나머지 **23강**도 원래63강 안에 그대로 있으며 그림 연결이 없다는 이유만으로 내용 누락으로 처리하지 않는다. 여러 강의에서 같은 그림을 함께 사용하는 연결은 의도된 재사용이다. 같은 그림을 같은 강의에 중복 배치하는 것은 허용하지 않는다.

그림의 원본 PNG 비율은8:5이고 통합 자산은2400×1500이다. 강의 화면에서 해당 그림만 연결하며, 기존 개념도와 표·SQL·결과표는 유지한다. 실제 글자 가독성·확대·스크롤의 최종 기기 판정은 [QA](QA.md)의 증거 범위를 따른다.

## 27개 그림의 연결

그림 ID는 `visual-01`부터 `visual-27`까지 유지한다. 아래 파일은 현재 앱에 표시하는 통합 자산이다. 각 행의 제목·연결은 정본에서 읽었으며 SQL 결과가 기존 예제와 같은 입력을 사용한다는 뜻은 아니다.

| 그림 ID | 제목 | 연결 강의 ID · 제목 | 연결 수 | 현재 PNG / SVG |
|---|---|---|---|---|
| visual-01 | DBMS는 중간에서 데이터를 관리한다 | 1-1-01 데이터베이스의 개념 | 1 | [PNG](../content/course-visuals/visual-01.png) / [SVG](../content/course-visuals/visual-01.svg) |
| visual-02 | 모델링: 현실의 일을 저장 구조로 바꾼다 | 1-1-02 데이터 모델링; 1-1-03 데이터 모델링과정 | 2 | [PNG](../content/course-visuals/visual-02.png) / [SVG](../content/course-visuals/visual-02.svg) |
| visual-03 | 스키마 3단계: 같은 DB를 보는 세 관점 | 1-1-04 스키마구조 3단계 | 1 | [PNG](../content/course-visuals/visual-03.png) / [SVG](../content/course-visuals/visual-03.svg) |
| visual-04 | ERD: 학생–수강–과목을 선으로 연결한다 | 1-1-05 ERD; 1-1-08 관계 | 2 | [PNG](../content/course-visuals/visual-04.png) / [SVG](../content/course-visuals/visual-04.svg) |
| visual-05 | 속성은 항목, 튜플은 정보 한 줄 전체 | 1-1-06 엔터티; 1-1-07 속성; 1-2-01 관계형 데이터베이스 개념 | 3 | [PNG](../content/course-visuals/visual-05.png) / [SVG](../content/course-visuals/visual-05.svg) |
| visual-06 | PK는 구별하고, FK는 다른 표를 참조한다 | 1-1-09 식별자; 1-2-02 키(Key) | 2 | [PNG](../content/course-visuals/visual-06.png) / [SVG](../content/course-visuals/visual-06.svg) |
| visual-07 | 1:1 · 1:N · N:M: 몇 개까지 연결되는가? | 1-1-08 관계 | 1 | [PNG](../content/course-visuals/visual-07.png) / [SVG](../content/course-visuals/visual-07.svg) |
| visual-08 | 무결성: 넣기 전에 규칙을 통과해야 한다 | 1-2-03 무결성 제약조건; 2-1-03 제약조건 | 2 | [PNG](../content/course-visuals/visual-08.png) / [SVG](../content/course-visuals/visual-08.svg) |
| visual-09 | 정규화: 반복되는 이유를 찾아 표를 나눈다 | 1-2-05 정규화의 필요성과 이상 현상; 1-2-06 정규형 | 2 | [PNG](../content/course-visuals/visual-09.png) / [SVG](../content/course-visuals/visual-09.svg) |
| visual-10 | 이상 현상: 한 표에 섞어 넣어서 생기는 문제 | 1-2-05 정규화의 필요성과 이상 현상 | 1 | [PNG](../content/course-visuals/visual-10.png) / [SVG](../content/course-visuals/visual-10.svg) |
| visual-11 | ALTER: 데이터 값이 아니라 표 구조를 바꾼다 | 2-1-04 ALTER~RENAME | 1 | [PNG](../content/course-visuals/visual-11.png) / [SVG](../content/course-visuals/visual-11.svg) |
| visual-12 | NULL은 0점이 아니다 | 2-1-15 NULL의 개념과 처리방식(1); 2-1-16 NULL의 개념과 처리방식(2); 2-1-17 NULL관련 함수 | 3 | [PNG](../content/course-visuals/visual-12.png) / [SVG](../content/course-visuals/visual-12.svg) |
| visual-13 | INNER JOIN: 조건이 맞는 행끼리 짝짓기 | 2-1-22 JOIN의 개념; 2-1-25 ANSI 표준 조인 | 2 | [PNG](../content/course-visuals/visual-13.png) / [SVG](../content/course-visuals/visual-13.svg) |
| visual-14 | OUTER JOIN: 짝 없는 행도 남긴다 | 2-1-23 OUTER JOIN | 1 | [PNG](../content/course-visuals/visual-14.png) / [SVG](../content/course-visuals/visual-14.svg) |
| visual-15 | CROSS JOIN: 한 명마다 모든 과목과 짝짓기 | 2-1-24 CROSS JOIN & SELF JOIN; 2-3-04 관계대수 | 2 | [PNG](../content/course-visuals/visual-15.png) / [SVG](../content/course-visuals/visual-15.svg) |
| visual-16 | SELF JOIN: 같은 사원표를 두 역할로 읽는다 | 2-1-24 CROSS JOIN & SELF JOIN | 1 | [PNG](../content/course-visuals/visual-16.png) / [SVG](../content/course-visuals/visual-16.svg) |
| visual-17 | 서브쿼리: 전체 기준과 현재 행의 기준을 구분 | 2-2-01 서브쿼리의 개념과 분류; 2-2-05 스칼라&인라인뷰&상관 서브쿼리 | 2 | [PNG](../content/course-visuals/visual-17.png) / [SVG](../content/course-visuals/visual-17.svg) |
| visual-18 | GROUP BY: 행을 묶은 뒤 그룹 하나로 요약한다 | 2-1-19 집계 함수; 2-1-20 GROUP BY; 2-1-21 HAVING | 3 | [PNG](../content/course-visuals/visual-18.png) / [SVG](../content/course-visuals/visual-18.svg) |
| visual-19 | ROLLUP: 오른쪽 항목부터 접어 소계를 만든다 | 2-2-07 ROLLUP; 2-2-09 GROUPING 함수 | 2 | [PNG](../content/course-visuals/visual-19.png) / [SVG](../content/course-visuals/visual-19.svg) |
| visual-20 | CUBE: 가능한 묶음 조합을 모두 집계한다 | 2-2-08 CUBE & GROUPING SETS; 2-2-09 GROUPING 함수 | 2 | [PNG](../content/course-visuals/visual-20.png) / [SVG](../content/course-visuals/visual-20.svg) |
| visual-21 | 윈도우 함수: 행을 없애지 않고 계산값을 붙인다 | 2-2-10 윈도우 함수의 개념 OVER절; 2-2-12 집계 윈도우 함수 | 2 | [PNG](../content/course-visuals/visual-21.png) / [SVG](../content/course-visuals/visual-21.svg) |
| visual-22 | 순위 함수: 동점 뒤 번호를 어떻게 붙이는가? | 2-2-11 순위 함수 | 1 | [PNG](../content/course-visuals/visual-22.png) / [SVG](../content/course-visuals/visual-22.svg) |
| visual-23 | 계층형 질의: 부모에서 자식으로 내려간다 | 2-2-15 계층형 질의 탐색원리; 2-2-16 계층형 질의 활용 | 2 | [PNG](../content/course-visuals/visual-23.png) / [SVG](../content/course-visuals/visual-23.svg) |
| visual-24 | PIVOT · UNPIVOT: 세로와 가로의 모양을 바꾼다 | 2-2-17 PIVOT & UNPIVOT | 1 | [PNG](../content/course-visuals/visual-24.png) / [SVG](../content/course-visuals/visual-24.svg) |
| visual-25 | 트랜잭션: 모두 확정하거나 모두 취소한다 | 2-3-02 트랜잭션과 TCL | 1 | [PNG](../content/course-visuals/visual-25.png) / [SVG](../content/course-visuals/visual-25.svg) |
| visual-26 | DCL: 데이터가 아니라 사용 권한을 바꾼다 | 2-3-03 DCL | 1 | [PNG](../content/course-visuals/visual-26.png) / [SVG](../content/course-visuals/visual-26.svg) |
| visual-27 | 순수 관계 연산자 4개를 그림으로 기억한다 | 2-3-04 관계대수 | 1 | [PNG](../content/course-visuals/visual-27.png) / [SVG](../content/course-visuals/visual-27.svg) |

그림20은 과목 소계→전체 합계 화살표 문구를 ‘과목 제거’로 정정한 표시본이다. [원래 PNG](../content/course-visuals/originals/visual-20.png)와 [원래 SVG](../content/course-visuals/originals/visual-20.svg)는 별도 보존했다. 표·수치·SQL의 결과는 바꾸지 않았다.

## 연결 없는23강과 처리 이유

각 강의는 기존 표·SQL·풀이·결과·자기점검을 유지한다. 전수 검토에서 이번 통합에 별도 그림 제작이 필수라고 판정한 강의는 없다. 아래 판정은 현재 자료에 대한 설명 방식의 판단이며 모든 학습자에게 그림이 불필요하다는 실험 결과는 아니다.

| 강의 ID | 제목 | 처리 이유 |
|---|---|---|
| 1-2-04 | SQL의 분류 | 27장 중 SQL 명령 분류 그림은 없다. CREATE·INSERT·GRANT·COMMIT의 기존 비교표가 직접적인 설명 수단이므로 추가 그림을 억지로 배치하지 않는다. |
| 1-2-07 | 반정규화 | 반정규화 전용 그림이 없다. 주문상세·합계표의 계산이 핵심이며 정규화 그림9를 반대 방향으로 읽게 하지 않는다. |
| 2-1-01 | DDL의 개념과 CREATE문 | 27장은 CREATE가 아닌 ALTER와 제약 그림을 제공한다. 이 강의는 빈 결과표와 CREATE SQL로 구조 생성 자체를 설명한다. |
| 2-1-02 | 자료형 | 자료형 전용 그림이 없다. 기존 문자/숫자 정렬 결과표와 정밀도 판정표를 그대로 사용한다. |
| 2-1-05 | INSERT | INSERT 전용 그림은 없다. 변경 전후 표와 값 순서 설명이 충분하며 ALTER 그림은 행 추가와 혼동될 수 있어 연결하지 않는다. |
| 2-1-06 | SELECT 기본구조 | 27장에 SELECT 전체 흐름 전용 그림이 없고 관계대수 그림27은 별도 강의에 연결되어 있다. 기존 정정된 논리 순서 도해를 사용한다. |
| 2-1-07 | WHERE절 기본 | WHERE 전용 그림이 없다. 실제 고객표와 TRUE/FALSE 판정·괄호 반례로 충분하다. |
| 2-1-08 | UPDATE | UPDATE 전용 그림이 없다. ALTER 그림을 값 변경 예제에 배치하면 구조/값 구분을 흐릴 수 있어 전후 표를 유지한다. |
| 2-1-09 | DELETE | DELETE/CASCADE 전용 그림은 없다. 기존 삭제 전후 표와 C02 참조 행 추적이 더 직접적이다. |
| 2-1-10 | MERGE | MERGE 전용 그림이 없다. 최종성적·새성적·변경 후 표 세 개와 번호별 처리로 충분하다. |
| 2-1-11 | WHERE절 | 27장에 WHERE/LIKE 전용 그림이 없다. 기존 조건별 결과표가 핵심이고 이름의 길이가 모두 같다는 주의도 보존한다. |
| 2-1-12 | ORDER BY & DISTINCT | 정렬·DISTINCT 전용 그림이 없다. 기존 세 조합 결과표와 순위 전후 표를 사용하며 순위 함수 그림과 혼합하지 않는다. |
| 2-1-13 | 단일행함수(1) | 단일행함수 전용 그림이 없다. 입력 문자열/수직선 의미를 기존 값·결과표로 설명하며 원래 도해는 유지한다. |
| 2-1-14 | 단일행함수(2) | 날짜 함수 그림이 없다. 고정 기준일과 네 결과 열을 비교하는 표가 충분하며 다른 날짜로 임의 변경하지 않는다. |
| 2-1-18 | CASE & DECODE | CASE 전용 새 그림은 없다. 이미 필터 오해를 교정한 기존 도해와4행 결과표가 있으므로 관계없는 그림을 더하지 않는다. |
| 2-2-02 | 단일행 서브쿼리 | 그림17은 전체 평균과 상관 평균을 비교하며 단일행의 0행·다중행 경계를 직접 설명하지 않는다. 기존 두 결과표를 유지한다. |
| 2-2-03 | 다중행 서브쿼리 | 다중행 비교와 NULL 목록의 전용 그림이 없다. 기존 급여 결과표와 3값 논리 단계가 직접적인 판정 자료다. |
| 2-2-04 | 다중컬럼 서브쿼리 | 다중컬럼 그림은 없다. 기존 입력표의 학과·점수를 한 쌍으로 읽는 것이 핵심이므로 상관 평균 그림을 끼워 넣지 않는다. |
| 2-2-06 | 집합 연산자 | 집합 연산자 전용 그림이 없다. 관계대수 그림27은 다른 연산 중심이므로 기존 네 결과표를 유지한다. |
| 2-2-13 | 기타 윈도우 함수 | 새 그림21은 그룹 평균을 각 행에 붙이는 비교이고 그림22는 순위 함수다. LAG/LEAD/LAST_VALUE의 다른 의미를 섞지 않고 기존 결과표를 유지한다. |
| 2-2-14 | TOP-N쿼리 | 그림22는 번호 부여 방식만 설명한다. 행 제한의 쿼리 단계와 WITH TIES 조건은 기존 두 SQL이 직접 보여주므로 별도 연결하지 않는다. |
| 2-2-18 | 정규 표현식 함수 | 정규식 전용 그림이 없다. 입력 문자열·패턴·판정표로 규칙을 구체적으로 읽을 수 있다. |
| 2-3-01 | 뷰의 개념과 활용 | 뷰 전용 그림은 없다. 기존90·70·80점 원본과80점 이상 조회표의 대조가 충분하다. |

## 같은 그림을 다른 강의에서 읽을 때

그림12는 NULL·3값 논리·대체 함수 세 강의의 출발점이다. 기존 각 강의의 점수표와 입력 인물·숫자는 다르므로 그림의 평균이나 COUNT를 다음 SQL의 답으로 사용하지 않는다. 그림18도 집계 함수·GROUP BY·HAVING의 공통 그림이지만 원래 예제는 각자 독립적인 입력과 조건을 사용한다.

그림19·20은 총계100을 쓰고 기존 ROLLUP/CUBE 예제는 총계1000을 쓴다. 그림21은 GROUP BY의2행과 AVG OVER의4행을 비교하며 누적 프레임을 직접 그린 자료가 아니다. 집계 윈도우 강의의 ROWS/RANGE 누적은 기존 SQL·결과표에서 이어서 읽는다. 그림16의 INNER SELF JOIN과 기존2-1-24-E02의 LEFT SELF JOIN은 최상위 관리자를 남기는지 다르다.

강의의 `exampleReadingGuide`는 결과를 포함할 수 있다. 앱에서는 **모든 예제 결과를 펼친 후에만 ‘그림과 예제 비교 해설’로 표시**한다. 풀이 전에는 다른 데이터로 전환한다는 중립적인 안내만 보인다. 비교 해설은 풀이 후 보충 설명으로 배치하며, 기존 단계별 예측·결과 공개 동선을 유지한다.

읽는 순서·판정 이유·주의·색의 의미는 이미지 밖 텍스트로도 제공한다. 색은 그림마다 범례가 다르므로 특정 색을 언제나 정답이나 탈락으로 통일해 해석하지 않는다. 정적인 그림의 화살표·번호는 실제 애니메이션이나 SQL 엔진 실행 증거가 아니다.

## 자료 및 검증 경계

[강의별 변경 목록](visual-lesson-changes.md), [최초63강 AI 검토](../evidence/visuals-lesson-review.json), [그림 검증기](../scripts/validate_visuals.py), [실패 경로 회귀 검사](../scripts/test_visual_content.py)를 함께 참조한다. 연결 검사는 전체 연결 수뿐 아니라 각 그림의 강의 ID가 제공 manifest와 일치하는지도 확인한다.

이 연결표는 적용된 콘텐츠 관계를 기록한다. 독립 AI 내용 검토와 데이터·파일 검사는 사람 전문가 검수, 공식 출제 빈도 조사 또는 학습효과 검증이 아니다. 최종 Android 실행 및 실기기 미검증 항목은 [QA](QA.md)에 분리해 기록한다.
