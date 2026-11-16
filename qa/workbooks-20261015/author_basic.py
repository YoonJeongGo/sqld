"""Original 2-1 staging; no Oracle execution or official/expert claim."""
from common import question, table, save
from collections import Counter
import json
from pathlib import Path
review=[]; mocks=[[],[],[]]; seen=Counter()
SRC={1:'oracle19-create-table',2:'oracle19-datatypes',3:'oracle19-constraints',4:'oracle19-alter-table',5:'oracle19-insert',6:'oracle19-select',7:'oracle19-logical',8:'oracle19-update',9:'oracle19-delete',10:'oracle19-merge',11:'oracle19-logical',12:'oracle19-select',13:'oracle19-functions',14:'oracle19-functions',15:'oracle19-nulls',16:'oracle19-logical',17:'oracle19-functions',18:'oracle19-case',19:'oracle19-aggregate',20:'oracle19-select',21:'oracle19-select',22:'oracle19-joins',23:'oracle19-joins',24:'oracle19-joins',25:'oracle19-select'}
ADVANCED={3,8,10,11,16,18,19,20,23,25}
def T(name,headers,rows): return table(name,headers.split(','),rows)
def A(lesson,stem,answers,why,sql='',data=None,source=None):
    """Nine independently authored cases per lesson; common shuffles answers."""
    seen[lesson]+=1; n=seen[lesson]; assert n<=9
    lid=f'2-1-{lesson:02}'
    if n<=3:
        kind=['recall','discriminate','apply'][n-1]; diff='basic' if n==1 else 'intermediate'
        qid=f'unit-2-1-review-{lesson:02}-{n:02}'
    else:
        form=(n-4)//2; within=(n-4)%2
        kind='application'
        diff='basic' if within==0 and lesson<=10 else ('advanced' if within==1 and lesson in ADVANCED else 'intermediate')
        qid=f'unit-2-1-mock-{form+1}-{(lesson-1)*2+within+1:02}'
    choices=answers.split('§'); assert len(choices)==4
    conditions='Oracle 19c. 제시 입력이 전부이며 명시 외 제약·트리거·동시 변경은 없다. '
    if lesson in [4,5,8,9,10]: conditions+='초기 입력은 COMMIT된 상태다. '
    if data: conditions+='표의 별도 자료형 명시가 없으면 숫자는 NUMBER, 문자는 VARCHAR2다. '
    parts=why.split(' / ')
    q=question(qid,lid,kind,diff,conditions+stem,choices,0,' '.join(parts),sql,data or [],parts,parts[-1],source or SRC[lesson])
    q.update(authorship='original_practice',verification='author_logical_review',engineVerified=False)
    if n<=3: review.append(q)
    else: mocks[form].append(q)

# 01 DDL / CREATE
A(1,'CREATE TABLE의 직접 목적은?','열과 자료형을 가진 테이블 정의를 만든다§기존 행을 모두 수정한다§조회 순서를 영구 고정한다§접속 사용자를 모두 삭제한다','CREATE TABLE은 구조를 정의하는 DDL이다. / 행 수정은 UPDATE, 출력 정렬은 ORDER BY이며 사용자 삭제와 다르다.')
A(1,'CREATE TABLE T(id NUMBER PRIMARY KEY,memo VARCHAR2(10)); 직후 데이터를 넣지 않았다. 상태는?','2열·0행§0열·2행§NULL 두 칸의 행이 자동 생성§빈 테이블이므로 생성 실패','두 열을 선언했지만 INSERT가 없어 행은0개다. / 열 수와 행 수는 다르며 PK가 있다고 초기 행이 필요한 것은 아니다.')
A(1,'CTAS가 R에 담는 행 수는?','2§0§1§3','v>=5는 id2,3을 선택한다. / DISTINCT가 없으므로 같은 v=5도 두 행이며 기존 S 전체3행을 복사하지 않는다.','CREATE TABLE R AS SELECT v FROM S WHERE v>=5;', [T('S','id,v',[[1,2],[2,5],[3,5]])])
A(1,'다음 DDL의 열 수는?','3§1§2§4','id,qty,note가 세 열이다. / PRIMARY KEY와 DEFAULT는 별도 열이 아닌 제약과 기본값이다.','CREATE TABLE T(id NUMBER PRIMARY KEY,\n qty NUMBER DEFAULT 0,note VARCHAR2(20));')
A(1,'S에 두 행이 있다. 다음 CTAS 직후 R의 COUNT(*) 값은?','0§1§2§NULL','1=0이 모든 행을 제외하므로 R은 빈 구조로 생성된다. / COUNT(*)는 빈 입력에서 NULL이 아닌0이며 CTAS가 반드시 원본 행을 복사하지 않는다.','CREATE TABLE R AS SELECT id,v FROM S WHERE 1=0;', [T('S','id,v',[[1,4],[2,6]])])
A(1,'CREATE TABLE T(id NUMBER,id VARCHAR2(10));가 잘못된 이유는?','한 테이블의 열 이름이 중복된다§VARCHAR2는 사용 불가§NUMBER는 반드시 크기를 지정§테이블은 열 하나만 허용','id라는 열 이름이 중복되어 구분할 수 없다. / VARCHAR2, 크기 없는 NUMBER, 여러 열 선언 자체는 허용되는 형태다.')
A(1,'T에 PK(id)와 CHECK(v>0)가 있다. CTAS로 R을 만들면 두 제약이 그대로 복사되는가?','보장되지 않아 별도 정의·확인이 필요하다§두 제약 모두 항상 복사§CHECK만 항상 복사§PK만 항상 복사','CTAS를 제약 전체 복제 명령으로 볼 수 없다. / 직접 열에서 일부 NOT NULL이 유지되는 규칙과 PK·CHECK 자동 복제를 혼동하지 않는다.','CREATE TABLE R AS SELECT id,v FROM T;')
A(1,'다음 선언에서 amount의 기본값은?','100§0§NULL만 허용§다른 행의 amount','DEFAULT 100은 값을 생략할 때 쓸 기본 표현식이다. / 행을 미리 만들거나 다른 행에서 값을 복사하는 기능이 아니다.','CREATE TABLE Invoice(id NUMBER,amount NUMBER DEFAULT 100);')
A(1,'다음 CTAS의 R.x 값은?','6과 14§3과 7§1과 2§0행','각 v에2를 곱해3×2=6,7×2=14를 저장한다. / x는 id의 이름 변경이 아니라 계산식의 별칭이다.','CREATE TABLE R AS SELECT v*2 AS x FROM S;', [T('S','id,v',[[1,3],[2,7]])])

# 02 Datatypes
A(2,'NUMBER(5,2)의5와2는?','전체 유효 숫자 자릿수·소수 자릿수§정수 자릿수·전체 자릿수§최솟값·최댓값§문자 수·바이트 수','정밀도5 안에 소수2자리가 포함된다. / 정수5자리와 소수2자리를 합쳐7자리로 해석하거나 값 범위 자체로 읽지 않는다.')
A(2,"CHAR(4)와 VARCHAR2(4)에 각각 'AB'를 저장했다. LENGTH 결과는?",'4와 2§2와 2§4와 4§2와 4','CHAR는 고정 길이 공백 채움을 하므로4, VARCHAR2는 입력 두 문자를 유지하므로2다. / 선언 최대 길이와 실제 길이를 구분한다.')
A(2,'T(v NUMBER(4,1))에12.36을 넣으면 저장 수치는?','12.4§12.3§123.6§항상 오류','소수1자리로 반올림하여12.4이며 정밀도4에 들어간다. / 절삭12.3이나 소수점 이동123.6이 아니다.','INSERT INTO T(v) VALUES(12.36);')
A(2,'Oracle DATE가 저장할 수 있는 정보는?','년·월·일과 시·분·초§년·월·일만§시간대 지역명을 항상 포함§소수 초9자리를 반드시 포함','DATE는 시·분·초까지 가진다. / 시간대 및 소수 초 정보는 DATE에 항상 포함되는 정보가 아니다.')
A(2,'T(v NUMBER(3,0))에999.6을 넣는 결과는?','반올림1000이 정밀도3을 넘어 실패§999로 절삭하여 성공§1000으로 성공§NULL을 저장하고 성공','소수0자리 반올림은1000인데 네 자리라 정밀도3을 넘는다. / 실패를 자동 절삭이나 NULL 대입으로 바꾸지 않는다.','INSERT INTO T VALUES(999.6);')
A(2,'길이가 변하는 영문 코드를 고정 공백 채움 없이 저장할 자료형은?','VARCHAR2(12)§CHAR(12)§DATE§NUMBER(12)','VARCHAR2는 가변 길이 문자형이다. / CHAR는 고정 길이이고 DATE·NUMBER는 문자 코드의 해당 목적과 다르다.')
A(2,"AL32UTF8에서 '가'는3바이트다. '가나'를 VARCHAR2(2 BYTE)와 VARCHAR2(2 CHAR)에 넣으면?",'BYTE 실패·CHAR 성공§둘 다 성공§둘 다 실패§BYTE 성공·CHAR 실패','가나는6바이트이지만2문자다. / BYTE의 제한2와 CHAR의 제한2는 단위가 다르다.')
A(2,"문자 '125'를 숫자125로 명시 변환하는 식은?","TO_NUMBER('125')§TO_CHAR('125')§LENGTH('125')§SUBSTR('125',1,2)",'TO_NUMBER는 수치125를 만든다. / TO_CHAR는 문자, LENGTH는3, SUBSTR는부분 문자열12를 반환해 목적이 다르다.')
A(2,'다음 식의 결과는? DATE 리터럴은 자정이다.','1.5§36§1§0.5','10월2일 정오와10월1일 자정의 차이는36시간=1.5일이다. / DATE 뺄셈 단위는 일이며 시각도 포함한다.',"SELECT (DATE '2026-10-02'+0.5)-DATE '2026-10-01' AS d FROM DUAL;")

# 03 Constraints
A(3,'PRIMARY KEY의 핵심 조건은?','중복·NULL 모두 금지§중복만 금지§NULL만 금지§외래키 열에만 지정 가능','PK는 유일성과 비NULL을 함께 요구한다. / UNIQUE만 또는 NOT NULL만 선언한 것과 같은 의미가 아니다.')
A(3,'v NUMBER CHECK(v>0)만 선언한 열에 NULL을 넣으면?','CHECK 자체는 거부하지 않는다§항상 CHECK 위반§자동0으로 저장§자동1로 저장','NULL>0은 UNKNOWN이며 CHECK는 FALSE를 거부한다. / NULL 금지는 NOT NULL로 별도 요구해야 한다.')
A(3,'T의 PK는(a,b)이다. 추가 가능한 행은?','(1,3)§(1,1)§(NULL,3)§(2,NULL)','(1,3)은 비NULL이며 기존 복합키와 다르다. / (1,1)은 중복이고 PK의 일부 NULL도 허용되지 않는다.',data=[T('T','a,b',[[1,1],[1,2],[2,1]])])
A(3,'UNIQUE(v)만 있으며 NULL 허용이다. 기존 값7이 있을 때 금지되는 삽입은?','7§NULL§8§9','비NULL7이 중복되면 UNIQUE 위반이다. / 다른 값8·9 및 NULL 허용 열의 NULL을 같은 위반으로 처리하지 않는다.')
A(3,'P(id PK)와 C(id PK,pid FK→P.id)이다. ON DELETE 옵션은 없다. 성공할 작업만 고르면? ㉠ P1 삭제 ㉡ P2 삭제 ㉢ C(12,3) 삽입','㉡만§㉠·㉡§㉡·㉢§셋 다','P1은 C10이 참조해 삭제가 막힌다. P2는 참조되지 않아 삭제 가능하다. / 부모3이 없어 C(12,3)은 FK 위반이다. 자식의 NULL은 부모3을 대신하지 않는다.',data=[T('P','id',[[1],[2]]),T('C','id,pid',[[10,1],[11,None]])])
A(3,'CHECK(qty>=0)만 있는 열에서 거부되는 값은?','-1§0§1§NULL','-1>=0만 FALSE다. / 0·1은 TRUE이며 NULL 비교는 UNKNOWN이라 CHECK만으로는 거부하지 않는다.')
A(3,'주문선 PK(order_id,line_no), FK(product_id→상품PK), qty NOT NULL 및 CHECK(qty>0)이다. 기존 키(8,1), 상품키100만 있다. 허용 행은?','(8,2,100,1)§(8,1,100,1)§(8,2,200,1)§(8,2,100,NULL)','새 키(8,2), 존재 상품100, 양수1은 모두 통과한다. / 나머지는 각각 PK 중복, 없는 부모200, qty의 NOT NULL 위반이다.')
A(3,'외래키의 주된 목적은?','자식 참조 값과 부모 키의 관계 유지§모든 조회 자동 정렬§모든 열 NULL 금지§자식 행 수를1개로 제한','FK는 참조 무결성을 유지한다. / 정렬·전체 열 NULL 금지·자식 수1 제한은 FK 하나로 보장되지 않는다.')
A(3,'C.pid는 P.id를 ON DELETE SET NULL로 참조하면서 NOT NULL이다. C가 P1을 참조한다. P1을 삭제하면?','자식 pid를 NULL로 만들 수 없어 실패§부모·자식 모두 삭제§자식 pid를0으로 변경§부모만 삭제하고 자식 pid1 유지','SET NULL 동작이 NOT NULL과 충돌한다. / CASCADE 삭제나0 대입으로 대신하지 않고 깨진 참조를 남기지도 않는다.')

# 04 ALTER and RENAME
A(4,'기존 테이블에 열을 추가하는 문장은?','ALTER TABLE T ADD (memo VARCHAR2(20))§UPDATE T ADD memo§INSERT COLUMN memo INTO T§SELECT ADD memo FROM T','구조 추가는 ALTER TABLE ADD다. / UPDATE·INSERT는 행 데이터 작업이고 SELECT는 구조 변경 명령이 아니다.')
A(4,'ALTER TABLE T RENAME COLUMN old_code TO code;의 효과는?','열 이름 변경·기존 값 보존§모든 값을 code로 변경§테이블 이름을 code로 변경§old_code와 code 두 열로 복제','RENAME COLUMN은 열 식별자를 바꾼다. / 데이터 UPDATE, 테이블 RENAME, 열 복제와 구분한다.')
A(4,'T(id)={1,2}에서 다음 ALTER 후 id2의 qty는?','5§0§NULL§반드시 실패','새 열 기본값5가 기존 행에도 제공된다. / DEFAULT가 없는 새 NULL 허용 열 추가와 혼동하지 않는다.','ALTER TABLE T ADD (qty NUMBER DEFAULT 5);',[T('T','id',[[1],[2]])])
A(4,'ALTER TABLE T DROP COLUMN memo; 성공 후 상태는?','memo 열 제거·다른 열 유지§T 전체 제거§memo 값을 NULL로만 변경§memo라는 새 테이블 생성','지정 열의 구조와 값을 제거한다. / DROP TABLE이나 UPDATE SET memo=NULL과 다르다.')
A(4,'표의 T.v를 NOT NULL로 바꾸려 한다. 필요한 조치는?','기존 NULL을 허용되는 비NULL 값으로 정리§제약 이름만 변경§id가 PK이면 바로 가능§ORDER BY v 실행','v에 NULL이 남아 있으면 검증을 통과하지 못한다. / 이름·다른 열의 PK·출력 순서는 v의 NULL을 없애지 않는다.','ALTER TABLE T MODIFY (v NOT NULL);',[T('T','id,v',[[1,None],[2,7]])])
A(4,'RENAME T TO T_ARCHIVE; 성공 시 기존 행은?','그대로 유지§전부 삭제§NULL 행 하나로 교체§다른 세션으로 이동','이름 변경은 행 삭제가 아니다. / TRUNCATE·DELETE의 효과나 세션 이동을 추가로 가정하지 않는다.')
A(4,"T(code VARCHAR2(8))에 'ALPHA'가 있다. VARCHAR2(3)으로 축소하면?",'현재5문자를 담지 못하므로 실패§ALP로 잘라 성공§NULL로 바꿔 성공§해당 행 자동 삭제','길이5인 현재 값은 새 최대 길이3을 넘는다. / ALTER 축소가 자동 잘라내기·NULL 변환·행 삭제를 수행하지 않는다.')
A(4,'ALTER로 열의 기본값을 바꿀 때 주된 대상은?','이후 값을 생략하는 삽입의 기본 표현식§기존 비NULL 값 전체 덮어쓰기§PK 자동 삭제§조회 순서 변경','기본값 정의 변경과 기존 행 UPDATE는 별개다. / 데이터 일괄 수정·키 제거·정렬 효과는 생기지 않는다.')
A(4,'T.v의 기존 값1, 기존 DEFAULT1이다. DEFAULT9로 변경한 뒤 v를 생략해 새 행을 넣었다. 기존·새 v는?','1과 9§9와 9§1과 1§NULL과 9','기존1은 보존하고 새 생략 값에9를 적용한다. / 기본값 정의 변경을 기존 값의 UPDATE로 해석하지 않는다.','ALTER TABLE T MODIFY (v DEFAULT 9);')

# 05 INSERT
A(5,'INSERT의 열 목록을 명시하는 주된 장점은?','값과 대상 열의 대응을 명확히 함§모든 제약 비활성화§중복 자동 제거§자동 COMMIT 보장','열 목록의 순서대로 VALUES를 대응한다. / 제약 무시·DISTINCT·자동 확정은 열 목록의 기능이 아니다.')
A(5,'v NUMBER DEFAULT8이며 DEFAULT ON NULL은 없다. v생략 행과 명시적 NULL 행의 v는?','8과 NULL§8과 8§NULL과 NULL§0과 NULL','일반 DEFAULT는 생략한 값에 적용한다. / 명시적 NULL까지 기본값으로 바꾸는 DEFAULT ON NULL과 구분한다.')
A(5,'빈 T(a NUMBER,b NUMBER)에 다음 INSERT 후(a,b)는?','(7,3)§(3,7)§(7,7)§(3,3)','열 목록 b,a의 순서이므로3→b,7→a다. / 테이블 선언 순서만 보고 값 순서를 읽지 않는다.','INSERT INTO T(b,a) VALUES(3,7);')
A(5,'빈 D에 추가되는 행 수는?','2§0§1§3','qty>0인 id1·3을 선택해 두 행을 넣는다. / INSERT SELECT는 조회된 모든 행을 넣으며 조건 밖 id2는 제외한다.','INSERT INTO D(id) SELECT id FROM S WHERE qty>0;',[T('S','id,qty',[[1,2],[2,0],[3,1]])])
A(5,'INSERT INTO T(a,b) VALUES(1);의 결과는?','열 목록과 값 개수가 달라 실패§b를1로 채워 성공§b를NULL로 채워 항상 성공§a 열 삭제','열 두 개에 값 하나를 제공해 대응 수가 맞지 않는다. / 열을 목록에서 생략하는 것과 VALUES 개수가 모자라는 것은 다르다.')
A(5,'T(id PK)에1이 있다. INSERT INTO T VALUES(1);의 결과는?','PK 중복으로 실패§기존 행 UPDATE§중복을 자동 무시§두 행 모두 유지','일반 INSERT는 중복 키를 허용하지 않는다. / UPSERT나자동 무시 기능을 명시 없이 가정하지 않는다.')
A(5,'D는 비어 있고 중복 허용이다. 다음 삽입 후 D.code는?','A,B 두 행§A,A,B 세 행§A 한 행§0행','SELECT DISTINCT가 A중복을 먼저 제거한다. / 대상의 중복 허용과 SELECT의 중복 제거는 서로 다른 단계다.','INSERT INTO D(code) SELECT DISTINCT code FROM S;',[T('S','code',[['A'],['A'],['B']])])
A(5,'T(id,v DEFAULT4)에 INSERT INTO T(id) VALUES(9); 후(id,v)는?','(9,4)§(4,9)§(9,NULL)§(9,0)','id9를 지정하고 생략된v에는 기본값4를 사용한다. / 지정 열과 기본값의 역할을 뒤집지 않는다.')
A(5,'T에는 기존 한 행이 있다. 아래 INSERT ALL이 추가하는 행 수는? 중복 제약은 없다.','2§1§3§0','DUAL 한 행에 대해 INTO 두 개를 적용해(2,20),(3,30)을 추가한다. / 기존 한 행은 추가 행 수에 포함하지 않는다.','INSERT ALL\n INTO T(id,v) VALUES(2,20)\n INTO T(id,v) VALUES(3,30)\nSELECT 1 FROM DUAL;')

# 06 SELECT structure
A(6,'SELECT 목록의 역할은?','반환할 열·표현식을 정한다§행을 반드시 정렬한다§테이블 정의를 변경한다§변경을 COMMIT한다','SELECT 목록은 결과 열을 정한다. / 정렬은 ORDER BY, 구조 변경은 DDL, 확정은 COMMIT의 역할이다.')
A(6,'SELECT v*2 AS doubled FROM T WHERE doubled>10은 왜 일반적으로 잘못되는가? T에 doubled라는 원래 열은 없다.','같은 블록 WHERE에서 SELECT 별칭을 쓸 수 없다§곱셈을 SELECT에 쓸 수 없다§별칭은 숫자로만 정한다§WHERE에는 비교를 쓸 수 없다','WHERE는 해당 SELECT 별칭을 참조할 수 없다. / v*2를 WHERE에 직접 쓰거나 바깥 조회에서 별칭을 사용한다. 곱셈·비교 자체는 유효하다.')
A(6,'다음 결과의(paid)는 id순으로?','18,35§9,7§2,5§11,12','각 행에서 qty×price를 계산해2×9=18,5×7=35다. / 한 열만 읽거나 덧셈으로 바꾸지 않는다.','SELECT qty*price AS paid FROM Sale ORDER BY id;',[T('Sale','id,qty,price',[[1,2,9],[2,5,7]])])
A(6,'SELECT 10-2*3 AS v FROM DUAL의 v는?','4§24§6§10','곱셈2×3=6을 먼저 계산하고10-6=4다. / 왼쪽부터(10-2)×3=24로 계산하지 않는다.','SELECT 10-2*3 AS v FROM DUAL;')
A(6,'표의 T에 다음 SELECT를 실행하면 결과 행 수와 열 수는?','3행·1열§1행·3열§2행·1열§3행·2열','SELECT 1은 각 입력 행마다 상수1을 출력해3행1열이다. / DISTINCT나집계가 없으므로 상수가 같다고 합치지 않는다.','SELECT 1 AS flag FROM T;',[T('T','id,v',[[1,4],[2,5],[3,6]])])
A(6,'SELECT a+b*2 FROM T에서 a=3,b=4이면 값은?','11§14§7§24','b*2=8을 먼저 계산해3+8=11이다. / (a+b)*2=14와 다르며 더하기·곱하기를 생략하지 않는다.','SELECT a+b*2 AS v FROM T;',[T('T','a,b',[[3,4]])])
A(6,'다음 SELECT에 입력이0행인 EmptyT라면 결과는?','0행§v=5인1행§v=NULL인1행§문법 오류','FROM의 입력 행이 없어 상수 표현식도 출력할 행이 없다. / DUAL 한 행 조회나그룹 없는 집계와 구분한다.','SELECT 5 AS v FROM EmptyT;')
A(6,'SELECT의 AS 별칭에 대한 옳은 설명은?','출력 열 이름을 바꾸며 원본 열 이름은 그대로다§원본 열도 즉시 RENAME한다§값을 모두 별칭 문자열로 바꾼다§기존 행을 삭제한다','별칭은 해당 결과의 이름이다. / ALTER RENAME, 문자열 대입, DELETE 효과가 아니다.','SELECT amount AS total FROM T;')
A(6,'다음 SELECT의 두 열(sale,fee)은?','(24,6)§(30,7.5)§(24,7.5)§(6,24)','sale=(price-discount)×qty=(10-2)×3=24,fee=price×0.2×qty=6이다. / sale 별칭을 다음 표현식이 자동 참조하는 것이 아니며 각 식을 별도로 읽는다.','SELECT (price-discount)*qty AS sale,\n price*0.2*qty AS fee FROM T;',[T('T','price,discount,qty',[[10,2,3]])])

# 07 WHERE basic comparisons
A(7,'WHERE 절이 남기는 조건의 평가값은?','TRUE만§FALSE만§TRUE와 UNKNOWN§UNKNOWN만','WHERE는 TRUE인 행만 통과시킨다. / NULL 비교의 UNKNOWN은 FALSE와 마찬가지로 결과에서 제외되지만 둘은 같은 논리값은 아니다.')
A(7,'숫자 v가NULL인 행을 찾는 조건은?','v IS NULL§v=NULL§v<>NULL§NOT(v=NULL)','IS NULL이 존재 여부를 판정한다. / NULL에 대한 =·<> 및 그 NOT은 UNKNOWN이라 NULL을 찾아내지 못한다.')
A(7,'다음 결과 id는?','2,3§1,2§1,2,3§3만','v>=10이므로 경계10인id2와15인id3을 포함한다. / >=를 >로 바꾸면id2를 놓치고 조건 밖5를 넣으면 안 된다.','SELECT id FROM T WHERE v>=10 ORDER BY id;',[T('T','id,v',[[1,5],[2,10],[3,15]])])
A(7,'v=8일 때 v>5 AND v<10의 값은?','TRUE§FALSE§UNKNOWN§문법 오류','8>5와8<10이 둘 다 TRUE다. / AND는 두 조건을 모두 요구하며 NULL이 없으므로 UNKNOWN이 생기지 않는다.')
A(7,'다음 결과 id는?','2§1§1,2§2,3','dept10이면서activeY인id2만 두 조건을 만족한다. / id1은N, id3은dept20이므로 OR처럼 합치면 안 된다.','SELECT id FROM T WHERE dept=10 AND active=\'Y\' ORDER BY id;',[T('T','id,dept,active',[[1,10,'N'],[2,10,'Y'],[3,20,'Y']])])
A(7,'v<>5의 결과가TRUE인 값은?','7§5§NULL§값을 모르는 모든 행','7은5와 다르다. / 5는FALSE, NULL은UNKNOWN이며 미확정 값을 자동으로 참이라고 판정하지 않는다.')
A(7,'다음 조건에 통과하는 id는?','1,3§1,2§2,3§1만','qty=0인id1 또는statusR인id3이 통과한다. / OR는 두 조건 중 하나만 참이어도 되지만id2는둘 다 거짓이다.','SELECT id FROM T WHERE qty=0 OR status=\'R\' ORDER BY id;',[T('T','id,qty,status',[[1,0,'N'],[2,2,'N'],[3,3,'R']])])
A(7,'NOT(v>=10)에서 v=8이면?','TRUE§FALSE§UNKNOWN§숫자8','8>=10은FALSE이고 NOT으로TRUE가 된다. / 조건의 반환 의미와 데이터 값8을 구분한다.')
A(7,'다음 결과 id는? 문자열은 대소문자 구분한다.','2,3§1,2§2만§1,3','v>=0인id1,2 중 id1은code가X여서 제외한다. id3은vNULL이라 UNKNOWN이지만 OR v IS NULL로 포함된다. / 괄호 안 AND와 바깥 OR를 분리해 평가한다.','SELECT id FROM T\nWHERE (v>=0 AND code<>\'X\') OR v IS NULL\nORDER BY id;',[T('T','id,v,code',[[1,0,'X'],[2,4,'Y'],[3,None,'X']])])

# 08 UPDATE
A(8,'UPDATE에서 WHERE를 생략하면 기본 대상은?','테이블의 모든 행§첫 행만§마지막 행만§어떤 행도 아님','WHERE가 없으면 모든 행이 갱신 대상이다. / 행의 저장 순서나첫 행 개념으로 대상이 제한되지 않는다.')
A(8,'UPDATE와 ALTER의 차이로 옳은 것은?','UPDATE는 행 값, ALTER는 구조를 바꾼다§두 명령 모두 구조만 변경§UPDATE는 조회만 수행§ALTER는 항상 모든 행 삭제','SET을 사용하는 UPDATE는 데이터 값 변경이다. / 열 추가·이름 변경 등 ALTER 구조 작업 및 DELETE와 구분한다.')
A(8,'갱신 후 T.v를 id순으로 나열하면?','5,12,17§7,12,17§5,10,15§5,2,2','v>=10인id2,3에2를 더한다. / id1은조건 밖이며 SET v=v+2를 v=2로 읽지 않는다.','UPDATE T SET v=v+2 WHERE v>=10;',[T('T','id,v',[[1,5],[2,10],[3,15]])])
A(8,'T의 세 행에 UPDATE T SET flag=\'Y\'를 실행했다. 변경 대상 수는?','3§0§1§2','WHERE가 없으므로 세 행 모두 대상이다. / 한 행씩 실행되는 표현식이라도 전체 대상 수를1로 줄이지 않는다.',"UPDATE T SET flag='Y';",[T('T','id,flag',[[1,'N'],[2,'N'],[3,'N']])])
A(8,'T(a,b)=(2,7)에서 다음 UPDATE 후(a,b)는?','(7,2)§(7,7)§(2,2)§(2,7)','같은 UPDATE의 우변은 갱신 전 행 값을 참조하므로 a←7,b←2다. / SET 항목을 순차 대입 프로그램처럼 읽어 b에 이미 바뀐a7을 넣지 않는다.','UPDATE T SET a=b,b=a;',[T('T','a,b',[[2,7]])])
A(8,'WHERE id=99에 맞는 행이 없으면 UPDATE 결과는?','오류 없이0행 변경§새 id99행 생성§첫 행 수정§전체 행 수정','대상 없는 UPDATE는 INSERT가 아니며0행을 변경한다. / 조건이 틀렸다고 첫 행·전체 행으로 대상을 바꾸지 않는다.','UPDATE T SET v=1 WHERE id=99;',[T('T','id,v',[[1,8]])])
A(8,'T.v에 CHECK(v>=0)가 있다. 아래 단일 UPDATE의 결과는?','문장 실패로 원래(4,1) 유지§(-1,-4) 모두 저장§첫 행만-1로 변경§NULL로 바꿔 성공','두 값에서5를 빼면둘 다음수여서 CHECK 위반이다. / 실패한 한 DML 문장의 일부만 남긴다고 가정하지 않는다.','UPDATE T SET v=v-5;',[T('T','id,v',[[1,4],[2,1]])])
A(8,'SELECT로 현재 값을 읽어10을 직접 SET하는 것보다 SET v=v+10이 직접 표현하는 것은?','각 대상 행의 기존v에10을 더함§모든v를10으로 통일§기존v를 삭제§행을10개 복제','우변 v는 각 대상 행의 기존 값이다. / SET v=10 및 INSERT와 의미가 다르다.')
A(8,'현재 T와 S는 표와 같다. S에 매칭이 없는 id2의 v까지 고려한 UPDATE 후 값은? S.id는고유다.','id1=9,id2=NULL§id1=9,id2=5§둘 다NULL§id1=9,id2=9','id1의 스칼라 조회는9, id2는0행이어서NULL이다. / 매칭이 없다고 UPDATE가 자동 생략되는 것은 아니며 바깥 WHERE가 없는 모든T행이 대상이다.','UPDATE T t SET v=(SELECT s.v FROM S s WHERE s.id=t.id);',[T('T','id,v',[[1,3],[2,5]]),T('S','id,v',[[1,9]])])

# 09 DELETE
A(9,'DELETE FROM T WHERE ...의 일반적인 대상은?','조건에 맞는 행§조건에 맞는 열 정의§테이블 이름§테이블의 자료형 전체','DELETE는 행을 제거한다. / 열 제거는 ALTER DROP COLUMN이며 테이블 정의 제거는 DROP TABLE이다.')
A(9,'DELETE FROM T와 DROP TABLE T를 구분한 설명은?','DELETE는 행 제거 후 테이블 정의 유지§둘 다 항상 정의 제거§DROP은 값만NULL로 변경§DELETE는 열 이름만 변경','WHERE 없는 DELETE는 모든 행을 지워도 테이블은 남는다. / DROP TABLE과 UPDATE NULL·RENAME을 혼동하지 않는다.')
A(9,'삭제 후 남는 id는?','1,3§2§1,2§0행','statusC인id2만 삭제한다. / 조건에 맞는 행이 남는 것이 아니라 제거되며id1,3은유지한다.',"DELETE FROM T WHERE status='C';",[T('T','id,status',[[1,'O'],[2,'C'],[3,'O']])])
A(9,'세 행이 있는 T에 DELETE FROM T를 실행한 직후 같은 세션의 COUNT(*)는?','0§3§1§NULL','WHERE 없이 모든행을 삭제해0행이다. / COUNT(*)의0과NULL은 다르며 테이블 정의는 남아 조회할 수 있다.','DELETE FROM T;',[T('T','id',[[1],[2],[3]])])
A(9,'다음 DELETE 후 남는 id는?','2,3§1§3만§0행','v<>0은id1의5에서TRUE, id2의0에서FALSE,id3의NULL에서UNKNOWN이다. / DELETE도 TRUE 대상만 지우므로NULL은 남는다.','DELETE FROM T WHERE v<>0;',[T('T','id,v',[[1,5],[2,0],[3,None]])])
A(9,'DELETE WHERE id=99에 맞는 행이 없으면?','0행 삭제§문법 오류§첫 행 삭제§전체 테이블 삭제','대상 조건이 참인 행이 없으므로 아무 행도 지우지 않는다. / 조건 불일치는 문법 오류가 아니며 대상을 자동 확대하지 않는다.','DELETE FROM T WHERE id=99;',[T('T','id',[[1],[2]])])
A(9,'초기 입력이 COMMIT되었다. 다음 순서 후 남는 id는?','1,2§2만§1만§0행','DELETE한id1은 COMMIT 전 ROLLBACK으로복원된다. / ROLLBACK은 초기 COMMIT된id2까지 지우지 않으며 DELETE의 미확정 변경만 취소한다.','DELETE FROM T WHERE id=1;\nROLLBACK;',[T('T','id',[[1],[2]])])
A(9,'특정 행만 지우려면 무엇을 확인해야 하는가?','DELETE의 WHERE가 원하는 대상만 TRUE로 만드는지§SELECT 별칭의 글자 수§테이블 출력 순서만§데이터 파일 이름만','삭제 대상은 WHERE 논리로 결정된다. / 별칭·정렬·파일명은 삭제 대상을 대신 지정하지 않는다.')
A(9,'표에서 중복 code=A인 행을 모두 지우되 B는 남기는 DELETE 결과 행 수는?','1§0§2§3','조건 code=A가 id1,2 모두에 참이므로 두 행을 삭제하고id3하나만 남긴다. / DELETE가중복 중첫 행만 지운다는 가정은 틀리다.',"DELETE FROM T WHERE code='A';",[T('T','id,code',[[1,'A'],[2,'A'],[3,'B']])])

# 10 MERGE: each form uses a different branch boundary.
A(10,'MERGE의 ON 조건이 주로 결정하는 것은?','원본 행이 대상과 매칭되는지§최종 출력 정렬§트랜잭션 자동 확정 여부§모든제약 해제 여부','ON은 매칭에 따른 UPDATE/INSERT 분기를 판단한다. / ORDER BY·COMMIT·제약 비활성화의 역할이 아니다.')
A(10,'MERGE의 UPDATE 대상 열에 대한 제한으로 옳은 것은?','ON에서 참조한 열은 UPDATE SET으로 바꿀 수 없다§모든 숫자 열은 갱신 불가§대상과 원본 열 이름은 반드시 같아야 함§INSERT절이 없으면 UPDATE 불가','Oracle MERGE는 ON 참조열 갱신을 제한한다. / 숫자열 일반 갱신, 서로 다른 이름의 대응, UPDATE절만의 사용까지 금지하지 않는다.')
A(10,'MERGE 후 D의(id,v)는? D.id와 S.id는각각고유다.','(1,8),(2,9)§(1,3),(2,9)§(1,8)만§(2,9)만','id1은매칭되어8로 갱신, id2는미매칭되어9로 삽입된다. / ON이TRUE인 행을 INSERT하거나 전체대상을 교체하는 작업이 아니다.','MERGE INTO D d USING S s ON(d.id=s.id)\nWHEN MATCHED THEN UPDATE SET d.v=s.v\nWHEN NOT MATCHED THEN INSERT(id,v) VALUES(s.id,s.v);',[T('D','id,v',[[1,3]]),T('S','id,v',[[1,8],[2,9]])])
A(10,'WHEN MATCHED THEN UPDATE만 있는 MERGE에서 미매칭 원본행은?','삽입되지 않는다§자동 INSERT된다§대상 첫행을 덮는다§반드시 문법오류','INSERT 분기가 없으므로 미매칭 원본행을 새로 넣지 않는다. / UPDATE절만 있는 MERGE가 가능하며 첫대상을 대신 선택하지 않는다.')
A(10,'다음 MERGE 후 D는? 원본·대상 id는고유다.','(2,0)만§(1,0),(2,0)§0행§(1,1),(2,0)','id1을1→0으로 UPDATE한 뒤 갱신후v=0 조건으로삭제한다. id2는원본과매칭되지 않아 DELETE WHERE대상이 아니다. / MERGE DELETE는 대상전체 정리명령이 아니다.','MERGE INTO D d USING S s ON(d.id=s.id)\nWHEN MATCHED THEN UPDATE SET d.v=d.v-s.delta\nDELETE WHERE d.v=0;',[T('D','id,v',[[1,1],[2,0]]),T('S','id,delta',[[1,1]])])
A(10,'ON(0=1)이고 INSERT절만 있는 MERGE에서 원본행은?','모두 미매칭 삽입 후보§모두 기존행 갱신 후보§자동 전부 삭제§원본을 한행으로 집계','상수FALSE이므로 매칭이없어INSERT분기 대상이다. / 실제삽입은그밖의 제약도만족해야하며 UPDATE·DELETE·집계로변하지 않는다.')
A(10,'매칭id1이 UPDATE의 WHERE를 만족하지 못했다. INSERT절은존재한다. 최종D는?','(1,5)만§(1,0)만§(1,5),(1,0)§0행','id1은ON에서이미매칭이다. s.v>0이FALSE라UPDATE를건너뛰어5를유지한다. / UPDATE생략을미매칭으로다시분류해INSERT하지 않는다.','MERGE INTO D d USING S s ON(d.id=s.id)\nWHEN MATCHED THEN UPDATE SET d.v=s.v WHERE s.v>0\nWHEN NOT MATCHED THEN INSERT(id,v) VALUES(s.id,s.v);',[T('D','id,v',[[1,5]]),T('S','id,v',[[1,0]])])
A(10,'MERGE의 USING이 지정하는 것은?','비교·반영할 원본 데이터§항상 최종 정렬열§삭제할 모든 제약§COMMIT 간격','USING은원본테이블·조회결과를지정한다. / ON은매칭조건이며 USING은정렬·제약삭제·확정주기설정이 아니다.')
A(10,'MERGE 후 D는? id는각표에서고유하고 D.id는PK다.','(1,7),(3,4)§(1,7),(2,-1),(3,4)§(1,3),(3,4)§(1,7)만','id1은갱신하여7, id2는미매칭이지만s.v>0이FALSE라삽입생략, id3은4로삽입한다. / INSERT WHERE와UPDATE분기조건을혼동하지 않는다.','MERGE INTO D d USING S s ON(d.id=s.id)\nWHEN MATCHED THEN UPDATE SET d.v=s.v\nWHEN NOT MATCHED THEN INSERT(id,v) VALUES(s.id,s.v)\nWHERE s.v>0;',[T('D','id,v',[[1,3]]),T('S','id,v',[[1,7],[2,-1],[3,4]])])

# 11 WHERE compound predicates and pattern boundaries
A(11,'x BETWEEN 3 AND 7의 경계 처리로 옳은 것은?','3과 7을 모두 포함한다§두 경계를 모두 제외한다§3만 제외한다§7만 제외한다','BETWEEN은 x>=3 AND x<=7과 같은 경계 포함 조건이다. / > 또는 <로만 바꾸면 경계 행을 빠뜨린다.')
A(11,"LIKE에서 '_'와 '%'의 의미를 구분하면?",'문자 한 개와 문자 0개 이상§둘 다 숫자 한 개§둘 다 문자 한 개§한 개 이상과 정확히 두 개','밑줄은 한 문자를 요구하고 퍼센트는 빈 길이도 포함한다. / 따라서 A_에는 A만으로 부족하지만 A%에는 A가 맞는다.')
A(11,'다음 조건을 통과하는 id는?','1,3§1,2§2,3§3만','AND가 OR보다 먼저이므로 a=1 OR (b=1 AND c=1)이다. / id1은 a로 통과하고 id3은 b와c로 통과하며 id2는 c가0이라 제외된다.','SELECT id FROM T WHERE a=1 OR b=1 AND c=1 ORDER BY id;',[T('T','id,a,b,c',[[1,1,0,0],[2,0,1,0],[3,0,1,1]])])
A(11,"code는 VARCHAR2이며 대소문자를 구분한다. LIKE 'A_%'의 결과는?",'AB, ABC§A, AB, ABC§A만§BA만','밑줄 때문에 A 다음 최소 한 문자가 있어야 하므로 AB와 ABC가 맞는다. / A는 너무 짧고 BA는 첫 문자가 다르다.',"SELECT code FROM T WHERE code LIKE 'A_%' ORDER BY code;",[T('T','code',[['A'],['AB'],['ABC'],['BA']])])
A(11,'NULL도 포함하여 3~7 범위 밖인 x를 찾는다. 맞는 조건은?','x NOT BETWEEN 3 AND 7 OR x IS NULL§x NOT BETWEEN 3 AND 7§x<3 AND x>7§NOT(x BETWEEN 3 AND 7 OR x IS NULL)','범위 밖 조건만으로 NULL은 UNKNOWN이라 빠진다. OR x IS NULL을 더해야 한다. / x<3 AND x>7은 동시에 만족할 수 없고 NOT(x BETWEEN 3 AND 7 OR x IS NULL)은 NULL을 오히려 제외한다.')
A(11,'x IN(2,2,5)를 평가할 때 x=2인 입력 한 행은 결과에 몇 번 나타나는가? DISTINCT는 없다.','1번§2번§3번§0번','IN 목록은 조건 판정이며 목록의 중복 수만큼 입력 행을 복제하지 않는다. / JOIN으로 행을 결합할 때의 중복 증식과 구분한다.','SELECT x FROM T WHERE x IN(2,2,5);',[T('T','x',[[2]])])
A(11,"정확히 'A_'로 시작하는 문자열을 찾는다. ESCAPE '!'를 쓴 다음 결과는?",'A_1만§A_1과 AB1§AB1만§0행','!_는 와일드카드가 아닌 실제 밑줄을 뜻한다. / A!_%는 A와 밑줄 뒤 임의 문자열이므로 AB1은 통과하지 않는다.',"SELECT code FROM T WHERE code LIKE 'A!_%' ESCAPE '!' ORDER BY code;",[T('T','code',[['A_1'],['AB1'],['BA_']])])
A(11,'다음 조건이 참인 x 값은?','1과 9§1만§9만§5만','NOT BETWEEN은 경계3·7 안쪽을 제외하므로 1과9가 남는다. / AND가 아니라 두 바깥 범위를 OR로 연결한 의미다.','SELECT x FROM T WHERE x NOT BETWEEN 3 AND 7 ORDER BY x;',[T('T','x',[[1],[3],[5],[7],[9]])])
A(11,'다음 WHERE를 통과하는 id는?','2,4§1,2,4§2만§3,4','id2는 qty>0이 거짓이지만 urgent=Y라 통과한다. id4도 urgent=Y다. / id1의 UNKNOWN OR FALSE는 UNKNOWN, id3의 FALSE OR FALSE는 FALSE다.','SELECT id FROM T\nWHERE (qty>0 AND status=\'O\') OR urgent=\'Y\'\nORDER BY id;',[T('T','id,qty,status,urgent',[[1,None,'O','N'],[2,0,'O','Y'],[3,2,'C','N'],[4,None,'C','Y']])])

# 12 Ordering and DISTINCT
A(12,'ORDER BY가 없는 SELECT의 결과 순서에 대해 옳은 것은?','특정 순서가 보장되지 않는다§항상 PK 오름차순§항상 입력 순서§항상 최신 행 먼저','정렬 요구는 최종 ORDER BY로 표현한다. / 실행 계획이나 현재 관찰된 순서를 영구 규칙으로 삼지 않는다.')
A(12,'SELECT DISTINCT a,b는 무엇을 중복 제거하는가?','(a,b) 전체 조합§a만§b만§각 열의 값을 따로 합친 목록','DISTINCT는 SELECT 결과 행 전체를 비교한다. / a가 같아도 b가 다르면 별개 조합이다.')
A(12,'다음 결과는?','(1,7),(1,9),(2,7)§(1,7),(2,7)§(1,7),(1,7),(1,9),(2,7)§(1,9),(2,7)','중복 (1,7) 두 행을 하나로 만들고 a,b 순서로 정렬한다. / a만 중복 제거하거나 DISTINCT를 무시하면 다른 결과가 된다.','SELECT DISTINCT a,b FROM T ORDER BY a,b;',[T('T','a,b',[[1,7],[1,7],[1,9],[2,7]])])
A(12,'다음 결과의 id 순서는?','2,1,3§3,1,2§1,2,3§2,3,1','v ASC NULLS FIRST이므로 NULL인id2가 먼저, 값5인id1,9인id3 순이다. / NULL을0으로 계산하는 것이 아니라 위치 규칙을 적용한다.','SELECT id FROM T ORDER BY v ASC NULLS FIRST;',[T('T','id,v',[[1,5],[2,None],[3,9]])])
A(12,'점수가 같은 행까지 항상 같은 id 순서로 보여 주려면? id는 고유하다.','ORDER BY score DESC,id ASC§ORDER BY score DESC만§ORDER BY 1만; 첫 열은 score§ORDER BY score,score','동점일 때 고유 id를 보조 키로 써 전체 순서를 정한다. / score를 반복하거나 score만 정렬하면 동점 순서가 결정되지 않는다.')
A(12,'다음 SQL의 ORDER BY 2는 어느 열을 기준으로 하는가?','b DESC§a DESC§원본 두 번째 입력 행§결과 행을 두 개만 반환','번호2는 SELECT 목록 둘째 표현식 b다. / 행 위치나 반환 개수 제한이 아니다.','SELECT a,b FROM T ORDER BY 2 DESC;')
A(12,'NULL을 포함한 다음 DISTINCT 결과의 행 수는?','3§4§2§1','NULL,1,2의 세 결과 값이 남는다. / DISTINCT의 NULL 중복 처리를 일반 비교 NULL=NULL의 UNKNOWN과 동일하게 해석하지 않는다.','SELECT DISTINCT v FROM T;',[T('T','v',[[None],[None],[1],[2]])])
A(12,'Oracle에서 ORDER BY v DESC만 쓰면 NULL의 기본 위치는?','앞쪽§뒤쪽§NULL 행 제거§무조건 오류','DESC의 기본은 NULLS FIRST다. / ASC의 기본과 뒤집어 기억하거나 정렬을 행 제거로 해석하지 않는다.')
A(12,'다음 결과의 id 순서는?','3,2,1§1,2,3§2,3,1§3,1,2','dept가10인id2,3이 먼저이며 같은dept에서는 score DESC라90인id3이 먼저다. / 그 뒤 dept20의id1이 온다.','SELECT id FROM T ORDER BY dept ASC,score DESC;',[T('T','id,dept,score',[[1,20,99],[2,10,70],[3,10,90]])])

# 13 Single-row character/numeric functions
A(13,'단일행 함수와 집계함수를 구분한 설명은?','단일행 함수는 각 입력 행의 값을 가공한다§단일행 함수는 항상 전체를 한 행으로 줄인다§집계함수만 SELECT에서 사용 가능§단일행 함수는 NULL을 무조건0으로 바꾼다','UPPER·ROUND 등은 각 행에 적용한다. / 행을 묶는 집계와 다르며 NULL 처리는 함수별 규칙을 확인한다.')
A(13,'FLOOR(-2.3)과 TRUNC(-2.3)는?','-3과 -2§-2와 -2§-3과 -3§2와 3','FLOOR는 값 이하의 가장 큰 정수-3, TRUNC는 소수 부분을 잘라-2다. / 음수에서 내림과0 방향 절삭은 다르다.')
A(13,'다음 값(s,n)은?','(CDE,3)§(BCD,3)§(CDEF,4)§(CDE,6)','SUBSTR는1부터 세어3번째 C에서3문자 CDE를 뽑는다. LENGTH는 그 결과의 길이3이다. / 0기반 시작이나 원문 길이를 적용하지 않는다.',"SELECT SUBSTR('ABCDEF',3,3) AS s,\n LENGTH(SUBSTR('ABCDEF',3,3)) AS n FROM DUAL;")
A(13,'다음 값(r,t)은?','(12.6,12.5)§(12.5,12.6)§(13,12)§(12.56,12.56)','소수1자리에서 ROUND는 다음자리6으로 반올림12.6, TRUNC는 버려12.5다. / 자릿수 인자1을 정수 자리로 읽지 않는다.','SELECT ROUND(12.56,1) AS r,TRUNC(12.56,1) AS t FROM DUAL;')
A(13,'다음 문자열은?','00AB-CD§AB-CD00§000AB-CD§00AB_CD','REPLACE로 AB_CD가 AB-CD가 되고 길이5를7로 LPAD해 왼쪽0두 개를 붙인다. / 목표 길이7은 추가 문자 수가 아니며 RPAD처럼 오른쪽에 붙이지 않는다.',"SELECT LPAD(REPLACE('AB_CD','_','-'),7,'0') AS v FROM DUAL;")
A(13,'다음 INSTR 값은?','4§2§3§0','ANA의 첫 등장은 BANANA의2, 다음 시작 검색에서4의 ANA도 찾는다. / 일반 INSTR의 겹치는 검색과 정규식 비중첩 검색을 혼동하지 않는다.',"SELECT INSTR('BANANA','ANA',1,2) AS p FROM DUAL;")
A(13,'다음 값(a,c,f)은?','(3,-2,-3)§(-3,-2,-3)§(3,-3,-2)§(3,2,3)','ABS(-3)=3이다. -2.4 이상 최소 정수는-2, 이하 최대 정수는-3이다. / 올림·내림을 절댓값 기준으로 적용하지 않는다.','SELECT ABS(-3) AS a,CEIL(-2.4) AS c,FLOOR(-2.4) AS f FROM DUAL;')
A(13,'다음 문자열은?','SQL§ sql §sql§SQL  ','TRIM으로 양쪽 공백을 제거하고 UPPER로 소문자를 대문자로 바꾼다. / 원문 공백을 유지하거나 LOWER를 적용한 결과가 아니다.',"SELECT UPPER(TRIM(' sql ')) AS v FROM DUAL;")
A(13,'다음 값(m,s)은?','(2,-1)§(3,-1)§(2,1)§(0,0)','17=5×3+2이므로 MOD는2, SIGN(-8)은 음수 부호-1이다. / 몫3과 나머지2를 구분하고 SIGN을 절댓값으로 읽지 않는다.','SELECT MOD(17,5) AS m,SIGN(-8) AS s FROM DUAL;')

# 14 Date and conversion functions
A(14,'TO_DATE와 TO_CHAR의 역할을 바르게 연결하면?','문자→날짜, 값→표시 문자열§날짜→문자, 문자→날짜§둘 다 행을 정렬§둘 다 숫자를 합산','TO_DATE는 형식에 따라 날짜로 해석하고 TO_CHAR는 표시 문자열을 만든다. / 출력 모양을 바꾸는 것과 내부 날짜를 만드는 것을 구분한다.')
A(14,'DATE 값에1/24를 더하면?','한 시간 증가§하루 증가§한 분 증가§24일 증가','Oracle DATE에서 숫자1은 하루라1/24는 한 시간이다. / 날짜 산술의 단위를 시·분으로 직접 대입하지 않는다.')
A(14,'NLS_CALENDAR=GREGORIAN이다. 다음 문자열은?','2026-02-28§2026-03-03§2026-02-31§2026-01-31','1월31일에서 한 달 뒤는2월 말일28일로 조정된다. / 31일을 더하는 연산이나 존재하지 않는2월31일이 아니다.',"SELECT TO_CHAR(ADD_MONTHS(DATE '2026-01-31',1),'YYYY-MM-DD') AS d FROM DUAL;",source='oracle19-add-months')
A(14,'다음 값은?','2026/10/05§2026-10-05§20261005§날짜형 자체','TO_CHAR의 형식 YYYY/MM/DD에 따라 슬래시가 있는 문자열이다. / TO_DATE의 입력 형식과 최종 표시 형식을 구분한다.',"SELECT TO_CHAR(TO_DATE('20261005','YYYYMMDD'),'YYYY/MM/DD') AS d FROM DUAL;",source='oracle19-todate')
A(14,'NLS_CALENDAR=GREGORIAN이다. 다음 값은?','1§28/30§28/31§0','3월31일과2월28일은 모두 해당 월의 말일이므로 MONTHS_BETWEEN은 정수1이다. / 항상 일수 차이를30이나31로 나누는 함수가 아니다.','SELECT MONTHS_BETWEEN(DATE \'2026-03-31\',DATE \'2026-02-28\') AS m FROM DUAL;',source='oracle19-months-between')
A(14,'다음 두 값(y,m)은?','(2026,10)§(26,10)§(2026,15)§(10,2026)','YEAR는2026,MONTH는10을 수치로 추출한다. / DAY15를 MONTH로 쓰거나 표시용 YY와 혼동하지 않는다.',"SELECT EXTRACT(YEAR FROM DATE '2026-10-15') AS y,\n EXTRACT(MONTH FROM DATE '2026-10-15') AS m FROM DUAL;")
A(14,'DATE에 저장된 시각이10월15일18:30일 때 아래 결과는?','2026-10-15 00:00§2026-10-15 18:30§2026-10-01 00:00§2026-10-16 00:00','TRUNC(d)는 날짜의 시각 부분을 잘라 당일 자정으로 만든다. / 월 단위 절삭이나 다음날 반올림이 아니다.',"SELECT TO_CHAR(TRUNC(TO_DATE('20261015 1830','YYYYMMDD HH24MI')),\n 'YYYY-MM-DD HH24:MI') AS d FROM DUAL;",source='oracle19-trunc-date')
A(14,'아래 두 숫자 표시 문자열(a,b)은? 보기의 작은따옴표는 문자열 경계를 나타낸다.',"('0012','12')§('12','12')§('0012','0012')§(' 0012','   12')",'0000의 0은 필수 숫자 자리를 0으로 채워 0012를 만든다. 9999의 9가 만든 앞쪽 빈자리와 양수 부호 공백은 FM으로 제거되어 12다. / FM은 공백 채움을 억제하지만 숫자 형식 0이 요구하는 필수 0까지 제거하지 않는다.',"SELECT TO_CHAR(12,'FM0000') AS a,\n TO_CHAR(12,'FM9999') AS b FROM DUAL;",source='https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Format-Models.html')
A(14,'NLS_CALENDAR=GREGORIAN이다. 다음 값은?','2028-02-29§2028-02-28§2028-03-01§2028-01-31','2028년은 윤년이고2월의 마지막 날은29일이다. / LAST_DAY는 같은 월의 말일이며 다른 월로 이동하지 않는다.',"SELECT TO_CHAR(LAST_DAY(DATE '2028-02-10'),'YYYY-MM-DD') AS d FROM DUAL;")

# 15 NULL values, arithmetic, aggregate absence and Oracle empty strings
A(15,'NULL과 숫자0의 관계로 옳은 것은?','NULL은 값 부재·모름이며0이라는 값과 다르다§둘은 모든 SQL에서 같다§NULL은 항상 음수§0은 집계에서 항상 제외','0은 실제 숫자라 계산·COUNT에 포함될 수 있다. / NULL을0으로 취급하려면 의도한 대체 표현식이 필요하다.')
A(15,'Oracle의 빈 문자열과 공백 한 칸을 구분하면?',"''은 NULL로 취급되고 ' '은 한 문자다§둘 다 한 문자§둘 다 숫자0§공백만 NULL이다","길이0 문자열은 Oracle에서 NULL로 취급한다. / 공백 한 칸은 길이1인 값이므로 TRIM 전에는 빈 문자열과 다르다.")
A(15,'다음 결과(c,s)는?','(2,10)§(3,10)§(2,NULL)§(3,0)','COUNT(v)는0과10 두 값을 세고 SUM은0+10=10이다. / NULL 행은 값 집계에서 제외하지만 숫자0은 제외하지 않는다.','SELECT COUNT(v) AS c,SUM(v) AS s FROM T;',[T('T','v',[[None],[0],[10]])])
A(15,'숫자 NULL+5의 결과는?','NULL§5§0§항상 오류','값이 없는 피연산자가 포함된 일반 산술 결과는NULL이다. / 더하기가 NULL을 자동0으로 바꾸지는 않는다.','SELECT CAST(NULL AS NUMBER)+5 AS v FROM DUAL;')
A(15,'다음 두 합계(a,b)는?','(3,10)§(10,10)§(NULL,10)§(3,3)','x+y는(3,NULL)이므로 SUM은3이다. 따로 SUM(x)=6,SUM(y)=4라 합10이다. / 행별 덧셈의 NULL 전파와 열별 집계의 NULL 제외를 구분한다.','SELECT SUM(x+y) AS a,SUM(x)+SUM(y) AS b FROM T;',[T('T','x,y',[[1,2],[5,None],[None,2]])])
A(15,'그룹 없는 집계에 입력이0행일 때 COUNT(*)와 SUM(v)는?','0과 NULL, 결과1행§0과0, 결과0행§NULL과NULL, 결과1행§0과NULL, 결과0행','빈 입력도 그룹 없는 집계는 한 행의 결과를 낸다. / COUNT는0이고 SUM은NULL이며 집계 값과 결과 행 수는 다르다.','SELECT COUNT(*),SUM(v) FROM T WHERE 1=0;')
A(15,'다음 문자열은?','AB§NULL§A NULL B§빈 문자열','Oracle 문자열 연결에서 NULL을 끼워도 비NULL인 A와B가 연결된다. / 일반 숫자 덧셈의 NULL 전파를 연결 연산에 그대로 적용하지 않는다.',"SELECT 'A'||CAST(NULL AS VARCHAR2(1))||'B' AS v FROM DUAL;",source='oracle19-concat')
A(15,'COUNT(*)와 COUNT(v)의 차이는?','전체 행 수와 v가 비NULL인 행 수§둘 다 항상 같은 수§COUNT(*)만 NULL 행 제외§COUNT(v)는 서로 다른 값만 센다','COUNT(v)는 비NULL 값의 중복도 각 행마다 센다. / 서로 다른 값은 COUNT(DISTINCT v)이며 COUNT(*)는 NULL 여부와 무관하게 행을 센다.')
A(15,'다음 AVG와 AVG(NVL)의 값은?','10과5§5와5§10과10§NULL과5','AVG(v)는NULL 제외로(0+20)/2=10이다. NVL로NULL 둘을0으로 바꾸면 총4개라20/4=5다. / 대체 시점이 분모를 바꾼다.','SELECT AVG(v) AS a,AVG(NVL(v,0)) AS b FROM T;',[T('T','v',[[0],[20],[None],[None]])])

# 16 Three-valued predicates
A(16,'NOT UNKNOWN의 논리값은?','UNKNOWN§TRUE§FALSE§숫자0','판단 불가를 부정해도 참·거짓을 확정할 수 없어 UNKNOWN이다. / NOT을 NULL 검사나 FALSE의 부정처럼 적용하지 않는다.')
A(16,'WHERE와 CHECK가 UNKNOWN을 다루는 방식을 바르게 비교하면?','WHERE는 제외하고 CHECK는 그 이유만으로 거부하지 않는다§둘 다 항상 거부§둘 다 항상 TRUE로 바꾼다§WHERE만 TRUE로 바꾼다','WHERE는 TRUE만 남기고 CHECK는 FALSE를 거부한다. / CHECK 통과가 UNKNOWN을 TRUE라는 논리값으로 변환했다는 뜻은 아니다.')
A(16,'다음 WHERE 결과 id는?','2,3§1,2§2만§3만','id2는 v<>5가 TRUE이고 id3은 IS NULL이 TRUE다. / NULL<>5 자체는 UNKNOWN이지만 OR의 TRUE가 전체를 결정한다.','SELECT id FROM T WHERE v<>5 OR v IS NULL ORDER BY id;',[T('T','id,v',[[1,5],[2,7],[3,None]])])
A(16,'FALSE AND UNKNOWN과 TRUE OR UNKNOWN은 각각?','FALSE와 TRUE§UNKNOWN과 UNKNOWN§TRUE와 FALSE§FALSE와 UNKNOWN','AND에 FALSE가 있으면 전체 FALSE, OR에 TRUE가 있으면 전체 TRUE다. / UNKNOWN이 포함되었다고 모든 조합이 UNKNOWN은 아니다.')
A(16,'다음 두 조건 A,B의 결과를 id 집합으로 비교하면? A:NOT(v=5), B:v<>5 OR v IS NULL','A={2}, B={2,3}§둘 다{2,3}§A={2,3}, B={2}§둘 다{2}','id3의 v=5는 UNKNOWN이고 NOT도 UNKNOWN이므로 A에서는 빠진다. / B는 NULL을 명시적으로 포함하여 id3도 남는다.',data=[T('T','id,v',[[1,5],[2,8],[3,None]])])
A(16,'x=2일 때 x NOT IN(1,NULL)의 논리값은?','UNKNOWN§TRUE§FALSE§2','2<>1은 TRUE지만 2<>NULL은 UNKNOWN이며 AND 결과는 UNKNOWN이다. / 목록에2가 없다는 이유만으로 TRUE라고 결론내리지 않는다.')
A(16,'다음 결과 id는?','1,3§1만§2,3§0행','id1은 TRUE OR UNKNOWN이 TRUE다. id3은 v IS NULL이 TRUE다. / id2는 FALSE OR FALSE라 제외하며 NULL이 있는 모든 행을 무조건 버리는 규칙도 아니다.','SELECT id FROM T WHERE flag=1 OR v IS NULL ORDER BY id;',[T('T','id,flag,v',[[1,1,5],[2,0,7],[3,None,None]])])
A(16,'NULL인 x에 x=x를 적용하면?','UNKNOWN§TRUE§FALSE§항상 오류','일반 비교에서 NULL은 자기 자신과도 TRUE로 비교되지 않는다. / DECODE의 특수 NULL 처리나 IS NULL 조건을 일반 등호에 적용하지 않는다.')
A(16,'다음 조건 A,B 중 id3(NULL,NULL)을 포함하는 것은? A:(a=1 OR b=1), B:NOT(a<>1 AND b<>1)','둘 다 포함하지 않는다§A만 포함§B만 포함§둘 다 포함','id3에서 각 비교는 UNKNOWN이다. A의 OR도 UNKNOWN, B의 AND와 NOT도 UNKNOWN이다. / 두 조건이 논리적으로 같은 결과여도 UNKNOWN은 WHERE를 통과하지 않는다.',data=[T('T','id,a,b',[[1,1,2],[2,2,2],[3,None,None]])])

# 17 NULL-related functions
A(17,'NVL(x,0)의 의미는?','x가 NULL이면0, 아니면x§x가0이면NULL§항상0§x가 음수일 때만0','NVL은 NULL 여부로 대체한다. / 숫자0이나 음수 자체를 NULL로 취급하지 않는다.',source='oracle19-nvl')
A(17,'COALESCE(NULL,0,9)의 값은?','0§9§NULL§오류','왼쪽부터 첫 비NULL인0을 선택한다. / 0은 값이므로 건너뛰지 않으며 마지막 인자를 무조건 고르지 않는다.',source='oracle19-coalesce')
A(17,'다음 결과 id별 r은?','5,0,7§5,9,7§0,0,0§NULL,0,7','id1은 NVL(NULL,5)=5, id2의0은 그대로, id3의7도 그대로다. / NVL은0을 두 번째 인자로 바꾸지 않는다.','SELECT NVL(v,5) AS r FROM T ORDER BY id;',[T('T','id,v',[[1,None],[2,0],[3,7]])],source='oracle19-nvl')
A(17,'NULLIF(4,4)와 NULLIF(4,9)는?','NULL과4§4와NULL§0과4§NULL과9','같으면 NULL, 다르면 첫 인자4를 반환한다. / 다를 때 둘째 인자9를 반환하는 함수가 아니다.','SELECT NULLIF(4,4),NULLIF(4,9) FROM DUAL;',source='oracle19-nullif')
A(17,'다음 결과(v)는 id순으로?','NULL,5§오류,5§0,5§NULL,10','id1의 분모 NULLIF(0,0)는 NULL이라 나눗셈 결과도 NULL이다. id2는10/2=5다. / 분모0 오류를 피하되 결과를0으로 대체하는 식은 아니다.','SELECT amount/NULLIF(qty,0) AS v FROM T ORDER BY id;',[T('T','id,amount,qty',[[1,10,0],[2,10,2]])],source='oracle19-nullif')
A(17,'NVL2(x,10,20)에서 x가NULL과0일 때 결과는?','20과10§10과20§20과20§10과10','NVL2는 x가 비NULL이면 둘째 인자, NULL이면 셋째 인자를 고른다. / 숫자0은 비NULL이므로10이다.','SELECT NVL2(NULL,10,20),NVL2(0,10,20) FROM DUAL;',source='https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/NVL2.html')
A(17,'다음 COALESCE 결과는 id순으로?','4,0,9§4,7,9§NULL,0,9§4,0,NULL','id1은 b4, id2는 첫 비NULL a0, id3은 두 열이 NULL이라9다. / 첫 비NULL이0이어도 멈추며 기본값9는 모든 앞 값이 NULL일 때 사용한다.','SELECT COALESCE(a,b,9) AS v FROM T ORDER BY id;',[T('T','id,a,b',[[1,None,4],[2,0,7],[3,None,None]])],source='oracle19-coalesce')
A(17,'다음 식의 값은?','3§NULL§8§0','안쪽 NVL(NULL,3)=3이므로 바깥 NVL은3을 그대로 반환한다. / 가장 바깥 대체값8을 항상 선택하지 않는다.','SELECT NVL(NVL(CAST(NULL AS NUMBER),3),8) AS v FROM DUAL;',source='oracle19-nvl')
A(17,'T에 v=2,NULL이 있다. 두 식 SUM(NVL(v,5)), NVL(SUM(v),5)의 값은?','7과2§7과7§2과2§NULL과5','첫 식은 행별로 NULL→5를 하여2+5=7이다. 둘째는 SUM이2이므로 NVL로 바뀌지 않는다. / 집계 전 대체와 집계 결과 대체는 같지 않다.','SELECT SUM(NVL(v,5)),NVL(SUM(v),5) FROM T;',[T('T','v',[[2],[None]])],source='oracle19-nvl')

# 18 CASE and DECODE
A(18,'검색 CASE에서 여러 WHEN이 TRUE이면?','앞에서 처음 TRUE인 THEN을 반환한다§마지막 TRUE를 반환한다§모든 THEN을 합산한다§반드시 오류','CASE는 순서대로 첫 TRUE 분기를 선택한다. / 조건이 겹친다고 결과를 합치거나 마지막 분기로 덮지 않는다.')
A(18,'CASE x WHEN NULL THEN 1 ELSE 0 END에서 x=NULL이면?','0§1§NULL§오류','단순 CASE는 등호 비교이므로 NULL과 NULL이 TRUE가 되지 않아 ELSE0이다. / 검색 CASE WHEN x IS NULL 또는 DECODE의 NULL 처리를 혼동하지 않는다.')
A(18,'다음 결과는?','B§A§C§NULL','score85는 첫 조건>=80을 만족해 B를 반환한다. / 더 높은 등급 A가 뒤에 있어도 이미 참인 앞 분기를 건너뛰지 않는다.','SELECT CASE WHEN score>=80 THEN \'B\'\n WHEN score>=90 THEN \'A\' ELSE \'C\' END AS grade\nFROM T;',[T('T','score',[[85]])])
A(18,'CASE WHEN v>0 THEN 1 END에서 v=-2이면?','NULL§0§1§-2','맞는 WHEN이 없고 ELSE가 생략되어 NULL이다. / ELSE0은 작성하지 않은 규칙이므로 추가로 가정하지 않는다.','SELECT CASE WHEN v>0 THEN 1 END AS r FROM T;',[T('T','v',[[-2]])])
A(18,'다음 총액은?','26§30§20§16','A행은10×2=20, B행은6을 그대로 더해26이다. / 두 행을 모두 두 배로 하거나 ELSE 값을 누락하지 않는다.','SELECT SUM(CASE WHEN kind=\'A\' THEN amount*2 ELSE amount END) AS total\nFROM T;',[T('T','kind,amount',[['A',10],['B',6]])])
A(18,'다음 두 값(d,c)은?','(1,0)§(1,1)§(0,0)§(0,1)','DECODE는 NULL끼리를 같은 것으로 처리해1이다. 단순 CASE NULL WHEN NULL은 매칭되지 않아0이다. / 두 문법의 특수 비교 규칙을 같다고 보면 안 된다.','SELECT DECODE(NULL,NULL,1,0) AS d,\n CASE NULL WHEN NULL THEN 1 ELSE 0 END AS c FROM DUAL;',source='https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/DECODE.html')
A(18,'다음 조건부 건수(a,b)는?','(2,3)§(2,2)§(3,3)§(1,3)','a는 Y행에서만1, N행은 ELSE생략 NULL이므로2다. b는 N행도0이라는 비NULL을 반환해 세 행을 센다. / COUNT는 값0도 센다는 점이 핵심이다.','SELECT COUNT(CASE WHEN flag=\'Y\' THEN 1 END) AS a,\n COUNT(CASE WHEN flag=\'Y\' THEN 1 ELSE 0 END) AS b FROM T;',[T('T','flag',[['Y'],['N'],['Y']])])
A(18,'다음 DECODE의 값은?','other§NULL§one§two','x=3은 search1,2 어디에도 같지 않아 마지막 default other를 반환한다. / 기본값을 생략한 경우의 NULL과 구분한다.',"SELECT DECODE(3,1,'one',2,'two','other') AS v FROM DUAL;",source='https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/DECODE.html')
A(18,'다음 결과 id별 v는?','0,5§오류,5§NULL,5§0,10','qty0이면 첫 WHEN에서0을 반환해 나누기 분기로 가지 않는다. qty2이면10/2=5다. / CASE는 해당 조건의 선택 순서를 따르며 사용하지 않을 나눗셈 결과를 정답으로 삼지 않는다.','SELECT CASE WHEN qty=0 THEN 0 ELSE amount/qty END AS v\nFROM T ORDER BY id;',[T('T','id,amount,qty',[[1,10,0],[2,10,2]])])

# 19 Aggregates
A(19,'COUNT(DISTINCT v)는 무엇을 세는가?','서로 다른 비NULL v 값§전체 행 수§NULL만§최댓값 하나','DISTINCT로 중복을 제거하고 COUNT의 NULL 제외 규칙을 적용한다. / COUNT(*) 및 COUNT(v)와 구분한다.')
A(19,'AVG(v)를 일반적으로 올바르게 표현한 것은?','SUM(v)/COUNT(v)§SUM(v)/COUNT(*) 항상 동일§MAX(v)/MIN(v)§COUNT(v)/SUM(v)','NULL이 아닌 값의 개수가 평균의 분모다. / NULL 행이 있으면 COUNT(*)와 COUNT(v)가 달라진다. 빈 입력이나 전부 NULL인 입력에서는 SUM(v)와 AVG(v)가 NULL이고 COUNT(v)는 0이다. Oracle에서 NULL/0도 NULL이므로 제시한 식의 결과와 일치한다.')
A(19,'다음 (c,d,s)는?','(3,2,14)§(4,3,14)§(3,3,14)§(3,2,9)','비NULL은4,4,6의3개, 서로 다른 값은4,6의2개, 합계14다. / DISTINCT는 d에만 있으며 s에서 중복4를 제거하지 않는다.','SELECT COUNT(v) AS c,COUNT(DISTINCT v) AS d,SUM(v) AS s FROM T;',[T('T','v',[[4],[4],[6],[None]])])
A(19,'다음 MIN,MAX는?','-4와3§NULL과3§-4와NULL§0과3','MIN·MAX는 NULL을 제외한 -4,0,3에서 경계를 구한다. / 정렬의 NULL 위치 규칙을 집계 MIN·MAX에 대입하지 않는다.','SELECT MIN(v),MAX(v) FROM T;',[T('T','v',[[-4],[0],[3],[None]])])
A(19,'행별 단가 평균과 총액/총수량의 값은?','15와12.5§15와15§12.5와12.5§20와12.5','단가10,20의 단순 평균은15다. 총액3×10+1×20=50, 총수량4이므로 가중 단가는12.5다. / AVG(price)는 qty 가중치를 자동 반영하지 않는다.','SELECT AVG(price) AS simple_avg,SUM(qty*price)/SUM(qty) AS weighted\nFROM T;',[T('T','qty,price',[[3,10],[1,20]])])
A(19,'집계에 입력된 값이 전부NULL일 때 SUM(v),COUNT(v)는?','NULL과0§0과0§NULL과2§0과2','SUM은 합칠 비NULL 값이 없어 NULL, COUNT(v)는0이다. / 입력 행 수가2라는 사실은 COUNT(*)에 해당한다.','SELECT SUM(v),COUNT(v) FROM T;',[T('T','v',[[None],[None]])])
A(19,'다음 두 집계(a,b)는?','(10,5)§(10,10)§(15,5)§(5,5)','SUM(DISTINCT v)는2+8=10, AVG(DISTINCT v)는(2+8)/2=5다. / 중복2의 개수는 두 DISTINCT 집계의 분모·합계에 반영되지 않는다.','SELECT SUM(DISTINCT v) AS a,AVG(DISTINCT v) AS b FROM T;',[T('T','v',[[2],[2],[8],[None]])])
A(19,'COUNT(1)과 COUNT(*)의 행 수 계산은?','둘 다 각 입력 행을 센다§COUNT(1)은 첫 행만 센다§COUNT(*)만 중복 제거§COUNT(1)은 NULL 열이 있으면 제외','상수1은 모든 입력 행에서 비NULL이므로 행을 센다. / 숫자1을 행 번호나 최대 반환 개수로 읽지 않는다.')
A(19,'문자열을 구분자 없이 연결해 서로 다른 (a,b) 조합 수를 세려고 한다. 아래 c의 값과 이 방법의 한계는?','c=1; 다른 두 조합이 같은 ABC로 합쳐진다§c=2; 항상 조합 수와 일치한다§c=3; DISTINCT는 연결식에 적용되지 않는다§c=NULL; 문자열은 COUNT할 수 없다','(A,BC)와 (AB,C)는 서로 다른 조합이지만 둘 다 ABC로 연결된다. 따라서 DISTINCT 연결 값은 하나다. / 단순 연결의 충돌을 고려하지 않으면 복합 조합의 수를 과소 계산한다.','SELECT COUNT(DISTINCT a||b) AS c FROM T;',[T('T','a,b',[['A','BC'],['AB','C'],['A','BC']])])

# 20 GROUP BY
A(20,'GROUP BY dept의 결과 단위는?','각 dept 그룹§항상 원본 각 행§항상 테이블 전체 한 행§각 열마다 한 행','같은 dept 값을 가진 행들이 한 그룹이 된다. / SELECT 집계는 그룹별로 계산되며 무조건 원본 행 수를 유지하지 않는다.')
A(20,'SELECT dept,name,SUM(v) FROM T GROUP BY dept에서 name이 그룹키도 집계식도 아니면?','name 때문에 오류§임의 name을 공식적으로 보장§첫 name 자동 선택§name을 자동 GROUP BY에 추가','한 dept 안 여러 name 중 무엇을 출력할지 정해져 있지 않다. / Oracle은 임의 값을 고르는 방식으로 허용하지 않는다.')
A(20,'다음 결과 (dept,s)는?','(10,7),(20,5)§(10,3),(10,4),(20,5)§(10,12),(20,12)§(10,2),(20,1)','dept10은3+4=7,dept20은5다. / 원본 행 나열이나 전체 합12 반복, 건수와 혼동하지 않는다.','SELECT dept,SUM(v) AS s FROM T GROUP BY dept ORDER BY dept;',[T('T','dept,v',[[10,3],[10,4],[20,5]])])
A(20,'NULL인 dept 두 행은 GROUP BY dept에서?','한 NULL 그룹으로 묶인다§항상 두 그룹§전부 제거§오류','그룹화에서는 NULL dept 행들을 하나의 그룹으로 취급한다. / 일반 비교 NULL=NULL이 UNKNOWN이라는 이유로 그룹을 둘로 나누지 않는다.','SELECT dept,COUNT(*) FROM T GROUP BY dept;',[T('T','dept',[[None],[None],[10]])])
A(20,'다음 결과 행 수와 그룹별 COUNT(*)는?','3행; (A,1)=2,(A,2)=1,(B,1)=1§2행; A=3,B=1§4행; 모두1§1행; 전체4','두 열의 조합으로 그룹화하여(A,1)만 두 행이다. / dept만 그룹화하거나 원본 행마다 그룹을 만드는 것으로 읽지 않는다.','SELECT dept,shift,COUNT(*) FROM T GROUP BY dept,shift;',[T('T','dept,shift',[['A',1],['A',1],['A',2],['B',1]])])
A(20,'GROUP BY가 결과 정렬까지 보장하는가?','아니며 최종 ORDER BY가 필요하다§항상 그룹키 오름차순 보장§항상 그룹키 내림차순 보장§항상 COUNT 큰 순서','그룹 구성과 출력 순서는 별개다. / 현재 관찰한 결과 순서를 모든 실행에 보장되는 규칙으로 삼지 않는다.')
A(20,'다음 결과 (band,cnt)는?','(H,2),(L,2)§(H,1),(L,3)§(H,3),(L,1)§H 한 행만','80과90은 H,70과 NULL은 L이다. NULL>=80은 UNKNOWN이므로 CASE의 ELSE로 간다. / GROUP BY는 CASE가 만든 같은 레이블끼리 묶는다.','SELECT CASE WHEN score>=80 THEN \'H\' ELSE \'L\' END AS band,COUNT(*) AS cnt\nFROM T\nGROUP BY CASE WHEN score>=80 THEN \'H\' ELSE \'L\' END\nORDER BY band;',[T('T','score',[[70],[80],[90],[None]])])
A(20,'GROUP BY 없이 SELECT SUM(v)와 GROUP BY dept의 차이는?','전자는 전체 집계, 후자는 dept별 집계§둘 다 항상 같은 행 수§전자는 행마다 합계 없음§후자는 집계를 쓸 수 없음','그룹키가 없으면 전체가 집계 대상이고 dept를 주면 그룹별 대상이 된다. / 입력과 그룹 수에 따라 결과 행 수도 달라진다.')
A(20,'WHERE v>3을 먼저 적용한 다음 GROUP BY 결과는?','(A,1,6),(B,1,8)§(A,2,8),(B,2,9)§(A,1,2),(B,1,1)§0행','각 그룹에서2와1이 WHERE에서 빠지고6과8만 남는다. / 그룹 합계를 구한 뒤 개별 값 필터를 적용하는 순서가 아니다.','SELECT dept,COUNT(*) AS c,SUM(v) AS s FROM T\nWHERE v>3 GROUP BY dept ORDER BY dept;',[T('T','dept,v',[['A',2],['A',6],['B',1],['B',8]])])

# 21 HAVING
A(21,'HAVING의 주된 필터 대상은?','그룹별 집계 결과§테이블 열 정의§인덱스 이름§항상 원본 개별 행만','HAVING은 GROUP BY로 만든 그룹 조건을 검사한다. / 집계 전 개별 행 조건은 보통 WHERE에서 적용하며 DDL 대상과 다르다.')
A(21,'WHERE SUM(v)>10이 아닌 HAVING SUM(v)>10을 쓰는 이유는?','합계는 그룹 집계 후 판정해야 하기 때문이다§WHERE에는 숫자 비교를 못 쓰기 때문§HAVING은 정렬 명령이기 때문§SUM은 SELECT에 못 쓰기 때문','집계 입력 행을 고르는 WHERE와 집계값을 거르는 HAVING은 단계가 다르다. / 숫자 비교나 SELECT의 SUM 사용 자체가 금지된 것은 아니다.')
A(21,'다음 결과 dept는?','A만§B만§A와 B§0행','A의 합은4+7=11로10보다 크고 B는10으로 경계에 걸려 제외된다. / >를 >=로 읽거나 원본 행 하나의 값만 비교하지 않는다.','SELECT dept FROM T GROUP BY dept HAVING SUM(v)>10 ORDER BY dept;',[T('T','dept,v',[['A',4],['A',7],['B',10]])])
A(21,'다음 결과 dept는?','A만§B만§C만§A,B,C','COUNT(v)는 A에서2,B에서1,C에서0이다. / COUNT(*)가 아니므로 NULL 행만 있는 C를 건수1로 판단하지 않는다.','SELECT dept FROM T GROUP BY dept HAVING COUNT(v)=2 ORDER BY dept;',[T('T','dept,v',[['A',1],['A',2],['B',3],['C',None]])])
A(21,'WHERE와 HAVING을 함께 적용한 결과는?','(B,12)§(A,12),(B,12)§(A,8),(B,12)§0행','WHERE v>=5로 A의4가 빠져 A합8,B합12다. HAVING>=10은 B만 남긴다. / WHERE 적용 전 A합12를 사용하지 않는다.','SELECT dept,SUM(v) AS s FROM T WHERE v>=5\nGROUP BY dept HAVING SUM(v)>=10 ORDER BY dept;',[T('T','dept,v',[['A',4],['A',8],['B',6],['B',6]])])
A(21,'HAVING SUM(v)>0에서 그룹의 v가 전부 NULL이면?','그 그룹은 제외된다§반드시 포함된다§SUM을0으로 바꿔 포함한다§항상 오류','SUM은 NULL이고 NULL>0은 UNKNOWN이어서 통과하지 않는다. / NULL을 자동 양수나0으로 바꾸는 규칙이 없다.','SELECT dept FROM T GROUP BY dept HAVING SUM(v)>0;',[T('T','dept,v',[['A',None],['A',None]])])
A(21,'GROUP BY 없는 다음 집계의 입력은0행이다. 최종 결과는?','0행§COUNT값0인1행§COUNT값NULL인1행§오류','그룹 없는 COUNT 자체는0을 만들지만 HAVING COUNT(*)>0이 FALSE라 그 결과 행을 제외한다. / 집계가 한 행을 만든다는 중간 단계만 보고 끝내면 안 된다.','SELECT COUNT(*) AS c FROM T WHERE 1=0 HAVING COUNT(*)>0;')
A(21,'다음 HAVING은 어떤 그룹을 남기는가?','서로 다른 비NULL v가2개 이상인 그룹§전체 행이2개 이상이면 모두§NULL만2개인 그룹§같은 v가2번 반복된 그룹만','COUNT(DISTINCT v)는 NULL과 중복을 제외한다. / 총 행 수나 단순 반복 횟수와 다르다.','SELECT dept FROM T GROUP BY dept HAVING COUNT(DISTINCT v)>=2;')
A(21,'다음 결과 dept는?','B만§A만§A와 B§0행','A는 평균10이지만 최솟값0이라 MIN>=5를 만족하지 못한다. B는 평균10,최솟값8로 둘 다 통과한다. / AND로 연결한 두 집계 조건을 모두 검사한다.','SELECT dept FROM T GROUP BY dept\nHAVING AVG(v)>=10 AND MIN(v)>=5 ORDER BY dept;',[T('T','dept,v',[['A',0],['A',20],['B',8],['B',12]])])

# 22 Inner joins and multiplicity
A(22,'INNER JOIN의 결과에 포함되는 행 조합은?','ON 조건을 만족하는 양쪽 행 쌍§왼쪽 모든 행을 항상 보존§오른쪽 모든 행을 항상 보존§양쪽 행을 순번대로 한 번씩 결합','내부 조인은 조건에 맞는 모든 쌍을 만든다. / 원본 순번 맞추기나 외부 조인의 보존 규칙과 다르다.')
A(22,'A.k=B.k로 조인한다. 두 표의 k가 모두 NULL인 행은 서로 매칭되는가?','일반 등호에서는 매칭되지 않는다§항상 매칭된다§숫자0으로 바꾸어 매칭§문법 오류','NULL=NULL은 UNKNOWN이므로 ON의 TRUE 조건을 충족하지 못한다. / NULL끼리 묶는 GROUP BY 규칙을 등호 조인에 적용하지 않는다.')
A(22,'내부 조인 결과의 행 수는?','3§2§4§1','A의 k1 두 행은 B의 k1 한 행에 각각 매칭해2행, k2는1행이어서 총3행이다. / 키가 같다고 조인 결과 중복을 자동 제거하지 않는다.','SELECT a.id,b.code FROM A a JOIN B b ON a.k=b.k;',[T('A','id,k',[[1,1],[2,1],[3,2]]),T('B','k,code',[[1,'X'],[2,'Y']])])
A(22,'다음 결과의 (eid,dname)는?','(1,X),(3,Y)§(1,X),(2,NULL),(3,Y)§(1,X)만§(2,Y),(3,X)','eid1의dept10은X,eid3의dept20은Y와 매칭된다. / eid2의dept30은 D에 없어 내부 조인에서 제외된다.','SELECT e.eid,d.dname FROM E e JOIN D d ON e.dept=d.dept ORDER BY e.eid;',[T('E','eid,dept',[[1,10],[2,30],[3,20]]),T('D','dept,dname',[[10,'X'],[20,'Y']])])
A(22,'다음 비등가 조인에서 각 id의 구간 이름은? 양끝은 포함한다.','1=L,2=H,3=H§1=L,2=L,3=H§1=H,2=H,3=L§2는 어떤 구간에도 없음','점수49는0~49,50과80은50~100에 들어간다. / BETWEEN 양끝 포함과 겹치지 않게 설정된 구간 경계를 확인한다.','SELECT t.id,g.label FROM T t JOIN G g\nON t.score BETWEEN g.lo AND g.hi ORDER BY t.id;',[T('T','id,score',[[1,49],[2,50],[3,80]]),T('G','lo,hi,label',[[0,49,'L'],[50,100,'H']])])
A(22,'다음 JOIN 결과에서 SUM(a.amount)는?','20§10§2§0','A의 한 행이 B의 두 일치 행과 결합하므로 amount10이 두 번 나타나 합20이다. / JOIN이 원본 금액을 자동으로 한 번만 집계하지 않는다.','SELECT SUM(a.amount) AS s FROM A a JOIN B b ON a.k=b.k;',[T('A','k,amount',[[1,10]]),T('B','k,tag',[[1,'X'],[1,'Y']])])
A(22,'두 키를 모두 일치시켜야 한다. 다음 조인 결과 쌍(a.id,b.id)은?','(1,8)만§(1,8),(1,9)§(1,8),(2,9)§(2,8)만','a1의(k,ver)=(7,1)은 b8과만 일치한다. a2의(7,2)는 B에 없다. / k 하나만 비교하면 다른 버전까지 잘못 매칭된다.','SELECT a.id,b.id FROM A a JOIN B b\nON a.k=b.k AND a.ver=b.ver;',[T('A','id,k,ver',[[1,7,1],[2,7,2]]),T('B','id,k,ver',[[8,7,1],[9,7,3]])])
A(22,'조건이 같은 등호 내부 조인에서 A JOIN B와 B JOIN A는 무엇이 다른가? SELECT 열은 같은 순서로 명시한다.','같은 행 조합을 얻으며 출력 순서는 별도 지정해야 한다§행 조합 수가 반드시 두 배§항상 왼쪽 전체 행을 보존§오른쪽 표는 항상 무시','등호 내부 조인의 매칭 쌍은 바꾸어 써도 같은 관계다. / 다만 SELECT * 열 순서와 최종 행 정렬까지 같다고 보장하는 설명은 아니다.')
A(22,'아래 조인의 출력 행 수는? 범위가 겹친다.','3§2§1§4','점수50은0~60과40~100 두 구간에 모두 매칭해2행, 점수70은 두 번째만 매칭해1행이다. / 비등가 조인도 한 입력이 여러 행과 매칭될 수 있다.','SELECT t.id,g.label FROM T t JOIN G g\nON t.score BETWEEN g.lo AND g.hi;',[T('T','id,score',[[1,50],[2,70]]),T('G','lo,hi,label',[[0,60,'L'],[40,100,'H']])])

# 23 Outer joins
A(23,'A LEFT JOIN B에서 반드시 보존하는 쪽은?','A§B§매칭된 B만§양쪽 전체 항상','LEFT는 왼쪽 A의 미매칭 행도 NULL 확장하여 보존한다. / B 전체 보존은 RIGHT, 양쪽 전체는 FULL의 역할이다.')
A(23,'LEFT JOIN의 오른쪽 조건을 ON에서 WHERE로 옮기면 결과가 달라질 수 있는 이유는?','WHERE가 NULL 확장 행을 다시 제거할 수 있다§ON은 항상 모든 행을 삭제한다§WHERE는 정렬만 한다§두 위치는 모든 경우 동일하다','ON은 매칭 결정, WHERE는 조인 후 결과 필터다. / 오른쪽 열에 대한 등호 조건은 NULL 확장 행에서 UNKNOWN이 되어 빠질 수 있다.')
A(23,'다음 LEFT JOIN 결과는?','(1,X),(2,NULL)§(1,X)만§(2,NULL)만§(1,X),(2,X)','A의k10은X와 매칭되고k20은미매칭이지만왼쪽행이라보존된다. / 없는B값을다른행의X로채우지않는다.','SELECT a.id,b.name FROM A a LEFT JOIN B b ON a.k=b.k ORDER BY a.id;',[T('A','id,k',[[1,10],[2,20]]),T('B','k,name',[[10,'X']])])
A(23,'다음 두 건수(c1,c2)는? B.k는 NOT NULL이다.','(2,1)§(1,1)§(2,2)§(1,2)','LEFT JOIN은 A 두 행을 보존하므로 COUNT(*)=2다. 미매칭행의 b.k는 NULL이어서 COUNT(b.k)=1이다. / 행 수와 오른쪽 실제 매칭 수를 구분한다.','SELECT COUNT(*) AS c1,COUNT(b.k) AS c2\nFROM A a LEFT JOIN B b ON a.k=b.k;',[T('A','k',[[1],[2]]),T('B','k',[[1]])])
A(23,'FULL JOIN 결과 행 수는? 두 표 모두 k의 중복을 허용한다.','6§4§5§9','k1은A2행×B2행=4쌍이다. A의k2와B의k3 미매칭을각각1행씩보존해총6행이다. / FULL이중복을제거하거나모든조합9행을만드는것은아니다.','SELECT a.k,b.k FROM A a FULL JOIN B b ON a.k=b.k;',[T('A','k',[[1],[1],[2]]),T('B','k',[[1],[1],[3]])])
A(23,'다음 RIGHT JOIN 결과는?','(1,10),(NULL,20)§(1,10)만§(1,10),(2,NULL)§(NULL,10),(NULL,20)','오른쪽B의k10은A.id1과매칭, B.k20은미매칭이어도보존된다. / A의k30은보존대상이아니므로출력되지않는다.','SELECT a.id,b.k FROM A a RIGHT JOIN B b ON a.k=b.k ORDER BY b.k;',[T('A','id,k',[[1,10],[2,30]]),T('B','k',[[10],[20]])])
A(23,'다음 두 조회 P,Q의 결과 id 집합은? P는 오른쪽 flag조건을 ON에, Q는 WHERE에 둔다.','P={1,2}, Q={1}§둘 다{1,2}§둘 다{1}§P={1}, Q={1,2}','P는id2에서조건을만족하는B가없어도NULL확장해보존한다. Q는조인된N행을WHERE에서제거한다. / 오른쪽필터위치는보존행결과를바꾼다.',"SELECT a.id FROM A a LEFT JOIN B b\n ON a.k=b.k AND b.flag='Y';\n-- Q\nSELECT a.id FROM A a LEFT JOIN B b ON a.k=b.k\n WHERE b.flag='Y';",[T('A','id,k',[[1,10],[2,20]]),T('B','k,flag',[[10,'Y'],[20,'N']])])
A(23,'A가0행이고 B에2행일 때 FULL JOIN ON(1=1)의 행 수는?','2§0§1§4','매칭할A행이없어도 FULL은B의미매칭두행을보존한다. / INNER나CROSS의0행규칙을FULL에그대로적용하지않는다.','SELECT a.k,b.k FROM A a FULL JOIN B b ON(1=1);',[T('A','k',[]),T('B','k',[[1],[2]])])
A(23,'실제로 B와 매칭되지 않은 A만 찾으려 한다. B.k는 NOT NULL, B.note는 NULL 허용이다. 제시된 LEFT JOIN 뒤에 추가할 적절한 WHERE절은?','WHERE b.k IS NULL§WHERE b.note IS NULL§WHERE a.k IS NULL§WHERE b.k=NULL','매칭된 B행의 k는비NULL이므로b.k IS NULL이NULL확장행을식별한다. / note는실제매칭행에서도NULL일수있어잘못포함하며= NULL은UNKNOWN이다.','SELECT a.id FROM A a LEFT JOIN B b ON a.k=b.k;',[T('A','id,k',[[1,10],[2,20]]),T('B','k,note',[[10,None]])])

# 24 CROSS JOIN and SELF JOIN
A(24,'A가3행, B가2행일 때 CROSS JOIN 행 수는?','6§5§3§2','각 A행에 B두행을짝지어3×2=6이다. / 행수를더하거나큰쪽수만선택하지않는다.')
A(24,'SELF JOIN의 본질은?','같은 테이블에 서로 다른 별칭을 주어 관계를 조인한다§항상 자기행만 반환한다§새 물리 테이블이 반드시 필요하다§JOIN 조건이 필요 없다','한 테이블을직원·관리자등서로다른역할로참조한다. / 별칭과조건이필요하며물리복제나자기자신매칭만의뜻은아니다.')
A(24,'다음 내부 SELF JOIN 결과(e.id,m.id)는?','(2,1),(3,1)§(1,NULL),(2,1),(3,1)§(1,2),(1,3)§(2,2),(3,3)','e.mgr=m.id이므로직원2,3은관리자1과매칭한다. / 관리자없는루트1은내부조인에서제외되며조인방향을뒤집지않는다.','SELECT e.id,m.id FROM E e JOIN E m ON e.mgr=m.id ORDER BY e.id;',[T('E','id,mgr',[[1,None],[2,1],[3,1]])])
A(24,'다음 CROSS JOIN에서 WHERE까지 적용한 쌍(a.x,b.y)은?','(1,2),(1,3),(2,3)§(1,2),(2,3)§(2,2)§네 조합 전부','전체4쌍에서x<y가거짓인(2,2)를제외해3쌍이다. / 순번끼리만짝지거나WHERE를무시하지않는다.','SELECT a.x,b.y FROM A a CROSS JOIN B b WHERE a.x<b.y ORDER BY a.x,b.y;',[T('A','x',[[1],[2]]),T('B','y',[[2],[3]])])
A(24,'세 사람의 서로 다른 두 사람 조합을 중복 없이 구하려면? id는1,2,3이다.','a.id<b.id§a.id<>b.id§a.id=b.id§조건 없음','<는(1,2),(1,3),(2,3)만남긴다. / <>는반대방향까지6쌍,=는자기쌍3개,조건없음은9쌍이다.','SELECT a.id,b.id FROM E a CROSS JOIN E b;',[T('E','id',[[1],[2],[3]])])
A(24,'A는2행, B는0행이다. CROSS JOIN 결과는?','0행§2행§1행§NULL 확장2행','2×0=0이므로만들쌍이없다. / CROSS는외부조인처럼왼쪽행을NULL로확장해보존하지않는다.','SELECT a.id,b.id FROM A a CROSS JOIN B b;',[T('A','id',[[1],[2]]),T('B','id',[])])
A(24,'다음 SELF LEFT JOIN의 결과(name,manager)는?','(ROOT,NULL),(DEV,ROOT)§(DEV,ROOT)만§(ROOT,DEV),(DEV,ROOT)§(ROOT,ROOT),(DEV,DEV)','ROOT는관리자가없지만왼쪽e라보존되고DEV는ROOT와매칭한다. / INNER JOIN결과처럼루트를빠뜨리거나방향을서로바꾸지않는다.','SELECT e.name,m.name AS manager FROM E e LEFT JOIN E m ON e.mgr=m.id ORDER BY e.id;',[T('E','id,mgr,name',[[1,None,'ROOT'],[2,1,'DEV']])])
A(24,'같은 테이블을 두 번 쓸 때 e와m 별칭을 쓰는 이유는?','각 역할의 열 참조를 구별한다§서로 다른 DBMS로 바꾼다§원본 데이터를 두 배로 저장한다§모든 제약을 해제한다','e.id와m.id는같은열정의라도조인에서서로다른행역할을가리킨다. / 별칭은DBMS전환·물리복제·제약해제가아니다.')
A(24,'직원의 상사와 그 상사를 두 번 SELF JOIN한다. 다음 결과 직원 id는?','3만§2,3§1,2,3§1만','id3은직속상사2와그상사1이모두있다. id2의상사1에는다음상사가없어두번째내부조인에서빠진다. / 한단계조인만계산해id2를포함하지않는다.','SELECT e.id FROM E e JOIN E m ON e.mgr=m.id\nJOIN E g ON m.mgr=g.id ORDER BY e.id;',[T('E','id,mgr',[[1,None],[2,1],[3,2]])])

# 25 ANSI joins: USING, NATURAL and explicit ON
A(25,'JOIN ... USING(k)의 핵심 의미는?','양쪽의 같은 이름 k를 등호로 비교한다§k를 항상 삭제한다§k를 부등호로 비교한다§조건 없이 모든 행을 결합한다','USING은명시한동명이름열의등가조인이다. / 결과에서공통열을하나로다루는것과열자체를삭제하는것은다르다.')
A(25,'NATURAL JOIN은 어떤 열을 조인 조건으로 삼는가?','양쪽에 이름이 같은 모든 열§항상 첫 번째 열만§PK로 선언된 열만§숫자형 열만','동명열전체가자동조건이다. / 새동명열이추가되면결과가달라질수있으므로PK나첫열만확인하면안된다.')
A(25,'다음 USING 조인 결과의(id,x,y)는?','(1,A,C)§(1,A,C),(2,B,NULL)§(1,A,C),(3,NULL,D)§(2,B,D)','공통id1만매칭한다. / 내부조인이므로한쪽에만있는id2·3을보존하지않으며USING은공통id를하나로출력한다.','SELECT id,x,y FROM A JOIN B USING(id);',[T('A','id,x',[[1,'A'],[2,'B']]),T('B','id,y',[[1,'C'],[3,'D']])])
A(25,'A(k,x),B(k,y)의 SELECT * FROM A JOIN B USING(k) 결과 열 수는?','3§4§2§1','공통k를하나로출력하고x,y가더해져3열이다. / ON조인에서양쪽k를모두출력하는경우와구분한다.')
A(25,'A와B에id,color가공통이다. NATURAL JOIN 결과 id는?','2만§1,2§1만§0행','id1은color가R과B로달라제외되고id2는둘다G라매칭한다. / NATURAL을id만의JOIN이라고가정하면id1을잘못포함한다.','SELECT id,color FROM A NATURAL JOIN B;',[T('A','id,color',[[1,'R'],[2,'G']]),T('B','id,color',[[1,'B'],[2,'G']])])
A(25,'A(a)와 B(b)는 공통 열 이름이 없고 각각2행이다. NATURAL JOIN의 행 수는?','4§2§0§항상 오류','공통열이없어모든조합인카티션곱이되어2×2=4다. / 같은위치열을자동비교하거나빈결과가된다고보지않는다.','SELECT * FROM A NATURAL JOIN B;',[T('A','a',[[1],[2]]),T('B','b',[[3],[4]])])
A(25,'FULL JOIN USING(k)에서 공통 출력 k는? A와 B의 k는 원래 NOT NULL이다.','1,2,3§1,2,NULL§1,NULL,3§2만','k2는매칭하고k1·3은각쪽미매칭으로보존된다. USING의공통출력k는값이존재하는쪽을사용해1,2,3이다. / 한쪽k만SELECT한결과의NULL확장과구분한다.','SELECT k FROM A FULL JOIN B USING(k) ORDER BY k;',[T('A','k',[[1],[2]]),T('B','k',[[2],[3]])])
A(25,'USING(k)로 조인한 공통k를 같은 SELECT 블록에서 참조하는 적절한 방식은?','SELECT k§SELECT a.k§SELECT b.k§SELECT a.k+b.k만 허용','Oracle에서USING의조인열은테이블별칭으로한정하지않고공통k로참조한다. / 비공통열의별칭사용규칙을공통USING열에그대로적용하지않는다.')
A(25,'A의복합키(k,ver)와B를아래처럼USING(k)만으로조인했다. 결과행수와원하는동일버전조인을위한수정은?','4행; USING(k,ver)와 SELECT k,ver로 함께 바꾸면 2행§2행; 수정 불필요§4행; DISTINCT k만 추가하면 동일 의미§0행; ON(1=1)이 필요','k7인A두행과B두행이모두결합해4행이다. ver까지비교하면(7,1),(7,2)의2쌍만남는다. / DISTINCT k는버전정보를잃으므로원하는복합조건조인의대안이아니다.','SELECT k,a.ver AS av,b.ver AS bv\nFROM A a JOIN B b USING(k);',[T('A','k,ver',[[7,1],[7,2]]),T('B','k,ver',[[7,1],[7,2]])])

# Copy edits are authored replacements of prose only. SQL, choices and table
# strings are intentionally untouched by this pass.
def revise(qid,why=None,stem=None):
    q=next(x for x in review+[q for f in mocks for q in f] if x['id']==qid)
    if why:
        parts=why.split(' / '); q['explanation']=' '.join(parts); q['steps']=parts; q['pitfall']=parts[-1]
    if stem:
        prefix=q['stem'].split('없다. ',1)[0]+'없다. '
        if '초기 입력은 COMMIT된 상태다. ' in q['stem']:prefix+='초기 입력은 COMMIT된 상태다. '
        if q['tables']:prefix+='표의 별도 자료형 명시가 없으면 숫자는 NUMBER, 문자는 VARCHAR2다. '
        q['stem']=prefix+stem
revise('unit-2-1-review-10-02','Oracle MERGE는 ON에서 참조한 열의 갱신을 제한한다. / 숫자 열의 일반 갱신, 서로 다른 이름의 대응, UPDATE 절만 사용하는 것까지 금지하는 규칙은 아니다.')
revise('unit-2-1-review-10-03','id=1은 매칭되어 8로 갱신되고 id=2는 미매칭이어서 9로 삽입된다. / ON이 TRUE인 행을 INSERT하거나 대상 전체를 교체하는 작업이 아니다.','MERGE 후 D의 (id,v)는? D.id와 S.id는 각각 고유하다.')
revise('unit-2-1-mock-1-19','INSERT 분기가 없으므로 미매칭 원본 행을 새로 넣지 않는다. / UPDATE 절만 있는 MERGE가 가능하며, 매칭되는 대상이 없다고 첫 대상 행을 대신 선택하지 않는다.','WHEN MATCHED THEN UPDATE만 있는 MERGE에서 미매칭 원본 행은?')
revise('unit-2-1-mock-1-20','id=1을 1에서 0으로 갱신한 뒤, 갱신 후 값이 v=0이므로 삭제한다. id=2는 원본과 매칭되지 않아 DELETE WHERE의 대상이 아니다. / MERGE의 DELETE는 대상 전체를 정리하는 별도 DELETE 문과 다르다.','다음 MERGE 후 D는? 원본과 대상에서 id는 각각 고유하다.')
revise('unit-2-1-mock-2-19','ON은 상수 FALSE이므로 매칭이 없어 모든 원본 행이 INSERT 분기 후보가 된다. / 실제 삽입은 그 밖의 제약도 만족해야 하며 UPDATE·DELETE·집계로 바뀌지 않는다.','ON(0=1)이고 INSERT 절만 있는 MERGE에서 원본 행은?')
revise('unit-2-1-mock-2-20','id=1은 ON에서 이미 매칭된 행이다. s.v>0이 FALSE이므로 UPDATE를 건너뛰어 기존 값 5를 유지한다. / UPDATE 생략을 미매칭으로 다시 분류하여 INSERT하지 않는다.','매칭된 id=1이 UPDATE의 WHERE를 만족하지 못했다. INSERT 절도 존재한다. 최종 D는?')
revise('unit-2-1-mock-3-19','USING은 원본 테이블 또는 조회 결과를 지정한다. / ON은 매칭 조건이며 USING은 정렬·제약 삭제·확정 주기를 설정하는 절이 아니다.')
revise('unit-2-1-mock-3-20','id=1은 7로 갱신한다. id=2는 미매칭이지만 s.v>0이 FALSE여서 삽입하지 않고 id=3은 4로 삽입한다. / INSERT WHERE와 UPDATE의 분기 조건을 혼동하지 않는다.','MERGE 후 D는? id는 각 표에서 고유하고 D.id는 PK다.')
revise('unit-2-1-mock-1-30','x+y는 3,NULL,NULL이므로 SUM은 3이다. 따로 구하면 SUM(x)=6, SUM(y)=4여서 합은 10이다. / 행별 덧셈의 NULL 전파와 열별 집계의 NULL 제외를 구분한다.')
revise('unit-2-1-review-22-03','A에서 k=1인 두 행은 B의 k=1인 한 행과 각각 매칭하여 2행을 만든다. k=2는 1행이므로 총 3행이다. / 키가 같다고 조인 결과의 중복을 자동 제거하지 않는다.')
revise('unit-2-1-mock-1-43','eid=1의 dept=10은 X, eid=3의 dept=20은 Y와 매칭된다. / eid=2의 dept=30은 D에 없어 내부 조인에서 제외된다.')
revise('unit-2-1-mock-1-44','점수 49는 0~49, 점수 50과 80은 50~100에 들어간다. / BETWEEN의 양끝 포함과 겹치지 않게 설정한 구간 경계를 확인한다.')
revise('unit-2-1-mock-2-43','A의 한 행이 B의 두 일치 행과 결합하므로 amount=10이 두 번 나타나 합은 20이다. / JOIN은 원본 금액을 자동으로 한 번만 집계하지 않는다.')
revise('unit-2-1-mock-2-44','A의 id=1은 (k,ver)=(7,1)로 B의 id=8과만 일치한다. A의 id=2인 (7,2)는 B에 없다. / k 하나만 비교하면 다른 버전까지 잘못 매칭된다.')
revise('unit-2-1-mock-3-44','점수 50은 0~60과 40~100의 두 구간에 모두 매칭하여 2행, 점수 70은 두 번째 구간에만 매칭하여 1행을 만든다. / 비등가 조인에서도 한 입력이 여러 행과 매칭될 수 있다.')
revise('unit-2-1-review-23-03','A의 k=10은 X와 매칭되고 k=20은 미매칭이지만 왼쪽 행이므로 보존된다. / 존재하지 않는 B 값을 다른 행의 X로 채우지 않는다.')
revise('unit-2-1-mock-1-45','LEFT JOIN은 A의 두 행을 보존하므로 COUNT(*)=2다. 미매칭 행의 b.k는 NULL이어서 COUNT(b.k)=1이다. / 전체 행 수와 오른쪽의 실제 매칭 수를 구분한다.')
revise('unit-2-1-mock-1-46','k=1은 A의 2행과 B의 2행이 결합하여 4쌍이다. A의 k=2와 B의 k=3인 미매칭 행을 각각 하나씩 보존해 총 6행이다. / FULL은 중복을 제거하거나 모든 조합인 9행을 만드는 연산이 아니다.')
revise('unit-2-1-mock-2-45','오른쪽 B의 k=10은 A의 id=1과 매칭되고, B의 k=20은 미매칭이어도 보존된다. / A의 k=30은 보존 대상이 아니므로 출력하지 않는다.')
revise('unit-2-1-mock-2-46','P는 id=2에서 조건을 만족하는 B가 없어도 NULL 확장하여 보존한다. Q는 조인된 N 행을 WHERE에서 제거한다. / 오른쪽 필터의 위치는 보존 행의 결과를 바꾼다.','두 조회 P,Q의 결과 id 집합은? P는 오른쪽 flag 조건을 ON에, Q는 WHERE에 둔다.')
revise('unit-2-1-mock-3-45','매칭할 A 행이 없어도 FULL은 B의 미매칭 두 행을 보존한다. / INNER 또는 CROSS의 0행 규칙을 FULL에 그대로 적용하지 않는다.','A가 0행이고 B에 2행일 때 FULL JOIN ON(1=1)의 행 수는?')
revise('unit-2-1-mock-3-46','매칭된 B 행의 k는 비NULL이므로 b.k IS NULL이 NULL 확장 행을 식별한다. / note는 실제 매칭 행에서도 NULL일 수 있어 잘못 포함하며, =NULL 비교는 UNKNOWN이다.')
revise('unit-2-1-review-24-01','각 A 행에 B의 두 행을 짝지어 3×2=6행이다. / 행 수를 더하거나 큰 쪽의 행 수만 선택하지 않는다.','A가 3행, B가 2행일 때 CROSS JOIN의 행 수는?')
revise('unit-2-1-review-24-02','한 테이블을 직원·관리자 등 서로 다른 역할로 참조한다. / 별칭과 조건으로 역할을 구분하며 물리 복제나 자기 자신과의 매칭만을 뜻하지 않는다.')
revise('unit-2-1-review-24-03','e.mgr=m.id이므로 직원 2와 3은 관리자 1과 매칭한다. / 관리자가 없는 루트 1은 내부 조인에서 제외되며 조인 방향을 뒤집지 않는다.')
revise('unit-2-1-mock-1-47','전체 4쌍에서 x<y가 거짓인 (2,2)를 제외하여 3쌍이다. / 순번끼리만 짝지거나 WHERE를 무시하지 않는다.')
revise('unit-2-1-mock-1-48','a.id<b.id는 (1,2),(1,3),(2,3)만 남긴다. / <>는 반대 방향까지 6쌍, =는 자기 쌍 3개, 조건이 없으면 9쌍이다.','세 사람의 서로 다른 두 사람 조합을 중복 없이 구하려 한다. 아래 SQL의 FROM절 뒤에 WHERE절을 추가할 때 사용할 조건은? id는 1,2,3이다.')
revise('unit-2-1-mock-2-47','2×0=0이므로 만들 수 있는 쌍이 없다. / CROSS는 외부 조인처럼 왼쪽 행을 NULL 확장하여 보존하지 않는다.','A는 2행, B는 0행이다. CROSS JOIN의 결과는?')
revise('unit-2-1-mock-2-48','ROOT는 관리자가 없지만 왼쪽 e에 속하여 보존되고 DEV는 ROOT와 매칭한다. / INNER JOIN의 결과처럼 루트를 빠뜨리거나 관계의 방향을 뒤집지 않는다.')
revise('unit-2-1-mock-3-47','e.id와 m.id는 같은 열 정의라도 조인에서 서로 다른 행의 역할을 가리킨다. / 별칭은 DBMS 전환·물리 복제·제약 해제가 아니다.','같은 테이블을 두 번 쓸 때 e와 m이라는 별칭을 쓰는 이유는?')
revise('unit-2-1-mock-3-48','id=3에는 직속 상사 2와 그 상사 1이 모두 있다. id=2의 상사 1에는 다음 상사가 없어 두 번째 내부 조인에서 빠진다. / 한 단계 조인만 계산해 id=2를 포함하지 않는다.')
revise('unit-2-1-review-25-01','USING은 명시한 동명 열을 등호로 비교한다. / 결과에서 공통 열을 하나로 다루는 것과 그 열 자체를 삭제하는 것은 다르다.')
revise('unit-2-1-review-25-02','이름이 같은 열 전체가 자동 조인 조건이다. / 새 동명 열이 추가되면 결과가 달라질 수 있으므로 PK나 첫 번째 열만 확인하면 안 된다.')
revise('unit-2-1-review-25-03','공통 id=1만 매칭한다. / 내부 조인이므로 한쪽에만 있는 id=2와 3은 보존하지 않으며 USING은 공통 id를 하나로 출력한다.')
revise('unit-2-1-mock-1-49','공통 k를 하나로 출력하고 x,y가 더해져 3열이다. / ON 조인에서 양쪽 k를 모두 출력하는 경우와 구분한다.')
revise('unit-2-1-mock-1-50','id=1은 color가 R과 B로 달라 제외되고 id=2는 양쪽 모두 G라 매칭한다. / NATURAL을 id만의 JOIN으로 가정하면 id=1을 잘못 포함한다.','A와 B에서 id,color는 공통 열이다. NATURAL JOIN의 결과 id는?')
revise('unit-2-1-mock-2-49','공통 열이 없어 모든 조합인 카티션 곱이 되어 2×2=4행이다. / 같은 위치의 열을 자동 비교하거나 빈 결과를 반환한다고 보지 않는다.','A(a)와 B(b)는 공통 열 이름이 없고 각각 2행이다. NATURAL JOIN의 행 수는?')
revise('unit-2-1-mock-2-50','k=2는 매칭하고 k=1과 3은 각 쪽의 미매칭 행으로 보존된다. USING의 공통 출력 k는 값이 존재하는 쪽을 사용해 1,2,3이다. / 한쪽 k만 SELECT한 결과의 NULL 확장과 구분한다.')
revise('unit-2-1-mock-3-49','Oracle에서 USING의 조인 열은 테이블 별칭으로 한정하지 않고 공통 k로 참조한다. / 비공통 열의 별칭 사용 규칙을 USING의 공통 열에 그대로 적용하지 않는다.','USING(k)로 조인한 공통 k를 같은 SELECT 블록에서 참조하는 적절한 방식은?')
revise('unit-2-1-mock-3-50','k=7인 A의 두 행과 B의 두 행이 모두 결합하여 4행이다. USING(k,ver)로 ver까지 비교하고 SELECT k,ver로 두 공통 열을 한정 없이 출력하면 (7,1),(7,2)의 2행만 남는다. / USING(k,ver)로 바꾼 뒤에도 a.ver,b.ver를 그대로 쓰면 Oracle의 공통 열 한정 참조 금지 규칙에 걸린다. DISTINCT k는 버전 정보를 잃으므로 원하는 복합 조건 조인의 대안이 아니다.','A의 복합키 (k,ver)와 B를 아래처럼 USING(k)만으로 조인했다. 결과 행 수와 동일 버전 조인을 위한 수정은?')

revise('unit-2-1-mock-2-06','(8,2,100,1)은 새 키 (8,2), 존재하는 상품 100, 양수인 수량 1이므로 모든 제약을 통과한다. / (8,1,100,1)은 PK 중복, (8,2,200,1)은 존재하지 않는 상품 200 참조, (8,2,100,NULL)은 qty의 NOT NULL 위반이다.')
revise('unit-2-1-mock-2-18','DELETE한 id=1은 COMMIT 전 ROLLBACK으로 복원된다. / ROLLBACK은 초기 COMMIT된 id=2까지 지우지 않으며 DELETE의 미확정 변경만 취소한다.','클라이언트 자동 COMMIT은 없고 같은 세션에서 아래 문장을 순서대로 실행한다. 모두 실행한 뒤 같은 세션에서 조회하면 남는 id는?')
revise('unit-2-1-mock-2-32','id=1은 TRUE OR FALSE이므로 TRUE다. id=3은 UNKNOWN OR TRUE이므로 TRUE다. / id=2는 FALSE OR FALSE라 제외하며 NULL이 있는 모든 행을 무조건 버리는 규칙도 아니다.')
revise('unit-2-1-mock-3-14','id=1은 TRUE AND FALSE여서 제외되고 id=2는 TRUE AND TRUE여서 포함된다. id=3은 v>=0이 UNKNOWN, code<>\'X\'가 FALSE여서 괄호 안 AND가 FALSE다. 그러나 바깥 OR의 v IS NULL이 TRUE이므로 포함된다. / 괄호 안 AND와 바깥 OR를 나누어 평가하며 결과는 id=2,3이다.')
revise('unit-2-1-mock-3-18','code=\'A\'가 id=1,2 모두에 참이므로 두 행을 삭제하고 id=3 한 행만 남긴다. / DELETE가 중복 중 첫 행만 지운다는 가정은 틀리며, 삭제된 행 수 2와 남은 행 수 1을 구별한다.','아래 DELETE를 실행한 뒤 T에 남는 행 수는?')

assert seen==Counter({i:9 for i in range(1,26)}),seen
for form in mocks:
    assert Counter(q['difficulty'] for q in form)=={'basic':10,'intermediate':30,'advanced':10}
    assert Counter(q['lessonId'] for q in form)=={f'2-1-{i:02}':2 for i in range(1,26)}
all_questions=review+[q for form in mocks for q in form]
assert len(review)==75 and len(all_questions)==225
for q in all_questions:
    assert q['id'].startswith('unit-')
    assert len(q['sql'].splitlines())<=12
    for t in q['tables']:
        assert len(t['rows'])<=5 and len(t['headers'])<=5
        assert all(len(r)==len(t['headers']) for r in t['rows'])
save('2-1','SQL 기본: 강의별 복습과 단원 모의고사',review,mocks)
print('coverage',len(seen),'lessons; sql/table',sum(bool(q['sql'] or q['tables']) for q in all_questions))
