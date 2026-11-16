# 0.4.1 강의 본문 폭 개선

태블릿에서 63강 본문이 760dp로 제한되어 그림 양옆에 큰 빈 공간이 남았다. 본문의 최대 폭 제한을 제거하고 좌우 20dp 바깥 여백을 유지했다. 공통 화면의 1200dp 제한도 강의 경로에만 적용하지 않아 왼쪽 목록을 접으면 그 공간까지 사용한다. 기존 41개 개념 노트와 다른 화면은 이번 변경 대상이 아니다.

그림 자체는 8:5 비율을 유지한다. 넓어진 그림이 화면 높이보다 크면 본문을 위아래로 스크롤해 읽는다. 실제 표시 폭이 원본의 절반을 넘으면 축소 이미지 대신 원본 해상도로 읽어서 태블릿에서 글자가 흐려지는 것을 방지한다. 별도 확대 화면의 화면 맞춤·원본 크기·확대·축소·끌어 이동은 기존 동작을 유지한다. 전체 그림을 한 번에 맞춘 확대 화면에는 화면과 그림의 비율 차이로 여백이 남을 수 있다.

## 보존

- 강의·그림·문항 JSON은 0.4.0과 바이트 단위로 같다. `evidence/visuals-width-content-hashes.json`에 SHA-256을 기록했다.
- 전용 에뮬레이터에서 0.4.0 → 0.4.1 업데이트 전후 실제 저장 상태 17개 필드가 모두 동일했다. 제출 55개와 강의 진도 5개를 포함한다. `evidence/visuals-width-state-update.json` 참조. 원본 DB는 소스 ZIP에 넣지 않는 비공개 로컬 백업에 보존했다.
- Room schema, 백업 형식, 채점·예제 단계·답안 공개 조건을 변경하지 않았다.

## 실행 및 되돌리기

`scripts/build.ps1`로 `assembleDebug,assembleRelease,testDebugUnitTest,assembleDebugAndroidTest,lintRelease`를 실행한다. 기존 의존성이 준비된 환경에서는 `-Offline`을 사용할 수 있다. `python scripts/package_artifacts.py --build-type release`로 APK와 소스 ZIP을 묶는다.

설치는 같은 서명의 `dist/SQL-note-0.4.1-release.apk`를 `adb -s <확인한 기기> install -r <APK>`로 업데이트한다. 기존 앱을 제거하지 않는다. 0.4.0 APK·소스 ZIP은 그대로 보존했다. 코드 복원은 `evidence/visuals-width-before/`의 변경 전 소스 또는 0.4.0 소스 ZIP에서 해당 파일만 복구한다. 설치된 최신 앱을 되돌릴 때는 복구 코드를 더 높은 versionCode로 빌드해 업데이트하는 방법을 우선 사용한다. Android의 버전 내림 거부를 우회하려고 앱을 제거하면 학습 기록이 삭제될 수 있다.

## 검증 범위

최종 빌드·화면별 검사 결과와 실제 release 화면은 아래에 기록한다. Galaxy Tab 실기기와 S Pen 검증은 하지 않았다.

- 최종 오프라인 debug/release 빌드 성공. JVM 72개 통과. release lint 오류 0개, 기존 경고 4개.
- 1280×800dp 태블릿 가로, 글씨 100%: 그림·강의·목록 접기 Android UI 11개 통과. `evidence/visuals-width-tablet-android.log`.
- 360×800dp 휴대폰 세로, 글씨 100%: 그림·강의 Android UI 8개 통과. `evidence/visuals-width-phone-android.log`.
- 320×640dp 작은 휴대폰, 글씨 200%: 그림 Android UI 5개 통과. `evidence/visuals-width-large-font-android.log`.
- 0.4.0 release와 최종 release의 학습 자산 57개가 모두 같다. 빌드 코드에 따라 생성되는 dexopt 프로필 2개는 학습 자산 비교에서 제외했다. `evidence/visuals-width-integrity.json`.
- 실제 화면보다 높아진 그림의 비율 검사는 화면에 잘려 보이는 영역이 아닌 전체 측정 크기를 사용한다. 원본 PNG의 8:5와 화면 배치 비율을 계속 검증한다.
- 최종 release 0.4.1을 업데이트 설치해 2560×1600px/density320에서 목록 펼침·접힘과 그림 아래쪽 스크롤을 실제 캡처했다. `evidence/visuals-width-release-tablet.png`, `evidence/visuals-width-release-tablet-collapsed.png`, `evidence/visuals-width-release-tablet-bottom.png`. 원본 PNG나 목업을 앱 화면으로 제시한 것이 아니다.
