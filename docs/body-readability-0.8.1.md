# 0.8.1 학습 본문 표시 개선

2026-10-13. 기존 SQLD 앱의 본문 표시만 변경했다. 설명·문제·보기·SQL·정답·표 데이터·학습 순서를 재저작하지 않았다. 이번 작업은 학습효과나 공식 시험 범위 검증이 아니다.

## 공통 구현

- `StudyBodyText.kt`: 일반 학습 본문 17sp, 보조 학습 설명 16sp, 줄높이 1.6배, 진한 중립색. 화면 폭에 따라 자연스럽게 줄바꿈하며 고정 줄수·말줄임·글자 자동 축소를 사용하지 않는다. 인라인 식별자는 같은 크기의 고정폭 글꼴, 핵심 구간은 Bold다.
- `BodyTextRules.kt`: 원문을 고치지 않는 표시 계획. 일반 강조는 첫 유효 등장만, 기본 후보는 실제 일치한 3구간까지다. 식별자 경계를 확인해 `id`를 `pid` 안에서 잘못 강조하지 않는다. 현재 SQL과 직접 연결되는 구간만 기존 파란 배경을 쓴다.
- `BodyTextOverrides.kt`: 정확한 원문 161개에 별도 강조·의미별 문단 메타데이터. 63강 개요·대표 단계, FK/INSERT 보충, 16종 노트의 24본문을 검토했다. 나머지 본문도 공통 글꼴·간격·기존 핵심어 정보를 사용한다. 모든 문장을 별도 문단으로 자르지 않는다.
- `StudySection`/`StudyPaper`: 제목과 설명 8dp, 같은 설명의 문단 10dp, 구간 16dp, 학습 카드 안쪽 16dp. 공통 대시보드 카드와 메뉴는 그대로다.
- `NoteTextProjection.kt`/`SelectableNoteText`: 선택 가능한 노트에도 명시한 문단 경계만 표시한다. 원문 문자와 공백을 삭제하지 않고 표시용 개행을 삽입한다. `NoteParagraphGap`은 삽입된 빈 문단 줄을 본문 한 줄 높이 대신 10dp 간격으로 표시한다. 선택 위치는 원문 위치로 역변환해 기존 형광펜·밑줄·메모 quote를 보존한다. 동일 View가 다른 본문을 표시할 때 최신 매핑과 콜백을 사용한다.
- `StudyTable`: 고정 120dp였던 열 폭을 현재 글자 크기·실제 헤더/값으로 측정한다. 각 열은 112~320dp이며 표 내부 가로 스크롤을 유지한다. NULL은 오류색 대신 명시적 `NULL ∅` 표기로 구분한다.

적용 화면: 진도별 개념, 강의 핵심 정리·예제 해설·자기점검 정답 공개 후 해설, 학습 노트, 예제 따라 읽기, 채점 후 문제 해설, 용어·주의, 그림 읽기 설명. 문제지문/선택지, SQL 블록/필기면, 그림 전체 전사문과 출처 URL은 원문 구조를 유지한다. 정답 공개 조건과 기존 메뉴·학습 동선은 변경하지 않았다.

SQL 및 문자열 공백은 일반 본문 정리 대상이 아니다. `010-****-1003`을 Markdown 구문으로 해석하지 않는다. 자동 문장 요약·문장별 강제 분리·공백 일괄 제거를 추가하지 않았다.

## 실제 검증 기록

- 변경 전 JVM 호출: Gradle `UP-TO-DATE`, 보관된 기존 결과 93개 통과. 이번 호출로 93개를 새로 실행했다고 주장하지 않는다.
- 변경 전 소스/자산/문서/스크립트 655파일을 ZIP과 SHA-256 목록으로 보관했다.
- 콘텐츠와 앱 자산 527파일은 변경 전 해시와 byte 단위로 동일하다. 정답·SQL·원문 JSON·예시 값·IDs 포함. 근거: `evidence/body-readability-20261013/content-preservation.json`.
- 실제 학습 DB/제출/복구 지점은 개인 기록이므로 `private_evidence/body-readability-20261013/`에만 보관하며 배포 파일에서 제외한다.

| 검사 | 실제 결과 | 근거 |
|---|---|---|
| 최종 Debug·Release·AndroidTest 빌드 | 성공 | `build-verified.log`, `BUILD SUCCESSFUL` |
| 최종 JVM 검사 | 100개 통과, 실패·오류·건너뜀 0 | `jvm-lint-summary.json` |
| 최종 Debug / Release lint | 각각 오류 0·경고 8 | `jvm-lint-summary.json` |
| 초기 태블릿 전체 실행 | 94개 중 90개 통과·4개 실패. 기존 87개는 통과, 신규 7개 중 4개가 검사 코드에서 실패 | `tablet-initial-instrumentation.log` |
| 최종 태블릿 재검사 | 신규 본문 검사 7개 + 기존 테마/필기 검사 1개, 8/8 통과 | `tablet/instrumentation.log` |
| 최종 휴대폰 재검사 | 신규 본문 검사 7/7 통과 | `phone/instrumentation.log` |
| 최종 휴대폰 200% 글씨 재검사 | 신규 본문 검사 7/7 통과 | `phone200/instrumentation.log` |
| 최종 데스크톱 폭 재검사 | 신규 본문 검사 7/7 통과 | `desktop/instrumentation.log` |

위 근거 경로의 기준은 `evidence/body-readability-20261013/`이다. 초기 전체 실행과 최종 영향 범위 실행은 별개이며 **최종 한 번의 94/94 통과 실행으로 합쳐 보고하지 않는다.** 마지막 표시 조정 후 기존 87개 전체를 다시 실행한 결과는 없다.

초기 실패 4개 중 3개는 `didOverflowWidth`만으로 실제 글자 잘림을 판정한 검사 문제였다. 진단 실행에서 제목의 실제 줄과 Text 폭은 249px인데 `MultiParagraph`가 부모의 할당 폭 775px를 유지해 overflow 값이 참이 되는 상황을 확인했다. 최종 검사는 각 줄의 좌우 경계가 실제 Text 폭 안에 있는지, 마지막 줄이 원문 끝까지 포함하는지, 세로 잘림·말줄임이 없는지를 확인한다. 허용 오차는 픽셀 반올림을 위한 1px다. 다른 1개는 동일한 해설 요약과 암기 문장이 존재하는 화면에서 테스트가 텍스트 노드 1개만 예상한 선택자 문제로, 대상 선택자를 보완했다. 초기 실패 로그와 중간 진단 실패 로그 `tablet-measurement-instrumentation.log`를 그대로 보존했다.

신규 검사는 실제 Bold span, 모델링 의미 문단, INSERT 컬럼·값 보존, 이전/다음 복귀, 용어·주의 설명, 채점 전 해설 비공개와 제출 유지, 긴 인라인 식별자, 표 내부 가로스크롤, SQL/문자열 공백을 확인한다. native 노트 검사는 문단 경계에 걸친 기존 하이라이트와 메모·밑줄 선택 콜백, 전체 선택의 원문 quote 복원, 같은 TextView가 다른 본문으로 바뀐 뒤 최신 매핑 사용을 포함한다. 테스트 학습 기록은 격리된 in-memory DB를 사용한다. 이 검사를 실제 사용자의 앱 갱신 전후 기록 비교와 동일하게 취급하지 않는다.

| 프로필 | 화면 설정 | 글씨 배율 |
|---|---|---|
| `phone` | 720×1600px / 320dpi = 360×800dp | 1.0 |
| `phone200` | 720×1600px / 320dpi = 360×800dp | 2.0 |
| `tablet` | 1600×1000px / 160dpi = 1600×1000dp | 1.0 |
| `desktop` | 1920×1080px / 160dpi = 1920×1080dp | 1.0 |

각 설정은 Android API 34 `SQLNote_QA` 에뮬레이터의 `environment.json`에 기록했다. dp 수치는 전체 에뮬레이터 화면 기준이며 앱 콘텐츠 영역은 시스템 바와 앱 UI가 차지하는 만큼 작다.

### 실제 기존 기록·업데이트 확인

기존 기록이 있는 앱에 Debug 0.8.1을 적용하고 `MainActivity`를 실제로 연 뒤 DB 전체 저장 필드를 비교했다. 초기화나 앱 데이터 삭제 없이 상태 필드 변경 0개, 제출 테이블 55행과 복구 지점 1행이 정확히 같았다. 기록 수는 세션 5, 제출 55, 별표 1, 텍스트 필기/메모 2, 노트 진도 4, 강의 진도 5, 코드 필기 문서 0이다. 코드 필기 문서가 없는 이 데이터의 비교를 실제 사용자의 펜 문서 보존 증거로 확대하지 않는다. 근거: `record-preservation.json`의 `allStoredFieldsEqual=true`, `submissionRowsEqual=true`, `recoveryRowsEqual=true`.

최초 기록 비교 도구는 SQLite 행의 Python tuple과 JSON을 다시 읽은 list를 서로 비교해 실패했다. 저장된 JSON snapshot은 당시에도 동일했으며, 비교 도구의 자료형을 list로 통일한 뒤 전체 비교가 통과했다. 이 진단 이력 `record-comparison-initial.json`도 보존했다.

이후 같은 서명의 Release APK를 `install -r`로 설치해 `Success`, 콜드 실행 `Status: ok`, versionCode 16 / 0.8.1을 확인했다(`release-install.log`, `release-version.log`). **Release 설치 이후 DB를 다시 내보내 비교한 것은 아니다.** 따라서 위 전체 DB 동일성은 실제 Debug 0.8.1 실행 전후의 결과이며 Release 설치 확인과 구분한다. 검사 종료 후 원래 화면 크기·밀도·글씨 등 표시 설정을 복원했다.

## 비교 화면

변경 전은 0.8.0의 기존 실제 에뮬레이터 캡처다. 캡처를 다시 그리거나 수정하지 않았다. 변경 후는 0.8.1의 격리된 테스트 DB에서 새로 실행한 실제 화면을 사용한다.

- 모델링 전: `evidence/body-readability-20261013/before/modeling.png`
- INSERT 전: `evidence/body-readability-20261013/before/insert.png`
- 변경 후 캡처·기기 설정·검사 로그: `evidence/body-readability-20261013/<profile>/`

| 대표 화면 | 변경 전 | 변경 후 |
|---|---|---|
| 모델링 개념 해설 | [0.8.0 기존 화면](../evidence/body-readability-20261013/before/modeling.png) | [0.8.1 태블릿](../evidence/body-readability-20261013/tablet/body-modeling.png) |
| INSERT 컬럼·값 해설 | [0.8.0 기존 화면](../evidence/body-readability-20261013/before/insert.png) | [0.8.1 태블릿](../evidence/body-readability-20261013/tablet/body-insert.png) |
| 선택 가능한 학습 노트 문단 | 해당 프로필의 동일 상태 전후 촬영 없음 | [0.8.1 노트 문단](../evidence/body-readability-20261013/tablet/body-note-paragraphs.png) |
| 휴대폰 큰 글씨 | 해당 프로필의 동일 상태 전후 촬영 없음 | [0.8.1 200% INSERT](../evidence/body-readability-20261013/phone200/body-insert.png) |
| 데스크톱 폭 | 해당 프로필의 동일 상태 전후 촬영 없음 | [0.8.1 모델링](../evidence/body-readability-20261013/desktop/body-modeling.png) |

변경 후 캡처는 Debug 테스트 앱의 실제 렌더링이며 실물 태블릿 촬영이나 최종 Release 수동 조작 증거가 아니다. 메타데이터 161개는 본문 항목 수로, 161개 전체 화면의 모든 상태를 시각 검수했다는 뜻이 아니다.

## 실행·갱신·되돌리기

```powershell
$env:ANDROID_HOME='C:\Android\Sdk'
python scripts/validate_content.py
./scripts/build.ps1 -Tasks assembleDebug,assembleRelease,assembleDebugAndroidTest,testDebugUnitTest,lintDebug,lintRelease -Offline
python scripts/package_artifacts.py --build-type release
```

앱은 같은 기존 서명으로 versionCode 16 / 0.8.1을 사용한다. 기존 앱 위에 업데이트한다. Room schema 1, 백업 schema 3, 콘텐츠 ID를 변경하지 않았다.

복구 원본은 `backups/body-readability-20261013/source-before.zip`과 `hashes.json`이다. 별도 폴더에서 비교해 변경 코드만 복구하고, 기존 서명과 더 높은 versionCode로 복구용 빌드를 만든다. 현재 앱을 제거하거나 DB를 지우지 않는다. 학습 기록의 복원은 기존 앱의 검사·미리보기·복구 지점·원자적 교체 절차를 사용한다.

## 검증의 한계

Android API 34 에뮬레이터 검사는 실제 Galaxy Tab/S Pen, 펜 지연·팜리젝션, 제조사 분할 화면 검증이 아니다. 데스크톱 폭은 Android 앱의 큰 창 배치를 검사하는 것이며 별도 웹/Windows 앱을 만들었다는 뜻이 아니다. 63강의 대표 표시 정보는 검토했으나 모든 화면의 모든 상태를 사람 사용자가 검수한 것은 아니다. 이번 프로필 검사는 글씨 1.0/2.0의 지정 크기에 한하며 모든 Android 버전·임의 배율·기기 조합을 검증하지 않았다. TalkBack 음성 읽기와 물리 키보드 선택 동작도 별도 미검증이다. 교육 내용의 정확성·SQL 엔진·학습효과는 이번 표시 변경의 검사와 구분한다.
