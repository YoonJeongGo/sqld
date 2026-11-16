# 기능 QA 반복 기록

## 기준선 (수정 전)
0.6.0/code11, 소스 238파일 ZIP+SHA 보존, 기존 user0 UI 전체 백업. 새 Android user10에 같은 release를 install-existing해 데이터를 격리했다. JVM76/76, Python63/63, Android56/56 PASS. Debug/AndroidTest/Release 빌드 PASS. lint는 valid Unicode escape 오진으로 FAIL(1오류/4경고). 실제 release에서 선택/개별채점 2회 탭 후 제출은1개였다. baseline debug rich 백업은 force-stop/재실행 후 payload 전체 동일. 손상파일 거절과 정상 미리보기 취소 확인.

6개 감사 역할은 실제 에이전트 3명이 순차 담당했다. 별도 6명이나 실제 사용자 조사로 포장하지 않는다. 정적 발견을 root가 판정하고 root 한 명만 소스 수정했다.

## 반복 1 — 기능 수정 및 회귀 검사
- PV-01(통합 RU-03): 계획범위 앞N 고정 문제를 seen 횟수/마지막 노출시각으로 순환. 이는 제출완료와 다른 '본 문제' 정책이다. 일반 복습 정렬과 저장된 세션은 유지.
- FT-01: 자료 초기화 오류 후 단일 작업 재시도, 데이터 초기화 금지, 타이머 중복 생성 방지.
- FT-02: 강의 검색 결과 포함 개수/빈 상태 판정.
- AR-02/AR-03: 신규/수정 메모와 내용 오류 입력을 성공 후 닫기, 실패 시 초안 유지, saved-instance 복원. 안정 ID/트랜잭션 내 복원 generation 검사/저장 중 입력·취소 잠금. 회전 뒤에도 commit된 상태를 관찰해 창 닫기.
- BUILD-01: app/lint.xml에서 생성 local.properties에 한해 PropertyEscape 오탐 제외. 다른 파일/검사는 켜 둠. SDK 경로를 변형하지 않고 두 변형 빌드로 확인.

첫 빌드의 Layout 상수 치환은 최신 SDK WrongConstant lint 오류를 일으켰다. 기존 동작을 그대로 되돌리고 재실행했으며 앱 코드의 UiComponents.kt는 원본 바이트로 복원했다. 경고를 없애기 위해 API 지원/디자인을 임의 변경하지 않았다. 이 실패도 iteration-1-build.log에 보존한다.

실행: iteration-1-build-recheck.log exit0, JVM78/78, Debug/AndroidTest/Release 및 Debug/Release lint PASS. 남은 lint 경고4개는 이전 API 상수2, target35 안내1, Uri KTX 제안1. 새 Android 회귀8개를 위한 별도 테스트APK build도 exit0.

최종 Android/Release 재검증과 종료 판정은 PRODUCT_QA_AFTER.md, FINAL_PRODUCT_GATE.md에 기록한다. 최대5회 제한 안에서 불필요한 P3 수정·기능 확대를 하지 않는다.

## 반복 2 — 테스트 대상 범위 보정
신규 Android8은 최초7 PASS/1 FAIL. 실패는 신고 대화상자의 체크박스 선택자가 배경 별표까지 함께 찾는 모호성(FunctionalRecoveryUiTest:201)이었다. 앱 저장 오류로 집계하지 않는다. 해당 테스트 선택자를 대화상자 내부로 제한하고 같은 검증을 재실행한다. 앱 코드/APK는 변경하지 않는다. 로그 final-new8-instrumentation.log를 보존한다.

반복2 결과: final-all64-instrumentation.log 64/64 PASS, 99.895초, 실패0/skip0. 테스트대상 보정으로 기존 결함검사를 우회하지 않았고 전체 회귀를 다시 확인했다.

## 반복 3 — 200% 화면의 테스트 스크롤 보정
폰320dp/200% 12개 중11 PASS/1 FAIL. 메모 편집 항목의 LazyColumn 탐색 문제를 의심해 필기목록 스크롤을 보정했다. 그러나 영향2개 재실행은 1 PASS/1 FAIL로 같은 테스트가 다시 실패했다. 첫 가설만으로 원인이 해결되지 않았으므로 좁은 화면 전체 통과로 처리하지 않는다. 같은 환경의 실제 release 메모 수정/저장은 통과했지만 자동 검사의 실패 원인은 별도 확인한다. 앱 코드는 변경하지 않았다. 최초 실패와 재실행을 final-phone320-font200-12-instrumentation.log, final-phone320-font200-memo2-rerun.log에 유지한다.

## 반복 4 — 실제 실패 화면으로 탐색 경로 진단
실패 테스트에서 설정의 필기목록 버튼을 누르기 전/후 및 실패 시점의 화면과 semantics를 확보했다. 설정 행의 병합된 터치 중심(y1152)을 저장 완료 Snackbar(y1145~1320)가 덮어 다음 화면으로 이동하지 않았음이 확인됐다. 제목은 보였지만 테스트는 그 제목만의 좌표가 아닌 병합 행 중앙을 눌렀다. 이는 메모 저장 실패나 편집 기능 미구현이 아니었다.

검사는 안내의 자연 종료를 기다린 후 스크롤·실제 터치하고 목적 화면 제목을 확인한다. 상태를 직접 지우거나 내비게이션 함수를 호출하지 않는다. 실패 시 화면을 남기는 장치도 유지한다. 영향2개 최종 재실행 모두 PASS(11.863초, final-phone320-font200-memo2-final.log). 폰320dp/200%의 고유12개는 최초11 PASS + 실패1 최종 PASS이며, 재실행2 중1은 중복 검증이다. 앱 코드/APK는 반복1 이후 동일하다.

종료: 개선 반복4회/상한5회. 임의 점수 상향을 위해 P2 정책·기능을 추가하지 않는다. 실패 로그와 진단 PNG/txt를 보존한다.
