# 0.2.2 줄바꿈·화면 밀도 개선

2026-09-15. 글자가 어색하게 끊기거나 학습 목록보다 안내·필터가 더 크게 보이는 부분을 실제 Android 화면과 비교해 정리했다. 개인용 0.2.2 / versionCode 4.

## 변경

- 홈의 두 줄 슬로건과 중복 소개를 제거하고 `오늘의 학습`으로 바꿨다. 이어서 공부의 개념명과 `적용 연습` 등 학습 종류를 분리해 마지막 한 글자만 남는 제목을 줄였다. 목표일 미설정 안내도 홈에서 반복하지 않는다.
- 개념 노트·복습·설정·모의고사·학습 기록·필기·출처의 큰 홍보성 제목을 기능명으로 줄였다. 기능 화면 자체나 학습 자료는 삭제하지 않았다.
- 노트의 중요도 필터와 중요 배지는 항상 표시한다. 과목·정렬과 복습의 세부 조건은 필요할 때 펼치며, 접은 뒤에도 적용 조건을 표시하고 유지한다.
- 공통 제목·버튼의 줄높이는 글자 크기의 1.35배, 본문은 1.55배로 구분했다. 한국어 로케일과 제목/문단별 줄바꿈 규칙을 적용했다. 실제 확대 화면에서 문장 끝 한 글자만 남는 경우를 확인해 문단 줄 길이도 균형 있게 나누도록 조정했다. 의미 없는 강제 줄바꿈이나 보이지 않는 문자를 콘텐츠에 삽입하지 않는다.
- 학습 횟수·진도는 짧은 항목 단위로 줄이 넘어간다. 홈의 오늘 복습량과 전체 대상 수량은 분리했다. 빈 복습 목록의 비활성 시작 버튼과 공통 빈 상태의 큰 장식 아이콘은 제거했다. 처음 시작할 때도 진도 통계보다 노트 펼치기가 먼저 나온다.
- 카드 안쪽 여백은 20→16dp, 주요 화면 바깥쪽은 24→20dp로 조정해 작은 화면의 문장 폭을 확보했다. 큰 글씨/긴 분류명은 목록 번호와 제목을 위아래로 배치한다. 본문 글자를 축소하거나 말줄임으로 숨기지 않는다.
- 태블릿 노트 본문 최대 폭을 760dp로 제한해 지나치게 긴 한 줄을 줄였다. 좌측 목차는 유지한다. 선택 가능한 Android 본문은 한국어 문단 줄바꿈과 기존 필기/원문 텍스트를 함께 보존한다.
- 설정의 범위·날짜 형식·간격 설명을 짧은 입력 라벨 아래로 분리했다. 내용 오류 0건인 큰 빈 카드와 비활성 버튼을 한 줄 안내로 줄였다.
- 필기의 메모 수정·노트 보기·삭제 버튼은 폭이 부족하면 다음 줄로 흐른다. 모의고사 카드의 중복 `MOCK 01` 표기를 제거했다.
- 문제의 `original_practice`를 한국어 출처 유형으로 표시하고 문항 번호·버전을 별도 줄에 뒀다. 큰 글씨의 문제 모드와 타이머·문항 수도 분리했다. 연습 시작창은 짧은 제목 아래에 실제 학습 제목을 표시한다.

구현 참고: [Android 공식 문단 스타일/줄바꿈 문서](https://developer.android.com/develop/ui/compose/text/style-paragraph?hl=ko). 언어/OS/글꼴별 줄바꿈은 다를 수 있어 실제 캡처와 함께 판단한다.

## 검증

| 확인 | 결과와 증거 |
|---|---|
| 최종 소스 빌드 | `testDebugUnitTest,assembleDebug,assembleDebugAndroidTest,assembleRelease,lintRelease` 성공. `evidence/readability-build-balanced.log` |
| JVM 검사 | 55개 통과, 실패/오류 0. `evidence/readability-apk-verification.json`, `evidence/jvm-results/` |
| Android 검사 | 28개 통과, 44.032초. `evidence/readability-instrumentation-delivery.log`. 별도 DB의 영속·백업/복원 및 Compose 조작 검사 |
| 추가 UI 회귀 | 노트 필터를 접고 읽은 뒤 돌아와도 선택 유지, 복습 과목 변경 시 숨겨진 세부 주제 초기화와 실제 표시 조건으로 시작. 기존 일일 복습량·핵심 진도 검사도 새 배치에서 통과 |
| Release lint | 오류 0, 경고 4. OldTargetApi 1, UseKtx 1, InlinedApi 2. API29의 정수 줄바꿈 상수는 컴파일 시 정수 2로 삽입되어 해당 클래스의 런타임 필드 조회가 없는 것을 확인. API26 실제 실행 증거는 없음 |
| 업데이트 보존 | 기존 개발 서명을 유지. 제출 55·세션 3·필기 2·북마크 1·노트 진도 3 및 설정을 포함한 전체 상태가 업데이트 전후 일치. `readability-upgrade-preservation.json`, `readability-final-installed-apk.json`. 이후 화면 검사의 읽기 위치·학습 시간 변경까지 불변이라는 뜻은 아님 |
| 콘텐츠/엔진 보존 | 콘텐츠·채점/기록 엔진 13파일의 변경 전후 hash 일치. 노트 41·문항 661 유지. `readability-content-and-engine-preserved.json` |
| APK | release 디버깅 불가, debug 디버깅 가능. 두 APK 모두 콘텐츠 팩이 원본과 일치. `readability-apk-verification.json` |
| 앱 재시작 | 최종 release의 COLD 시작 성공(452ms). 해당 앱 프로세스 로그에서 FATAL EXCEPTION·앱 ANR 일치 항목 없음. 화면 검사를 마친 뒤 720×1600px·320dpi·글꼴 100%·라이트와 홈 화면으로 복구. `readability-final-runtime.json` |

이번에 실행한 앱 자동 검사는 합계 83개다. 이전 버전의 Python 31개 검사를 이번 결과에 합산하지 않는다. QA 보조 도구의 네트워크 ADB 대상 파일명에 콜론이 들어가던 Windows 문제도 수정했고, 기본 대상과 네트워크 대상의 파일명 생성 결과를 확인했다.

최종 release SHA-256: `ef7e06a3b577ff45d858e5ff3d29599ad2d4a42d1956be8e95ada46636ae7da2`. 아래 `readability-final-*` 화면은 이 APK를 실제 설치한 뒤 캡처했다. 앞선 `readability-after-*`·`readability-settings-200.png` 등은 중간 후보 화면으로 최종 APK 증거와 구분한다.

| 실제 화면 조건 | 확인한 화면 |
|---|---|
| Android 14/API34, 720×1600px / 320dpi / 글꼴 100% | 홈의 제목·복습량, 노트의 접힌 필터와 중요 표시, 복습 빈 화면, 노트 본문 |
| 같은 화면 / 글꼴 200% | 노트 본문, 필기 인용문과 여러 줄로 배치되는 동작 버튼 |
| 640×1280px / 320dpi / 글꼴 200% (320×640dp) | 문제 모드·문항 수·채점/이동 버튼, 내용 오류 창의 스크롤과 취소 |
| 1920×1200px / 240dpi / 글꼴 100% / 다크 (1280×800dp) | 노트 좌측 목차, 가운데 본문 폭, 중요 카드 |

한글 문장이 모든 기기에서 단어 단위로만 줄바꿈되는 것은 아니다. 200%의 좁은 본문에서는 단어 중간 줄바꿈이 남을 수 있다. 제목 끝 한 글자, 버튼 충돌, 수량/단위 분리를 줄이는 방향으로 확인했으며 원문·필기 범위를 바꾸는 보이지 않는 문자나 강제 개행은 넣지 않았다.

기준 화면: `evidence/readability-before-home.png`, `readability-before-notes.png`, `readability-before-review.png`. 원래 홈에서 `집계 함수와 NULL · 적용 연습`의 마지막 `습`이 별도 줄로 떨어졌고, 노트/복습에서는 첫 결과가 화면 하단까지 밀렸다.

## 수정 전후 화면

| 홈 수정 전 | 홈 수정 후 |
|---|---|
| ![이전 홈](../evidence/readability-before-home.png) | ![최종 홈](../evidence/readability-final-home.png) |

| 노트 수정 전 | 노트 수정 후 |
|---|---|
| ![이전 목록](../evidence/readability-before-notes.png) | ![최종 목록](../evidence/readability-final-notes.png) |

[최종 필기 200%](../evidence/readability-final-annotations-200.png), [작은 창 문제](../evidence/readability-final-small-session.png), [태블릿 노트](../evidence/readability-final-tablet-note-top.png)도 원본 크기로 확인할 수 있다. 코드의 이전 버전 대비 차이는 `evidence/readability-source-changes.diff`에 있다.

## 범위

41개 노트·661개 문항과 채점/기록 엔진을 보존했다. 공개 배포나 실물 기기 설치는 하지 않았다. 기존 개발 서명으로 설치 가능한 개인용 release이며 스토어용 서명이 아니다. 실제 Galaxy S24+/Tab, TalkBack 음성, 모든 글꼴/OS, 사람 대상 사용성·학습 효과 검증으로 확대 해석하지 않는다.
