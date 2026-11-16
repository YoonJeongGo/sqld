# SQL 노트 기능 QA 기준선 — 2026-10-05

목적: 승인된 Canva 기반 Compose 디자인을 유지하면서 실제 클릭, 학습, 저장, 재개, 복원 동작을 확인한다. 휴리스틱 평가는 사용자 조사와 구별한다. 신규 PDF 뷰어, 영상 재생기, SQL 엔진은 이번 수정 범위가 아니다.

## 변경 전 상태
- Kotlin/Compose/Material3, Room schema 1, DataStore 설정 투영. 앱 0.6.0 / code 11 / minSdk26 / target35.
- Git 저장소 없음. 소스·자료 238파일을 `backups/product-functional-qa-before-20261005.zip`에 보존. SHA256 목록: `evidence/product-functional-qa-20261005/source-before.json`.
- 에뮬레이터 SQLNote_QA / emulator-5590 / API34. 실제 Galaxy 검증 아님. user0 학습기록은 UI 백업 보존, 신규 user10에서 출시판 동작 검증.
- 원본 개인 백업은 private-user0-before-backup.json. 공개 산출물/ZIP에 포함하지 않는다.
- 실제 기능: 계획 날짜/5·6시간 선택 및 자료 연결, 63강 읽기/예제/자기점검, 41개 노트/필기, 일반 연습/채점/해설/별표/복습, 창작 모의고사/타이머, 검색, 설정/백업 검사·복원·복구 지점.
- 정적인 안내: 보유 PDF 쪽수, 외부 수강 영상 제목, 정적 그림, 사전에 작성된 SQL 처리 단계. 앱 내 PDF/강의 재생/SQL 엔진은 없음.

## 변경 전 검증
| 항목 | 결과 | 근거 |
|---|---|---|
| JVM 단위 테스트 | PASS 76, 캐시 없이 재실행 | baseline-unit-summary.json, TEST-*.xml |
| Debug / AndroidTest APK / Release 빌드 | PASS | baseline-build.log의 해당 tasks |
| Debug / Release lint | FAIL | 한국어 SDK 경로의 올바른 Java properties Unicode escape를 PropertyEscape가 오진. 1오류/4경고. baseline-lint-*.txt |
| Kotlin 타입/컴파일 | PASS | 두 변형 assemble 작업 |
| 별도 formatter | 구성 없음 | 루트·app Gradle 설정. 실행한 것으로 표기하지 않음 |
| 콘텐츠 구조/강의/그림 검증 | PASS | validate_content.py --strict, validate_course.py, validate_visuals.py exit0. 661문항/63강/95예제/189자기점검/27그림 |
| 실제 DBMS SQL, 전문가/학습효과/공식범위 | NOT VERIFIED | 구조 검증과 별도 |
| 기존 Android 통합/UI 전체 | PASS 56/56, skip0, 84.05초 | runtime/baseline-all-android-instrumentation.log |
| 출시판 기준선 실제 클릭 | PASS 선택·중복채점 후 제출1개 | 별도 user10 실제 UI 내보내기; 이후 확장 경로는 AFTER에 구분 |

## 제품 가정
개인 학습자는 이미 강의/PDF를 보유하며 앱은 복습 보조 역할을 한다. 중요도 표시는 강사·자료 근거이며 실측 공식 출제율이 아니다. 문제 반복과 저장된 오답은 재방문 이유가 될 수 있으나 실제 학습 전이·합격률은 입증하지 않았다. 오프라인 개인 사용 외 공개 배포·결제·광고·계정은 비대상이다.

## 실제 감사 구성
FUNCTION_DATA_RELIABILITY_AUDITOR: threeway_sql_advanced (ADB 단독).
PRODUCT_VALUE_RED_TEAM 및 SECURITY_POLICY_RELEASE_AUDITOR: product_value_red_team, 역할 순차 수행.
FIRST_TIME_USER_AUDITOR / REPEAT_USER_FRICTION_AUDITOR / ACCESSIBILITY_RECOVERY_AUDITOR: threeway_sql_basic, 역할 순차 수행.
동시 thread 제한으로 모든 역할마다 별도 새 agent를 만들지는 못했다. 수행하지 않은 독립성은 주장하지 않는다. 소스 수정 담당자는 root 한 명이다.

기준선 완료 보충: Python 63/63 PASS(exit0), Android 전체 56/56 PASS(skip0,84.05초). Release 전용사용자에서 중복채점 2회→export 결과 제출1개/세션1개, checksum PASS. 나머지 실제 경로는 수정 후 재검증에 포함한다.
