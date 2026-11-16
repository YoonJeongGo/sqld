# 63강 학습자료 통합 콘텐츠 검토

검토일: 2026-09-28. 대상은 사용자가 제공한 `SQLD_63강_Canva_Codex_전체.zip`의 `data/content.json` 및 강의별 SVG이다. 원본 추출 폴더는 수정하지 않았다.

## 수록 범위와 진도

5개 단원, 63강, 490개 개념 항목, 95개 예제, 입력·결과 표 223개, SQL 코드 70개, 도해 63개, 자기점검 189개를 별도 `course-pack.json`으로 수록한다. 원자료의 강의 시간 합계는 1,932분이며 영상은 포함하지 않는다. 표의 숫자는 Android 표시 모델에 맞춰 문자열로 저장하고 NULL은 NULL로 보존한다. 63강의 순서와 예제·자기점검 ID는 원자료의 ID를 유지한다.

이 자료는 사용자가 제공한 강의 목차에 맞춘 창작 학습자료이다. 강사 영상·교재의 전문이나 공식 기출문제로 표시하지 않는다. 기존 41개 개념 노트는 보존하며 다대다 연결한다. 별도 강의가 없는 본질식별자/인조식별자 노트도 식별자·키 강의에서 연결한다.

189개 자기점검은 단답형 답을 펼쳐 본 뒤 스스로 이해 상태를 표시하는 활동이다. 기존 661개 선택형 문제와 별도이며, 문제풀이 정답률이나 모의고사 점수에 합산하지 않는다. 강의 읽음 표시는 영상 수강 인증 또는 숙달 판정이 아니다.

## 수정한 의미·도해

| 강의 | 수정 | 근거/판정 |
|---|---|---|
| 1-2-03 무결성 | 도해의 `TRUE만 통과`를 CHECK의 `FALSE이면 거부`, `TRUE · UNKNOWN 허용`으로 교정 | [Oracle 19c constraint](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/constraint.html)의 Check Constraints 절을 현재 확인. NOT NULL은 별도 제약이다. |
| 2-1-18 CASE | 필터처럼 보이던 `통과한 행 표시`를 행마다 출력값을 계산하는 흐름으로 교정 | [Oracle CASE Expressions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CASE-Expressions.html)를 현재 확인. 위에서 첫 TRUE인 분기의 결과를 택하고, 해당 분기가 없으면 ELSE 또는 NULL을 반환한다. |
| 2-2-09 GROUPING_ID | 모호한 `a소계`를 `a가 집계 기준에서 제외되면`으로 교정. 계산식을 `GROUPING(a) × 2 + GROUPING(b)`로 명시 | [Oracle GROUPING_ID](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/GROUPING_ID.html)를 현재 확인. 왼쪽 인자가 높은 비트다. 지역 소계는 과목을 제외하므로 `(0,1)`이며 ID 1이다. |
| 2-1-06, 2-1-21 | 논리 처리 순서 도해에 ORDER BY 추가 | FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY로 설명. 실제 실행계획과 같다고 주장하지 않는다. |
| 2-1-13, 2-2-03, 2-3-02 | 도해 마지막 암기 문장이 생략되던 부분 복구 | 함수의 FLOOR 설명, NOT IN의 NULL 주의, 송금의 원자성을 끝까지 표시한다. |
| 여러 강의 | 사람 이름 뒤 잘못된 조사 수정 | 이름에 붙은 독립 조사만 제한적으로 수정한다. SQL 및 모든 표 값은 원문과 동일함을 검사한다. |

세부 수정 경로와 전후 텍스트/도해 해시는 `evidence/course-content-import.json`에 있다. 기존 원자료의 검증 표시는 출처 설명으로 남기며, 현재 검증 결과와 혼합하지 않는다.

## 실제 검증

`scripts/import_course.py`는 원자료의 데이터와 SVG만 읽는다. ZIP의 Python/JavaScript/명령 스크립트는 실행하지 않는다. `scripts/validate_course.py`는 스키마, 안정 ID, 단원 순서, 41개 기존 노트 참조, 출처 참조, 필수 답·해설, 표의 직사각형 구조, 모든 셀의 문자열/NULL 형식과 수량, 정규화된 저작 소스와 앱 asset의 바이트 일치를 검사한다. SVG는 허용한 정적 태그만 허용하고 script, foreignObject, 이벤트, 외부 링크, CSS, DTD/ENTITY를 거부한다.

`python scripts/validate_course.py --engine`은 새로 작성한 검증기로 메모리 SQLite를 사용한다. 원자료의 표 리터럴에서 테이블을 구성하며 원자료 setup SQL은 실행하지 않는다. ATTACH/PRAGMA/확장 로드/파일 함수를 차단하고 실행량과 결과 행 수를 제한한다. 표시된 SQL 50개를 그대로 실행하고, Oracle 예제 10개는 별도 SQLite 대체식으로 계산한다. 결과는 NULL, 열 수, 값, 중복 개수 및 명시된 최상위 ORDER BY 순서까지 비교한다. 실행한 엔진 버전과 예제별 결과는 `evidence/course-content-engine.json`에 기록된다.

대체식 성공은 Oracle 문법·Oracle 실행계획·Oracle 타입 동작이 검증됐다는 뜻이 아니다. 나머지 35개 이론/Oracle 예제는 SQL 실행 미실시로 남긴다. 앱은 학습용 정적 표·해설을 표시하며 SQL 엔진을 실행하지 않는다.

`python scripts/test_course_content.py`는 원본·현재 pack 재현성, 표/SQL 보존, 모든 기존 노트 연결과 잘못된 참조/답/표/도해 차단을 확인한다. 또한 예상 정답 변조, 중복 결과 손실, 위험 SQL, 무한 재귀가 실패하는지 확인한다. 일반 SQL 테스트 성공만을 콘텐츠 전문가 검수라고 부르지 않는다.

## 증거 구분과 남은 범위

- 원자료 작성·원자료의 자체 검증 주장: 입력 자료에 포함된 기록.
- 현재 구조/회귀 검사와 SQLite 실행: 위 명령의 실제 출력과 JSON 증거.
- 현재 AI 의미 검토: 위 세 가지 오류와 도해/문장 수정, 관련 표·단답 해설의 일관성 확인.
- 사람 전문가의 63강 전수 검수, 실제 Oracle/SQL Server 실행, 공식 출제 빈도 분석, 수험생 학습 효과/합격 가능성 검증: 미실시.

재현 명령:

```powershell
python scripts/import_course.py  # 원본 추출 폴더가 있을 때만 재가져오기
python scripts/validate_course.py
python scripts/validate_course.py --engine
python scripts/test_course_content.py
```

배포 소스에 원본 ZIP이 없더라도 `content/course-pack.json`과 `evidence/course-content-fixtures.json`으로 구조·엔진 검사를 반복할 수 있다. 원본과의 비교 두 검사는 원본이 없으면 SKIP을 명시한다.
