## 0.11.0 단원 모의고사 동선·실전 버튼 — 2026-10-18

**모의고사 → 단원 → 회차 → 문제** 전용 화면으로 연결하고, 단원별 복습은 복습 메뉴로 분리했습니다. 기존 전체 SQLD 모의고사도 보조 링크로 보존했습니다. 미제출 실전에서 개별 채점·모르겠어요를 숨기고 다음·전체 제출을 강조했으며, 마지막 문제는 전체 제출을 주 버튼으로 표시합니다. 일반 연습의 채점과 기존 데이터 형식은 그대로입니다.

Debug/Release 빌드, JVM124/124, 콘텐츠 검증, lint 각각 오류0·경고8을 확인했습니다. 콘텐츠·자산·Room schema·핵심 저장/채점 코드539파일은 byte 동일합니다. API34 태블릿 회귀25/25 뒤 촬영 동기화를 보완한 강화4/4, 휴대폰 시스템200% 강화4/4가 통과했습니다. 겹치는 메서드를33개로 합산하지 않습니다. 초기 테스트 빌드 오류·캡처 프레임 혼합·UI 반영 전 단언 실패 로그는 최종PASS와 분리해 보존했습니다.

기존 실제 앱 DB는 촬영 뒤·Debug20 실행 뒤·Release20 실행 뒤 세 시점 모두 전체 필드·제출55행·복구1행 동일했습니다. Release 실행 후 DB는 같은 버전 Debug를 미실행 접근용으로 설치해 읽었습니다. 실물 Galaxy Tab/S Pen·TalkBack은 미실행입니다. [변경·실행·되돌리기](mock-navigation-0.11.0.md), `evidence/mock-navigation-20261018/`를 참고하세요.

## 0.10.1 펜 옆 버튼 임시 지우개 — 2026-10-18

SQL 필기의 스타일러스 버튼 누름·해제를 읽어 누르는 동안만 획 지우개로 바꾸고 원래 펜·형광펜 설정으로 돌아가도록 수정했습니다. 접촉 중 전환의 구간 분리와 손가락 입력 격리·취소를 다룹니다. 문제·콘텐츠·Room schema535파일은 작업 전과 동일하며, 단원 모의15세트×50문항은 타 단원 혼입0으로 별도 대조했습니다.

Debug/Release 빌드·JVM124/124, lint 오류0·경고8을 확인했습니다. API34 태블릿 입력·필기·저장·SQL 해설28/28, 휴대폰 시스템200%의 버튼/설정14/14가 통과했습니다. 기존0.10.0에서 새 Debug/Release 실행 후 전체 DB 필드·제출55행·복구1행이 동일했습니다. Release 확인 뒤 같은 버전 Debug를 미실행 접근용으로 설치해 DB를 읽고 Release로 복귀했습니다. 물리 Galaxy Tab/S Pen·제조사 버튼 전달·TalkBack은 미실행입니다. [0.10.1 보고서](spen-button-0.10.1.md), `evidence/spen-button-20261018/`에 실제 근거를 보존하며 이전 버전 결과와 합산하지 않습니다.

## 0.10.0 학습 진도 동선 — 2026-10-18

홈의 주 학습 진입점을 63강 진도로 정리하고, 강의에 **설명 → 개념 → 예제 → 확인 → 다음 강의**의 고정 하단 버튼을 연결했습니다. 계획표·개념 찾기·추가 문제·자유 이동은 접을 수 있는 보조 도구에 보존합니다. 저장 형식·문제·콘텐츠는 변경하지 않았고 기존 콘텐츠/앱 자산/Room schema 535파일이 동일합니다.

Debug/Release 빌드, JVM124/124·Python63/63, lint 오류0/경고8을 확인했습니다. 태블릿 전체105개 초기 실행은101통과·구형 홈/복습 문구 선택자4실패였고, 기대 문자열을 고친 영향범위23/23 재검사는 통과했습니다. 최종 학습 동선4개는 태블릿 가로·세로, 휴대폰 기본·시스템200% 네 환경에서 각각4/4 통과했습니다. 전체105/105 단일 최종 실행으로 합산하지 않습니다.

Release 업데이트 설치·실제 홈 표시 뒤에도 기존 DB 전체 필드와 제출55행·복구1행이 동일했습니다. DB는 Release 실행 후 같은 버전 Debug APK를 접근용으로만 설치해 미실행 상태에서 읽었고, 마지막으로 Release를 다시 설치했습니다. 원래 표시 설정을 복원했습니다. 실제 캡처·설치·비교 방법은 [0.10.0 보고서](learning-flow-0.10.0.md)와 `evidence/learning-flow-20261018/`에 있습니다. 물리 Galaxy Tab/S Pen·TalkBack·학습효과는 미검증이며 아래 기존 버전 결과와 구별합니다.

## 0.9.0 단원별 문제·표 동시 표시 — 2026-10-15

5개 단원에 강의·유형별 복습189문항과 단원 모의15회×50문항=750문항을 추가했습니다. 기존661문항·63강과 원본 자산527파일은 바이트 단위 동일합니다. 채점 문제의 총수는1,600개이며 강의 자기점검189개는 별도입니다. 검토된 추가 원본과 앱 은행을 별도로 관리하고 저술 파일 해시·독립 AI 검토·3회50문항·63강 참조를 빌드/패키징에서 검사합니다. 전체 SQLD 모의의 ExamSpec과 단원 집중 연습의 판정은 구별합니다.

최종 앱의 JVM108/108, Debug/Release lint 각각 오류0·경고8, API34 에뮬레이터1280×800dp 전체101/101, 휴대폰360×800dp 기본/200% 각6/6이 통과했습니다. 답지에서 선택 문제로 반복 복귀·화면 복원·제외 문항이 있는 기존 시험 재개·정답 공개 시점·표의 unclipped 경계 등을 검사했습니다. 초기 실제 반복 복귀 버그와 중복 문장 검사 선택자의 오판 로그를 보존하고 최종 PASS와 구별했습니다.

업데이트한 Debug의 실제 MainActivity 실행 뒤 기존 DB의 모든 필드·제출55행·복구1행 동일을 확인했습니다. 이후 같은 서명의 Release0.9.0/versionCode17 업데이트 설치·콜드 실행을 확인했고 표시 환경을 복원했습니다. Release 설치 후 DB 재수출 비교는 하지 않았습니다. 자세한 근거·실제 화면·되돌리기는 [0.9.0 보고서](unit-practice-0.9.0.md), 최종 로그는 `evidence/unit-practice-20261015/`를 참고하세요. 실제 Galaxy Tab/S Pen·공식 시험과의 난도 동등성·신규 최종본 Oracle/SQL Server 실행·사람 전문가 검수는 미검증입니다.

## 0.8.1 학습 본문 표시 — 2026-10-13

기존 진도별 개념·학습 노트·교재/문제 해설의 본문 렌더러를 통일했습니다. 17/16sp 본문·1.6배 줄높이, 선택한 핵심어 Bold, 문단 10dp, 관련 제목·본문 8dp 간격을 적용했습니다. 선택 가능한 노트는 원문 문자·공백을 유지하고 표시용 문단 간격만 넣으며, `NoteTextProjection`으로 필기의 quote를 원문에 연결하고 `NoteParagraphGap`으로 빈 문단 줄을 10dp로 표시합니다. 상세 범위와 전후 화면은 [0.8.1 보고서](body-readability-0.8.1.md)에 있습니다.

최종 빌드 성공, JVM **100/100**, Debug/Release lint 각각 **오류 0·경고 8**을 확인했습니다. 보호 대상 콘텐츠·자산 **527파일은 byte 단위 동일**합니다. 초기 태블릿 전체 94개 실행에서는 기존 87개가 모두 통과했고 신규 7개 중 4개가 검사 코드에서 실패했습니다. 폭 할당값을 글자 잘림으로 오판한 검사를 실제 줄 경계·원문 끝 포함·세로 잘림/말줄임 검사로 보완하고, 중복 요약 문장 선택자를 고쳤습니다. 초기·중간 실패 로그는 보존했습니다.

최종 영향 범위 재실행은 태블릿 **1600×1000dp / 1.0배에서 8/8**(신규 7개+기존 필기 테마 1개), 휴대폰 **360×800dp / 1.0배와 2.0배에서 각각 7/7**, 데스크톱 폭 **1920×1080dp / 1.0배에서 7/7** 통과입니다. 원문 quote 보존·문단 경계 선택·동일 native TextView 재사용·강조 span·이전/다음·채점 시점·표 스크롤·SQL 공백을 검사했습니다. 초기 전체 실행과 최종 재실행을 단일 최종 **94/94** 결과로 합치지 않습니다. 근거는 `evidence/body-readability-20261013/`의 `build-verified.log`, `jvm-lint-summary.json`, `content-preservation.json`, 각 프로필 `instrumentation.log`와 `environment.json`입니다.

기존 기록을 가진 Debug 0.8.1 앱의 MainActivity를 연 뒤 전체 DB를 비교해 상태 필드 변경 0개, 제출 55행·복구 지점 1행 동일을 확인했습니다(`record-preservation.json`). 세션 5·제출 55·별표 1·텍스트 필기/메모 2·노트 진도 4·강의 진도 5·코드 필기 문서 0이며 데이터 초기화는 하지 않았습니다. 최초 비교 실패는 tuple/list 자료형 불일치였고 저장 JSON 자체는 동일했습니다. 비교 도구를 보완한 PASS와 초기 실패 자료를 함께 보관했습니다. 이후 같은 서명 Release의 `install -r` 성공과 콜드 실행·versionCode 16 / 0.8.1을 확인했지만 Release 설치 후 DB를 다시 내보내 비교하지는 않았습니다. 검사 후 원래 표시 설정을 복원했습니다.

전 화면은 기존 0.8.0 에뮬레이터 캡처, 후 화면은 0.8.1 격리 DB의 실제 테스트 앱 캡처입니다. 메타데이터 161본문 항목을 161화면 전수 시각 검수로 표현하지 않습니다. 실제 Galaxy Tab/S Pen·제조사 멀티윈도우·TalkBack·학습효과·공식 시험 범위 검증은 포함하지 않았습니다. 아래 이전 버전 결과와 합산하지 않습니다.

## 0.7.0 SQL 따라 읽기·코드 필기 — 2026-10-07

기존 문제와 해설에 SQL 현재 구문·실제 값의 중간표·직접 이전/다음·문서 좌표 필기를 연결했습니다. [구현·적용 범위·실행 결과](sql-reader-0.7.0.md), [133문항 적용 및 미적용 사유](sql-walkthrough-coverage.md)를 확인하세요. 기존 콘텐츠·자산·Room schema 131파일과 업데이트 전후 기존 학습 필드 보존을 확인했습니다. 최종 Release에서도 user0 기록은 첫 갱신 후와 같고, 별도 QA 사용자가 직접 쓴 필기 1문서는 APK 갱신·화면 크기 변경·재실행 뒤 정확히 같았습니다. JSON 학습 상태/백업은 schema 3이며 이전 1/2는 읽고, 구버전 앱은 새 백업을 거부합니다.

SQL 최소 높이까지 수정한 **최종 빌드**에서 JVM **89/89**, 태블릿 전체 **78/78**, 폰 **320dp/150% 10/10**, **320dp/200% 선택 범위 4/4**가 통과했습니다. Debug/Release lint는 각각 오류 0·경고 8입니다. 자동 기기 검사는 독립 DB를 쓰는 Debug 앱에서, 실제 화면·업데이트 기록 검사는 Release 앱에서 진행했습니다. 최종 로그는 `evidence/sql-reader-20261006/build-viewport-final.log`와 `instrumentation-summary.json`을 따릅니다. 콘텐츠 검사는 SQL 필드가 있는 217문항 중 적용한 133문항과 별도 예시 1개의 875단계·873표, 경계 검사13개, 독립 값 대조49개를 포함합니다. 미적용 84문항은 이유를 기록하고 기존 해설을 유지하며 SQLite 3.50.4 비교를 Oracle 실행으로 표현하지 않습니다.

**최종 Release 화면 확인:** 실제 폰에서 발견한 SQL 첫 줄 잘림을 수정하고, 태블릿의 SQL·해설·중간표 동시 표시와 코드 필기, 펜 설정, 일반 객관식 한 화면, 320dp/150% 해설 스크롤을 다시 확인했습니다. [태블릿 화면](../evidence/sql-reader-20261006/runtime/public-sql-reader-final-tablet.png), [객관식 화면](../evidence/sql-reader-20261006/runtime/public-sql-reader-final-mcq-phone.png), [큰 글씨 화면](../evidence/sql-reader-20261006/runtime/public-sql-reader-phone320-text-fixed.png)을 남겼습니다. 수정 전 불량 캡처와 초기 검사 도구·테스트 호스트 실패는 보고서에 구분해 보관합니다. Release 빌드 APK는 18,176,370바이트로 이전 버전 대비 +448,225바이트(+2.53%)이며 실제 패키징 산출물·해시는 `dist/manifest.json`으로 확인합니다. 실물 Galaxy Tab/S Pen·팜리젝션·Oracle 실행·사람 전문가 검토·학습 효과는 미검증입니다. 아래 이전 버전이나 서로 겹치는 검사 수와 합산하지 않습니다.

## 0.6.2 버튼 간격·줄바꿈 — 2026-10-06

좁은 화면의 버튼 압축과 제목·날짜 줄바꿈을 개선했습니다. [변경·실행 근거](ui-spacing-0.6.2.md)를 참조하세요. 아래 0.6.1 전체 기능 검사와 이번 영향 범위 검사는 구분합니다.

## 0.6.1 실제 기능 QA — 2026-10-05

승인된 Canva 디자인을 유지하고 클릭·기록·오류 복구를 확인했습니다. [최종 판정](../FINAL_PRODUCT_GATE.md), [실제 검사 결과](../PRODUCT_QA_AFTER.md), [수정 내역](../PRODUCT_FIX_REPORT.md), [잔여 위험](../REMAINING_PRODUCT_RISKS.md)을 참조하세요. 아래 이전 버전 검사 수와 합산하지 않습니다.

## 0.6.0 Canva UI 디자인 적용 — 2026-10-05

현재 앱의 테마·홈·학습 계획·공통 카드와 SQL 표시를 개편했습니다. 콘텐츠·학습 기록의 저장 구조는 유지합니다. [이번 버전 실행 QA](ui-redesign-qa-2026-10-05.md), [디자인 출처와 범위](ui-redesign-design-source-2026-10-05.md)를 확인하세요.

## 0.5.0 날짜별 학습 계획 — 2026-10-05

104강과 교재 5권을 28공부일로 배치하고, 기존 앱 내용을 복습으로 연결했습니다. [이번 버전의 검사와 한계](study-plan-2026-10-05.md)에 실제 증거를 기록합니다. 이전 버전의 검사 수를 이번 결과와 합산하지 않습니다.

## 0.4.1 학습 화면 폭 개선 — 2026-09-29

이번 변경은 태블릿 본문 폭과 큰 그림의 표시 해상도에 한정합니다. [검증 보고서](visual-width-0.4.1.md)에 이번 버전의 실제 검사와 화면을 기록합니다.

## 0.4.0 그림 통합 검사 — 2026-09-29

이번 변경의 실제 검증 범위와 한계는 [0.4.0 통합 보고서](visual-integration-0.4.0.md)에 기록했습니다. 아래 내용은 이전 버전의 증거이며 최신 검사 수로 합산하지 않습니다.

# SQL 노트 버전별 QA 안내

> 이전 0.3.2는 넓은 화면의 왼쪽 메뉴·노트 목차에 접기/펼치기를 추가했습니다. [목록 접기 QA](sidebar-0.3.2.md): 태블릿 UI 8개 통과, 최종 release에서 접기·복원·자기점검 답안·화면 크기 전환·200% 글씨 확인. 콘텐츠와 기록 형식은 변경하지 않았으며 실기기는 미검증입니다.

> 이전 0.3.1은 노트·검색·초시계·저장·백업 검사의 반복 작업을 줄였습니다. [최적화 보고서](optimization-0.3.1.md): JVM 72개·Android 44개, 200% 큰 글씨 6개 통과, release lint 오류 0개·기존 경고 4개. 0.3.0→0.3.1 업데이트에서 강의 진도와 답안을 포함한 상태 전체 필드가 동일했습니다. 콘텐츠와 채점 엔진은 변경하지 않았으며, 실제 Galaxy 속도 측정은 하지 않았습니다.

> 이전 0.3.0은 제공한 63강 자료와 별도 진도를 통합했습니다. [통합·QA 보고서](course-integration-0.3.0.md): JVM 66개·Python 50개·Android 36개 및 200% 큰 글씨 강의 UI 3개 통과, release lint 오류 0개·경고 4개. 기존 55개 제출 등 업데이트 기록 보존을 확인했습니다. [콘텐츠 검토](course-content-review.md)는 SQLite 직접 실행 50개와 대체식 10개를 Oracle 실행·사람 검수와 구분합니다. Galaxy 실기기 검증은 하지 않았습니다.

> 이전 0.2.2 줄바꿈·화면 정리 결과는 [readability-qa-0.2.2.md](readability-qa-0.2.2.md)에 기록합니다. JVM 55개·Android 28개 검사, release lint 오류 0개, 기존 기록 보존과 최종 release APK의 일반·큰 글씨·작은 창·태블릿 화면을 확인했습니다. Python 검증기 31개는 해당 UI 변경에서 재실행하지 않았습니다.

> 이전 0.2.1 버그 수정·사용성 검증은 [usability-qa-0.2.1.md](usability-qa-0.2.1.md)에 기록합니다. 0.2.1에서 JVM 55개·Python 31개·Android 26개 검사와 API34 에뮬레이터 릴리스 화면·백업·업데이트 기록 보존 검사를 완료했습니다. 아래 이전 버전의 PASS와 별도로 재검증한 결과입니다. 0.2.0의 콘텐츠 보강·중요도 검증은 [priority-update.md](priority-update.md)를 참조하세요. 최신 콘텐츠 수량과 검수 집계는 [coverage.md](coverage.md) 및 [content-review-summary.json](../evidence/content-review-summary.json)에 있습니다.

## 0.1.0 실행 QA 기록

검증일: 2026-09-14. **설치 가능한 개인용 디버그 앱입니다. 완성품 검증 완료·공식 SQLD 검증·학습 효능 입증으로 판정하지 않습니다.**

## 환경과 실제 명령

- Windows 11, PowerShell, Android Studio JBR 21.0.10, Gradle 8.13, AGP 8.13.1, Kotlin 2.0.21. Android SDK compile36/target35/min26.
- 최종 전용 AVD: `SQLNote_QA`, `emulator-5590`, Android 14/API34, x86_64 Google APIs Play Store 이미지, Emulator 36.5.10, 소프트웨어 GPU. 로그인하지 않았습니다. 비행기 모드·Wi-Fi 꺼짐 상태에서 앱을 실행했습니다.
- 독립 AVD는 `D:\SQLD\.android\avd`에 있습니다. 초기에는 기존 에뮬레이터가 이 작업에서 시작된 것으로 잘못 판단한 구간이 있었습니다. 다른 프로젝트 데이터가 있는 것을 확인한 뒤 화면 크기/밀도/글꼴/야간 설정을 캡처된 기준으로 복구하고 이후 검증을 전용 AVD로 옮겼습니다. 기존 앱/AVD 데이터를 초기화하지 않았습니다. 최종 대표 증거는 `dedicated-*`, `instrumentation-final-*`를 사용합니다.
- 에뮬레이터 37.1.11 부팅 정지와 구버전의 한글 경로 해석 실패는 실행 환경 문제로 기록했습니다. 설치된 `C:\Android\Sdk`의 이미지와 36.5.10으로 해결했습니다.

```powershell
$env:ANDROID_HOME='C:\Android\Sdk'
$env:PYTHONIOENCODING='utf-8'
python scripts/validate_content.py
python -m unittest discover -s scripts -p 'test_*.py' -v
./scripts/build.ps1 -Tasks assembleDebug,testDebugUnitTest,assembleDebugAndroidTest,lintDebug -Offline
adb -s emulator-5590 install -r app/build/outputs/apk/debug/app-debug.apk
adb -s emulator-5590 install -r app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb -s emulator-5590 shell am instrument -w kr.sqld.study.test/androidx.test.runner.AndroidJUnitRunner
python scripts/device_qa.py window 640x1280 --density 320 --font 2.0 --night yes
adb -s emulator-5590 shell am instrument -w -e class kr.sqld.study.LearningUiTest kr.sqld.study.test/androidx.test.runner.AndroidJUnitRunner
```

최종 패키지에 대응하는 빌드·설치·테스트 기록과 파일 검사값은 `evidence/final-delivery-*`, `dist/manifest.json`에 별도 보관합니다. 소스 변경 후 이 증거를 자동 승계하지 않습니다.

## 자동 검증

| 검사 | 실제 결과 | 증거 |
|---|---|---|
| JVM 채점·복습·노출·시계·snapshot | 32 PASS | `evidence/jvm-results/TEST-kr.sqld.study.StudyEngineTest.xml` |
| JVM 백업 형식·손상·참조·미래 schema 등 | 18 PASS | `evidence/jvm-results/TEST-kr.sqld.study.BackupCodecTest.xml` |
| Room 통합 | 10 PASS | `final-delivery-instrumentation.log` |
| 실제 Compose UI | 6 PASS | `final-delivery-instrumentation.log`, 합계16 |
| 320×640dp / 200% / 다크 UI | 6 PASS | `instrumentation-final-font200.log` |
| 1600×1000dp / 가로 태블릿 UI | 6 PASS | `instrumentation-final-tablet.log` |
| 콘텐츠 구조·출처·중복·분포·fixture·검수 hash | 생성 검증 게이트 통과, 세부 수치 별도 | `content-validation.json`, `docs/coverage.md` |
| 검증기 자체 회귀·마스킹 도구 | 28 PASS | `content-validator-tests.log`, `blind-review-helper-tests.log`, `final-delivery-python.log` |
| Android lint | 오류0·경고22(버전 갱신 권고21, KTX 표현 권고1) | `evidence/lint-results-debug.xml`, 최종 로그 |
| 색상 대비 | 지정16쌍 모두4.5:1이상, 최소6.254:1 | `accessibility-checks.json` |

JVM 상태 기반 테스트는 seed7/42/20260914에서 선택·이동·채점·별표·중단을 각180회 섞어 총540전이를 검사합니다. 이것은 실제 수험생 학습 효과 시뮬레이션이 아닙니다.

Room 테스트는 사용자 DB와 분리된 DB를 사용해 재열기, 제출 유일성, 교체 전 복구 지점, 반복 복원, 트랜잭션 실패 주입과 rollback을 검사합니다. Compose 테스트도 별도 in-memory Room을 사용합니다. 보기 선택과 제출 구분, 다른 문항 초안 보존, 개별→전체 제출 중복 방지, 명시적 미응답, 실전 전환 확인/취소/영구성, 별표 해제 후 세트 유지, 과거 원판정과 현재 참고 판정의 구분을 조작합니다.

## 실제 앱과 파일 검증

| 동선 | 실제 확인 결과 | 증거 |
|---|---|---|
| 오프라인 첫 실행 | 빈 개인 DB에서 노트/메뉴 표시 | `dedicated-home.png`, `dedicated-launch.log` |
| 실제 파일 백업→깨끗한 별도 앱→복원→재내보내기 | 시도4·별표1·필기1·세션1·노트진도1·복습4·노출4, 설정 포함 모든 payload 필드 일치(내부 revision 제외) | `dedicated-backup-comparison.json`, 원본/복원 JSON |
| 복원 미리보기와 복구 지점 | 적용 전 0→4 시도 표시, 복원 전 빈 상태를 다시 열어 확인·취소 | `dedicated-restore-preview.png`, `dedicated-recovery-preview.png` |
| 모의 도중 강제종료·재실행·가상기기 재부팅 | 세션/첫 답안/2번 위치/strict 유지, BOOT_COUNT1→2, 남은시간 감소, 허위 시계이상·중복제출 없음 | `dedicated-timer-comparison.json`, `timer-*/summary.json` |
| 200% 다크 실전→연습→현재 미응답 채점→전체 제출→결과 | 확인창/확정 버튼 접근·채점 잠금·2점 결과 표시 | `dedicated-font200-*.png` |
| 문장 선택→밑줄 저장 | Android 선택 메뉴에서 ‘대출과’를 선택하고 밑줄 저장, DB quote/style 확인 | `dedicated-text-selection-second.png`, `dedicated-underline-dialog.png`, `annotation-after-selection/state.json` |
| 메모 유지 | 파일 복원 후 `QA_note_preservation` 메모와 강조가 재시작 후 표시 | `dedicated-tablet-note.png` |

화면 크기는 `wm size/density`로 앱 창 크기를 바꾼 **에뮬레이션**입니다. 태블릿 세로와 좁은 창의 재배치는 확인하되, 실제 Galaxy Tab 분할 화면 멀티윈도우 검증이라고 부르지 않습니다. 스크린샷마다 환경 JSON을 함께 기록합니다. SQL 표·해설은 검토한 정적 교육 자료이며 DB 실행 추적 화면이 아닙니다.

## 발견한 문제와 처리

- 일반 연습의 점수 계산이 모의고사 총 문항수를 가정하던 오류 수정. 연습은 실제 문항수로 계산하고 모의만 과목별 합격 기준을 적용합니다.
- 큰 글꼴에서 채점 버튼이 옆 버튼에 눌리던 배치 수정. 200%에서는 채점 버튼을 한 줄 전체에 배치합니다. 큰 글꼴의 하단 메뉴는 읽을 수 있는 접근성 이름을 가진 아이콘 메뉴로 전환합니다.
- 별표 취소 알림이 계속 떠 있어 다음 버튼을 가리던 문제 수정. 짧은 Snackbar로 바꾸고 버튼 영역 위에 배치했습니다.
- 문항 이동 버튼의 접근성 노드 높이가46dp로 잡힌 부분을 수정했고, 최종 APK에서58×50dp로 재측정했습니다(`final-delivery-touch-target.json`). 이전 캡처의46dp 발견 기록은 보존합니다.
- 노트 간 스크롤 상태 혼용 수정. 노트/문항별 위치를 분리합니다.
- 첫 Android 테스트 실패 중 중복 텍스트 노드/화면 전환 대기/화면 밖 버튼 클릭을 재현하고 테스트 선택·대기를 보완했습니다. 전용 기본화면16, 200%6, 태블릿6 재실행 PASS입니다. 실패 로그를 삭제하거나 PASS로 바꾸지 않았습니다.
- lint 의존성이 없는 오프라인 실행은 실패했습니다. 공식 의존성 다운로드 후 검사했습니다. 유효한 Java Unicode escape를 lint가 Windows 구분자로 오인한 로컬 SDK 경로 문제는 설치된 ASCII SDK로 검사하여 해결했습니다. 오류를 전역 suppress하지 않았습니다.
- Android 자동 백업은 allowBackup/fullBackupContent=false, API31+ cloud/device-transfer의 각 저장 도메인을 명시적으로 제외합니다. 실제 제조사 이동 도구를 실행한 검증은 아닙니다.
- 콘텐츠 검토에서 모호한 SQL 조건과 해설 문구, 같은 판단을 이름만 바꾼 모의 문항을 발견했습니다. 검수 미달 세트가 일시 차단됐으며 교체·재검토 후 복구했습니다. 최종 상세 결과는 `content-review.md`/`corrections.md`에 있습니다.

## 성능과 검증 경계

`am start -W` 관찰치는 첫 전용 실행1457ms, 강제종료 후1192ms, 기기 재부팅 후3525ms입니다. 기기 상태·캐시·앱 기록이 서로 다른 단발 측정이므로 평균 성능이나 보장치로 해석하지 않습니다. 600콘텐츠를 로드하는 실제 앱을 조작했으나, 수만 회 장기 학습 기록/낮은 저장 공간/메모리 압박의 체계적 성능 시험은 미실시입니다.

**미실행 또는 부분 확인:**

- 현행 DataQ 출제기준·시험 변경·정오표 공식 원문 접근 실패. 34학습목표의 공식 필수범위 완전 일치 판정 보류.
- Oracle/SQL Server 실행0, 사람 전문가 검수0, 실제 수험생 학습 효과 검증0. 창작 정답은 공식 문서와 AI 독립 풀이/해설 검토 근거이며 엔진 결과가 아닙니다.
- fixture 예상표는 `String?` 값입니다. Kotlin 값/열위치/중복 bag/순서를 검사하며 SQL 데이터타입·숫자 정밀도·드라이버 결과 정규화까지 검증하는 도구는 아닙니다.
- TalkBack 실제 음성 읽기 순서, 외부 키보드 전체 동선, Galaxy S24+/Tab 실기기, 제조사 분할화면, Android8/15/16 기기 QA 미실시. 지정 대비쌍 및 캡처의 선택된 타깃 검사만으로 WCAG 완전 준수를 주장하지 않습니다.
- 문항 이동 버튼은 최종 접근성 노드 높이도 재측정했습니다. 스크롤 아래로 일부만 노출된 보기의 작은 경계는 전체 터치 크기와 구분합니다.

- 실제 OS 디스크 고갈·기록 저장 중 전원 단절 시험 미실시. DB 저장 실패를 테스트에서 주입한 증거와 구분합니다.
- 최초 Room schema1이므로 과거 배포 schema에서 실제 앱 업데이트 마이그레이션 증거가 없습니다. snapshot/노트 anchor 재연결 및 데이터보존 테스트는 수행했습니다.
- 백그라운드 프로세스 종료 상태에서 OS가 만료 순간 점수를 쓰는 서비스는 없습니다. 재실행 시 시계 기준으로 만료를 처리합니다. 실제90분 방치 시험은 미실시이고 경계값은 자동 테스트로 확인했습니다.
- 일부 한국어 띄어쓰기·짧게 잘린 문항 제목과 제한된 텍스트 anchor(동일 문장 반복 시 첫 위치)는 추가 개선 여지가 있습니다. 문제 화면의 본문은 stem을 표시합니다.
- 공개 배포·릴리스 키 서명·Play 제출 없음. 계정·결제·광고·분석SDK·런타임 INTERNET 권한 없음.

## 완료 판정

노트·퀴즈·두 채점·현재문항만 채점·복습·별표·모의·기록·검색·개인필기·백업·복원의 로컬 앱 구현과 위 자동/에뮬레이터 검증은 완료했습니다. 공식 범위 확인, 엔진·전문가 검수, 지정 실기기/접근성의 미검증 항목 때문에 마스터 명령서의 ‘완성판 검증 완료’ 조건을 모두 충족했다고 판정하지 않습니다.
