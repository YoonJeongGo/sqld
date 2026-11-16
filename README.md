# SQL 노트 — 개인용 오프라인 SQLD 학습 앱

Android용 Kotlin·Compose 앱입니다. 노트 41개와 63강 학습 자료를 제공하며, 기존 661문항에 단원 복습 189문항·단원 모의 15회 750문항을 더해 채점 문제는 1,600문항입니다. 답안 선택과 채점을 분리하며, 최초 제출·별표·복습·필기·진행 중 답안을 기기 안에 보관합니다.

**현재 개인용 버전은 0.11.0입니다.** **모의고사 → 단원 선택 → 회차 선택 → 문제**로 바로 이동합니다. 단원별 복습은 **복습 → 단원별 복습 문제**에서 고릅니다. 실전에서는 개별 채점을 숨기고 다음·전체 제출을 강조합니다. 기존 전체 SQLD 모의고사와 학습 기록·펜 기능을 보존합니다. [변경·검사·한계](docs/mock-navigation-0.11.0.md)를 확인하세요.

이전 0.10.1의 SQL 코드 필기에서 펜 옆 버튼을 누르는 동안 지우개로 쓰고, 떼면 원래 펜·형광펜으로 돌아가는 동작을 유지합니다. [펜 버튼 검사와 한계](docs/spen-button-0.10.1.md)를 확인하세요.

**0.10.0 변경 기록.** 홈의 **내 학습 진도**에서 이어서 공부하고, 강의 하단의 **다음** 버튼으로 **설명 → 개념 → 예제 → 확인 → 다음 강의**를 따라갑니다. **진도** 메뉴는 63강 목차입니다. 계획표·개념 찾기·추가 문제는 접을 수 있는 학습 도구에 보존했습니다. [변경·실제 검사·되돌리기](docs/learning-flow-0.10.0.md)를 확인하세요.

**0.9.0 변경 기록.** 5개 단원마다 강의·유형별 복습과 50문항 모의고사 3회, 제출 후 별도 답지·해설을 추가했습니다. 문제 표를 본문에 펼쳐 두고 태블릿 가로에서는 문제·SQL·표와 보기를 나란히 읽습니다. 단원 모의는 해당 단원 집중 연습이며 전체 SQLD 진단과 구분합니다. [수량·변경·실제 검사·되돌리기](docs/unit-practice-0.9.0.md)를 확인하세요.

**0.8.1 변경 기록.** 학습 본문을 17sp·1.6배 줄간격과 의미별 문단으로 표시하며 핵심어·컬럼/값을 필요한 곳에서 굵게 구분합니다. 진도·노트·예제·채점 후 해설에 공통 적용하고 원문·SQL·정답·학습 기록을 보존합니다. [본문 표시 변경·실제 화면·검사](docs/body-readability-0.8.1.md)를 확인하세요.

**0.8.0 변경 기록.** 기존 63강의 95예제·189자기점검에 별도 상세 해설을 연결했습니다. 강의의 **대상·값·방향부터 따라 읽기**에서 목적·용어·중간표를 보고, 문제에서는 채점 후 관련 강의로 연결합니다. 원본 콘텐츠와 기록은 보존합니다. [실제 적용 범위·검사·되돌리기](docs/explanation-upgrade-0.8.0.md), [63강별 연결표](docs/lesson-guide-coverage-20261012.md)를 확인하세요. 661문항 전체를 새 단계 해설로 다시 쓴다는 뜻은 아니며, 기존 문제별 SQL 따라 읽기 133개는 그대로 유지됩니다.

**0.6.2 변경 기록.** 좁은 화면의 채점 버튼·날짜 표시·시간표 배치와 홈 제목 줄바꿈을 개선했습니다. [이번 화면 검사](docs/ui-spacing-0.6.2.md)를 확인하세요. 0.6.1에서는 현재 디자인을 유지하면서 계획 복습의 문제 순환, 검색 결과, 초기 오류 재시도, 메모·오류표시의 저장 실패/회전 초안 보존을 개선했습니다. [기능 QA 판정](FINAL_PRODUCT_GATE.md)과 [수정 내역](PRODUCT_FIX_REPORT.md)을 확인하세요. 0.6.0에서는 Canva 앱 화면 시안을 바탕으로 홈·학습 계획과 공통 테마를 개편했습니다. 네이비 강조 카드·흰 본문 카드·틸 버튼, 태블릿 두 열 배치, 계획 세부 내용 접기를 제공합니다. [디자인 적용 기준](docs/ui-redesign-design-source-2026-10-05.md)과 [실행 QA](docs/ui-redesign-qa-2026-10-05.md)를 확인하세요. 홈의 **학습 계획**에서 2026-10-05~11-13의 날짜별 강의·PDF 범위와 앱 복습을 확인합니다. 28공부일 × 5시간=140시간, 6시간=168시간이며 주말과 10/8·9는 쉽니다. [전체 계획과 검증](docs/study-plan-2026-10-05.md), [인쇄용 PDF](output/pdf/SQLD_40일_전체학습계획_5시간_6시간.pdf), [상세 계획표](output/study-plan/전체계획표.html)를 제공합니다. 이전 0.4.1에서는 63강 학습 본문의 760dp 폭 제한을 없애 태블릿에서 좌우 20dp만 남기고 넓게 표시합니다. 큰 그림은 원본 해상도로 읽습니다. [화면 폭 개선과 검증](docs/visual-width-0.4.1.md)을 확인하세요. 기존 63강에 핵심 그림 27장과 그림을 읽는 순서를 연결했습니다. [통합·검증 보고서](docs/visual-integration-0.4.0.md), [63강 변경 목록](docs/visual-lesson-changes.md), [그림 연결표](docs/visual-lesson-map.md), [데이터 일치 점검표](docs/visual-data-consistency.md)를 확인하세요. 넓은 화면의 상단 **목록 접기 / 목록 펼치기**로 왼쪽 메뉴와 개념 노트 목차를 함께 숨기고 다시 열 수 있습니다. [목록 접기 동작과 검증 범위](docs/sidebar-0.3.2.md)를 확인하세요. 이전 [0.3.1 최적화 기록](docs/optimization-0.3.1.md)은 보존했습니다. release 빌드와 debug 빌드를 제공하며 기존 개발 서명을 유지합니다. 63강 통합 기록은 [0.3.0 QA 보고서](docs/course-integration-0.3.0.md), 이전 줄바꿈 검사는 [0.2.2 QA 보고서](docs/readability-qa-0.2.2.md)에 보존했습니다. 현행 DataQ 출제기준 원문, 사람 전문가 검수, Oracle/SQL Server 실제 실행, Galaxy 실기기 검증은 완료되지 않았습니다. 설치 가능한 앱과 ‘완성품 검증 완료’는 구분합니다. 이전 버전의 검사와 구분한 [버전별 QA 안내](docs/QA.md), 콘텐츠 수량과 검수 상태는 [coverage](docs/coverage.md)와 [검수 보고서](docs/content-review.md)를 확인하세요.

## 63강 자료와 별도 진도

- **진도**에서 5개 단원, 63강을 순서대로 학습합니다. 기존 41개 개념 노트는 **개념 찾기**에서 계속 이용합니다.
- 강의 안에서 **1 설명 → 2 개념 → 3 예제 → 4 확인**을 선택합니다. 핵심 정리에서는 쉬운 뜻 → 연결된 그림과 읽는 순서 → 결과·주의점 → 한 줄 기억을 봅니다. **기존 SQL 예제로 연습하기**를 누르면 원래 입력표·단계·결과로 이어집니다. 그림과 기존 예제는 다른 데이터이며, 예제 비교 해설은 해당 강의의 모든 예제 결과를 펼친 뒤 표시합니다.
- 그림 27장은 40강에 45번 연결됩니다. 연결 없는 23강에는 관계없는 그림을 넣지 않았습니다. 그림을 누르면 **화면 맞춤 / 원본 크기 / 확대·축소**와 손가락 이동을 사용할 수 있습니다. 그림 속 글자는 검색에 포함되며 **그림의 표·글자를 텍스트로 보기**에서 선택·복사할 수 있습니다. 그림 안의 화살표·[다음]은 정적 표시이고, 예제의 단계 버튼은 기존대로 실제 동작합니다.
- 490개 개념 설명, 95개 예제, 223개 표, 70개 SQL, 63개 개념도를 수록했습니다.
- **읽음 / 예제 확인 / 자기점검 이해·다시 보기**를 별도로 기록합니다. 영상 수강 완료나 시험 점수를 뜻하지 않습니다. 자기점검 189개는 기존 661개 창작 문항에 합산하지 않습니다.
- 마지막 강의·화면·읽던 위치, 풀이 단계, 입력한 자기점검 답안과 평가를 저장합니다. **홈 → 내 학습 진도**에서 이어서 공부합니다.
- 기존 개념 노트와 연결 연습으로 이동할 수 있습니다. 강의의 연결 연습에는 모의고사 예약 문항을 넣지 않습니다.
- 백업 v2에 새 진도를 포함합니다. v1 백업도 가져올 수 있으며, v2 백업은 0.3.0 이상에서 사용합니다. Room DB 테이블은 변경하지 않았습니다.
- 자료는 사용자가 제공한 창작 학습 패키지입니다. 유료 강의 영상·교재 원문이나 실제 기출문제라는 뜻이 아닙니다. [자료 검토 범위](docs/course-content-review.md)를 확인하세요.

## 중요도와 보강 학습

- **학습 핵심 14개 / 중요 22개 / 기초 보충 5개**를 목차에 표시하고 중요도별 필터·정렬을 제공합니다. 기초 보충도 생략 권고가 아닙니다.
- **교재·강사 강조**는 출판사·강사의 실제 공개 자료에 근거한 별도 표시입니다. 길벗 저자의 출제경향 분석은 확인했지만 표본·분석 방법은 미확인입니다. 공식 출제 확률로 표시하지 않습니다.
- 각 노트의 **중요도와 출제 근거**에서 선정 이유·집중할 항목·출처를 확인합니다. 핵심 요약은 배경과 글자 표시를 함께 사용합니다.
- 홈의 **핵심 개념 진도**는 현재 내용 읽음·무도움 개념 정답·무도움 적용 정답의 주제 수를 구분합니다. 반복 정답을 여러 주제로 세지 않습니다.
- 이전 읽음·필기·제출은 보존합니다. 내용이 늘어난 노트는 **보강 내용 확인 전**으로 표시하며, 원래부터 v2였지만 변경되지 않은 노트는 기존 읽음을 유지합니다.
- 스키마·ERD·반정규화·자료형·ALTER/RENAME·뷰·관계대수 7노트, 기존 10노트의 설명 보강과 61문항을 추가했습니다. [업데이트 검증](docs/priority-update.md), [중요도 조사](docs/study-priority-research.md)를 확인하세요.

## 설치와 첫 사용

1. `dist/SQL-note-0.11.0-release.apk`를 Android 8.0 이상 기기로 옮겨 설치합니다. Android의 해당 파일 제공 앱 설치 허용이 필요할 수 있습니다. 서명된 공개 릴리스가 아니라 Android 개발용 서명을 사용합니다.
2. **SQL 노트**를 실행합니다. 계정, 인터넷 연결, 결제 없이 콘텐츠를 읽고 학습합니다.
3. **홈 → 내 학습 진도**에서 강의를 순서대로 읽습니다. 별도 문제는 **진도 → 단원별 복습·모의고사** 또는 강의의 추가 학습 도구에서 선택합니다. 보기 터치는 답안 선택이며, 채점 버튼을 눌러야 확정됩니다. 확정 후 답안은 바꿀 수 없습니다.
4. **복습**에서 현재 오답·과거 오답·헷갈림·별표·오늘 복습을 구분합니다. 별표를 해제해도 진행 중 문제 세트는 그대로입니다.
5. **모의고사**는 50문항·90분의 잠정 시험 기준을 사용합니다. 실전 중 해설이나 노트 도움을 열려면 확인 후 연습 모드로 영구 전환되며 순수 진단에서 제외됩니다.

ADB 설치는 `adb devices`로 본인 기기를 확인한 뒤 `adb -s <기기ID> install -r dist/SQL-note-0.11.0-release.apk`를 사용합니다. 기존 앱이 다른 개발 서명으로 설치됐다면 덮어쓰기가 거부될 수 있습니다. 기록을 백업하지 않은 채 제거하지 마세요.

## 백업·복원·필기

- **설정 → 전체 기록 내보내기**에서 직접 파일 위치를 선택합니다. 별표, 제출, 진행 중 답안, 필기, 복습 일정, 노트·강의 진도, 자기점검 답안과 평가, 설정을 포함합니다. 자동 클라우드 백업은 없습니다.
- **백업 파일 검사·복원**은 검사값·형식·참조 검증 후 교체 전후 수량을 보여줍니다. `검사한 기록으로 교체`를 눌러야 적용됩니다. 병합이 아닌 전체 교체이고, 적용 직전 기록은 로컬 복구 지점에 보관됩니다. 같은 백업을 두 번 복원해도 시도 수를 늘리지 않습니다.
- **복원 전 로컬 복구 지점 열기**로 직전 교체 이전 기록을 미리 보고 되돌릴 수 있습니다. 기기 고장에 대비하려면 외부 파일 백업이 필요합니다.
- 백업은 최대 32MB이며 암호화하지 않은 개인 기록 파일입니다. SHA-256은 우발적 손상 검사용이고 출처 인증 서명이 아닙니다.
- 노트의 문장을 길게 선택하면 형광펜·밑줄·메모를 추가합니다. 블록 메뉴에서도 필기를 저장합니다. 업데이트로 문장 연결을 찾지 못하면 삭제하지 않고 **나의 필기와 북마크 → 재연결 보관함**에 남깁니다.

## 소스와 빌드

주요 경로는 `app/src/main/java/kr/sqld/study`(앱), `content/part-a.json`·`part-b.json`(작성 원본), `content/sources.json`(출처), `app/src/main/assets/content-pack.json`(검증 후 생성 팩), `scripts`(빌드·검수), `evidence`·`qa`(실제 증거)입니다.

0.9.0 추가 단원 문제는 별도 원본 `content/part-unit-*.json`에서 생성합니다. `python scripts/build_unit_questions.py --check`로 독립 검토의 원본 해시와 앱 자산을 검사합니다. 내용 수정 시 기존 검토를 그대로 재사용할 수 없으며, 수정본을 재검토하고 `python scripts/build_unit_questions.py`로 생성한 뒤 다시 검사합니다.

개발 환경: JDK 21, Android SDK platform 36/build tools, Gradle 8.13, AGP 8.13.1, Kotlin 2.0.21. Java bytecode는 17, minSdk 26/targetSdk 35입니다. 최초 의존성 다운로드에는 인터넷이 필요하지만 설치한 앱은 네트워크 권한이 없습니다. 주요 버전은 Gradle 파일에서 고정했습니다. 현재 머신은 Android Studio 번들 JDK와 SDK를 사용했습니다.

```powershell
Set-Location D:\SQLD
$env:JAVA_HOME='C:\Program Files\Android\Android Studio\jbr'
# 다른 위치의 SDK를 사용하는 경우 설정
$env:ANDROID_HOME='C:\Users\사용자\AppData\Local\Android\Sdk'
$env:PYTHONIOENCODING='utf-8'
python scripts/validate_content.py --strict
python scripts/validate_course.py --engine
python scripts/validate_visuals.py
python scripts/verify_visual_examples.py
./scripts/build.ps1 -Tasks assembleDebug,assembleRelease,testDebugUnitTest,assembleDebugAndroidTest,lintDebug,lintRelease
# 의존성 다운로드 완료 후에는 -Offline 추가 가능
```

빌드 결과는 `app/build/outputs/apk/release/app-release.apk`와 `app/build/outputs/apk/debug/app-debug.apk`입니다. release는 디버깅 가능 플래그를 끄지만 기존 개발 서명을 사용하며, R8 축소·난독화는 활성화하지 않습니다. Python 검수 도구는 표준 라이브러리로 실행합니다.

빌드·설치·테스트 결과를 확인한 뒤 `python scripts/package_artifacts.py --build-type release`로 `dist/SQL-note-0.11.0-release.apk`, `dist/SQL-note-0.11.0-debug.apk`, `dist/SQL-note-0.11.0-source.zip`, `dist/manifest.json`을 묶습니다. `manifest.json`의 파일명·SHA-256과 QA 보고서를 함께 확인합니다. 소스 ZIP은 코드·콘텐츠·검수 자료와 전용 에뮬레이터 QA 캡처를 포함하며, 앱 DB·원본 백업·서명 키는 포함하지 않습니다. 원본 보존용 자료를 제외하는 것이며 작업 폴더의 원본을 삭제하지 않습니다.

기존 설치에 덮어쓰려면 같은 개발 서명 키를 사용합니다. 필요하면 빌드 전에 `SQLNOTE_DEBUG_KEYSTORE` 환경 변수에 기존 `debug.keystore`의 절대 경로를 지정하세요. 이 PC의 빌드 스크립트는 로컬 `.android/debug-keystore-path.txt`도 읽습니다. 키와 로컬 경로 설정은 소스 ZIP에 포함하지 않습니다.

## 테스트

```powershell
python -m unittest discover -s scripts -p 'test_*.py' -v
./scripts/build.ps1 -Tasks testDebugUnitTest,assembleDebug,assembleDebugAndroidTest -Offline
adb -s <테스트기기ID> install -r app/build/outputs/apk/debug/app-debug.apk
adb -s <테스트기기ID> install -r app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb -s <테스트기기ID> shell am instrument -w kr.sqld.study.test/androidx.test.runner.AndroidJUnitRunner
```

JVM은 채점·복습·시계·노출·백업 규칙, Android 테스트는 별도 DB의 영속·원자적 복원·저장 실패 및 실제 Compose 조작을 검사합니다. 테스트가 실제 사용자의 앱 DB를 초기화하지 않습니다. `scripts/device_qa.py`는 AVD 이름이 **SQLNote_QA**인 에뮬레이터만 허용합니다. 기본 연결은 `emulator-5590` / ADB 포트 `5037`이며, `SQLNOTE_ADB_DEVICE`·`SQLNOTE_ADB_PORT`로 연결 대상과 서버 포트를 지정해도 같은 AVD 검사를 유지합니다. 다른 프로젝트의 에뮬레이터나 실물 기기를 조작하지 않도록 제한했습니다.

## 콘텐츠 추가와 정정

63강 정본은 `content/course-pack.json`, 추가 그림·읽기 안내 정본은 `content/course-visuals.json`과 `content/course-visuals/`입니다. 수정 후 `python scripts/validate_course.py --sync-asset --engine`, `python scripts/validate_visuals.py --sync-assets`로 검사해 앱 assets에 복사합니다. ZIP의 `src/build_content.py`나 `scripts/import_course.py`로 현재 내용을 다시 생성하지 마세요. 후자는 정본이 있으면 덮어쓰기를 거부합니다. 새 그림을 넣어도 기존 ID·답안·기록을 바꾸지 않습니다.

1. [콘텐츠 계약](content/CONTRACT.md)에 맞춰 원본 JSON을 수정합니다. `questionId`, `choiceId`, `familyId`, 노트 `blockId`를 안정적으로 유지하고 출처·DBMS·버전·조건·오답별 이유·정답 검증 방법을 기록합니다. 실제 기출로 표시하지 않습니다.
2. 예약 모의고사 family는 일반 연습과 분리합니다. 정답과 해설을 제외하고 choice ID와 순서를 가린 검토 입력을 생성합니다.
3. 다른 검토자가 독립적으로 풀고 근거를 저장한 **뒤** 정답과 비교합니다. `scripts/blind_review.py prepare --help`, `compare --help`에 인자가 있습니다. AI 검토를 사람 검수나 DBMS 실행으로 표시하지 않습니다.
4. `python scripts/validate_content.py`로 스키마·참조·분포·중복·SQL fixture·해설 조건을 확인합니다. 오류 항목은 격리하고 정상 세션에서 제외합니다. 검토 뒤 문항을 바꾸면 기존 hash 검토를 승계할 수 없습니다.
5. 같은 문항 정정은 `version`을 올리고 `corrections`에 이유를 남깁니다. 원래 세션은 원문·보기 순서·ExamSpec·채점 snapshot을 유지하며, 현재 콘텐츠와 달라지면 이력 화면에서 원판정과 현재 기준을 비교합니다.
6. 관련 테스트와 UI를 재검증하고 새 APK를 빌드합니다. 현재 팩은 APK에 포함되므로 온라인 자동 갱신되지 않습니다.

앱의 **내용 오류 표시**는 로컬 개인 검토 목록입니다. 자동 문의나 외부 전송을 하지 않습니다. 설정에서 검토 목록 파일을 직접 내보낼 수 있습니다.

## 근거와 한계

[설계 결정](docs/decisions.md) · [요구사항 추적표](docs/requirements.md) · [시험 근거](docs/sources-and-scope.md) · [정정 이력](docs/corrections.md) · [실행 QA](docs/QA.md)

시험 기준은 공식 원문 확인 전까지 잠정 상태입니다. 수록 문제는 학습용 창작이고 실제 시험 예측·합격률·학습 효능을 입증하지 않습니다. 앱이 종료된 동안에는 OS 백그라운드 서비스가 점수를 쓰지 않고, 재실행 때 저장된 시간 기준으로 만료를 복구합니다. 장기 대용량 기록 성능, 실제 OS 저용량 장애, TalkBack 음성 순서와 외부 키보드, 물리 기기 검증은 별도입니다.
