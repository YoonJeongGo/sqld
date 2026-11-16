# 강의 범위 보강 A — 작성자 검토 기록

작성일: 2026-09-14
상태: 작성자 문서 대조 완료. 새 문항 전부 quarantined. 독립 검수·Oracle 엔진 실행·사람 전문가 검수·기기 QA는 이 작업에서 하지 않았다.
대상: content/part-a.json. 기존 285문항, 18 objectives, 기존 노트 블록 원문을 모두 보존했다. 수정 노트는 version 1 → 2이며 블록·참고문항·출처만 추가했다.
작성 전 part-a 의미 내용 SHA256: 4216e7c9adebfbe3bd2462f71d5bd043dad7b8761e204b0832d38a682ddaacb1

## 추가·수정 목록
- 신규 objectives/notes: note-M11, note-M12, note-M13, note-S25, note-S26
- 확장 노트: note-M01, note-M02, note-M06, note-S03, note-S05
- 신규 문항: 35개 (회상 19, 적용 16). 기존 모의고사 5세트에 손대지 않았다.
- 독립 검수는 이 문서와 정답·해설을 숨긴 별도 입력으로 진행해야 한다. 이 파일을 읽은 검수자는 완전 블라인드라고 표기할 수 없다.

## 문항 목록 및 근거
| 문항 | 종류 | 출처 | 작성자 검토 초점 |
|---|---|---|---|
| M11-R01-external-view | recall | ucdavis-three-schema | 질문은 전체 구조나 디스크 저장이 아니라 특정 역할이 보는 정보를 묻는다. |
| M11-R02-physical-independence | recall | ucdavis-three-schema | 변경 대상은 내부 저장 방법이다. |
| M11-R03-process-versus-layer | recall | ucdavis-three-schema | 모델링 단계는 설계 활동의 구체화 수준을 구분한다. |
| M11-A01-split-preserved-view | application | ucdavis-three-schema | 테이블 분리는 개념적·논리 구조의 변화다. |
| M11-A02-index-stable-meaning | application | ucdavis-three-schema | 바뀐 것은 내부 접근 경로이며 이용자가 다루는 논리적 의미는 유지된다. |
| M12-R01-endpoint-direction | recall | uiowa-erd-conceptual | 출발점을 회원 한 명으로 잡는다. |
| M12-R02-cardinality-minimum | recall | uiowa-erd-conceptual | 「여러 개까지 가능」과 「반드시 하나 이상」은 다른 질문이다. |
| M12-R03-erd-first-business | recall | uiowa-erd-conceptual | 같은 회원·예약 이름이라도 회원 없는 예약을 허용하는지 등에 따라 규칙이 달라진다. |
| M12-A01-optional-parent-not-null | application | uiowa-erd-conceptual, oracle19-constraints | 점검 하나에서 장비를 보면 장비 쪽 표기는 //다. |
| M12-A02-association-history-key | application | uiowa-erd-conceptual | 한 번만 참가한다면 두 번호의 조합이 유일할 수 있다. |
| M13-R01-deliberate-redundancy | recall | cornell-denormalization, aalto-denormalization | 합계는 원본 상세에서 다시 계산할 수 있는 값을 따로 저장한 것이다. |
| M13-R02-measure-before-choice | recall | cornell-denormalization | 먼저 어떤 조회·데이터량에서 무엇이 느린지 확인한다. |
| M13-R03-snapshot-meaning | recall | aalto-denormalization | 값의 모양보다 그 속성이 나타내는 사실의 시점을 확인한다. |
| M13-A01-total-cancellation | application | cornell-denormalization, aalto-denormalization | 현재 유효 상세는 30분 한 건이다. |
| M13-A02-frequent-master-update | application | cornell-denormalization | 사본은 과거 번호 기록이 아니라 현재 전화번호를 나타낸다. |
| S25-R01-char-varchar-storage | recall | oracle19-datatypes | 두 열의 선언 길이는 4이고 입력은 2문자다. |
| S25-R02-number-precision-scale | recall | oracle19-datatypes | p=5, s=2이며 일반적인 비음수 스케일 사례다. |
| S25-R03-date-timestamp-fields | recall | oracle19-datatypes | DATE의 필드에는 시·분·초가 포함된다. |
| S25-A01-explicit-char-length | application | oracle19-datatypes, oracle19-cast, oracle19-length | CAST의 목표 자료형을 각각 확인한다. |
| S25-A02-numeric-cast-scales | application | oracle19-datatypes, oracle19-cast | NUMBER(5,2)는 셋째 소수 6을 보고 12.35를 만든다. |
| S26-R01-add-modify-update | recall | oracle19-alter-table, oracle19-update | 요구를 열의 존재, 열의 정의, 행의 값으로 나눈다. |
| S26-R02-rename-column-vs-alias | recall | oracle19-alter-table, oracle19-rename | 질문은 출력 별칭이나 열의 값이 아니라 실제 열 이름을 요구한다. |
| S26-R03-drop-column-versus-delete | recall | oracle19-alter-table, oracle19-delete | DROP COLUMN의 대상은 열의 정의와 값이다. |
| S26-A01-add-null-existing-row | application | oracle19-alter-table | 초기 행은 id=5 한 건이며 새 score에 DEFAULT를 지정하지 않았다. |
| S26-A02-rename-retains-values | application | oracle19-alter-table, oracle19-rename | 열 code가 item_code로 바뀌고 테이블 T가 T_ARCHIVE로 바뀐다. |
| S03-R07-instr-result-kind | recall | oracle19-instr, oracle19-substr | INSTR는 문자열이 어디에서 발견되는지를 묻는다. |
| S03-A07-instr-occurrence-missing | application | oracle19-instr | BANANA의 문자 위치를 1부터 세면 AN이 2와 4에서 시작한다. |
| S03-A08-padding-final-length | application | oracle19-lpad, oracle19-rpad | 두 원본은 한 문자이고 목표 전체 길이는 4다. |
| S03-A09-negative-integer-directions | application | oracle19-abs, oracle19-sign, oracle19-ceil, oracle19-floor | ABS는 크기만 남기고 SIGN은 음수임을 -1로 나타낸다. |
| S03-A10-lower-uppercase-sequence | application | oracle19-lower, oracle19-upper | 안쪽 UPPER를 먼저 계산하면 SQL이다. |
| S05-R06-nvl2-return-branch | recall | oracle19-nvl2 | 먼저 x=0이 NULL인지 판단한다. |
| S05-A07-decode-null-versus-case | application | oracle19-decode, oracle19-case | DECODE는 NULL 검색값을 만나 hit를 반환한다. |
| S05-A08-decode-default-omitted | application | oracle19-decode | 검색값과 결과를 (1,A), (2,B)로 짝짓는다. |
| M06-R06-bcnf-superkey | recall | juniata-bcnf | 비자명 함수 종속의 왼쪽 X가 무엇을 결정하는지 확인한다. |
| M02-R06-classification-two-axes | recall | kimnbuk-entity-classification | 문항은 엔터티가 무엇을 기록하는지와 어떻게 발생하는지를 나눈 명칭을 묻는다. |

## 정확성·보존 확인
- M11: 모델링 단계와 스키마 계층을 구별하고 물리/논리 독립성의 변경 계층·보호 계층을 확인했다.
- M12: 회원 ||──o{ 예약에서 오른쪽 0..N은 회원 1명 기준 예약 개수임을 재검토했다. 실제 도식 이미지를 복제하지 않고 자체 텍스트 도식을 작성했다. 기호 범례와 양방향 문장을 함께 제공한다.
- M13: 반정규화의 자동 성능 향상 주장을 배제하고 원본/집계 변경·대사 및 과거 사실의 별도 의미를 확인했다.
- S25: ASCII CHAR/VARCHAR2 길이, NUMBER(5,2)/(5,-1) 반올림, Oracle DATE 시분초·TIMESTAMP 소수 초 조건을 문서 대조했다.
- S26: ADD/MODIFY/DROP COLUMN/RENAME COLUMN/RENAME의 대상을 나누었다. SQL 적용 예제 2개는 초기 DDL/입력/명령순서/최종 예상표 fixture를 포함한다.
- 기존 확장: BCNF는 후보키가 아닌 슈퍼키의 정확한 조건으로 기술했다. DECODE NULL 매칭과 단순 CASE의 차이, NVL2에서 0은 비NULL이라는 규칙을 확인했다. 함수 결과를 실제 엔진에서 실행했다는 표현은 없다.
- M02의 한국어 분류축 명칭은 공개 출판사 요약집 PDF 5쪽만 제한 대조했다. Oracle·대학 자료가 그 명명법을 검증했다는 주장은 하지 않는다. 해당 PDF의 다른 정의나 문항은 재사용하지 않았다.

## 통합 담당자에게
- content/supplement-a-sources.json의 sources를 기존 sourceId 중복 없이 sources.json에 통합해야 한다.
- 신규 objective의 scopeStatus는 기존 계약대로 provisional이다. 강의 보강 목적이지 공식 최신 세부범위 검증을 의미하지 않는다.
- 새 문항 독립 검수 전 published로 올리지 않았다. 격리 때문에 새 노트의 회상 세션이 비어 보일 수 있으므로 최종 공개 전에 검수·상태 전환 필요.
- UI/validator/공용 sources.json/앱 assets는 이 담당자가 변경하지 않았다.
- 신규 노트·블록은 앱 화면의 긴 텍스트·도식 가독성 확인이 필요하다.

## 작성 후 실제 점검 결과
- 신규 5노트 각각 회상 3 + 적용 2 확인. 보강 총 35문항 중 SQL fixture 10개에 대해 표시 SQL과 준비 명령/최종 query의 순서 일치 및 예상 결과와 최종 해설표 일치 검사 통과.
- 노트 필수 블록 종류, 모든 회상 문항 참조, ID 중복 검사 통과. 새 정답 ID 분포 a=9,b=8,c=9,d=9. 정답만 유일하게 긴 보기 13/35 (37.1%)로 수치만 기록하며 학습 효과 검증을 의미하지 않는다.
- 공용 전체 validator와 앱 빌드는 통합 담당자가 출처 등록 후 수행한다. 이 담당자는 실제 assets나 UI를 변경·실행하지 않았다.
