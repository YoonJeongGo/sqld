# SQL 노트 0.6.1 기능 QA 실행 결과

현재 집계: 최종 Android 전체64 PASS, 폰320dp/200% 고유12개는 실패 원인 진단과 영향2개 재실행을 거쳐 모두 PASS. 최종 release 재실행과 원래 user0 전체 기록 동일성도 확인했다. 최종 판정은 FINAL_PRODUCT_GATE.md 참조.

## 환경과 데이터 격리
Windows PowerShell, 기존 scripts/build.ps1 / 오프라인 Gradle, SQLNote_QA API34 에뮬레이터 emulator-5590. Android user0의 기존55제출/5세션은 UI 백업으로 보존하고 user10에 실제 사용 경로용 별도기록을 만들었다. 자동검사는 in-memory 또는 고유 이름 Room DB와 분리설정을 사용한다. 물리 Galaxy 증거가 아니다.

## 자동 검사
| 항목 | 결과 | 직접 근거 |
|---|---|---|
| JVM | PASS 78/78 (기존76 + 계획순환2) | final-unit-summary.json, final-unit/*.xml |
| Python 검증기 | PASS 63/63 | baseline-python-tests.log, exit0 |
| 콘텐츠·강의·그림 구조 | PASS / 내용정확성전수검수와 별도 | validate_content.py --strict / validate_course.py / validate_visuals.py exit0 |
| Debug/Release/AndroidTest build | PASS | iteration-1-build-recheck.log, exit0 |
| Debug/Release lint | PASS 오류0·기존경고4 | app/build/reports/lint-results-*.txt |
| Android 전체 최종 | PASS 64/64, 실패0·skip0, 99.895초 | runtime/final-all64-instrumentation.log |
| Android 320dp/200% | 고유12 PASS(후속 재실행 포함) | 최초11 PASS/1 FAIL, 영향2 최종 PASS(11.863초). 전체64와 중복되는 별도환경 검사 |
| 초기 신규8 | 7 PASS / 1 테스트선택자 FAIL | final-new8-instrumentation.log. 배경별표와 신고체크 모호성; 대상범위보정 후 재실행 |
| 테스트APK 보정 빌드 | PASS | iteration-2-test-build-final.log, exit0 |

초기 신규8의 1실패는 배경 별표까지 선택한 잘못된 검사 선택자였다. 별도 폰검사의 실패는 저장완료 Snackbar가 자동검사의 터치 중심을 덮은 것이었다. memo-nav-before-click/after-click PNG와 semantics로 진단한 뒤 안내가 자연 종료될 때까지 기다려 실제 터치를 검증했다. 최초 실패 로그를 삭제하거나 PASS로 바꾸지 않는다. 전체64는 반복2 시점, 최종 폰2는 반복4 시점의 실행이며 앱 코드는 같다.

## 출시판 실제 클릭 결과
| 기능 | 실제 실행과 판정 | 근거 |
|---|---|---|
| 계획 5/6시간·접기·연습 | 실제 범위 연습 시작. 두10문항 세트 중복0. PASS | release-selection-grading-evidence.json |
| 검색→강의→뒤로 | ANSI 검색 결과 표시, 강의 열림, 검색어 유지. PASS | release-061-search 관련 캡처/실행 기록 |
| 메모 수정/회전/취소 | 실제 화면 회전 후 초안 유지, 저장·명시취소 정상. PASS | release-061-memo-* |
| 보기 선택/이전/다음/채점 | 선택만으로 채점 안 됨. 연속 채점은1개 기록. 전체제출10문항: 정답1/오답1/미응답8. PASS | release-selection-grading-evidence.json |
| 별표/오답 복습 | 실제 저장 후 복습 목록으로 연결. PASS | release QA 기록 요약 |
| 설정 | 학습량0 거절→5 저장, 테마·SQL줄바꿈 저장값 확인. PASS | release-061-invalid-settings.png, release-qa-record-summary.json |
| 작은 화면·큰 글씨 | 320dp/200%에서 메모 수정·저장버튼 실제 사용. PASS(대표동작) | release-061-320dp-font200-memo.png |
| 실제 소프트키보드 | 320dp/200% 메모 입력창에서 실제 IME 열림, 저장·취소 버튼 모두 키보드 위에 표시. PASS(대표동작) | release-061-320dp-font200-real-ime-memo.png, environment.json |
| 그림 | 태블릿에서 열기→화면맞춤→닫기. PASS | release-061-diagram-viewer.png |
| 백업 검사/취소 | 손상 checksum파일 거절, 정상 미리보기 후 취소. PASS | runtime 캡처·파일선택 실행 |
| 백업 교체/복구점 | user10에서 11→1제출로 실제 교체 후 복구점으로1→11 복귀. PASS(실행), 전체필드 비교는 최종요약 참조 | runtime 비교자료 |
| 오프라인 | 실제 화면에 비행기모드, 앱 네트워크권한 없음. 로컬 핵심흐름 사용. PASS | Manifest, 실제 캡처 |

## 보존과 변경 범위
content-preservation.json: 콘텐츠/자산/스키마/채점·저장·테마·강의 등 보호139파일 SHA256 동일. 강의63/예제95/자기점검189/그림27/채점문항661, ID 및 원본 데이터를 변경하지 않았다. 0.6.0→0.6.1 user10 rich payload 동일. baseline debug force-stop/restart에서도 payload 전체 동일.

최종 release 확정 비교:
- 원래 user0: 최초 백업과 전체 payload 문자열·SHA256 동일, 변경 필드0. 제출55/세션5/메모2/강의진도5 유지. 실제 UI 내보내기 근거 `runtime/final-user0-preservation.json`. 원래 사용자에 QA 제출·복원·초기화 없음.
- QA user10: 최종 release 덮어 설치→강제중지→재실행→UI 내보내기 뒤 전체 payload 동일. 제출11/세션4/메모1/강의진도2 유지. `runtime/final-user10-preservation.json`.
- release 복원→복구점 복귀: 학습 자료 전체 일치, 작업 revision만69→71. `runtime/release-restore-recovery-comparison.json`.
- 검증한 release SHA256: `042efaa51fdb19b9044187f2343d124671ec67e696d426700f94ab481678b9c5`. 최종 테스트APK 해시는 `final-apk-summary.json`, candidate 파일은 이전 시점 스냅샷이다.

## 판단 범위
버튼 handler만 읽은 경우와 실제 실행/자동 검사를 구별했다. 모든 수록문항의 정답, 모든 기기조합, 실제 사용자 학습효과를 통과시킨 것은 아니다. PDF·영상은 범위 안내이며 앱 내부 뷰어/플레이어가 아니다. SQL 예제는 정적 단계 해설이다. 미검증/남은 P2는 REMAINING_PRODUCT_RISKS.md 참조.

전체64에는 신규8이 포함된다. 별도 신규8 재시도/기준선56과 합산해 고유검사 수를 늘리지 않는다. FT-01/AR-02의 실제 실패 주입→복구, AR-03 저장중 상태재생성, generation guard가 최종 전체 실행에서 통과했다. 확인된 핵심P1 두 건은 이 근거로 해결 처리한다.
