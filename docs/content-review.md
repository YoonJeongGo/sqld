# 콘텐츠 독립 검토 기록

> 0.2.0의 콘텐츠 보강·중요도·현재 검증은 [priority-update.md](priority-update.md)를 참조하세요. 아래 초기 개발 기록은 당시 검증 범위를 보존합니다. 최신 콘텐츠 수량과 검수 집계는 coverage.md 및 evidence/content-review-summary.json에 있습니다.

확인일: 2026-09-14. 작성 역할: sources_scope (독립 AI 검토). **사람 전문가 검수·Oracle/SQL Server 실행·학습 효과 검증을 수행하지 않았다.**

## 0.1.0 동결 당시 결과

최종 동결본은 노트34개·문항600개(활성600, 격리0)·출처73개·정정5건입니다. 현재 정답과 해설600개에 대한 AI 교차 검토 근거를 추적했습니다: 원본 hash 일치550, 공개 상태만 변경1, 변경본 실제 재독49입니다. 정답/보기 순서를 마스킹하고 사전 정답 노출이 신고되지 않은 최초 검토 스냅샷은532개이며, 전체600개를 최초 완전 blind로 검토했다고 주장하지 않습니다. 공식 현행 범위·DBMS 실행·사람 검수는 미확인 또는 미실시입니다.

0.2.0을 포함한 현재 집계는 [content-review-summary.json](../evidence/content-review-summary.json), 현재 수량은 [coverage.md](coverage.md)입니다. 아래의 초기20개/추가12개 기록은 과정의 원본 증거이며 최종 수량을 뜻하지 않습니다.

## 초기 대표 묶음 검토 기록

초기 part-a의 대표 10문항과 part-b의 대표 10문항, 합계 **20문항**을 정답·해설·보기 이유를 읽기 전에 독립 풀이했다. 이후 원본 정답과 비교하여 **20개 일치, 0개 불일치**를 확인했다. 정답 일치는 조건·메타데이터·시각화까지 완성되었다는 의미가 아니다. 작성 중 새로 추가되는 문항은 이 결과에 포함되지 않는다.

독립 판단은 ID와 실제 선택 의미를 기준으로 기록했다. 이 초기 묶음은 정답의 고정 choiceId가 모두 a이지만 저장 배열의 정답 위치는 달랐다. 이 사실 자체를 정답 오류로 판정하지 않았다. 표시 위치 편향과 보기 섞기 동작은 전체 팩 자동검사와 앱 QA에서 별도로 확인해야 한다.

| 구분 | 확인 범위 | 결과 |
|---|---|---|
| 정답을 숨긴 독립 풀이 | S07-R01/R02/R03, S07-A01/A02/A03, S06-A01/R01, S08-A01/R01 | 10/10 원답 일치 |
| 정답을 숨긴 독립 풀이 | S09-R01-guarantee/R02-null-asc/R03-tie-order/R04-alias-order/R05-multi-key, S10-R01-pair-product/R02-null-equality/R03-cross-product/R04-non-equi/R05-join-union | 10/10 원답 일치 |
| 정답 공개 후 해설 대조 | 위 20개 요약·단계·보기별 이유 | 계산 또는 정답과 모순 발견 없음 |
| SQL fixture 완결성 | 위 적용 5문항 | 모두 fixture 메타데이터 누락 발견, 보완 요청 |
| 600문항 목표 전수 검수 | 미수행 | 완료 주장 불가 |
| 모델링 정규화 문항 독립 풀이 | 이 초기 묶음에 없음 | 미수행 |
| 고위험 응용 전 영역 독립 풀이 | 외부조인/서브쿼리/윈도우/트랜잭션 적용 대표는 아직 묶음에 없음 | 미수행 |
| Oracle/SQL Server 실행 | 미수행 | document review와 혼동 금지 |
| 실제 화면의 문제·해설 렌더링 | 이 역할에서 미수행 | 앱 QA 담당 결과 참조 |

## 증거와 재현

- 입력: [content-blind-input.json](../evidence/content-blind-input.json)
- 독립 정답·논리: [content-blind-decisions.json](../evidence/content-blind-decisions.json)
- 비교 결과: [content-blind-comparison.json](../evidence/content-blind-comparison.json)
- 실행 스크립트: [blind_review.py](../scripts/blind_review.py)
- 입력 SHA-256: `0f4b319aa1bf847a1861f5e15b3ce24c685dec901f257c0b1527af2ec0281cd4`
- 독립 결정 SHA-256: `60c07b9b35dbaef241f52d0cf5a631c054c1b0da5d194cc2edfca57db06f3c1b`
- 입력 작성: 2026-09-14 04:17:07 UTC
- 원답 비교: 2026-09-14 04:18:16 UTC

PowerShell, Python 3.14 환경에서 아래 명령을 실제 실행했다.

```powershell
python scripts/blind_review.py prepare content/part-a.json content/part-b.json --output evidence/content-blind-input.json
python scripts/blind_review.py compare --input evidence/content-blind-input.json --decisions evidence/content-blind-decisions.json --output evidence/content-blind-comparison.json
```

새 묶음은 기존 증거를 덮어쓰지 않는 새 입력/결정/결과 파일로 검토한다. `prepare --ids ID1,ID2`로 문항을 제한할 수 있다. 입력은 allowlist를 사용하여 questionId·title·stem·sql·tables·choiceId/text·DBMS·fixture의 입력만 내보낸다. correctChoiceIds, explanation, choice reason, fixture expectedRows 및 evidence는 제외된다. 독립 결정 저장 후에만 `compare`가 원본 정답을 읽는다.

문항 전체 SHA-256을 저장하므로 내용이나 해설이 바뀌면 `source_changed_requires_review`로 구분한다. 따라서 후속 작성자가 오류를 고쳐도 과거 검토를 현재 문항 전체에 자동 승계하지 않는다. 출력의 `answer_agrees`는 답안 일치 결과이지 자동 공개 승인 상태가 아니다.

## 발견 사항 및 후속 확인

### CR-001 — SQL 적용 문항의 fixture 누락

대상: S07-A01/A02/A03, S06-A01, S08-A01.

숫자 입력과 기대 답은 독립 풀이에서 일치했으나, 테이블 DDL/열 타입·setup SQL·query·제약·세션 조건·expectedRows·순서 보장 여부를 묶은 fixture가 없다. 원문에 입력값이 있다는 것만으로 사용자 명령서의 SQL 검증 메타데이터 요구를 충족하지 않는다. 콘텐츠 작성자에게 NUMBER 타입과 문서 검토 상태를 포함한 fixture 보완을 요청했다. **보완 확인 전 미해결.**

### CR-002 — SQL 시각화 중간 표 부족

S07-A01의 COUNT 대상(모든 행/비NULL 열)과 S08-A01의 그룹별 합계/HAVING 판정은 텍스트 단계로 설명되지만 단계에 연결된 중간 table은 없다. 최소 NULL·COUNT, GROUP BY/HAVING의 요구된 단계 시각화를 위해 선택 대상 행과 최종 결과를 표시하는 step.table 보완을 요청했다. **보완 확인 전 미해결.**

### CR-003 — 학습자 사고 단정 표현

S08-A01의 b 보기 이유 "개별 금액>=20을 WHERE로 걸렀을 때와 혼동했다."는 학습자가 실제로 그렇게 사고했다고 단정한다. "WHERE 금액>=20을 먼저 적용한 결과에 해당한다." 등의 객관적 비교로 변경 요청했다. **보완 확인 전 미해결.**

### CR-004 — 조건 명료화 권고

- S07-R03: SUM(x)의 x가 숫자 열이라는 전제 명시.
- S09-R01: ORDER BY도 동률을 완전히 정하려면 유일한 보조 키가 필요함을 해설에 연결.
- S09-R04: doubled가 원본 열이 아닌 계산 별칭임을 지문에서 분명히 제시.
- S10-R01: 같은 조인 값이 비NULL이며 해당 등호 조인 조건만 있고 추가 필터/DISTINCT가 없음을 명시.

위 문항의 의도한 단일 답은 이해 가능했고 독립 답과 일치했다. 이 권고는 불필요한 해석 여지를 줄이기 위한 것이며 현재 확정 답 오류로 집계하지 않았다.

## 공개 및 완료 판단

이 검토만으로 콘텐츠 팩 전체를 cross_reviewed로 승격시키면 안 된다. 독립 검토에 포함된 정확한 문항 버전/해시만 추적하고 발견 사항 수정 후 다시 대조한다. 새 목표·새 문항·새 모의고사 family는 각각 검토해야 한다. 구조 검사 통과, 정답 일치, 공식 문서 대조, 엔진 실행, UI 검수, 사람 검수를 서로 다른 증거로 남긴다.



## 추가 고위험 SQL 적용 12문항 — 보기 ID도 마스킹

2026-09-14 04:48:12 UTC, 외부조인 COUNT, NOT EXISTS, 빈 NOT IN/ALL, ROLLUP의 원본 NULL, 반복 GROUPING SETS, LAG NULL/default, NTILE, RANGE peer, 빈 미래 COUNT 프레임, 계층 WHERE, PIVOT의 남은 열을 대상으로 추가 독립 풀이를 했다. 기존 20문항 증거 파일은 수정하지 않았다.

원저술 정답이 공통 의미 ID `a`였기 때문에 이번에는 지문·SQL·입력·보기 텍스트만 추출한 다음 각 보기 ID를 무작위 `r1`~`r4`로 바꾸었다. 원래 ID의 대응표는 별도 파일에 쓰고, 독립 결정을 저장할 때까지 읽거나 출력하지 않았다. 입력에는 정답·보기별 이유·해설·예상 결과가 없다.

- 입력: `evidence/content-blind-risk-input.json`
- 독립 결정: `evidence/content-blind-risk-decisions.json`
- 후속 비교: `evidence/content-blind-risk-comparison.json`
- 선택 ID 대응표: `evidence/content-blind-risk-choice-map.json` (비교 단계에서만 사용)
- 입력 SHA-256: `1fa976db4d92520dfd26df5847e73211145de14f7f75fbd8f07c335c380248fc`
- 결정 SHA-256: `f0140e665b3b8988e9561ab6c2c25e77d3a5e350545e19061f21b8c04eebd2a5`

04:49:39 UTC 후속 원답 비교에서 12/12 일치, 불일치 0, 당시 원본 변경 0이었다. 원답 비교 전 각 결과의 연산 단계와 조건을 독립 결정 파일에 기록했다. 이번 단계는 정답 비교이며 이 12개 해설 전체를 별도의 독립 해설 검수 완료로 올리지 않는다. Oracle 엔진 실행이나 사람 전문가 검수가 아니다.

검수된 과거 스냅샷은 기존20+추가12=총32개이다. 이후 개정된 문항에는 hash가 다른 과거 검수 결과를 자동 승계하지 않는다. 현재 원본과 같은 검수본 개수는 자동 검증 보고서가 매번 계산한다. 전체 콘텐츠의 독립 정답 검수로 확대 해석하지 않는다.


## 보완 후 재확인

2026-09-14 후속 원본을 직접 읽어 CR-001의 다섯 적용 문항 모두 fixture를 갖춘 것을 확인했다. SQL/schema/setup, 예상 행, 세션 조건, 문서 자체 검토 evidence를 구조 검사했다. Oracle 실행으로 확인한 것은 아니다.

CR-002는 S07-A01의 COUNT 대상 표와 S08-A01의 그룹 합계/HAVING TRUE·FALSE 표 및 최종 결과 표를 실제 확인해 보완을 확인했다. CR-003은 S08-A01의 b 보기 이유가 객관적 WHERE/HAVING 비교로 바뀐 것을 직접 확인했다. CR-004 중 S07-R03의 x NUMBER 전제도 해설 조건에 추가되었다. 이 보완으로 기존 독립 입력의 hash가 바뀌었으므로 원래 blind 결과를 개정본 전체 검수로 자동 승계하지 않는다.

근접 중복 검토 중 발견한 S02-A02의 “DISTINCT가 제거된 뒤”라는 표현은 “DISTINCT가 중복 행을 제거한 뒤”로 수정된 원본을 직접 확인했다. 이는 정답 2행과 지문을 일치시키는 문구 수정이다.


추가12의 정답을 저장·비교한 뒤 현재 해설의 요약·단계·결과 표·모든 보기 이유도 읽어 대조했다(`evidence/content-blind-risk-explanation-review.json`). 계산 및 정답과의 모순은 발견하지 않았으나 S16-A01 기억 문장의 “ORDER BY 생략”으로 읽힐 수 있는 표현을 발견했다. 정확한 조건은 ORDER BY가 존재하고 프레임 절만 생략한 경우이며 B 작성자에게 수정을 요청했다. S14-A01의 원본 NULL 그룹을 “소계”로 부르는 용어도 실제 그룹과 집계 생성 소계를 구분하도록 보완 요청했다. 이 두 표현의 수정 확인 전에는 해당 해설의 완결 검수로 표시하지 않는다.


S16-A01의 기억 문장이 “ORDER BY가 있고 프레임 절을 생략하면 RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW”로 수정되고 S14-A01의 원본 NULL 그룹 표현이 “집계값5”로 바뀐 현재 원본을 직접 확인했다. 정답풀이의 원래 증거를 덮어쓰지 않고 해설 표현 보완 확인을 별도 기록한다.


## 노트 34개 본문 검토

모델링 M01~M10과 SQL S01~S24의 노트 34개 본문을 실제로 읽고 정의·조건·예시·비교·기억·오해·회상 연결을 대조했다. 입력 스냅샷은 `evidence/note-review-input.json`, 검토 결과와 노트별 SHA-256은 `evidence/note-content-review.json`에 남겼다. 정답을 가리는 문항 blind 검수와는 별도의 본문 검토다.

식별/비식별 관계와 필수 참여의 구분, ANY/ALL의 빈 집합 및 NULL, LAG/LEAD의 기존 NULL과 누락 행 default 및 NTILE의 나머지 배정 설명 부족을 발견해 저술자가 보완했다. 외부조인 WHERE의 SQL 위치, ROLLBACK 예시의 초기 COMMIT 상태, ROW_NUMBER의 최대 n행 표현도 수정했다. 위 여섯 보완은 현재 본문을 다시 읽어 확인했다. 안정된 기존 블록 ID를 유지하고 새 설명은 새 블록 ID로 추가했다.

이 검토는 독립 AI의 문서 의미 및 교육 연결 검토이며, 사람 SQLD 전문가 검수나 공식 현행 범위 확인·Oracle 실행·학습 효과 검증이 아니다. 원래 노트 입력 스냅샷을 보존하고 수정된 노트의 현재 해시와 재확인 범위를 따로 기록했다.


## 의미상 중복 교체와 공개 상태 추적

자동 문자열 중복 검사 외에 content_b가 발견한 M10-A01과 mock-1-M10-reservation-timeslot 버전1을 sources_scope가 원문·보기·해설까지 직접 대조했다. 인조 PK 외에 두 업무 열의 복합 UNIQUE를 추가하는 동일 판단에서 이름만 바뀐 문항이어서 기존 모의 문항을 격리했다. 확정 중복의 당시 양쪽 해시와 판단은 `evidence/content-duplicate-review.json`의 이전 스냅샷에 보존했다.

저술자는 버전2를 인조 PK 추가 후에도 모든 후보키 기준의 부분 종속이 남는 2NF 판정으로 교체했다. sources_scope는 현재 원문·보기·해설 및 기존 M06/M10 문항과의 판단 차이를 직접 확인했고, Waterloo의 대학 정규화 자료도 다시 접속해 정의를 대조했다. content_b의 새 마스킹 풀이 및 해설 대조도 완료했다. 검토 당시 격리본 전체 해시는 `849657efef32073997ed12518dbb513ded79df51c5c29c115f651613cbf36e5a`, status만 published로 바꾼 현재 전체 해시는 `00dfac7291c4dab67b798914567740edc5ddaeb1493dd6460fb7f489a65602d0`이다. 현재 객체의 status만 quarantined로 되돌려 해시를 계산했을 때 검토 당시 해시와 일치하는 것을 실제 확인했다. 원래 blind 증거는 수정하지 않았다.

최종 교차 검토 집계는 `scripts/summarize_content_reviews.py`가 만드는 `evidence/content-review-summary.json`에 별도로 남긴다. 중복 패스는 한 문항으로 세며, 정답 비교·해설 읽기·최신 원본 해시 일치·공개 상태만 변경·실제 변경본 재독·이전 정답 노출을 구분한다. 최초 ID 공개 검토 뒤 마스킹을 다시 적용한 결과를 최초 완전 blind로 승격하지 않는다.


## 최종 동결본 집계

최종 콘텐츠는 34목표·34노트·회상150+적용200+모의250=600문항이다. 모의는 각 모델링10+SQL40의 5세트이며 활성600, 격리0이다. 출처73개 중70개는 실제 문서 반환을 확인했고 DataQ3개 레코드는 미확보·과거색인 상태로 구분했다.

600개 고유 문항 모두 다른 AI의 정답 대조와 해설 읽기 이력이 있다. 최신 동결본은 정답 비교 당시 전체 객체 해시가 그대로인550개, 공개 상태만 변경된 것으로 입증한1개, 변경된 원문·해설을 실제 다시 읽어 근거를 저장한49개로 추적된다. 해설도 같은 최신600개 전부에 추적 근거가 있다. 변경49개 중42개는 현재 전체 본문 재독,7개는 저장된 이전 전체 스냅샷의 필드 차이와 현재 본문을 함께 읽었다. 존재하지 않는 과거 전체 스냅샷을 만들어냈다고 주장하지 않는다.

보기 ID와 순서를 가린 풀이 이력이 있는 고유문항은600개이나, 이전 정답 노출이 없었다고 기록된 마스킹 스냅샷 범위는532개다. 초기 B적용80은 원래 의미 ID가 보인 상태에서 읽었고 나중에 이전 정답노출을 명시하여 재계산했다. 이 중12개에는 다른 검토자의 별도 최초 마스킹 풀이 증거가 있다. 따라서 전체600개가 최초부터 완전 blind 검토되었다고 주장하지 않으며 `fullIndependentContentReview`를 일괄 승격하지 않았다.

원문·숫자만 바꾼 동일 family 1쌍을 실제 발견해 모의 원문을 교체했다. 자동근접11쌍+수동발견1쌍의 현재 조건을 다시 읽어 구별되는 규칙과 경계를 기록했으며, 탐지된 미해결 동일 family는0이다. 이로 전체 의미 중복 가능성이 수학적으로 제거된 것은 아니다. 정답 배열 위치·보기 길이 자동 편향 검사도 별도 보고서에 남겼다.

`python -m unittest discover -s scripts -p 'test_*.py'`는 실제28개 테스트 통과했다(`evidence/python-unit-tests.log`). `validate_content.py --strict`도 종료0이었다. `summarize_content_reviews.py`는 최신 스냅샷·수정기록 해시를 대조해 거부된 amendment0, 누락된 최신 정답·해설 추적0을 확인했다.

동결 asset SHA-256: `69c48d57773fa2b954f86328a9f65140bfc9875520afeb4dc5976fff6c200437`.

남은 한계는 공식 현행 출제기준·공지·정오표 원문 미확보, Oracle/SQL Server 실행 미실시, 사람 전문가 검수 미실시, 일부 붙은 한국어 띄어쓰기와 잘린 짧은 제목이다. SQL 비교는 예상 표의 행·열·NULL·중복 bag·순서를 다루며 DBMS 반환 타입이나 숫자 정밀도 정규화까지 실행 검증한 것은 아니다. 이 문서는 Android 기기·접근성·학습 효과의 증거를 대신하지 않는다.


마지막 앱 연동 확인에서 문항별 correction 메타데이터5건이 Kotlin ContentPack.corrections에 전달되지 않던 누락을 수정했다. 원본 문항과 개별 문항 해시는 유지하고 팩에 questionId/fromVersion/toVersion/reason/at의 최상위 이력을 추가했다. 회귀 테스트1건을 추가해 전체Python28개 통과를 확인했다.
