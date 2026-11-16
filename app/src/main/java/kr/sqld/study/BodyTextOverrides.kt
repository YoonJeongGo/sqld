package kr.sqld.study

/**
 * Display-only editorial metadata, matched against the complete unmodified body.
 * Values are excerpts of that body; no SQL, answers, tables or persisted offsets are rewritten.
 * Update the reviewed entry when its source body changes. No fuzzy matching is intentional.
 */
internal object BodyTextOverrides {
    val entries: Map<String, BodyTextOverride> = mapOf(
        // 1-1-01/o
        "학생표를 읽어 필요한 이름·점수를 보여 주는 조회다. 학생표를 만들거나 장정훈의 행을 삭제하는 작업은 아니다. SQL 문법은 뒤 단원에서 배우므로 여기서는 각 단어의 역할부터 함께 읽는다." to BodyTextOverride(
            strong = listOf("조회", "삭제하는 작업은 아니다"),
            inlineCodes = listOf("SQL"),
        ),
        // 1-1-02/o
        "SQL 실행이 아니라 저장 구조를 정하는 설계다. 학생 자체, 과목 자체, 어느 학생이 어느 과목에서 받은 점수라는 세 사실을 나누어 본다." to BodyTextOverride(
            strong = listOf("저장 구조를 정하는 설계", "세 사실"),
        ),
        // 1-1-03/o
        "학생표의 값을 바꾸는 과정이 아니라 설계를 구체화하는 세 단계다. 각 단계의 산출물은 같은 학생 관리 요구를 서로 다른 상세 수준으로 표현한다." to BodyTextOverride(
            strong = listOf("설계를 구체화하는 세 단계", "서로 다른 상세 수준"),
        ),
        // 1-1-04/o
        "학생 데이터를 변경하지 않고 사용자 관점·전체 논리 구조·실제 저장 방법을 나누어 설명한다. 스키마 3단계는 사용 중인 DB를 보는 관점이다." to BodyTextOverride(
            strong = listOf("사용자 관점·전체 논리 구조·실제 저장 방법", "DB를 보는 관점"),
            inlineCodes = listOf("DB"),
        ),
        // 1-1-05/o
        "ERD는 구조와 업무 규칙을 표현한다. 수강표는 학생·과목 사이의 각각의 연결을 한 행에 저장한다. 선만으로 자동 JOIN이나 데이터 입력이 실행되지는 않는다." to BodyTextOverride(
            strong = listOf("구조와 업무 규칙", "각각의 연결을 한 행에 저장"),
            inlineCodes = listOf("ERD", "JOIN"),
        ),
        // 1-1-06/o
        "테이블을 실행하는 과정이 아니라 대상을 구분하는 연습이다. 표 제목·한 행 전체·열 제목의 세 위치를 비교한다." to BodyTextOverride(
            strong = listOf("대상을 구분하는 연습", "표 제목·한 행 전체·열 제목"),
        ),
        // 1-1-07/o
        "학생표의 열 제목·행·허용 규칙을 읽는 개념 학습이다. 학번·이름·학과·학년을 구체적으로 세고 한 행의 값과 구분한다." to BodyTextOverride(
            strong = listOf("학번·이름·학과·학년", "한 행의 값과 구분"),
        ),
        // 1-1-08/o
        "학과 한 곳과 여러 학생의 관계를 해석한다. 학과.학과코드와 학생.학과코드는 이름이 같아도 서로 다른 표의 컬럼이다." to BodyTextOverride(
            strong = listOf("학과 한 곳과 여러 학생", "서로 다른 표의 컬럼"),
            inlineCodes = listOf("학과.학과코드", "학생.학과코드"),
        ),
        // 1-1-09/o
        "수강 한 행을 유일하게 지정할 속성 조합을 정한다. 학번과 과목코드를 함께 쓰는 것은 한 기본키를 두 컬럼으로 구성하는 뜻이다." to BodyTextOverride(
            strong = listOf("유일하게 지정할 속성 조합", "한 기본키를 두 컬럼으로 구성"),
        ),
        // 1-2-01/o
        "릴레이션 구조와 현재 저장값을 구별하는 개념이다. 수학적 관계 모델의 성질을 SQL 조회 결과의 중복·정렬 규칙과 혼동하지 않는다." to BodyTextOverride(
            strong = listOf("릴레이션 구조와 현재 저장값", "중복·정렬 규칙"),
        ),
        // 1-2-02/o
        "키 분류를 확인하는 설계 예제다. 테이블을 만들거나 열을 복사하지 않는다. 유일성·최소성·선택 여부를 차례로 검사한다." to BodyTextOverride(
            strong = listOf("유일성·최소성·선택 여부", "테이블을 만들거나 열을 복사하지 않는다"),
        ),
        // 1-2-03/o
        "새 테이블을 만드는 코드가 아니라 네 입력 후보를 독립적으로 판정하는 개념 예제다. 거부된 후보는 정상 저장된 학생표에 넣지 않는다." to BodyTextOverride(
            strong = listOf("네 입력 후보를 독립적으로 판정", "거부된 후보"),
        ),
        // 1-2-04/o
        "네 요구를 명령 종류로 분류하는 예제다. 나열된 단어는 기능 이름이며 완전한 SQL 실행문이나 순서대로 실행한 결과가 아니다." to BodyTextOverride(
            strong = listOf("명령 종류로 분류", "순서대로 실행한 결과가 아니다"),
        ),
        // 1-2-05/o
        "SQL 실행 예제가 아니라 저장 구조와 이상 현상을 비교한다. 정규화로 표를 나누는 일과 강의실 값을 301→401로 수정하는 일은 서로 다른 변화다." to BodyTextOverride(
            strong = listOf("저장 구조와 이상 현상", "서로 다른 변화"),
        ),
        // 1-2-06/o
        "두 개의 독립된 개념 예제다. 첫 예제는 성적통합을 학생·학과·성적으로 나누고 두 번째 예제는 학생·과목·강사의 후보키를 분석한다. SQL 실행 단계로 가장하지 않는다." to BodyTextOverride(
            strong = listOf("두 개의 독립된 개념 예제", "후보키"),
            paragraphStarts = listOf("SQL 실행 단계로 가장하지 않는다."),
        ),
        // 1-2-07/o
        "원본 SQL은 주문상세를 읽어 합계를 보여 주는 SELECT다. 저장합계는 결과 열 별칭이며 이 SQL만으로 주문표에 값을 저장하지 않는다. 반정규화의 저장·갱신 비용은 별도 가정으로 비교한다." to BodyTextOverride(
            strong = listOf("SELECT", "결과 열 별칭", "값을 저장하지 않는다"),
            paragraphStarts = listOf("반정규화의 저장·갱신 비용은"),
            inlineCodes = listOf("SELECT"),
        ),
        // 2-1-01/o
        "CREATE TABLE은 학생이라는 테이블 하나를 만든다. 학번·이름·학년은 컬럼 정의이며 괄호 안 숫자는 저장 규칙이다. 실제 학생 등록은 INSERT로 별도로 한다." to BodyTextOverride(
            strong = listOf("테이블 하나", "컬럼 정의", "저장 규칙"),
            inlineCodes = listOf("CREATE TABLE", "INSERT"),
        ),
        // 2-1-02/o
        "이 강의 원본 두 예제에는 실행 SQL이 없다. 자료형 비교와 NUMBER(5,2)의 저장 판정을 하는 개념 학습이며 가상의 SQL 실행 단계를 만들지 않는다." to BodyTextOverride(
            strong = listOf("실행 SQL이 없다", "자료형 비교", "저장 판정"),
            inlineCodes = listOf("NUMBER(5,2)"),
        ),
        // 2-1-03/o
        "CREATE TABLE은 시험성적의 번호·이름·점수 세 컬럼과 입력 규칙을 정의한다. 원본의 점수입력 표는 입력을 시도할 값의 목록이며 이미 저장된 성적표가 아니다." to BodyTextOverride(
            strong = listOf("세 컬럼과 입력 규칙", "입력을 시도할 값의 목록", "이미 저장된 성적표가 아니다"),
            inlineCodes = listOf("CREATE TABLE"),
        ),
        // 2-1-04/o
        "ALTER는 학생 구조에 연락처 컬럼을 추가하고 RENAME은 학생이라는 객체 이름을 재학생으로 바꾼다. 두 명의 이름을 수정하거나 새 학생을 넣는 작업이 아니다." to BodyTextOverride(
            strong = listOf("연락처 컬럼을 추가", "객체 이름을 재학생으로 바꾼다"),
            inlineCodes = listOf("ALTER", "RENAME"),
        ),
        // 2-1-05/o
        "INSERT는 이미 있는 학생·합격자 테이블에 행을 추가한다. 뒤의 SELECT는 변경 내용을 조회하는 별도 문장이다. 열 개수나 표 정의는 바꾸지 않는다." to BodyTextOverride(
            strong = listOf("행을 추가", "별도 문장", "열 개수나 표 정의는 바꾸지 않는다"),
            inlineCodes = listOf("INSERT", "SELECT"),
        ),
        // 2-1-06/o
        "SELECT는 성적을 조회한다. 원본 성적의 점수나 컬럼 이름은 바꾸지 않고 조회 결과에 시험점수라는 이름을 붙인다. 설명 순서는 논리적 읽기 순서이며 물리 실행계획은 아니다." to BodyTextOverride(
            strong = listOf("조회 결과", "원본 성적의 점수나 컬럼 이름은 바꾸지 않고", "논리적 읽기 순서"),
            paragraphStarts = listOf("설명 순서는 논리적 읽기 순서이며"),
            inlineCodes = listOf("SELECT"),
        ),
        // 2-1-07/o
        "조건은 고객 행마다 참·거짓을 판정한다. AND는 둘 다 참이어야 하며 OR는 하나라도 참이면 된다. 논리식 괄호는 의미를 정하고 DB가 조건을 물리적으로 평가하는 순서를 약속하지 않는다." to BodyTextOverride(
            strong = listOf("둘 다 참", "하나라도 참", "의미를 정하고"),
            paragraphStarts = listOf("논리식 괄호는 의미를 정하고"),
            inlineCodes = listOf("AND", "OR"),
        ),
        // 2-1-08/o
        "UPDATE는 성적이라는 기존 표의 선택된 행에서 점수 값만 바꾼다. WHERE는 고를 행, SET은 그 행의 어떤 컬럼에 무엇을 넣을지 정한다." to BodyTextOverride(
            strong = listOf("선택된 행에서 점수 값만 바꾼다", "고를 행", "어떤 컬럼에 무엇을 넣을지"),
            inlineCodes = listOf("UPDATE", "WHERE", "SET"),
        ),
        // 2-1-09/o
        "DELETE는 데이터 행을 지운다. 학번·이름·학년 컬럼 정의는 유지한다. ON DELETE CASCADE가 정의된 두 표에서는 부모 행 삭제가 자식 행 삭제로 이어질 수 있다." to BodyTextOverride(
            strong = listOf("데이터 행을 지운다", "컬럼 정의는 유지", "자식 행 삭제"),
            paragraphStarts = listOf("ON DELETE CASCADE가 정의된"),
            inlineCodes = listOf("DELETE", "ON DELETE CASCADE"),
        ),
        // 2-1-10/o
        "바뀔 곳은 최종성적 t이고 값을 가져올 곳은 새성적 s다. MERGE는 결과를 합쳐 보여주는 조회가 아니라 최종성적에 UPDATE와 INSERT를 적용하는 DML이다." to BodyTextOverride(
            strong = listOf("바뀔 곳은 최종성적 t", "값을 가져올 곳은 새성적 s", "DML"),
            inlineCodes = listOf("MERGE", "UPDATE", "INSERT"),
        ),
        // 2-1-11/o
        "IN은 값 목록과 같음을 비교하고 BETWEEN은 양끝을 포함한 범위를 비교한다. LIKE의 밑줄은 한 글자 자리이며 %는 0글자 이상이다. 이 예제들은 조회라 원본을 바꾸지 않는다." to BodyTextOverride(
            strong = listOf("같음을 비교", "양끝을 포함", "한 글자 자리", "0글자 이상"),
            inlineCodes = listOf("IN", "BETWEEN", "LIKE"),
        ),
        // 2-1-12/o
        "DISTINCT는 SELECT에 쓴 전체 열 조합의 중복을 줄인다. ORDER BY는 조회 결과의 순서를 정한다. 원본 학생 행을 삭제하거나 원본값을 수정하지 않는다." to BodyTextOverride(
            strong = listOf("전체 열 조합", "조회 결과의 순서", "원본값을 수정하지 않는다"),
            inlineCodes = listOf("DISTINCT", "SELECT", "ORDER BY"),
        ),
        // 2-1-13/o
        "단일행함수는 각 행의 입력을 받아 값을 계산한다. SELECT 안의 함수는 원본 과목명을 고치지 않는다. 숫자 함수 예제는 실행 SQL 없이 계산 규칙을 비교한다." to BodyTextOverride(
            strong = listOf("각 행의 입력", "원본 과목명을 고치지 않는다", "계산 규칙을 비교"),
            paragraphStarts = listOf("숫자 함수 예제는"),
            inlineCodes = listOf("SELECT"),
        ),
        // 2-1-14/o
        "이 SELECT는 날짜 상수로 네 결과값을 계산한다. 사용자 날짜 테이블을 수정하지 않는다. DUAL은 Oracle에서 상수식을 조회하기 위한 한 행짜리 보조 표다." to BodyTextOverride(
            strong = listOf("네 결과값", "수정하지 않는다", "한 행짜리 보조 표"),
            inlineCodes = listOf("SELECT", "DUAL"),
        ),
        // 2-1-15/o
        "COUNT(*)는 학생 정보 행을 세고 COUNT(점수)·AVG(점수)는 점수가 NULL인 입력을 제외한다. 집계값 0과 조회결과 0행은 서로 다른 상태다." to BodyTextOverride(
            strong = listOf("학생 정보 행", "NULL인 입력을 제외", "집계값 0과 조회결과 0행"),
            inlineCodes = listOf("COUNT(*)", "COUNT(점수)", "AVG(점수)"),
        ),
        // 2-1-16/o
        "NULL과 90의 일반 비교는 UNKNOWN이다. WHERE는 TRUE만 남기므로 NULL 학생을 포함하려면 IS NULL 조건을 따로 결합한다. UNKNOWN과 FALSE는 같은 논리값이 아니다." to BodyTextOverride(
            strong = listOf("UNKNOWN", "TRUE만 남기므로", "같은 논리값이 아니다"),
            inlineCodes = listOf("NULL", "WHERE", "IS NULL", "FALSE"),
        ),
        // 2-1-17/o
        "COALESCE는 NULL이 아닌 첫 값을 반환하고 NULLIF는 두 값이 같으면 NULL을 반환한다. SELECT 안의 대체는 표시·계산에 사용되며 원본 NULL을 저장 변경하지 않는다." to BodyTextOverride(
            strong = listOf("NULL이 아닌 첫 값", "두 값이 같으면 NULL", "원본 NULL을 저장 변경하지 않는다"),
            inlineCodes = listOf("COALESCE", "NULLIF", "SELECT"),
        ),
        // 2-1-18/o
        "CASE는 행의 값을 보고 반환값을 고르는 표현식이다. SELECT 안에서는 원본 점수를 수정하지 않는다. 먼저 맞은 WHEN이 결과를 결정하므로 조건 순서와 NULL 분기를 함께 읽는다." to BodyTextOverride(
            strong = listOf("반환값을 고르는 표현식", "원본 점수를 수정하지 않는다", "먼저 맞은 WHEN"),
            inlineCodes = listOf("CASE", "SELECT", "NULL"),
        ),
        // 2-1-19/o
        "집계는 여러 행에서 요약값을 만든다. COUNT의 괄호 안이 *, 점수, DISTINCT 점수 중 무엇인지에 따라 세는 대상이 달라진다." to BodyTextOverride(
            strong = listOf("요약값", "세는 대상이 달라진다"),
            inlineCodes = listOf("COUNT", "DISTINCT 점수"),
        ),
        // 2-1-20/o
        "GROUP BY 학과는 같은 학과값의 학생을 묶는다. COUNT(*)는 각 묶음의 행수를 센다. 저장된 학생 5행은 그대로이며 조회 결과만 학과별 2행이 된다." to BodyTextOverride(
            strong = listOf("같은 학과값", "각 묶음의 행수", "저장된 학생 5행은 그대로"),
            inlineCodes = listOf("GROUP BY", "COUNT(*)"),
        ),
        // 2-1-21/o
        "WHERE는 집계에 들어갈 학생 행을 고르고 HAVING은 집계된 학과 그룹을 고른다. 논리적 풀이 순서로 필터→그룹→평균→그룹 조건을 추적한다." to BodyTextOverride(
            strong = listOf("학생 행", "학과 그룹", "필터→그룹→평균→그룹 조건"),
            inlineCodes = listOf("WHERE", "HAVING"),
        ),
        // 2-1-22/o
        "조회예요. 학생·수강의 저장값은 그대로이고, 학번이 맞는 행 조합의 이름·과목을 결과에 붙여요. 두 번째 예제는 성적.점수를 등급의 하한·상한과 비교해요." to BodyTextOverride(
            strong = listOf("조회", "학번이 맞는 행 조합", "저장값은 그대로"),
            paragraphStarts = listOf("두 번째 예제는"),
            inlineCodes = listOf("성적.점수"),
        ),
        // 2-1-23/o
        "조회예요. FULL은 회원·주문의 미일치를 양쪽에서 보존하고, LEFT는 학생 쪽 미일치를 보존해요. NULL을 붙이는 곳은 조회 결과의 상대편 칸이며 원본 데이터 수정이 아니에요." to BodyTextOverride(
            strong = listOf("양쪽에서 보존", "학생 쪽 미일치를 보존", "조회 결과의 상대편 칸"),
            inlineCodes = listOf("FULL", "LEFT", "NULL"),
        ),
        // 2-1-24/o
        "두 예제 모두 조회예요. CROSS는 학생2명과 과목3개의 모든 조합을 만들고, SELF는 사원표를 직원 e와 관리자 m이라는 두 역할로 읽어요." to BodyTextOverride(
            strong = listOf("모든 조합", "두 역할"),
            inlineCodes = listOf("CROSS", "SELF"),
        ),
        // 2-1-25/o
        "조회예요. USING은 지정한 동명 열을 비교하고, NATURAL은 양쪽의 모든 동명 열을 비교해요. R·S의 코드는 같아도 이름이 다르면 NATURAL 결과가 없어요." to BodyTextOverride(
            strong = listOf("지정한 동명 열", "모든 동명 열", "이름이 다르면 NATURAL 결과가 없어요"),
            inlineCodes = listOf("USING", "NATURAL"),
        ),
        // 2-2-01/o
        "조회예요. 안쪽 성적표에서 평균80이라는 한 값을 만들고, 바깥 성적표의 각 점수를 그 기준과 비교해요. 점수를 수정하지 않아요." to BodyTextOverride(
            strong = listOf("평균80이라는 한 값", "각 점수를 그 기준과 비교", "점수를 수정하지 않아요"),
        ),
        // 2-2-02/o
        "조회예요. MAX가 돌려주는 기준 한 값과 바깥 결과의 행 수는 별개예요. 두 번째 예제는 안쪽0행을 한 값 자리에서 NULL로 읽어요." to BodyTextOverride(
            strong = listOf("기준 한 값", "바깥 결과의 행 수", "NULL로 읽어요"),
            paragraphStarts = listOf("두 번째 예제는"),
            inlineCodes = listOf("MAX", "NULL"),
        ),
        // 2-2-03/o
        "조회예요. 사원의 급여를 개발부 급여250·300 목록과 각각 비교해요. ANY와 ALL 두 SELECT는 독립 조회이며 첫 결과가 다음 입력을 바꾸지 않아요." to BodyTextOverride(
            strong = listOf("목록과 각각 비교", "독립 조회", "다음 입력을 바꾸지 않아요"),
            inlineCodes = listOf("ANY", "ALL", "SELECT"),
        ),
        // 2-2-04/o
        "조회예요. 안쪽에서 학과·최고점의 두 열을 만들고 바깥의 같은 두 열을 같은 순서의 한 쌍으로 비교해요." to BodyTextOverride(
            strong = listOf("두 열", "같은 순서의 한 쌍"),
        ),
        // 2-2-05/o
        "세 예제 모두 조회예요. 상관은 먼저 바깥 행을 정하고 그 값으로 안쪽 조건을 읽어요. 인라인뷰 a는 조회 결과를 부르는 이름이며 영구 테이블을 만들지 않아요." to BodyTextOverride(
            strong = listOf("바깥 행", "그 값으로 안쪽 조건", "영구 테이블을 만들지 않아요"),
            paragraphStarts = listOf("인라인뷰 a는"),
        ),
        // 2-2-06/o
        "조회예요. R·S의 번호 한 열을 행 방향으로 결합해요. JOIN처럼 서로 다른 표의 컬럼을 옆으로 붙이지 않아요." to BodyTextOverride(
            strong = listOf("행 방향으로 결합", "컬럼을 옆으로 붙이지 않아요"),
            inlineCodes = listOf("JOIN"),
        ),
        // 2-2-07/o
        "조회 집계예요. 매출4행은 그대로 있고 조회 결과에 상세4줄·지역소계2줄·전체1줄이 생겨요. ROLLUP의 열 순서가 소계 종류를 결정해요." to BodyTextOverride(
            strong = listOf("매출4행은 그대로", "상세4줄·지역소계2줄·전체1줄", "열 순서"),
            inlineCodes = listOf("ROLLUP"),
        ),
        // 2-2-08/o
        "조회 집계예요. CUBE는 지역·과목의 가능한 그룹 조합을, GROUPING SETS는 괄호에 직접 요청한 조합만 만들어요." to BodyTextOverride(
            strong = listOf("가능한 그룹 조합", "직접 요청한 조합만"),
            inlineCodes = listOf("CUBE", "GROUPING SETS"),
        ),
        // 2-2-09/o
        "조회 결과의 집계 수준을 표시해요. 원본 매출의 지역NULL·금액200과 전체합계300의 지역NULL은 원인이 달라요." to BodyTextOverride(
            strong = listOf("집계 수준", "원인이 달라요"),
            inlineCodes = listOf("NULL"),
        ),
        // 2-2-10/o
        "조회 계산이에요. 성적4행을 유지하고 학과평균이라는 결과 열을 덧붙여요. GROUP BY처럼 학과2줄로 줄이지 않아요." to BodyTextOverride(
            strong = listOf("성적4행을 유지", "결과 열", "학과2줄로 줄이지 않아요"),
            inlineCodes = listOf("GROUP BY"),
        ),
        // 2-2-11/o
        "조회 계산이에요. 이승현90·박강열90·김현수80·박상현70의 행을 유지하면서R·D·RN세 결과 열을 붙여요." to BodyTextOverride(
            strong = listOf("행을 유지", "세 결과 열"),
        ),
        // 2-2-12/o
        "조회 계산이에요. 입금 원본은 그대로이며 행누적·값누적·이동합을 계산해 보여줘요.20두행을 포함하는 기준이 다르므로30과50이갈려요." to BodyTextOverride(
            strong = listOf("원본은 그대로", "포함하는 기준", "30과50"),
            inlineCodes = listOf("행누적", "값누적", "이동합"),
        ),
        // 2-2-13/o
        "조회 계산이에요. 번호 1·2·3의 금액 10·20·30을 수정하지 않고 이전·다음·전체 마지막 값을 표시해요. 분포 예제는 별도의 10·20·20·30 데이터예요." to BodyTextOverride(
            strong = listOf("이전·다음·전체 마지막 값", "별도의 10·20·20·30 데이터"),
            paragraphStarts = listOf("분포 예제는"),
        ),
        // 2-2-14/o
        "조회예요. ROW_NUMBER 예제는 점수·학번순 번호를 안쪽에서 만들고 바깥에서 1·2만 골라요. ROWNUM 예제는 정렬된 인라인뷰의 앞 두 행을 골라요." to BodyTextOverride(
            strong = listOf("안쪽에서 만들고", "바깥에서 1·2만", "정렬된 인라인뷰의 앞 두 행"),
            inlineCodes = listOf("ROW_NUMBER", "ROWNUM"),
        ),
        // 2-2-15/o
        "조회예요. 관리자번호 NULL을 시작점으로 잡고, 방금 방문한 사원의 사번과 다음 후보의 관리자번호를 비교해요. 원본을 조직순서로 다시 저장하지 않아요." to BodyTextOverride(
            strong = listOf("시작점", "방금 방문한 사원의 사번", "다음 후보의 관리자번호"),
            inlineCodes = listOf("NULL"),
        ),
        // 2-2-16/o
        "조회예요. WHERE로 2번 유성재의 표시만 빼도 이미 탐색한 4번 노우성은 남아요. 다른 예제는 노우성 4번을 시작점으로 4→2→1을 따라가요." to BodyTextOverride(
            strong = listOf("표시만 빼도", "이미 탐색한 4번 노우성은 남아요", "4→2→1"),
            paragraphStarts = listOf("다른 예제는"),
            inlineCodes = listOf("WHERE"),
        ),
        // 2-2-17/o
        "조회 변환이에요. PIVOT 결과 DB·JAVA열은 출력 모양이며 원본 성적표에 ALTER로 추가되는 열이 아니에요. UNPIVOT은 별도 가로성적표를 입력으로 써요." to BodyTextOverride(
            strong = listOf("출력 모양", "추가되는 열이 아니에요", "별도 가로성적표"),
            paragraphStarts = listOf("UNPIVOT은 별도"),
            inlineCodes = listOf("PIVOT", "ALTER", "UNPIVOT"),
        ),
        // 2-2-18/o
        "첫 예제는 조회 필터예요. 정규식에 맞는 과목명만 보여주고 저장 문자열을 수정하지 않아요. 두 번째는 SQL 없는 패턴 판정 연습으로 코드를 억지로 만들지 않아요." to BodyTextOverride(
            strong = listOf("조회 필터", "저장 문자열을 수정하지 않아요", "SQL 없는 패턴 판정"),
            paragraphStarts = listOf("두 번째는"),
        ),
        // 2-3-01/o
        "일반 뷰는 SELECT 정의를 가진 객체다. CREATE VIEW는 조회 정의를 만들고 뒤 SELECT는 그 정의로 현재 성적을 보여준다. WITH CHECK OPTION은 그 뷰를 통한 변경이 뷰 조건을 벗어나지 않도록 검사한다." to BodyTextOverride(
            strong = listOf("SELECT 정의", "현재 성적", "뷰 조건을 벗어나지 않도록"),
            paragraphStarts = listOf("WITH CHECK OPTION은"),
            inlineCodes = listOf("CREATE VIEW", "SELECT", "WITH CHECK OPTION"),
        ),
        // 2-3-02/o
        "트랜잭션은 함께 확정하거나 취소할 작업 묶음이다. UPDATE는 현재 잔액을 바꾸고 SAVEPOINT는 취소 기준을 기억하며 COMMIT은 남은 변경을 확정한다." to BodyTextOverride(
            strong = listOf("함께 확정하거나 취소할 작업 묶음", "취소 기준", "남은 변경을 확정"),
            inlineCodes = listOf("UPDATE", "SAVEPOINT", "COMMIT"),
        ),
        // 2-3-03/o
        "GRANT·REVOKE는 학생 데이터가 아니라 계정의 권한을 바꾼다. ON 뒤 객체, TO/FROM 뒤 사용자를 찾고 어떤 작업 권한을 나열했는지 읽는다." to BodyTextOverride(
            strong = listOf("계정의 권한", "객체", "사용자"),
            inlineCodes = listOf("GRANT", "REVOKE", "ON", "TO/FROM"),
        ),
        // 2-3-04/o
        "관계대수 σ는 행 선택,π는 열 투영이다. SQL의 SELECT라는 단어와 이름이 같다고 σ를 SELECT 목록으로 읽지 않는다. 디비전 SQL은 바깥 학생의 학번에 연결해 부족한 필수과목이 없는지를 확인한다." to BodyTextOverride(
            strong = listOf("σ는 행 선택", "π는 열 투영", "부족한 필수과목이 없는지"),
            paragraphStarts = listOf("디비전 SQL은"),
            inlineCodes = listOf("SELECT"),
        ),
        // 1-1-01/e0s1
        "박상현의 컴퓨터는 조건과 같아 참, 장정훈의 전자는 달라 거짓, 박보성의 컴퓨터는 같아 참이다. 참인 두 행만 조회 후보에 남긴다. 장정훈의 원본 행은 유지된다." to BodyTextOverride(
            strong = listOf("참인 두 행만", "원본 행은 유지된다"),
        ),
        // 1-1-02/e0s0
        "학생은 사람을 관리하는 대상이고 과목은 수업을 관리하는 대상이다. 수강하고 점수를 받는다는 말은 두 대상 사이의 연결에 붙는 사실이다. 현실의 모든 정보를 저장하지 않고 이 업무에 필요한 사실을 뽑는 것이 추상화다." to BodyTextOverride(
            strong = listOf("학생", "과목", "연결에 붙는 사실", "이 업무에 필요한 사실을 뽑는 것"),
            paragraphStarts = listOf("현실의 모든 정보를 저장하지 않고"),
        ),
        // 1-1-03/e0s3
        "NUMBER(6)의 6은 학번 숫자의 정밀도 제한이다. 학생 여섯 명이나 자동 일련번호라는 뜻이 아니다. 이 예시의 NUMBER(6)은 소수 자릿수 0으로 취급되어 소수 입력은 반올림될 수 있고 반올림한 값이 정밀도를 넘으면 오류다. VARCHAR2(30 CHAR)의 30은 이름 문자열의 문자 수 기준 길이다." to BodyTextOverride(
            strong = listOf("숫자의 정밀도 제한", "자동 일련번호라는 뜻이 아니다", "반올림한 값이 정밀도를 넘으면 오류", "문자 수 기준 길이"),
            paragraphStarts = listOf("VARCHAR2(30 CHAR)의"),
            inlineCodes = listOf("NUMBER(6)", "VARCHAR2(30 CHAR)"),
        ),
        // 1-1-04/e0s3
        "파일·데이터 페이지·인덱스는 저장하고 찾는 방법이다. 인덱스를 바꾸어도 교수에게 이름·점수를 계속 제공하면 물리적 변경으로부터 논리 구조를 분리한 것이다. 학생표를 분해한 뒤 같은 조회 관점을 유지하는 것은 논리적 독립성 사례다." to BodyTextOverride(
            strong = listOf("저장하고 찾는 방법", "물리적 변경으로부터 논리 구조를 분리", "논리적 독립성 사례"),
            paragraphStarts = listOf("학생표를 분해한 뒤"),
        ),
        // 1-1-05/e0s2
        "(1001,C01)은 양지훈-DB 연결 하나다. (1001,C02)는 같은 학생의 다른 수강이고 (1002,C01)은 다른 학생의 DB 수강이다. 학번 하나나 과목코드 하나의 중복은 허용하되 두 값의 조합으로 연결을 구별한다." to BodyTextOverride(
            strong = listOf("양지훈-DB 연결 하나", "중복은 허용", "두 값의 조합"),
        ),
        // 1-1-06/e0s1
        "(1002, 양지훈, 전자)는 특정 학생 인스턴스 한 건이다. 양지훈이라는 이름만이 아니라 학번과 학과까지 묶어서 한 행이다. 같은 이름이 생겨도 학번으로 다른 학생인지 판단한다." to BodyTextOverride(
            strong = listOf("인스턴스 한 건", "학번과 학과까지 묶어서 한 행", "학번으로"),
        ),
        // 1-1-07/e0s2
        "학년에는 지금 2·3·4가 보인다. 허용 규칙을 1·2·3·4로 정했다면 현재 학생이 없어도 1은 허용된다. 반대로 표에 없다는 이유만으로 9를 넣어도 되는 것은 아니다." to BodyTextOverride(
            strong = listOf("허용된다", "표에 없다는 이유만으로 9를 넣어도 되는 것은 아니다"),
        ),
        // 1-1-08/e0s1
        "학생.학과코드가 참조하는 쪽인 FK다. 양지훈 1001의 D01, 양선규 1002의 D01을 학과표 D01과 각각 맞춘다. 학생.학번 1001과 1002는 달라 두 학생이며 FK D01의 반복은 이 1:N 설계에서 허용된다." to BodyTextOverride(
            strong = listOf("두 학생", "FK D01의 반복"),
            inlineCodes = listOf("학생.학과코드", "학생.학번"),
        ),
        // 1-1-09/e0s3
        "학번+과목코드는 문자열 덧셈이 아니라 두 속성의 조합이라는 표시다. 기본키를 이 조합으로 정하면 기본키 제약 하나가 두 컬럼을 포함한다. 두 컬럼이 각각 단독으로 유일해야 한다는 뜻이 아니다." to BodyTextOverride(
            strong = listOf("두 속성의 조합", "기본키 제약 하나", "각각 단독으로 유일해야 한다는 뜻이 아니다"),
        ),
        // 1-2-01/e0s2
        "1001과 1003의 학과는 모두 컴퓨터지만 학번과 이름이 다르다. 한 컬럼값이 같은 것과 행 전체가 같은 것은 다르므로 서로 다른 튜플이다." to BodyTextOverride(
            strong = listOf("한 컬럼값이 같은 것", "행 전체가 같은 것", "서로 다른 튜플"),
        ),
        // 1-2-02/e0s3
        "(학번,이름)에서 이름을 빼도 학번만으로 박강열을 구별한다. 따라서 이 조합은 유일성은 만족해 슈퍼키지만 최소성이 없어 후보키가 아니다. 반면 학과코드 D01은 두 학생에게 있어 학생 식별용 키가 아니다." to BodyTextOverride(
            strong = listOf("유일성은 만족", "최소성이 없어 후보키가 아니다", "학생 식별용 키가 아니다"),
            paragraphStarts = listOf("반면 학과코드 D01은"),
        ),
        // 1-2-03/e0s3
        "학생 쪽 D99를 부모 학과표의 D01·D02와 비교하면 일치하는 코드가 없다. 따라서 거부다. 학생 입력이 D99 학과를 자동으로 만드는 것은 아니다." to BodyTextOverride(
            strong = listOf("학생 쪽 D99", "부모 학과표", "일치하는 코드가 없다", "자동으로 만드는 것은 아니다"),
        ),
        // 1-2-04/e0s4
        "DELETE는 조건에 맞는 행을 지우는 DML, DROP은 객체를 없애는 DDL, TRUNCATE는 구조를 유지하면서 모든 행을 비우는 DDL이다. DDL이 구조만 다루어 데이터를 절대로 건드리지 않는다고 외우면 TRUNCATE에서 막힌다." to BodyTextOverride(
            strong = listOf("조건에 맞는 행", "객체를 없애는", "구조를 유지하면서 모든 행을 비우는"),
            paragraphStarts = listOf("DDL이 구조만 다루어"),
            inlineCodes = listOf("DELETE", "DROP", "TRUNCATE"),
        ),
        // 1-2-05/e0s1
        "가상 변경 시도: 박보성 행만 301→401로 바꾸고 유성재 행을 301에 남겨 두면 같은 C01의 방이 둘로 갈린다. 이 표는 오류 상태를 설명한 중간표이며 올바른 최종 결과가 아니다." to BodyTextOverride(
            strong = listOf("301→401", "301에 남겨 두면", "오류 상태", "올바른 최종 결과가 아니다"),
        ),
        // 1-2-06/e0s1
        "1001이 DB를 듣든 JAVA를 듣든 이름은 이승현, 학과코드는 D01이다. 이 둘은 키 일부인 학번으로 정해진다. 2NF를 위해 성적에는 학번·과목·점수를 남기고 학생 사실을 분리한다." to BodyTextOverride(
            strong = listOf("키 일부인 학번", "학번·과목·점수", "학생 사실을 분리"),
            inlineCodes = listOf("2NF"),
        ),
        // 1-2-07/e0s3
        "AS 저장합계는 합계 결과 열을 저장합계라는 이름으로 보여 준다는 뜻이다. 실제 금액 컬럼을 이름 변경하거나 저장하는 명령이 아니다. ORDER BY 주문번호로101 다음102 순서를 지정한다." to BodyTextOverride(
            strong = listOf("결과 열", "실제 금액 컬럼을 이름 변경하거나 저장하는 명령이 아니다", "101 다음102"),
            paragraphStarts = listOf("ORDER BY 주문번호로"),
            inlineCodes = listOf("AS 저장합계", "ORDER BY 주문번호"),
        ),
        // 2-1-01/e0s2
        "DEFAULT 1은 학년을 생략한 입력의 기본값을 1로 정한다. CHECK는 저장할 학년이 1~4 범위인지 검사한다. 학년 NULL은 비교가 UNKNOWN이므로 CHECK만으로 금지되지 않는다." to BodyTextOverride(
            strong = listOf("입력의 기본값", "1~4 범위", "CHECK만으로 금지되지 않는다"),
            paragraphStarts = listOf("학년 NULL은"),
            inlineCodes = listOf("DEFAULT 1", "CHECK", "NULL", "UNKNOWN"),
        ),
        // 2-1-02/e1s1
        "123.45는 정수 3자리·소수 2자리여서 저장 가능하다. 1234.56은 정수부가 4자리여서 범위를 넘는다. 12.345는 소수 셋째 자리 5를 반올림해 12.35가 되고 그 값은 범위 안이다." to BodyTextOverride(
            strong = listOf("저장 가능", "범위를 넘는다", "반올림해 12.35", "범위 안"),
        ),
        // 2-1-03/e0s3
        "장정훈의 점수가 NULL이면 범위 비교는 알 수 없음(UNKNOWN)이다. CHECK만 있다면 거부하지 않지만, 실제 SQL에는 점수 NOT NULL도 있어 입력을 거부한다. UNKNOWN을 FALSE라고 바꾸어 외우지 않는다." to BodyTextOverride(
            strong = listOf("알 수 없음(UNKNOWN)", "NOT NULL도 있어 입력을 거부", "FALSE라고 바꾸어 외우지 않는다"),
            inlineCodes = listOf("NULL", "CHECK", "NOT NULL"),
        ),
        // 2-1-04/e0s1
        "ADD 연락처는 이름 뒤에 연락처 항목을 만든다. 기본값이 없고 NULL을 허용하므로 두 기존 학생의 새 연락처 칸은 NULL이다. 이름과 학번은 그대로 둔다." to BodyTextOverride(
            strong = listOf("연락처 항목", "새 연락처 칸은 NULL", "이름과 학번은 그대로"),
            inlineCodes = listOf("ADD 연락처", "NULL"),
        ),
        // 2-1-05/e0s1
        "컬럼 목록의 첫 학번에는 첫 값 1003, 둘째 이름에는 문자값 박강열, 셋째 학년에는 숫자 1이 들어간다. 쉼표로 나눈 위치를 하나씩 대응시킨다." to BodyTextOverride(
            strong = listOf("학번에는 첫 값 1003", "이름에는 문자값 박강열", "학년에는 숫자 1", "위치를 하나씩 대응"),
        ),
        // 2-1-06/e0s2
        "남은 두 행에서 이름과 점수만 고른다. AS 시험점수는 결과 머리글이고 성적.점수의 원래 정의는 그대로다. 새 시험점수 컬럼을 테이블에 저장하는 ALTER가 아니다." to BodyTextOverride(
            strong = listOf("결과 머리글", "원래 정의는 그대로", "테이블에 저장하는 ALTER가 아니다"),
            inlineCodes = listOf("AS 시험점수", "성적.점수", "ALTER"),
        ),
        // 2-1-07/e1s2
        "C가 거짓인데도 원래 식은 A가 참이라 통과한다. (A OR B) AND C는 C도 필수로 요구해 탈락한다. 이것은 조건의 의미 비교이지 엔진의 평가 시각 측정이 아니다." to BodyTextOverride(
            strong = listOf("A가 참이라 통과", "C도 필수로 요구해 탈락", "조건의 의미 비교"),
            paragraphStarts = listOf("이것은 조건의 의미 비교이지"),
            inlineCodes = listOf("(A OR B) AND C"),
        ),
        // 2-1-08/e0s1
        "SET 점수=95는 1002번 행의 성적.점수에 95를 넣는다. 이전 70과 95가 같은지 묻는 식이 아니다. 학번 1002와 이름 유성재는 SET에 적지 않아 유지한다." to BodyTextOverride(
            strong = listOf("성적.점수에 95를 넣는다", "같은지 묻는 식이 아니다", "유지한다"),
            inlineCodes = listOf("SET 점수=95", "성적.점수"),
        ),
        // 2-1-09/e1s1
        "수강의 (1001,C02), (1002,C02)는 지울 부모C02를 가리켜 연쇄 삭제된다. (1001,C01)은 다른 부모C01을 가리키므로 유지된다." to BodyTextOverride(
            strong = listOf("C02를 가리켜 연쇄 삭제", "다른 부모C01을 가리키므로 유지"),
        ),
        // 2-1-10/e0s2
        "SET t.점수 = s.점수는 김현수의 새성적 점수 95를 최종성적 점수 칸에 넣는다. 왼쪽의 이전 70이 95로 바뀐다. 학번과 이름은 SET에 없으므로 유지한다." to BodyTextOverride(
            strong = listOf("새성적 점수 95", "최종성적 점수 칸", "이전 70이 95로 바뀐다", "학번과 이름은 SET에 없으므로 유지"),
            inlineCodes = listOf("SET t.점수 = s.점수"),
        ),
        // 2-1-11/e1s0
        "LIKE '____'의 작은따옴표 안에는 밑줄이 네 개다. 밑줄 한 개가 정확히 한 글자를 받으므로 첫째부터 넷째 자리까지 있어야 하고 다섯째 자리는 허용하지 않는다." to BodyTextOverride(
            strong = listOf("밑줄이 네 개", "정확히 한 글자", "다섯째 자리는 허용하지 않는다"),
            inlineCodes = listOf("LIKE '____'"),
        ),
        // 2-1-12/e0s1
        "(컴퓨터,2) 두 개는 하나가 되고 (컴퓨터,4)는 학년이 다르므로 별도로 남는다. (전자,2)는 학과가 달라 별도다. 학년 2라는 이유만으로 모두 합치지 않는다." to BodyTextOverride(
            strong = listOf("(컴퓨터,2) 두 개는 하나", "학년이 다르므로 별도로", "학과가 달라 별도"),
        ),
        // 2-1-13/e1s0
        "수직선에서 -2 < -1.2 < -1이다. CEIL은 입력 이상인 가장 작은 정수 -1, FLOOR는 입력 이하인 가장 큰 정수 -2를 고른다." to BodyTextOverride(
            strong = listOf("입력 이상인 가장 작은 정수 -1", "입력 이하인 가장 큰 정수 -2"),
            inlineCodes = listOf("CEIL", "FLOOR"),
        ),
        // 2-1-14/e0s1
        "9월 28일에 하루를 더하면 9월 29일이다. 한 달을 더하면 10월 28일이다. 여기서 두 식의 숫자 1은 같아도 연산의 단위가 다르다." to BodyTextOverride(
            strong = listOf("하루를 더하면 9월 29일", "한 달을 더하면 10월 28일", "연산의 단위가 다르다"),
        ),
        // 2-1-15/e0s0
        "(1002, 양지훈, NULL)도 학번·이름·점수로 된 한 행이다. 그래서 COUNT(*)에는 포함한다. 다만 점수값은 없어 COUNT(점수)의 대상에서는 빠진다." to BodyTextOverride(
            strong = listOf("한 행", "COUNT(*)에는 포함", "COUNT(점수)의 대상에서는 빠진다"),
            inlineCodes = listOf("NULL", "COUNT(*)", "COUNT(점수)"),
        ),
        // 2-1-16/e0s1
        "IS NULL은 양선규에게 참이다. 앞 조건 UNKNOWN과 OR로 결합하면 UNKNOWN OR TRUE가 TRUE가 되어 통과한다. 박강열은 FALSE OR FALSE여서 제외한다." to BodyTextOverride(
            strong = listOf("양선규에게 참", "UNKNOWN OR TRUE가 TRUE", "FALSE OR FALSE여서 제외"),
            inlineCodes = listOf("IS NULL", "OR"),
        ),
        // 2-1-17/e0s2
        "COALESCE(AVG(점수),0)는 AVG가 NULL을 제외하고 (90+70)/2=80을 만든다. 80은 NULL이 아니므로 바깥 COALESCE가 0으로 바꾸지 않는다." to BodyTextOverride(
            strong = listOf("NULL을 제외", "(90+70)/2=80", "0으로 바꾸지 않는다"),
            inlineCodes = listOf("COALESCE(AVG(점수),0)", "AVG"),
        ),
        // 2-1-18/e0s1
        "한창주 95는 >=90이 참이므로A다. 95>=80도 참이지만 이미 앞에서 결과가 정해졌다. 양지훈 85는 >=90이 거짓이고 >=80이 참이어서B다." to BodyTextOverride(
            strong = listOf("이미 앞에서 결과가 정해졌다", ">=90이 거짓이고 >=80이 참"),
            inlineCodes = listOf(">=90", ">=80"),
        ),
        // 2-1-19/e0s0
        "COUNT(*)는 김현수·노우성·박보성·이승현 네 행을 센다. COUNT(점수)는NULL을 뺀 90,90,70 세 입력이다. COUNT(DISTINCT 점수)는 중복 90을 합쳐 90,70 두 종류다." to BodyTextOverride(
            strong = listOf("네 행", "세 입력", "두 종류"),
            inlineCodes = listOf("COUNT(*)", "COUNT(점수)", "COUNT(DISTINCT 점수)"),
        ),
        // 2-1-20/e0s1
        "컴퓨터 그룹은 학생 정보 세 행이므로 COUNT(*)=3, 전자 그룹은 두 행이므로 2다. 컴퓨터라는 단어의 글자 수나 학과 열의 개수를 세지 않는다." to BodyTextOverride(
            strong = listOf("학생 정보 세 행", "COUNT(*)=3", "두 행이므로 2"),
            inlineCodes = listOf("COUNT(*)"),
        ),
        // 2-1-21/e0s2
        "컴퓨터는 160÷2=80이고 80>=75가참이다. 전자는 140÷2=70이고 70>=75가거짓이다. HAVING은 학생 한 명의 점수를 지우는 대신 전자라는 요약그룹을 제외한다." to BodyTextOverride(
            strong = listOf("80>=75가참", "70>=75가거짓", "전자라는 요약그룹을 제외"),
            paragraphStarts = listOf("HAVING은 학생 한 명의"),
            inlineCodes = listOf("HAVING"),
        ),
        // 2-1-22/e0s1
        "s.학번=e.학번은 비교예요. 유성재 1001은 수강 1001/DB와 1001/JAVA 두 행 각각에 참이라 두 조합이 생겨요." to BodyTextOverride(
            strong = listOf("비교", "두 행 각각에 참", "두 조합"),
            inlineCodes = listOf("s.학번=e.학번"),
        ),
        // 2-1-23/e1s3
        "박상현은 COUNT(*) 2·COUNT(e.과목) 2예요. 한창주는 행은 1이지만 과목값은 NULL이라 COUNT(*) 1·COUNT(e.과목) 0이에요." to BodyTextOverride(
            strong = listOf("행은 1", "과목값은 NULL", "COUNT(*) 1·COUNT(e.과목) 0"),
            inlineCodes = listOf("COUNT(*)", "COUNT(e.과목)"),
        ),
        // 2-1-24/e1s0
        "FROM 사원 e에서 e는 직원 역할, LEFT JOIN 사원 m에서 m은 관리자 후보 역할이에요. 이름이 같은 컬럼도 e.이름과 m.이름을 구별해요." to BodyTextOverride(
            strong = listOf("직원 역할", "관리자 후보 역할", "e.이름과 m.이름을 구별"),
            inlineCodes = listOf("FROM 사원 e", "LEFT JOIN 사원 m", "e.이름", "m.이름"),
        ),
        // 2-1-25/e1s1
        "코드는 1=1로 참이지만 이름은 박강열=박보성으로 거짓이에요. 두 조건을 모두 만족해야 하므로 이 쌍은 연결되지 않아요." to BodyTextOverride(
            strong = listOf("1=1로 참", "박강열=박보성으로 거짓", "두 조건을 모두 만족"),
        ),
        // 2-2-01/e0s2
        "양지훈 90>80은 참, 김현수 70>80과 유성재 80>80은 거짓이에요. >에는 같음을 포함하지 않아요." to BodyTextOverride(
            strong = listOf("90>80", "80>80", "같음을 포함하지 않아요"),
        ),
        // 2-2-02/e0s2
        "안쪽 기준은 1행이지만 조건을 만족한 바깥은 2행이에요. 학번 1001 박보성, 1002 노우성순으로 표시해요." to BodyTextOverride(
            strong = listOf("안쪽 기준은 1행", "바깥은 2행"),
        ),
        // 2-2-03/e0s2
        "300은 300보다 크지 않아서 ALL에 실패해요. 280도 300 비교에서 실패해요. 350만 두 비교가 모두 참이라 남아요." to BodyTextOverride(
            strong = listOf("300보다 크지 않아서", "두 비교가 모두 참", "350만"),
            inlineCodes = listOf("ALL"),
        ),
        // 2-2-04/e0s2
        "김현수 (전자,80)는 전자 기준쌍과 같아서 참이고, 박상현 (전자,70)은 거짓이에요. 점수 80이 기준 목록 어딘가에 있다는 것만으로는 충분하지 않아요." to BodyTextOverride(
            strong = listOf("전자 기준쌍과 같아서 참", "박상현 (전자,70)은 거짓", "충분하지 않아요"),
        ),
        // 2-2-05/e0s0
        "현재 o행을 학번 1001 유성재로 잡으면 o.학과=컴퓨터, o.점수=90이에요. o·i는 같은 성적표의 서로 다른 조회 역할이에요." to BodyTextOverride(
            strong = listOf("현재 o행", "o.학과=컴퓨터", "o.점수=90", "서로 다른 조회 역할"),
            inlineCodes = listOf("o.학과", "o.점수"),
        ),
        // 2-2-06/e0s1
        "UNION은 중복 발생을 하나로 줄여 1·2·3·4의 4행이에요. UNION ALL은 발생수 1+2+2+1=6행을 유지해요." to BodyTextOverride(
            strong = listOf("중복 발생을 하나로", "4행", "6행을 유지"),
            inlineCodes = listOf("UNION", "UNION ALL"),
        ),
        // 2-2-07/e0s2
        "부산은 과목을 구별하지 않아 100+200=300, 서울은 300+400=700이에요. 소계의 과목 NULL은 입력 과목을 지운 것이 아니라 이번 집계에서 과목을 뺐다는 표시예요." to BodyTextOverride(
            strong = listOf("100+200=300", "300+400=700", "이번 집계에서 과목을 뺐다는 표시"),
            paragraphStarts = listOf("소계의 과목 NULL은"),
            inlineCodes = listOf("NULL"),
        ),
        // 2-2-08/e1s0
        "GROUPING SETS((지역),(과목))에 적힌 것은 지역 단독과 과목 단독이에요. 상세 쌍이나 빈 그룹 ()는 적혀 있지 않아요." to BodyTextOverride(
            strong = listOf("지역 단독과 과목 단독", "상세 쌍이나 빈 그룹 ()는 적혀 있지 않아요"),
            inlineCodes = listOf("GROUPING SETS((지역),(과목))"),
        ),
        // 2-2-09/e0s2
        "ROLLUP의 전체 ()는 지역을 구별하지 않고 100+200=300을 만들어요. 지역 표시 NULL은 소계용이고 G=1이에요." to BodyTextOverride(
            strong = listOf("지역을 구별하지 않고", "100+200=300", "소계용", "G=1"),
            inlineCodes = listOf("ROLLUP", "NULL"),
        ),
        // 2-2-10/e0s2
        "컴퓨터 학생 두 행에 80을 각각 붙이고 전자 학생 두 행에 70을 붙여요. 학과평균은 결과 별칭이며 원본에 새 컬럼을 저장하지 않아요." to BodyTextOverride(
            strong = listOf("80을 각각", "70을 붙여요", "원본에 새 컬럼을 저장하지 않아요"),
        ),
        // 2-2-11/e0s1
        "90 두 명은 앞에 높은 점수가 없어 공동 1등, 80 앞에는 2명이라 3등, 70 앞에는 3명이라 4등이에요." to BodyTextOverride(
            strong = listOf("공동 1등", "2명이라 3등", "3명이라 4등"),
        ),
        // 2-2-12/e0s3
        "첫 10은 두 범위 모두 10, 마지막 30은 10+20+20+30=80이에요. 중간 두 20의 행누적은 30·50, 값누적은 50·50으로 갈려요." to BodyTextOverride(
            strong = listOf("행누적은 30·50", "값누적은 50·50"),
        ),
        // 2-2-13/e0s0
        "번호순 1 유성재 10→2 김현수 20→3 양선규 30이에요. LAG(금액,1,0)의 1은 이전 한 행, 0은 이전 행이 없을 때 쓸 값이에요." to BodyTextOverride(
            strong = listOf("이전 한 행", "이전 행이 없을 때 쓸 값"),
            inlineCodes = listOf("LAG(금액,1,0)"),
        ),
        // 2-2-14/e0s0
        "ROW_NUMBER는 점수 내림차순 다음 학번 오름차순으로 번호를 붙여요. rn은 그 번호의 출력 별칭, x는 그 결과 전체의 별칭이에요." to BodyTextOverride(
            strong = listOf("점수 내림차순 다음 학번 오름차순", "번호의 출력 별칭", "결과 전체의 별칭"),
            inlineCodes = listOf("ROW_NUMBER", "rn", "x"),
        ),
        // 2-2-15/e0s1
        "PRIOR 사번은 방금 방문한 노우성의 1이에요. 후보 관리자번호=1인 김현수 2·박강열 3이 연결돼 LEVEL 2예요." to BodyTextOverride(
            strong = listOf("방금 방문한 노우성의 1", "후보 관리자번호=1", "LEVEL 2"),
            inlineCodes = listOf("PRIOR 사번", "LEVEL"),
        ),
        // 2-2-16/e0s2
        "4번은 2번을 거쳐 찾은 깊이 3 그대로예요. 2번이 안 보인다고 4번의 관리자번호를 1로 바꾸거나 깊이를 2로 재계산하지 않아요." to BodyTextOverride(
            strong = listOf("깊이 3 그대로", "관리자번호를 1로 바꾸거나 깊이를 2로 재계산하지 않아요"),
        ),
        // 2-2-17/e1s2
        "박상현 DB 90·JAVA 80과 유성재 DB 70은 값이 있어 남아요. 유성재 JAVA는 NULL이라 기본 EXCLUDE NULLS로 해당 행을 제외해요." to BodyTextOverride(
            strong = listOf("값이 있어 남아요", "NULL이라 기본 EXCLUDE NULLS", "해당 행을 제외"),
            inlineCodes = listOf("NULL", "EXCLUDE NULLS"),
        ),
        // 2-2-18/e0s0
        "^는 시작, \$는 끝, (DB|JAVA)는 DB 또는 JAVA를 묶어요. 따라서 전체 문자열이 두 선택지 중 하나여야 해요." to BodyTextOverride(
            strong = listOf("시작", "끝", "전체 문자열이 두 선택지 중 하나"),
            inlineCodes = listOf("^", "\$", "(DB|JAVA)"),
        ),
        // 2-3-01/e1s1
        "1004 노우성의 70은 70>=80이거짓이다. WITH CHECK OPTION은 변경 뒤에도 이 뷰로 볼 수 있는 행이어야 하므로 이번 삽입을 거부한다." to BodyTextOverride(
            strong = listOf("70>=80이거짓", "변경 뒤에도 이 뷰로 볼 수 있는 행", "삽입을 거부"),
            inlineCodes = listOf("WITH CHECK OPTION"),
        ),
        // 2-3-02/e0s3
        "ROLLBACK TO s1은 1100으로 만든 200 추가를 취소해 900으로 돌아간다. s1보다 앞의 100 출금은 취소하지 않아 1000이 아니다." to BodyTextOverride(
            strong = listOf("200 추가를 취소", "900으로 돌아간다", "100 출금은 취소하지 않아"),
            inlineCodes = listOf("ROLLBACK TO s1"),
        ),
        // 2-3-03/e0s2
        "REVOKE UPDATE는 회수할 작업을 UPDATE로 지정했다. FROM U01은 그 계정에게서 거둔다는 뜻이다. SELECT까지 함께 적지 않았으므로 조회 권한은 남는다." to BodyTextOverride(
            strong = listOf("회수할 작업", "그 계정에게서", "조회 권한은 남는다"),
            inlineCodes = listOf("REVOKE UPDATE", "FROM U01", "SELECT"),
        ),
        // 2-3-04/e0s2
        "관계대수 SELECT인σ는 WHERE처럼 행을 고른다. 관계대수 PROJECT인π가 SQL SELECT 목록의 열 선택과 가깝다. 이름이 같은 SELECT를 같은 기능이라고 외우지 않는다." to BodyTextOverride(
            strong = listOf("σ는 WHERE처럼 행을 고른다", "π가 SQL SELECT 목록의 열 선택과 가깝다"),
            inlineCodes = listOf("WHERE", "SELECT"),
        ),
        // 2-1-03/u0s0
        "CREATE TABLE EMPLOYEE는 새 사원표 하나를 만든다. DEPARTMENT는 이미 있는 부서표다. EMP_ID·EMP_NAME·DEPT_ID 세 컬럼만 EMPLOYEE 안에 생긴다." to BodyTextOverride(
            strong = listOf("새 사원표 하나", "이미 있는 부서표", "세 컬럼만 EMPLOYEE 안에"),
            inlineCodes = listOf("CREATE TABLE EMPLOYEE", "DEPARTMENT", "EMP_ID", "EMP_NAME", "DEPT_ID"),
        ),
        // 2-1-03/u0s1
        "EMP_ID NUMBER(6)의 6과 DEPT_ID NUMBER(4)의 4는 숫자의 정밀도다. 10 같은 작은 수를 저장해도 된다. 자동 번호 생성이나 행 개수 제한이 아니다. Oracle NUMBER(p)는 scale 0이며 소수 입력은 반올림과 정밀도 초과를 구별한다." to BodyTextOverride(
            strong = listOf("숫자의 정밀도", "자동 번호 생성이나 행 개수 제한이 아니다", "반올림과 정밀도 초과"),
            paragraphStarts = listOf("Oracle NUMBER(p)는"),
            inlineCodes = listOf("EMP_ID NUMBER(6)", "DEPT_ID NUMBER(4)", "NUMBER(p)"),
        ),
        // 2-1-03/u0s2
        "CONSTRAINT는 규칙에 이름을 붙이는 SQL 문법이다. FK_EMP_DEPT는 설계자가 지은 이름이고, 실제 외래키 종류는 다음 FOREIGN KEY가 정한다. 이 줄 때문에 FK_EMP_DEPT라는 표나 컬럼은 생기지 않는다." to BodyTextOverride(
            strong = listOf("규칙에 이름을 붙이는", "설계자가 지은 이름", "외래키 종류", "표나 컬럼은 생기지 않는다"),
            inlineCodes = listOf("CONSTRAINT", "FK_EMP_DEPT", "FOREIGN KEY"),
        ),
        // 2-1-03/u0s3
        "FOREIGN KEY (DEPT_ID)는 지금 만드는 EMPLOYEE의 DEPT_ID를 말한다. REFERENCES DEPARTMENT(DEPT_ID)는 상대 부서표의 DEPARTMENT.DEPT_ID를 지정한다. 이름은 같아도 소속 표가 다르며 외래키는 EMPLOYEE.DEPT_ID다." to BodyTextOverride(
            strong = listOf("지금 만드는 EMPLOYEE의 DEPT_ID", "상대 부서표의 DEPARTMENT.DEPT_ID", "외래키는 EMPLOYEE.DEPT_ID"),
            paragraphStarts = listOf("이름은 같아도 소속 표가 다르며"),
            inlineCodes = listOf("FOREIGN KEY (DEPT_ID)", "REFERENCES DEPARTMENT(DEPT_ID)", "EMPLOYEE.DEPT_ID"),
        ),
        // 2-1-03/u0s4
        "박강열의 10과 양지훈의 10은 DEPARTMENT에 있어 각각 허용한다. 외래키는 여러 사원이 같은 부서를 가리키는 것을 금지하지 않는다. 유성재의 99는 부모 키에 없어 거부한다. 아래는 저장 결과가 아닌 독립 입력 시도다." to BodyTextOverride(
            strong = listOf("각각 허용", "같은 부서를 가리키는 것을 금지하지 않는다", "부모 키에 없어 거부", "독립 입력 시도"),
            paragraphStarts = listOf("아래는 저장 결과가 아닌"),
            inlineCodes = listOf("DEPARTMENT"),
        ),
        // 2-1-03/u0s5
        "DEPT_ID에는 NOT NULL이 없다. 김현수의 NULL은 특정 부서 키를 주장하지 않는 상태여서 이 단일 열 FK 자체로는 거부하지 않는다. 반드시 부서를 정해야 하는 업무라면 DEPT_ID에 NOT NULL을 별도로 둔다." to BodyTextOverride(
            strong = listOf("NOT NULL이 없다", "이 단일 열 FK 자체로는 거부하지 않는다", "NOT NULL을 별도로"),
            paragraphStarts = listOf("반드시 부서를 정해야 하는"),
            inlineCodes = listOf("DEPT_ID", "NOT NULL", "NULL"),
        ),
        // 2-1-03/u0s6
        "이 전체 SQL은 CREATE 한 문장이다. 줄별로 다른 테이블을 만들거나 부서의 10과 20을 사원표에 복사하지 않는다. 실제 사원 행은 이후 INSERT를 해야 생긴다." to BodyTextOverride(
            strong = listOf("CREATE 한 문장", "복사하지 않는다", "INSERT를 해야 생긴다"),
            inlineCodes = listOf("CREATE", "INSERT"),
        ),
        // 2-1-05/u0s0
        "STUDENT의 정의 순서는 ID, NAME, PHONE이다. 이번 INSERT는 NAME, PHONE, ID 순서로 컬럼 이름을 직접 적었다. 테이블 자체의 컬럼 순서를 바꾸는 문장이 아니다." to BodyTextOverride(
            strong = listOf("정의 순서는 ID, NAME, PHONE", "NAME, PHONE, ID 순서", "컬럼 순서를 바꾸는 문장이 아니다"),
            inlineCodes = listOf("STUDENT", "INSERT", "ID", "NAME", "PHONE"),
        ),
        // 2-1-05/u0s1
        "첫 이름 NAME은 양지훈, 둘째 PHONE은 010-****-1003, 셋째 ID는 1003을 받는다. 오른쪽 값이 앞의 같은 위치 컬럼에 들어간다." to BodyTextOverride(
            strong = listOf("NAME은 양지훈", "PHONE은 010-****-1003", "ID는 1003", "같은 위치 컬럼"),
            paragraphStarts = listOf("오른쪽 값이 앞의 같은 위치 컬럼에 들어간다."),
            inlineCodes = listOf("NAME", "PHONE", "ID"),
        ),
        // 2-1-05/u0s2
        "새 행을 ID, NAME, PHONE 순서로 읽으면 (1003, 양지훈, 010-****-1003)이다. 기존 박강열 행도 유지한다. 이 표의 나열 순서는 설명용이며 원본 INSERT에는 ORDER BY 조회가 없다." to BodyTextOverride(
            strong = listOf("(1003, 양지훈, 010-****-1003)", "기존 박강열 행도 유지", "나열 순서는 설명용"),
            paragraphStarts = listOf("이 표의 나열 순서는 설명용이며"),
            inlineCodes = listOf("ID", "NAME", "PHONE", "INSERT", "ORDER BY"),
        ),
        // 2-1-05/u0s3
        "컬럼 목록 전체를 빼면 이 기본 테이블에서는 ID·NAME·PHONE 정의 순서의 세 값을 줘야 한다. 반면 (ID, NAME)만 적으면 PHONE 컬럼을 생략한 것이다. 여기서는 PHONE 기본값이 없고 NULL을 허용해 새 행의 PHONE은 NULL이 된다." to BodyTextOverride(
            strong = listOf("컬럼 목록 전체를 빼면", "PHONE 컬럼을 생략", "PHONE은 NULL"),
            paragraphStarts = listOf("반면 (ID, NAME)만 적으면"),
            inlineCodes = listOf("ID", "NAME", "PHONE", "NULL"),
        ),
        // note-M01/M01-02
        "도서관을 전부 복제하지 않고 회원, 책, 대출과 이들 사이의 규칙을 그린 지도라고 생각하자. 화면 디자인보다 먼저 무엇을 어떤 규칙으로 기억할지 정한다." to BodyTextOverride(
            strong = listOf("회원, 책, 대출", "무엇을 어떤 규칙으로 기억할지"),
        ),
        // note-M01/M01-03
        "추상화는 필요한 특징을 선택하고, 단순화는 복잡함을 이해 가능한 구조로 줄이며, 명확화는 같은 표현이 같은 뜻을 갖도록 하는 것이다. 개념 모델은 업무 핵심, 논리 모델은 식별자·속성·관계, 물리 모델은 특정 DBMS 저장 구조와 자료형 등을 구체화한다." to BodyTextOverride(
            strong = listOf("필요한 특징을 선택", "이해 가능한 구조로 줄이며", "같은 표현이 같은 뜻"),
            paragraphStarts = listOf("개념 모델은 업무 핵심,"),
        ),
        // note-M01/M01-supp-database
        "데이터베이스(DB)는 업무와 관련된 데이터를 규칙에 맞게 저장하고 함께 이용하는 데이터의 모음이다. DBMS는 그 데이터를 정의·조회·변경하고 권한·동시 접근·복구를 관리하는 소프트웨어다. 데이터 자체와 이를 관리하는 프로그램은 다르다." to BodyTextOverride(
            strong = listOf("데이터의 모음", "소프트웨어", "데이터 자체와 이를 관리하는 프로그램은 다르다"),
            inlineCodes = listOf("DB", "DBMS"),
        ),
        // note-M04/M04-05
        "1:N은 최대 연결 수와 관련되고, 선택/필수는 최소 연결 수와 관련된다. 1:N이라는 말만으로 고객에게 반드시 주문이 있다고 결론낼 수 없다." to BodyTextOverride(
            strong = listOf("최대 연결 수", "최소 연결 수", "반드시 주문이 있다고 결론낼 수 없다"),
        ),
        // note-M04/M04-identifying
        "부모의 식별자가 자식 주식별자의 일부이면 식별 관계다. 부모키가 자식의 일반 FK에만 있고 자식 PK에는 없으면 비식별 관계다. 예: 주문 PK=주문ID, 상세 PK=(주문ID,줄번호)이면 식별 관계다. 상세 PK=상세ID이고 주문ID가 일반 FK이면 비식별 관계다. 비식별 관계라도 주문ID가 NOT NULL이면 상세의 부모 참여는 필수다. 식별 여부는 PK 포함 여부, 선택·필수는 최소 참여 조건이라는 두 기준을 나누어 읽는다. 부모ID가 인조식별자여도 같은 기준을 적용한다." to BodyTextOverride(
            strong = listOf("자식 주식별자의 일부", "자식 PK에는 없으면", "식별 여부는 PK 포함 여부", "선택·필수는 최소 참여 조건"),
            paragraphStarts = listOf("예: 주문 PK=주문ID,", "비식별 관계라도 주문ID가"),
            inlineCodes = listOf("PK", "FK", "NOT NULL"),
        ),
        // note-M06/M06-03
        "X→Y는 같은 X 값이면 항상 같은 Y 값이라는 업무 제약이다. 1NF는 도메인에 맞는 원자값, 2NF는 1NF이고 모든 비주요 속성이 모든 후보키 전체에 완전 함수 종속, 3NF는 비자명 FD X→A마다 X가 슈퍼키이거나 A가 주요 속성인 조건이다. 초급 사례에서는 비키→비키 이행 종속 제거로 이해하되 일반 정의와 구분한다." to BodyTextOverride(
            strong = listOf("같은 X 값이면 항상 같은 Y 값", "완전 함수 종속", "X가 슈퍼키이거나 A가 주요 속성"),
            paragraphStarts = listOf("1NF는 도메인에 맞는 원자값,", "초급 사례에서는"),
            inlineCodes = listOf("X→Y", "1NF", "2NF", "3NF"),
        ),
        // note-M06/M06-supp-bcnf-definition
        "BCNF(보이스·코드 정규형)는 모든 비자명 함수 종속 X→Y에서 X가 슈퍼키인 정규형이다. 비자명은 Y에 X 바깥의 속성이 있다는 뜻이고, 슈퍼키는 그 값으로 행 전체를 식별할 수 있는 속성 집합이다. 후보키는 최소 슈퍼키다. 따라서 「모든 결정자가 최소 후보키여야 한다」로 좁혀 외우면 불필요한 속성을 더한 결정자를 잘못 판단할 수 있다." to BodyTextOverride(
            strong = listOf("X가 슈퍼키", "행 전체를 식별", "후보키는 최소 슈퍼키"),
            paragraphStarts = listOf("따라서 「모든 결정자가"),
            inlineCodes = listOf("BCNF", "X→Y"),
        ),
        // note-S01/S01-03
        "관계 모델의 수학적 집합과 SQL 결과의 중복 허용 특성을 구분한다. SQL SELECT는 기본적으로 중복 행을 제거하지 않는다. 행의 표시 순서는 ORDER BY로 요구하며 저장 순서나 PK만으로 보장되지 않는다." to BodyTextOverride(
            strong = listOf("중복 허용", "중복 행을 제거하지 않는다", "저장 순서나 PK만으로 보장되지 않는다"),
            inlineCodes = listOf("SELECT", "ORDER BY", "PK"),
        ),
        // note-S03/S03-03
        "이 노트의 실행 대상은 Oracle 19c다. SUBSTR 시작 위치는 1 기반이며 음수는 끝에서 센다. LENGTH는 문자 수, LENGTHB는 바이트 수이다. ROUND(n,1)는 소수 첫째 자리, ROUND(n,-1)는 십의 자리로 반올림한다." to BodyTextOverride(
            strong = listOf("1 기반", "음수는 끝에서", "문자 수", "바이트 수"),
            paragraphStarts = listOf("ROUND(n,1)는"),
            inlineCodes = listOf("SUBSTR", "LENGTH", "LENGTHB", "ROUND(n,1)", "ROUND(n,-1)"),
        ),
        // note-S03/S03-supp-instr-example
        "INSTR('BANANA','AN',1,2)는 4다. 첫 번째 AN은 위치 2에서, 두 번째 AN은 위치 4에서 시작한다. SUBSTR('BANANA',4,2)는 AN이다. INSTR('BANANA','ZX')는 0이며 NULL을 뜻하지 않는다. 찾을 단어가 길어도 결과는 단어 길이가 아니라 시작 위치다." to BodyTextOverride(
            strong = listOf("4다", "AN이다", "0이며 NULL을 뜻하지 않는다", "시작 위치"),
            paragraphStarts = listOf("SUBSTR('BANANA',4,2)는"),
            inlineCodes = listOf("INSTR('BANANA','AN',1,2)", "SUBSTR('BANANA',4,2)", "INSTR('BANANA','ZX')"),
        ),
        // note-S05/S05-03
        "검색 CASE는 위에서부터 TRUE인 첫 WHEN의 결과를 반환한다. ELSE가 없고 아무 조건도 TRUE가 아니면 NULL이다. COALESCE는 첫 비NULL 값, NVL은 첫 인자가 NULL이면 둘째 값, NULLIF(a,b)는 같으면 NULL 아니면 a이다. 자료형 호환성도 확인한다." to BodyTextOverride(
            strong = listOf("TRUE인 첫 WHEN", "아무 조건도 TRUE가 아니면 NULL", "첫 비NULL 값", "같으면 NULL 아니면 a"),
            paragraphStarts = listOf("COALESCE는 첫 비NULL 값,"),
            inlineCodes = listOf("CASE", "WHEN", "ELSE", "COALESCE", "NVL", "NULLIF(a,b)"),
        ),
        // note-S05/S05-supp-decode-null-example
        "DECODE(NULL,NULL,'비어있음','그외')는 비어있음이다. DECODE는 검색 비교에서 두 NULL을 같은 것으로 취급한다. 반면 CASE NULL WHEN NULL THEN '비어있음' ELSE '그외' END는 그외다. 일반 동등 비교의 NULL은 TRUE가 아니기 때문이다. CASE WHEN x IS NULL THEN ... 형식이면 의도를 정확히 표현할 수 있다." to BodyTextOverride(
            strong = listOf("두 NULL을 같은 것으로 취급", "일반 동등 비교의 NULL은 TRUE가 아니기 때문"),
            paragraphStarts = listOf("반면 CASE NULL WHEN NULL"),
            inlineCodes = listOf("DECODE(NULL,NULL,'비어있음','그외')", "CASE NULL WHEN NULL THEN '비어있음' ELSE '그외' END", "CASE WHEN x IS NULL THEN ..."),
        ),
        // note-S06/S06-03
        "AND에서는 FALSE가 있으면 FALSE, 나머지에 UNKNOWN이 있으면 UNKNOWN이다. OR에서는 TRUE가 있으면 TRUE, 나머지에 UNKNOWN이 있으면 UNKNOWN이다. NOT UNKNOWN은 UNKNOWN이다. 기본 우선순위는 NOT, AND, OR이며 의도를 괄호로 표현한다." to BodyTextOverride(
            strong = listOf("FALSE가 있으면 FALSE", "TRUE가 있으면 TRUE", "NOT UNKNOWN은 UNKNOWN", "NOT, AND, OR"),
            paragraphStarts = listOf("기본 우선순위는"),
            inlineCodes = listOf("AND", "OR", "NOT UNKNOWN"),
        ),
        // note-S07/S07-03
        "COUNT(*)는 모든 입력 행, COUNT(식)는 식 결과가 비NULL인 행을 센다. SUM·AVG·MIN·MAX는 일반적으로 NULL 입력을 제외한다. 그룹 없는 빈 입력의 COUNT는 0, SUM·AVG는 NULL이다." to BodyTextOverride(
            strong = listOf("모든 입력 행", "비NULL인 행", "NULL 입력을 제외", "빈 입력의 COUNT는 0"),
            paragraphStarts = listOf("그룹 없는 빈 입력의"),
            inlineCodes = listOf("COUNT(*)", "COUNT(식)", "SUM", "AVG"),
        ),
        // note-S08/S08-03
        "WHERE는 그룹화 전 개별 행을 제한하고 HAVING은 그룹을 제한한다. SELECT에 일반 열을 출력하려면 해당 그룹에서 값이 정의되도록 GROUP BY 표현식 또는 집계에 맞춰 작성한다. Oracle 19c를 기준으로 비그룹 열을 임의로 선택하지 않는다." to BodyTextOverride(
            strong = listOf("그룹화 전 개별 행", "그룹을 제한", "그룹에서 값이 정의되도록"),
            paragraphStarts = listOf("SELECT에 일반 열을 출력하려면"),
            inlineCodes = listOf("WHERE", "HAVING", "SELECT", "GROUP BY"),
        ),
        // note-S08/S08-04
        "T(부서,금액)=(A,10),(A,20),(B,5). GROUP BY 부서 결과는 A 합계30·건수2, B 합계5·건수1. HAVING SUM(금액)>=20이면 A만 남는다. WHERE 금액>=20을 먼저 적용하면 A의 20 한 행만 집계된다." to BodyTextOverride(
            strong = listOf("A 합계30·건수2", "B 합계5·건수1", "A만 남는다", "20 한 행만 집계"),
            paragraphStarts = listOf("WHERE 금액>=20을 먼저"),
            inlineCodes = listOf("GROUP BY 부서", "HAVING SUM(금액)>=20", "WHERE 금액>=20"),
        ),
        // note-S10/S10-conditions
        "INNER JOIN은 ON 조건이 TRUE인 행 쌍만 반환한다. 한쪽 키의 중복과 관계의 카디널리티가 결과 행 수를 결정한다. 일반 등호 비교에서 NULL=NULL은 TRUE가 아니다." to BodyTextOverride(
            strong = listOf("TRUE인 행 쌍만", "결과 행 수", "NULL=NULL은 TRUE가 아니다"),
            inlineCodes = listOf("INNER JOIN", "ON", "NULL=NULL"),
        ),
        // note-S11/S11-conditions
        "LEFT JOIN은 왼쪽, RIGHT JOIN은 오른쪽, FULL OUTER JOIN은 양쪽의 미매칭 행을 보존한다. ON은 매칭 조건이고 WHERE는 조인 결과를 거르는 조건이다." to BodyTextOverride(
            strong = listOf("양쪽의 미매칭 행", "매칭 조건", "조인 결과를 거르는 조건"),
            inlineCodes = listOf("LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN", "ON", "WHERE"),
        ),
        // note-S12/S12-conditions
        "스칼라 서브쿼리는 1열·최대 1행이어야 한다. 0행이면 NULL, 2행 이상이면 오류다. EXISTS는 행의 존재, IN은 값의 소속을 검사한다. 상관 서브쿼리는 바깥 행의 값을 참조한다." to BodyTextOverride(
            strong = listOf("1열·최대 1행", "0행이면 NULL", "2행 이상이면 오류", "바깥 행의 값을 참조"),
            paragraphStarts = listOf("EXISTS는 행의 존재,"),
            inlineCodes = listOf("EXISTS", "IN"),
        ),
        // note-S16/S16-conditions
        "ROWS는 정렬된 행 위치 기준, RANGE는 정렬 값 기준이다. 프레임을 지원하는 함수에서 ORDER BY만 있고 프레임을 생략하면 Oracle 기본은 RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW다." to BodyTextOverride(
            strong = listOf("정렬된 행 위치 기준", "정렬 값 기준", "프레임을 생략하면"),
            paragraphStarts = listOf("프레임을 지원하는 함수에서"),
            inlineCodes = listOf("ROWS", "RANGE", "ORDER BY", "RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW"),
        ),
        // note-S21/S21-conditions
        "INSERT 열 목록과 값의 대응을 확인한다. UPDATE·DELETE에서 WHERE를 생략하면 대상 테이블 전체 행이 대상이다. NULL을 판별할 때 =NULL이 아닌 IS NULL을 사용한다. MERGE는 ON 매칭 여부에 따라 지정한 갱신·삽입을 수행한다." to BodyTextOverride(
            strong = listOf("열 목록과 값의 대응", "대상 테이블 전체 행", "ON 매칭 여부"),
            paragraphStarts = listOf("NULL을 판별할 때"),
            inlineCodes = listOf("INSERT", "UPDATE", "DELETE", "WHERE", "=NULL", "IS NULL", "MERGE"),
        ),
        // note-S22/S22-conditions
        "COMMIT은 현재 변경을 확정하고 기존 savepoint를 지운다. ROLLBACK은 미확정 변경을 취소한다. ROLLBACK TO savepoint는 그 지점 이후만 되돌리며 트랜잭션을 끝내지 않는다." to BodyTextOverride(
            strong = listOf("현재 변경을 확정", "기존 savepoint를 지운다", "미확정 변경을 취소", "그 지점 이후만 되돌리며 트랜잭션을 끝내지 않는다"),
            inlineCodes = listOf("COMMIT", "ROLLBACK", "ROLLBACK TO savepoint"),
        ),
        // note-S23/S23-conditions
        "CREATE TABLE은 객체 생성, ALTER TABLE은 구조 변경, DROP TABLE은 객체 제거, TRUNCATE TABLE은 정의를 유지하고 전체 행을 비운다. PRIMARY KEY는 유일성과 NOT NULL을 요구한다. FOREIGN KEY는 참조 무결성이다." to BodyTextOverride(
            strong = listOf("정의를 유지하고 전체 행을 비운다", "유일성과 NOT NULL", "참조 무결성"),
            paragraphStarts = listOf("PRIMARY KEY는"),
            inlineCodes = listOf("CREATE TABLE", "ALTER TABLE", "DROP TABLE", "TRUNCATE TABLE", "PRIMARY KEY", "FOREIGN KEY"),
        ),
        // note-S23/S23-compare
        "CHECK는 FALSE를 거부하며 UNKNOWN을 통과시킬 수 있으므로 NOT NULL을 대신하지 못한다. UNIQUE와 PRIMARY KEY는 NULL 허용 조건에서 차이가 있다." to BodyTextOverride(
            strong = listOf("FALSE를 거부", "NOT NULL을 대신하지 못한다", "NULL 허용 조건에서 차이"),
            inlineCodes = listOf("CHECK", "UNKNOWN", "NOT NULL", "UNIQUE", "PRIMARY KEY"),
        ),
    )
}
