# 0.8.0 — 대상·값·방향을 따라 읽는 추가 해설

2026-10-12. 현재 앱에 별도 강의 해설을 통합했다. 원본 앱 콘텐츠 및 채점 방식은 유지했다. 원본 강의 자료에 대한 포함 여부와 공식 SQLD 출제범위 전체 충족은 별개다.

## 실제 적용 범위

- 63강 전체, 기존 95예제, 자기점검 189개에 추가 읽기 안내·해설을 연결했다. FK와 INSERT 컬럼 순서의 가상 보충 예제 2개는 원본 예제와 구별한다.
- 태블릿: 왼쪽 해설·중간표, 오른쪽 원문 SQL·입력표. 작은 화면: 위아래 배치. 매우 짧은 창은 본문이 사라지지 않도록 두 열 또는 고정 높이 패널 스크롤을 사용한다.
- 목적·바뀌는 대상·전제 → 전체 SQL → 정확한 구문 강조·실제 값 중간표 → 비교 설명. ‘이 구문의 기초’와 용어·질문을 펼쳐 볼 수 있다. 자동 재생은 없다.
- 기존 27개 그림 자산을 재사용하고 그림 읽기 안내·텍스트·확대/축소를 유지했다. 연결된 40강에서 추가 해설의 읽기 준비에도 표시한다. SQL 없는 개념에 임의 SQL을 만들지 않았다.
- 자기점검은 정답 공개 전에는 읽기 출발점만 제공한다. 상세 이유는 기존 정답 공개 이후 표시한다.
- 661문항 모두 채점 후 관련 강의로 연결된다. 각 문항과 다른 입력 데이터일 수 있음을 안내한다. 기존 문항별 따라 읽기 133개·원래 풀이를 보존했다.
- 외부 AI/API/계정/Figma/Canva를 실행 조건으로 추가하지 않았다. 자유 입력 대화형 튜터는 구현하지 않았으며 문맥별 정적 질문·답변을 제공한다.

강의별 목적, 예제·확인문제 ID, PDF 페이지, 그림 연결은 [63강 연결표](lesson-guide-coverage-20261012.md)와 `evidence/explanation-upgrade-20261012/coverage.json`에 기록했다.

## 보존 및 자료 관리

- 새 저술 원본: `content/lesson-guides/<lessonId>.json`. 검증 후 `app/src/main/assets/lesson-guides`에 동기화한다. 기존 `course-pack.json`, 문항 pack, 그림, 기존 walkthrough는 수정하지 않는다.
- 각 추가 해설은 해당 원본 강의 전체 snapshot을 가진다. 원문·예제·정답·버전 등이 바뀌면 일치하지 않는 추가 해설을 열지 않는다. 기존 해설은 계속 사용할 수 있다.
- 강의 해설은 요청한 한 강의만 읽으며 최근 3개만 메모리에 유지한다. 모든 해설을 시작 시 로드하지 않는다.
- 읽던 단계는 기존 진도 map의 `guide:<exampleId>` 키로 저장한다. 원래 예제 단계·자기점검·읽음 표시와 구분한다. 단계 변경만으로 원본 예제를 완료 처리하지 않는다.
- 문제/보기/블록 ID, 제출 기록, 세션 snapshot, 타이머, ExamSpec, Room schema, 백업 v3를 유지한다. 기존 백업 v1/v2도 기존 경로로 읽는다.
- SQL 필기는 기존 문서 좌표/내용 fingerprint 저장 체계를 재사용한다. 실제 S Pen의 필압·손바닥 방지는 실물 검증을 하지 않았다.

## 저술·검증 근거

5개 원본 PDF의 텍스트, 예제에 필요한 페이지 렌더, 기존 course 원문을 대조했다. 원본 PDF와 사용자 창작 63강 예제를 동일한 자료로 취급하지 않는다. PDF를 수정하거나 전체 문항을 앱에 복제하지 않았다.

모델링 16강, SQL 기본·관리 25강, 활용·JOIN 22강으로 저술하고 다른 검토자가 교차 검토했다. 전체 구조/원문 연결 검사와 내용 검토는 서로 구분한다. 글자 수나 단계 수로 교육 품질을 인증하지 않는다.

- 원본 SQLite 모드 예제 50개를 SQLite 3.50.4에서 실제 실행해 대조했다. 입력 DDL이 없는 예제는 제공 표의 값을 담는 별도 fixture를 명시했다. 이 결과는 Oracle 호환성의 증명이 아니다.
- FK 방향·NUMBER 반올림·MERGE·ANY/ALL·NULL 등 Oracle 관련 설명은 공식 문서와 수동/Python 논리 검산을 사용한다. Oracle/SQL Server 엔진은 실행하지 않았다.
- PDF의 DEFAULT 생략 설명, 외래키의 참조 대상, 관계 필수성, LOB 크기, 서브쿼리/윈도 함수 요령 등은 필요한 조건을 별도 주의에 기재했다. 원문은 몰래 수정하지 않았다.
- 교차 검토에서 수정한 문제: SQLite에 그대로 적용될 것처럼 보인 VALUES(DEFAULT) 설명, 문자별로 분리된 강조 목록, 숫자와 단어의 불필요한 붙임.

자세한 저술·독립검토 결과는 `evidence/explanation-upgrade-20261012/*review.json`에 있다. 이 기록은 사람 전문가 검수나 학습효과 평가가 아니다.

## 검사 결과

2026-10-12 최종 소스와 자산으로 실행했다. 아래 기기 검사는 Android API 34 `SQLNote_QA` 에뮬레이터의 결과다.

| 검사 | 실제 결과 | 근거 |
|---|---|---|
| 단위 테스트 | 93 통과, 실패·오류·건너뜀 0 | `evidence/jvm-results/TEST-*.xml` |
| 태블릿 전체 기기 테스트 | 87/87 통과 | `tablet-final-instrumentation.log` |
| 휴대폰 360×800dp·글씨 150% | 강의 해설/기존 SQL 해설 14/14 통과 | `phone-final-instrumentation.log` |
| 짧은 가로 창 640×360dp | MERGE 코드 가시성·이전/다음 1/1 통과 | `short-landscape-instrumentation.log` |
| debug/release 빌드 및 lint | 성공, lint 각 0 오류·8 경고 | `verified-build.log`, `evidence/lint-results-*.xml` |
| 콘텐츠·추가 해설·APK 자산 | 63강·95예제·189확인문제 연결, 원본 저술 파일 208개 변경 없음, 앱 자산과 원본 일치 | `validation.json`, `apk-validation.json` |
| 기존 기록 보존 | 갱신 전 백업과 최종 기기 테스트 후 DB의 모든 필드 동일 | `update-preservation.json` |
| 최종 릴리스 기록 보존 | 0.8.0 release 설치 후 앱에서 다시 내보낸 백업도 갱신 전과 모든 필드 동일 | `release-record-preservation.json` |
| 릴리스 서명 | 기존 개발 서명으로 검증 성공 | `release-signature.log` |

이 표의 짧은 파일명은 `evidence/explanation-upgrade-20261012/` 기준이다. 보존 검사에는 세션 5개, 제출 55개, 별표 1개, 텍스트 필기 2개, 노트 진도 4개, 강의 진도 5개가 포함된다. 기존 실제 기록에 SQL 필기 문서는 0개여서, SQL 필기 보존은 별도 합성 데이터의 백업·복원/화면 테스트 근거와 구분한다.

초기 태블릿 검사에서 4개 실패를 확인한 뒤 원인별로 수정했다. 노트 상세를 접을 때 스크롤 최대값이 줄어 펼친 위치까지 잃는 실제 문제는 펼침/접힘 위치를 분리해 해결했다. 나머지는 모달 뒤의 같은 버튼까지 찾던 테스트 선택자와 짧은 검색 결과에도 스크롤을 요구하던 검사 전제였다. 초기 로그 `tablet-all-instrumentation.log`도 보존한다. SQL 표의 컬럼명이 한 글자씩 끊기는 문제는 실제 글자 크기를 측정해 컬럼 최소 폭을 정하도록 수정했다.

릴리스 APK는 18,563,216 bytes이고, 이전 0.7.0의 18,176,370 bytes보다 386,846 bytes 증가했다. 추가 해설 JSON은 합계 1,369,821 bytes다. 요청한 한 강의만 로드하는 구조와 3강 캐시를 검사했지만, 실행 속도나 메모리 절약량의 실측 벤치마크는 하지 않았다.

실제 릴리스 화면은 `guide-final-release-*.png`, 최종 디버그 APK의 격리된 테스트 화면은 `guide-pilot-*.png`, `guide-phone-*.png`, `guide-final-short-landscape.png`로 구분한다. 릴리스 화면은 새 QA 사용자에서 촬영해 기존 사용자 기록과 섞지 않았다.

릴리스 설치 후 홈·검색·강의 해설·MERGE 단계 이동·그림 확대·기록 내보내기를 실제 UI로 확인했다. 촬영용 사용자 11은 제거하고 기존 사용자 0·10을 보존했으며, 화면 크기·글씨·애니메이션 설정을 작업 전 값으로 복구했다. [MERGE 실제 화면](../evidence/explanation-upgrade-20261012/guide-final-release-merge.png), [그림 실제 화면](../evidence/explanation-upgrade-20261012/guide-final-release-image.png), `qa-summary.json`과 `release-install-summary.json`에 최종 근거를 남겼다.

## 실행 및 갱신

```powershell
$env:ANDROID_HOME='C:\Android\Sdk'
python scripts/validate_content.py
python scripts/validate_course.py
python scripts/validate_walkthroughs.py
python scripts/validate_lesson_guides.py --sync
python scripts/report_lesson_guides.py
./scripts/build.ps1 -Tasks assembleDebug,assembleRelease,assembleDebugAndroidTest,testDebugUnitTest,lintDebug,lintRelease -Offline
python scripts/package_artifacts.py --build-type release
```

위 SDK 경로는 이 작업 환경의 기존 설치 위치다. 다른 환경은 자신의 SDK 경로를 지정한다. 새 강의 해설을 수정했다면 source와 assets를 따로 편집하지 말고 validator의 `--sync`를 사용한다. 예전 `src/build_content.py`로 원본을 다시 만들지 않는다.

설치 파일은 `dist/SQL-note-0.8.0-release.apk`, 전체 코드/콘텐츠는 `dist/SQL-note-0.8.0-source.zip`이다. 기존 개발 서명을 유지하며 공개 스토어 출시 인증을 뜻하지 않는다. 기기에서는 기존 앱 위에 업데이트한다. 서명이 다르면 앱을 지워서 해결하지 말고 기존 기록을 먼저 내보낸다.

## 되돌리기

- 변경 전 source backup: `backups/explanation-upgrade-20261012/source-before.zip`, 파일별 checksum: 같은 폴더 `hashes.json`.
- 기존 앱에서 내보낸 실제 기록은 `private_evidence/guide-before-20261012.json`에 보관했다. 개인 기록은 APK·배포 ZIP에서 제외한다.
- 코드 복구는 backup을 별도 빈 폴더에 풀어 비교하고 필요한 파일을 되돌린다. 현재 작업 폴더 위에 무조건 덮어쓰거나 사용자 DB를 삭제하지 않는다. 새 `LessonGuide*` 파일과 연결 호출을 함께 되돌려야 한다.
- 기기의 앱을 단순 제거하면 데이터가 사라진다. 앱 코드만 되돌릴 때는 같은 서명과 더 높은 versionCode로 복구 빌드를 만든다. 기록 복원은 앱의 검사→미리보기→복구 지점 저장→원자적 교체 절차를 사용한다.

## 남은 범위

원본 PDF 전체 개별 문항의 추가 풀이, 기존 661문항 모두의 새 전용 단계 해설, 자유 입력 대화형 튜터, Oracle/SQL Server 실행, 실제 Galaxy Tab/S Pen, 사람 전문가 검수·처음 보는 문제로의 전이 평가, 현행 공식 SQLD 출제범위 전체 충족은 이번 작업에서 완료하지 않았다. 기존 SQL 217문항 중 전용 따라 읽기 적용 133개/미적용 84개 구분을 유지한다. 내용 추가와 합격 가능성 보장은 다르다.
