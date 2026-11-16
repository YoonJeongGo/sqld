# 기능 수정 보고 — SQL 노트 0.6.1 / code12

Canva 기반 현재 디자인을 유지한 기능 QA 수정이다. 모의고사/채점 엔진, Room 테이블, 백업 v2 형식, 콘텐츠와 질문/보기/강의 ID는 변경하지 않았다.

| 문제 | 이전 동작 | 수정 후 동작 | 관련 파일 |
|---|---|---|---|
| PV-01 · P2 | 계획범위48문항에서 기본10문항을 다시 시작해도 앞10 고정 | 같은범위에서 덜 본 문제 우선, 동률은 오래전에 본 문제·기존순서 | StudyPlan.kt, PlanScreens.kt |
| FT-01 · P1 장애 시 | 초기 자료 읽기 실패 후 앱 안에서 재시도 불가 | 다시 열기, 중복 초기화 방지, 기록 유지 | StudyViewModel.kt, MainActivity.kt |
| FT-02 · P2 | 강의만 검색되면 결과 있음+없음이 동시에 표시 | 강의 포함 개수, 실제 전체0일 때만 빈 안내 | LearningScreens.kt |
| AR-02 · P1 | 메모·오류표시 저장 완료 전 창 닫힘, 실패 시 초안 폐기 | 성공 후 닫힘, 오류 뒤 입력 보존과 재시도 | MainActivity.kt, LibraryScreens.kt |
| AR-03 · P2 | 회전/상태재생성 때 미저장 입력 폐기 | 대상·입력·제외 선택 복원, 저장중 재생성 시 안정 ID로 중복 방지 | MainActivity.kt, LibraryScreens.kt |
| BUILD-01 · P2 | Unicode SDK경로 lint 오진으로 실패 | 해당 생성파일의 해당 검사만 한정 예외, 실제 SDK컴파일 통과 | app/lint.xml |

자동 회귀: 계획 문항 전체 순환/노출종류/정렬동률 단위2개, 최초오류/검색/초안저장실패/상태재생성/저장중재생성/복원이후오래된초안/문항제외 등 Android8개. 개수만으로 품질을 증명하지 않으며 실제 실행 결과는 AFTER 참조.

## 사용·실행
개인용 APK: dist/SQL-note-0.6.1-release.apk. 기존 앱을 제거하지 않고 같은 서명으로 덮어 설치한다. 앱 설정→전체 기록 내보내기를 먼저 사용할 수 있다.

개발 검증: `scripts/build.ps1 -Tasks testDebugUnitTest,assembleDebug,assembleDebugAndroidTest,assembleRelease,lintDebug,lintRelease -Offline`; 콘텐츠 구조: `python scripts/validate_content.py --strict`, `python scripts/validate_course.py`, `python scripts/validate_visuals.py`. Python검증기: `python -m unittest discover -s scripts -p "test_*.py"`.

## 되돌리기
소스: `backups/product-functional-qa-before-20261005.zip`과 source-before.json으로 변경파일을 비교해 필요한 파일만 복구한다. 현재 앱/자료 위에 ZIP 전체를 무조건 덮어쓰지 않는다. 새보고서/새테스트/app/lint.xml은 이 작업에서 추가된 파일이다.

앱: 이전 0.6.0 APK와 source ZIP은 dist에 보존했다. Android 버전 다운그레이드는 기본 차단될 수 있으므로 학습기록을 지우거나 uninstall하지 않는다. 코드만 되돌릴 필요가 있으면 이전 소스를 더 높은 versionCode로 빌드해 같은서명 업데이트하고 먼저 QA 사용자에서 확인한다. DB/백업 형식은 그대로이지만 다운그레이드 설치 자체는 테스트하지 않았다.

기록: 손상/미래형식 검증→미리보기→로컬 복구점→원자적 교체 기능을 사용한다. 검증용 원래 user0의 private 백업은 프로젝트 evidence/runtime에 로컬로 보존하며 배포ZIP에 넣지 않는다.
