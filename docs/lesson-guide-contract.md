# 2026-10-12 추가 해설 자료 계약

기존 콘텐츠/문항/학습 기록을 수정하지 않는 별도 자료다. 원본 63강은 흥달쌤 PDF 자체가 아니다. 원본 PDF 참조는 `tmp/pdfs/three-way-20261005/{section}/page-*.txt` 및 렌더 이미지/실제 PDF로 확인한다.

## 저술 파일

`content/lesson-guides/<lessonId>.json` 한 강의당 하나. 아래 필드는 Kotlin 모델과 일치해야 한다.

```json
{
  "schemaVersion": 1,
  "lessonId": "2-1-03",
  "source": "현재 course-pack의 해당 lesson 객체를 그대로 저장 (실제 JSON 객체)",
  "purpose": "구체적인 사용 상황과 배울 목적",
  "overview": "전체 작업의 종류, 바뀌는 것/유지되는 것을 실제 대상 이름으로 설명",
  "terms": [{"token":"CONSTRAINT","kind":"키워드","meaning":"영어 뜻과 쉬운 의미","role":"이 강의에서 실제로 하는 일"}],
  "pitfalls": ["이 강의에 맞는 비교와 주의"],
  "questions": [{"question":"이 단어는 무엇인가?","answer":"현재 예시와 연결된 짧은 답"}],
  "pdfRefs": [{"sectionId":"2-1","title":"SQL 기본","fromPage":1,"toPage":3,"note":"확인한 원본 PDF 단원/예시 연결. 다른 데이터임을 명시"}],
  "examples": [{
    "exampleId":"기존 예제 ID",
    "why":"이 예제를 사용하는 상황",
    "effect":"조회/입력/수정/삭제/구조 정의/개념 중 무엇인가 + 대상",
    "prerequisites":["원본 표 및 명시적 가정. 추가 데이터는 가상 예시"],
    "steps":[{"id":"read-01","title":"읽을 부분","text":"실제 대상/소속/방향/값을 짚는 해설","codeFocus":[{"needle":"SQL에서 정확히 존재하는 문자열","occurrence":0}],"highlights":["text에 실제 포함된 강조 문자열"],"table":{"title":"학습용 중간표","columns":["열"],"rows":[["값"]]},"focusCells":[],"focusRows":[]}],
    "comparison":"현재 예제에서 헷갈리는 개념과 차이",
    "verification":"문서 대조/독립 검산, 실제 실행 엔진 범위. 미실행은 명시"
  }],
  "checkGuides":[{"checkId":"기존 자기점검 ID","hint":"정답을 포함하지 않는 읽기 출발점","reasoning":"원래 답의 실제 이유를 예시와 연결"}],
  "sourceUrls":["실제로 확인한 공식 문서"],
  "reviewNotes":["불확실하거나 조건이 부족한 원문은 주의 표시"]
}
```

원본 예제 SQL/표/값/순서/답은 변경 금지. source 전체 객체 동일성으로 낡은 해설을 차단한다. 표 셀은 문자열 또는 null. codeFocus는 전체 SQL 원문에서만 찾는다. SQL 없는 예제는 codeFocus=[]이고 개념/표를 설명한다. 기존 steps 복사만으로 완료하지 말고 실제 입력과 중간 판단을 적는다. 원문에 없는 조건을 만들면 가정으로 표시한다. 단계에 SQL 없는 가상 실행 결과를 만들지 않는다. 원본 확인문제와 별도 가상 보충 예제의 정답을 섞지 않는다.

작업 분담: modeling = 1-1/1-2의 16강, basic = 2-1-01~21 + 2-3의 25강, advanced = 2-1-22~25 + 2-2의 22강. 신규 가상 예시는 박강열/유성재/양지훈/박보성/이승현/김현수만 사용. 원본의 이름은 보존.

별도 검토 기록은 `evidence/explanation-upgrade-20261012/<group>-review.json`에 강의별 부족점/조치/미검증을 작성. 설명 길이나 항목 수만으로 품질 통과 판정 금지.

선택 필드: `ExampleGuide.terms`는 해당 예제에만 맞는 용어 목록이다. 강의 전체 용어에 다른 예제의 테이블/제약조건 이름이 있으면 예제별 목록을 우선한다. `supplementalExamples`는 `{example: CourseExample, guide: ExampleGuide}` 목록이며, 원본과 다른 ID 및 가상 보충 예제 표시가 필요하다. 원본 개수/진도에 합산하지 않는다.
