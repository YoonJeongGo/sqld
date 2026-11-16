# SQL 따라읽기 독립 검토 결과

검토: 2026-10-06~07, 독립 AI 검토 담당. 기존 앱과 원문을 읽고 별도 해설 자료·모델·화면·필기 경계를 검토했다. 원문 콘텐츠/앱 구현은 수정하지 않았고, 독립 검사와 테스트 코드 및 테스트 진입 동작만 작성·보정했다.

## 결론과 범위

기존 문제를 다시 작성하지 않고 **원문과 정확히 일치할 때만 별도 해설을 연결하는 방식**이 적절하다. 현재 연결된 133문항의 원문 스냅샷·최종 결과·구조 검사를 통과했으며, 49개의 명시적 중간값/유형별 비교와 사용자 예시의 독립 계산도 통과했다. 이는 모든 설명 문장의 사람 검수나 Oracle 실행, 학습 효과 검증을 뜻하지 않는다.

| 대상 | 현재 확인 결과 |
|---|---|
| 기존 문제 | 661개 유지. 별도 SQL 필드가 있는 217개 중 133개 적용, 84개는 기존 해설 유지 |
| 새 해설 | 133문항 849단계 + 별도 학습 예시 1개 26단계 = 875단계 |
| SQL 필드 없는 문제 | 444개. 이 수가 전부 순수 개념 문제라는 뜻은 아니다. 본문/보기 안 SQL은 별도 SQL 필드 적용 수에 포함하지 않았다 |
| 기존 자산 | 기준 백업 목록에 있던 content/·app assets·Room schema 131개 SHA-256 동일, 변경·삭제 0개 |
| 비교 엔진 | SQLite 3.50.4. Oracle 전용 구문 변환·숫자 함수 어댑터·NULL 정렬 보정을 명시한 별도 검산 |
| Oracle 19c 실제 실행 | 미실행. 설치 명령·서비스·대표 경로·레지스트리 읽기 검사에서 환경을 발견하지 못함 |

## 실제 실행한 독립 검사

- `python qa/walkthrough-review/review_reference_example.py`: PASS. 사용자 EMPLOYEE 6행에 대해 NOT IN, > ANY, AND의 TRUE/FALSE/UNKNOWN을 독립 Python 값 계산으로 구했다. SQLite의 명시적 변환 쿼리와 결과 0행이 일치한다. `UNKNOWN AND FALSE`는 FALSE임을 따로 확인했다.
- `python qa/walkthrough-review/review_generated.py`: PASS. 133개 자료/849단계의 원문 일치·asset 일치·강조 위치·표 직사각형·셀 범위·최종 결과를 전수 검사했다. 정렬 없는 결과는 중복 수를 유지하는 bag 비교를 사용했다. 유형별 49개 독립 값 검사는 `generated-review-result.json`에 문항/단계별로 기록했다.
- 원본 보존 독립 해시 대조: PASS, 131개. `original-preservation-result.json`은 root가 작업 전에 저장한 `source-before.json`을 기준으로 한다. 이 검사는 현재 사용자 DB 자체를 검사한 것이 아니다.
- 원본과 결과가 같은지만으로 중간 과정 전체가 옳다고 판정하지 않았다. 집계 NULL, 빈 집계, ON/WHERE 차이, 다중 조인쌍, 외부 조인 NULL 확장, COUNT 차이, 상관/존재/ANY/ALL/튜플 서브쿼리, 집합, 윈도 프레임·동률을 별도로 확인했다.

공식 의미 대조의 URL과 한정된 Oracle 설치 검사 결과는 `review-criteria.md`에 있다. 저작자의 `validate_walkthroughs.py` 결과와 위 독립 스크립트 결과는 서로 다른 검토 단계다.

## 코드 검토와 수정 피드백

| 확인한 위험 | 반영 상태 |
|---|---|
| 문제 ID만 같아 SQL/표/보기/정답이 바뀐 자료에 예전 해설·필기가 붙음 | WalkSource의 원문 스냅샷 비교와 fingerprint, 필기 SQL 해시를 함께 사용. 불일치는 기존 해설로 돌아감 |
| 채점 전에 정답이 든 단계 자료를 읽거나 강조로 정답을 암시함 | SessionScreen은 submission이 있을 때만 개별 자료를 읽음. 채점 전 단계/결과표/현재 강조 없음 |
| 화면 회전·해설 모드 전환에서 단계/기초 펼침 초기화 | 관련 saveable 상태가 폭/모드 분기 위에 있음. 같은 문제·원문 기준으로 유지 |
| 작은 화면에서 원본 표가 SQL 공간을 전부 차지함 | 작은 화면 원본 표는 별도 펼침 대화상자, SQL와 해설은 상하 분할 유지 |
| 저장 상태 문장이 길어져 SQL와 필기 위치가 밀림 | 고정 상태줄, 긴 상태는 설정에서 확인. 원문 문서 좌표와 화면 pan/zoom을 구별 |
| 오래된 필기 저장 실패가 최신 저장 성공 뒤에도 오류로 남음 | 현재 초안과 일치하는 요청에만 오류 적용. 최신 저장 성공 시 해당 초안/오류 제거 |
| 긴 SQL의 다음 강조가 화면 밖에 남음 | 단계 강조가 바뀌고 해당 구문이 안 보일 때 현재 위치로 이동하도록 보정 |
| 짧은 강조 문자열 T가 SELECT의 T를 가리킴 | 저작자가 발견하고 FROM/GROUP BY/ORDER BY 절 전체로 수정. 독립 Python/JVM 검사에 의미별 prefix 조건 추가 |
| HAVING에만 있는 집계 대상 또는 집계 바깥 NVL/산술 과정이 빠짐 | 저작자가 집계 수집을 SELECT+HAVING으로 확장하고 실제 계산값 단계를 보완. 이후 독립 최종 검사를 다시 통과 |
| 일반 객관식을 억지로 한 화면에 넣느라 읽기 어려워짐 | 본문/보기 삭제·말줄임 없이 간격만 줄이고 48dp 보기 최소 높이 및 스크롤을 유지. 기기별 최종 가독성은 별도 화면 QA 대상 |

기존 StudyEngine의 정답 공개 시점·선택 ID·고정 세션 snapshot을 새 해설 계산으로 대체하지 않는다. 원본 자료 131개가 그대로여서 정답/보기/내용 변경에 따른 기록 이전도 필요하지 않았다. 새 필기는 별도 저장 필드와 schema 3 백업에 추가되고, Room schema 1 파일은 보존됐다.

## 앱 검사 상태

이 검토 담당은 Gradle/ADB를 실행하지 않았다. root가 실행한 결과와 실제 생성된 로그/XML을 구분해 확인한다.

- JVM `SqlWalkthroughTest` 4/4 PASS: `app/build/test-results/testDebugUnitTest/TEST-kr.sqld.study.SqlWalkthroughTest.xml` 확인. 스냅샷 변경 거절, 문자열 occurrence, 셀 범위/중복 단계 거절, 133개 자료 전체 decode 검사를 포함한다.
- root의 JVM 전체 89개 PASS, Debug/Release lint PASS. `evidence/sql-reader-20261006/build-final.log`에서 빌드 성공을 확인했다.
- 태블릿 첫 실행 77개 중 74개 PASS/3개 FAIL. 새 SqlWalkthroughUiTest 5개는 PASS다. 실패 3개는 새로 접힌 `문제 정보·도움`을 열지 않고 내부 버튼을 찾던 기존 테스트였다. 실제 펼침 클릭을 추가했으며 원래 기록/복원/제외 검증을 제거하지 않았다. 수정 후 해당 3개 재실행도 **3/3 PASS**: `runtime/tablet-final-instrumentation.log`. 첫 실행의 통과 74개와 수정 후 통과 3개로 판정한 것이며, 77개 전체를 마지막에 다시 실행했다는 뜻은 아니다.
- 320dp/150% 글꼴 첫 실행 9개 중 3개 PASS/6개 FAIL. 6개는 문제 화면 전 홈 LazyColumn에서 아직 구성되지 않은 `이어서 공부` 노드를 찾던 진입 helper 실패다. 부모 목록을 먼저 스크롤하도록 2개 helper를 보정했다. 동일 선택 범위 9개 재실행 **9/9 PASS**: `runtime/phone320-font150-debug-final-instrumentation.log`.
- 재실행 사이 release APK에 debug 전용 시험 호스트를 열려던 실행은 `Unable to resolve ... androidx.activity.ComponentActivity`로 시작하지 못했다. 이 환경 불일치 로그는 `tablet-harness-recheck-instrumentation.log`, `phone320-font150-final-instrumentation.log`에 남아 있다. 올바른 debug APK로 다시 실행한 위 최종 로그와 구분한다. Release 앱의 수동 실제 클릭/스크린샷은 root의 별도 검사 대상이다.
- root의 `runtime/record-preservation.json` 확인: user0의 답안 55·세션 5·메모 2·교재 진도 5, user10의 답안 11·세션 5·메모 1·교재 진도 2 유지. schema 2→3와 revision 외 기존 학습 필드 변화 없음. 이 검토 담당은 원본 개인 백업 내용을 읽거나 수정하지 않고 결과 요약을 확인했다.
- `StateRestorationTester` 검사는 저장 상태 복원을 확인하는 테스트이며 실제 Galaxy Tab 회전/S Pen 검사를 대신하지 않는다.

위 재검사 로그는 `evidence/sql-reader-20261006/runtime/`에 있다. 최초 실패 기록은 숨기거나 덮어 성공으로 표현하지 않는다. 이 통과 판정은 에뮬레이터 범위이며 실물 증거가 아니다.

### Release 실제 화면에서 추가 발견한 잘림

위 기능 검사 통과 후 root의 **실제 Release 화면 320dp/150% 글꼴 캡처**에서 SQL 첫 줄 잘림을 발견했다. 코드 canvas 높이가 약 83px(36.9dp)이었는데, 확대된 첫 줄 baseline은 48dp에 있어 글자를 읽을 수 없었다. 기존 테스트가 접근성 노드/버튼 동작/상태만 검사한 한계이며, 앱의 실제 표시 결함이었다. 앞서 통과한 자동검사로 이 잘림까지 검증됐다고 보지 않는다.

root가 작은 화면 코드 영역에 글자 배율을 반영한 최소 높이를 확보하고, 채점 후 중복 상태줄을 헤더로 옮기고, 상시 안내를 `학습용 논리 흐름`으로 줄였다. 물리 실행계획과의 차이는 intro/검증 설명에 유지했다. 이 변경은 최초 77개 및 9개 검사 뒤의 **추가 앱 구현 변경**이다.

회귀 검사 `codeViewportFitsFirstLineBeforeAndAfterGradingAtCurrentFontScale`를 추가했다. 채점 전·후·다음 단계에서 코드 영역 높이가 `(32 baseline + 6 descent) × 시스템 글꼴 배율 × density × 앱 글씨 배율` 이상인지 검사한다. 따라읽기 모드, 단계 제목, 하단 라벨, 다음 버튼 표시와 다음 단계 제목도 확인한다. 기존 SqlWalkthroughUiTest 5개에 더해 이제 6개다.

최종 viewport 수정 앱의 재실행 로그를 직접 확인했다.

| 검사 | 최종 결과 | 근거 파일 |
|---|---|---|
| 태블릿 전체 | **78/78 PASS**, 이번에는 수정 앱으로 전체 재실행 | `runtime/tablet-viewport-final-all-instrumentation.log` |
| 320dp, 시스템 글꼴 150% | **10/10 PASS**, geometry 포함 | `runtime/phone320-font150-viewport-final-instrumentation.log` |
| 320dp, 시스템 글꼴 200% | **4/4 PASS**, 선택한 확대/viewport 검사 범위 | `runtime/phone320-font200-viewport-final-instrumentation.log` |
| JVM 전체 | **89/89 PASS**, 실패/오류 0 | `app/build/test-results/testDebugUnitTest/TEST-*.xml` 합계 확인 |
| Debug/Release lint | 각각 오류 0, 경고 8 | `app/build/reports/lint-results-debug.xml`, `lint-results-release.xml` |
| 최종 빌드 | 성공 | `evidence/sql-reader-20261006/build-viewport-final.log` |

위 runtime 파일은 `evidence/sql-reader-20261006/runtime/` 기준이다. 높이 검사 또한 글자 픽셀 자체의 정확성, 전체 긴 SQL/표의 모든 위치, 실물 S Pen을 보증하지 않는다. root가 최종 Release 재설치와 실제 화면 캡처/클릭 검사를 별도로 진행한다. 이 보고서는 위 자동검사 최종 로그까지 확인했으며, 최종 PNG의 픽셀 검토 결과를 대신하지 않는다.

## 남은 한계

- Oracle 19c 원문 실행, 사람 SQL 전문가 검수, 실제 Galaxy Tab/S Pen의 필압·손바닥 차단·회전 동작은 미검증이다.
- SQLite 통과로 Oracle의 타입 변환·NLS·빈 문자열·실제 실행계획까지 검증됐다고 판단하지 않는다.
- 미적용 SQL 84개와 SQL 필드 없는 444개에 새 실행 단계를 추측해 붙이지 않았다. 기존 개념/표/해설을 유지한다. 미적용 전수 사유는 `docs/sql-walkthrough-coverage.md`를 따른다.
- 모든 문장을 전수 의미 검토하거나 학습 효과/합격 가능성을 실험한 것은 아니다. 구조와 최종값 전수 검사, 유형별 명시적 중간값 검사, 기기 동작 검사를 따로 보고한다.
- 성능 근거는 개별 자료 지연 읽기·LRU 6개 제한·표 가시 행 렌더링 구조와 동작 검사다. 기존 대비 속도 향상 수치를 측정하지 않았다.

## 재검사 명령

```powershell
python qa/walkthrough-review/review_reference_example.py
python qa/walkthrough-review/review_generated.py
```

위 명령은 원본 문제나 앱 구현을 변경하지 않고 이 폴더의 검사 결과 JSON만 갱신한다. 앱 빌드/기기 검사는 프로젝트의 `scripts/build.ps1`과 root의 최종 실행 기록을 사용한다.
