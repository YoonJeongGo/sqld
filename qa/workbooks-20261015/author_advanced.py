"""Original app practice; authored reasoning only, not engine execution."""
from common import question,table,save
BASE='https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/'
groups=[[],[],[]]
sources={1:'Using-Subqueries.html',2:'Scalar-Subquery-Expressions.html',3:'Comparison-Conditions.html',4:'IN-Condition.html',5:'Scalar-Subquery-Expressions.html',6:'The-UNION-ALL-INTERSECT-MINUS-Operators.html',7:'SELECT.html',8:'SELECT.html',9:'GROUPING.html',10:'Analytic-Functions.html',11:'RANK.html',12:'Analytic-Functions.html',13:'LAST_VALUE.html',14:'SELECT.html',15:'Hierarchical-Queries.html',16:'Hierarchical-Queries.html',17:'SELECT.html',18:'REGEXP_SUBSTR.html'}
def A(g,l,stem,opts,why,trap,sql='',tab=None,source=None):
    i=len(groups[g]);choices=opts.split('|')
    difficulty='basic' if i in {0,2,4,8,10,13,17,20,23,26} else 'advanced' if i in {7,9,16,22,25,32,35,40,43,49} else 'intermediate'
    groups[g].append(question(f'unit-2-2-mock-{g+1}-{i+1:02}',f'2-2-{l:02}','mock',difficulty,
        stem,choices,0,why+' 오답 점검: '+trap,sql=sql,tables=tab or [],steps=[why,trap],pitfall=trap,source=source or BASE+sources[l]))
def P(l,items):
    assert len(items)==3
    for g,kw in enumerate(items): A(g,l,**kw)
def C(stem,opts,why,trap,sql='',tab=None,source=None):
    return dict(stem=stem,opts=opts,why=why,trap=trap,sql=sql,tab=tab,source=source)
def T(name,cols,rows):return [table(name,cols,rows)]
# Subquery classification: two decisions per set.
P(1,[
C('다음 WHERE 안의 SELECT는 어느 위치의 서브쿼리인가?','조건식에 사용된 서브쿼리|FROM절 인라인 뷰|CREATE TABLE 정의|윈도우 프레임','바깥 WHERE의 비교값을 안쪽 SELECT가 제공한다.','위치를 기준으로 분류하며 SELECT 목록이나 FROM 위치로 바꾸지 않는다.',"SELECT id FROM T WHERE v>(SELECT AVG(v) FROM T);"),
C('아래 쿼리에서 X가 가리키는 것은?','FROM절의 인라인 뷰|영구 테이블을 새로 만드는 명령|시퀀스|윈도우 프레임','FROM 안의 조회 결과에 별칭 X를 붙였으므로 인라인 뷰다.','별칭은 영구 객체 생성이나 자료형 선언이 아니다.',"SELECT X.dept FROM (SELECT DISTINCT dept FROM T) X;"),
C('바깥 행 E의 dept를 안쪽 조건에서 참조한다. 분류는?','상관 서브쿼리|외부 참조 없는 독립 서브쿼리|집합 연산자 자체|DDL','서브쿼리가 바깥 행의 열을 참조하므로 상관 관계가 있다.','SELECT 위치나 실제 옵티마이저 실행 횟수로 분류를 단정하지 않는다.',"SELECT E.id FROM E WHERE EXISTS\n(SELECT 1 FROM D WHERE D.dept=E.dept);")])
P(1,[
C('서브쿼리에 ORDER BY가 없을 때 단일행 서브쿼리의 뜻은?','반환 행 수가 최대 한 행인 비교 용도의 서브쿼리|첫 행만 자동 선택하는 서브쿼리|항상 정렬된 서브쿼리|열 수가 무조건 테이블 전체인 서브쿼리','단일행 비교는 비교값을 하나 제공하는 반환 크기를 전제로 한다.','여러 행이 나와도 임의 첫 행을 선택하는 규칙은 없다.'),
C('서브쿼리 결과가 여러 행일 수 있는 상황에서 = 대신 적절한 비교를 선택할 때 고려할 것은?','IN·ANY·ALL의 의미와 NULL·빈 결과 조건|괄호를 없애면 항상 해결됨|첫 행을 자동으로 사용하므로 무관함|서브쿼리 별칭 글자 수','다중행 비교는 멤버십·존재 비교·전체 비교 중 의도에 맞는 연산을 사용한다.','구문 오류 회피만이 아니라 논리 의미가 일치해야 한다.'),
C('상관 서브쿼리가 쓰였다는 사실만으로 실제 물리 실행을 단정할 수 있는가?','아니다. 옵티마이저가 동치 변환할 수 있다|반드시 바깥 행 수만큼 전체 테이블을 재조회한다|항상 한 번만 수행된다|항상 오류가 발생한다','상관 여부는 논리적인 외부 참조 특징이며 실제 실행은 실행 계획에 달려 있다.','학습용 행별 계산 설명을 실제 엔진 실행 증거로 표현하지 않는다.')])
# Single-row scalar semantics.
P(2,[
C('스칼라 서브쿼리의 반환 행이 0개다. v의 값은?','NULL|0|빈 테이블 객체|항상 오류','0행인 스칼라 서브쿼리는 NULL값을 제공한다.','0행과 두 행 이상 오류, COUNT의 0을 구별한다.',"SELECT (SELECT n FROM T WHERE 1=0) v FROM dual;"),
C('스칼라 서브쿼리가 n=4와 n=7 두 행을 반환한다. 실행 결과는?','단일행 서브쿼리 다중행 오류|4|7|11','스칼라 위치는 한 값만 허용하므로 두 행을 임의 선택하거나 합산하지 않는다.','집계나 행 제한이 없는 한 첫 행 선택 규칙은 없다.',"SELECT (SELECT n FROM T) v FROM dual;",T('T',['n'],[[4],[7]])),
C('T가 비어 있고 GROUP BY가 없다. 다음 v는?','0|NULL|0행|다중행 오류','COUNT(*) 집계는 입력이 없어도 한 행의 0을 반환한다.','일반 스칼라 서브쿼리의 0행 NULL 규칙과 집계 결과 한 행을 구별한다.',"SELECT (SELECT COUNT(*) FROM T) v FROM dual;")])
P(2,[
C('T의 n={2,6,10}이다. 아래 결과 n은?','10|6과 10|2와 6|모든 행','AVG=6이고 엄격한 > 조건이므로 10만 남는다.','평균과 같은 6을 포함하지 않는다.',"SELECT n FROM T WHERE n>(SELECT AVG(n) FROM T);",T('T',['n'],[[2],[6],[10]])),
C('T는 비어 있다. 아래 비교 5 > (SELECT MAX(n) FROM T)의 진리값은?','UNKNOWN|TRUE|FALSE|항상 오류','빈 입력의 MAX는 NULL이고 5>NULL은 UNKNOWN이다.','COUNT와 MAX의 빈 입력 반환값을 구별한다.'),
C('T(n,dept)={(2,A),(7,B)}이고 안쪽 GROUP BY는 두 그룹을 만든다. 결과는?','다중행 오류|9|7|2','그룹별 SUM은 두 행을 반환하므로 스칼라 비교 =의 단일값 요구를 위반한다.','집계 함수를 썼다고 GROUP BY 결과가 항상 한 행이 되지는 않는다.',"SELECT 1 FROM dual WHERE 7=(SELECT SUM(n) FROM T GROUP BY dept);")])
# Multirow conditions: four per set.
P(3,[
C('3 > ANY ({2,5})의 진리값은?','TRUE|FALSE|UNKNOWN|오류','3>2가 TRUE여서 하나 이상을 만족하는 ANY는 TRUE다.','ANY를 모든 값과 비교하는 ALL로 바꾸지 않는다.'),
C('3 > ALL ({2,5})의 진리값은?','FALSE|TRUE|UNKNOWN|오류','3>5가 FALSE이므로 모든 비교를 만족하지 못한다.','최솟값 2만 비교해서 ALL을 판단하지 않는다.'),
C('3 = ANY ({2,3,5})와 같은 의미의 조건은?','3 IN (2,3,5)|3 NOT IN (2,3,5)|3 > ALL (2,3,5)|3 < ALL (2,3,5)','=ANY는 목록 중 적어도 하나와 같은지를 묻는 IN과 대응한다.','ANY 자체를 언제나 IN으로 바꾸는 것이 아니라 =ANY일 때 대응한다.')])
P(3,[
C('5 > ANY (빈 서브쿼리)의 진리값은?','FALSE|TRUE|UNKNOWN|오류','비교를 만족하는 원소가 하나도 없어 ANY는 FALSE다.','빈 결과를 NULL 한 행과 같게 보지 않는다.'),
C('5 > ALL (빈 서브쿼리)의 진리값은?','TRUE|FALSE|UNKNOWN|오류','ALL은 반례가 없으므로 빈 결과에 대해 TRUE다.','집계 MAX가 NULL인 경우와 빈 집합 ALL은 다르다.'),
C('NULL = ANY (빈 서브쿼리)의 진리값은?','FALSE|UNKNOWN|TRUE|오류','빈 결과에는 비교 항 자체가 없으므로 ANY는 FALSE다.','NULL이 등장했다는 이유만으로 빈 집합 비교를 UNKNOWN으로 단정하지 않는다.')])
P(3,[
C('5 NOT IN (2,NULL)의 진리값은?','UNKNOWN|TRUE|FALSE|오류','5<>2는 TRUE지만 5<>NULL이 UNKNOWN이므로 AND 결과는 UNKNOWN이다.','확실한 불일치 하나가 전체 NOT IN을 TRUE로 만들지는 않는다.'),
C('2 NOT IN (2,NULL)의 진리값은?','FALSE|UNKNOWN|TRUE|오류','2<>2가 FALSE이므로 나머지가 UNKNOWN이어도 전체 AND는 FALSE다.','NULL이 있으면 NOT IN이 무조건 UNKNOWN이라는 암기도 틀린다.'),
C('5 > ANY (2,NULL)의 진리값은?','TRUE|UNKNOWN|FALSE|오류','5>2가 TRUE이므로 TRUE OR UNKNOWN은 TRUE다.','ANY와 ALL의 결합 논리가 다르다.')])
P(3,[
C('5 > ALL (2,NULL)의 진리값은?','UNKNOWN|TRUE|FALSE|오류','5>2는 TRUE, NULL 비교는 UNKNOWN이므로 전체 ALL은 UNKNOWN이다.','NULL을 0으로 치환하지 않는다.'),
C('1 > ALL (2,NULL)의 진리값은?','FALSE|UNKNOWN|TRUE|오류','1>2가 FALSE여서 AND의 나머지가 UNKNOWN이어도 FALSE다.','ALL에서 확정된 반례 하나는 전체를 FALSE로 만든다.'),
C('E의 id={1,2}, D의 id={1,NULL}이다. NOT EXISTS 결과는?','2|없음|1과 2|1','E.id=2에 일치하는 D행이 없으므로 반환한다. NULL은 동등 비교로 2와 일치하지 않는다.','NOT EXISTS를 NULL이 있는 NOT IN과 무조건 동치로 바꾸지 않는다.',"SELECT E.id FROM E WHERE NOT EXISTS\n(SELECT 1 FROM D WHERE D.id=E.id);")])
# Multiple columns.
P(4,[
C('T={(1,A),(1,B),(2,A)}, S={(1,A),(2,B)}이다. 쌍 IN 결과는?','(1,A)|(1,A),(1,B),(2,A)|(1,B),(2,A)|(2,A)','a,b가 같은 한 행의 쌍으로 동시에 일치해야 하므로 (1,A)만 남는다.','각 열의 IN 목록을 독립 결합하면 잘못된 조합이 추가된다.',"SELECT a,b FROM T WHERE (a,b) IN (SELECT a,b FROM S);"),
C('(a,b) IN 서브쿼리에서 안쪽 SELECT가 a만 반환한다. 판단은?','비교 열 수가 맞지 않아 오류|b를 자동 NULL로 채운다|첫 열만 비교한다|Cartesian 곱으로 보정한다','행 값 비교는 대응하는 열 수가 같아야 한다.','자동 누락열 보충이나 열 무시는 하지 않는다.',"SELECT * FROM T WHERE (a,b) IN (SELECT a FROM S);"),
C('T={(1,X),(2,Y)}, S={(1,X),(1,X)}이다. 쌍 IN으로 T를 조회한 결과 행 수는?','1|2|3|4','멤버십 조건은 일치 존재를 확인하므로 S의 중복이 T행을 증식시키지 않는다.','동등 조인에서의 일치 수만큼 증식과 IN을 혼동하지 않는다.',"SELECT a,b FROM T WHERE (a,b) IN (SELECT a,b FROM S);")])
P(4,[
C('(1,2) NOT IN ((2,NULL))의 진리값은?','TRUE|UNKNOWN|FALSE|오류','첫 열 1=2가 FALSE이므로 전체 행 동등성은 FALSE이고 그 부정은 TRUE다.','행 비교에서는 다른 열의 확실한 불일치가 NULL 영향을 결정할 수 있다.'),
C('(1,2) NOT IN ((1,NULL))의 진리값은?','UNKNOWN|TRUE|FALSE|오류','첫 열은 같지만 둘째 열은 UNKNOWN이므로 행 동등성도 UNKNOWN이고 NOT도 UNKNOWN이다.','모든 열 비교의 논리를 결합해야 한다.'),
C('T={(1,A),(2,B)}, S={(1,B),(2,A)}이다. (a,b) IN S와 a IN S.a AND b IN S.b의 차이는?','쌍 IN은 0행, 독립 IN은 2행|둘 다 2행|둘 다 0행|쌍 IN만 2행','원래 쌍은 하나도 없지만 각 열 값은 모두 독립 목록에 존재한다.','다중컬럼 조건을 각 열 조건으로 분해하면 조합 의미를 잃을 수 있다.')])
# Scalar, inline, correlation: three.
P(5,[
C('E={(1,A),(2,B)}, D={(A,개발)}이다. 다음 결과의 name은?','id1 개발, id2 NULL|id1 개발만 반환|둘 다 개발|id2에서 무조건 오류','상관 스칼라 조회는 A에 한 행, B에 0행이므로 각각 개발과 NULL을 준다.','스칼라 서브쿼리 0행은 바깥 행 제거가 아니라 NULL값이다.',"SELECT E.id,(SELECT D.name FROM D WHERE D.dept=E.dept) name FROM E;"),
C('D에 같은 dept=A인 서로 다른 name 두 행이 있다. E의 A행에서 상관 스칼라 조회는?','다중행 오류|항상 첫 name|항상 마지막 name|name 두 값을 자동 연결','바깥 한 행에서 두 값을 반환하면 스칼라 조건을 위반한다.','중복 제거·집계·명시적 제한 없이 임의 값을 선택하지 않는다.'),
C('E에는 3행이 있고 독립 스칼라 서브쿼리 SELECT COUNT(*) FROM D의 결과는 2다. 바깥 결과는?','3행이며 각 cnt가 2|1행 cnt=2|6행|2행 cnt=3','SELECT 목록의 스칼라 값은 바깥 각 행에 붙으며 바깥 E의 행 수를 바꾸지 않는다.','집계가 안쪽에 있다는 사실을 바깥 전체 집계로 바꾸지 않는다.',"SELECT E.id,(SELECT COUNT(*) FROM D) cnt FROM E;")])
P(5,[
C('T의 dept별 점수가 A:10,20 / B:40이다. 아래 평균 초과 id는?','A의 20점 행만|A의 20점과 B의 40점|모든 행|없음','부서 평균 A=15,B=40이다. 엄격히 초과하는 A20만 남는다.','전체 평균과 부서별 평균을 혼동하거나 같은 값을 초과로 포함하지 않는다.',"SELECT E.id FROM T E WHERE E.score>\n(SELECT AVG(X.score) FROM T X WHERE X.dept=E.dept);"),
C('E.id={1,2}, D.eid={1,1}이다. EXISTS 조회 결과의 E행 수는?','1|2|3|4','E1은 일치 존재가 TRUE여서 한 번 남고 E2는 FALSE다. D의 두 행이 E를 복제하지 않는다.','EXISTS의 선택과 일반 조인의 행 증식을 구별한다.',"SELECT E.id FROM E WHERE EXISTS (SELECT 1 FROM D WHERE D.eid=E.id);"),
C('EXISTS 안쪽 SELECT 목록이 NULL이지만 WHERE를 만족하는 행이 한 개 존재한다. EXISTS는?','TRUE|FALSE|UNKNOWN|오류','EXISTS는 반환 값이 아니라 행의 존재 여부를 본다. NULL 한 행도 존재한다.','SELECT NULL을 0행으로 오해하지 않는다.',"SELECT 1 FROM dual WHERE EXISTS (SELECT NULL FROM dual);")])
P(5,[
C('인라인 뷰에서 그룹별 합계를 total로 만든 뒤 바깥에서 total>10을 필터한다. 합계 A=8,B=12일 때 결과는?','B|A|A와 B|없음','먼저 그룹별 집계한 결과를 바깥 WHERE가 필터하므로 B만 남는다.','원본 개별 행 값과 집계 결과 total을 구별한다.',"SELECT dept FROM\n(SELECT dept,SUM(v) total FROM T GROUP BY dept)\nWHERE total>10;"),
C('같은 SELECT 목록에서 AVG(v) OVER()에 avg_v 별칭을 붙였다. 그 SELECT의 WHERE에서 avg_v를 바로 필터하려 한다. 적절한 해결은?','안쪽 조회에서 계산하고 바깥 조회에서 별칭을 필터한다|별칭은 WHERE에서 항상 바로 사용 가능하다|WHERE를 FROM 앞으로 옮긴다|AVG를 열 이름으로 다시 선언한다','분석 함수 결과는 WHERE보다 뒤 단계에서 계산하므로 조회 단계를 분리해야 한다.','SELECT 별칭과 분석 결과의 평가 위치를 확인한다.'),
C('바깥 E행을 기준으로 안쪽 D의 존재 여부만 필요할 때 EXISTS를 선택한 의미는?','일치 개수와 무관하게 존재 여부로 바깥 행을 선별한다|항상 물리 실행 속도가 모든 JOIN보다 빠르다는 보장|모든 D열을 결과에 추가한다|D의 모든 행을 삭제한다','EXISTS는 존재 조건을 명확하게 표현한다. 성능 우열은 실행 계획·데이터 조건에 달려 있다.','논리 의미와 검증하지 않은 성능 보장을 분리한다.')])

# Set operators: four decisions.
P(6,[
C('A의 n={1,1,2}, B의 n={1,3}이다. UNION 결과 행 수는?','3|5|4|2','중복을 제거한 값은 1,2,3 세 개다.','UNION ALL의 5행과 구별한다.',"SELECT n FROM A UNION SELECT n FROM B;"),
C('A의 n={1,1,2}, B의 n={1,3}이다. UNION ALL 결과 행 수는?','5|3|4|2','양쪽의 3행과 2행을 중복 유지하여 합치므로 5행이다.','UNION의 중복 제거를 적용하지 않는다.',"SELECT n FROM A UNION ALL SELECT n FROM B;"),
C('A의 n={1,1,2}, B의 n={1,1,3}이다. INTERSECT 결과는?','1 한 행|1 두 행|1 네 행|1과 2','Oracle INTERSECT는 공통 값의 중복을 제거하므로 1 한 행이다.','조인의 일치 곱이나 다중집합 교집합으로 계산하지 않는다.',"SELECT n FROM A INTERSECT SELECT n FROM B;")])
P(6,[
C('A={1,2}, B={2,3}에서 A MINUS B는?','1|3|1과 3|2','A에 있지만 B에는 없는 값 1이다.','MINUS의 방향을 뒤집지 않는다.',"SELECT n FROM A MINUS SELECT n FROM B;"),
C('A={NULL,1}, B={NULL,2}에서 UNION 결과는?','NULL,1,2의 3행|NULL 두 개와 1,2의 4행|1,2만|NULL 한 행만','집합 연산 중복 판정에서는 두 NULL을 하나로 통합한다.','WHERE의 NULL=NULL이 UNKNOWN인 비교와 집합 중복 제거를 혼동하지 않는다.'),
C('A={NULL,1}, B={NULL}에서 A MINUS B는?','1|NULL과 1|NULL만|공집합','집합 연산의 중복·일치 판정으로 B에 있는 NULL은 제거하고 1이 남는다.','NOT IN의 NULL 논리와 MINUS를 같은 방식으로 계산하지 않는다.')])
P(6,[
C('두 SELECT를 UNION하려는데 반환 열 수가 각각 2개와 3개다.','열 수 불일치로 오류|자동으로 NULL 열을 보충한다|첫 열만 비교한다|더 많은 쪽의 마지막 열을 무시한다','집합 연산의 대응 SELECT는 같은 수의 식을 반환해야 한다.','부족한 열을 자동 보충하지 않으므로 명시적으로 맞춰야 한다.'),
C('Oracle에서 한쪽은 NUMBER, 다른 쪽은 VARCHAR2인 같은 위치 열을 집합 연산으로 묶으려 한다. 안전한 조치는?','호환되는 같은 자료형 그룹으로 명시적 변환한다|집합 연산이 모든 자료형 그룹 사이를 자동 변환한다고 가정한다|열 순서를 무시한다|별칭만 같게 하면 모든 자료형 문제가 사라진다','집합 연산은 대응 열의 자료형 그룹 조건을 만족해야 하므로 의도한 변환을 명시한다.','별칭 일치와 자료형 호환성은 별개다.'),
C('A=(id=1,v=X), B=(id=1,v=Y)이다. 두 열 UNION의 결과 행 수는?','2|1|0|4','중복 판정은 반환 열 전체에 대해 하므로 v가 다른 두 튜플은 다르다.','첫 열 id만 보고 중복으로 제거하지 않는다.')])
P(6,[
C('A={1,2}, B={2,3}, C={2}이다. 괄호가 명시된 (A UNION B) MINUS C는?','1과 3|2만|1,2,3|공집합','먼저 합집합 {1,2,3}에서 C의 2를 제거한다.','괄호를 생략해 다른 결합 순서로 계산하지 않는다.'),
C('A={1}, B={1}, C={2}이다. A UNION ALL (B UNION C)의 행 수는?','3|2|1|4','괄호 안의 B UNION C는 1,2 두 행이고 바깥 ALL은 A의 1을 추가해 3행이다.','안쪽 중복 제거가 바깥 ALL의 중복까지 없애지는 않는다.'),
C('UNION 결과를 n 오름차순으로 보장하려면 어디에 ORDER BY를 두는가?','전체 복합 조회의 마지막 ORDER BY|첫 SELECT에만 ORDER BY|UNION이 자동 정렬을 보장하므로 불필요|각 테이블 생성 순서에 맡김','최종 출력 순서는 복합 조회 전체의 ORDER BY로 지정한다.','중복 제거의 내부 처리나 저장 순서는 정렬 계약이 아니다.')])
# ROLLUP.
P(7,[
C('GROUP BY ROLLUP(a,b)가 만드는 그룹 집합은?','(a,b),(a),()|(a,b),(b),()|(a),(b)만|(a,b),(a),(b),()','ROLLUP은 지정 순서의 접두 그룹을 남겨 상세, a 소계, 전체합계를 만든다.','독립 b소계는 CUBE와 다르게 생성하지 않는다.'),
C('GROUP BY ROLLUP(b,a)가 만드는 소계 기준은?','b|a|a와 b 각각 모두|소계 없음','앞쪽 b를 남기는 접두 그룹이 생기므로 b 소계다.','ROLLUP 열 순서를 바꾸어도 결과가 같다고 생각하지 않는다.'),
C('GROUP BY a,ROLLUP(b)의 그룹 집합은?','(a,b),(a)|(a,b),(a),()|(a),(b),()|()만','a는 ROLLUP 밖의 고정 그룹 키로 남으므로 전체합계 ()가 없다.','부분 ROLLUP과 전체 ROLLUP을 구별한다.')])
P(7,[
C('T={(A,X,2),(A,Y,3),(B,X,4)}의 ROLLUP(a,b) 결과 행 수는?','6|7|5|3','상세 3 + a소계 2 + 전체 1 =6이다.','조합 수를 전체 가능한 a×b로 세지 않고 실제 그룹을 센다.',"SELECT a,b,SUM(v) FROM T GROUP BY ROLLUP(a,b);"),
C('같은 T의 ROLLUP(b,a) 결과에서 b=X 소계는?','6|2|4|9','b=X인 A2와 B4를 합쳐 6이다.','a소계나 전체합계9와 구별한다.',tab=T('T',['a','b','v'],[['A','X',2],['A','Y',3],['B','X',4]])),
C('T={(A,X,2),(A,Y,3),(B,X,4)}에서 GROUP BY a,ROLLUP(b)의 결과 행 수는?','5|6|7|3','상세3 + a소계2이며 모든 a를 합친 전체합계는 없다.','ROLLUP 밖 a를 제거한 전체 행을 추가하지 않는다.')])
P(7,[
C('ROLLUP(a,b)에서 GROUPING(a)=0, GROUPING(b)=1인 행의 뜻은?','a별 소계|상세 행만|전체합계|b별 소계','a는 그룹에 남고 b가 집계되어 생성된 행이므로 a 소계다.','표시값 NULL만으로 구별하지 말고 GROUPING 플래그를 본다.'),
C('ROLLUP(a,b)에서 전체합계만 남기려 한다. 조건은?','HAVING GROUPING(a)=1 AND GROUPING(b)=1|HAVING a IS NULL|WHERE GROUPING(a)=1|HAVING GROUPING(a)=0 AND GROUPING(b)=0','전체합계는 두 키 모두 집계되어 플래그가 1이다.','원본 NULL이 있을 수 있고 GROUPING은 집계 후 HAVING에서 사용한다.'),
C('원본 a=NULL인 상세 행도 있다. ROLLUP 결과 a IS NULL만으로 전체합계를 골라도 되는가?','안 된다. 원본 NULL과 집계 생성 NULL을 구별해야 한다|항상 된다. NULL은 원본에 존재할 수 없다|ROLLUP은 원본 NULL 행을 삭제한다|NULL 행은 GROUPING 값이 항상 1이다','집계로 제거된 키와 실제 저장된 NULL은 GROUPING으로 구별한다.','IS NULL은 값 검사이므로 집계 수준 자체를 알려 주지 않는다.')])
# CUBE/GROUPING SETS.
P(8,[
C('CUBE(a,b)가 만드는 그룹 집합 개수는?','4|3|2|8','(a,b),(a),(b),()의 네 조합이다.','이론적 그룹 집합 수와 실제 출력 행 수는 다르다.'),
C('CUBE(a,b,c)의 그룹 집합 개수는?','8|4|6|3','독립된 세 그룹 표현식의 포함 여부 조합은 2의 3제곱인 8개다.','실제 데이터별 출력 행 수를 8로 고정하는 뜻은 아니다.'),
C('GROUPING SETS((a),(b))가 생성하지 않는 것은?','전체합계 ()|a별 집계|b별 집계|명시된 두 그룹 집합','명시한 (a),(b)만 계산하므로 전체합계는 포함하지 않는다.','GROUPING SETS에 암묵적 ()가 추가된다고 생각하지 않는다.')])
P(8,[
C('T={(A,X,2),(A,Y,3),(B,X,4)}에서 CUBE(a,b)의 출력 행 수는?','8|6|7|9','상세3+a소계2+b소계2+전체1=8이다.','CUBE 그룹 집합 4개와 출력 행 수8을 구별한다.'),
C('같은 T에서 GROUPING SETS((a),())의 출력 행 수는?','3|6|4|2','a별 A,B 두 행과 전체합계 한 행을 더해3이다.','상세 (a,b)는 명시하지 않았으므로 나오지 않는다.',tab=T('T',['a','b','v'],[['A','X',2],['A','Y',3],['B','X',4]])),
C('T={(A,X,2),(A,Y,3),(B,X,4)}에서 GROUPING SETS((a),(b))의 합계값 집합은?','5,4,6,3|2,3,4|9만|5,4,9','a별 A5,B4와 b별 X6,Y3 네 행이다.','전체합계와 상세행은 요청하지 않았다.')])
P(8,[
C('GROUP BY GROUPING SETS((a),(a))의 중복 그룹 집합은 어떻게 취급하는가?','같은 집계 행이 반복될 수 있다|자동 DISTINCT로 항상 한 번만 나온다|문법상 항상 금지다|전체합계로 자동 치환된다','GROUPING SETS는 지정된 집계 결과를 UNION ALL 성격으로 결합하므로 중복 지정 결과가 반복될 수 있다.','집합이라는 이름만 보고 결과 중복 제거를 가정하지 않는다.'),
C('CUBE((a,b),c)에서 (a,b)를 복합 항목으로 묶었다. 생성되는 그룹 집합은?','(a,b,c),(a,b),(c),()|(a),(b),(c),()만|단일 a와 단일 b를 포함한 8개|상세 (a,b,c)만','(a,b)를 한 단위로 포함·제외하여 두 항목의 4개 조합을 만든다.','괄호로 묶인 복합 항목을 독립 a,b로 펼치지 않는다.'),
C('ROLLUP(a,b)와 GROUPING SETS((a,b),(a),())는?','같은 그룹 집합을 표현한다|후자는 b소계를 추가한다|전자만 전체합계를 만든다|후자는 상세행을 만들지 않는다','ROLLUP의 접두 그룹 집합을 그대로 명시한 표현이다.','출력 정렬은 어느 쪽도 ORDER BY 없이 보장하지 않는다.')])
# GROUPING / GROUPING_ID.
P(9,[
C('원본 a=NULL인 상세 그룹에서 GROUPING(a)는?','0|1|NULL|자료형에 따라 임의값','a가 실제 그룹 키에 포함되어 있으면 원본 값이 NULL이어도 GROUPING=0이다.','GROUPING은 IS NULL 함수가 아니다.'),
C('전체합계 행의 GROUPING(a),GROUPING(b)는?','1,1|0,0|1,0|NULL,NULL','두 열 모두 해당 집계 수준에서 제거되었으므로 1이다.','합계가 NULL인지 여부와 무관하다.'),
C('CASE WHEN GROUPING(a)=1 THEN \'합계\' ELSE a END는 무엇을 구별하는가?','집계 때문에 제거된 a와 원래 그룹 키 a|모든 NULL을 같은 문자열로 바꾸기만 함|a가 숫자인지 여부|행이 정렬되었는지 여부','GROUPING은 집계 생성 행 표시를 제공하므로 저장 NULL과 구별되는 라벨링에 쓸 수 있다.','ELSE a에 원본 NULL이 있으면 그대로 NULL일 수 있다.')])
P(9,[
C('GROUPING(a)=0, GROUPING(b)=1일 때 GROUPING_ID(a,b)는?','1|2|3|0','a,b 플래그 01을 이진수로 해석하므로 1이다.','오른쪽 인수 b가 하위 비트다.'),
C('GROUPING(a)=1, GROUPING(b)=0일 때 GROUPING_ID(a,b)는?','2|1|3|0','플래그 10의 십진 값은2다.','인수 순서를 바꾸면 비트 위치도 달라진다.'),
C('GROUPING(a)=1, GROUPING(b)=0, GROUPING(c)=1이면 GROUPING_ID(a,b,c)는?','5|3|6|7','101의 십진 값은4+1=5다.','플래그를 단순 합산한2나 전체합계111과 혼동하지 않는다.')])
# OVER: two.
P(10,[
C('T의 부서 A에 2행, B에1행이 있다. SUM(v) OVER(PARTITION BY dept)는 결과를 몇 행으로 만드는가?','3행|2행|1행|0행','분석 함수는 행을 그룹별 한 행으로 축약하지 않고 각 원본 행에 결과를 붙인다.','GROUP BY의 행 축약과 구별한다.'),
C('SUM(v) OVER()에서 PARTITION BY가 없다는 의미는?','조회 결과 전체를 하나의 파티션으로 계산한다|각 행이 반드시 별도 파티션이다|오류다|빈 파티션만 만든다','파티션 구분을 생략하면 대상 전체가 한 그룹이다.','일반 집계처럼 바깥 행 수를 한 행으로 축약하지 않는다.'),
C('분석 함수 안 ORDER BY id만 있고 조회 마지막 ORDER BY는 없다. 최종 표시 순서는?','분석 정렬만으로 최종 출력 순서를 보장하지 않는다|항상 id 오름차순으로 보장된다|항상 id 내림차순이다|모든 행이 무작위로 강제된다','OVER의 정렬은 분석 계산 기준이며 최종 출력 순서 계약은 바깥 ORDER BY다.','우연히 보이는 순서를 보장으로 설명하지 않는다.')])
P(10,[
C('T={(1,2),(2,5),(3,8)}이고 WHERE v>=5 뒤 SUM(v) OVER()를 계산한다. 각 합계는?','13|15|8|5','WHERE 후 남은5,8을 대상으로 분석 합계13을 계산한다.','필터에서 제외된2를 포함하지 않는다.',"SELECT id,SUM(v) OVER() s FROM T WHERE v>=5;"),
C('A부서 v=2,3이고 B부서 v=7이다. 부서별 분석 SUM의 값은?','A행들 5, B행 7|모든 행 12|A행들 2,3, B행7|A행들7,B행5','PARTITION BY dept가 A와 B를 분리하여 합계를 붙인다.','전체 OVER()와 행별 값 표시를 구별한다.'),
C('분석 함수의 결과 rn=1만 고르려 한다. Oracle19c에서 적절한 위치는?','인라인 뷰의 분석 결과를 바깥 WHERE로 필터|같은 SELECT의 WHERE에서 ROW_NUMBER() 직접 사용|FROM 전에 HAVING 작성|OVER 내부 WHERE rn=1','Oracle19c는 WHERE 후 분석을 수행하므로 쿼리 블록을 나눈다.','새 버전의 다른 구문을 Oracle19c에 임의 적용하지 않는다.')])
# Rank: three.
P(11,[
C('점수 내림차순 90,90,80의 RANK는?','1,1,3|1,1,2|1,2,3|3,3,1','동점은 같은 순위를 받고 그 다음은 앞선 행 수를 반영하여3이다.','DENSE_RANK와 구별한다.'),
C('점수 내림차순 90,90,80의 DENSE_RANK는?','1,1,2|1,1,3|1,2,3|2,2,1','서로 다른 점수 그룹 순서에 빈 순위 없이 번호를 준다.','RANK의 건너뜀을 적용하지 않는다.'),
C('점수 내림차순 90,90,80의 ROW_NUMBER 결과에 대한 설명은?','서로 다른 1,2,3을 주지만 동점 두 행의 배정은 보조 키 없이 불확정일 수 있다|동점 두 행은 둘 다1이다|반드시 삽입 순서로1,2를 준다|중복 점수가 있으면 오류','ROW_NUMBER는 행별 고유 번호를 주되 전체 순서가 정해지지 않은 동점의 배정은 보장되지 않는다.','RANK처럼 동점 번호를 공유하지 않는다.')])
P(11,[
C('T(id,score)={(1,90),(2,90),(3,80)}에 ROW_NUMBER OVER(ORDER BY score DESC,id ASC)를 쓰면 id2의 번호는?','2|1|3|불확정','점수 동점은 id오름차순으로 풀어 id1,id2,id3 순서가 확정된다.','보조 키가 유일한 순서를 만들므로 동점 불확정을 남기지 않는다.'),
C('A부서 점수80,70 / B부서 점수95,90이다. PARTITION BY dept로 RANK DESC를 계산한 1위 행 수는?','2|1|4|3','각 부서에서 순위를 새로 시작하여 A80과 B95가 1위다.','전체 테이블 순위와 부서별 순위를 구별한다.'),
C('점수100,90,90,80에서 RANK<=3으로 필터하면 행 수는?','3|4|2|1','순위1,2,2,4이므로 처음 세 행만 남는다.','순위 번호3이 없다고 결과를2행으로 줄이지 않는다.')])
P(11,[
C('점수100,90,90,80에서 DENSE_RANK<=3이면 행 수는?','4|3|2|1','순위1,2,2,3으로 네 행 모두 조건을 만족한다.','상위3개의 서로 다른 점수와 상위3행은 다르다.'),
C('점수가 NULL,90,80일 때 Oracle ORDER BY score DESC만 사용한 RANK1은?','NULL 점수 행|90 점수 행|80 점수 행|NULL은 자동 제외되어 없음','Oracle의 DESC 기본 NULLS FIRST로 NULL이 선두에 놓인다.','높은 실수 점수를 먼저 원하면 NULLS LAST를 명시한다.'),
C('RANK() OVER(ORDER BY score DESC,id)에서 id가 고유하다. score가 같아도 같은 순위를 받는가?','전체 정렬 키가 달라 같은 순위가 아닐 수 있다|score만 같으면 언제나 동순위다|id는 자동 무시된다|RANK는 여러 정렬 키를 허용하지 않는다','동점 판정은 모든 정렬 키 조합에 대한 동등성이다.','안정 정렬용 보조 키 추가가 RANK의 동점 정의까지 바꾼다는 점을 확인한다.')])
# Aggregate windows: three.
P(12,[
C('id=1,2,3 순서의 v=2,5,7이다. ROWS UNBOUNDED PRECEDING 누적 SUM은?','2,7,14|14,14,14|2,5,7|7,12,14','현재 행까지 물리 행을 누적하여2,2+5,2+5+7이 된다.','전체 파티션 합계와 이동창을 구별한다.',"SELECT id,SUM(v) OVER(ORDER BY id ROWS UNBOUNDED PRECEDING) s FROM T;"),
C('id=1,2,3의 v=2,5,7이다. ROWS BETWEEN 1 PRECEDING AND CURRENT ROW에서 id3 합계는?','12|14|7|5','id3 현재7과 직전id2의5만 합쳐12다.','UNBOUNDED 누적합처럼id1까지 포함하지 않는다.'),
C('id=1,2,3의 v=2,NULL,6이다. 같은 1 PRECEDING~CURRENT ROW 창에서 id2의 AVG(v)는?','2|1|NULL|0','창에는2,NULL이 있고 AVG는 NULL을 제외해2/1=2다.','창의 물리 행 수2를 AVG의 비NULL 분모로 착각하지 않는다.')])
P(12,[
C('k=1,1,2이며 v=3,4,5이다. SUM(v) OVER(ORDER BY k)의 k=1 두 행 결과는?','둘 다7|3과7로 반드시 고정|둘 다12|둘 다1','기본 RANGE UNBOUNDED PRECEDING~CURRENT ROW는 같은 k인 동료 행을 함께 포함한다.','기본 프레임을 ROWS로 가정하지 않는다.'),
C('동일 k=1인 두 행 v=3,4가 있고 ROWS 누적합의 ORDER BY는 k뿐이다. 개별 행 결과 판단은?','동점 내 순서가 불확정이어서 특정 행의 누적값을 단정하기 어렵다|각 행은 반드시7|v=3행이 무조건먼저다|반드시 오류','ROWS는 물리 순서 기반이므로 동점 해소 키가 없으면 개별 행 누적값 배정이 달라질 수 있다.','RANGE의 동료 행 통합 결과를 ROWS에 적용하지 않는다.'),
C('k=1,1,2이며 v=3,4,5이다. RANGE BETWEEN CURRENT ROW AND CURRENT ROW의 합계는?','k1행들7, k2행5|3,4,5|12,12,12|0,0,0','RANGE CURRENT ROW는 정렬 키가 같은 동료 그룹을 포함한다.','현재 행이 항상 물리 한 행이라는 가정은 ROWS와 구별해야 한다.')])
P(12,[
C('날짜 대신 수치 k=1,3,4이고 v=10,20,30이다. RANGE BETWEEN 1 PRECEDING AND CURRENT ROW에서 k4의 SUM은?','50|60|30|40','키 범위[3,4]에 있는20,30을 합친다.','앞의 모든 행을 포함하는 누적합과 다르다.'),
C('k=1,3,4이고 v=10,20,30이다. RANGE 1 PRECEDING에서 k3의 SUM은?','20|30|50|60','키 범위[2,3]에는 k3만 있다. k1은 물리 직전 행이지만 범위 밖이다.','ROWS 1 PRECEDING이면k1도 포함하지만 RANGE는 값 간격이다.'),
C('id=1,2,3의 v=2,5,7이다. ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING의 SUM은?','14,12,7|2,7,14|14,14,14|2,5,7','현재부터 마지막까지 합쳐14,5+7=12,7이 된다.','이전 방향 누적과 이후 방향 누적을 구별한다.')])
# Other windows: three.
P(13,[
C('id1,2,3의 v=10,20,30이다. LAG(v,1,0) OVER(ORDER BY id)의 결과는?','0,10,20|20,30,0|10,20,30|NULL,NULL,NULL','LAG는 이전 행을 보고 첫 행에는 범위 밖 기본값0을 반환한다.','LEAD의 다음 행 방향과 구별한다.',source=BASE+'LAG.html'),
C('id1,2,3의 v=10,20,30이다. LEAD(v,1,-1)의 결과는?','20,30,-1|-1,10,20|10,20,30|-1,-1,-1','다음 행 값이 없는 마지막에만 기본값-1을 사용한다.','기본값을 모든 NULL이나 모든 행에 적용하지 않는다.',source=BASE+'LEAD.html'),
C('id1,2,3의 v=10,NULL,30이다. LAG(v,1,0)에서 id3의 결과는?','NULL|0|10|30','기본 RESPECT NULLS에서는 실제 직전 행의 NULL을 반환한다. 기본값0은 대상 행이 없을 때 쓴다.','NULL 대상과 파티션 범위 밖을 구별한다.',source=BASE+'LAG.html')])
P(13,[
C('id1,2,3의 v=10,20,30이다. LAST_VALUE(v) OVER(ORDER BY id)의 id1 결과는?','10|30|NULL|20','기본 프레임 끝이 현재 행이므로 id1 창의 마지막은10이다.','함수 이름만 보고 항상 파티션 끝30을 반환한다고 생각하지 않는다.'),
C('id1,2,3의 v=10,20,30이다. 모든 행에 마지막 값30을 붙일 프레임은?','ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING|ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW|ROWS BETWEEN CURRENT ROW AND CURRENT ROW|ROWS BETWEEN 1 PRECEDING AND CURRENT ROW','전체 파티션 끝까지 프레임에 넣으면 LAST_VALUE가 마지막30을 본다.','현재 행에서 끝나는 프레임은 앞선 행에30을 보장하지 않는다.'),
C('id1,2,3의 v=10,NULL,30이다. LAST_VALUE(v IGNORE NULLS)를 처음부터 현재까지 ROWS로 계산한 id2 결과는?','10|NULL|30|0','현재까지10,NULL 중 NULL을 무시한 마지막 값은10이다.','아직 창에 없는 다음30을 가져오지 않는다.')])
P(13,[
C('v=2,3,5인 전체 파티션에서 RATIO_TO_REPORT(v)의 v3행 값은?','0.3|3|0.5|0.2','합계10에 대한 해당3의 비율은3/10이다.','순위나 누적 비율로 바꾸지 않는다.',source=BASE+'RATIO_TO_REPORT.html'),
C('고유 id1~5에 NTILE(2) OVER(ORDER BY id)를 적용한 버킷 번호는?','1,1,1,2,2|1,1,2,2,2|1,2,1,2,1|1,2,3,4,5','5행을 최대 한 행 차이로 나누고 큰 버킷을 먼저 배치해3행과2행이 된다.','동일 점수 그룹을 묶는 DENSE_RANK와 다르다.',source=BASE+'NTILE.html'),
C('정렬값10,20,20,30에서 CUME_DIST의 20행 값은?','0.75|0.5|0.25|1','현재 값 이하인 행은10과20두행으로3개, 전체4개여서3/4이다.','동료행을 한 그룹만 세거나 현재 물리 위치만 세지 않는다.',source=BASE+'CUME_DIST.html')])

# Top-N: three.
P(14,[
C('Oracle19c에서 점수 내림차순 상위2행을 안정적으로 고르려 한다. 올바른 방법은?','ORDER BY score DESC,id 후 FETCH FIRST 2 ROWS ONLY|같은 블록에서 WHERE ROWNUM<=2 후 ORDER BY score DESC|ORDER BY 없이 FETCH FIRST 2 ROWS ONLY만 사용|WHERE ROWNUM>2만 사용','정렬한 결과를 행 제한하며 유일한 id를 보조 키로 넣어 동점을 해소한다.','같은 블록 ROWNUM 선필터는 전체 최고점을 보장하지 않는다.',"SELECT id,score FROM T\nORDER BY score DESC,id FETCH FIRST 2 ROWS ONLY;"),
C('SQL Server 2022에서 최고 점수 2행을 고르려 한다. 적절한 구문은?','SELECT TOP (2) id,score FROM T ORDER BY score DESC,id|SELECT id,score FROM T WHERE ROWNUM<=2|SELECT LIMIT 2 id,score FROM T|SELECT id,score FROM T FETCH FIRST 2 ROWS ONLY','SQL Server는 TOP과 ORDER BY 조합을 사용할 수 있다.','Oracle ROWNUM이나 다른 DBMS LIMIT 구문을 섞지 않는다.',source='https://learn.microsoft.com/en-us/sql/t-sql/queries/top-transact-sql?view=sql-server-ver16'),
C('Oracle에서 고전적인 정렬 후 ROWNUM 상위N 방식의 구조는?','안쪽 조회 ORDER BY, 바깥 WHERE ROWNUM<=N|안쪽 ROWNUM<=N, 바깥 ORDER BY만|WHERE ROWNUM>N만|ORDER BY 없이 ROWNUM>N만','안쪽이 정렬한 후보를 바깥에서 N행으로 제한해야 의도한 순위 기준을 적용한다.','먼저 임의 N행을 고른 뒤 정렬하는 구조와 구별한다.')])
P(14,[
C('score=100,90,90,80에서 ORDER BY score DESC FETCH FIRST 2 ROWS WITH TIES 결과 행 수는?','3|2|4|1','두 번째 경계 점수90과 같은 동점 행까지 포함하여3행이다.','WITH TIES는 정확히2행 보장이 아니다.'),
C('같은 데이터에 고유 id를 ORDER BY score DESC,id로 추가하고 FETCH FIRST 2 ROWS WITH TIES하면?','2행|반드시3행|반드시4행|문법 오류','동점은 전체 ORDER BY 키로 판단하며 고유 id가 경계 동점을 없앤다.','score만 같은 행을 보존하려면 정렬 키의 동점 의미를 확인한다.'),
C('id1~5를 ORDER BY id OFFSET 2 ROWS FETCH NEXT 2 ROWS ONLY로 조회하면?','id3,id4|id2,id3|id1,id2|id4,id5','처음2행을 건너뛰고 다음2행을 가져온다.','OFFSET 숫자를 시작 행 번호로 혼동하지 않는다.')])
P(14,[
C('Oracle WHERE ROWNUM>1만 사용해 두 번째 이후 행을 받으려 한다. 일반적인 결과는?','0행|첫 행을 제외한 전부|정확히1행|오류가 반드시 발생','처음 후보가 ROWNUM1로 조건을 통과하지 못하므로 다음 번호로 진행할 반환 행이 만들어지지 않는다.','페이지 범위는 안쪽에서 번호를 붙인 후 바깥에서 필터한다.'),
C('점수 동점 모두 포함한 부서별 최고점을 고르려 한다. 적절한 분석 조건은?','PARTITION BY dept ORDER BY score DESC NULLS LAST의 RANK=1|전체 ROW_NUMBER=1만|부서와 무관한 ROWNUM=1|COUNT(*)=1인 부서만','부서별 순위를 만들고 동점에 같은1을 주는 RANK로 선별한다.','정확히 한 행만 필요할 때의 ROW_NUMBER와 요구가 다르다.'),
C('서로 다른 점수 상위2등급을 모두 고르려 한다. 점수100,90,90,80에서 적절한 것은?','DENSE_RANK() OVER(ORDER BY score DESC)<=2를 바깥에서 필터|ROW_NUMBER()<=2만|WHERE ROWNUM=2|COUNT(score)<=2','조밀 순위1,2,2,3 중2까지 선택하면100과90두행을 모두 얻는다.','상위 행 수와 서로 다른 점수 등급 수를 구별한다.')])
# Hierarchy traversal: two.
P(15,[
C('id-parent가 (1,NULL),(2,1),(3,2)이다. 1을 루트로 PRIOR id=parent를 탐색한 LEVEL은?','id1=1,id2=2,id3=3|id1=0,id2=1,id3=2|모두1|id1=3,id2=2,id3=1','PRIOR id는 부모의 id이고 현재 parent와 연결하여 아래로 내려간다. 루트 LEVEL은1이다.','PRIOR가 붙은 쪽과 LEVEL 시작값을 확인한다.',"SELECT id,LEVEL FROM T START WITH id=1 CONNECT BY PRIOR id=parent;"),
C('같은 체인에서 id3을 시작으로 PRIOR parent=id를 쓰면 반환 id는?','3,2,1|3만|1,2,3,3|1만','이전 행의 parent와 현재 id를 연결하므로 자식에서 조상 방향으로 올라간다.','PRIOR의 위치가 탐색 방향을 바꾼다.'),
C('START WITH parent IS NULL의 역할은?','탐색 시작 루트 행을 정한다|모든 자식의 출력만 정렬한다|루트 행을 결과에서 반드시 제외한다|행마다 부모를 자동 생성한다','START WITH는 시작 조건이며 CONNECT BY가 다음 단계 연결을 정의한다.','정렬·출력 필터와 시작점을 구별한다.')])
P(15,[
C('T={(1,NULL),(2,1),(3,1),(4,2)}이다. 루트1에서 내려갈 때 id4의 LEVEL은?','3|4|2|1','경로1→2→4에 루트 포함3개 노드이므로LEVEL3이다.','id값4를 깊이로 사용하지 않는다.'),
C('루트 후보가 (1,NULL),(9,NULL)이고 각각 자식 하나가 있다. START WITH parent IS NULL이면?','두 루트에서 각각 LEVEL1로 시작한다|한 루트만 임의 선택한다|두 번째 루트는 LEVEL2다|오류다','여러 시작 행이 각각 계층 트리를 구성하며 LEVEL은 각 루트에서 다시1이다.','전체 결과 행 번호와 LEVEL을 혼동하지 않는다.'),
C('자기참조 순환 데이터에서 NOCYCLE 없이 CONNECT BY를 수행해 순환이 발견되면?','계층 루프 오류가 발생할 수 있다|무조건 자동 중복 제거된다|자동으로 최솟값 루트가 생긴다|원본 행이 삭제된다','Oracle의 일반 계층 탐색은 순환을 발견하면 오류가 날 수 있어 조건과 NOCYCLE을 확인한다.','무한 탐색을 항상 자동 허용하거나 자동 정리한다고 가정하지 않는다.')])
# Hierarchy applications: three.
P(16,[
C('name이 A→B→C인 체인이다. SYS_CONNECT_BY_PATH(name,\'/\')에서 C의 경로는?','/A/B/C|A/B/C|/C/B/A|/C','루트부터 현재 행까지 구분자를 앞에 붙여 연결한다.','선행 구분자와 탐색 방향을 빠뜨리지 않는다.'),
C('부모1의 자식 이름이 Z,A이고 자식2의 자식이 X이다. 계층 구조를 유지하며 형제 이름만 정렬할 구문은?','ORDER SIBLINGS BY name|ORDER BY name만|GROUP BY name|PARTITION BY name만','SIBLINGS 정렬은 같은 부모의 형제 순서를 정하면서 계층 구조를 유지한다.','일반 ORDER BY는 계층 결과의 표시 순서를 덮어쓸 수 있다.'),
C('루트 이름 ROOT, 자식C, 손자G일 때 G에서 CONNECT_BY_ROOT name은?','ROOT|C|G|NULL','CONNECT_BY_ROOT는 현재 경로 시작 행의 지정 값을 돌려준다.','현재 값이나 바로 위 부모값과 구별한다.')])
P(16,[
C('T={(1,NULL),(2,1),(3,2)}에서 START WITH id=1 CONNECT BY PRIOR id=parent 후 WHERE id<>2이면 id3은?','남을 수 있다|부모2를 숨겼으므로 반드시 제거된다|id2로 변경된다|무조건 오류','일반 WHERE는 계층을 구성한 뒤 각 행을 걸러 부모2를 제거하더라도 자식3을 자동 제거하지 않는다.','탐색 중 가지를 차단하는 CONNECT BY 조건과 출력 필터를 구별한다.',"SELECT id FROM T WHERE id<>2\nSTART WITH id=1 CONNECT BY PRIOR id=parent;"),
C('같은 체인에서 CONNECT BY PRIOR id=parent AND id<>2이면 id3은?','id2로 내려가는 연결이 차단되어 도달하지 않는다|WHERE 사례처럼 반드시 남는다|루트로 자동 승격된다|LEVEL이0이 된다','연결 조건이 현재 자식id2를 막으면 그 가지의 아래id3까지 탐색하지 못한다.','필터 적용 단계가 결과를 바꾼다.'),
C('루트1의 자식2,3 중 2에만 자식4가 있다. 전체 계층에서 CONNECT_BY_ISLEAF=1인 id는?','3과4|1과2|2와3|4만','현재 탐색 결과에서 자식이 없는3,4가 잎이다.','물리 행 순서의 마지막 한 행을 잎으로 고르지 않는다.')])
P(16,[
C('순환을 포함한 계층에서 NOCYCLE을 쓰는 목적은?','루프 때문에 전체 조회가 실패하지 않도록 순환 경로를 제어한다|모든 순환 원본 행을 삭제한다|순환이 없는 새 테이블을 자동 생성한다|LEVEL을 모두1로 바꾼다','NOCYCLE은 순환이 있어도 결과를 반환할 수 있게 하며 원본 데이터를 고치지 않는다.','데이터 정리 명령이나 무한 반복 허용으로 오해하지 않는다.'),
C('CONNECT_BY_ISCYCLE을 사용하려면 함께 고려할 Oracle 구문은?','CONNECT BY NOCYCLE|GROUP BY CUBE|PIVOT XML만|FOR UPDATE만','ISCYCLE은 NOCYCLE과 함께 순환 관련 행을 표시하는 계층 의사열이다.','일반 집계 플래그 GROUPING과 구별한다.'),
C('START WITH id=2로 중간 노드를 새 시작점으로 삼았다. 그 노드의 LEVEL은?','1|원본 전체 트리 깊이를 자동 유지|항상2|NULL','LEVEL은 해당 조회의 시작 행에서1로 계산된다.','원본 데이터의 절대 깊이와 선택한 탐색의 깊이는 다르다.')])
# Pivot three.
P(17,[
C('T(dept,q,v)={(A,Q1,2),(A,Q2,5),(B,Q1,7)}를 q의 Q1,Q2로 SUM PIVOT하면 B의 Q2 합계는?','NULL|0|7|5','B의 Q2에 대응하는 입력이 없어 SUM은 NULL이다.','없는 조합을 자동0으로 채우지 않으므로 필요하면 별도NVL을 쓴다.',"SELECT * FROM T PIVOT(SUM(v) FOR q IN ('Q1' AS q1,'Q2' AS q2));"),
C('T(dept,q,v)={(A,Q1,2),(A,Q1,3)}를 같은 조건으로 PIVOT한 A의 Q1값은?','5|2|3|두 행으로 반드시 유지','PIVOT 집계 SUM이 같은 그룹과 축의 두 값을 합친다.','첫 값이나 마지막 값을 임의 선택하지 않는다.'),
C('PIVOT 입력에 dept,q,v뿐 아니라 고유 id도 그대로 남겼다. 결과가 부서 한 행으로 합쳐지지 않을 수 있는 이유는?','집계·피벗에 쓰지 않은 id가 암묵적 그룹 키에 포함되기 때문|PIVOT은 집계하지 않기 때문|id가 자동 삭제되기 때문|SUM이 문자열 함수이기 때문','PIVOT은 참조되지 않은 나머지 입력 열로 암묵적 그룹을 만들므로 불필요한 id를 입력에서 빼야 한다.','입력 투영 범위가 그룹 수준을 바꾼다.')])
P(17,[
C('T(id,q1,q2)={(1,10,NULL)}를 기본 UNPIVOT하면 행 수는?','1|2|0|3','UNPIVOT의 기본값 EXCLUDE NULLS로 q2의 NULL행은 제외된다.','원본 열 개수와 출력 행 수가 항상 같지는 않다.',"SELECT * FROM T UNPIVOT(v FOR q IN(q1 AS 'Q1',q2 AS 'Q2'));"),
C('같은 T를 UNPIVOT INCLUDE NULLS하면 행 수는?','2|1|0|3','INCLUDE NULLS를 명시했으므로10행과NULL행을 모두 세로로 펼친다.','기본 EXCLUDE NULLS 규칙을 그대로 적용하지 않는다.'),
C('UNPIVOT으로 펼칠 q1은 NUMBER, q2는 DATE다. 먼저 확인할 조건은?','값 열의 호환되는 자료형 그룹|두 열 이름 길이가 같아야 함|행 수가 반드시2여야 함|항상 임의 문자열로 자동 변환됨','UNPIVOT 대상 값 열은 같은 자료형 그룹이어야 하므로 적절한 명시적 변환을 검토한다.','모든 자료형을 무조건 자동 통합한다고 가정하지 않는다.')])
P(17,[
C('두 행 (A,Q1,2),(A,Q1,3)을 SUM PIVOT한 후 UNPIVOT하면 원래 두 행을 완전히 복원할 수 있는가?','아니다. 집계로 합쳐진 세부 내역은 일반적으로 복원되지 않는다|항상2와3을 다시 분리한다|자동으로1과4를 생성한다|PIVOT은 집계를 수행하지 않아 항상 가능하다','합계5에는 원래 값 구성 정보가 없으므로 역변환이 원본 복원과 같지 않다.','형태 변환과 정보 손실 없는 가역성을 구별한다.'),
C('PIVOT의 IN 목록이 Q1,Q2뿐인데 원본에 Q3도 있다. Q3가 자동 별도 결과 열로 생성되는가?','아니다. 일반 PIVOT은 명시된 IN값의 열을 만든다|언제나 Q3열을 추가한다|Q3가 Q1에 자동 합산된다|Q3행이 원본에서 삭제된다','일반 정적 PIVOT은 지정한 축 값을 결과 열로 생성한다.','입력 값이 늘었다고 정적 열 목록이 자동 확장되지 않는다.'),
C('T={(1,10,20),(2,30,40)}를 q1,q2로 UNPIVOT하면 id1의 출력은?','(1,Q1,10),(1,Q2,20)|(1,10,20) 한 행|(1,Q1,30),(1,Q2,40)|(Q1,10),(Q2,20)으로 id가 항상 사라짐','유지 열 id는 각 펼쳐진 행에 남고 축 이름과 값이 세로 열로 나온다.','다른 원본 행의 값과 섞거나 보존 열을 자동 제거하지 않는다.')])
# Regex three, unique patterns and meanings.
P(18,[
C('REGEXP_LIKE(code,\'^[0-9]{3}$\')를 만족하는 값은?','123|A123|1234|12','처음과 끝 사이에 숫자가 정확히3개여야 한다.','부분 일치와 전체 일치, 정확한 반복 횟수를 구별한다.',source=BASE+'Pattern-matching-Conditions.html'),
C('REGEXP_LIKE(code,\'[0-9]{3}\')를 만족하는 값은?','A123B|AB12|ABC|A1B2C3','앵커가 없어서 연속된 세 숫자를 부분 문자열로 찾으면 된다.','숫자가 총3개라도 떨어져 있으면 연속 패턴에 맞지 않는다.',source=BASE+'Pattern-matching-Conditions.html'),
C('REGEXP_LIKE(\'abc\',\'^ABC$\',\'i\')의 결과는?','TRUE|FALSE|NULL|오류','i 옵션은 대소문자를 구별하지 않아 전체abc가ABC와 대응한다.','명시적 match_param을 기본 대소문자 설정으로 덮어쓰지 않는다.',source=BASE+'Pattern-matching-Conditions.html')])
P(18,[
C('REGEXP_SUBSTR(\'A12B345\',\'[0-9]+\',1,2)는?','345|12|A12|NULL','연속 숫자 첫 일치는12, 두 번째 일치는345이므로345다.','position1과 occurrence2의 역할을 바꾸지 않는다.'),
C('REGEXP_INSTR(\'AB12CD\',\'[0-9]+\')는?','3|12|4|0','숫자 부분12의 시작 위치는1부터 세어3이다.','찾은 문자열의 값12와 시작 인덱스3을 구별한다.',source=BASE+'REGEXP_INSTR.html'),
C('REGEXP_COUNT(\'a1b22c333\',\'[0-9]+\')는?','3|6|1|333','+가 연속 숫자 묶음 하나를 일치시키므로1,22,333의 세 번이다.','숫자 문자 총수6과 패턴 일치 횟수3을 구별한다.',source=BASE+'REGEXP_COUNT.html')])
P(18,[
C('REGEXP_REPLACE(\'A1B22\',\'[0-9]+\',\'#\')는?','A#B#|A#B##|#|A1B22','기본으로 모든 일치 묶음을 대체하여1과22가 각각#이 된다.','+로 묶은22를 두 번 따로 대체하지 않는다.',source=BASE+'REGEXP_REPLACE.html'),
C('REGEXP_SUBSTR(\'ABC\',\'[0-9]+\')는?','NULL|0|빈 결과 집합|ABC','일치하는 숫자 부분이 없으므로 스칼라 함수는NULL을 반환한다.','INSTR의 실패0과 SUBSTR의 실패NULL을 구별한다.'),
C('REGEXP_SUBSTR(\'2026-10\',\'([0-9]{4})-([0-9]{2})\',1,1,NULL,2)는?','10|2026|2026-10|NULL','subexpr=2는 두 번째 괄호 그룹인 월 두 자리를 반환한다.','전체 일치와 첫 그룹을 구별한다.')])

review=[]
def R(l,n,stem,opts,why,trap,sql='',tab=None,source=None):
    kind = 'concept' if n==1 else 'apply' if n==2 else 'discriminate'
    kind = {(1,2):'discriminate',(2,3):'discriminate',(6,3):'concept',(9,3):'apply',(14,3):'apply',(15,3):'concept',(16,3):'concept',(18,3):'concept'}.get((l,n),kind)
    review.append(question(f'unit-2-2-review-{l:02}-{n:02}',f'2-2-{l:02}',kind,
        'basic' if n==1 else 'intermediate',stem,opts.split('|'),0,why+' 오답 점검: '+trap,
        sql=sql,tables=tab or [],steps=[why,trap],pitfall=trap,source=source or BASE+sources[l]))
R(1,1,'FROM절에 괄호로 감싼 SELECT를 배치해 임시 조회 입력으로 쓰는 표현의 이름은?','인라인 뷰|일반 인덱스|시스템 권한|저장점','FROM절 서브쿼리는 인라인 뷰로 쓰인다.','데이터 정의 객체나 트랜잭션 명령과 구별한다.')
R(1,2,'안쪽 SELECT가 바깥 조회의 E.dept를 참조한다. 이 사실로 확정할 수 있는 것은?','논리적으로 상관된 서브쿼리다|반드시 매번 전체 스캔한다|반드시 한 번만 실행된다|반드시 오류다','상관 여부는 외부 열 참조로 결정한다.','실제 물리 실행 횟수와 성능은 실행 계획을 확인해야 한다.')
R(1,3,'어떤 서브쿼리가 이번 데이터에서 한 행을 반환했다. 앞으로도 항상 단일행이라고 보장하려면?','제약·조건·집계 구조 등 최대 행 수를 보장하는 근거를 확인한다|현재 한 행이니 영구 보장된다|별칭을 붙이면 한 행이 된다|정렬하면 한 행이 된다','현재 표본의 반환 수와 쿼리 구조의 반환 수 보장은 다르다.','ORDER BY는 행 수를 제한하지 않는다.')
R(2,1,'스칼라 서브쿼리에 허용되는 반환 열 수는?','한 열|임의의 모든 열|최소 두 열|반드시 열이 없어야 함','스칼라는 한 값 위치이므로 한 열을 반환해야 한다.','행 수 제한뿐 아니라 열 수도 확인한다.')
R(2,2,'비어 있는 T에서 SELECT SUM(v) FROM T는 GROUP BY가 없을 때?','NULL값 한 행|0행|0값 한 행|오류','SUM은 입력이 없으면NULL이며 일반 전체 집계 결과 한 행은 존재한다.','COUNT의0과 SUM의NULL을 구별한다.')
R(2,3,'단일행 비교의 안쪽 조회에 GROUP BY를 추가하면 무엇을 다시 확인해야 하는가?','그룹 수가 둘 이상이 되어 스칼라 조건을 위반하는지|SELECT 별칭이 짧은지|ORDER BY가 반드시 있는지|테이블 이름이 같은지','그룹마다 한 행이 생기므로 집계 함수가 있어도 여러 행이 될 수 있다.','전체 집계와 그룹별 집계의 반환 크기를 구별한다.')
R(3,1,'x > ANY(S)가 TRUE이기 위한 조건은?','S에 x보다 작은 값을 가진 비교 TRUE 항이 적어도 하나 있다|S의 모든 값보다 x가 커야 한다|S가 비어 있어야 한다|S에 NULL만 있어야 한다','ANY는 여러 비교의 OR 의미다.','ALL의 모든 항 만족과 구별한다.')
R(3,2,'7 IN (7,NULL)의 진리값은?','TRUE|UNKNOWN|FALSE|오류','7=7이TRUE이므로 OR의 다른UNKNOWN이 있어도TRUE다.','NULL이 있으면 모든 IN이UNKNOWN이라는 단순화는 틀리다.')
R(3,3,'x NOT IN(S)를 NOT EXISTS로 바꿀 때 특히 확인할 조건은?','x와 S의 NULL 가능성 및 비교 의미|원본 테이블 이름 길이|SUBQUERY의 들여쓰기|WHERE의 대문자 여부','NULL은 NOT IN의 UNKNOWN을 만들 수 있지만 상관 NOT EXISTS는 일치 행 유무를 검사하므로 결과가 달라질 수 있다.','변환 전 NULL 조건을 점검한다.')
R(4,1,'(a,b) IN (SELECT x,y FROM S)는 어떤 단위로 일치 여부를 보는가?','같은 반환 행의 x,y 쌍|x와 y의 임의 조합|첫 열만|마지막 열만','다중컬럼 비교는 대응하는 값을 행 단위로 묶는다.','각 열 목록을 독립적으로 조합하지 않는다.')
R(4,2,'T={(1,P),(2,Q)}, S={(2,Q),(2,Q)}일 때 쌍 IN을 만족하는 T행 수는?','1|2|3|4','T의 (2,Q) 한 행만 조건을 만족하며 S의 중복은 멤버십 결과를 늘리지 않는다.','JOIN의 일치 수 곱셈과 구별한다.')
R(4,3,'다중컬럼 서브쿼리의 열 순서를 바꾸어도 결과가 항상 같은가?','아니다. 위치별 비교이므로 의미가 달라진다|항상 같다. 열 이름으로 자동 매칭한다|자료형만 같으면 언제나 같다|열 순서는 정렬 때만 의미가 있다','(a,b)는 안쪽 첫째,둘째 식에 각각 대응한다.','이름 기반 자동 연결로 생각하지 않는다.')
R(5,1,'EXISTS가 검사하는 대상은?','서브쿼리 결과 행의 존재|SELECT 목록 숫자의 합|첫 값이1인지|반환 열 개수가2인지','행이 하나라도 존재하면TRUE다.','값이NULL인 한 행도 존재하는 행이다.')
R(5,2,'바깥 행이4개이고 각 행의 상관 스칼라 서브쿼리가 정확히1행을 반환한다. 스칼라 값을 SELECT 목록에 붙인 결과 행 수는?','4|1|8|16','선택 목록의 스칼라 값은 바깥 각 행에 하나씩 붙으므로4행이다.','상관 조회를 카티션 곱으로 계산하지 않는다.')
R(5,3,'분석 함수로 만든 별칭을 필터할 때 인라인 뷰가 유용한 이유는?','계산된 값을 다음 쿼리 블록의 입력 열로 제공하기 때문|모든 성능 문제가 자동 해결되기 때문|원본 행을 영구 삭제하기 때문|NULL이 모두0이 되기 때문','안쪽 계산 결과를 바깥 WHERE가 참조하도록 평가 단계를 분리한다.','논리 구조 개선을 검증 없는 성능 보장으로 말하지 않는다.')
R(6,1,'중복을 보존하여 두 조회 결과를 붙이는 연산은?','UNION ALL|UNION|INTERSECT|MINUS','ALL은 양쪽 입력의 중복 행을 유지한다.','UNION의 중복 제거와 구별한다.')
R(6,2,'A={2,2,3}, B={3}일 때 A MINUS B의 결과는?','2 한 행|2 두 행|3 한 행|공집합','차집합은 B의3을 제외하고 남은2의 중복도 제거한다.','Oracle19c MINUS를 중복 보존 차감으로 계산하지 않는다.')
R(6,3,'집합 연산의 중복 행 판정 범위는?','SELECT 목록의 모든 대응 열 값|첫 열만|기본키라고 추측한 열만|별칭 글자만','전체 결과 튜플이 같아야 중복으로 취급한다.','일부 열만 같다고 다른 열이 다른 행을 지우지 않는다.')
R(7,1,'ROLLUP(x,y,z)의 그룹 집합 수는?','4|8|3|6','(x,y,z),(x,y),(x),()의 접두 그룹4개다.','CUBE의2^3=8과 구별한다.')
R(7,2,'ROLLUP(region,product)는 product만의 전체 지역 소계를 생성하는가?','아니다. region 소계와 전체합계를 만든다|그렇다. 모든 독립 소계를 만든다|product 소계만 만든다|어떤 소계도 없다','뒤쪽 키부터 제거하는 ROLLUP에는 (product) 단독 그룹이 없다.','독립 조합이 필요하면 CUBE나 명시적 GROUPING SETS를 검토한다.')
R(7,3,'GROUP BY region,ROLLUP(product)에서 region별 전체가 아닌 전사 총합 행을 기대해도 되는가?','안 된다. region은 고정 그룹 키로 남는다|언제나 총합을 추가한다|빈 입력일 때만 모든 총합을 추가한다|정렬하면 총합이 생긴다','ROLLUP 밖 키는 제거되지 않아() 그룹이 생성되지 않는다.','집계 수준을 명시한 구문을 읽어야 한다.')
R(8,1,'GROUPING SETS를 사용하는 목적은?','원하는 그룹 집합들을 명시해 한 조회에서 계산한다|모든 NULL을 삭제한다|모든 입력을 정렬만 한다|기본키를 생성한다','상세·소계·전체합계 중 필요한 조합을 명시한다.','열 변환이나 무결성 정의 명령과 다르다.')
R(8,2,'GROUPING SETS((dept),())에 상세(employee,dept)행도 자동 포함되는가?','포함되지 않는다|항상 포함된다|dept가NULL이면 모두 포함된다|별칭이 있으면 포함된다','명시한dept집계와 전체합계만 생성한다.','누락된 집계 수준을 자동 추가하지 않는다.')
R(8,3,'CUBE(x,y)는 ROLLUP(x,y)에 어떤 그룹 집합을 추가한 형태인가?','(y)|(x)|()|(x,y)','ROLLUP은(x,y),(x),()이고CUBE에는(y)가 더 있다.','그룹 집합 차이와 실제 추가 행 수를 구별한다.')
R(9,1,'GROUPING(col)=1의 의미는?','현재 집계 수준에서 col이 제거되어 생성된 NULL이다|원본 col값이 반드시NULL이었다|col자료형이 숫자다|집계값이1이다','GROUPING은 집계로 생긴 키 표시값을 구별한다.','원본 NULL값 검사와 다르다.')
R(9,2,'두 열의 GROUPING_ID(a,b)=0이면?','두 열 모두 현재 그룹 키에 포함된다|두 열 모두 집계에서 제거되었다|a만 제거되었다|b만 제거되었다','플래그00이므로 두 열 모두 GROUPING=0이다.','두 열값 자체가NULL일 가능성과 별개다.')
R(9,3,'GROUPING_ID(a,b)=3인 행은?','a,b 모두 집계에서 제거된 수준|a만 남은 수준|b만 남은 수준|두 열 모두 남은 수준','3은 이진11이므로 두 플래그가 모두1이다.','단순 플래그 합계2와 비트 조합3을 구별한다.')
R(10,1,'PARTITION BY를 분석 함수에서 쓰는 이유는?','분석 계산을 독립적으로 다시 시작할 그룹을 나눈다|원본 테이블을 물리적으로 반드시 분할한다|각 그룹을 무조건 한 행으로 줄인다|최종 출력 정렬을 보장한다','논리적 분석 파티션을 지정한다.','물리 파티셔닝·GROUP BY·최종 ORDER BY와 역할을 구별한다.')
R(10,2,'T에 v=1,4,9가 있고 WHERE v>1 뒤 COUNT(*) OVER()를 붙이면 각 cnt는?','2|3|1|14','WHERE를 통과한4,9의 두 행이 분석 대상이다.','원본전체행수3이나값의합을 세지 않는다.')
R(10,3,'분석 함수의 OVER ORDER BY와 바깥 ORDER BY를 다르게 쓸 수 있는가?','가능하며 계산 순서와 표시 순서를 별도로 정한다|불가능하다. 항상 같아야 한다|둘 다 있으면 무조건 오류다|바깥 ORDER BY가 분석 값을 자동 재계산한다','분석 정렬은 계산 기준이고 바깥 정렬은 최종 출력 기준이다.','두 역할을 하나의 정렬 계약으로 합치지 않는다.')
R(11,1,'동순위 뒤 번호를 건너뛰는 순위 함수는?','RANK|DENSE_RANK|ROW_NUMBER|COUNT','RANK는 앞선 행 수를 반영해 동순위 다음 번호가 뛴다.','DENSE_RANK는 순위에 빈틈을 두지 않는다.')
R(11,2,'점수70,70,60,50의 DENSE_RANK 내림차순 결과는?','1,1,2,3|1,1,3,4|1,2,3,4|4,4,2,1','서로 다른 점수70,60,50을1,2,3으로 번호 매긴다.','동점 행 개수 때문에 다음 순위를 건너뛰지 않는다.')
R(11,3,'동점에서 정확히 어떤 행을1번으로 정할지 보장하는 ROW_NUMBER 설계는?','고유한 보조 정렬 키를 추가한다|ORDER BY를 없앤다|테이블 저장 순서를 믿는다|동점이면 항상NULL을 반환한다고 가정한다','모든 행을 구분하는 정렬 순서를 만들면 번호 배정이 결정적이다.','논리적 정렬이 없는 저장·조회 관찰 순서에 의존하지 않는다.')
R(12,1,'ROWS와 RANGE의 기준을 대응한 것은?','ROWS는 물리 행 위치, RANGE는 정렬값의 논리 범위|ROWS는 날짜만, RANGE는 문자만|둘 다 항상 한 행만|둘 다 항상 전체 테이블','프레임 경계의 단위가 다르므로 동점·값 간격에서 결과가 달라질 수 있다.','동일한 PRECEDING 숫자라도 같은 행 집합이라고 가정하지 않는다.')
R(12,2,'고유 id 1,2,3의 v는 각각 1,4,8이다. SUM(v) OVER(ORDER BY id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)의 id=3 결과는?','12|13|8|5','마지막 창은 직전 4와 현재 8의 두 행이므로 12다.','처음1까지 더하는 누적합과 다르다.')
R(12,3,'SUM(v) OVER(ORDER BY key)에서 창을 생략했을 때 기본 프레임은?','RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW|ROWS BETWEEN CURRENT ROW AND CURRENT ROW|ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING|항상 전체 파티션','기본 논리 누적 창은 현재 정렬 키의 동료 행까지 포함한다.','ROWS 누적 창과 같은 것으로 외우면 동점에서 틀릴 수 있다.')
R(13,1,'이전 행의 값을 가져오는 함수와 다음 행의 값을 가져오는 함수는?','LAG와 LEAD|RANK와 DENSE_RANK|SUM과 AVG|FIRST_VALUE와 COUNT','LAG는 이전, LEAD는 다음 위치 값을 참조한다.','방향을 바꾸지 않는다.',source=BASE+'LAG.html')
R(13,2,'LAG(v,1,99)에서 대상 이전 행은 존재하지만 v가NULL이다. 기본RESPECT NULLS 결과는?','NULL|99|0|현재 행의 v','기본값 99는 대상 행이 범위 밖일 때 사용하고 존재하는 행의 NULL을 자동 대체하지 않는다.','NULL 무시 옵션과 기본값의 역할은 다르다.',source=BASE+'LAG.html')
R(13,3,'LAST_VALUE가 항상 파티션 마지막 값을 반환하지 않는 이유는?','결과가 현재 행의 윈도우 프레임 끝에 따라 달라지기 때문|함수가 임의 값을 반환하기 때문|ORDER BY를 사용할 수 없기 때문|모든 NULL을0으로 바꾸기 때문','현재 행까지의 창이면 그 창의 마지막을 본다. 전체 마지막을 원하면 프레임 끝을 UNBOUNDED FOLLOWING으로 명시한다.','함수명보다 창 범위를 먼저 확인한다.')
R(14,1,'상위 N행의 기준을 명확히 하는 데 필요한 핵심 절은?','ORDER BY|GROUP BY만|COMMIT|GRANT','무엇이 상위인지 정렬 기준으로 정의해야 한다.','행 제한만으로 최고점·최신순을 보장하지 않는다.')
R(14,2,'Oracle19c에서 ORDER BY n OFFSET 1 ROWS FETCH NEXT 2 ROWS ONLY, n=2,4,6,8이면?','4와6|2와4|6과8|4만','정렬 후 첫 행 2를 건너뛰고 다음 두 행 4, 6을 선택한다.','OFFSET을 1부터 시작하는 결과 번호로 해석하지 않는다.')
R(14,3,'FETCH FIRST 1 ROW WITH TIES에서 최고 정렬 키가 같은 행이 3개다. 다른 키는 더 낮다. 몇 행인가?','3|1|2|0','경계인 첫 행과 정렬 키가 같은 모든 동료 행을 포함한다.','WITH TIES를 정확히 1행 제한으로 해석하지 않는다.')
R(15,1,'Oracle 계층 조회에서 루트의 LEVEL은?','1|0|-1|NULL','LEVEL은 시작 행을 1로 하여 연결 단계마다 증가한다.','일부 프로그래밍의 0부터 시작하는 깊이와 다르다.')
R(15,2,'CONNECT BY PRIOR id=parent에서 PRIOR가 참조하는 행은?','직전 상위 단계의 부모 행|항상 현재 자식 행|항상 전체 결과의 마지막 행|임의 첫 행','부모 id와 현재 행 parent를 비교해 아래로 연결한다.','PRIOR 위치를 확인하지 않고 탐색 방향을 암기하지 않는다.')
R(15,3,'START WITH가 여러 행을 만족하면 어떤 구조를 만들 수 있는가?','여러 루트에서 시작하는 계층|항상 오류|첫 루트만 강제로 선택|모든 루트를 한 행으로 합산','각 시작 행이 자기 계층의 루트가 될 수 있다.','계층 조회가 단일 루트만 가능하다고 가정하지 않는다.')
R(16,1,'SYS_CONNECT_BY_PATH의 목적은?','루트부터 현재 노드까지의 경로 문자열을 만든다|최종합계만 계산한다|형제행을 자동 삭제한다|루트를 영구 변경한다','현재 탐색 경로의 값을 구분자로 연결한다.','실제 원본 데이터 구조를 바꾸지 않는다.')
R(16,2,'계층조회 WHERE로 중간 부모 행만 제거하면 그 자손도 반드시 함께 제거되는가?','아니다. 일반 WHERE는 행별 결과 필터다|항상 함께 제거된다|원본 테이블에서 부모도 삭제된다|자손의 LEVEL이 자동1이 된다','CONNECT BY에 의한 계층 구성과 일반 WHERE에 의한 행 선별은 다른 단계다.','가지 탐색 차단을 원하면 연결 조건을 검토한다.')
R(16,3,'ORDER SIBLINGS BY는 무엇을 유지하며 정렬하는가?','계층을 유지하며 같은 부모의 형제 순서를 정한다|모든 행을 평면적으로만 정렬한다|모든 루트를 제거한다|관계없는 집계 그룹만 정렬한다','형제 단위 정렬이므로 계층 표시 구조를 보존한다.','일반 ORDER BY와 역할 차이를 확인한다.')
R(17,1,'PIVOT과 UNPIVOT의 방향을 설명한 것은?','PIVOT은 행의 축값을 열로, UNPIVOT은 열을 행으로 펼친다|둘 다 권한을 부여한다|둘 다 테이블을 삭제한다|UNPIVOT은 모든 집계를 완전히 되돌린다','행·열 형태를 바꾸지만 집계로 잃은 세부 정보 복원은 보장하지 않는다.','역방향 형태 변환과 원본 완전 복원을 구별한다.')
R(17,2,'UNPIVOT에서 NULL인 값도 행으로 남기려면?','INCLUDE NULLS|EXCLUDE NULLS|DISTINCT만|ORDER SIBLINGS BY','기본은 EXCLUDE NULLS이므로 NULL 행 유지 옵션을 명시한다.','원본 열 개수만 세어 결과 행 수를 단정하지 않는다.')
R(17,3,'PIVOT하기 전 필요한 열만 인라인 뷰로 고르는 이유는?','의도하지 않은 나머지 열이 암묵적 그룹 키가 되는 것을 막기 위해|PIVOT은 FROM을 사용할 수 없기 때문|모든 NULL을 삭제하기 위해|집계를 없애기 위해','입력의 비피벗·비집계 열이 그룹 수준을 정하므로 불필요한 고유 id 등을 제외한다.','보기 좋은 열 순서 문제만이 아니다.')
R(18,1,'정규식 ^와 $가 보통 나타내는 경계는?','문자열의 시작과 끝|숫자의 합과 차|대문자와 소문자|첫 그룹과 둘째 그룹','앵커로 전체 문자열 일치 범위를 제한할 수 있다.','여기서는 별도 다중행 옵션이 없는 기본 문자열 기준이다.',source=BASE+'Pattern-matching-Conditions.html')
R(18,2,'REGEXP_SUBSTR(\'X7Y88Z\',\'[0-9]+\',1,2)의 결과는?','88|7|2|NULL','첫 숫자 묶음 7 다음 두 번째 숫자 묶음 88을 반환한다.','일치 횟수와 반환 문자열을 구별한다.')
R(18,3,'REGEXP_INSTR가 일치하는 부분을 찾지 못했을 때 반환값은?','0|NULL|원문 전체|항상 오류','위치를 반환하는 REGEXP_INSTR는 미일치 시 0이다.','부분 문자열 함수 REGEXP_SUBSTR의 미일치 NULL과 다르다.',source=BASE+'REGEXP_INSTR.html')

# Independent reviewer requested fully self-contained conditions.
clarified_stems = {
'unit-2-2-mock-1-29':'T(id,score)={(1,90),(2,90),(3,80)}에 ROW_NUMBER() OVER(ORDER BY score DESC,id ASC)를 쓰면 id2의 번호는?',
'unit-2-2-mock-1-33':'T(k,v)={(1,10),(3,20),(4,30)}이다. SUM(v) OVER(ORDER BY k RANGE BETWEEN 1 PRECEDING AND CURRENT ROW)에서 k=4의 결과는?',
'unit-2-2-mock-1-37':'Oracle19c에서 id는 유일하다. 제시된 SELECT에 정렬·행 제한을 추가하여 점수 내림차순 상위 2행을 안정적으로 고르려 한다. 적절한 방법은?',
'unit-2-2-mock-2-31':'T(id,v)={(1,2),(2,5),(3,7)}이다. SUM(v) OVER(ORDER BY id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)에서 id=3의 결과는?',
'unit-2-2-mock-2-33':'T(k,v)={(1,10),(3,20),(4,30)}이다. SUM(v) OVER(ORDER BY k RANGE BETWEEN 1 PRECEDING AND CURRENT ROW)에서 k=3의 결과는?',
'unit-2-2-mock-2-34':'T(id,v)={(1,10),(2,20),(3,30)}이다. LEAD(v,1,-1) OVER(ORDER BY id)의 결과를 id 오름차순으로 나열하면?',
'unit-2-2-mock-2-35':'T(id,v)={(1,10),(2,20),(3,30)}이다. LAST_VALUE(v) OVER(ORDER BY id <고를 프레임>)로 모든 행에 마지막 값 30을 붙이려 한다. 알맞은 프레임은?',
'unit-2-2-mock-2-38':'T(id,score)={(1,100),(2,90),(3,90),(4,80)}이며 id는 유일하다. ORDER BY score DESC,id FETCH FIRST 2 ROWS WITH TIES의 결과 행 수는?',
'unit-2-2-mock-2-40':'T(id,parent)={(1,NULL),(2,1),(3,2)}이다. START WITH id=3 CONNECT BY PRIOR parent=id로 탐색하면 방문하는 id는?',
'unit-2-2-mock-2-43':'T(id,parent)={(1,NULL),(2,1),(3,2)}이다. START WITH id=1 CONNECT BY PRIOR id=parent AND id<>2로 탐색하면 id3은?',
'unit-2-2-mock-2-45':'T(dept,q,v)={(A,Q1,2),(A,Q1,3)}이다. SUM(v)를 집계하고 q의 Q1을 결과 열로 만드는 PIVOT에서 A의 Q1 값은?',
'unit-2-2-mock-2-46':'T(id,q1,q2)={(1,10,NULL)}이다. q1,q2를 값 열 v와 축 열 q로 UNPIVOT INCLUDE NULLS하면 결과 행 수는?',
'unit-2-2-mock-3-31':'T(id,v)={(1,2),(2,NULL),(3,6)}이다. AVG(v) OVER(ORDER BY id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)에서 id=2의 결과는?',
'unit-2-2-mock-3-32':'T(k,v)={(1,3),(1,4),(2,5)}이다. SUM(v) OVER(ORDER BY k RANGE BETWEEN CURRENT ROW AND CURRENT ROW)의 결과는?',
'unit-2-2-mock-3-33':'T(id,v)={(1,2),(2,5),(3,7)}이다. SUM(v) OVER(ORDER BY id ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING)의 결과를 id 오름차순으로 나열하면?',
'unit-2-2-mock-3-34':'T(id,v)={(1,10),(2,NULL),(3,30)}이다. LAG(v,1,0) OVER(ORDER BY id)에서 id=3의 결과는?',
'unit-2-2-mock-3-35':'T(id,v)={(1,10),(2,NULL),(3,30)}이다. LAST_VALUE(v IGNORE NULLS) OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)에서 id=2의 결과는?',
'unit-2-2-mock-3-36':'T의 v는 10,20,20,30이다. CUME_DIST() OVER(ORDER BY v ASC)를 계산하면 v=20인 두 행의 값은?',
'unit-2-2-review-14-03':'점수에 NULL은 없다. ORDER BY score DESC FETCH FIRST 1 ROW WITH TIES에서 최고점이 같은 행은 3개이고 나머지는 모두 점수가 낮다. 결과는 몇 행인가?'
}
for q in review + [q for form in groups for q in form]:
    if q['id'] in clarified_stems:
        q['stem'] = clarified_stems[q['id']]
    if q['id']=='unit-2-2-mock-1-37':
        q['sql']='SELECT id,score FROM T'
    replacements = {}
    if q['id']=='unit-2-2-mock-2-46':
        replacements={'10행과NULL행':'값 10인 행과 값 NULL인 행'}
    if q['id']=='unit-2-2-mock-3-39':
        replacements={'100과90두행을 모두 얻는다.':'100점 한 행과 90점 두 행, 총 3행을 얻는다.'}
    for a,b in replacements.items():
        q['explanation']=q['explanation'].replace(a,b)
        q['steps']=[s.replace(a,b) for s in q['steps']]

save('2-2','SQL 활용',review,groups)


