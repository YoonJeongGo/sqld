# 63강 교재와 핵심 그림 27장 통합 — 0.4.0

2026-09-29. 현재 Android 앱의 콘텐츠와 표시 화면을 개선했다. Kotlin/Compose/Room/DataStore, 기존 41개 노트·661개 창작 채점 문항, 왼쪽 목록 접기·펼치기와 태블릿 가로 배치를 유지했다. 새 앱·웹판을 만들거나 ZIP 전체를 덮어쓰지 않았다.

## 설치와 학습 흐름

`dist/SQL-note-0.4.0-release.apk`를 기존 앱 위에 업데이트 설치한다. 개발 서명을 유지했으며 공개 배포용 서명이나 Play 등록은 아니다. 기존 앱을 제거하지 않는다. 업데이트 전 앱의 **설정 → 전체 기록 내보내기**로 개인 기록을 따로 보관할 수 있다.

**오늘 → 63강 이어보기**, 또는 **노트 → 강의 순서 → 강의**로 들어간다. 핵심 정리에서 쉬운 뜻, 연결된 그림, 번호별 읽기 순서, 결과와 이유, 주의점, 한 줄 기억을 읽는다. **기존 SQL 예제로 연습하기**로 이동하면 다른 데이터로 구성된 원래 입력표·SQL·풀이 단계·결과를 확인한다. 그 강의의 모든 예제 결과를 펼친 뒤 **그림과 예제 비교 해설**이 나타난다. **자기 점검**의 입력·답안 펼치기·자기 평가는 기존처럼 별도 진도로 저장된다.

그림은 8:5 비율의 PNG다. 그림을 누르거나 확대 버튼을 누르면 **화면 맞춤 / 원본 크기 / 확대 / 축소**, 핀치와 양방향 끌기를 사용할 수 있다. 원본 크기는 원본 픽셀 대비100%다. 회전 시 화면 맞춤 기준이 변해 표시 배율은 바뀔 수 있고 이동 위치는 새 화면 경계로 보정한다. 전체 그림 글자와 읽기 안내는 검색에 포함되며, **그림의 표·글자를 텍스트로 보기**에서 선택·복사한다. PNG 속 `[다음]`·화살표는 정적 표식이고 기존 예제 단계 버튼은 실제 동작한다.

## 검토·보존 결과

- 63강 전수 검토: **유지18 / 설명 보완5 / 오류 수정3 / 그림 안내 추가37**. 오류 수정 분류에서도 연결된 그림 안내는 제공한다. [강의별 변경 근거](visual-lesson-changes.md).
- 강의63개, 개념490개, 예제95개, 자기점검189개, 기존 표223개·SQL70개·SVG63개를 보존했다. 전체 강의·예제·자기점검 ID와 순서, 모든 결과표와 자기점검 질문·답·해설이 동일하다. 예제93개는 전체 내용 동일, 2개만 아래 정정을 포함한다.
- 원본에 별도의 `learningObjectives` 배열은 없다. 실제 존재하는 `easy/why/concepts/memory/traps/examples/quiz`를 대조했다. 누락된 가상 필드를 보존했다고 표시하지 않는다.
- 기존41노트·661문제 콘텐츠 팩은 바이트 단위로 동일하다. 노트/블록/문항/family/choice/정답 ID와 기존31건의 교재 정정도 유지했다. [실제 보존 검사17건](../evidence/visuals-preservation.json).
- 그림27개, 연결45개, 연결된 강의40개. 연결 없는23강은 표·SQL·결과로 충분한 이유를 각각 기록했다. 별도 그림을 억지로 넣거나 기존 자산을 삭제하지 않았다. [연결표와 미연결 이유](visual-lesson-map.md).
- 27장의 PNG를 직접 열어 AI 시각 검토하고 manifest·scenes·실제 SVG 글자/연결/표를 대조했다. 추가로 PNG 전체 청크 CRC·압축 픽셀 해제·2400×1500 크기, SVG 활성 콘텐츠·외부 경로 차단과 전사 일치를 검사했다. [27장 데이터 일치 점검표](visual-data-consistency.md). 검토 수·문장 수가 설명 품질이나 학습 효과의 입증은 아니다.

## 수정한 오류

1. **CUBE 그림20**: `(과목) → ()` 화살표의 `지역 제거`를 `과목 제거`로 고쳤다. 원본 SVG의 해당 한 텍스트를 수정해 PNG를 다시 렌더링했다. 수치·표는 동일하다. 원본 PNG/SVG는 `content/course-visuals/originals/`에 보존했다. [정정 및 렌더링 근거](../evidence/visuals-corrections/20-correction-evidence.json).
2. **2-3-04-E02 디비전**: 이름 대신 고정 학번1001~1004로 같은 학생을 연결한다. 기존 이름·과목 셀과 결과 박상현·김현수는 유지했다. 표시 SQL과 검사 fixture를 함께 수정했고 동명이인 반례도 검사했다. 해당 강의만 version2로 올려 이전 읽음 기록은 남기고 **보강 내용 확인 전**을 표시한다. 예전 점수를 새 문제에 옮기는 변경이 아니다.
3. **조사 두 곳**: 1-1-06 `유성재”은 → 유성재”는`, 2-1-25-E02 `박보성로 → 박보성으로`. 문제 의미나 결과는 바꾸지 않았다.
4. **비교 해설의 정답 선노출**: 예제 위에서 정답을 미리 보여 주던 새 안내는 모든 예제 결과를 확인한 뒤에만 표시한다. 일반 데이터 전환 안내는 예제 앞에 유지한다.
5. **320dp·글꼴200%의 확대 화면 재배치 반복**: 배율 숫자와 긴 안내 문장을 한 Text에 놓으면 줄 수가 달라져 그림 영역 높이와 배율이 계속 바뀌었다. 배율을 고정폭100dp·한 줄 영역으로 분리해 반복을 없앴다. 실패했던 같은5검사는 수정 후 모두 통과했고, 최종 APK에서도 다시 검사했다.
6. **학습 본문 정리**: 자료 점검용 `manifest/scenes/source_tables` 표현은 본문에서 빼고 실제 입력과 기존 예제의 차이·가정을 설명했다. 동일 의미의 경고는 합쳐94개에서73개로 정리했다. 검토용 세부 근거는 원본 검토 JSON과 점검표에 유지했다.

## 기존 기록과 복원 가능 백업

변경 전 원본 파일154개의 복구 ZIP, 파일 해시, 기존 APK manifest와 검사 로그를 `evidence/visuals-0.4.0-before/`에 보관했다. 두 입력 ZIP은 별도 디렉터리에 추출해 읽었으며 공급자의 생성 코드를 실행하지 않았다. 입력 ZIP 위치·해시는 [입력 기록](../evidence/visuals-inputs.json)에 있다.

실제로 존재하는 저장 항목은 세션·확정 제출·노출·복습·문제 별표·노트 북마크·문장 필기·노트 진도·내용 오류 신고·설정, 강의 읽음/탭/스크롤/풀이 단계/결과 공개/자기점검 답안·평가/마지막 강의다. 강의에 새 범용 메모 기능을 만들었다고 주장하지 않는다. Room schema1·백업schema2와 저장 구조는 유지했다.

전용 SQLNote_QA 에뮬레이터의 기존 DB와 앱 호환 복구 백업을 비공개 `evidence/visuals-private-before/`에 보관했다. 최종 업데이트 직전/직후 DB는 `visuals-private-before-final/`, `visuals-private-after-final/`에 있다. **전체 StudyState와 revision566이 업데이트 전후 완전히 동일**했다. 기존5세션·55제출·55복습·165노출·1별표·2필기·3노트 진도·설정도 최초 작업 전 상태와 동일하다. 시범 화면 수동 열람으로 강의 진도는1개에서2개가 됐으며, 최종 업데이트 전후 두 기록은 그대로다. [개인 내용 없는 비교 결과](../evidence/visuals-state-update.json). 실제 사용자의 Galaxy DB를 읽은 검사가 아니다.

개인 DB·원본 복구 백업·서명 키·ADB 키는 소스 ZIP에 넣지 않는다. 테스트는 별도 메모리/전용 DB를 사용하며 학습 앱 데이터 초기화나 제거를 하지 않았다.

## 실제 검사 결과

| 검사 | 실제 결과 | 증거 |
|---|---|---|
| 정본/설치 콘텐츠 검증 | 기존 콘텐츠 strict·63강·27그림 통과 | visuals-main-validation.log, visuals-assets-final.log |
| Python 회귀 검사 | 63/63, 실패·skip0 | visuals-python-tests-final.log |
| JVM 단위 검사 | 72/72, 실패·skip0 | jvm-results/TEST-*.xml |
| 최종 debug/release 빌드 | 성공, 0.4.0/versionCode8 | visuals-build-delivery.log |
| release lint | 오류0 / 기존 경고4 | lint-results-release.txt |
| Android 태블릿 가로 | 1280×800dp·100% 글자, 전체52/52 | visuals-delivery-tablet-android.log |
| Android 휴대폰 | 360×800dp·100% 글자, 강의/그림8/8 | visuals-delivery-phone-android.log |
| Android 좁은 화면·큰 글자 | 320×640dp·200% 글자, 그림5/5 | visuals-delivery-large-font-android.log |
| 설치 APK 자산 | debug/release 각각57파일 정본 일치, 기존 서명 유지·INTERNET 없음 | visuals-apk-integrity.json |
| 실저장 업데이트 | 최종 APK 업데이트 후 전체state·revision566 동일 | visuals-state-update.json |

검사 로그는 [evidence](../evidence/) 아래에 있다. Android 자동 검사는 API34 SQLNote_QA 에뮬레이터의 debug APK에서 수행했다. 세 환경에 반복된 검사가 있으므로52+8+5를 서로 다른65개 기능으로 세지 않는다. 최종 자동 검사 APK SHA-256은 `dfe4e5654c5d9bad5c4379b0de2f8529130e802e18734109373aac8a79286cee`다.

릴리스 APK도 `install -r`로 실제 설치했다. [태블릿 전체 그림](../evidence/visuals-release-tablet-cube-fit.png), [휴대폰200% 화면 맞춤](../evidence/visuals-release-phone-large-fit.png), [크기 변경 후 확대 상태](../evidence/visuals-release-phone-large-restored.png), [다크 모드 텍스트/표](../evidence/visuals-release-phone-dark-text.png), [실제 선택·복사 메뉴](../evidence/visuals-release-phone-text-selection.png), [복사된 값 미리보기](../evidence/visuals-release-phone-text-copied.png), [기존 개념도](../evidence/visuals-release-original-diagram.png)를 확인했다. CUBE 원본 보기·150% 확대·팬, 가로→세로 화면 크기 변경 중 열린 그림 유지, 화면 맞춤·닫기, 텍스트 펼치기·복사와 기존 개념도 열기/닫기가 동작했다. 현재 릴리스 프로세스 로그의 FATAL/ANR은0건이었다. 단일 cold start 관찰은1151ms이며 성능 보장이 아니다. [릴리스 검사 범위](../evidence/visuals-release-smoke.json).

복사 메뉴는 실제 화면에는 있었지만 Android 계층 덤프에는 없어 첫 자동 조작 스크립트의 탐색 assertion이 실패했다. 캡처에서 메뉴를 확인해 누른 뒤 복사 미리보기를 확인했으며, 앱 오류로 분류하지 않았다. 에뮬레이터의 크기·밀도·글꼴·야간 설정은 작업 전 값으로 복구했다.

시범 ALTER(2-1-04), OUTER JOIN(2-1-23), GROUP BY(2-1-20)의 3개 Android 검사를 통과한 뒤 전체27장으로 적용했다. 최종 결과는 위 표이며 변경 전 기준 검사를 최종 검사 수에 합산하지 않는다. 기준은 Python50·JVM72·태블릿 Android8 통과였다. 중간 Python60 검사에서는 원본과 완전히 같다고 가정한 보존 테스트2개가 정정을 거부했다. 전수 비교를 삭제하지 않고 독립적인 정확한 정정 허용목록·동명이인 회귀 검사로 보완했다. 실패 로그도 보존한다. 큰 글꼴의 초기5검사 중2건은 실제 레이아웃 반복으로 실패했으며 `visuals-large-font-android.log`에 남겼다. 시간 제한을 늘리거나 검사를 제외하지 않고 표시 코드를 고쳤다.

95예제 중 **SQLite3.50.4 직접50 / 대응식10 / 엔진 미실행35**다. 새 그림은 **14장에 관한26개 결과 검사**를 같은 SQLite에서 통과했다. ROLLUP/CUBE/PIVOT/UNPIVOT 등의 대응 계산은 Oracle 구문의 실행 증거가 아니다. 원본 SQL·테이블·예상 결과를 앱에서 동적으로 실행하거나 자동 채점하지 않는다. [교재 엔진 검사](../evidence/visuals-course-engine-final.log), [그림 실행식·입력·결과·문서 출처](../evidence/visuals-example-checks.json).

## 실행·콘텐츠 갱신

Windows PowerShell, JDK21, Android SDK36/build tools, Gradle8.13 환경이다. 다른 머신에서는 SDK와 기존 서명 키 경로를 지정한다. 아래 명령은 저장소 루트에서 실행한다.

```powershell
$env:PYTHONIOENCODING='utf-8'
$env:ANDROID_HOME='C:\Android\Sdk'
python scripts/validate_content.py --strict
python scripts/validate_course.py --engine
python scripts/validate_visuals.py
python scripts/verify_visual_examples.py
python -m unittest discover -s scripts -p 'test_*.py' -v
./scripts/build.ps1 -Tasks assembleDebug,assembleRelease,testDebugUnitTest,assembleDebugAndroidTest,lintRelease -Offline
adb -s <확인한-기기ID> install -r app/build/outputs/apk/release/app-release.apk
python scripts/package_artifacts.py --build-type release
```

최초 의존성 다운로드가 필요하면 `-Offline`을 생략한다. 앱의 실행에는 인터넷·로그인·Canva·외부 AI API가 필요 없다. `scripts/device_qa.py`는 SQLNote_QA 전용 에뮬레이터만 조작하도록 제한한다. 이번 실행은 ADB포트5039 / emulator-5590였다.

정본은 **`content/course-pack.json`**, **`content/course-visuals.json` + `content/course-visuals/`**다. 수정 후 `validate_course.py --sync-asset --engine`, `validate_visuals.py --sync-assets`로 검증하고 assets를 동기화한다. `content/visual-source/`는 수정하지 않은 공급 manifest/scenes/sources 보관본이며 앱의 두 번째 로더가 아니다. 원래63강 ZIP의 `src/build_content.py`를 실행하면 현재 정정이 사라질 수 있으므로 사용하지 않는다. 초기 `scripts/import_course.py`는 정본이 있으면 덮어쓰기를 거부한다. 새 그림도 initial import 후 정본을 편집한다.

그림 SQL 검사는 소스 ZIP 내부 자료로 재현된다. 원본63강과의 재수입 동등성 검사2개는 공급 ZIP 추출 디렉터리 `evidence/incoming-63lectures-20260928/SQLD_63_Visual_Notes/`가 없으면 명시적으로 skip한다. 최종 작업 폴더에서는 원본이 있어 실제 수행했다. 그 밖의 검사에는 외부 계정이나 원본 생성 코드 실행이 필요 없다.

## 되돌리는 방법

1. 현재 앱에서 전체 기록을 먼저 내보낸다. 이미 기록한 기존 파일을 덮어쓰지 말고 새 파일명으로 보관한다.
2. 코드 롤백은 `evidence/visuals-0.4.0-before/source-baseline.zip` 또는 기존 `dist/SQL-note-0.3.2-source.zip`을 **새 폴더에** 푼 뒤 파일을 비교한다. 현재 폴더에 ZIP 전체를 덮어쓰거나 원본을 삭제하지 않는다.
3. 일반 Android는 버전코드가 낮은 APK 설치를 거부할 수 있다. 제거 후 재설치 대신, 이전 코드의 버전코드를 현재보다 높여 같은 개발 서명으로 빌드하고 업데이트 설치한다. Room/백업 구조가 같으므로 새 그림을 제거해도 기존 학습 기록은 유지된다. 이 롤백 APK 자체의 설치 실험은 하지 않았다.
4. 필요한 경우 앱의 **백업 파일 검사·복원**으로 저장된 백업을 읽고 교체 전후 수량을 확인한 뒤 복원한다. 적용 직전 기록은 기존 원자적 복구 지점에 남는다. 예전 코드는 디비전 보강 여부를 표시하지 못하므로, 단순히 새 화면이 낯설다는 이유로 콘텐츠까지 되돌릴 필요는 없다.

## 미검증과 한계

- 실제 Galaxy Tab/S Pen·휴대폰 실기기, TalkBack 음성 순서·외부 키보드, 다양한 제조사 회전/분할화면은 미실시다. PC에서 실행한 Android 에뮬레이터의 태블릿/휴대폰 화면 검사이며 Windows 네이티브 앱이나 별도 웹판의 검사가 아니다.
- Oracle/SQL Server 실제 엔진, 현행 DataQ 공식 출제범위 완전 일치, 사람 전문가 검수, 학습 효과·합격 가능성의 실증은 완료하지 않았다. 사용자 교재를 공식 범위 전체나 실제 기출이라고 표시하지 않는다.
- 이름·점수·금액 등은 고정된 가상 예시다. 원본 그림의 이름을 UI에서 임의로 치환하거나 문제 의미를 바꾸지 않았다. 그림27의 네 칸처럼 한 장 안에서도 독립적인 데이터가 있음을 안내한다.
- 화면 맞춤의 작은 그림 글자를 원래 크기보다 읽기 좋다고 보장하지 않는다. 확대/팬과 텍스트 전사를 함께 제공한다. 원본20 재렌더링은 설치된 한국어 글꼴을 사용해 원본과 글꼴 모양이 일부 다를 수 있다.
- 기존 lint 경고4개는 그대로 남아 있다(줄바꿈 상수 API 표기2, target API 안내1, KTX 권고1). 오류는0이다. 관계없는 프레임워크·저장 로직 정리는 하지 않았다.
