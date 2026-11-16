# 0.10.1 펜 버튼 임시 지우개

기존 SQL 코드 필기 화면은 화면에서 고른 지우개와 `TOOL_TYPE_ERASER`만 읽었다. S펜 옆 버튼의 누름·해제 상태를 읽지 않아, 버튼을 누르는 동안만 지우개로 쓰는 동작이 없었다.

## 실제 변경

- `InkSqlSurface.kt`: 스타일러스 접촉의 `buttonState`를 매번 읽고, `ACTION_BUTTON_PRESS/RELEASE`는 `onGenericMotionEvent`로 처리한다. 버튼을 누르는 동안 임시 획 지우개, 해제하면 원래 선택한 펜/형광펜으로 돌아간다. 색상·굵기·불투명도 설정은 바꾸지 않는다.
- 펜을 떼지 않고 버튼을 눌렀다 떼어도 도구가 바뀐다. 도구 전환 전 실제 접촉 구간을 저장하고, 새 구간을 시작해 지우개 궤적을 가로지르는 펜 연결선을 만들지 않는다.
- 일반 펜 접촉·실제 지우개 팁도 유지한다. 버튼 신호는 스타일러스일 때만 적용하고, 손가락 필기를 별도 스타일러스 버튼으로 바꾸지 않는다.
- hover/버튼 이벤트는 추가 접촉점이 아니다. 누르지 않은 새 접촉의 실제 상태가 이전 hover 상태보다 우선한다. 취소·포커스 상실·화면 분리에서는 미확정 구간과 임시 모드를 정리한다.
- 임시 지우개 상태는 아이콘과 하단 문구로 알린다. 설정 창의 원래 선택 도구는 유지하고 설명 문구를 추가했다.
- `StylusButtonTest.kt`: SDK로 만든 MotionEvent를 실제 View dispatch 경로에 보내는13개 회귀 검사. `actionButton`에는 공개 setter가 없어 합성 검사는 앱이 실제 읽는 `buttonState`를 사용한다. 실제 하드웨어 입력 증거와 구별한다.

입력 API는 [Android MotionEvent 문서](https://developer.android.com/reference/android/view/MotionEvent)의 `getButtonState`, `BUTTON_STYLUS_PRIMARY/SECONDARY`, `ACTION_BUTTON_PRESS/RELEASE`와 [대형 화면의 입력 호환성](https://developer.android.com/develop/ui/views/touch-and-input/input-compatibility-on-large-screens)을 확인했다. 기기별 실제 버튼 전달이나 제조사 설정을 검증했다는 뜻은 아니다.

## 단원 모의고사 확인

기존5개 단원에 각각 **50문항×3회**가 있다. 총15회750문항을 실제 은행과 강의의 `partId`로 대조해 타 단원 혼입0, 세트 내·세트 간 중복ID0, 원본·앱 자산 바이트 동일을 확인했다. 각 회차는 선택한 대단원 전체를 포함하며, 복습용 세부 강의 필터와는 구별된다. 문제나 답안은 이번 수정에서 바꾸지 않았다.

진입은 **홈 → 학습 도구 더보기 → 단원별 추가 문제 → 원하는 단원 → 모의고사1~3회**다. 진도 목차 하단에도 연결이 있다. `unit-mock-membership.json`에 실제 파일 해시와15세트 대조 결과를 기록했다. 이 검사는 공식 시험과의 난도 동등성 검증이 아니다.

## 보존과 검사

Room schema1·백업 schema3, 필기 문서 ID/획 ID/undo 이력 형식, 문제·강의·정답·진도는 변경하지 않는다. 자료와 기존 저장 데이터는 작업 전 백업을 만들었다. 검사 결과는 `evidence/spen-button-20261018/`에 남긴다. 비공개 DB는 `private_evidence/spen-button-20261018/`에 분리하며 APK·소스 ZIP에 넣지 않는다.

- Debug/Release·AndroidTest 빌드 PASS, JVM124/124 PASS. Debug/Release lint 각각 오류0·경고8 (`build-final.log`, `build-summary.json`).
- API34 태블릿1280×800dp에서 **28/28 PASS**: 버튼 합성 입력13, 기존 입력6, 펜 설정1, Room 필기 영속1, SQL 따라읽기7. 눌림/해제·도중 전환·원래 형광펜 설정·undo·취소·포커스·손가락 격리를 실제 View dispatch에서 검사했다.
- 휴대폰360×800dp·시스템 글자200%에서 **14/14 PASS**: 버튼 입력13 및 펜 설정1. 이 수치는28개와 별도 환경의 재검사이며42개 고유 검사라는 뜻이 아니다.
- Debug 실제 홈 확인 후, Release0.10.1/versionCode19 갱신·실제 홈 실행 후 모두 기존 DB 전체 필드·제출55행·복구1행 동일. 실제 샘플은 세션5·별표1·텍스트 필기2·노트4·강의5·자유 필기 문서0이다. 자유 필기 자체의 저장·복원은 별도 합성/격리 DB 검사로 확인했다.
- Release DB 비교는 같은 버전·서명의 Debug를 접근용으로만 설치하고 **Debug 미실행 상태**에서 `run-as`로 읽었다. 이후 Release를 다시 설치하고 원래 표시·애니메이션 설정을 정확히 복원했다 (`final-environment.json`). 원시 DB는 비공개로 유지하며 `release-record-preservation.json`에 방법을 명시했다.
- 물리 Galaxy Tab/S Pen·제조사 버튼 설정·TalkBack: 미실행.

검사 코드는 소스에 포함한다. `scripts/build.ps1 -Tasks assembleDebug,assembleRelease,assembleDebugAndroidTest,testDebugUnitTest,lintDebug,lintRelease -Offline`로 빌드했다. 전용 SQLNote_QA 이외의 사용자 기기나 다른 프로젝트 에뮬레이터는 조작하지 않았다.

## 설치·되돌리기

`dist/SQL-note-0.10.1-release.apk`를 기존 앱 위에 같은 개발 서명으로 업데이트 설치한다. `dist/SQL노트_0.10.1_카톡전송.zip`은 APK와 사용 안내다. 전체 코드는 `dist/SQL-note-0.10.1-source.zip`에 묶는다.

작업 전 소스는 `backups/spen-button-20261018/source-before.zip`이다. 되돌리려면 별도 폴더에 이전 소스를 풀고 현재 설치보다 높은 versionCode로 같은 서명 빌드 후 업데이트한다. 앱 삭제·기록 초기화는 하지 않는다. 설정의 전체 기록 내보내기와 기존 백업 검사·복구 지점 기능을 유지한다.
