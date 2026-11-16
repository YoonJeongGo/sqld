# 요구사항 추적표

원문: `MASTER-REQUEST.txt`. 이 표는 구현 위치를 추적하며 코드 존재만으로 QA 완료를 의미하지 않는다. 마지막 검증 상태는 `QA.md`, 콘텐츠 수량/검증은 `coverage.md`, `content-review.md`에 기록한다.

| ID | 요구사항 묶음 | 구현/콘텐츠 | 증거·확인 대상 |
|---|---|---|---|
| R01 | 신규 환경 확인·오프라인 Android·제약 | Gradle/Manifest/AGENTS/decisions | APK build log, manifest permission 검사 |
| R02 | 공식 시험 기준·출처·ExamSpec snapshot | Models/ContentPack/sources.json | sources-and-scope, 공식 원문 미확인 |
| R03 | 출처 유형·이용권한·창작 표기 | Question.sourceType/validationEvidence | content validation, source registry |
| R04 | 목표·선수·노트·문제 범위 연결 | objectives/notes/question.objectiveIds | coverage.md 자동 누락 탐지 |
| R05 | 필기형 노트·보기 전환·개인필기·위치 | LearningScreens/UiComponents/Annotation | Compose rendered QA, annotation reconcile test |
| R06 | 4지선다·고정 choiceId·SQL 조건·600목표 | part-a/b.json, contract | counts/unique/family/fixture 검사 |
| R07 | 상세 해설·오답 이유·단계 표 | ExplanationPanel/ExplanationStep | 대표 blind review, UI 실제 단계 확인 |
| R08 | DBMS 차이·실행/문서 구분·SQL bag | SqlFixture/StudyEngine.equalRows | 공식 문서 대조, bag test; 엔진 미실시 |
| R09 | 연습 두 채점·실전 개별채점 숨김·도움 전환 | StudyEngine/SessionScreens | JVM + LearningUiTest + UnitMockFlowCaptureTest |
| R10 | 별표·현재/과거오답·확신도 | StudyState/ReviewScreen | bookmark/immutable sessions test |
| R11 | 간격복습·오늘양·새학습·개수선택 | StudyEngine.grade/Home/Practice dialog | review rule test, 실제 수량 경계 |
| R12 | 모의고사·타이머·미열람·통계 분리 | MockScreen/StudyEngine.tick/Result | clock/family/score tests + emulator |
| R13 | 전 화면·반응형·검색·표 SQL 확대 | Main/UiComponents/all Screens | 캡처 크기별 실제 확인 |
| R14 | 48dp·대비·200%·TalkBack·키보드 | Theme/components/semantics | contrast JSON + UI captures; 실물/음성검증 별도 |
| R15 | 콘텐츠/기록 분리·영속·트랜잭션·snapshot | StudyRepository/Models | Room reopen/duplicate/failure tests |
| R16 | 전체백업·원자복원·로컬정정·보안 | BackupCodec/restore/SAF/ContentIssue | malformed/future/rollback/recovery tests |
| R17 | 콘텐츠 파이프라인·독립풀이·공개차단 | scripts/validate_content.py/blind_review.py | evidence/content*.json |
| R18 | 단위·통합·E2E·상태기반·시각QA | test/androidTest/scripts | 실제 XML/JUnit/캡처 로그 |
| R19 | 단계별 작동·오류정직보고 | docs/QA + evidence | APK 설치/오프라인 첫 실행 증거 |
| R20 | 소스·APK·문서·한계 인수인계 | README/APK/docs/evidence | 산출물 hash 및 최종 QA 표 |
| R21 | 제공한 63강 자료·5개 단원·기존 노트 연결 | CourseModels/CourseScreens/course-pack.json | validate_course.py 및 course-content-review.md |
| R22 | 강의 읽기·예제·자기점검 진도 분리, 이어보기·백업 | CourseStudy/CourseProgress/BackupCodec v2 | CourseStudyTest/CoursePersistenceTest/CourseUiTest, course-integration-0.3.0.md |

| R23 | 63강·27그림 통합, 실제 자료 대조 및 기록 보존 | CourseVisualModels/CourseVisualScreens/course-visuals.json | visual-integration-0.4.0.md, visual-lesson-changes.md, visual-data-consistency.md |

## 명시적 미검증 또는 후속 판정 필요
- DataQ 현행 출제기준·변경·정오표 원문 미확인. 목표34개는 초안 및 출판사 교차자료 기반.
- 실제 Oracle/SQL Server 엔진 실행, 사람 전문가/학습효과, Galaxy S24+/Tab, TalkBack 읽기·외부 키보드 실기기 검증.
- 최초 schema1의 기존 앱버전→새 Room schema 실마이그레이션 증거는 적용할 기존 버전 없음. destructive fallback을 사용하지 않는다.
- 0.3.0에서는 Room 테이블 schema1을 유지하며 JSON 학습 상태·백업만 v1→v2로 이전했다. 기존 0.2.2 에뮬레이터 앱의 55개 제출·3개 세션·필기·설정 등 기존 필드 동일성은 `evidence/course-update-preservation.json`으로 확인했다. 새 Room 테이블 스키마 마이그레이션 검증과는 구분한다.
- 콘텐츠 정정 비교 UI는 합성 이전 버전의 제출을 사용한 Compose 테스트에서 원판정과 현재 참고 판정을 함께 표시하고 원본을 유지함을 확인했다. 개발 중 발견·수정한 문항은 팩의 corrections에 기록했다. 실제 과거 출시판에서 새 출시판으로 옮긴 사용자 기록의 정정 비교는 미검증이다.
- SQL fixture는 문서 기반 예상표와 값/열위치/중복 bag/순서 비교이며, 실제 DBMS 데이터타입·숫자 정밀도·드라이버 결과 정규화 검증은 미실행이다.

## 인수인계 상태

- 구현 완료: R01, R03~R07, R09~R13, R15~R16의 로컬 앱 동선 및 R20 소스·디버그 APK·문서. 모든 세부 기기 조건의 검증 완료를 의미하지 않는다.
- 부분 확인: R02(공식 현행 원문 미확인), R08(문서/독립 풀이와 fixture 검사, 실제 엔진 미실행), R14(일부 대비·크기·UI 검사, 실제 TalkBack/외부 키보드/지정 기기 미검증), R17(구조 전수 및 AI 교차검토, 사람 검수 미실시), R18~R19(자동·전용 에뮬레이터 실행, 실기기·실제 저용량 장애·장기 성능 미실시).
- 선택형 SQL 실습실/외부 서비스/공개 릴리스는 구현 또는 수행하지 않았다. 검증된 정적 해설 단계를 사용한다.
