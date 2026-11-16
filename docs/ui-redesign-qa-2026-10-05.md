# SQL 노트 0.6.0 디자인 변경 QA

전용 SQLNote_QA 에뮬레이터(emulator-5590)에서 새 홈·계획·테마·탐색 화면을 검사했다. 휴대폰 26개와 태블릿 7개 UI 실행이 통과했다. 이후 200% 글씨에서 접기 화살표가 눌리는 현상을 수정하고 계획 테스트 4개를 두 화면 크기에서 다시 통과했다. 최종 릴리스 설치와 백업 비교도 완료했다.

## 최종 빌드

- 버전 0.6.0 / versionCode 11 / 17,728,145바이트.
- 릴리스 APK와 실제 설치된 base.apk SHA-256: `819a35968a033c195f8effe82394b05b3af0ed2b103a45eea5ac1f011de3641f`.
- 기존 앱에 install -r로 업데이트했다. 삭제·초기화·복원은 하지 않았다.
- APK v2 서명 검증 성공. 기존 개인 배포 인증서 SHA-256은 `7d8bc4994c76b95c3dccfd482178c7b9a1de28131924d1891fd6075a7a9ed317`이다.
- 콘텐츠 4개(content-pack/course-pack/course-visuals/study-plan)는 0.5.0 baseline, 현재 source, 최종 APK assets가 모두 일치했다. [콘텐츠 비교](../evidence/ui-redesign-20261005/final-content-preservation.json)

## 실행 검사

| 실행 묶음 | 결과 | 로그 |
|---|---|---|
| 최종 빌드 JVM 단위 테스트 | 76/76 통과, 실패·오류·건너뜀 0 | [JVM 결과](../evidence/ui-redesign-20261005/jvm-test-summary.json), [빌드 로그](../evidence/ui-redesign-20261005/build.log) |
| 아이콘 수정 전 휴대폰: Plan4, Navigation2, Learning9, Course3, Usability7, AnnotationTheme1 | 26/26 통과, 118.746초 | [phone](../evidence/ui-redesign-20261005/phone-instrumentation.log) |
| 아이콘 수정 전 태블릿: Sidebar3, Plan4 | 7/7 통과, 43.561초 | [tablet](../evidence/ui-redesign-20261005/tablet-instrumentation.log) |
| 최종 수정 후 휴대폰 Plan 재검사 | 4/4 통과, 27.768초 | [final phone](../evidence/ui-redesign-20261005/final-phone-plan-instrumentation.log) |
| 최종 수정 후 태블릿 Plan 재검사 | 4/4 통과, 27.704초 | [final tablet](../evidence/ui-redesign-20261005/final-tablet-plan-instrumentation.log) |

반복 실행을 서로 다른 UI 검사 41개로 합산하지 않았다. UI 테스트는 in-memory Room과 projectPreferences=false를 사용하며 테마 테스트는 별도 ComponentActivity를 사용한다. 개인 학습 DB에 테스트 답안이나 제출을 추가하지 않는다. 최종 debug·release·AndroidTest APK 빌드가 성공했고, 콘텐츠 구조 검증도 통과했다. 이 구조 검증은 실제 DBMS 실행이나 전체 교재의 의미 검수를 대신하지 않는다.

날짜·시간 선택, 화면 복귀, 접기·펼치기, 일반 연습·강의 연결, 실전 전환 안내·취소, 답안 초안·제출 구분, 기존 제출 보존, 검색·복습 필터, 자기점검 입력, 태블릿 목록 상태 복원, 테마 변경 시 형광펜 보존을 검사했다.

## 실제 화면

| 환경 | 확인 결과 | 캡처 |
|---|---|---|
| 휴대폰 720×1600px / 320dpi, 360×800dp | 계획·이어보기 버튼과 한글 제목·본문이 읽힘 | [최종 홈](../evidence/ui-redesign-20261005/ui-phone-home.png) |
| 태블릿 2560×1600px / 320dpi, 1280×800dp | 홈·계획의 2열 배치와 탐색 표시 정상 | [최종 홈](../evidence/ui-redesign-20261005/ui-tablet-home.png), [최종 계획](../evidence/ui-redesign-20261005/ui-tablet-plan.png) |
| 640×1280px / 320dpi, 글씨 200% | 버튼 여러 줄 배치·스크롤 가능. 화살표 전체 표시와 실제 펼치기 확인 | [수정 전](../evidence/ui-redesign-20261005/before-font200-plan.png), [최종](../evidence/ui-redesign-20261005/ui-font200-plan.png), [펼침](../evidence/ui-redesign-20261005/ui-font200-overview-open.png) |
| 태블릿 너비, 글씨 200% | 홈이 1열로 전환 | [큰 글씨 홈](../evidence/ui-redesign-20261005/ui-tablet-font200-home.png) |
| 시스템 다크모드 | 홈·계획의 글자와 선택 상태 구분 | [홈](../evidence/ui-redesign-20261005/ui-phone-dark-home.png), [계획](../evidence/ui-redesign-20261005/ui-phone-dark-plan.png) |
| SQL 읽기 | 키워드·한글·SQL 줄바꿈 확인. 결과 공개·읽음 표시·제출은 누르지 않음 | [SQL](../evidence/ui-redesign-20261005/ui-phone-sql.png), [다크 SQL](../evidence/ui-redesign-20261005/ui-phone-dark-sql.png) |

태블릿에서 선택한 10/6·6시간 상태가 휴대폰 너비 변경, 테마 변경, 홈 왕복 후에도 유지됐다. 근거는 ui-tablet-plan-selected.png, ui-phone-plan-after-resize.png, ui-phone-dark-plan.png이다. 최초 33개 실행과 다크·SQL·너비 변경 캡처는 아이콘 수정 전 빌드의 증거다. 최종 빌드에서는 위 표의 최종 홈·계획·큰 글씨 개요 캡처를 새로 생성하고 영향 테스트만 다시 실행했다.

확인한 화면에서 작은 한글 깨짐이나 본문·버튼 겹침으로 인한 조작 장애는 발견하지 않았다. 200%에서는 아래 내용에 스크롤이 필요하다. 좁은 홈 제목의 둘째 줄이 ‘· ERD’로 시작하고 태블릿 날짜 버튼 내부 여백이 넓은 점은 작은 마감 사항이다. 가로 표의 일부 열은 기존 가로 스크롤 영역에 속한다. 200% 하단 탐색은 아이콘 중심이며 접근성 설명이 있지만 실제 TalkBack 음성 검사는 하지 않았다.

선택한 10개 불투명 글자·배경 색상쌍의 계산 대비비는 5.06~13.35였다. 전체 앱 접근성 인증은 아니다. [색상 비교](../evidence/ui-redesign-20261005/static-color-contrast.json)

## 기록 보존

시작 화면과 새 로컬 UI export 백업을 확보했으며 시작 백업은 이전 0.5.0 최종 백업과 정확히 일치했다. 원시 private-*-backup.json은 로컬에만 보관하고 배포 ZIP에서 제외한다. 비교 결과에는 개인 답안·메모 본문을 넣지 않았다.

- 0.5.0 baseline부터 초기 UI/테마 검사 완료·SQL 열람 전까지 payload 완전 일치. [비교](../evidence/ui-redesign-20261005/before-vs-pre-sql-state-comparison.json)
- SQL 캡처를 위해 기존 강의 2-1-20을 열어 해당 탭, 스크롤 1340→1356, 갱신 시각 및 revision 607→612만 변경됐다. 예제 단계·읽음 여부·자기점검·제출은 유지됐다. [전체 전후 비교](../evidence/ui-redesign-20261005/before-vs-final-state-comparison.json)
- SQL 캡처 후부터 최종 수정 빌드 설치·검사 완료까지 payload는 `a0c57a321a1e418deebb4dd5d3ae9e343c524ddc129dd9fff193288c4a75f7d8`로 완전 일치. [최종 업데이트 비교](../evidence/ui-redesign-20261005/final-update-state-comparison.json)
- 제출55·세션5·필기2·강의진도5가 유지됐다. 세션·답안·필기·별표·메모·복습·노출·설정은 변하지 않았다. 정상적인 읽기 위치 변화를 숨기거나 복원으로 되돌리지 않았다.
- 화면을 시작 값 720×1600px / 320dpi / 글씨1.0 / 야간 no로 복구하고 오늘 화면에 두었다. [설치·환경](../evidence/ui-redesign-20261005/final-installed-environment.json)

이번 결과는 전용 에뮬레이터와 명시한 검사에 한정된다. 실제 Galaxy 기기, 모든 화면 조합, 모든 콘텐츠 정확성이나 학습 효과 검증으로 확대하지 않는다. [기계 판독 결과](../evidence/ui-redesign-20261005/qa-summary.json)
