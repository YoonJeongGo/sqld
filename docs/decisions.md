# 결정 기록 (2026-09-14)

## 구현 환경과 버전
- 신규 폴더에서 시작. 기존 소스/데이터 없음을 확인했으며 Git 최초 커밋·원격 저장소·공개 배포를 만들지 않았다.
- Kotlin 2.0.21, Compose compiler 2.0.21, AGP 8.13.1, Gradle 8.13 (wrapper SHA-256 고정), Compose UI/Foundation 1.7.6, Material3 1.3.1, Room 2.6.1, DataStore 1.1.7. 프리뷰를 사용하지 않고 재현 가능한 안정 버전을 택했다. 로컬 캐시와 공개 Maven 의존성으로 실제 빌드 호환성을 확인한다.
- 공식 Compose Kotlin 문서 https://developer.android.com/jetpack/androidx/releases/compose-kotlin (2026-09-14 열기 성공): Kotlin 2.0+는 같은 버전 Compose compiler plugin 사용.
- Room https://developer.android.com/jetpack/androidx/releases/room / Material3 https://developer.android.com/jetpack/androidx/releases/compose-material3 / DataStore https://developer.android.com/jetpack/androidx/releases/datastore 실제 열기 성공. 최신 안정판이 별도로 있지만 최신이라는 이유만으로 업그레이드하지 않았다. API 호환성과 빌드 결과로 선택을 검증한다.
- AGP 8.13 release archive 직접 조회 실패. 로컬 AGP artifact와 빌드 결과가 호환성 증거이며 공식 AGP 페이지 최신 원문 확인으로 과장하지 않는다.
- 개발 JDK: Android Studio 번들 OpenJDK 21.0.10. Java/Kotlin bytecode target17. compileSdk36 / targetSdk35 / minSdk26. 주 환경 S24+/Tab을 고려하되 특정 기기명으로 레이아웃을 분기하지 않는다.
- 실행: Android API34 x86_64 에뮬레이터. 실제 Galaxy 기기는 연결되지 않았다. 실기기·TalkBack·외부 키보드 검증을 자동 주장하지 않는다.
- 최종 빌드/lint와 전용 AVD는 설치된 ASCII 경로 `C:\Android\Sdk`를 사용했다. 한글 경로 SDK로도 APK 빌드는 성공했으나 Java Unicode escape를 lint가 잘못 판정하는 문제가 있어 이 경로를 사용했다. `scripts/build.ps1`은 ANDROID_HOME/ANDROID_SDK_ROOT를 우선한다. 런타임 AVD는 workspace의 SQLNote_QA이며 초기 기존 에뮬레이터 사용과 복구 경계는 QA.md에 기록했다.

## 데이터와 상태
- 콘텐츠는 JSON 버전 팩, 개인 기록은 Room DB. 화면에 정답을 하드코딩하지 않는다.
- 단일 개인 앱의 구조를 단순하게 유지하기 위해 전체 개인 상태를 JSON snapshot으로 저장하고, 제출 테이블에 `(sessionId, questionId)` UNIQUE 제약을 추가한다. 채점/시도/복습은 Room 트랜잭션으로 한 번에 저장한다. 원본 첫 제출을 수정하지 않는다.
- 순수 `StudyEngine`이 상태 전이를 처리하고 UI는 DB commit 후 상태를 반영한다. DB 오류 시 이전 상태를 표시하고 오류를 안내한다. 제출 중복은 domain guard와 DB unique 양쪽으로 방어한다.
- 데이터 보존을 위해 destructive migration을 사용하지 않는다. 현재 schema1이므로 과거 배포 버전에서 실제 업그레이드한 Room migration 증거는 아직 존재하지 않는다. Content pack 교체 시 세션의 원문 snapshot/choice order/ExamSpec을 유지한다.
- Room snapshot에 설정까지 포함하여 복원이 원자적이다. DataStore는 표시 설정의 파생 캐시이며 Room이 정본이다. 캐시 쓰기 실패로 정본 기록을 되돌리지 않으며 다음 시작 때 재구축한다.
- 전체 JSON snapshot은 개인 사용 규모에서 단순하고 복구하기 쉽다. 장기 수만 회 시도에 대한 성능은 측정 전이며, 기록 수가 많아지면 정규화 DB를 추가해야 할 수 있다. 숫자를 지어내지 않는다.
- 필기는 noteId/blockId/quote로 연결한다. blockId 일치+인용 포함을 우선하고 같은 노트 내 인용 재탐색을 시도한다. 실패해도 archived 보관함에 남긴다. 동일한 문장의 여러 발생 위치는 v1에서 첫 일치에 강조된다.
- 문장 선택은 Android TextView 기본 선택 툴바를 확장하여 형광펜·밑줄·메모를 제공한다. 실제 텍스트이며 OS 선택/복사를 지원한다.

## 시험과 노출
- ExamSpec은 사용자 초안과 출판사 교차 확인 기준이다. DataQ 공식 최신 원문은 접근 실패. 앱과 보고서에 provisional 상태를 유지한다.
- 연습 답안 터치는 초안이며 채점 버튼만 제출한다. '모르겠어요'는 명시적 미응답이다. 개별 채점된 항목을 전체 제출에서 건너뛴다.
- 0.11.0부터 strict 화면은 개별 채점·모르겠어요를 숨기고 이전·다음·전체 제출만 하단에 표시한다. 노트 도움은 확인 후 mixed로 영구 전환하며 제출 도움 표기·순수 진단 제외를 복원 후에도 유지한다. 기존 엔진의 전환 가드는 하위 호환을 위해 보존하고 일반 연습의 개별 채점은 유지한다.
- 예약 문제는 일반 search/practice/filter 경로에서 제외한다. 세트 시작 전에 기존 family 노출을 검사하고 응시 시작을 영구 기록한다. 모든 세트는 실제 모델10/SQL40 조건이 맞아야 열린다.
- 모의고사는 monotonic elapsedRealtime과 BOOT_COUNT를 사용한다. 같은 부팅에서는 monotonic와 wall 진행 중 큰 값을 차감해 시계 조작으로 시간을 늘리지 않는다. 재부팅 후 wall 경과로 남은 시간을 줄인다. 2초를 넘는 역행 또는 같은 부팅에서 2분 넘는 clock drift는 즉시 제출하고 진단 제외한다. 변경이 재부팅 중 일어나 기준 시각보다 여전히 미래라면 완전 감지할 수 없는 오프라인 한계가 있다.
- 프로세스가 살아 있으면 5초마다 타이머 상태를 저장하고 UI는 1초 단위로 표시한다. 프로세스가 종료돼도 저장된 시각 기준으로 재실행 시 만료를 복구하며 중복 제출하지 않는다. 앱 프로세스가 없는 동안 OS에 점수 기록을 즉시 쓰는 서비스를 운용하지 않는다.
- 일반 연습은 화면 밖에서 활성 풀이시간 집계를 쉬며 일시 중단·이어서 풀기가 가능하다. 이는 실전의 경과시간과 별도다. 활성시간 5초 미만 구간은 현재 집계에서 누락될 수 있다.
- 복습: 기본 1/3/7/14/30일, 조정 가능. 당일 반복/도움/헷갈림으로 간격을 앞당기거나 유지한다. 다른 날 무도움 정답이며 헷갈림·추측으로 표시하지 않았을 때 단계를 올린다. 확신도를 입력하지 않은 정답도 이 조건에 포함된다. 숙달/효능/합격 확률 수치로 해석하지 않는다.

## 백업과 개인 정보
- INTERNET 권한, 계정, 광고, 결제, 분석 SDK 없음. OS 자동 백업은 allowBackup=false.
- fullBackupContent=false와 API31+ data-extraction-rules를 추가해 cloud-backup/device-transfer 양쪽의 root/file/database/sharedpref/external 및 device-protected 도메인을 제외했다. 공식 Android Auto Backup 문서(출처 android-auto-backup)가 allowBackup=false만으로 제조사 D2D 이동이 모두 차단되지 않을 수 있음을 명시한다. 실제 제조사 전송 실행은 미검증이다.
- Storage Access Framework 파일 선택으로 내보내기/가져오기. 불필요한 저장소 권한 없음.
- 백업은 32MB 한도, 형식/schema/검사값/참조/상태 검사를 통과한 후 변화 수량을 보여준다. SHA-256은 우발적 손상 검사이며 파일 신뢰성/서명을 보장하지 않는다.
- 복원은 명시적인 전체 교체. 기존 state를 recovery_points에 보관하고 제출 테이블 재구축과 교체를 하나의 트랜잭션으로 수행한다. 실패 시 rollback. 같은 파일 재복원은 중복 학습 시도를 만들지 않는다.
- 백업 파일에는 민감한 개인 메모가 포함될 수 있으며 암호화되지 않는다. 앱 내 안내에 표시한다. 공유/네트워크 전송은 자동 실행하지 않는다.

## 시각 언어
- 종이 #F7F5EF, 잉크 #253632, 청록 #205C52. 작은 제목과 여백으로 편집형 노트 구성.
- 강조는 작성자 '핵심/필수 암기'와 사용자 별표를 별도 컴포넌트로 표현한다.
- width>=840dp에서 목차/노트 또는 문제/해설 두 영역. 그 아래는 한 열. 태블릿 이름 분기 없음.
- 본문17sp, SQL monospace. 시스템 fontScale과 앱0.85~1.5배 설정을 함께 적용한다. 버튼 최소48dp. 다크 별도 palette. UI 캡처와 대비 검사는 QA 보고서에 실제 결과만 기입한다.
- 수동 단계 해설, 자동 음악·소리·진동·장식 애니메이션 없음.


## 2026-09-28: 63강 자료 통합
- 기존 41개 노트와 661개 채점 문항은 별도 유지하고, 강의 순서와 개념별 노트를 같은 하단 노트 탭에서 제공한다.
- 63강 원본 압축파일 및 추출 자료는 수정하지 않는다. 정규화 원본은 content/course-pack.json, 설치본은 assets/course-pack.json이며 독립 검증 후 일치시킨다.
- 강의 읽음은 학습자의 명시적 표시다. 예제 결과 열람과 자기점검 이해/다시 보기는 별도 진도이며 시험점수·합격예측·영상 수강완료로 집계하지 않는다.
- 원본의 189개 서술형 자기점검을 억지로 4지선다 채점 문항으로 만들지 않는다. 기존 모의고사 문항은 강의 연결 연습에서 모두 제외한다.
- JSON StudyState/BackupEnvelope는 v2로 올리고 v1을 이전한다. 기존 앱이 새 백업의 강의 진도를 버린 채 읽지 못하도록 envelope 버전도 올린다. Room 테이블 버전은 1을 유지한다.
- 복원 트랜잭션의 mutex 내부에서 transient restoreGeneration을 갱신하여 이전 강의 화면의 예약 저장을 차단한다. 원자적 복원과 복구 지점은 유지한다.
- SVG 개념도는 앱에 내장한 검증 자료만 표시한다. JavaScript·파일·콘텐츠 접근·네트워크 로딩을 차단하며 새 권한이나 의존성을 추가하지 않는다.

## 0.3.1: 반복 계산과 보조 설정 저장 최적화
- 노트 행의 과거 정답 횟수는 현재 버전 숙달과 다른 지표다. 기존 과거 버전·반복 정답 포함 기준을 그대로 유지하면서 학습목표별로 한 번 집계한다.
- 정적 콘텐츠 검색 문자열과 연결 연습 후보를 재사용하되 검색 조건·제외 기록·모의고사 노출 등 실제 의존 데이터가 바뀌면 갱신한다.
- 1초 시계 구독은 초시계 표시 안으로 제한한다. 시간 저장·만료 제출·채점 상태 전이는 그대로 둔다.
- Room은 계속 정본으로 읽으며 JSON snapshot 구조도 유지한다. 불필요한 두 번째 SELECT만 제거한다. DataStore 보조 투영은 마지막 성공한 설정과 같으면 건너뛰고 실패 시 재시도한다.
- 백업 검사는 세션별 문항 조회표를 사용하며, 먼저 중복 ID를 검사해 인덱스 덮어쓰기로 손상 기록이 가려지지 않게 한다. Room·StudyState·백업 스키마와 콘텐츠 파일은 변경하지 않는다.


## 0.4.0: 기존 강의와 추가 그림의 단계적 통합
- ALTER·OUTER JOIN·GROUP BY 시범 3강의 네이티브 동작을 검사한 뒤 27장·63강 전체에 적용했다. 그림 연결은 제공 manifest의 45개 연결(40강)을 그대로 따른다. 연결 없는 23강은 근거를 남기고 기존 표·SQL로 설명한다.
- 63강 정본은 content/course-pack.json이다. 그림/읽기 안내 정본은 content/course-visuals.json과 content/course-visuals/이며 validators가 검증한 뒤 assets에 동일하게 복사한다. 공급 ZIP의 생성 코드를 실행하지 않는다. 기존 정본이 있으면 초기 import_course 실행을 거부한다.
- 그림 데이터와 원래 예제 데이터는 통합하지 않는다. 각각 검토한 표·식별자·NULL·결과를 유지하고 전환을 명시한다. 정답이 포함된 예제 비교 안내는 모든 예제 결과를 펼친 뒤만 보여 준다.
- 8:5 PNG는 BitmapFactory로 비동기 읽고 Compose에서 확대·축소·양방향 이동한다. 원본 크기는 실제 이미지 픽셀 대비100%다. 회전 시 화면 맞춤 배율이 달라져 표시%는 달라질 수 있으며 이동 위치는 새 경계에 맞춘다. 그림의 정적 [다음]과 실제 예제 단계 버튼을 구별한다.
- 전체 SVG 글자와 표를 선택·복사 가능한 텍스트로 유지하고 목차/노트 검색에도 포함한다. 색 의미는 그림마다 별도 글자 설명을 제공한다. 기존63개 개념도는 삭제하지 않는다.
- CUBE20의 한 화살표 글자만 고치고 원본을 content/course-visuals/originals에 보존했다. 디비전 E02는 고정 학번으로 학생을 연결하며 이름은 표시값으로 유지한다. 이 강의만 version2로 올려 기존 readVersion1을 보존하며 보강 확인 전 상태를 보인다.
- Room schema1, 백업schema2, 채점/세션 snapshot/복습/필기 형식은 그대로다. 외부 API·계정·유료 서비스·INTERNET 권한·새 프레임워크는 추가하지 않는다.

- 큰 글꼴에서 배율 숫자의 줄바꿈이 뷰포트 높이와 배율을 다시 바꾸는 반복을 막기 위해 배율은 고정폭 한 줄로 표시하고 제스처 안내는 별도 문장으로 둔다. 자료 점검용 필드명은 학습 본문 대신 감사 근거에 보관한다.

## 0.8.0: 원본과 분리한 상세 해설
- 강의·문항을 다시 생성하지 않고 `content/lesson-guides`를 정본으로 추가한다. 원본 강의 snapshot 불일치 시 추가 해설 연결을 차단한다.
- FK·INSERT·MERGE 3강의 실제 화면/상태/정답 공개 검사를 먼저 통과한 뒤 63강에 확장했다. 원본 PDF 페이지 참조는 원본 문항의 복제나 전부 개정 완료를 뜻하지 않는다.
- 추가 읽기 단계는 `CourseProgress.exampleSteps["guide:<exampleId>"]`에 저장한다. 원래 예제 완료 및 자기점검 정답 공개 기록을 변경하지 않는다. Room/백업 schema를 변경하지 않는다.
- 문제의 관련 해설은 기존 채점 후에만 제공한다. 자유 입력 AI 튜터 대신 추가 용어·문맥별 질문을 오프라인으로 제공한다.
- 현재 단계 해설/SQL/중간표에는 기존 읽기·필기 컴포넌트를 재사용한다. 짧은 창에서는 SQL 본문 높이를 우선 확보하고 필요한 방향으로 스크롤한다.
- 공급 교재/창작 예제/가상 보충 예제의 데이터를 섞지 않는다. 검산 fixture, Oracle 문서 대조, 독립 AI 검토, 실제 기기/전문가 검증을 구별한다.
