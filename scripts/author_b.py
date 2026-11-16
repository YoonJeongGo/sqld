"""Serialize independently authored Korean Oracle 19c lessons and questions.

No external exam questions, random word/number variations, or engine-test claims.
The author reviewed explanations against official references. This script is not
an independent correctness oracle; document_review is deliberately preserved.
"""
import json
import re
from functools import lru_cache
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
pack = {'objectives': [], 'notes': [], 'questions': []}
counts = Counter()
TOPICS = {**dict.fromkeys(range(9,12),'C'), **dict.fromkeys(range(12,21),'D'), **dict.fromkeys(range(21,25),'E')}
SOURCES = {
9:['oracle19-select'],10:['oracle19-joins'],11:['oracle19-joins'],12:['oracle19-subqueries','oracle19-in','oracle19-exists','oracle19-comparison'],
13:['oracle19-setops'],14:['oracle19-select','oracle19-grouping'],15:['oracle19-analytic','oracle19-lag','oracle19-lead','oracle19-ntile'],16:['oracle19-analytic','oracle19-last-value'],
17:['oracle19-select','oracle19-rownum'],18:['oracle19-hierarchy'],19:['oracle19-select'],20:['oracle19-regexp','oracle19-regexp-substr'],
21:['oracle19-insert','oracle19-update','oracle19-delete','oracle19-merge'],
22:['oracle19-commit','oracle19-rollback','oracle19-savepoint'],23:['oracle19-create-table','oracle19-alter-table','oracle19-truncate','oracle19-drop-table'],24:['oracle19-grant','oracle19-revoke']}
TITLES={9:'ORDER BY와 결과 순서',10:'조인과 행의 결합',11:'표준 조인과 외부 조인',12:'서브쿼리',13:'집합 연산자',14:'ROLLUP·CUBE·GROUPING',15:'순위와 윈도우 함수',16:'윈도우 프레임',17:'Top N 쿼리',18:'계층형 질의와 셀프 조인',19:'PIVOT과 UNPIVOT',20:'정규 표현식',21:'DML과 데이터 변경',22:'TCL과 트랜잭션',23:'DDL과 무결성 제약',24:'DCL과 권한'}
PREREQS={9:['S02'],10:['S02','S06'],11:['S10'],12:['S02','S06','S07'],13:['S02'],14:['S07'],15:['S07','S09'],16:['S15'],17:['S09','S15'],18:['S10'],19:['S07'],20:['S04'],21:['S06'],22:['S21'],23:['S01'],24:['S23']}

def note(n,definition,easy,conditions,example,compare,exception,misconception,recall,synonyms):
    oid=f'S{n:02}'
    pack['objectives'].append(dict(id=oid,subjectId='sql',topicId=TOPICS[n],title=TITLES[n],prerequisites=PREREQS[n],synonyms=synonyms,scopeStatus='provisional'))
    rows=[('goal','explain','이번에 이해할 것',f'{TITLES[n]}의 규칙을 설명하고 작은 입력에서 결과·오류를 판단한다.'),('definition','definition','한 문장 정의',definition),('easy','explain','쉬운 설명',easy),('conditions','remember','정확한 조건',conditions),('example','example','작은 사례',example),('compare','compare','혼동 개념 비교',compare),('exceptions','remember','조건과 예외',exception),('misconception','misconception','오해와 반례',misconception),('recall','recall','스스로 답하기',recall),('navigation','explain','학습 연결',f"선수 개념: {', '.join(PREREQS[n])}. 이 노트의 확인 퀴즈를 푼 뒤 적용 문제에서 조건을 직접 추적한다. 시험 범위는 공식 상세 기준 대조 미완료로 provisional이며 문법 기준은 Oracle Database 19c다. 사람이 검수하거나 Oracle에서 실행한 콘텐츠는 아니다.")]
    pack['notes'].append(dict(id='note-'+oid,version=1,objectiveId=oid,title=TITLES[n],summary=definition,sourceIds=SOURCES[n],verification='document_review',blocks=[dict(id=f'{oid}-{a}',kind=b,title=c,text=d) for a,b,c,d in rows],recallQuestionIds=[]))

def q(n,kind,slug,stem,answers,summary,steps,memory,conditions=None,tables=None,sql=None,fixture=None,mock=None,objectives=None):
    """answers: four authored (answer, rationale) pairs; first is correct before rotation."""
    oid=f'S{n:02}'; counts[(oid,kind)]+=1
    ident=(f'{mock}-{oid}-{slug}' if mock else f'{oid}-'+('R' if kind=='recall' else 'A')+f'{counts[(oid,kind)]:02}-{slug}')
    # Deterministic rotation balances positions but keeps fixed choice IDs.
    offset=(len(pack['questions'])+n)%4
    choices=[dict(id=chr(97+i),text=t,reason=r) for i,(t,r) in enumerate(answers)]
    correct=choices[0]['id']
    choices=choices[offset:]+choices[:offset]
    item=dict(id=ident,version=1,subjectId='sql',topicId=TOPICS[n],objectiveIds=objectives or [oid],familyId=f'authored-{oid}-{slug}',kind=kind,title=stem.split('\n')[0][:70],stem=stem,choices=choices,correctChoiceIds=[correct],explanation=dict(summary=summary,prerequisites=PREREQS[n],conditions=conditions or ['Oracle Database 19c의 명시된 규칙으로 판단한다.','지문에 없는 제약·정렬·동시 변경은 가정하지 않는다.'],steps=[dict(title=f'{i+1}단계',text=s) if isinstance(s,str) else s for i,s in enumerate(steps)],memory=memory,relatedNoteId='note-'+oid),sourceIds=SOURCES[n],sourceType='original_mock' if mock else 'original_practice',verification='document_review',status='published',dialect='Oracle',dialectVersion='19c',difficulty='basic' if kind=='recall' else 'intermediate',difficultyReason='한 규칙의 조건을 구분한다.' if kind=='recall' else '입력과 연산 순서를 추적하여 결과 또는 오류를 판단한다.',importanceReason='학습목표의 핵심 규칙을 확인한다. 실제 시험 출제 빈도를 의미하지 않는다.',tables=tables or [],validationEvidence=['독자 창작; 저술자가 명시 조건·정답·보기별 이유를 문서 규칙과 대조함.','독립 풀이 및 사람 전문가 검수 미실시. Oracle 19c 실행 미실시.'])
    if sql: item['sql']=sql
    if fixture: item['fixture']=fixture
    if mock: item['mockSetId']=mock
    pack['questions'].append(item)
    if kind=='recall':
        next(z for z in pack['notes'] if z['objectiveId']==oid)['recallQuestionIds'].append(ident)

def r(n,slug,stem,correct,wrongs,why,step,memory):
    q(n,'recall',slug,stem,[(correct,why)]+wrongs,why,[step,why],memory)

def table(title,columns,rows): return dict(title=title,columns=columns,rows=[[None if c is None else str(c) for c in row] for row in rows])

def sqlq(n,slug,stem,query,inputs,output,wrong,steps,memory,mock=None,ordered=False,constraints=None):
    """inputs is [(name,[(col,type)],rows)], output is an explicit final Table."""
    schema=[]; setup=[]; tables=[]
    for name,cols,rows in inputs:
        schema.append('CREATE TABLE '+name+' ('+', '.join(a+' '+b for a,b in cols)+');')
        for row in rows:
            vals=['NULL' if v is None else str(v) if isinstance(v,(int,float)) else "'"+str(v).replace("'","''")+"'" for v in row]
            setup.append('INSERT INTO '+name+' VALUES ('+', '.join(vals)+');')
        tables.append(table(name,[c[0] for c in cols],rows))
    fixture=dict(schemaSql='\n'.join(schema),setupSql='\n'.join(setup),query=query,expectedRows=output['rows'],ordered=ordered,constraints=constraints or ['記載した行が入力の全件。列型はschemaSqlに記載。明示しない制約はない。'.replace('記載した行が入力の全件。列型はschemaSqlに記載。明示しない制約はない。','표에 제시한 행이 전체 입력이다. 열 자료형은 schemaSql에 명시하며 추가 제약은 없다.')],sessionSettings=['Oracle Database 19c','날짜·문자 정렬에 의존하는 경우 지문에 별도 조건을 명시한다.'],verificationMethod='document_review',evidence='저술자가 공식 문서의 연산 규칙으로 입력을 단계 추적한 예상 결과. 실제 Oracle 실행 결과가 아님.')
    summary='최종 결과는 '+format_rows(output['rows'])+'이다.'
    q(n,'mock' if mock else 'application',slug,stem,[(format_rows(output['rows']),summary)]+wrong,summary,steps+[dict(title='최종 결과',text='중간 계산을 SELECT 열에 맞춰 투영한다. 결과의 NULL은 값 없음이며 숫자 0과 다르다.',table=output)],memory,conditions=['Oracle Database 19c. 입력 표가 전체 데이터다.','최종 ORDER BY가 있으면 지정 순서를 적용하고, 없으면 행의 나열 순서는 채점 의미에 포함하지 않는다.']+(constraints or []),tables=tables,sql=query,fixture=fixture,mock=mock)

def format_rows(rows):
    return '0행 (빈 결과)' if not rows else ' / '.join('('+', '.join('NULL' if v is None else str(v) for v in row)+')' for row in rows)

def save():
    polish_pack()
    pack['provenance']=dict(authoring='original Korean learning content',review='author document review only',engineExecution=False,expertReview=False,variantGeneration=False,quantityPolicy='숫자나 이름만 교체한 파생 문제를 생성하지 않는다.')
    (ROOT/'content'/'part-b.json').write_text(json.dumps(pack,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'notes':len(pack['notes']),'questions':len(pack['questions']),'kinds':dict(Counter(x['kind'] for x in pack['questions']))},ensure_ascii=False))

# Author's explicit editorial corrections; this changes prose spacing only.
# SQL, schemas, input/expected cells, IDs and answer mappings are never touched.
EDITORIAL = '''
집계단위가주문인데조인결과단위는상세행이어서주문금액이중복집계된다|집계 단위가 주문인데 조인 결과 단위는 상세 행이어서 주문 금액이 중복 집계된다
객체권한의종속재부여경로는상위권한회수의영향을받는다|객체 권한의 종속 재부여 경로는 상위 권한 회수의 영향을 받는다
객체권한은열단위로제한할수있고그범위를넘는수정은허용되지않는다|객체 권한은 열 단위로 제한할 수 있고 그 범위를 넘는 수정은 허용되지 않는다
객체생성능력과기존타인표의데이터접근권한은별개다|객체 생성 능력과 기존 타인 표의 데이터 접근 권한은 별개다
엄격부등식이자기쌍과대칭역순을함께제외한다|엄격 부등식이 자기 쌍과 대칭 역순을 함께 제외한다
모든행이조건을만족함은그조건을위반한행이없음으로표현할수있다|모든 행이 조건을 만족함은 그 조건을 위반한 행이 없음으로 표현할 수 있다
이미생성된번호열을다른블록의일반값으로필터할수있다|이미 생성된 번호 열을 다른 블록의 일반 값으로 필터할 수 있다
부모는바로윗관계행이며루트는경로의출발행이다|부모는 바로 윗 관계 행이며 루트는 경로의 출발 행이다
월별요약으로건수정보를버린뒤같은가중치로평균하면원본행가중치와달라진다|월별 요약으로 건수 정보를 버린 뒤 같은 가중치로 평균하면 원본 행 가중치와 달라진다
여러자식의동일부모참조는일대다관계의일반형태다|여러 자식의 동일 부모 참조는 일대다 관계의 일반 형태다
집합연산은대응열의자료형그룹을확인하며명시변환으로의도를표현해야한다|집합 연산은 대응 열의 자료형 그룹을 확인하며 명시 변환으로 의도를 표현해야 한다
분석계산결과열을다음쿼리블록의입력으로만들어필터할수있다|분석 계산 결과 열을 다음 쿼리 블록의 입력으로 만들어 필터할 수 있다
계층탐색경로에이미존재하는행으로돌아가는순환은별도처리가필요하다|계층 탐색 경로에 이미 존재하는 행으로 돌아가는 순환은 별도 처리가 필요하다
한출력값열에들어갈여러입력열은호환자료형그룹이어야한다|한 출력 값 열에 들어갈 여러 입력 열은 호환 자료형 그룹이어야 한다
역할은허용작업들의묶음이며그실제내용과활성조건을확인해야한다|역할은 허용 작업들의 묶음이며 그 실제 내용과 활성 조건을 확인해야 한다
범위조건을직접만족하는구간이없으며중간공백을자동보정하지않는다|범위 조건을 직접 만족하는 구간이 없으며 중간 공백을 자동 보정하지 않는다
서브쿼리의최솟값한개와그값을가진바깥행여러개를구별한다|서브쿼리의 최솟값 한 개와 그 값을 가진 바깥 행 여러 개를 구별한다
공통행이라는조건은양쪽입력의위치를바꾸어도동일하다|공통 행이라는 조건은 양쪽 입력의 위치를 바꾸어도 동일하다
여러집계수준은같은원본행을반복포함하므로모두더하면중복계산된다|여러 집계 수준은 같은 원본 행을 반복 포함하므로 모두 더하면 중복 계산된다
버킷수가행수보다크면실제행에는앞번호버킷이하나씩배정된다|버킷 수가 행 수보다 크면 실제 행에는 앞 번호 버킷이 하나씩 배정된다
건너뛸개수가결과행수보다커남은행이없다|건너뛸 개수가 결과 행 수보다 커 남은 행이 없다
데이터이동문장은대상변경권한과소스읽기권한을각각필요로한다|데이터 이동 문장은 대상 변경 권한과 소스 읽기 권한을 각각 필요로 한다
집계로고객집합을선택한뒤그고객에속한원본행전체를삭제한다|집계로 고객 집합을 선택한 뒤 그 고객에 속한 원본 행 전체를 삭제한다
기본참조규칙에서참조받는부모를제거하면자식의유효한참조가깨진다|기본 참조 규칙에서 참조받는 부모를 제거하면 자식의 유효한 참조가 깨진다
객체별부여권한의범위를독립적으로추적한다|객체별 부여 권한의 범위를 독립적으로 추적한다
조인행수와최종투영의중복제거후행수는다르다|조인 행 수와 최종 투영의 중복 제거 후 행 수는 다르다
대체값이실제도메인과충돌하면서로다른의미를같은키로만든다|대체값이 실제 도메인과 충돌하면 서로 다른 의미를 같은 키로 만든다
전체충족조건은위반요구사항의부재로평가되며빈요구집합에는반례가없다|전체 충족 조건은 위반 요구사항의 부재로 평가되며 빈 요구 집합에는 반례가 없다
공통값집합과매칭행쌍은중복을다르게다룬다|공통 값 집합과 매칭 행 쌍은 중복을 다르게 다룬다
정렬순서없는파티션집계는파티션전체를집계한다|정렬 순서 없는 파티션 집계는 파티션 전체를 집계한다
계층깊이는경로에서몇번연결했는지로정해진다|계층 깊이는 경로에서 몇 번 연결했는지로 정해진다
괄호가첫대문자를캡처하고역참조가같은문자의반복을요구한다|괄호가 첫 대문자를 캡처하고 역참조가 같은 문자의 반복을 요구한다
제약을강화하려면기존데이터가새규칙을만족하는지확인해야한다|제약을 강화하려면 기존 데이터가 새 규칙을 만족하는지 확인해야 한다
권한종류와옵션별공식회수규칙을따로적용해야한다|권한 종류와 옵션별 공식 회수 규칙을 따로 적용해야 한다
문장원자성은실패한문장의변경을되돌리며이전성공문장을자동전체취소한다고볼수없다|문장 원자성은 실패한 문장의 변경을 되돌리며 이전 성공 문장을 자동 전체 취소한다고 볼 수 없다
물리행위치를사용하므로동점순서를정하지않으면행별창이다르게될수있다|물리 행 위치를 사용하므로 동점 순서를 정하지 않으면 행별 창이 다르게 될 수 있다
모든현재행의창이파티션첫행부터마지막행까지열린다|모든 현재 행의 창이 파티션 첫 행부터 마지막 행까지 열린다
윈도우함수는원래네행을유지해각파티션합계를반복붙인다|윈도우 함수는 원래 네 행을 유지해 각 파티션 합계를 반복 붙인다
각대입의오른쪽열식은그행의기존값을참조한다|각 대입의 오른쪽 열 식은 그 행의 기존 값을 참조한다
복합키구성열을빠짐없이비교한다|복합 키 구성 열을 빠짐없이 비교한다
'''

# Independently reviewed phrase boundaries appearing in the original Korean
# authoring tuples. Long phrases are applied first to preserve their meaning.
PHRASES = '''
원본행식별자|원본 행 식별자
원본전체행|원본 전체 행
전체집계결과|전체 집계 결과
원본NULL그룹|원본 NULL 그룹
객체권한재부여능력|객체 권한 재부여 능력
객체권한재부여|객체 권한 재부여
종속재부여경로|종속 재부여 경로
실제매칭행|실제 매칭 행
동일이름savepoint|동일 이름 savepoint
기존COMMIT|기존 COMMIT
이전COMMIT|이전 COMMIT
부분롤백|부분 롤백
전체롤백|전체 롤백
일반ROLLBACK|일반 ROLLBACK
암묵적COMMIT|암묵적 COMMIT
암묵COMMIT|암묵 COMMIT
추가동점행|추가 동점 행
대상행선택|대상 행 선택
최종표시순서|최종 표시 순서
표시순서|표시 순서
계산순서|계산 순서
부서파티션|부서 파티션
파티션경계|파티션 경계
파티션전체|파티션 전체
전체파티션|전체 파티션
파티션첫행|파티션 첫 행
파티션합계|파티션 합계
파티션분리|파티션 분리
파티션초기화|파티션 초기화
파티션안|파티션 안
파티션밖|파티션 밖
원본행전체|원본 행 전체
현재정렬값|현재 정렬값
같은정렬값|같은 정렬값
서로다른값|서로 다른 값
서로다른행|서로 다른 행
서로다른|서로 다른
전체정렬키|전체 정렬 키
복합정렬키|복합 정렬 키
보조정렬키|보조 정렬 키
단일정렬키|단일 정렬 키
정렬키전체|정렬 키 전체
정렬키|정렬 키
정렬된행|정렬된 행
행별누적값|행별 누적값
전체집계|전체 집계
집계결과행수|집계 결과 행 수
집계결과행|집계 결과 행
집계결과|집계 결과
집계수준|집계 수준
집계단위|집계 단위
집계대상|집계 대상
집계함수|집계 함수
분석함수|분석 함수
윈도우함수|윈도우 함수
분석계산|분석 계산
분석입력|분석 입력
그룹집계|그룹 집계
그룹수준|그룹 수준
그룹결과|그룹 결과
그룹빈도|그룹 빈도
암묵그룹|암묵 그룹
그룹키|그룹 키
전체합계|전체 합계
부서합계|부서 합계
원본평균|원본 평균
전체평균|전체 평균
월별평균|월별 평균
집계값|집계값
SELECT결과|SELECT 결과
SELECT열|SELECT 열
ON조건|ON 조건
WHERE조건|WHERE 조건
WHERE필터|WHERE 필터
GROUPING표시|GROUPING 표시
COUNT집계|COUNT 집계
COUNT결과|COUNT 결과
NULL값|NULL 값
NULL행|NULL 행
NULL두행|NULL 두 행
NULL한행|NULL 한 행
NULL비교|NULL 비교
NULL처리|NULL 처리
NULL치환|NULL 치환
NULL대체|NULL 대체
NULL확장|NULL 확장
NULL조건|NULL 조건
NULL판정|NULL 판정
NULL입력|NULL 입력
NULL원본|NULL 원본
NULL허용|NULL 허용
NULL여부|NULL 여부
NULL금지|NULL 금지
NULL포함|NULL 포함
NULL제외|NULL 제외
NULL배치|NULL 배치
비NULL참조값|비NULL 참조값
비NULL값|비NULL 값
비NULL행|비NULL 행
원본데이터|원본 데이터
기존데이터|기존 데이터
입력데이터|입력 데이터
원본입력|원본 입력
입력전체|입력 전체
전체입력|전체 입력
전체행수|전체 행 수
입력행수|입력 행 수
결과행수|결과 행 수
출력행수|출력 행 수
매칭행수|매칭 행 수
선택행수|선택 행 수
매칭행쌍|매칭 행 쌍
매칭행|매칭 행
미매칭원본|미매칭 원본
미매칭행|미매칭 행
미매칭보존|미매칭 보존
매칭개수|매칭 개수
매칭조건|매칭 조건
매칭키|매칭 키
매칭다중성|매칭 다중성
조인결과|조인 결과
내부조인|내부 조인
외부조인|외부 조인
셀프조인|셀프 조인
조인조건|조인 조건
조인중복|조인 중복
집합연산|집합 연산
자기차집합|자기 차집합
왼쪽차집합|왼쪽 차집합
빈집합|빈 집합
공통행|공통 행
공통값|공통 값
대응열|대응 열
열개수|열 개수
열수|열 수
열순서|열 순서
열구조|열 구조
열정의|열 정의
열목록|열 목록
자료형그룹|자료형 그룹
자료형호환|자료형 호환
명시변환|명시 변환
암묵변환|암묵 변환
원본행|원본 행
입력행|입력 행
결과행|결과 행
출력행|출력 행
현재행|현재 행
앞행|앞 행
이전행|이전 행
다음행|다음 행
마지막행|마지막 행
첫행|첫 행
동료행|동료 행
대상행|대상 행
실제행|실제 행
가상행|가상 행
새행|새 행
행부재|행 부재
행존재|행 존재
행생성|행 생성
행삭제|행 삭제
행제거|행 제거
행필터|행 필터
행번호|행 번호
행위치|행 위치
행개수|행 개수
행수|행 수
한행|한 행
두행|두 행
세행|세 행
네행|네 행
여러행|여러 행
각행|각 행
모든행|모든 행
한개|한 개
두개|두 개
세개|세 개
한번|한 번
두번|두 번
세번|세 번
정확히한|정확히 한
각열|각 열
각값|각 값
각부서|각 부서
각단계|각 단계
각수준|각 수준
각파티션|각 파티션
각원본|각 원본
각입력|각 입력
기존값|기존 값
현재값|현재 값
대체값|대체값
치환값|치환값
전체값|전체 값
양끝앵커|양끝 앵커
시작앵커|시작 앵커
끝앵커|끝 앵커
전체일치|전체 일치
부분일치|부분 일치
대소문자옵션|대소문자 옵션
숫자변환|숫자 변환
정규식대안|정규식 대안
문자클래스|문자 클래스
숫자수가|숫자 수가
반복범위|반복 범위
반복단위|반복 단위
문자열전체|문자열 전체
일치문자열|일치 문자열
기본값적용|기본값 적용
기본값조건|기본값 조건
상관조건|상관 조건
비상관조건|비상관 조건
서브쿼리결과|서브쿼리 결과
스칼라값|스칼라 값
스칼라행수|스칼라 행 수
스칼라오류|스칼라 오류
다중행오류|다중행 오류
위반조건|위반 조건
업무규칙|업무 규칙
빈요구집합|빈 요구 집합
반례필수과목|반례 필수과목
필수과목자체|필수과목 자체
이수표가많은행만|이수표가 많은 행만
참거짓소속판정|참거짓 소속 판정
집계모집단|집계 모집단
소속조건|소속 조건
기본키중복|기본키 중복
참조무결성|참조 무결성
무결성제약|무결성 제약
명시제약|명시 제약
즉시검사|즉시 검사
제약위반|제약 위반
제약검사|제약 검사
제약적용|제약 적용
기본제약|기본 제약
복합키|복합 키
단일열|단일 열
객체권한|객체 권한
시스템권한|시스템 권한
직접권한|직접 권한
권한회수|권한 회수
권한부여|권한 부여
권한종류|권한 종류
권한범위|권한 범위
권한경로|권한 경로
재부여능력|재부여 능력
부여경로|부여 경로
활성역할|활성 역할
객체생성|객체 생성
객체정의|객체 정의
객체삭제|객체 삭제
객체제거|객체 제거
소유권이전|소유권 이전
데이터접근|데이터 접근
일반조회|일반 조회
같은세션|같은 세션
다른세션|다른 세션
자기세션|자기 세션
현재세션|현재 세션
미확정변경|미확정 변경
이미확정|이미 확정
자동확정|자동 확정
이전트랜잭션|이전 트랜잭션
현재트랜잭션|현재 트랜잭션
트랜잭션전체|트랜잭션 전체
이전성공문장|이전 성공 문장
실패문장|실패 문장
문장실패|문장 실패
문장원자성|문장 원자성
문장전체|문장 전체
한문장|한 문장
다중열대입|다중 열 대입
대입식|대입식
순차변수대입|순차 변수 대입
자동삭제|자동 삭제
자동생성|자동 생성
자동변환|자동 변환
자동복구|자동 복구
자동회수|자동 회수
자동추가|자동 추가
자동소멸|자동 소멸
자동전체취소|자동 전체 취소
자동동시에회수|자동으로 동시에 회수
실제원본|실제 원본
실제입력|실제 입력
원래데이터|원래 데이터
원래행|원래 행
원래값|원래 값
데이터손실|데이터 손실
행별계산|행별 계산
값종류수|값 종류 수
값종류|값 종류
값개수|값 개수
값비교|값 비교
값범위|값 범위
경계조건|경계 조건
범위조건|범위 조건
범위밖|범위 밖
범위안|범위 안
계층관계|계층 관계
계층질의|계층 질의
계층깊이|계층 깊이
계층결과|계층 결과
계층탐색|계층 탐색
관계조건|관계 조건
직접부모|직접 부모
직속부하|직속 부하
전체자손|전체 자손
여러루트|여러 루트
두루트|두 루트
실제깊이|실제 깊이
상대깊이|상대 깊이
경로전체|경로 전체
출력필터|출력 필터
연결조건|연결 조건
경로조건|경로 조건
순환관계|순환 관계
순환오류|순환 오류
계층구조|계층 구조
동점규칙|동점 규칙
동점집합|동점 집합
동점순서|동점 순서
동점보조|동점 보조
동점행|동점 행
추가동점|추가 동점
분석정렬|분석 정렬
정렬조건|정렬 조건
정렬방향|정렬 방향
정렬환경|정렬 환경
버킷번호|버킷 번호
버킷수|버킷 수
앞번호|앞 번호
단계별|단계별
기존표|기존 표
타인표|타인 표
부모표|부모 표
자식표|자식 표
주문표|주문 표
고객표|고객 표
대상표|대상 표
소스표|소스 표
행쌍|행 쌍
중복제거|중복 제거
중복보존|중복 보존
중복계산|중복 계산
중복집계|중복 집계
중간결과|중간 결과
최종결과|최종 결과
정상키|정상 키
실제도메인|실제 도메인
숫자모양|숫자 모양
같은값|같은 값
같은행|같은 행
같은표|같은 표
같은키|같은 키
같은조건|같은 조건
새규칙|새 규칙
새번호|새 번호
최근위치|최근 위치
최근변경|최근 변경
동일수준|동일 수준
빈결과|빈 결과
빈입력|빈 입력
빈원본|빈 원본
단계필터|단계 필터
조인단계|조인 단계
집계단계|집계 단계
어떤경우|어떤 경우
그이유|그 이유
그범위|그 범위
그값|그 값
그뒤|그 뒤
그앞|그 앞
그조건|그 조건
이조건|이 조건
두조건|두 조건
세조건|세 조건
모든조건|모든 조건
어떤열|어떤 열
그열|그 열
두열|두 열
세열|세 열
두키|두 키
각키|각 키
두입력|두 입력
각각하나|각각 하나
서로독립|서로 독립
다른두|다른 두
값하나|값 하나
참인비교|참인 비교
그대로유지|그대로 유지
항상같다|항상 같다
항상동일|항상 동일
언제나같다|언제나 같다
'''

VERBS = '''
적용하지않았다|적용하지 않았다
사용하지않았다|사용하지 않았다
포함하지않았다|포함하지 않았다
지정하지않았다|지정하지 않았다
정의하지않았다|정의하지 않았다
반환하지않는다|반환하지 않는다
생성하지않는다|생성하지 않는다
허용하지않는다|허용하지 않는다
수행하지않는다|수행하지 않는다
포함하지않는다|포함하지 않는다
요구하지않는다|요구하지 않는다
대신하지않는다|대신하지 않는다
일치하지않는다|일치하지 않는다
같지않다|같지 않다
다르지않다|다르지 않다
되지않는다|되지 않는다
되지않았다|되지 않았다
하지않는다|하지 않는다
하지않았다|하지 않았다
아니라는뜻|아니라는 뜻
아니라는점|아니라는 점
볼수없다|볼 수 없다
볼수있다|볼 수 있다
할수없다|할 수 없다
할수있다|할 수 있다
될수없다|될 수 없다
될수있다|될 수 있다
가질수있다|가질 수 있다
얻을수있다|얻을 수 있다
남을수있다|남을 수 있다
달라질수있다|달라질 수 있다
알수없다|알 수 없다
알수있다|알 수 있다
있어야한다|있어야 한다
이어야한다|이어야 한다
여야한다|여야 한다
해야한다|해야 한다
필요하지않다|필요하지 않다
'''

NOUN_WORDS = '''
원본 입력 출력 결과 행 열 값 표 키 수 개 번 명 점 위 월 년 쌍 단계 집합 조인 집계 함수 조건
명령 문장 쿼리 블록 서브쿼리 스칼라 분석 윈도우 프레임 파티션 순서 정렬 방향 번호 순위 동점
대상 소스 부서 고객 주문 상품 학생 직원 상사 부모 자식 루트 경로 관계 계층 깊이 구간 범위
규칙 의미 요구 업무 상태 상태값 데이터 구조 설계 제약 기본키 외래키 무결성 유일성 참조 자료형
그룹 수준 전체 소계 총계 합계 평균 최댓값 최솟값 최대값 최소값 개수 행수 분모 분자 금액 급여
점수 성적 단위 가중치 정보 손실 구분 차이 비교 판정 처리 존재 부재 누락 중복 반복 발생 보존
제거 삭제 생성 삽입 갱신 변경 대입 변환 치환 투영 선택 필터 검사 적용 실행 계산 조회 확정 취소
롤백 트랜잭션 시점 위치 범위 경계 시작 끝 앞 뒤 안 밖 중간 마지막 현재 이전 다음 최초 최종
이름 별칭 식별자 기본값 대체값 치환값 암묵 문법 오류 실패 성공 권한 객체 시스템 역할 옵션
수신자 부여 회수 재부여 능력 경로 접근 읽기 쓰기 관리 소유권 인증 능력 최소 목적 대상 범위
문자 문자열 숫자 공백 대문자 소문자 대소문자 패턴 앵커 괄호 대괄호 덩어리 종류 부분 전체
버킷 나머지 몫 오프셋 시간 시각 시간대 날짜 비율 반올림 올림 정수 소수 비음수 음수 양수
첫째 둘째 셋째 넷째 예외 반례 모집단 참거짓 원소 원자성 독립 종속 단계 효력 수명 표시 화면
임의 정상 실제 기본 일반 복합 단일 상세 독립 직접 간접 직속 기존 현재 비슷한 다른 동일 같은
원래 필요 가능 불가능 자동 유효 활동 활성 충분 단순 적법 임의 명시 상대 절대 추가 빈
내용 작업 지표 분기 참조열 식 열식 대입식 비교식 우선순위 우선 위치 경로 카디널리티
부분집합 교집합 차집합 합집합 동등성 대칭 역순 자기 인라인뷰 메타정보 메타데이터 원자성
도메인 충돌 겉모습 유료 비유료 미매칭 매칭 안티 원가 가격 할인 가산 지급 보정 사람 건수
상위 하위 최저 최고 중간 지점 영향 행위 능력 허용 금지 생존 필수 선택 연결 확장 탐색 자손
화면 원문 길이 인수 단어 언어 경로 동의어 과정 입력값 결과값 집계값 정렬값 키값 순가격
합산 차단 불일치 일치 유일 객체명 테이블 프로그램 변수 판별 모집단 원본값 요구사항 정책
부족분 변환행 제외목록 첫번째 두번째 세번째 전체값 생존행 공통값 포함키 정렬식 집계식
접두키 역할별 선언 지시 기준 기준값 기본형 일반형태 자기값 조건식 결과표 미래 과거
비교목록 양쪽 왼쪽 오른쪽 반대편 상단 하단 왼쪽값 오른쪽값 위쪽 아래쪽 문항 표현 근거
'''.split()
PARTICLES = ['으로부터','에서부터','에게서','으로는','으로도','에서는','에서도','만으로','만큼','으로','에서','에게','까지','부터','보다','처럼','마다','이라','이며','이면','이고','에는','에도','만을','만이','대로','하고','와는','과는','은','는','이','가','을','를','의','에','와','과','로','만','도']
FORM_WORDS = '''
한 두 세 네 각 모든 같은 다른 서로 어떤 해당 각각 하나 둘 여러 바로 먼저 나중에 이미 아직
항상 반드시 오직 모두 전혀 그대로 별도 따로 함께 다시 정상적으로 일반적으로 자동으로
직접적으로 독립적으로 논리적으로 실제로 완전히 단지 즉 바로 앞서 이후 이전 뒤쪽 앞쪽
있다 없다 아니다 다르다 같다 크다 작다 맞다 남는다 된다 필요하다 가능하다 무관하다
있고 있고는 있고도 있으므로 있어 있으며 있으면 있는데 없고 없어 없으며 없으면 없는 없음
않는다 않았다 않고 않아 않으며 않으면 않은 않는 아닌 아니며 아니라 같고 같은 달라 다르게
된다 되었다 되고 되어 되므로 되지만 되는 되면 된 할 하는 하며 하므로 하면 한뒤 해야 한다
했다 했고 했으며 했지만 하기 위해 때 만큼 뿐 인 즉 및 또는 그리고 따라서 그러므로 그러면
만든다 만든 만들고 만들어 만들며 만들면 만들수 생긴다 생긴 생겨 생기며 생기면 바꾼다 바꾼
바꾸는 바꾸면 바꾸어 바꾸지 바뀐다 바뀐 바뀌며 바뀔 변한다 변한 변하며 변하면 변하지
확인한다 확인한 확인해 확인하며 확인해야 확인하지 검사한다 검사한 검사하며 검사하지
비교한다 비교한 비교해 비교하면 비교하지 비교하여 선택한다 선택한 선택해 선택하면 선택하지
적용한다 적용한 적용해 적용하면 적용하지 적용하여 계산한다 계산한 계산해 계산하면 계산하지
반환한다 반환한 반환해 반환하면 반환하지 반환하는 생성한다 생성한 생성해 생성하면 생성하지
제거한다 제거한 제거해 제거하면 제거하지 제거되는 유지한다 유지한 유지해 유지하면 유지하지
보존한다 보존한 보존해 보존하면 보존하지 보존하는 집계한다 집계한 집계해 집계하면 집계하지
수행한다 수행한 수행해 수행하면 수행하지 수행하는 포함한다 포함한 포함해 포함하면 포함하지
제외한다 제외한 제외해 제외하면 제외하지 제외하는 구분한다 구분한 구분해 구분하면 구분하지
구별한다 구별한 구별해 구별하면 구별하지 판단한다 판단한 판단해 판단하면 판단하지
요구한다 요구한 요구해 요구하면 요구하지 허용한다 허용한 허용해 허용하면 허용하지
발생한다 발생한 발생해 발생하면 발생하지 금지한다 금지한 금지해 금지하면 금지하지
위반한다 위반한 위반해 위반하면 위반하지 만족한다 만족한 만족해 만족하면 만족하지
대입한다 대입한 대입해 대입하면 대입하지 읽는다 읽은 읽어 읽으며 읽으면 읽지 읽었다
세다 센다 센 세고 세며 세면 세지 더한다 더한 더해 더하면 더하지 뺀다 뺀 빼고 빼며 빼야
나눈다 나눈 나눠 나누어 나누며 나누면 나누지 합친다 합친 합쳐 합치면 합치지
통과한다 통과한 통과해 통과하면 통과하지 차단한다 차단한 차단해 차단하면 차단하지
찾는다 찾은 찾아 찾으며 찾으면 찾지 없애지 없애고 없애며 없애면 없앤다 없앤
넘지 넘어 넘으면 넘는 넘을 줄인다 줄인 줄여 줄이면 줄이지 줄어 줄어든다 줄어든
늘린다 늘린 늘려 늘리면 늘리지 늘어 늘어난다 늘어난 커 작아 많아 적어 많으면 적으면
추가한다 추가한 추가해 추가하면 추가하지 더하는 생략한다 생략한 생략해 생략하면 생략하지
지정한다 지정한 지정해 지정하면 지정하지 정의한다 정의한 정의해 정의하면 정의하지
설정한다 설정한 설정해 설정하면 설정하지 설계한다 설계한 설계해 설계하면 설계하지
읽어야 알아야 정한다 정한 정해 정하면 정하지 지정된 정의된 설정된 생성된 변경된
달라진다 달라질 달라지며 달라지면 달라지지 동일하다 동일한 동일하게 중복된 중복되어
이해한다 이해한 의미한다 의미한 뜻한다 뜻하는 간주한다 간주한 가정한다 가정한 가정하면
보장한다 보장한 보장하지 보장할 실패한다 실패한 실패하여 실패하면 실패하지 성공한다
성공한 성공하여 성공하면 취소된다 취소된 취소되어 취소하면 취소하지 소멸한다 소멸한
상실한다 상실한 지워진다 지운 지우며 지우면 지우지 되돌린다 되돌린 되돌려 되돌리면 되돌리지
복구한다 복구한 복구해 복구하면 복구하지 확정한다 확정한 확정해 확정하면 확정하지
무시했다 무시한 무시한다 무시하면 무시하지 누락했다 누락한 누락한다 놓쳤다 빠뜨렸다
반영한다 반영한 반영해 반영하면 반영하지 반영했다 적용했다 합쳤다 합산했다 계산했다
오해했다 혼동했다 뒤집었다 바꾸었다 읽었다 덮었다 축약했다 재집계했다 대조한다
표현한다 표현한 표현해 표현하면 표현하지 표시한다 표시한 표시해 표시하면 표시하지
지킨다 지키는 가진 가지는 가질 붙인다 붙인 붙여 붙이면 붙이지 붙는 붙여야
따른다 따른 따라 따르면 따르지 받는다 받은 받아 받으면 받지 얻는다 얻은 얻어 얻으면 얻지
의존한다 의존한 의존해 의존하면 의존하지 결정한다 결정한 결정해 결정하면 결정하지
설명한다 설명한 설명해 설명하면 설명하지 검토한다 검토한 검토해 검토하면 검토하지
되살린다 되살린 묻는다 묻는 묻고 보인다 보인 보여 보이면 보이지 보여주는
먹는 따른다는 아니라는 한다는 된다는 않는다는 있다는 없다는 뜻으로 되었다는
'''.split()

NOUN_WORDS += '부등식 등호 지표 원자성 오름차순 내림차순 차단표 추출값 전체값 한행 한개 가독성 단일값 한쪽 양쪽 바깥값 하한 상한 단계형 보정값 시작점 도착점 등가 비등가 해당값 비교집합 대책 방법 조합 이동 동등 유료주문 비유료주문 제한순서 업무방향 곱셈 상세별행 해당권한 참조대상 재작성 확장행 유일키 동점키 고유키 정도 상황 출력열 입력열 월별건수 원본총액 소계단위 자식존재 관계상태 최종화면 보존정책 읽기일관성'.split()
NOUN_WORDS += '수행 증식 검증 독립적 일반적 정상적 의도적 가능성 필요성 중요성 정확성 과거 전체합계 한행결과 재계산 재평가 재집계 무시 요청 가정 명시 설명 누락 사용 저장 소멸 보장 적합 충족 일치 부정 역참조 매개변수 필수성 최소성'.split()
NOUN_WORDS += ['미확정','이후','이전','직후','직전']
PARTICLES += ['이다','이므로','이어서','이지만','인데','이면','이라면','이라는','이라고','인가','다']
LEXICON=set(FORM_WORDS+['만들','없는지','않는지','않아야','않다','없이','하는가','있다는','없다는','같아도','되더라도','언제나','고르는','나오는','아닌지','이었는지','어느쪽'])
for word in NOUN_WORDS:
    LEXICON.add(word)
    for suffix in PARTICLES: LEXICON.add(word+suffix)
    if len(word)>=2:
        for suffix in ['한다','하는','하는가','하고','하며','하므로','하면','하지','해야','한','했다','했고','했으며','했으므로','했지만','했다고','한다고','한지','하지는','하였고','하였다','된','되어','되었고','되었다','되지','된다','되며','되면','되는','되지않는지','되지않아야할','하지못한다','하지못하므로']:
            LEXICON.add(word+suffix)
LEX_MAX=max(map(len,LEXICON))
LEX_START={w[:2] for w in LEXICON if len(w)>=2}

@lru_cache(maxsize=None)
def space_run(run):
    if len(run)<4:return run
    # Conservative vocabulary segmentation: retain every character in order.
    length=len(run); dp=[None]*(length+1); dp[length]=(0,[])
    for pos in range(length-1,-1,-1):
        candidates=[]
        for end in range(pos+1,min(length,pos+LEX_MAX)+1):
            piece=run[pos:end]
            if piece in LEXICON:
                cost=0.32+(0.6 if len(piece)==1 else 0)
                candidates.append((cost+dp[end][0],[piece]+dp[end][1]))
        # An unknown span is kept intact until the next known word boundary.
        for end in range(pos+1,length+1):
            if end==length or run[end:end+2] in LEX_START:
                candidates.append((2.3+(end-pos)*0.85+dp[end][0],[run[pos:end]]+dp[end][1]))
        dp[pos]=min(candidates,key=lambda v:v[0])
    return ' '.join(dp[0][1])

def prose(text):
    pairs=[]
    for block in (EDITORIAL,PHRASES,VERBS):
        pairs.extend(line.split('|',1) for line in block.strip().splitlines() if '|' in line)
    for before,after in sorted(pairs,key=lambda z:-len(z[0])):
        if before != after: text=text.replace(before,after)
    # Reviewed boundaries around SQL tokens and numeric examples in prose.
    text=re.sub(r'([가-힣])(?=(?:NULL|TRUE|FALSE|UNKNOWN|SELECT|WHERE|GROUP BY|ORDER BY|PARTITION BY|COUNT|SUM|AVG|EXISTS|COMMIT|ROLLBACK|RANGE|ROWS|ROWNUM|PIVOT|UNPIVOT|RANK|NTILE|LAG|LEAD|DISTINCT|WITH TIES|FETCH|OFFSET|UPDATE|INSERT|DELETE|MERGE|DDL|DML|CHECK|NOT NULL|UNIQUE|PK|FK)(?:\b|[가-힣(]))',r'\1 ',text)
    text=re.sub(r'([가-힣])(?=\d)',r'\1 ',text)
    text=re.sub(r'(\d)(?=(?:행|개|번|명|점|위|월|년|쌍|자)(?:[은는이가을를의만도에으과와]|\b))',r'\1 ',text)
    text=re.sub(r'(?<=[가-힣0-9)])(먼저|반드시|항상|자동으로|각각|모두|이미|다시|서로)(?=[가-힣A-Z])',r' \1 ',text)
    text=re.sub(r'(?<=[가-힣0-9)])(확인한다|구별한다|구분한다|반환한다|계산한다|판단한다|선택한다|적용한다|생성한다|제거한다|검사한다|유지한다|필요하다|가능하다|무관하다|다르다|남는다|보존한다|존재한다|없다|있다|아니다)(?=[.!?\s]|$)',r' \1',text)
    text=re.sub(r'(?<=[가-힣0-9)])(이므로|이어서|이지만|으므로|보다|아니라)(?=[가-힣A-Z0-9])',r'\1 ',text)
    text=re.sub(r'(?<=[가-힣0-9)])(후|뒤)(?=(?:그|각|다른|현재|전체|원본|같은|변경|적용|집계|계산|나머지))',r' \1 ',text)
    text=re.sub(r'[ \t]{2,}',' ',text)
    text=re.sub(r'[가-힣]{4,}',lambda m:space_run(m.group()),text)
    text=text.replace('비 NULL','비NULL')
    # Split mixed SQL/Korean prose at token boundaries while keeping particles
    # attached. This does not run on SQL source or fixture cells.
    token=r'(?:[A-Za-z_][A-Za-z0-9_.]*(?:\([^\n()]*\))?)'
    suffix=r'(이므로|이어서|이어도|이지만|으로는|으로도|에서는|에서도|에게서|에는|에도|으로|에서|에게|까지|부터|보다|처럼|이며|이면|은|는|이|가|을|를|의|에|와|과|로|도|만)'
    text=re.sub('('+token+')'+suffix+r'(?=[가-힣A-Za-z_])',r'\1\2 ',text)
    text=re.sub('('+token+')'+r'(?=[가-힣])',lambda m:m.group(1) if re.match(suffix,text[m.end():]) or text[m.end():].startswith(('다','했다','한다','하는','이고','이다')) else m.group(1)+' ',text)
    text=text.replace('비 NULL','비NULL').replace('되지않는지','되지 않는지').replace('되지않아야할','되지 않아야 할').replace('하지못한다','하지 못한다').replace('하지못하므로','하지 못하므로')
    text=re.sub(r'([A-Za-z0-9_)])이 (다|며|고|면|므로|어서)',r'\1이\2',text)
    text=text.replace('만들수','만들 수').replace('매칭한후','매칭한 후').replace('이방법','이 방법').replace('행사이','행 사이').replace('한행','한 행').replace('행이된다','행이 된다')
    text=re.sub(r'([가-힣])(?=[A-Za-z_])',r'\1 ',text)
    text=text.replace('비 NULL','비NULL')
    repairs={'수 행':'수행','에 는':'에는','에 게':'에게','이 어도':'이어도','독립 적인':'독립적인','가능 성':'가능성','필요 성':'필요성','가능하다 고':'가능하다고','만 이':'만이','해야 한다':'해야 한다','충족 해야':'충족해야','하지 않 다':'하지 않다','때문 이다':'때문이다','소멸 하여':'소멸하여','반환 할':'반환할','읽 지':'읽지','해당 하지':'해당하지','이 므로':'이므로','수 행했다':'수행했다','별도 로':'별도로','범위 밖이 므로':'범위 밖이므로','일반 적으로':'일반적으로','정상 적으로':'정상적으로','형식 적으로':'형식적으로','동일 하게':'동일하게','외부에서 는':'외부에서는','비교집합 의':'비교집합의','추가해도 ON 조건이 동과':'추가해도 ON 조건 이동과','충족 해야':'충족해야'}
    for before,after in repairs.items():text=text.replace(before,after)
    text=re.sub(r'(\d) (행|개|번|명|점|위|월|년|쌍|자)',r'\1\2',text)
    text=re.sub(r'(?<=[가-힣]),(?=[가-힣])',', ',text)
    return text.strip()

def polish_pack():
    for item in pack['questions']:
        if item['kind']=='recall':continue
        for key in ('title','stem','difficultyReason','importanceReason'):
            item[key]=prose(item[key])
        for choice in item['choices']:
            choice['text']=prose(choice['text'])
            choice['reason']=prose(choice['reason'])
        for key in ('summary','memory'):
            item['explanation'][key]=prose(item['explanation'][key])
        item['explanation']['conditions']=[prose(t) for t in item['explanation']['conditions']]
        for step in item['explanation']['steps']:
            step['text']=prose(step['text'])
        if item['id']=='S21-A01-update-filter-rows':
            next(c for c in item['choices'] if c['id']=='c')['reason']='같은 세션은 자신의 미확정 변경을 볼 수 있다.'
        if item['id']=='S22-A05-ddl-commits-prior':
            item['explanation']['memory']='Oracle DDL은 앞선 미확정 DML에도 암묵적 COMMIT 경계를 만든다.'
        if item['id']=='mock-5-S11-m5-full-on-true-empty':
            next(c for c in item['choices'] if c['id']=='b')['reason']='FULL은 반대편이 비어도 미매칭 A 행을 보존한다.'
            item['version']=2
        if item['id']=='mock-4-S22-m4-read-committed-two-sessions':
            item['explanation']['memory']='자기 변경의 가시성과 다른 세션의 미확정 변경에 대한 가시성을 구별한다.'
            item['version']=2
        if item['id']=='mock-3-S22-m3-rollback-later-savepoint':
            next(c for c in item['choices'] if c['id']=='b')['reason']='롤백은 이미 취소한 변경을 다시 복원하는 기능을 제공하지 않는다.'
            item['version']=2
        if item['id'] in ('mock-2-S17-m2-with-ties-needs-order','mock-3-S16-m3-range-current-peers-only','mock-4-S21-m4-update-correlated-all-null','S22-A05-ddl-commits-prior'):
            item['version']=2


note(9,'ORDER BY는 반환 결과의 정렬 기준을 지정한다.','행이 책상에 놓였다는 것과 순서대로 줄 섰다는 것은 다르다. 테이블과 정렬 없는 SELECT 결과에는 보장된 행 순서가 없다.','기본 방향은 ASC다. 여러 키는 왼쪽부터 비교한다. Oracle에서 ASC의 기본 NULL 위치는 LAST, DESC는 FIRST다. 같은 정렬 키를 가진 행의 내부 순서를 고정하려면 유일한 보조 키가 필요하다.','T(id NUMBER, score NUMBER)의 전체 입력: (1,90),(2,NULL),(3,90). SELECT id FROM T ORDER BY score DESC NULLS LAST, id ASC; 결과: 1,3,2. 90점 두 행은 id가 순서를 결정한다.','GROUP BY는 집계를 위한 묶음이고 ORDER BY는 결과의 표시 순서다. GROUP BY가 정렬을 보장한다는 의미는 아니다.','SELECT 별칭은 ORDER BY에서 사용할 수 있다. DISTINCT를 함께 쓸 때는 정렬식에 제약이 있으므로 SELECT에 없는 임의 열을 정렬해도 된다고 일반화하지 않는다. 문자열 순서는 적용된 collation 조건의 영향을 받는다.','오해: 삽입한 순서대로 늘 조회된다. 반례: 인덱스 사용이나 실행 계획 변경으로 순서가 달라질 수 있으므로 요구한 순서는 ORDER BY로 표현한다.','ASC의 NULL 기본 위치는? 동점자를 안정적으로 정렬하려면? GROUP BY만으로 순서를 보장하는가?',['정렬','ascending','descending','NULLS FIRST','NULLS LAST'])

r(9,'guarantee','결과 행의 순서를 요구사항대로 보장하는 수단은?', '최종 SELECT의 ORDER BY',[('INSERT를 실행한 순서','테이블은 삽입 순서를 결과 순서로 보장하지 않는다.'),('기본키가 존재한다는 사실','기본키는 유일성·식별 규칙이며 조회 정렬 지시가 아니다.'),('GROUP BY만 사용','묶음의 생성은 결과 순서 보장과 별개다.')],'최종 ORDER BY가 조회 결과의 정렬 요구를 표현한다.','저장 순서와 반환 순서를 분리하고 결과 단계의 정렬 지시를 찾는다.','표시 순서가 요구되면 최종 ORDER BY를 명시한다.')
r(9,'null-asc','Oracle 19c에서 ASC를 쓰고 NULLS FIRST/LAST를 생략하면 NULL은?', '비NULL 값 뒤에 배치된다',[('비NULL 값 앞에 배치된다','이는 Oracle DESC의 기본 또는 명시한 NULLS FIRST다.'),('행에서 제거된다','정렬은 NULL 행을 제거하지 않는다.'),('숫자 0으로 바뀐다','정렬은 값의 의미나 자료형을 바꾸지 않는다.')],'Oracle ASC의 기본은 NULLS LAST다.','정렬 방향을 확인한 뒤 NULL 배치의 별도 지정 유무를 확인한다.','Oracle ASC 기본 LAST, DESC 기본 FIRST; 다른 DBMS로 일반화하지 않는다.')
r(9,'tie-order','점수가 같은 사람끼리도 실행마다 동일한 순서를 얻으려면?', 'ORDER BY score DESC, 고유한 id ASC',[('ORDER BY score DESC만 지정','동점자 내부의 순서는 결정되지 않는다.'),('score에 DISTINCT를 적용','동점자를 제거하는 동작이지 사람의 순서를 결정하지 않는다.'),('WHERE score IS NOT NULL만 지정','행을 거르는 조건이며 동점 순서를 지정하지 않는다.')],'고유한 보조 정렬 키가 동점 행 사이의 순서를 결정한다.','첫 키 score로 묶인 동점 집합을 찾고 그 내부에서 중복되지 않는 키를 추가한다.','안정적인 Top N·페이징에는 전체 순서를 결정할 정렬 키가 필요하다.')
r(9,'alias-order','SELECT amount*2 AS doubled FROM T 결과를 계산 별칭으로 정렬할 수 있는 위치는?', 'ORDER BY doubled',[('같은 SELECT의 WHERE doubled > 0','일반적으로 같은 쿼리 블록의 SELECT 별칭을 WHERE에서 참조할 수 없다.'),('FROM doubled','별칭은 테이블 이름이 아니다.'),('JOIN doubled USING(amount)','계산 별칭을 조인 테이블로 사용할 수 없다.')],'SELECT 목록의 별칭은 ORDER BY에서 참조할 수 있다.','doubled가 테이블·원본 열이 아니라 SELECT 결과 이름임을 확인한다.','SELECT 별칭의 허용 위치를 모든 절로 확대하지 않는다.')
r(9,'multi-key','ORDER BY dept ASC, salary DESC의 의미는?', 'dept를 먼저 오름차순, 같은 dept 안에서 salary를 내림차순 정렬한다',[('salary를 먼저 정렬한 뒤 dept를 무시한다','왼쪽 정렬 키의 우선순위가 더 높다.'),('dept와 salary 모두 내림차순이다','DESC는 바로 앞 정렬식 salary에 적용된다.'),('dept마다 salary 합계를 만든다','정렬은 집계를 수행하지 않는다.')],'각 정렬식은 독립된 방향을 가지며 왼쪽 키부터 우선 적용한다.','먼저 dept로 비교한다. dept가 같을 때만 salary를 비교한다.','복합 정렬은 왼쪽 키 우선, 방향은 각 식별로 해석한다.')

note(10,'조인은 조건에 맞는 두 입력의 행 쌍을 결합한다.','명단과 주문서를 고객번호로 맞붙이는 작업이다. 한 고객의 주문이 세 개면 고객 정보가 세 결과 행에 나타난다.','INNER JOIN은 ON 조건이 TRUE인 행 쌍만 반환한다. 한쪽 키의 중복과 관계의 카디널리티가 결과 행 수를 결정한다. 일반 등호 비교에서 NULL=NULL은 TRUE가 아니다.','A(k NUMBER)의 입력 1,1,2; B(k NUMBER)의 입력 1,1,3. SELECT A.k FROM A JOIN B ON A.k=B.k; 결과는 1이 네 행이다. A의 1 두 행이 B의 1 두 행과 각각 만난다.','선택은 행을 거르고 조인은 행 쌍을 만든다. UNION은 같은 모양의 결과를 세로로 이어 집합 연산하며 JOIN은 열을 결합한다.','동일 이름 열은 테이블 별칭으로 구분한다. 비등가 조인도 가능하며 등호 조건만이 조인은 아니다. 키 제약이 명시되지 않았다면 이름만 보고 유일성을 가정하지 않는다.','오해: 두 표를 조인하면 행 수는 작은 표의 행 수와 같다. 반례: 중복 키 2개씩은 네 쌍을 만든다.','중복 키가 2개와 3개면 몇 쌍인가? NULL끼리 등호로 매칭되는가? JOIN과 UNION의 차이는?',['INNER JOIN','내부 조인','등가 조인','비등가 조인','카디널리티'])
r(10,'pair-product','INNER JOIN에서 같은 키가 왼쪽 2행, 오른쪽 3행에 있고 다른 매칭은 없으면 결과 행 수는?', '6행',[('2행','왼쪽 각 행은 오른쪽 세 행과 각각 결합한다.'),('3행','오른쪽 행 수만 세면 왼쪽 중복을 빠뜨린다.'),('5행','조인은 두 개수를 더하는 연산이 아니다.')],'같은 키의 가능한 행 쌍 2×3개가 모두 결과에 들어간다.','왼쪽 첫 행의 세 쌍과 둘째 행의 세 쌍을 따로 센다.','조인 행 수는 매칭되는 행 쌍의 수다.')
r(10,'null-equality','일반적인 A.k=B.k 내부 조인에서 두 열이 모두 NULL인 행 쌍은?', '등호 조건이 UNKNOWN이므로 매칭되지 않는다',[('NULL끼리는 항상 매칭된다','NULL 비교는 일반 값의 동일성 비교와 다르다.'),('0끼리 비교한 것으로 매칭된다','NULL은 숫자 0으로 변환되지 않는다.'),('비교만으로 쿼리가 문법 오류가 된다','NULL 등호 비교 자체는 문법상 가능하지만 TRUE가 아니다.')],'INNER JOIN은 ON 결과가 TRUE인 쌍만 남기며 NULL=NULL은 UNKNOWN이다.','두 입력값에 NULL이 있는지 보고 등호의 3값 논리를 적용한다.','NULL 비교가 필요하면 의도한 IS NULL 조건을 별도로 설계한다.')
r(10,'cross-product','CROSS JOIN은 두 입력을 어떻게 결합하는가?', '왼쪽 각 행과 오른쪽 모든 행의 조합을 만든다',[('동일 이름의 열만 자동 비교한다','그 설명은 NATURAL JOIN 쪽에 가깝고 CROSS JOIN에는 매칭 키가 없다.'),('매칭되지 않은 왼쪽 행만 남긴다','그것은 안티 조인 요구에 가깝다.'),('중복을 제거하여 세로로 합친다','그것은 UNION의 성격이다.')],'CROSS JOIN은 데카르트 곱을 생성한다.','각 입력이 m행과 n행이면 가능한 순서쌍을 m×n개 센다.','CROSS JOIN의 행 수는 m×n이며 한쪽이 비면 0행이다.')
r(10,'non-equi','급여가 등급표의 최솟값 이상·최댓값 이하인 행을 붙이는 조인은?', '범위 조건을 사용하는 비등가 조인',[('등호만 허용되므로 구현 불가능','ON은 적법한 범위 조건도 사용할 수 있다.'),('UNION ALL 조인','UNION ALL은 조인이 아니라 집합 연산자다.'),('항상 NATURAL JOIN','동일 이름 열 자동 등호 비교로 급여 범위를 표현할 수 없다.')],'조인 조건은 등호에 한정되지 않으며 구간 포함 여부로도 행 쌍을 선택한다.','급여 행마다 BETWEEN 또는 두 부등식을 만족하는 등급 구간을 찾는다.','구간이 겹치면 한 급여 행이 여러 등급 행과 매칭될 수 있다.')
r(10,'join-union','JOIN과 UNION의 기능 차이로 적절한 것은?', 'JOIN은 행 쌍의 열을 결합하고 UNION은 호환되는 결과 행을 합친다',[('JOIN은 언제나 중복을 제거한다','중복 키가 있으면 조인 결과도 여러 행이 된다.'),('UNION은 두 표의 열을 가로로 붙인다','세로 방향의 결과 집합 결합이다.'),('둘 다 반드시 기본키가 있어야 한다','기본키 없이도 적법한 조인·집합 연산이 가능하다.')],'두 연산은 결과를 구성하는 방식과 호환 조건이 다르다.','열을 붙여 관계를 탐색하는지, 같은 열 구조의 행을 모으는지 구분한다.','JOIN은 행 쌍, 집합 연산은 결과 행의 결합이다.')

note(11,'외부 조인은 매칭된 행 쌍과 함께 보존할 쪽의 미매칭 행을 NULL 확장하여 반환한다.','주문이 없는 고객도 명단에서 지우지 않으려면 고객 쪽을 보존한다. 주문 열에는 없던 주문을 꾸며 넣지 않고 NULL을 표시한다.','LEFT JOIN은 왼쪽, RIGHT JOIN은 오른쪽, FULL OUTER JOIN은 양쪽의 미매칭 행을 보존한다. ON은 매칭 조건이고 WHERE는 조인 결과를 거르는 조건이다.','C(id NUMBER): 1,2. O(cid NUMBER, paid NUMBER): (1,1). SELECT C.id,O.paid FROM C LEFT JOIN O ON C.id=O.cid ORDER BY C.id; 결과 (1,1),(2,NULL). 최종 ORDER BY 앞에 WHERE O.paid=1을 추가하면 (2,NULL)은 UNKNOWN이므로 제거된다.','INNER JOIN에는 미매칭 보존 단계가 없다. CROSS JOIN은 모든 행 쌍이다. NATURAL JOIN은 같은 이름의 모든 열을 비교하므로 스키마 변경에 주의한다. USING은 명시한 같은 이름 열로 동등 조인을 표현한다.','외부 조인 후 오른쪽 열 IS NULL을 이용해 미매칭을 판별할 때는 매칭된 오른쪽 행의 해당 열이 NULL일 수 없는지 확인한다. 오른쪽 PK 같은 열을 사용하면 의미가 분명하다.','오해: LEFT JOIN이면 WHERE 조건과 관계없이 왼쪽 행이 모두 남는다. 반례: NULL 확장된 오른쪽 열을 WHERE에서 >0으로 검사하면 그 행은 제거된다.','ON 필터와 WHERE 필터는 왜 다른가? FULL JOIN의 두 종류 미매칭 행은 어떤 열이 NULL인가?',['LEFT OUTER JOIN','RIGHT JOIN','FULL JOIN','USING','NATURAL JOIN'])
note(12,'서브쿼리는 다른 SQL 안에 포함되어 값·행 집합·존재 여부를 제공하는 질의다.','질문 속 작은 질문이다. 전체 평균을 먼저 계산해 평균보다 큰 값을 찾거나, 현재 고객에게 주문이 있는지를 고객별로 확인할 수 있다.','스칼라 서브쿼리는 1열·최대 1행이어야 한다. 0행이면 NULL, 2행 이상이면 오류다. EXISTS는 행의 존재, IN은 값의 소속을 검사한다. 상관 서브쿼리는 바깥 행의 값을 참조한다.','E(id NUMBER,sal NUMBER): (1,10),(2,30). SELECT id FROM E WHERE sal > (SELECT AVG(sal) FROM E); 평균20보다 큰 id2만 남는다. 최종 결과는 (2) 한 행이다.','JOIN은 매칭 수만큼 바깥 행을 늘릴 수 있지만 EXISTS는 존재 여부만 판단한다. NOT IN과 NOT EXISTS는 비교 대상 NULL 때문에 결과가 달라질 수 있다.','NOT IN 목록에 NULL이 있으면 불일치 값도 UNKNOWN이 될 수 있다. 빈 서브쿼리에 대한 IN은 FALSE이고 NOT IN은 TRUE다. 스칼라 0행은 0이 아니라 NULL이다.','오해: 서브쿼리는 항상 먼저 한 번만 실제 실행된다. 반례: 상관 형태가 있고 옵티마이저가 재작성할 수 있으므로 논리 의미와 물리 실행을 구별해야 한다.','스칼라 0행·2행의 차이는? EXISTS SELECT 목록이 중복되어도 바깥 행 수를 늘리는가?',['scalar subquery','상관 서브쿼리','EXISTS','NOT IN','ANY','ALL'])
note(13,'집합 연산자는 열 구조가 호환되는 SELECT 결과를 행 단위로 결합한다.','같은 양식의 명단 둘을 합치거나, 두 명단에 함께 있는 사람이나 한쪽에만 있는 사람을 구하는 작업이다.','UNION은 합친 뒤 중복 제거, UNION ALL은 중복 유지, INTERSECT는 공통 행, MINUS는 왼쪽에만 있는 행이다. Oracle 19c의 이 세 중복 제거 연산은 결과 행 전체를 비교한다.','A(v NUMBER): 1,1,2,NULL. B(v NUMBER): 2,3,NULL. SELECT v FROM A MINUS SELECT v FROM B; 결과 (1). 중복1은 하나로 줄고 양쪽 NULL은 공통 행으로 취급되어 제외된다.','WHERE의 NULL=NULL은 UNKNOWN이지만 집합 중복 제거는 NULL 행도 하나로 묶는다. JOIN은 열을 붙이므로 집합 연산과 다르다.','각 SELECT의 열 개수가 같고 대응 자료형 그룹이 호환되어야 한다. SELECT 열 이름은 첫 SELECT를 따른다. 최종 정렬을 지정하지 않으면 출력 순서를 기대하지 않는다.','오해: UNION ALL도 중복을 하나로 만든다. 반례: 왼쪽 두 번·오른쪽 한 번 나타나는 행은 세 번 남는다.','중복을 유지하려면? MINUS의 좌우를 바꾸면? WHERE의 NULL 비교와 중복 제거의 NULL 취급은?',['UNION','UNION ALL','INTERSECT','MINUS','집합 연산'])
note(14,'ROLLUP·CUBE·GROUPING SETS는 여러 묶음 수준의 집계를 한 질의로 표현한다.','반별 합계·학년별 합계·전교 합계를 따로 계산하는 대신 원하는 소계 수준을 지정한다.','ROLLUP(a,b)는 (a,b),(a),()를 만든다. CUBE(a,b)는 (a,b),(a),(b),()를 만든다. GROUPING SETS는 나열한 그룹만 계산한다. GROUPING(expr)는 집계 때문에 생긴 NULL이면 1, 원래 데이터 그룹이면 0이다.','T(a VARCHAR2(1),v NUMBER): (X,10),(X,20). SELECT a,SUM(v),GROUPING(a) FROM T GROUP BY ROLLUP(a); 결과 (X,30,0),(NULL,30,1), 순서 미지정. NULL 행은 전체 합계다.','GROUP BY a,b는 상세 그룹 한 수준이다. ROLLUP은 왼쪽부터 계층적 소계, CUBE는 모든 부분집합, GROUPING SETS는 선택한 수준이다.','원래 데이터에도 NULL이 존재할 수 있으므로 a IS NULL만으로 전체 합계를 판별하지 않는다. 중복된 grouping set을 직접 나열하면 중복 그룹 결과가 생길 수 있다.','오해: ROLLUP(a,b)는 b별 소계도 항상 만든다. 반례: (b) 그룹은 없으며 필요하면 GROUPING SETS나 CUBE를 선택한다.','ROLLUP(a,b)의 수준은? 데이터 NULL과 합계 NULL을 무엇으로 구별하는가?',['ROLLUP','CUBE','GROUPING SETS','GROUPING','소계'])
note(15,'윈도우 함수는 결과 행을 유지하면서 해당 행과 관련된 집합을 분석한다.','집계가 반을 한 행으로 요약한다면, 윈도우 함수는 각 학생 행 옆에 반 평균이나 순위를 붙인다.','PARTITION BY는 계산 집합을 나누고 OVER의 ORDER BY는 그 집합 안의 계산 순서를 정한다. RANK는 동점 다음 번호를 건너뛰고 DENSE_RANK는 건너뛰지 않는다. ROW_NUMBER는 행마다 서로 다른 번호를 준다.','T(id NUMBER,score NUMBER): (1,90),(2,90),(3,70). score DESC 기준 RANK는 1,1,3; DENSE_RANK는 1,1,2다. ROW_NUMBER를 score DESC,id로 계산하면 id순 번호1,2,3이다.','GROUP BY는 행을 묶어 줄인다. 윈도우 SUM은 각 원래 행에 합계를 붙인다. OVER 안 ORDER BY와 최종 ORDER BY는 역할이 달라 표시 순서를 별도로 명시한다.','ROW_NUMBER의 동점자 번호를 재현하려면 고유 보조 키가 필요하다. RANK에 보조 키를 추가하면 그 키까지 비교하여 원래 동점이 해소될 수 있다. 일반 WHERE에서 같은 SELECT의 윈도우 계산 결과를 곧바로 필터하지 말고 바깥 쿼리를 쓴다.','오해: RANK는 항상 연속 번호다. 반례: 선두 두 명이 동점이면 다음은3위다.','동점90,90,70의 RANK와 DENSE_RANK는? 순위를 필터하려면 어느 쿼리 블록에서 하는가?',['RANK','DENSE_RANK','ROW_NUMBER','LAG','LEAD','NTILE','분석 함수'])
note(16,'윈도우 프레임은 현재 행의 분석 계산에 포함할 행 또는 값 범위를 지정한다.','한 반 전체가 PARTITION이라면 프레임은 그 안에서 지금 계산할 작은 창이다. 앞사람 한 명과 나만 더할 수도 있고 처음부터 나까지 더할 수도 있다.','ROWS는 정렬된 행 위치 기준, RANGE는 정렬 값 기준이다. 프레임을 지원하는 함수에서 ORDER BY만 있고 프레임을 생략하면 Oracle 기본은 RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW다.','T(id NUMBER,k NUMBER,v NUMBER): (1,1,10),(2,1,20),(3,2,5). SUM(v) OVER(ORDER BY k)의 결과는 id1=30,id2=30,id3=35다. k=1 동료 행을 함께 포함한다. ROWS를 쓰고 ORDER BY k,id이면 누적10,30,35다.','PARTITION은 계산 집합의 경계, ORDER BY는 순서, 프레임은 각 행에서 실제 포함할 부분이다. ROWS와 RANGE는 동점 값이 있을 때 결과가 달라질 수 있다.','물리적 ROWS 프레임은 동점에서 순서가 고정되지 않으면 결과가 불안정할 수 있다. RANGE의 값 오프셋과 복수 정렬 키에는 문법 제약이 있다. LAST_VALUE는 기본 프레임에서는 파티션의 마지막이 아니라 현재 프레임의 마지막을 본다.','오해: UNBOUNDED PRECEDING이 있으면 항상 전체 파티션이다. 반례: 끝 경계가 CURRENT ROW면 이후 값은 빠진다.','앞1행부터 현재까지의 프레임은? LAST_VALUE로 전체 마지막 값을 얻으려면 끝 경계는?',['ROWS','RANGE','CURRENT ROW','UNBOUNDED PRECEDING','LAST_VALUE'])
note(17,'Top N은 기준에 맞춰 정렬한 결과에서 상위 일부를 선택하는 질의다.','먼저 성적순으로 줄을 세우고 앞에서 몇 명을 고른다. 사람을 먼저 자른 뒤 정렬하면 전체 상위가 아니다.','Oracle 19c FETCH FIRST n ROWS ONLY는 정렬 결과를 n행으로 제한한다. WITH TIES는 마지막 선택 행과 ORDER BY 키가 동점인 추가 행도 포함한다. ROWNUM은 같은 쿼리 블록의 최종 ORDER BY 전에 부여되는 의미에 주의한다.','T(id NUMBER,score NUMBER): (1,80),(2,100),(3,100). SELECT id FROM T ORDER BY score DESC FETCH FIRST 1 ROW WITH TIES; id2,id3 두 행, 내부 순서 미지정. id까지 정렬 키에 넣으면 두 행은 그 복합 키로 동점이 아니다.','ROW_NUMBER<=n은 최대 n행 제한에, RANK<=n은 순위 번호 조건에, DENSE_RANK<=n은 서로 다른 상위 n개 정렬값 선택에 해당한다. 동점 때 서로 다르다.','단순 WHERE ROWNUM>1은 첫 후보가1로 탈락하고 다음 후보도1로 탈락하여 0행이다. OFFSET 페이징은 안정적인 정렬이 필요하다. SELECT만 있고 ORDER BY 없는 FETCH는 어떤 행이 선택될지 보장하지 않는다.','오해: WHERE ROWNUM<=3 ORDER BY score DESC는 항상 전체 상위3명이다. 반례: 먼저 선택된 세 후보를 마지막에 정렬할 수 있다. 정렬한 인라인 뷰 바깥에서 제한하거나 FETCH를 쓴다.','ONLY와 WITH TIES의 차이는? ROWNUM>1은 왜 비는가?',['Top N','FETCH FIRST','OFFSET','WITH TIES','ROWNUM'])
note(18,'셀프 조인은 같은 테이블을 다른 역할로 결합하고 계층형 질의는 부모·자식 관계를 재귀적으로 따라간다.','직원표의 나와 상사를 각각 다른 별명으로 읽으면 셀프 조인이다. 최상위에서 부하를 계속 찾아 내려가면 계층 탐색이다.','Oracle START WITH는 루트 조건, CONNECT BY는 다음 관계, PRIOR는 부모 행의 식을 가리킨다. 부모 id와 자식 parent_id를 잇는 하향 탐색은 CONNECT BY PRIOR id=parent_id다. LEVEL은 루트1부터 시작한다.','N(id NUMBER,pid NUMBER): (1,NULL),(2,1),(3,2). SELECT id,LEVEL FROM N START WITH pid IS NULL CONNECT BY PRIOR id=pid; (1,1),(2,2),(3,3). 행 순서는 별도 표시 요구가 없으면 여기서는 집합으로 판단한다.','직원 e LEFT JOIN 직원 m ON e.manager_id=m.id는 직속 상사 한 단계다. 계층 질의는 여러 깊이를 탐색한다. ORDER SIBLINGS BY는 형제끼리 정렬하여 계층을 유지한다.','순환 데이터는 오류·무한 관계 문제를 일으킬 수 있다. NOCYCLE과 CONNECT_BY_ISCYCLE로 순환을 다룬다. WHERE의 행 필터를 START WITH나 CONNECT BY의 경로 제한과 동일시하지 않는다.','오해: PRIOR는 항상 우측 열 앞에 와야 한다. 반례: PRIOR가 어느 식을 부모에서 평가하는지가 중요하며 등식 양변을 바꿀 수 있다.','루트의 LEVEL은? 하향 탐색에서 부모 식은? 직속 상사만 필요할 때 어떤 방법이 간단한가?',['CONNECT BY','START WITH','PRIOR','LEVEL','셀프 조인','ORDER SIBLINGS BY'])
note(19,'PIVOT은 행의 범주를 집계 열로 펼치고 UNPIVOT은 여러 열을 행의 범주·값으로 바꾼다.','월별 매출 행을 1월·2월 열로 나란히 보거나 반대로 넓은 월별 표를 월·금액 두 열로 세운다.','PIVOT은 지정한 집계와 FOR 열·IN 목록을 사용하며 그 절에 쓰이지 않은 입력 열을 암묵적 그룹 키로 삼는다. UNPIVOT은 기본적으로 NULL 값 행을 제외한다. INCLUDE NULLS를 명시하면 포함한다.','T(shop VARCHAR2(1),mon NUMBER,amt NUMBER): (A,1,10),(A,1,5),(A,2,20). SELECT * FROM T PIVOT(SUM(amt) FOR mon IN(1 AS M1,2 AS M2)); 결과 (A,15,20). 같은 shop·mon 두 행은 SUM으로 합친다.','PIVOT은 집계로 원래 행의 세부 구분을 잃을 수 있어 UNPIVOT이 언제나 원본을 완벽히 복구하지 않는다. 조건부 집계도 비슷한 결과를 표현할 수 있지만 문법과 NULL 조건을 비교해야 한다.','PIVOT 입력에 불필요한 id 열이 남으면 그 id도 그룹 키가 되어 기대보다 많은 행이 나올 수 있다. UNPIVOT의 값 열들은 호환되는 자료형 그룹이어야 한다.','오해: UNPIVOT은 NULL 열도 기본으로 행을 만든다. 반례: Q1=10,Q2=NULL이면 기본 결과는 Q1 한 행이며 INCLUDE NULLS일 때 두 행이다.','PIVOT의 암묵적 그룹 키는 무엇인가? NULL 열을 행으로 남기려면?',['PIVOT','UNPIVOT','INCLUDE NULLS','조건부 집계'])
note(20,'정규 표현식은 문자 패턴을 기호로 표현하여 검색·추출·치환한다.','문자열을 통째로 외우지 않고 숫자 세 자리, 영문으로 시작 같은 모양을 검사한다.','^와 $는 각각 시작과 끝을, [0-9]는 숫자 한 문자, +는 앞 요소1회 이상, *는0회 이상, ?는0회 또는1회, {m,n}은 반복 범위를 뜻한다. REGEXP_LIKE는 부분 일치도 TRUE가 될 수 있다.','SELECT CASE WHEN REGEXP_LIKE(\'A12B\',\'^[0-9]+$\') THEN 1 ELSE 0 END FROM dual; 결과0. 전체가 숫자여야 하는데 A와 B가 있으므로 실패한다. 패턴을 \'[0-9]+\'로 바꾸면 부분12가 있어1이다.','LIKE의 %는 임의 문자열이지만 정규식에서 %는 보통 그대로의 문자다. REGEXP_SUBSTR는 맞는 문자열, REGEXP_INSTR는 위치, REGEXP_REPLACE는 치환 결과를 반환한다.','일반 문자 비교·대소문자와 정렬 규칙은 세션 또는 collation의 영향을 받을 수 있으므로 문항은 ASCII와 match_param c 또는 i를 명시한다. .은 기본적으로 줄바꿈을 포함하지 않으며 n 옵션과 구별한다.','오해: [ab]+는 문자열 ab 반복만 뜻한다. 반례: aaa,b,abba도 a 또는 b 한 문자 반복이므로 맞는다. ab 덩어리 반복은 (ab)+다.','전체 숫자 여부를 검사하는 패턴은? 부분 검색과 전체 검사는 어떻게 다른가?',['REGEXP_LIKE','REGEXP_SUBSTR','REGEXP_REPLACE','정규식','패턴'])
note(21,'DML은 INSERT·UPDATE·DELETE·MERGE 등으로 테이블 데이터를 변경한다.','표의 설계도를 바꾸는 것이 아니라 행을 넣고 고치고 지우는 작업이다. WHERE 조건은 어떤 기존 행이 영향을 받을지 결정한다.','INSERT 열 목록과 값의 대응을 확인한다. UPDATE·DELETE에서 WHERE를 생략하면 대상 테이블 전체 행이 대상이다. NULL을 판별할 때 =NULL이 아닌 IS NULL을 사용한다. MERGE는 ON 매칭 여부에 따라 지정한 갱신·삽입을 수행한다.','T(id NUMBER PRIMARY KEY,v NUMBER): (1,10),(2,NULL). 초기 입력은 이미 COMMIT되었고 자동 커밋·트리거·동시 변경은 없다. UPDATE T SET v=0 WHERE v IS NULL; 이후 같은 트랜잭션의 SELECT id,v FROM T ORDER BY id 결과 (1,10),(2,0). COMMIT 전 변경을 ROLLBACK하면 (2,NULL)로 돌아간다.','DELETE는 행을 지우는 DML, DROP TABLE은 테이블 객체를 없애는 DDL, TRUNCATE는 모든 행을 비우는 DDL이다. 단어 뜻이 비슷해도 트랜잭션 동작은 다르다.','명시하지 않은 열은 기본값·NULL 허용·제약조건에 따라 달라진다. UPDATE 계산은 해당 행의 기존 값을 기준으로 의미를 해석한다. 다중행 문장에서 한 행이 제약 위반을 일으키면 그 문장의 부분 성공을 가정하지 않는다.','오해: DELETE에 WHERE가 없으면 문법 오류다. 반례: 적법하지만 모든 행을 대상으로 하므로 의도를 확인해야 한다.','UPDATE 대상 행을 결정하는 절은? DELETE와 DROP의 차이는? MERGE의 분기를 결정하는 조건은?',['INSERT','UPDATE','DELETE','MERGE','데이터 조작어'])
note(22,'트랜잭션은 함께 확정하거나 취소할 논리적 작업 단위이며 TCL이 그 경계를 제어한다.','송금에서 출금만 남고 입금이 사라지면 안 된다. 여러 변경을 한 묶음으로 확정하거나 묶음 전체를 취소한다.','COMMIT은 현재 변경을 확정하고 기존 savepoint를 지운다. ROLLBACK은 미확정 변경을 취소한다. ROLLBACK TO savepoint는 그 지점 이후만 되돌리며 트랜잭션을 끝내지 않는다.','초기 T(id NUMBER PRIMARY KEY,v NUMBER)에 (1,10), 이미 COMMIT. UPDATE로20 → SAVEPOINT s → UPDATE로30 → ROLLBACK TO s. 현재 같은 세션의 값은20이다. 이어 전체 ROLLBACK하면10이다.','SAVEPOINT는 중간 되돌림 표시이지 COMMIT과 같은 영구 확정이 아니다. 문장 단위 원자성과 트랜잭션 전체 경계도 구별한다.','Oracle은 적법한 DDL 실행 전에 암묵적 COMMIT을 수행하고 성공한 DDL 뒤에도 COMMIT한다. 따라서 DDL을 DML처럼 나중에 ROLLBACK하면 모두 복구된다고 가정하지 않는다. 다른 DBMS의 DDL 동작으로 일반화하지 않는다.','오해: COMMIT한 변경도 ROLLBACK으로 취소할 수 있다. 반례: 이미 확정된 이전 트랜잭션은 일반 ROLLBACK 범위를 벗어난다.','ROLLBACK TO가 트랜잭션을 끝내는가? COMMIT 후 savepoint는? DDL 앞의 DML은 어떻게 되는가?',['COMMIT','ROLLBACK','SAVEPOINT','원자성','ACID'])
note(23,'DDL은 테이블 등 데이터베이스 객체의 구조와 제약조건을 정의·변경·제거한다.','집의 방 구조를 만드는 일이 DDL, 그 안에 가구를 넣는 일이 DML이다. 제약조건은 어떤 데이터가 들어올 수 있는지 지키는 규칙이다.','CREATE TABLE은 객체 생성, ALTER TABLE은 구조 변경, DROP TABLE은 객체 제거, TRUNCATE TABLE은 정의를 유지하고 전체 행을 비운다. PRIMARY KEY는 유일성과 NOT NULL을 요구한다. FOREIGN KEY는 참조 무결성이다.','CREATE TABLE T(id NUMBER PRIMARY KEY,age NUMBER CHECK(age>=0)); 에 (1,NULL)은 age NOT NULL이 없으므로 가능하다. (2,-1)은 CHECK가 FALSE여서 실패한다. (NULL,20)은 PK의 NOT NULL 위반이다.','CHECK는 FALSE를 거부하며 UNKNOWN을 통과시킬 수 있으므로 NOT NULL을 대신하지 못한다. UNIQUE와 PRIMARY KEY는 NULL 허용 조건에서 차이가 있다.','Oracle 19c 단일 열 UNIQUE는 여러 NULL을 허용할 수 있다. 복합 UNIQUE의 부분 NULL 규칙은 단일 열 규칙으로 단정하지 않는다. 외래키 열을 반드시 NOT NULL로 만드는 것은 별도 업무 규칙이다.','오해: FK가 있으면 부모 삭제가 언제나 자식까지 자동 삭제한다. 반례: 기본 참조 동작과 ON DELETE CASCADE는 다르며 DDL 정의를 확인해야 한다.','CHECK(age>=0)가 NULL도 막는가? TRUNCATE 후 열 정의는? PK와 UNIQUE의 NULL 차이는?',['CREATE TABLE','ALTER TABLE','DROP TABLE','TRUNCATE','PRIMARY KEY','FOREIGN KEY','CHECK'])
note(24,'DCL은 GRANT·REVOKE 등으로 데이터베이스 접근 권한을 부여하거나 회수한다.','건물 출입권과 특정 방의 읽기·수정 권한을 나누어 주는 작업이다. 사용자가 어떤 자격으로 권한을 얻었는지도 확인한다.','객체 권한은 특정 테이블의 SELECT·UPDATE 등이고 시스템 권한은 CREATE TABLE 같은 작업 능력이다. 역할(role)은 권한을 묶는다. WITH GRANT OPTION은 받은 객체 권한을 다른 사용자에게 재부여할 수 있게 한다.','소유자 A가 GRANT SELECT ON A.T TO B WITH GRANT OPTION; B가 GRANT SELECT ON A.T TO C; 를 수행했다면 B는 T 읽기 권한과 재부여 능력을 받았다. INSERT 권한까지 받은 것은 아니다.','WITH ADMIN OPTION은 시스템 권한·역할 관리와 관련되고 WITH GRANT OPTION은 객체 권한 재부여와 관련된다. 같은 문구로 바꾸어 사용할 수 있다고 가정하지 않는다.','한 경로의 권한을 REVOKE해도 역할·PUBLIC·다른 직접 부여 경로가 남으면 접근이 가능할 수 있다. 객체 권한 재부여의 종속 회수와 시스템 권한 회수의 동작을 동일시하지 않는다.','오해: GRANT SELECT는 테이블 수정도 허용한다. 반례: UPDATE·INSERT 권한은 별도로 필요하다. 최소 권한 원칙에 따라 목적에 필요한 작업만 준다.','SELECT 권한과 CREATE TABLE 권한의 종류는? 재부여를 허용하는 절은? 회수 후 접근이 남을 수 있는 이유는?',['GRANT','REVOKE','ROLE','WITH GRANT OPTION','WITH ADMIN OPTION','최소 권한'])

# Each recall below tests a separate rule or exception; no numeric variants.
r(11,'left-preservation','LEFT OUTER JOIN이 매칭 실패 때 보존하는 행은?','왼쪽 행과 NULL로 채운 오른쪽 열',[('오른쪽 행과 NULL로 채운 왼쪽 열','RIGHT OUTER JOIN의 보존 방향이다.'),('매칭된 행만','INNER JOIN의 동작이다.'),('임의 오른쪽 행 하나','미매칭을 실제 행으로 대체하지 않는다.')],'LEFT는 왼쪽 입력의 미매칭 행을 보존한다.','ON이 TRUE인 쌍을 만든 뒤 왼쪽 미매칭 행에 오른쪽 NULL 열을 붙인다.','외부 조인은 실제 없는 값을 만들어 채우지 않고 NULL 확장한다.')
r(11,'on-where','왼쪽 고객을 모두 유지하면서 유료 주문만 붙이려면 유료 조건을 둘 위치는?','LEFT JOIN의 ON 조건',[('오른쪽 유료 열에 대한 WHERE 조건','NULL 확장 고객까지 필터하여 제거할 수 있다.'),('ORDER BY에만 지정','정렬은 매칭 조건이 아니다.'),('SELECT 별칭 이름에만 기재','별칭은 데이터 필터가 아니다.')],'ON에서 주문 매칭을 제한하면 유료 주문이 없는 고객도 미매칭으로 보존된다.','고객 보존과 주문 선택을 분리한다. 매칭할 주문을 ON에서 고른다.','ON은 매칭, WHERE는 결합 결과의 생존 여부를 결정한다.')
r(11,'natural-columns','NATURAL JOIN이 자동으로 등호 비교에 사용하는 열은?','양쪽 입력에서 이름이 같은 모든 열',[('양쪽 기본키만','기본키 메타데이터만 보고 열을 고르는 조인이 아니다.'),('이름이 다른 모든 열','동일 이름 열을 사용한다.'),('각 표의 첫 번째 열만','열 순서는 그 기준이 아니다.')],'NATURAL JOIN은 공통 열 이름을 자동 사용한다.','두 스키마의 열 이름 교집합을 먼저 찾는다.','NATURAL JOIN은 공통 열 추가에 의미가 바뀔 수 있다.')
r(11,'using-coalesced','A FULL JOIN B USING(k)에서 SELECT k의 k는?','조인 키를 한 열로 표현한 결과',[('항상 A.k만 그대로 선택','미매칭 오른쪽 키도 공통 키 결과에 나타날 수 있다.'),('두 k를 문자열로 연결한 값','연결 함수가 아니다.'),('항상 NULL','일치·보존된 키를 표현한다.')],'USING 열은 중복된 두 키 열 대신 공통 결과 열로 다룬다.','공통 키와 양쪽 다른 열의 NULL 확장을 구별한다.','USING의 공통 열과 ON으로 남는 개별 열을 구별한다.')
r(11,'anti-null-key','외부 조인 후 미매칭 여부를 오른쪽 열 IS NULL로 검사할 때 가장 명확한 열은?','매칭된 행에서는 NULL이 될 수 없는 오른쪽 기본키',[('원래 NULL이 가능한 메모 열','매칭된 행의 메모도 NULL일 수 있어 미매칭과 혼동한다.'),('왼쪽 고객 이름','오른쪽 매칭 여부를 나타내지 않는다.'),('상수 NULL 표현식','모든 행이 NULL로 보여 구별하지 못한다.')],'오른쪽 PK는 매칭된 행에서 NULL이 아니므로 NULL 확장과 구분된다.','실제 오른쪽 행에 NULL이 들어갈 가능성을 먼저 확인한다.','미매칭 판별 열은 실제 매칭 행에서 비NULL임이 보장되어야 한다.')
r(12,'scalar-empty','스칼라 서브쿼리가 0행을 반환하면 스칼라 값은?','NULL',[('숫자 0','행이 없다는 의미를 숫자 0으로 바꾸지 않는다.'),('빈 문자열이라는 별도 값','스칼라 결과는 NULL이다.'),('반드시 다중행 오류','오류는 2행 이상일 때 발생한다.')],'0행 스칼라 서브쿼리는 NULL로 평가된다.','단일값 위치인지 확인하고 반환 행 수를 0·1·복수로 구분한다.','스칼라: 0행=NULL, 1행=그 값, 복수행=오류.')
r(12,'scalar-many','단일값 위치의 서브쿼리가 같은 값 2행을 반환하면?','다중행 스칼라 서브쿼리 오류',[('두 값이 같으므로 자동 하나로 줄인다','DISTINCT나 집계를 명시하지 않으면 행 수2가 유지된다.'),('첫 번째 행만 사용한다','임의 첫 행 선택 규칙은 없다.'),('두 값을 더한다','SUM을 요청하지 않았다.')],'같은 값이어도 2행이므로 스칼라의 최대1행 조건에 위배된다.','값의 종류 수와 반환 행 수를 구별한다.','스칼라 제약은 서로 다른 값 수가 아니라 행 수다.')
r(12,'exists-projection','EXISTS (SELECT NULL FROM T WHERE ...)가 TRUE인 조건은?','서브쿼리가 최소 한 행을 반환한다',[('SELECT 값이 NULL이 아니어야 한다','EXISTS는 SELECT 값이 아니라 행 존재를 본다.'),('반드시 정확히 한 행이어야 한다','여러 행이어도 TRUE다.'),('T 전체 행이 조건에 맞아야 한다','하나만 있어도 TRUE다.')],'EXISTS는 반환 값의 NULL 여부와 관계없이 행 존재를 판단한다.','필터를 통과한 행이 있는지만 센다.','EXISTS는 값이 아니라 행의 존재를 묻는다.')
r(12,'not-in-null','비NULL x에 대해 x NOT IN (1,NULL)의 설명으로 맞는 것은?','x=1이면 FALSE, x가1과 달라도 UNKNOWN이라 WHERE를 통과하지 못한다',[('x가1과 다르면 언제나 TRUE','NULL과의 비교가 UNKNOWN이다.'),('NULL을 자동 무시한다','NOT IN은 NULL을 자동 제거하지 않는다.'),('문법 오류다','적법한 식이지만 3값 논리 결과에 주의한다.')],'NOT IN은 모든 원소와 다름을 요구하며 NULL 비교가 TRUE를 막는다.','x<>1 AND x<>NULL로 의미를 풀어 FALSE 또는 UNKNOWN을 확인한다.','NOT IN 전에 비교 집합의 NULL 가능성을 확인한다.')
r(12,'any-all','비어 있지 않은 숫자 집합에서 x > ALL은 어떤 뜻인가?','집합의 모든 값보다 커야 한다',[('집합의 값 하나보다 크면 된다','이는 >ANY의 뜻이다.'),('집합 안 값과 같아야 한다','그것은 소속·동등 비교다.'),('집합 행 수보다 크면 된다','비교 대상은 행 수가 아니라 반환 값이다.')],'ALL은 각 비교가 모두 TRUE여야 하는 조건이다.','ANY는 하나, ALL은 모두로 읽고 NULL이 없는지 별도 확인한다.','ANY와 ALL의 의미를 행 수와 혼동하지 않는다.')
r(13,'all-duplicates','두 결과의 중복 행까지 모두 보존하는 집합 연산자는?','UNION ALL',[('UNION','중복 제거를 수행한다.'),('INTERSECT','공통 행을 중복 제거해 반환한다.'),('MINUS','왼쪽 차집합을 중복 제거해 반환한다.')],'UNION ALL은 양쪽 결과의 각 행을 보존한다.','집합 연산 요구에서 중복이 의미 있는지 먼저 확인한다.','중복 보존 요구는 ALL 여부를 확인한다.')
r(13,'minus-direction','A MINUS B의 의미는?','A에 있지만 B에는 없는 서로 다른 행',[('B에 있지만 A에는 없는 행','좌우가 반대다.'),('양쪽 모두에 있는 행','INTERSECT의 의미다.'),('A와 B의 모든 중복 행','UNION ALL의 의미다.')],'MINUS는 방향이 있는 차집합이다.','왼쪽 행 중 오른쪽과 같은 행을 제거하고 남은 중복을 정리한다.','MINUS는 좌우를 바꾸면 일반적으로 결과가 달라진다.')
r(13,'column-compatibility','집합 연산 SELECT들 사이에 요구되는 기본 조건은?','열 개수가 같고 대응 열의 자료형 그룹이 호환된다',[('테이블 이름이 같아야 한다','서로 다른 표의 결과도 결합할 수 있다.'),('각 SELECT의 행 수가 같아야 한다','행 수는 달라도 된다.'),('열 별칭이 모두 같아야 한다','결과 이름은 보통 첫 SELECT에 따르며 같은 별칭은 필수 조건이 아니다.')],'집합 연산은 같은 구조의 행을 비교·결합하므로 대응 열의 호환이 필요하다.','열의 개수와 대응 위치의 자료형을 순서대로 점검한다.','열 이름보다 개수·위치·자료형 호환을 먼저 본다.')
r(13,'set-null','UNION의 중복 제거에서 두 입력의 동일한 한 열 NULL 행은?','한 행의 NULL로 합쳐진다',[('NULL=NULL이 UNKNOWN이므로 반드시 두 행 유지','WHERE 등호의 3값 논리와 집합 중복 제거를 혼동했다.'),('NULL 행을 전부 제거한다','UNION이 NULL을 필터하지는 않는다.'),('0 한 행으로 바뀐다','값을 숫자0으로 치환하지 않는다.')],'집합 중복 제거는 NULL을 포함한 동일 행도 중복으로 처리한다.','NULL 행의 보존과 중복 제거를 별개의 단계로 생각한다.','UNION의 NULL 중복 취급을 WHERE 등호와 동일시하지 않는다.')
r(14,'rollup-levels','ROLLUP(a,b)가 생성하는 그룹 수준은?','(a,b), (a), ()',[('(a,b), (b), ()','ROLLUP의 앞쪽 접두 키는 a다.'),('(a,b)만','기본 GROUP BY a,b와 혼동했다.'),('(a,b), (a), (b), ()','그것은 두 키 CUBE의 수준이다.')],'ROLLUP은 오른쪽부터 키를 줄여 계층 소계와 전체 합계를 만든다.','두 키→첫 키→키 없는 전체 합계로 한 단계씩 줄인다.','ROLLUP 키 순서는 소계의 종류에 영향을 준다.')
r(14,'cube-levels','독립 키 a,b의 CUBE가 나타내는 그룹 수준 수는?','4개',[('2개','상세·전체만 있는 것이 아니라 단일 키별 소계도 있다.'),('3개','두 키 ROLLUP의 수준 수다.'),('항상 입력 행 수와 같다','그룹 수준 수와 출력 행 수는 다르다.')],'두 키의 부분집합은 (a,b),(a),(b),() 네 개다.','각 키를 포함하거나 제외하는 조합을 나열한다.','CUBE 수준 수와 각 수준의 실제 출력 행 수를 구별한다.')
r(14,'grouping-null','집계 결과의 NULL이 원래 데이터인지 소계 때문에 생긴 것인지 구분하는 함수는?','GROUPING(열)',[('IS NULL만 검사','두 종류 NULL 모두 참이므로 원인을 구분하지 못한다.'),('COUNT(*)','행 수를 셀 뿐 NULL의 발생 원인을 알려주지 않는다.'),('ROWNUM','그룹 수준 표시가 아니다.')],'GROUPING은 집계 때문에 제외된 그룹 열이면1을 반환한다.','해당 열이 현재 그룹 수준에서 포함됐는지 확인한다.','GROUPING=1은 집계용 NULL, 실제 NULL 그룹은0이다.')
r(14,'sets-explicit','(부서) 소계와 전체 합계만 원할 때 직접 표현할 수 있는 것은?','GROUP BY GROUPING SETS((dept),())',[('GROUP BY dept,team','팀별 상세 그룹을 만든다.'),('GROUP BY CUBE(dept,team)','팀 단독 등 필요하지 않은 수준도 만든다.'),('GROUP BY team','부서 소계와 전체 합계를 요청하지 않았다.')],'GROUPING SETS는 원하는 그룹 수준을 명시적으로 나열한다.','필요 수준 두 개를 (dept)와 빈 그룹()로 적는다.','빈 그룹()는 전체 합계 수준이다.')
r(15,'rank-gaps','점수가90,90,70일 때 score DESC의 RANK 값은?','1,1,3',[('1,1,2','DENSE_RANK의 번호다.'),('1,2,3','ROW_NUMBER처럼 동점도 분리한 번호다.'),('0,0,2','순위 번호는1부터 시작한다.')],'RANK는 동점 행 수를 반영하여 다음 순위에 간격이 생긴다.','선두 두 행이1위를 차지했으므로 세 번째 행은3위다.','RANK는 동점 동일 순위와 다음 순위 건너뜀을 함께 기억한다.')
r(15,'dense-rank','DENSE_RANK가 RANK와 다른 점은?','동점 뒤 다음 순위에 빈 번호가 없다',[('동점을 서로 다른 순위로 만든다','둘 다 같은 정렬 키면 같은 순위를 준다.'),('순위를0부터 시작한다','1부터 시작한다.'),('항상 행 수를 줄인다','분석 함수는 원래 결과 행에 값을 붙인다.')],'DENSE_RANK는 서로 다른 정렬값의 순서를 연속 번호로 센다.','동점 그룹 하나가 끝나면 다음 그룹의 순위를1 증가시킨다.','서로 다른 상위 점수 개수를 고를 때 DENSE_RANK 의미를 확인한다.')
r(15,'partition-reset','ROW_NUMBER() OVER(PARTITION BY dept ORDER BY id)의 번호가 다시1이 되는 경계는?','dept별 파티션의 시작',[('전체 결과에서 한 번만','PARTITION BY가 집합을 나눈다.'),('id가 짝수인 행마다','그런 규칙은 없다.'),('NULL이 나타날 때마다 무조건','NULL dept 행들은 같은 파티션을 이룰 수 있으며 행마다 초기화하지 않는다.')],'각 dept 파티션은 독립적으로 번호를 매긴다.','dept 그룹을 먼저 나누고 각 내부에서 id 순서를 만든다.','PARTITION BY는 분석 계산을 독립적으로 나누는 경계다.')
r(15,'lag-offset','LAG(v,1,0) OVER(ORDER BY id)가 뜻하는 것은?','id 순서로 한 행 앞의 v, 앞 행이 없으면0',[('현재 v가 NULL이면 항상0','기본값은 앞 행이 없을 때 쓰며 그 행의 NULL 값을 자동 치환하지 않는다.'),('id 값이 정확히1 작은 행의 v','행 위치 오프셋이며 id 숫자 차이가 아니다.'),('한 행 뒤의 v','LEAD의 방향이다.')],'LAG는 정렬된 결과의 앞 행을 참조한다.','현재 행 앞 위치가 존재하는지 먼저 확인하고 있으면 해당 v를 읽는다.','LAG의 기본값은 누락된 행과 NULL 값의 차이를 보여준다.')
r(15,'analytic-order','OVER(ORDER BY score DESC)만 있고 최종 ORDER BY가 없으면?','분석 계산 순서는 정하지만 최종 표시 순서는 보장하지 않는다',[('최종 결과도 반드시 score DESC다','분석 계산과 결과 표시 정렬은 별도다.'),('분석 함수 자체가 문법 오류다','적법한 분석식이다.'),('score를 합산한다','정렬식만으로 합계를 만들지 않는다.')],'OVER의 ORDER BY는 분석 함수의 계산 기준이다.','함수 내부 절과 최종 SELECT 절을 분리해서 읽는다.','분석 순서와 표시 순서를 각각 명시한다.')
r(16,'rows-range','ROWS와 RANGE의 핵심 차이는?','ROWS는 행 위치, RANGE는 정렬값 범위 기준이다',[('ROWS는 문자열만, RANGE는 숫자만 허용','자료형만으로 두 개념을 나누는 설명이 아니다.'),('둘은 동점이 있어도 언제나 같다','RANGE는 같은 정렬값의 동료 행을 함께 포함할 수 있다.'),('RANGE는 항상 전체 표를 계산','파티션과 경계의 영향을 받는다.')],'물리적 위치와 논리적 값 범위의 차이가 동점에서 드러난다.','현재 행과 같은 정렬값을 가진 다른 행의 포함 여부를 확인한다.','동점이 있는 누적합은 프레임을 먼저 확인한다.')
r(16,'default-frame','Oracle에서 프레임 지원 분석 함수에 ORDER BY가 있고 프레임을 생략하면 기본은?','RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW',[('ROWS BETWEEN 1 PRECEDING AND CURRENT ROW','앞 한 행만 보는 제한은 기본이 아니다.'),('ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING','전체 파티션 물리 프레임이 기본은 아니다.'),('프레임을 생략하면 항상 문법 오류','지원 함수는 기본 프레임을 적용할 수 있다.')],'Oracle 문서의 기본은 처음부터 현재 정렬값까지의 RANGE다.','함수가 프레임을 지원하는지와 OVER ORDER BY 유무를 먼저 확인한다.','모든 분석 함수에 프레임 규칙을 무조건 적용하지 않는다.')
r(16,'last-full','LAST_VALUE로 파티션 전체의 마지막 값을 반복 표시하려면 끝 경계를 무엇으로 설정하는가?','UNBOUNDED FOLLOWING',[('CURRENT ROW','현재 프레임의 마지막이므로 전체 마지막과 다를 수 있다.'),('1 PRECEDING','현재보다 앞에서 끝난다.'),('UNBOUNDED PRECEDING만 지정','시작만으로 끝 경계가 정해지지 않는다.')],'전체의 뒤쪽까지 포함하도록 프레임 끝을 열어야 한다.','전체 마지막 행이 각 현재 행의 프레임에 포함되는지 확인한다.','LAST_VALUE는 이름보다 프레임 끝 경계를 먼저 본다.')
r(16,'moving-window','현재 행과 바로 앞 두 행의 합계를 위한 프레임은?','ROWS BETWEEN 2 PRECEDING AND CURRENT ROW',[('RANGE BETWEEN 2 PRECEDING AND CURRENT ROW','정렬값 간격2이며 반드시 앞 두 행은 아니다.'),('ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING','현재와 뒤 두 행이다.'),('ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW','처음부터 누적하며 앞 두 행으로 제한하지 않는다.')],'행 위치 기준으로 현재를 포함해 최대3행을 선택한다.','위치 오프셋2 앞에서 시작해 현재에서 끝낸다.','이동 창은 위치인지 값의 거리인지 먼저 구분한다.')
r(16,'first-boundary','ROWS BETWEEN 1 PRECEDING AND CURRENT ROW에서 파티션 첫 행은 몇 행을 포함하는가?','현재 행1개',[('가상의 이전 행까지2개','존재하지 않는 행을 생성하지 않는다.'),('0개','CURRENT ROW를 포함한다.'),('전체 파티션','경계가 한 행 앞과 현재로 제한된다.')],'파티션 밖의 이전 행은 없으므로 현재 행만 포함한다.','프레임을 파티션 경계와 교차시켜 실제 행만 남긴다.','프레임 경계는 파티션 밖의 가상 데이터를 만들지 않는다.')
r(17,'ties-key','FETCH FIRST 2 ROWS WITH TIES의 추가 동점 여부는 무엇으로 판단하는가?','ORDER BY에 나열한 정렬 키 전체',[('SELECT 첫 열만','정렬 키와 무관한 출력 열은 판단 기준이 아니다.'),('테이블 기본키만','정렬 키에 포함되지 않았다면 자동 기준이 아니다.'),('마지막 숫자 열만','그런 규칙은 없다.')],'WITH TIES는 마지막 제한 행과 ORDER BY 키가 같은 추가 행을 포함한다.','마지막 선택 행의 모든 정렬 키 값을 비교한다.','고유 키를 ORDER BY에 추가하면 점수 동점도 복합 키로는 동점이 아닐 수 있다.')
r(17,'rownum-greater','같은 쿼리 블록의 단순 WHERE ROWNUM > 1 결과는?','0행',[('첫 행만 제외한 나머지','첫 후보가 탈락하면 다음 후보도 ROWNUM1로 검사된다.'),('첫 행1개','조건1>1은 FALSE다.'),('문법 오류','적법하지만 결과가 비는 조건이다.')],'첫 통과 행에1을 부여하려 하지만1>1이 거짓이어서 어떤 행도 통과하지 못한다.','첫 후보와 다음 후보 모두 첫 통과 위치에서 검사를 반복함을 생각한다.','첫 ROWNUM 값 1을 제외하는 하한 조건은 안쪽 쿼리에서 부여한 별칭을 바깥 쿼리에서 필터링하여 다룬다.')
r(17,'top-before-sort','ROWNUM<=3과 ORDER BY를 같은 블록에 둔 전형적 쿼리의 주의점은?','전체를 정렬한 뒤 상위3행을 자른다는 보장이 없다',[('항상 전체 최하위3행을 준다','어떤 후보가 먼저 선택될지 단정할 수 없다.'),('반드시3행을 초과한다','제한 조건은 최대3행이다.'),('Oracle에서 ORDER BY를 쓸 수 없다','정렬은 가능하지만 제한과의 의미가 다르다.')],'같은 블록의 ROWNUM 선택 뒤 정렬되는 의미에 주의해야 한다.','선택 대상 집합의 제한과 최종 정렬 순서를 분리한다.','정렬한 인라인 뷰 밖 ROWNUM 제한 또는 ORDER BY FETCH를 사용한다.')
r(17,'offset-order','페이지를 반복 조회할 때 ORDER BY score만 있고 동점자가 있다면?','동점 내부 순서가 고정되지 않아 페이지 행 구성이 바뀔 수 있다',[('항상 PK순이 자동 추가된다','DB가 그런 보조 정렬을 보장하지 않는다.'),('OFFSET이 동점자를 제거한다','OFFSET은 건너뛰기이며 중복 제거가 아니다.'),('FETCH가 모든 동점자를 자동 포함한다','WITH TIES를 명시하지 않은 ONLY는 다르다.')],'페이징 경계가 동점 집합을 자를 수 있으므로 전체 순서를 결정할 키가 필요하다.','정렬 키가 각 행을 유일하게 순서 지을 수 있는지 확인한다.','안정적인 페이징에는 유일한 보조 정렬 키를 포함한다.')
r(17,'distinct-ranks','서로 다른 상위2개 점수에 속한 모든 사람을 고르는 순위 조건은?','점수 DESC DENSE_RANK 값<=2',[('ROW_NUMBER 값<=2','사람을 최대2행만 선택한다.'),('RANK 값=2만','1위가 제외되고 동점 구조에 따라2위 자체가 없을 수 있다.'),('ROWNUM=2','같은 블록의 ROWNUM=2는 단순 필터로 동작하지 않는다.')],'DENSE_RANK는 서로 다른 정렬값 그룹에 연속 번호를 부여한다.','상위 행 수인지 상위 점수 종류 수인지 요구를 구분한다.','상위 n개 값 그룹과 상위 n개 행은 다르다.')
r(18,'level-root','Oracle 계층 질의의 루트 행 LEVEL은?','1',[('0','Oracle LEVEL은 루트에서1이다.'),('NULL','루트도 깊이 값을 가진다.'),('루트 id와 같다','식별자와 깊이는 다른 값이다.')],'LEVEL은 계층 깊이를 루트1부터 센다.','START WITH로 선택된 행에 깊이1을 부여한다.','LEVEL은 식별자가 아니라 경로상의 깊이다.')
r(18,'prior-parent','CONNECT BY PRIOR id=parent_id에서 PRIOR id는 어느 행의 id인가?','현재 관계에서 부모 행의 id',[('항상 최초 루트의 id','직접 부모 식이며 모든 깊이에서 루트만 보는 것은 아니다.'),('자식 행의 id','PRIOR는 부모 평가를 지정한다.'),('직전 물리 저장 행의 id','계층 관계이며 물리 저장 위치가 아니다.')],'PRIOR는 부모 행의 식을 평가한다.','부모 id와 후보 자식 parent_id가 같은지 비교한다.','PRIOR의 방향을 열 이름만으로 추측하지 말고 식으로 읽는다.')
r(18,'siblings','계층 구조를 유지하며 같은 부모의 자식끼리 정렬하는 절은?','ORDER SIBLINGS BY',[('전체 ORDER BY만','계층 출력 구조를 깨는 전체 정렬이 될 수 있다.'),('GROUP BY LEVEL','깊이별 집계를 요청하여 행 의미를 바꾼다.'),('START WITH 정렬식','START WITH는 루트 조건이다.')],'ORDER SIBLINGS BY는 형제 행의 순서를 지정한다.','전체 결과 재정렬과 각 부모 아래 형제 정렬을 구별한다.','계층의 형제 정렬 요구에는 SIBLINGS를 확인한다.')
r(18,'self-roles','직원 표를 직원과 상사 역할로 한 번씩 참조하는 데 필요한 것은?','같은 표에 서로 다른 별칭을 부여한 셀프 조인',[('반드시 동일 데이터를 새 표로 복사','별칭으로 역할을 나눌 수 있다.'),('UNION으로 두 번 더하기','상사 열을 붙이는 요구를 수행하지 않는다.'),('기본키 삭제','조인을 위해 제약을 삭제할 필요가 없다.')],'별칭은 동일 테이블을 서로 다른 행 역할로 참조하게 한다.','직원 e의 manager_id를 상사 m의 id와 비교한다.','셀프 조인은 복사본이 아니라 동일 표의 역할 구분이다.')
r(18,'nocycle','순환이 있을 수 있는 Oracle 계층 관계 탐색에서 관련된 옵션은?','CONNECT BY NOCYCLE',[('DISTINCT만 지정','중복 결과 제거만으로 순환 탐색 제어를 대신하지 못한다.'),('ORDER BY LEVEL DESC만','순서 변경이 순환을 제거하지 않는다.'),('COMMIT 추가','트랜잭션 확정은 계층 순환 탐색 옵션이 아니다.')],'NOCYCLE은 순환 관계가 있는 입력에서 계층 결과를 다루기 위한 옵션이다.','부모 연결이 이미 경로에 있는 행으로 돌아오는지 생각한다.','순환 데이터와 중복 표시 문제를 별개로 본다.')
r(19,'pivot-group','PIVOT의 암묵적 그룹 키가 되는 입력 열은?','PIVOT의 집계·FOR 참조에 사용되지 않은 열',[('항상 첫 번째 열만','입력의 참조 관계로 결정된다.'),('집계 대상 값 열만','그 열은 집계에 사용되며 그룹 키가 아니다.'),('모든 열이 무조건 제거된다','남은 그룹 열이 결과를 구분한다.')],'PIVOT은 절에서 참조하지 않은 입력 열을 기준으로 암묵적 GROUP BY를 수행한다.','입력 열에서 집계 열과 FOR 열을 제외한다.','필요 없는 식별자 열은 PIVOT 입력 인라인 뷰에서 제거한다.')
r(19,'unpivot-null','Oracle UNPIVOT에서 NULL 행 포함 옵션을 생략하면?','값이 NULL인 변환 행을 제외한다',[('모두 포함한다','INCLUDE NULLS를 명시할 때 포함한다.'),('NULL을0으로 치환한다','값 대체가 아니다.'),('원래 행 전체를 삭제한다','해당 NULL 값의 변환 행만 제외한다.')],'UNPIVOT의 기본은 EXCLUDE NULLS다.','행이 될 각 원본 값 열의 NULL 여부를 개별 확인한다.','NULL을 행으로 유지하려면 INCLUDE NULLS를 명시한다.')
r(19,'pivot-loss','집계 PIVOT 다음 UNPIVOT을 수행하면 항상 원래 상세 행을 복원하는가?','아니다. 집계로 합쳐진 상세 행 구분은 잃을 수 있다',[('항상 완전히 복원한다','SUM으로 합친10과20의 구분은 합계30만으로 복구되지 않는다.'),('테이블 이름만 같으면 복원한다','객체 이름은 정보 손실과 관계없다.'),('UNPIVOT이 원래 기본키를 자동 생성한다','원래 행 식별자를 복원하는 기능이 아니다.')],'집계는 여러 행을 한 값으로 요약하므로 변환을 반대로 해도 원래 세부 데이터가 남지 않는다.','PIVOT 전 동일 그룹에 여러 원본 행이 있는지 확인한다.','형태를 되돌리는 것과 잃은 정보를 복구하는 것은 다르다.')
r(19,'unpivot-shape','Q1,Q2 매출 열을 quarter,amount 두 열의 행으로 바꾸는 목적에 맞는 연산은?','UNPIVOT',[('PIVOT','범주 행을 열로 펼치는 반대 방향이다.'),('CUBE','집계 수준을 생성한다.'),('TRUNCATE','데이터를 비운다.')],'UNPIVOT은 여러 값 열을 범주·값 행으로 세운다.','입력 열 두 개가 출력 행의 범주 값 두 개로 대응됨을 그린다.','열을 범주 행으로 세우는 것은 UNPIVOT이다.')
r(20,'anchors','ASCII 숫자로만 구성된 비어 있지 않은 전체 문자열을 검사할 패턴은?','^[0-9]+$',[('[0-9]+','문자열 중간의 숫자 일부만 있어도 일치할 수 있다.'),('^[0-9]*$','0회도 허용하므로 비어 있지 않음의 표현이 다르다.'),('^[0-9]$','정확히 숫자 한 문자만 허용한다.')],'양끝 앵커가 전체 범위, +가 한 번 이상을 요구한다.','시작·끝 제한과 반복 최소 횟수를 각각 읽는다.','전체 검사에는 앵커, 최소 한 글자에는 +를 확인한다.')
r(20,'class-group','[ab]+의 의미는?','a 또는 b 한 문자가 한 번 이상 반복된다',[('ab 두 글자 덩어리만 반복된다','그 표현은 (ab)+다.'),('a 뒤에 숫자 b개가 온다','문자 클래스와 반복을 잘못 읽었다.'),('a와 b가 각각 한 번만 나온다','+는 여러 번 반복을 허용한다.')],'대괄호는 한 문자 선택 집합이고 +는 그 원소의 반복이다.','[ab] 한 자리에는 a 또는 b가 온다고 보고 반복한다.','문자 클래스 []와 묶음 ()를 구별한다.')
r(20,'regexp-functions','일치한 부분 문자열 자체를 반환하는 Oracle 함수는?','REGEXP_SUBSTR',[('REGEXP_INSTR','일치 위치를 반환한다.'),('REGEXP_LIKE','패턴 일치 조건이다.'),('REGEXP_REPLACE','치환한 전체 문자열을 반환한다.')],'SUBSTR 계열은 추출된 문자열을 반환한다.','반환하려는 것이 값·위치·조건·치환 결과인지 구분한다.','함수 이름보다 반환 형태를 먼저 확인한다.')
r(20,'case-param','Oracle 정규식에서 대소문자 무시를 명시하는 match_param은?','i',[('c','대소문자 구분을 지정한다.'),('n','점이 줄바꿈을 포함하도록 하는 옵션과 관련된다.'),('m','여러 줄에서 앵커의 의미와 관련된다.')],'i는 case-insensitive 매칭을 명시한다.','기본 세션 동작을 추측하지 않고 인수에 명시된 옵션을 적용한다.','대소문자 문항은 c 또는 i 조건을 명확히 읽는다.')
r(21,'delete-no-where','DELETE FROM T에서 WHERE가 없으면 대상은?','T의 모든 행',[('문법 오류','조건 생략은 적법하다.'),('마지막 삽입 행만','그런 기본 제한은 없다.'),('T의 열 정의까지 삭제','객체 정의 제거는 DROP TABLE이다.')],'조건이 없으므로 모든 기존 행이 삭제 대상이다.','행 필터가 있는지 먼저 확인하고 없으면 전체 입력을 대상으로 본다.','DELETE의 WHERE 생략은 전체 행 대상이지 객체 제거가 아니다.')
r(21,'update-null','NULL인 v만0으로 바꾸려면 WHERE 조건은?','v IS NULL',[('v = NULL','UNKNOWN이어서 대상 행을 선택하지 못한다.'),('v = 0','이미0인 행을 고른다.'),('v IS NOT NULL','비NULL 행을 고른다.')],'NULL 여부는 IS NULL로 검사한다.','값 동등 비교와 NULL 판별을 분리한다.','DML의 WHERE에도 같은 3값 논리가 적용된다.')
r(21,'insert-column','INSERT에서 열 목록을 명시하는 주요 이점은?','각 값이 어느 열에 대응하는지 명확히 지정한다',[('모든 제약조건을 자동 무시한다','제약은 그대로 적용된다.'),('삽입과 동시에 자동 COMMIT된다','일반 INSERT 자체가 자동 확정을 뜻하지 않는다.'),('중복 기본키를 허용한다','PK 유일성 위반은 막힌다.')],'명시한 열 순서대로 VALUES가 대응한다.','열 목록과 값 목록을 위치별로 짝짓는다.','열 목록의 명시와 제약·트랜잭션 규칙은 별개다.')
r(21,'merge-branch','MERGE가 MATCHED와 NOT MATCHED 분기를 결정하는 기준은?','소스와 대상 사이의 ON 매칭 조건',[('테이블의 생성 순서','조인 조건과 무관한 메타정보다.'),('소스 행의 첫 글자','그런 일반 규칙은 없다.'),('COMMIT 시각','분기 조건이 아니다.')],'ON이 대상 행과 소스 행의 매칭 여부를 결정한다.','ON 키로 대응 행을 찾고 정의된 분기 절을 적용한다.','MERGE는 모든 행을 무조건 INSERT하는 문장이 아니다.')
r(21,'statement-atomic','여러 행을 바꾸는 UPDATE 한 문장에서 즉시 검사 제약 위반이 발생했다. 기본 설명은?','그 문장의 변경은 취소되지만 앞선 성공 문장의 미확정 변경까지 자동 전부 취소된다고 단정하지 않는다',[('위반 전 행 변경은 일부 확정된다','문장 원자성을 무시했다.'),('테이블이 자동 DROP된다','제약 위반의 동작이 아니다.'),('현재 세션의 모든 과거 COMMIT도 취소된다','이미 확정된 트랜잭션은 범위 밖이다.')],'문장 수준 롤백과 전체 트랜잭션 롤백은 다르다.','실패한 문장의 경계와 그 전에 성공한 문장의 경계를 분리한다.','문장 실패가 곧 과거 전체 트랜잭션 롤백은 아니다.')
r(22,'savepoint-not-commit','SAVEPOINT s를 실행하면 무엇이 일어나는가?','현재 트랜잭션 안에 부분 롤백 지점을 만든다',[('현재 변경을 영구 확정한다','COMMIT과 다르다.'),('새 테이블을 만든다','DDL이 아니다.'),('모든 이전 변경을 취소한다','SAVEPOINT는 취소 명령이 아니다.')],'SAVEPOINT는 되돌림 지점을 표시하며 확정하지 않는다.','표시 생성과 변경 확정·취소를 각각 구분한다.','SAVEPOINT는 중간 표시, COMMIT은 확정이다.')
r(22,'rollback-to','ROLLBACK TO s의 설명으로 옳은 것은?','s 이후 변경을 취소하고 트랜잭션은 계속된다',[('트랜잭션 전체를 반드시 종료한다','전체 ROLLBACK과 다르다.'),('s 이전 변경을 영구 확정한다','COMMIT 동작이 아니다.'),('이전 COMMIT까지 되돌린다','현재 트랜잭션의 savepoint 범위다.')],'부분 롤백은 지정 지점 뒤의 변경을 되돌릴 뿐 트랜잭션을 종료하지 않는다.','savepoint 앞과 뒤의 변경을 구분하여 뒤쪽만 제거한다.','ROLLBACK TO 후에도 앞선 미확정 변경은 남아 있다.')
r(22,'commit-savepoint','COMMIT 직후 이전 트랜잭션의 savepoint를 대상으로 ROLLBACK TO를 하면?','그 savepoint는 더 이상 유효하지 않다',[('이전 트랜잭션으로 이동한다','COMMIT은 트랜잭션을 끝낸다.'),('자동으로 동일 savepoint를 복원한다','그런 복원은 하지 않는다.'),('현재 모든 테이블이 비워진다','오류를 데이터 삭제로 처리하지 않는다.')],'COMMIT은 모든 savepoint를 지운다.','트랜잭션 종료가 중간 표시의 수명을 끝내는지 확인한다.','savepoint는 생성된 현재 트랜잭션 안에서만 유효하다.')
r(22,'ddl-implicit','Oracle에서 적법한 DDL이 실행될 때 앞선 미확정 DML에 대한 주의점은?','DDL 전에 암묵적 COMMIT될 수 있어 뒤의 ROLLBACK으로 되돌리지 못한다',[('DDL은 언제나 앞선 DML을 자동 취소한다','암묵적 확정과 반대다.'),('모든 DBMS가 똑같이 동작한다','DBMS마다 DDL 트랜잭션 동작이 다르다.'),('DDL은 SAVEPOINT와 동일하다','객체 정의와 확정 경계에 관련된 별개 동작이다.')],'Oracle DDL은 앞선 트랜잭션 확정 경계에 영향을 준다.','DML 사이에 DDL이 끼어 있는지 찾고 트랜잭션 경계를 다시 표시한다.','Oracle에서 DDL을 실습할 때 암묵적 COMMIT을 고려한다.')
r(22,'own-changes','자신이 UPDATE한 뒤 COMMIT 전 같은 세션에서 SELECT하면 일반적으로?','자신의 미확정 변경을 볼 수 있다',[('언제나 이전 값만 보인다','자신의 변경 가시성을 무시했다.'),('SELECT 자체가 반드시 자동 COMMIT된다','일반 SELECT는 확정 명령이 아니다.'),('테이블 잠금 때문에 자신의 SELECT가 영원히 대기한다','자기 변경을 읽는 기본 동작 설명이 아니다.')],'트랜잭션은 자신의 변경을 같은 세션의 후속 조회에서 확인할 수 있다.','동일 세션인지 다른 세션인지 먼저 구분한다.','자기 변경의 가시성과 다른 세션에의 확정 가시성은 다르다.')
r(23,'pk-null','PRIMARY KEY에 대한 기본 조건은?','유일하며 구성 열은 NULL일 수 없다',[('중복만 금지하고 NULL은 허용','PK는 NOT NULL도 요구한다.'),('NULL만 금지하고 중복은 허용','유일성도 필요하다.'),('반드시 숫자 한 열이다','문자 또는 복합 키도 가능하다.')],'기본키는 각 행을 유일하게 식별하고 NULL을 허용하지 않는다.','유일성과 NULL 금지 두 조건을 각각 확인한다.','기본키의 핵심은 유일성+NOT NULL이다.')
r(23,'check-unknown','CHECK(v>=0)만 있는 열에 NULL을 넣을 때의 기본 판단은?','조건이 UNKNOWN이므로 CHECK만으로 거부되지 않는다',[('FALSE와 같아서 반드시 거부','CHECK는 UNKNOWN도 통과할 수 있다.'),('NULL을 자동0으로 바꾼다','CHECK는 값 치환이 아니다.'),('PRIMARY KEY가 자동 추가된다','다른 제약이 자동 생성되지 않는다.')],'CHECK는 FALSE를 금지하며 NULL을 막으려면 NOT NULL이 필요하다.','NULL>=0을 UNKNOWN으로 계산하고 CHECK 허용 규칙을 적용한다.','범위 CHECK와 필수값 NOT NULL을 따로 설계한다.')
r(23,'truncate-definition','TRUNCATE TABLE 뒤 유지되는 것은?','테이블의 열 정의',[('기존 모든 행','행을 비우는 명령이다.'),('현재 트랜잭션에서의 일반 DML 롤백 가능성','Oracle TRUNCATE는 DDL이다.'),('WHERE로 선택되지 않은 행','TRUNCATE에는 행 선택 WHERE가 없다.')],'TRUNCATE는 구조를 유지하며 전체 행을 제거한다.','객체 제거 DROP과 행 비우기 TRUNCATE를 구별한다.','Oracle TRUNCATE는 정의 유지·전체 행 제거·DDL이다.')
r(23,'fk-optional','외래키 열에 NOT NULL이 별도로 없을 때 올바른 판단은?','외래키라고 해서 반드시 값 입력을 강제하는 것은 아니다',[('FK가 자동 NOT NULL을 만든다','필수 참여는 별도 NOT NULL 제약과 관련된다.'),('NULL은 반드시 부모 NULL 행과 매칭돼야 한다','NULL 외래키를 일반 부모 매칭으로 해석하지 않는다.'),('외래키는 중복을 항상 금지한다','여러 자식이 같은 부모를 참조할 수 있다.')],'참조 무결성과 필수값 입력은 다른 제약이다.','부모 존재 조건과 NULL 허용 조건을 따로 확인한다.','FK는 참조 규칙이며 NOT NULL·UNIQUE를 자동 대체하지 않는다.')
r(23,'delete-cascade','부모 삭제 시 자식 행도 자동 삭제되도록 명시하는 참조 옵션은?','ON DELETE CASCADE',[('ON DELETE SET NULL','자식 참조 열을 NULL로 바꾸는 동작이다.'),('WITH GRANT OPTION','객체 권한 재부여 옵션이다.'),('PRIMARY KEY만 지정','기본키만으로 연쇄 삭제를 지시하지 않는다.')],'ON DELETE CASCADE는 부모 삭제의 영향을 자식 행 삭제로 전달한다.','자식의 행을 없앨지 참조 값만 비울지 구분한다.','삭제 전파는 FK 정의에 실제 명시된 옵션을 확인한다.')
r(24,'object-system','특정 T 테이블의 SELECT와 CREATE TABLE 권한의 구분은?','SELECT ON T는 객체 권한, CREATE TABLE은 시스템 권한',[('둘 다 T의 객체 권한','CREATE TABLE은 특정 기존 T 조회 권한이 아니다.'),('둘 다 데이터 행이다','권한은 데이터 접근·작업 능력이다.'),('SELECT는 시스템, CREATE TABLE은 객체 권한','구분이 반대다.')],'대상 객체의 작업 권한과 데이터베이스 수준 작업 능력을 나눈다.','권한이 특정 기존 객체에 묶이는지 확인한다.','객체 권한과 시스템 권한의 대상 범위를 구별한다.')
r(24,'grant-option','받은 객체 SELECT 권한을 다른 사용자에게 다시 부여할 수 있게 하는 절은?','WITH GRANT OPTION',[('WITH ADMIN OPTION만 동일하게 사용','시스템 권한·역할 쪽 옵션과 구분해야 한다.'),('WITH TIES','행 제한 동점 옵션이다.'),('ON DELETE CASCADE','외래키 삭제 동작이다.')],'WITH GRANT OPTION은 객체 권한의 재부여 능력을 준다.','조회 능력과 그 권한을 남에게 줄 능력을 분리한다.','객체 권한 재부여는 WITH GRANT OPTION이다.')
r(24,'revoke-paths','직접 SELECT 권한을 회수했는데 사용자가 T를 여전히 읽을 수 있다. 가능한 이유는?','유효한 역할 등 다른 권한 경로가 남아 있다',[('REVOKE는 언제나 아무 효과가 없다','회수한 경로에는 영향이 있다.'),('SELECT가 자동으로 INSERT 권한을 만든다','권한 종류가 자동 바뀌지 않는다.'),('권한 검사 없이 모든 테이블을 읽는다','일반 권한 모델의 설명이 아니다.')],'하나의 부여 경로를 지운 것만으로 모든 경로를 제거했다고 볼 수 없다.','직접 부여·역할·PUBLIC 등 실제 남은 경로를 확인한다.','권한 회수 효과는 경로 전체를 살펴 판단한다.')
r(24,'least-privilege','조회만 필요한 계정에 적용할 최소 권한의 예는?','필요한 테이블의 SELECT만 부여한다',[('모든 테이블의 변경 권한도 함께 준다','목적에 불필요한 권한이다.'),('DBA 역할을 기본 제공한다','조회 요구보다 훨씬 넓은 권한이다.'),('테이블 소유권을 모두 넘긴다','필요 이상으로 관리 능력을 준다.')],'목적에 필요한 객체·작업 범위만 허용한다.','실제 사용자 작업이 읽기인지 변경인지 먼저 명시한다.','최소 권한은 작업과 대상 범위를 함께 제한한다.')

# Applied questions: hand-authored operations, inputs and explicit results.
def W(a,ar,b,br,c,cr): return [(a,ar),(b,br),(c,cr)]
def O(cols,rows): return table('최종 결과',cols.split(','),rows)
def T(name,cols,rows): return (name,[(s.split(':')[0],s.split(':')[1]) for s in cols.split(',')],rows)

sortdata=[T('T','id:NUMBER,dept:NUMBER,score:NUMBER',[(1,2,80),(2,1,None),(3,1,90),(4,1,90)])]
sqlq(9,'mixed-sort','부서별 성적 명단의 id 순서는?', 'SELECT id FROM T ORDER BY dept ASC, score DESC NULLS LAST, id DESC',sortdata,O('ID',[(4,),(3,),(2,),(1,)]),W('(3) / (4) / (2) / (1)','동점에서 id DESC를 누락했다.','(2) / (4) / (3) / (1)','명시한 NULLS LAST를 기본 DESC 위치로 덮어썼다.','(4) / (3) / (1) / (2)','dept 우선순위를 무시했다.'),['dept1이 dept2보다 먼저다. dept1 안에서90점 두 행, NULL 행 순이다.','90점 동점은 id DESC이므로4 다음3, 이후2와1이다.'],'복합 정렬은 왼쪽 키부터 비교하고 각 방향을 따로 적용한다.',ordered=True)
sqlq(9,'case-priority','미채점 행을 먼저 확인한 뒤 id순으로 정렬한다. 출력은?','SELECT id FROM T ORDER BY CASE WHEN score IS NULL THEN 0 ELSE 1 END, id',sortdata,O('ID',[(2,),(1,),(3,),(4,)]),W('(1) / (2) / (3) / (4)','CASE 우선순위를 무시한 id 정렬이다.','(3) / (4) / (1) / (2)','점수순을 요청하지 않았다.','(2)만','CASE는 정렬 키이며 행 필터가 아니다.'),['NULL 점수인 id2의 CASE값은0, 나머지는1이다.','0 그룹의2가 먼저,1 그룹에서는 id1,3,4가 된다.'],'계산식 ORDER BY는 우선순위를 만들며 원본 행을 제거하지 않는다.',ordered=True)
sqlq(9,'alias-derived','계산된 비용으로 내림차순 정렬한 결과는?','SELECT id, price-discount AS net FROM P ORDER BY net DESC, id',[T('P','id:NUMBER,price:NUMBER,discount:NUMBER',[(1,100,40),(2,80,10),(3,90,30)])],O('ID,NET',[(2,70),(1,60),(3,60)]),W('(1, 60) / (3, 60) / (2, 70)','net ASC에 해당한다.','(1, 100) / (3, 90) / (2, 80)','계산과 별칭 정렬을 무시한 원가 결과다.','(2, 70) / (3, 60) / (1, 60)','동점 보조 id ASC를 무시했다.'),['각 net은60,70,60이다.','net70의 id2가 먼저이고60 동점은 id1,3이다.'],'ORDER BY 별칭은 출력 계산값을 가리킬 수 있다.',ordered=True)
sqlq(9,'null-explicit-desc','NULLS LAST를 붙인 내림차순의 값 나열은?','SELECT v FROM T ORDER BY v DESC NULLS LAST',[T('T','v:NUMBER',[(0,),(None,),(-2,),(5,)])],O('V',[(5,),(0,),(-2,),(None,)]),W('(NULL) / (5) / (0) / (-2)','기본 DESC의 NULL 위치를 사용했지만 명시 옵션이 우선한다.','(5) / (NULL) / (0) / (-2)','NULL은0 근처의 숫자가 아니다.','(-2) / (0) / (5) / (NULL)','값 방향을 오름차순으로 읽었다.'),['비NULL 값은5,0,-2 내림차순이다.','NULL은 명시한 LAST에 따라 모든 비NULL 뒤에 둔다.'],'명시한 NULLS FIRST/LAST는 방향별 기본 위치보다 우선한다.',ordered=True)
sqlq(9,'group-sort-total','부서별 합계가 큰 순서로 보인 결과는?','SELECT d,SUM(v) AS total FROM T GROUP BY d ORDER BY total DESC,d',[T('T','d:NUMBER,v:NUMBER',[(1,10),(1,20),(2,25),(3,30)])],O('D,TOTAL',[(1,30),(3,30),(2,25)]),W('(1, 10) / (1, 20) / (2, 25) / (3, 30)','GROUP BY 집계를 수행하지 않은 원본이다.','(2, 25) / (1, 30) / (3, 30)','합계 오름차순이다.','(3, 30) / (1, 30) / (2, 25)','합계 동점의 d ASC를 뒤집었다.'),['d1 합계30,d2 합계25,d3 합계30으로3그룹을 만든다.','합계 DESC 후 d ASC로1,3,2순이다.'],'집계 대상과 정렬 대상은 단계별로 구분한다.',ordered=True)
sqlq(9,'distinct-position','중복 제거한 두 열을 SELECT 두 번째 위치로 정렬한다. 결과는?','SELECT DISTINCT a,b FROM T ORDER BY 2 DESC,1',[T('T','a:NUMBER,b:NUMBER',[(1,2),(1,2),(2,3),(3,2)])],O('A,B',[(2,3),(1,2),(3,2)]),W('(1, 2) / (1, 2) / (2, 3) / (3, 2)','DISTINCT와 정렬을 모두 적용하지 않았다.','(3, 2) / (2, 3) / (1, 2)','첫 번째 열 내림차순으로 오해했다.','(1, 2) / (3, 2) / (2, 3)','두 번째 열 오름차순이다.'),['(1,2) 중복을 하나로 만든다.','ORDER BY2는 b DESC,1은 a ASC이므로(2,3)이 먼저다.'],'정렬 위치 번호는 SELECT 목록 위치를 가리킨다.',ordered=True)

sqlq(10,'duplicate-multiplication','각 주문과 각 태그를 고객번호로 결합하면 id,tag 결과는?','SELECT O.id,G.tag FROM O JOIN G ON O.cid=G.cid ORDER BY O.id,G.tag',[T('O','id:NUMBER,cid:NUMBER',[(1,7),(2,7),(3,8)]),T('G','cid:NUMBER,tag:NUMBER',[(7,10),(7,20)])],O('ID,TAG',[(1,10),(1,20),(2,10),(2,20)]),W('(1, 10) / (2, 20)','매칭마다 임의 한 행만 붙였다.','(1, 10) / (1, 20) / (2, 10) / (2, 20) / (3, NULL)','INNER JOIN에는 미매칭 보존이 없다.','(1, 10) / (2, 10)','태그20 매칭을 누락했다.'),['cid7인 주문 두 행은 태그10·20과 각각 만나 네 쌍을 만든다.','cid8 주문3은 태그가 없어 제외한다.'],'조인 중복은 행 쌍 수로 설명한다.',ordered=True)
sqlq(10,'null-pair-filter','NULL 키가 있는 내부 조인의 집계 결과는?','SELECT COUNT(*) AS n FROM A JOIN B ON A.k=B.k',[T('A','k:NUMBER',[(1,),(None,),(None,)]),T('B','k:NUMBER',[(1,),(None,)])],O('N',[(1,)]),W('(3)','NULL 두 행을 오른쪽 NULL과 매칭했다고 셌다.','(0)','비NULL1끼리의 유효 매칭을 빠뜨렸다.','(6)','CROSS JOIN의 전체 조합 수다.'),['1=1인 한 쌍만 TRUE다.','NULL 등호 비교는 UNKNOWN이므로 나머지 쌍이 통과하지 않는다.'],'NULL 키의 등호 매칭과 원본 행 수를 구별한다.')
sqlq(10,'overlap-band','등급 구간의 양 끝을 포함한다. 급여20이 붙는 등급은?','SELECT E.id,G.grade FROM E JOIN G ON E.sal BETWEEN G.lo AND G.hi ORDER BY G.grade',[T('E','id:NUMBER,sal:NUMBER',[(1,20)]),T('G','grade:NUMBER,lo:NUMBER,hi:NUMBER',[(1,10,20),(2,20,30)])],O('ID,GRADE',[(1,1),(1,2)]),W('(1, 1)','두 번째 구간의 포함 하한20도 만족한다.','(1, 2)','첫 번째 구간의 포함 상한20도 만족한다.','0행','BETWEEN은 양끝을 포함하므로20이 배제되지 않는다.'),['20은10이상20이하이므로 grade1과 매칭된다.','20은20이상30이하이므로 grade2와도 매칭된다.'],'범위가 겹치면 한 행이 여러 구간에 매칭될 수 있다.',ordered=True)
sqlq(10,'cross-filter','모든 쌍 중 a<b만 선택한 결과는?','SELECT A.a,B.b FROM A CROSS JOIN B WHERE A.a<B.b ORDER BY A.a,B.b',[T('A','a:NUMBER',[(1,),(3,)]),T('B','b:NUMBER',[(2,),(3,)])],O('A,B',[(1,2),(1,3)]),W('(1, 2) / (1, 3) / (3, 3)','3<3은 FALSE다.','(1, 2) / (3, 3)','행 위치별로만 결합하는 조인이 아니다.','(1, 2) / (1, 3) / (3, 2) / (3, 3)','WHERE 필터를 적용하지 않았다.'),['데카르트 곱 네 쌍은(1,2),(1,3),(3,2),(3,3)이다.','부등식 TRUE인 앞의 두 쌍만 유지한다.'],'CROSS JOIN 뒤 WHERE는 전체 행 쌍을 조건으로 고른다.',ordered=True)
sqlq(10,'aggregate-after-join','주문별 여러 상세행을 붙여 고객별 수량을 합친 결과는?','SELECT O.cid,SUM(L.qty) AS qty FROM O JOIN L ON O.id=L.oid GROUP BY O.cid ORDER BY O.cid',[T('O','id:NUMBER,cid:NUMBER',[(1,7),(2,7),(3,8)]),T('L','oid:NUMBER,qty:NUMBER',[(1,2),(1,3),(2,1),(3,4)])],O('CID,QTY',[(7,6),(8,4)]),W('(7, 3) / (8, 1)','SUM 대신 상세 행 COUNT를 센 결과다.','(7, 5) / (8, 4)','고객7의 두 번째 주문 수량1을 빠뜨렸다.','(7, 10) / (8, 10)','고객별 그룹을 나누지 않았다.'),['고객7에 연결되는 수량은2,3,1이고 고객8은4다.','고객별 합계를 계산하여6과4를 반환한다.'],'조인 결과의 행을 먼저 만든 뒤 그룹별 집계 대상을 센다.',ordered=True)
sqlq(10,'two-key-matching','연도와 번호를 함께 비교한 내부 조인 결과는?','SELECT A.y,A.no,B.v FROM A JOIN B ON A.y=B.y AND A.no=B.no ORDER BY A.y',[T('A','y:NUMBER,no:NUMBER',[(2025,1),(2026,1)]),T('B','y:NUMBER,no:NUMBER,v:NUMBER',[(2025,1,10),(2026,2,20)])],O('Y,NO,V',[(2025,1,10)]),W('(2025, 1, 10) / (2026, 1, 10)','연도 조건을 무시했다.','(2025, 1, 10) / (2026, 1, 20)','번호 조건을 무시했다.','0행','두 키가 모두 일치하는2025년1번 쌍이 있다.'),['2025·1은 두 열 모두 일치한다.','2026·1은 B의2026·2와 번호가 달라 제외한다.'],'복합 업무 키는 모든 구성 열의 일치 조건을 확인한다.',ordered=True)
sqlq(10,'empty-cross','오른쪽 입력이 비어 있는 CROSS JOIN의 COUNT(*)는?','SELECT COUNT(*) AS n FROM A CROSS JOIN B',[T('A','id:NUMBER',[(1,),(2,)]),T('B','id:NUMBER',[])],O('N',[(0,)]),W('(2)','CROSS JOIN은 왼쪽 미매칭을 보존하지 않는다.','0행','집계 COUNT(*)는 빈 입력에서도0 한 행을 반환한다.','(NULL)','COUNT는 빈 집계 입력에서NULL이 아니라0이다.'),['가능한 행 쌍은2×0=0개다.','GROUP BY 없는 COUNT(*)는 그 빈 입력의 개수0을 한 행으로 출력한다.'],'조인 결과0행과 COUNT 결과0 한 행을 구별한다.')

outer=[T('C','id:NUMBER',[(1,),(2,),(3,)]),T('O','id:NUMBER,cid:NUMBER,paid:NUMBER',[(10,1,1),(11,1,0),(12,2,0)])]
sqlq(11,'on-paid-preserve','유료 주문만 ON에 넣은 LEFT JOIN의 결과는?','SELECT C.id,O.id FROM C LEFT JOIN O ON C.id=O.cid AND O.paid=1 ORDER BY C.id',outer,O('CID,OID',[(1,10),(2,None),(3,None)]),W('(1, 10)','미매칭 고객2,3 보존을 빠뜨렸다.','(1, 10) / (1, 11) / (2, 12) / (3, NULL)','ON의 paid 필터를 무시했다.','(1, 10) / (2, 12) / (3, NULL)','비유료 주문12를 매칭했다.'),['고객1은 주문10과 매칭하고 비유료11은 매칭되지 않는다.','고객2는 유료 매칭이 없으며 고객3은 주문 자체가 없다. 두 고객 모두 O열 NULL로 보존한다.'],'ON에서 오른쪽 조건을 걸면 왼쪽 미매칭 보존을 유지한다.',ordered=True)
sqlq(11,'where-paid-remove','같은 자료에서 paid 조건을 WHERE에 둔 결과는?','SELECT C.id,O.id FROM C LEFT JOIN O ON C.id=O.cid WHERE O.paid=1 ORDER BY C.id',outer,O('CID,OID',[(1,10)]),W('(1, 10) / (2, NULL) / (3, NULL)','WHERE가NULL 확장 행을 제거하는 효과를 빠뜨렸다.','(1, 10) / (1, 11)','주문11은 paid0이라 FALSE다.','(1, 10) / (3, NULL)','고객3의NULL=1은 UNKNOWN이라 제거된다.'),['LEFT JOIN 중간 결과는(1,10,1),(1,11,0),(2,12,0),(3,NULL,NULL)이다.','WHERE paid=1은 첫 행만 TRUE이고 나머지는 FALSE 또는 UNKNOWN이다.'],'WHERE는 이미 NULL 확장된 결과에도 적용된다.',ordered=True)
sqlq(11,'count-outer-null','고객마다 주문 행 수를 세는 두 COUNT의 결과는?','SELECT C.id,COUNT(*),COUNT(O.id) FROM C LEFT JOIN O ON C.id=O.cid GROUP BY C.id ORDER BY C.id',outer,O('CID,COUNT_STAR,COUNT_O_ID',[(1,2,2),(2,1,1),(3,1,0)]),W('(1, 2, 2) / (2, 1, 1) / (3, 0, 0)','COUNT(*)는 고객3의NULL 확장 행 한 개를 센다.','(1, 2, 2) / (2, 1, 1) / (3, 1, 1)','COUNT(O.id)는NULL을 제외한다.','(1, 1, 1) / (2, 1, 1) / (3, 1, 0)','고객1의 두 매칭 행을 하나로 줄이지 않는다.'),['고객1은 두 행,2는 한 행,3은NULL 확장 한 행을 가진다.','COUNT(*)는2,1,1; COUNT(O.id)는 비NULL만 세어2,1,0이다.'],'외부 조인 뒤 자식 수는 비NULL 자식 키를 세어야 한다.',ordered=True)
sqlq(11,'full-both-unmatched','FULL OUTER JOIN 결과를 공통 키 순으로 정렬하면?','SELECT A.k,B.k FROM A FULL OUTER JOIN B ON A.k=B.k ORDER BY COALESCE(A.k,B.k)',[T('A','k:NUMBER',[(1,),(2,)]),T('B','k:NUMBER',[(2,),(3,)])],O('A_K,B_K',[(1,None),(2,2),(None,3)]),W('(1, NULL) / (2, 2)','오른쪽 미매칭3을 빠뜨렸다.','(2, 2)','양쪽 미매칭 보존을 빠뜨렸다.','(1, 1) / (2, 2) / (3, 3)','없는 대응값을 실제 숫자로 꾸몄다.'),['키2끼리의 한 쌍을 만든다.','왼쪽1은 오른쪽NULL,오른쪽3은 왼쪽NULL로 확장하여 보존한다.'],'FULL JOIN은 양쪽 미매칭을 각각 반대편NULL로 확장한다.',ordered=True)
sqlq(11,'using-key-result','USING 공통 키를 반환하는 FULL JOIN 결과는?','SELECT k FROM A FULL OUTER JOIN B USING(k) ORDER BY k',[T('A','k:NUMBER',[(1,),(2,)]),T('B','k:NUMBER',[(2,),(3,)])],O('K',[(1,),(2,),(3,)]),W('(1) / (2) / (NULL)','오른쪽 미매칭의 공통 키3을NULL로 잘못 바꿨다.','(1) / (2) / (2) / (3)','매칭 키2를 두 개의 결과 행으로 중복 생성했다.','(2)','FULL의 미매칭 보존을 누락했다.'),['키2는 한 매칭 행,1과3은 각 미매칭 행이다.','USING의 공통 k는 각 보존된 키를 하나의 열로 표시한다.'],'USING 공통 키는 ON 조인의 개별 A.k와 동일하지 않을 수 있다.',ordered=True)
sqlq(11,'natural-extra-key','공통 열 k와 flag가 있는 NATURAL JOIN의 결과는?','SELECT k,flag FROM A NATURAL JOIN B ORDER BY k',[T('A','k:NUMBER,flag:NUMBER',[(1,0),(2,1)]),T('B','k:NUMBER,flag:NUMBER',[(1,1),(2,1)])],O('K,FLAG',[(2,1)]),W('(1, 0) / (2, 1)','공통flag 조건을 무시했다.','(1, 1) / (2, 1)','k만 비교하고 오른쪽flag를 취했다.','0행','k2·flag1은 두 열 모두 일치한다.'),['NATURAL은 k와flag를 모두 비교한다.','k1은flag 불일치, k2는두 열 일치로 한 행만 남는다.'],'NATURAL JOIN의 공통 열 전체를 먼저 확인한다.',ordered=True)
sqlq(11,'anti-exists-key','주문이 전혀 없는 고객을 오른쪽 비NULL 보장 키로 찾은 결과는?','SELECT C.id FROM C LEFT JOIN O ON C.id=O.cid WHERE O.id IS NULL ORDER BY C.id',outer,O('CID',[(3,)]),W('(2) / (3)','비유료 주문이 있는2도 주문 존재 자체는 있다.','(1) / (2)','주문이 있는 고객들을 골랐다.','(1) / (2) / (3)','WHERE를 적용하지 않았다.'),['고객1,2는 실제 주문id가 있는 매칭 행이다.','고객3만 O.id가NULL인 확장 행이므로 선택된다.'],'미매칭 판별은 실제 행에서 NULL이 되지 않는 자식 키로 한다.',ordered=True,constraints=['O.id는 입력의 모든 실제 행에서 비NULL이고 유일하다.'])

sqlq(12,'above-own-dept-average','각 부서 평균보다 급여가 큰 직원은?','SELECT e.id FROM E e WHERE e.sal>(SELECT AVG(x.sal) FROM E x WHERE x.d=e.d) ORDER BY e.id',[T('E','id:NUMBER,d:NUMBER,sal:NUMBER',[(1,1,10),(2,1,30),(3,2,50),(4,2,None)])],O('ID',[(2,)]),W('(2) / (3)','부서2 평균50과 같은50은 >를 만족하지 않는다.','(3)','전체 평균으로 비교하지 않는다.','(2) / (4)','NULL 급여 비교는TRUE가 아니다.'),['부서1 평균은20,부서2는NULL을 제외한50이다.','id1의10은작고,id2의30만크다. id3은동일,id4는UNKNOWN이다.'],'상관 조건이 평균의 집계 범위를 결정한다.',ordered=True)
sqlq(12,'exists-no-multiply','EXISTS를 사용한 고객 목록의 결과는?','SELECT C.id FROM C WHERE EXISTS(SELECT NULL FROM O WHERE O.cid=C.id) ORDER BY C.id',[T('C','id:NUMBER',[(1,),(2,)]),T('O','cid:NUMBER',[(1,),(1,)])],O('ID',[(1,)]),W('(1) / (1)','EXISTS는두 매칭 주문이 있어도 바깥 고객을 증식시키지 않는다.','0행','SELECT NULL도행이 존재하면 EXISTS는TRUE다.','(1) / (2)','고객2는매칭 주문이 없다.'),['고객1의상관 서브쿼리는2행이지만 존재판정은TRUE 하나다.','고객2는0행으로FALSE다.'],'EXISTS의행 존재와 JOIN의매칭 개수는 다르다.',ordered=True)
sqlq(12,'null-safe-not-exists','NULL이 섞인 제외표에서 NOT EXISTS 등호 조건으로 남는 값은?','SELECT A.k FROM A WHERE NOT EXISTS(SELECT 1 FROM B WHERE B.k=A.k) ORDER BY A.k NULLS LAST',[T('A','k:NUMBER',[(1,),(2,),(None,)]),T('B','k:NUMBER',[(1,),(None,)])],O('K',[(2,),(None,)]),W('(2)','NULL끼리등호가TRUE라고 가정했다.','0행','NOT IN의NULL 효과를NOT EXISTS에 그대로 적용했다.','(1) / (2) / (NULL)','일치하는1의존재를무시했다.'),['A1은B1과매칭이있어제외한다.','A2와A NULL은등호TRUE인B행이없어NOT EXISTS를통과한다.'],'NOT EXISTS의NULL 결과는내부비교조건을직접평가한다.',ordered=True)
sqlq(12,'not-in-empty','제외표 B가 비어 있을 때 NOT IN 결과는?','SELECT k FROM A WHERE k NOT IN(SELECT k FROM B) ORDER BY k NULLS LAST',[T('A','k:NUMBER',[(1,),(None,)]),T('B','k:NUMBER',[])],O('K',[(1,),(None,)]),W('(1)','빈집합의NOT IN은NULL왼쪽값도TRUE가된다.','0행','빈IN과빈NOT IN을반대로읽었다.','(NULL)','비NULL1도제외대상이없다.'),['서브쿼리가비어비교해야할원소가없다.','NOT IN빈집합은TRUE이므로두행모두남는다.'],'빈집합과NULL원소를포함한집합을구별한다.',ordered=True)
sqlq(12,'scalar-aggregate-empty','빈 조건의 AVG 스칼라 값을 조회하면?','SELECT (SELECT AVG(v) FROM T WHERE v>100) AS a FROM dual',[T('T','v:NUMBER',[(10,),(20,)])],O('A',[(None,)]),W('(0)','AVG의빈입력결과는0이아니다.','0행','바깥dual 한행은남아NULL값을반환한다.','(15)','v>100필터를적용하지않은평균이다.'),['v>100을만족하는입력은0행이다.','GROUP BY없는AVG는NULL 한행을만들고바깥스칼라가그NULL을출력한다.'],'빈집계값과바깥결과행의존재를구별한다.')
sqlq(12,'any-null-mixed','NULL이 섞인 ANY 비교를 통과하는 값은?','SELECT x FROM A WHERE x>ANY(SELECT v FROM B) ORDER BY x',[T('A','x:NUMBER',[(1,),(5,),(10,)]),T('B','v:NUMBER',[(3,),(None,)])],O('X',[(5,),(10,)]),W('0행','ANY는하나라도TRUE면UNKNOWN이함께있어도TRUE다.','(10)','5>3도TRUE다.','(1) / (5) / (10)','1>3은FALSE이고1>NULL은UNKNOWN이라통과하지못한다.'),['1은FALSE OR UNKNOWN으로UNKNOWN이다.','5와10은>3이TRUE이므로ANY전체가TRUE다.'],'ANY에서는참인비교하나가전체를참으로만든다.',ordered=True)
sqlq(12,'all-empty','빈 집합에 대한 >ALL의 결과는?','SELECT x FROM A WHERE x>ALL(SELECT v FROM B) ORDER BY x',[T('A','x:NUMBER',[(1,),(2,)]),T('B','v:NUMBER',[])],O('X',[(1,),(2,)]),W('0행','빈집합ANY와ALL의차이를구별해야한다.','(2)','임의기준값을만들어비교하지않는다.','(NULL)','원본값을NULL로치환하지않는다.'),['B는0행이므로반례가되는비교대상이없다.','ALL빈집합조건은TRUE로두행을보존한다.'],'빈집합ALL은TRUE,ANY는FALSE라는경계조건을확인한다.',ordered=True)
sqlq(12,'tuple-in','두 열을 함께 IN 비교하는 결과는?','SELECT y,no FROM A WHERE (y,no) IN(SELECT y,no FROM B) ORDER BY y,no',[T('A','y:NUMBER,no:NUMBER',[(2025,1),(2025,2),(2026,1)]),T('B','y:NUMBER,no:NUMBER',[(2025,1),(2026,2)])],O('Y,NO',[(2025,1)]),W('(2025, 1) / (2025, 2) / (2026, 1)','각열을독립목록으로비교하면원래없는조합을허용한다.','(2025, 1) / (2026, 1)','no만비교했다.','(2025, 2)','일치하지않는쌍이다.'),['각행의(y,no)쌍전체를B의쌍과비교한다.','2025·1만동일한쌍이며다른두쌍은없다.'],'다중열IN은열별독립소속이아니라행값의소속이다.',ordered=True)

setdata=[T('A','v:NUMBER',[(1,),(1,),(2,),(None,)]),T('B','v:NUMBER',[(2,),(3,),(None,)])]
sqlq(13,'union-null-combined','두 목록을 UNION으로 합친 결과는?','SELECT v FROM A UNION SELECT v FROM B',setdata,O('V',[(1,),(2,),(3,),(None,)]),W('(1) / (1) / (2) / (2) / (3) / (NULL) / (NULL)','UNION ALL결과다.','(1) / (2) / (3)','NULL행자체를제거하지않는다.','(2) / (NULL)','INTERSECT결과다.'),['양쪽행을모은뒤1,2,NULL의중복을각하나로줄인다.','서로다른행1,2,3,NULL이남는다. 순서는지정되지않았다.'],'UNION은NULL도보존하되같은행의중복을제거한다.')
sqlq(13,'all-count','UNION ALL 결과를 바깥에서 세면 두 COUNT는?','SELECT COUNT(*),COUNT(v) FROM (SELECT v FROM A UNION ALL SELECT v FROM B)',setdata,O('COUNT_STAR,COUNT_V',[(7,5)]),W('(4, 3)','UNION처럼중복을제거했다.','(7, 7)','COUNT(v)는NULL두행을제외한다.','(5, 5)','COUNT(*)에서도NULL을빼면안된다.'),['ALL은입력4행과3행을모두유지하여7행이다.','비NULL은A3행+B2행=5행이다.'],'집합중복보존과COUNT의NULL제외를독립적으로적용한다.')
sqlq(13,'intersection-two-columns','두 열 행 전체의 공통 집합은?','SELECT a,b FROM X INTERSECT SELECT a,b FROM Y',[T('X','a:NUMBER,b:NUMBER',[(1,10),(1,20),(2,None)]),T('Y','a:NUMBER,b:NUMBER',[(1,10),(2,20),(2,None)])],O('A,B',[(1,10),(2,None)]),W('(1, 10) / (1, 20) / (2, NULL)','첫열만같다고모두공통행은아니다.','(1, 10)','집합연산에서NULL포함동일행도공통이다.','(1, 20) / (2, 20)','공통되지않은행들이다.'),['(1,10)은양쪽에있고(1,20)은Y에없다.','(2,NULL)은양쪽에있으므로유지한다.'],'집합연산의중복·공통판정은선택열전체로한다.')
sqlq(13,'minus-dedup','구매자 A 중 제외자 B를 뺀 결과는?','SELECT v FROM A MINUS SELECT v FROM B',setdata,O('V',[(1,)]),W('(1) / (1)','MINUS는남은중복도제거한다.','(1) / (NULL)','NULL은B에도있어제외된다.','(3)','B MINUS A의방향에해당한다.'),['A의2와NULL은B에있어제거한다.','1두행은한개의서로다른행으로반환한다.'],'MINUS는왼쪽차집합이며결과중복을제거한다.')
sqlq(13,'parenthesized-difference','괄호로 B와 C를 먼저 합집합한 뒤 제외한다. 결과는?','SELECT v FROM A MINUS SELECT v FROM (SELECT v FROM B UNION SELECT v FROM C)',[T('A','v:NUMBER',[(1,),(2,),(3,)]),T('B','v:NUMBER',[(2,)]),T('C','v:NUMBER',[(3,),(4,)])],O('V',[(1,)]),W('(1) / (3) / (4)','A MINUS B후C UNION을한경우와혼동했다.','(1) / (4)','오른쪽에만있는4를왼쪽차집합에추가하지않는다.','0행','A의1은제외목록에없다.'),['괄호안B UNION C는2,3,4다.','A의1,2,3에서2,3을제외하여1만남는다.'],'괄호가집합연산의평가대상을명시한다.')
sqlq(13,'difference-count-empty','자기 자신을 뺀 집합의 바깥 COUNT는?','SELECT COUNT(*) FROM (SELECT v FROM A MINUS SELECT v FROM A)',[T('A','v:NUMBER',[(1,),(None,)])],O('COUNT_STAR',[(0,)]),W('0행','바깥COUNT는빈입력도0한행을낸다.','(1)','NULL행도집합상같은행으로제외된다.','(2)','자기차집합은모든행이제거된다.'),['1과NULL모두오른쪽에동일행이있어차집합은빈결과다.','바깥COUNT(*)가0을한행으로출력한다.'],'집합연산결과행수와그개수를출력하는행수를구분한다.')

sqlq(14,'rollup-original-null','원본에 NULL 그룹이 있는 ROLLUP의 결과는?','SELECT d,SUM(v),GROUPING(d) FROM T GROUP BY ROLLUP(d)',[T('T','d:NUMBER,v:NUMBER',[(1,10),(None,5)])],O('D,SUM_V,GROUPING_D',[(1,10,0),(None,5,0),(None,15,1)]),W('(1, 10, 0) / (NULL, 15, 1)','원본 NULL 그룹의 집계값5를 누락했다.','(1, 10, 0) / (NULL, 20, 1)','NULL원본을전체합계에서중복계산했다.','(1, 10, 1) / (NULL, 5, 1) / (NULL, 15, 0)','GROUPING표시를뒤집었다.'),['d1상세합계10과dNULL상세합계5는GROUPING0이다.','전체합계15는d가집계로제외되어GROUPING1이다.'],'NULL값모양만으로소계행을판별할수없다.')
sqlq(14,'rollup-two-keys','ROLLUP(d,t)의 결과에서 각 소계가 포함되는 형태는?','SELECT d,t,SUM(v) FROM X GROUP BY ROLLUP(d,t)',[T('X','d:NUMBER,t:NUMBER,v:NUMBER',[(1,1,10),(1,2,20)])],O('D,T,SUM_V',[(1,1,10),(1,2,20),(1,None,30),(None,None,30)]),W('(1, 1, 10) / (1, 2, 20) / (NULL, 1, 10) / (NULL, 2, 20) / (NULL, NULL, 30)','t단독소계는ROLLUP(d,t)에없다.','(1, 1, 10) / (1, 2, 20)','소계와전체합계를누락했다.','(1, NULL, 30) / (NULL, NULL, 30)','상세그룹을누락했다.'),['상세(d,t)두그룹은10과20이다.','d단독소계30,전체합계30을추가한다.'],'ROLLUP(a,b)는(a,b),(a),()를생성한다.')
sqlq(14,'cube-cross-subtotals','CUBE에서 d별·t별 소계와 전체를 모두 만든 행 수는?','SELECT COUNT(*) FROM (SELECT d,t,SUM(v) FROM X GROUP BY CUBE(d,t))',[T('X','d:NUMBER,t:NUMBER,v:NUMBER',[(1,1,10),(1,2,20)])],O('COUNT_STAR',[(6,)]),W('(4)','두키의그룹수준4개와실제결과행수는다르다.','(5)','상세2+d1+t2+전체1에서하나를빠뜨렸다.','(8)','각수준마다항상입력2행이되는것은아니다.'),['(d,t)상세2행,(d)1행,(t)2행,()1행이다.','합계2+1+2+1=6행이다.'],'그룹수준수와각수준에존재하는그룹수를구별한다.')
sqlq(14,'chosen-grouping-sets','선택한 GROUPING SETS의 결과는?','SELECT t,SUM(v) FROM X GROUP BY GROUPING SETS((t),())',[T('X','d:NUMBER,t:NUMBER,v:NUMBER',[(1,1,10),(2,1,20),(2,2,5)])],O('T,SUM_V',[(1,30),(2,5),(None,35)]),W('(1, 10) / (1, 20) / (2, 5)','같은 t1의 두 입력을 집계하지 않았다.','(1, 10) / (2, 25) / (NULL, 35)','t가 아니라 d로 묶은 집계값이다.','(1, 30) / (2, 5)','전체 합계 수준()을 빠뜨렸다.'),['선택한키는t뿐이므로t1합계30,t2합계5다.','부서 d는 그룹 키에 없으므로 부서를 가로질러 합친다. 전체 합계는 35다.'],'GROUPING SETS에없는상세그룹은생성하지않는다.')
sqlq(14,'having-total-only','GROUPING을 HAVING에서 검사하면 무엇이 남는가?','SELECT d,SUM(v) FROM X GROUP BY ROLLUP(d) HAVING GROUPING(d)=1',[T('X','d:NUMBER,v:NUMBER',[(1,10),(None,7)])],O('D,SUM_V',[(None,17)]),W('(NULL, 7) / (NULL, 17)','GROUPING1은원본NULL그룹을제외한다.','(1, 10)','상세그룹은GROUPING0이다.','(NULL, 7)','원본NULL과전체합계를바꾸어판단했다.'),['상세d1=10,상세dNULL=7,전체=17이생성된다.','GROUPING(d)=1은전체합계행만TRUE다.'],'소계필터는IS NULL보다GROUPING으로의도를명시한다.')
sqlq(14,'repeated-sets','같은 그룹을 GROUPING SETS에 두 번 명시한 결과는?','SELECT d,SUM(v) FROM X GROUP BY GROUPING SETS((d),(d))',[T('X','d:NUMBER,v:NUMBER',[(1,10),(1,20)])],O('D,SUM_V',[(1,30),(1,30)]),W('(1, 30)','중복grouping set을자동DISTINCT처리한다고가정했다.','(1, 60)','두수준의합계를한행으로재집계하지않는다.','(NULL, 30)','빈그룹전체합계를요청하지않았다.'),['각(d)수준은d1합계30한행을만든다.','동일수준을두번요청했으므로같은결과행이두번나온다.'],'GROUPING SETS의수준중복을의도하지않았다면목록을점검한다.')

rankdata=[T('T','id:NUMBER,d:NUMBER,v:NUMBER',[(1,1,90),(2,1,90),(3,1,70),(4,2,80)])]
sqlq(15,'ranks-side-by-side','부서별 RANK와 DENSE_RANK를 함께 표시한 결과는?','SELECT id,RANK() OVER(PARTITION BY d ORDER BY v DESC) AS r,DENSE_RANK() OVER(PARTITION BY d ORDER BY v DESC) AS dr FROM T ORDER BY id',rankdata,O('ID,R,DR',[(1,1,1),(2,1,1),(3,3,2),(4,1,1)]),W('(1, 1, 1) / (2, 2, 2) / (3, 3, 3) / (4, 1, 1)','동점들을별도순위로처리했다.','(1, 1, 1) / (2, 1, 1) / (3, 2, 3) / (4, 1, 1)','RANK와DENSE_RANK의간격을뒤집었다.','(1, 1, 1) / (2, 1, 1) / (3, 4, 3) / (4, 3, 2)','부서파티션분리를누락했다.'),['d1의90,90,70은RANK1,1,3/DENSE1,1,2다.','d2는한행이므로두순위모두1이다.'],'동점규칙과파티션초기화를각각적용한다.',ordered=True)
sqlq(15,'unique-number-with-tie-key','id를 보조 키로 쓴 ROW_NUMBER 결과는?','SELECT id,ROW_NUMBER() OVER(PARTITION BY d ORDER BY v DESC,id DESC) AS rn FROM T ORDER BY id',rankdata,O('ID,RN',[(1,2),(2,1),(3,3),(4,1)]),W('(1, 1) / (2, 2) / (3, 3) / (4, 1)','동점idDESC를ASC로읽었다.','(1, 1) / (2, 1) / (3, 3) / (4, 1)','ROW_NUMBER는동점도서로다른번호다.','(1, 2) / (2, 1) / (3, 4) / (4, 3)','파티션을구별하지않았다.'),['d1정렬은id2,id1,id3이라번호1,2,3이다.','출력id순으로다시배열하면id1의번호2가먼저보인다.'],'계산순서와표시순서를구별한다.',ordered=True)
sqlq(15,'partition-sum-maintains-rows','부서합계를 각 직원 옆에 붙인 결과는?','SELECT id,SUM(v) OVER(PARTITION BY d) AS total FROM T ORDER BY id',rankdata,O('ID,TOTAL',[(1,250),(2,250),(3,250),(4,80)]),W('(1, 250) / (2, 80)','집계로부서당한행으로축약하지않는다.','(1, 90) / (2, 180) / (3, 250) / (4, 80)','ORDER BY없는파티션합계를누적합으로오해했다.','(1, 330) / (2, 330) / (3, 330) / (4, 330)','파티션d를무시했다.'),['d1합계90+90+70=250,d2합계80이다.','윈도우함수는원래네행을유지해각파티션합계를반복붙인다.'],'분석집계는행유지,그룹집계는그룹당요약이다.',ordered=True)
sqlq(15,'lag-null-default','이전 행 값이 NULL일 때 LAG 기본값은 어떻게 적용되는가?','SELECT id,LAG(v,1,0) OVER(ORDER BY id) AS prev FROM T ORDER BY id',[T('T','id:NUMBER,v:NUMBER',[(1,10),(2,None),(3,30)])],O('ID,PREV',[(1,0),(2,10),(3,None)]),W('(1, 0) / (2, 10) / (3, 0)','존재하는이전행의NULL을기본값으로치환하지않는다.','(1, 10) / (2, NULL) / (3, 30)','현재행값을반환했다.','(1, NULL) / (2, 30) / (3, 0)','LEAD방향으로읽었다.'),['id1은이전행이없어기본0이다.','id2이전은10,id3이전은실제NULL값이므로NULL이다.'],'LAG기본값은행부재를다루며NULL치환과다르다.',ordered=True)
sqlq(15,'lead-gap-not-id','id가 연속하지 않는 데이터에서 LEAD 결과는?','SELECT id,LEAD(v,1,-1) OVER(ORDER BY id) AS next_v FROM T ORDER BY id',[T('T','id:NUMBER,v:NUMBER',[(10,5),(30,7),(80,9)])],O('ID,NEXT_V',[(10,7),(30,9),(80,-1)]),W('(10, -1) / (30, -1) / (80, -1)','id+1행을찾는것이아니라다음정렬행을본다.','(10, 5) / (30, 7) / (80, 9)','현재값을그대로반환했다.','(10, -1) / (30, 5) / (80, 7)','LAG의이전방향이다.'),['정렬된위치는id10,30,80이다.','다음행값은7,9이며마지막 행은 다음 행이 없어 -1이다.'],'오프셋은키값의차이가아니라정렬된행의위치차이다.',ordered=True)
sqlq(15,'ntile-unequal','5행을 NTILE(2)로 나눈 결과는?','SELECT id,NTILE(2) OVER(ORDER BY id) AS bucket FROM T ORDER BY id',[T('T','id:NUMBER',[(1,),(2,),(3,),(4,),(5,)])],O('ID,BUCKET',[(1,1),(2,1),(3,1),(4,2),(5,2)]),W('(1, 1) / (2, 1) / (3, 2) / (4, 2) / (5, 2)','나머지행은작은번호버킷부터배분된다.','(1, 1) / (2, 2) / (3, 1) / (4, 2) / (5, 1)','왕복순환배분이아니다.','(1, 1) / (2, 2) / (3, 3) / (4, 4) / (5, 5)','ROW_NUMBER와혼동했다.'),['5÷2는몫2,나머지1이다.','첫버킷에한행을더주어3행,두번째버킷2행을연속배분한다.'],'NTILE의잔여행은앞번호버킷부터한개씩배분한다.',ordered=True)

frame=[T('T','id:NUMBER,k:NUMBER,v:NUMBER',[(1,1,10),(2,1,20),(3,3,5)])]
sqlq(16,'range-peer-cumulative','기본 RANGE 누적합에서 동점 키의 결과는?','SELECT id,SUM(v) OVER(ORDER BY k) AS s FROM T ORDER BY id',frame,O('ID,S',[(1,30),(2,30),(3,35)]),W('(1, 10) / (2, 30) / (3, 35)','물리ROWS프레임으로읽었다.','(1, 35) / (2, 35) / (3, 35)','끝이현재정렬값이므로미래k3은처음두행에포함되지않는다.','(1, 10) / (2, 20) / (3, 5)','누적범위를적용하지않았다.'),['k1현재값의RANGE는동료두행10·20을모두포함한다.','k3범위에는앞선두행과5가포함되어35다.'],'SUM처럼 프레임을 지원하는 함수에서 ORDER BY가 있고 프레임 절을 생략하면 RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW다.',ordered=True)
sqlq(16,'rows-two-window','현재와 바로 앞 행의 이동합계는?','SELECT id,SUM(v) OVER(ORDER BY id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS s FROM T ORDER BY id',frame,O('ID,S',[(1,10),(2,30),(3,25)]),W('(1, 10) / (2, 30) / (3, 35)','마지막에서두행전10까지누적했다.','(1, 30) / (2, 25) / (3, 5)','현재와다음행의창이다.','(1, 0) / (2, 10) / (3, 20)','현재행을빼고앞행만읽었다.'),['첫창은10만,둘째창은10+20이다.','셋째창은바로앞20과현재5이므로25다.'],'ROWS오프셋창에서는범위밖의오래된행을빼야한다.',ordered=True)
sqlq(16,'range-value-distance','키 값의 거리1 이내 앞쪽 RANGE 합계는?','SELECT id,SUM(v) OVER(ORDER BY k RANGE BETWEEN 1 PRECEDING AND CURRENT ROW) AS s FROM T ORDER BY id',frame,O('ID,S',[(1,30),(2,30),(3,5)]),W('(1, 10) / (2, 30) / (3, 25)','앞한행기준ROWS와혼동했다.','(1, 30) / (2, 30) / (3, 35)','k3의하한2보다작은k1을포함했다.','(1, 10) / (2, 20) / (3, 5)','동점k1둘을함께포함해야한다.'),['k1의범위는[0,1]이므로두행합30이다.','k3의범위는[2,3]이고k1행들은제외되어5만남는다.'],'RANGE오프셋은키값의거리이며행개수가아니다.',ordered=True)
sqlq(16,'last-value-full','전체 파티션 프레임의 LAST_VALUE 결과는?','SELECT id,LAST_VALUE(v) OVER(ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_v FROM T ORDER BY id',frame,O('ID,LAST_V',[(1,5),(2,5),(3,5)]),W('(1, 10) / (2, 20) / (3, 5)','CURRENT ROW로끝나는프레임처럼읽었다.','(1, 10) / (2, 10) / (3, 10)','FIRST_VALUE방향이다.','(1, 35) / (2, 35) / (3, 35)','합계를요청하지않았다.'),['모든현재행의창이파티션첫행부터마지막행까지열린다.','id정렬마지막은id3값5이므로각행에5를반환한다.'],'LAST_VALUE의대상은각프레임의마지막행이다.',ordered=True)
sqlq(16,'future-count-boundary','현재 이후 한 행부터 끝까지의 COUNT(*)는?','SELECT id,COUNT(*) OVER(ORDER BY id ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING) AS n FROM T ORDER BY id',frame,O('ID,N',[(1,2),(2,1),(3,0)]),W('(1, 3) / (2, 2) / (3, 1)','현재행을포함하지않는시작경계를놓쳤다.','(1, 2) / (2, 1) / (3, NULL)','빈프레임COUNT는0이다.','(1, 0) / (2, 1) / (3, 2)','이전방향으로계산했다.'),['id1뒤에는두행,id2뒤에는한행이다.','마지막id3뒤는빈프레임이므로COUNT(*)0이다.'],'빈프레임COUNT0과SUM의NULL을구분한다.',ordered=True)
sqlq(16,'partition-boundaries','파티션별 이동합계에서 다른 부서 앞 행이 포함되는가?','SELECT id,SUM(v) OVER(PARTITION BY d ORDER BY id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS s FROM T ORDER BY id',[T('T','id:NUMBER,d:NUMBER,v:NUMBER',[(1,1,10),(2,1,20),(3,2,100),(4,2,5)])],O('ID,S',[(1,10),(2,30),(3,100),(4,105)]),W('(1, 10) / (2, 30) / (3, 120) / (4, 105)','id3의창이이전부서로넘어가지않는다.','(1, 30) / (2, 30) / (3, 105) / (4, 105)','전체파티션합계가아니다.','(1, 10) / (2, 20) / (3, 100) / (4, 5)','앞행을포함하는프레임을무시했다.'),['d1과d2를먼저나눠별개의정렬행목록을만든다.','각파티션첫행은자기값만포함하고둘째는두값합이다.'],'프레임은PARTITION경계를넘지않는다.',ordered=True)

topdata=[T('T','id:NUMBER,score:NUMBER',[(1,100),(2,90),(3,90),(4,80)])]
sqlq(17,'fetch-only-key','상위 두 행을 고유 키까지 정렬해 선택한 결과는?','SELECT id FROM T ORDER BY score DESC,id DESC FETCH FIRST 2 ROWS ONLY',topdata,O('ID',[(1,),(3,)]),W('(1) / (2)','동점 보조 키 id DESC를 거꾸로 읽었다.','(1) / (2) / (3)','ONLY는 추가 동점 행을 포함하지 않는다.','(3) / (2)','100점인 id1이 가장 먼저다.'),['점수 DESC, id DESC 순서는 1,3,2,4다.','그 순서에서 두 행만 선택한다.'],'정확한 행 수 제한에서도 동점 보조 정렬 키가 중요하다.',ordered=True)
sqlq(17,'fetch-ties-last-score','점수만 정렬하고 두 행까지 WITH TIES로 선택한 결과는?','SELECT id FROM T ORDER BY score DESC FETCH FIRST 2 ROWS WITH TIES',topdata,O('ID',[(1,),(2,),(3,)]),W('(1) / (2)','마지막 선택 점수90의 추가 동점 id3을 빠뜨렸다.','(1) / (2) / (3) / (4)','80점은 경계 점수90과 동점이 아니다.','(2) / (3)','첫100점 행도 상위 선택에 포함된다.'),['첫 행 점수100,두 번째 행의 점수는90이다.','경계90점과 같은 두 행 모두 포함해 총3행이다. 90점 두 행 사이 표시 순서는 보장하지 않는다.'],'WITH TIES는 마지막 제한 행의 정렬 키 동점을 포함한다.')
sqlq(17,'offset-page','첫 두 행을 건너뛴 다음 한 행의 결과는?','SELECT id FROM T ORDER BY score DESC,id OFFSET 2 ROWS FETCH NEXT 1 ROW ONLY',topdata,O('ID',[(3,)]),W('(2)','OFFSET2는 두 행을 건너뛴다.','(1)','OFFSET을 적용하지 않았다.','(4)','세 행을 건너뛴 경우다.'),['정렬 순서는 id1,2,3,4다.','앞 두 행1,2를 건너뛰고 다음 한 행3을 반환한다.'],'OFFSET은 0기준 건너뛸 행 수다.',ordered=True)
sqlq(17,'per-dept-top','부서별 최고 점수 동점자를 모두 구한 결과는?','SELECT id FROM (SELECT id,RANK() OVER(PARTITION BY d ORDER BY v DESC) AS r FROM T) WHERE r=1 ORDER BY id',rankdata,O('ID',[(1,),(2,),(4,)]),W('(1) / (4)','부서1 최고 점수 동점 id2를 빠뜨렸다.','(1) / (2)','부서2의 독립1위 id4가 있다.','(1) / (2) / (3) / (4)','70점 id3의 순위3은 제외된다.'),['부서1의 순위는 id1=1,id2=1,id3=3이다. 부서2는 id4=1이다.','바깥 WHERE r=1로 세 행을 선택한다.'],'분석 결과 필터는 바깥 쿼리에서 수행할 수 있다.',ordered=True)
sqlq(17,'rownum-lower-bound-empty','단순 ROWNUM 하한 조건 결과의 COUNT는?','SELECT COUNT(*) FROM T WHERE ROWNUM>1',topdata,O('COUNT_STAR',[(0,)]),W('(3)','첫 행만 건너뛰는 조건으로 읽었다.','(4)','조건을 무시했다.','0행','COUNT는 빈 입력에서도0 한 행을 출력한다.'),['첫 통과 행 후보의 ROWNUM은1이고1>1은 거짓이다.','통과 행이 생기지 않아 끝까지 빈 입력,COUNT0이다.'],'같은 블록에서 ROWNUM>1 또는 ROWNUM>=2처럼1을 제외하는 단순 하한을 두면 첫 통과 행이 생기지 않는다.')
sqlq(17,'rank-versus-dense-cut','상위2순위 RANK 조건에서 반환되는 행은?','SELECT id FROM (SELECT id,RANK() OVER(ORDER BY score DESC) AS r FROM T) WHERE r<=2 ORDER BY id',[T('T','id:NUMBER,score:NUMBER',[(1,100),(2,100),(3,90),(4,80)])],O('ID',[(1,),(2,)]),W('(1) / (2) / (3)','DENSE_RANK<=2의 결과와 다르다.','(1)','동점 두 명 모두1위다.','(1) / (2) / (3) / (4)','순위 제한을 적용하지 않았다.'),['100점 두 행은1위이고90점은3위,80점은4위다.','RANK<=2에는1위 두 행만 포함된다.'],'순위 번호 상한과 서로 다른 점수 종류 수를 구분한다.',ordered=True)

hier=[T('N','id:NUMBER,pid:NUMBER,v:NUMBER',[(1,None,10),(2,1,20),(3,1,30),(4,2,40)])]
sqlq(18,'hierarchy-levels','루트에서 하향 탐색한 id와 LEVEL의 집합은?','SELECT id,LEVEL AS depth FROM N START WITH pid IS NULL CONNECT BY PRIOR id=pid',hier,O('ID,DEPTH',[(1,1),(2,2),(4,3),(3,2)]),W('(1, 0) / (2, 1) / (3, 1) / (4, 2)','LEVEL의 시작은0이 아니라1이다.','(1, 1) / (2, 2) / (3, 3) / (4, 4)','표시 행 번호와 계층 깊이를 혼동했다.','(1, 1)','CONNECT BY로 자손을 계속 탐색한다.'),['pid NULL인 id1을 루트로 LEVEL1을 준다.','자식2,3은 LEVEL2이고2의 자식4는 LEVEL3이다.'],'LEVEL은 각 경로의 부모에서1씩 증가한다.')
sqlq(18,'self-manager-name','상사 없는 직원도 남기는 셀프 조인 결과는?','SELECT e.id,m.id AS manager FROM N e LEFT JOIN N m ON e.pid=m.id ORDER BY e.id',hier,O('ID,MANAGER',[(1,None),(2,1),(3,1),(4,2)]),W('(2, 1) / (3, 1) / (4, 2)','LEFT가 보존하는 루트 직원1을 빠뜨렸다.','(1, 2) / (1, 3) / (2, 4)','직원과 상사 역할을 뒤집었다.','(1, NULL) / (2, 1) / (3, 1) / (4, 1)','id4의 직속 상사는2이지 최상위1이 아니다.'),['직원 e의 pid를 상사 m의 id에 맞춘다.','pid NULL인 e1은 매칭 없이 보존하고 나머지는 직속 상사 한 행을 붙인다.'],'셀프 조인의 별칭은 역할을 구분하며 직접 관계 한 단계를 표현한다.',ordered=True)
sqlq(18,'subtree-start','START WITH id=2에서 시작한 부분 트리 결과는?','SELECT id,LEVEL AS depth FROM N START WITH id=2 CONNECT BY PRIOR id=pid',hier,O('ID,DEPTH',[(2,1),(4,2)]),W('(2, 2) / (4, 3)','선택한 시작 행이 이번 질의의 루트이므로 LEVEL1부터다.','(1, 1) / (2, 2) / (4, 3)','id1은 START WITH 조건을 만족하지 않는다.','(2, 1) / (3, 1) / (4, 2)','id3은 id2의 자손이 아니다.'),['시작 집합은 id2 한 행이다. 이 질의에서는 LEVEL1이다.','id2의 자식4만 다음 단계에 연결된다.'],'START WITH가 달라지면 질의의 루트와 상대 깊이도 달라진다.')
sqlq(18,'ancestor-direction','id4에서 부모 방향으로 올라가는 결과는?','SELECT id,LEVEL AS depth FROM N START WITH id=4 CONNECT BY PRIOR pid=id',hier,O('ID,DEPTH',[(4,1),(2,2),(1,3)]),W('(4, 1)','PRIOR pid=id는 부모 방향의 연결을 계속 찾는다.','(1, 1) / (2, 2) / (4, 3)','시작 행과 진행 방향을 뒤집었다.','(4, 1) / (2, 2) / (3, 3) / (1, 4)','형제3은 부모 경로에 속하지 않는다.'),['현재4의 pid2를 다음 후보 id2와 맞춘다.','현재2의 pid1로 id1을 찾고 그 pidNULL에서 더 연결되지 않는다.'],'PRIOR가 적용되는 식을 바꾸면 탐색 방향이 바뀔 수 있다.')
sqlq(18,'where-after-path','계층을 만든 뒤 WHERE로 id2만 제외하면 id4는 남는가?','SELECT id,LEVEL AS depth FROM N WHERE id<>2 START WITH id=1 CONNECT BY PRIOR id=pid',hier,O('ID,DEPTH',[(1,1),(4,3),(3,2)]),W('(1, 1) / (3, 2)','WHERE의 결과 행 필터를 경로 가지치기로 읽었다.','(1, 1) / (4, 2) / (3, 2)','행2 제거가 id4의 원래 계층 LEVEL을 다시 계산하지 않는다.','(4, 1) / (3, 1)','각 생존 행을 새 루트로 만들지 않는다.'),['CONNECT BY는1→2→4와1→3 경로를 만든다.','후속 WHERE가 id2 행만 제거하므로 id4는 LEVEL3으로 남는다.'],'계층 결과 필터와 관계 확장 조건의 위치는 서로 다르다.')
sqlq(18,'leaf-flags','CONNECT_BY_ISLEAF를 표시한 결과는?','SELECT id,CONNECT_BY_ISLEAF AS leaf FROM N START WITH pid IS NULL CONNECT BY PRIOR id=pid',hier,O('ID,LEAF',[(1,0),(2,0),(4,1),(3,1)]),W('(1, 1) / (2, 0) / (3, 0) / (4, 0)','루트 여부와 잎 여부는 다르다.','(1, 0) / (2, 1) / (3, 1) / (4, 1)','id2에는 자식4가 있어 잎이 아니다.','(1, 1) / (2, 2) / (3, 2) / (4, 3)','그 값들은 LEVEL이며 잎 표시0/1과 다르다.'),['현재 CONNECT BY 관계에서1의 자식은2,3이고2의 자식은4다.','자식이 없는3,4만 leaf1이다.'],'잎 여부는 이번 계층 조건으로 확장할 자식이 있는지 판단한다.')

pivot=[T('T','shop:NUMBER,mon:NUMBER,amt:NUMBER',[(1,1,10),(1,1,5),(1,2,20),(2,1,7)])]
sqlq(19,'pivot-sum-groups','월을 열로 펼친 SUM PIVOT 결과는?','SELECT shop,m1,m2 FROM T PIVOT(SUM(amt) FOR mon IN(1 AS m1,2 AS m2)) ORDER BY shop',pivot,O('SHOP,M1,M2',[(1,15,20),(2,7,None)]),W('(1, 10, 20) / (2, 7, NULL)','shop1·mon1의5를 합산하지 않았다.','(1, 15, 20) / (2, 7, 0)','빈 SUM 그룹을0으로 자동 치환하지 않는다.','(1, 42, 42)','shop과월 구분을 모두 무시했다.'),['shop이 암묵 그룹 키다. shop1의월1은10+5=15,월2는20이다.','shop2는월1=7이며월2 입력이 없어SUM이NULL이다.'],'PIVOT은 집계와 암묵 그룹 키를 함께 적용한다.',ordered=True)
sqlq(19,'pivot-count-missing','COUNT PIVOT에서 해당 월 입력이 없으면 결과는?','SELECT shop,m1,m2 FROM T PIVOT(COUNT(*) FOR mon IN(1 AS m1,2 AS m2)) ORDER BY shop',[T('T','shop:NUMBER,mon:NUMBER',[(1,1),(1,1),(1,2),(2,1)])],O('SHOP,M1,M2',[(1,2,1),(2,1,0)]),W('(1, 2, 1) / (2, 1, NULL)','COUNT는 없는 매칭 입력에서0이다.','(1, 1, 1) / (2, 1, 0)','두 월1 행을 중복 제거하지 않는다.','(1, 3, 3) / (2, 1, 1)','월별 범주 분리를 적용하지 않았다.'),['shop1의 월1행은2개,월2행은1개다.','shop2의 월2행은 없으므로COUNT0이다.'],'PIVOT에서 SUM과 COUNT의 빈 입력 결과는 다르다.',ordered=True)
sqlq(19,'pivot-extra-id','PIVOT 입력에 id까지 남아 있으면 어떤 그룹이 생기는가?','SELECT id,shop,m1,m2 FROM T PIVOT(SUM(amt) FOR mon IN(1 AS m1,2 AS m2)) ORDER BY id',[T('T','id:NUMBER,shop:NUMBER,mon:NUMBER,amt:NUMBER',[(1,7,1,10),(2,7,2,20)])],O('ID,SHOP,M1,M2',[(1,7,10,None),(2,7,None,20)]),W('(1, 7, 10, 20)','id가 암묵 그룹 키여서 두 행을 한 행으로 합치지 않는다.','(1, 7, 30, 30) / (2, 7, 30, 30)','id·월별 집계 경계를 무시했다.','(1, 7, 10, 0) / (2, 7, 0, 20)','빈SUM은0이 아니라NULL이다.'),['PIVOT 절은amt와mon을 참조하므로 id와shop이 그룹 키로 남는다.','id1과id2는 별도 행이며 각각 없는 월의 SUM은NULL이다.'],'PIVOT 입력의 남는 열을 먼저 확인한다.',ordered=True)
sqlq(19,'unpivot-default','NULL을 제외하는 기본 UNPIVOT 결과는?','SELECT id,quarter,amt FROM T UNPIVOT(amt FOR quarter IN(q1 AS \'Q1\',q2 AS \'Q2\')) ORDER BY id,quarter',[T('T','id:NUMBER,q1:NUMBER,q2:NUMBER',[(1,10,None),(2,0,5)])],O('ID,QUARTER,AMT',[(1,'Q1',10),(2,'Q1',0),(2,'Q2',5)]),W('(1, Q1, 10) / (1, Q2, NULL) / (2, Q1, 0) / (2, Q2, 5)','이는INCLUDE NULLS를 명시한 결과다.','(1, Q1, 10) / (2, Q2, 5)','숫자0은NULL이 아니므로 제외되지 않는다.','(1, Q1, 10)','id2의 값들도 모두 변환 대상이다.'),['각 q열을 quarter 이름과amt 값 행으로 세운다.','id1의q2만NULL이라 제외하고 숫자0은 유지한다.'],'UNPIVOT 기본 NULL 제외는0 제외가 아니다.',ordered=True)
sqlq(19,'unpivot-include-count','INCLUDE NULLS 이후 COUNT 두 종류의 값은?','SELECT COUNT(*),COUNT(amt) FROM T UNPIVOT INCLUDE NULLS(amt FOR quarter IN(q1,q2))',[T('T','id:NUMBER,q1:NUMBER,q2:NUMBER',[(1,10,None),(2,None,None)])],O('COUNT_STAR,COUNT_AMT',[(4,1)]),W('(1, 1)','기본NULL제외 모드로 읽었다.','(4, 4)','COUNT(amt)는NULL을 제외한다.','(2, 1)','원본 행 수만 세고 열→행 변환을 반영하지 않았다.'),['원본2행×값열2개로4변환행이 모두 유지된다.','amt의비NULL은10 하나이므로COUNT(amt)=1이다.'],'형태 변환 행 수와 비NULL 값 수를 따로 센다.')
sqlq(19,'conditional-pivot','조건부 집계로 특정 월의 합계를 구한 결과는?','SELECT shop,SUM(CASE WHEN mon=1 THEN amt END) AS m1,SUM(CASE WHEN mon=2 THEN amt END) AS m2 FROM T GROUP BY shop ORDER BY shop',pivot,O('SHOP,M1,M2',[(1,15,20),(2,7,None)]),W('(1, 15, 20) / (2, 7, 0)','ELSE0이 없으므로 월2 없는 그룹은NULL이다.','(1, 35, 35) / (2, 7, 7)','CASE월 조건을 무시했다.','(1, 10, 20) / (2, 7, NULL)','동일 월의 추가행5도 합산해야 한다.'),['CASE는 해당 월의amt만 남기고 다른 월은NULL을 만든다.','SUM은NULL을 제외하여월별합계를 계산하되 매칭값이 없으면NULL이다.'],'조건부 집계의ELSE유무는 빈 범주의 결과를 바꿀 수 있다.',ordered=True)

sqlq(20,'regexp-whole-digits','전체가 숫자인 문자열만 찾은 결과는?','SELECT id FROM T WHERE REGEXP_LIKE(txt,\'^[0-9]+$\',\'c\') ORDER BY id',[T('T','id:NUMBER,txt:VARCHAR2(20)',[(1,'123'),(2,'A12'),(3,'12-3'),(4,'0')])],O('ID',[(1,),(4,)]),W('(1) / (2) / (3) / (4)','부분 숫자 존재와 전체 숫자 검사를 혼동했다.','(1)','한 문자0도+의1회 조건을 만족한다.','(2) / (3)','숫자 외 문자가 있어 양끝 앵커 조건을 만족하지 않는다.'),['^와$가 전체를 제한하고[0-9]+가 숫자 한 개 이상을 요구한다.','123과0만 모든 문자가 숫자다.'],'전체 패턴 검사는 시작·끝 조건을 함께 확인한다.',ordered=True)
sqlq(20,'regexp-second-token','두 번째 숫자 묶음을 추출한 값은?','SELECT REGEXP_SUBSTR(\'A12-B345-C6\',\'[0-9]+\',1,2,\'c\') AS token FROM dual',[],O('TOKEN',[('345',)]),W('(12)','첫 번째 일치 결과다.','(6)','세 번째 일치 결과다.','(2)','occurrence는문자 위치가 아닌 몇 번째 일치인지다.'),['숫자 묶음 일치는12,345,6 순이다.','시작 위치1에서 두 번째 일치인345를 반환한다.'],'REGEXP_SUBSTR의position과occurrence를 구별한다.')
sqlq(20,'regexp-clean-replace','숫자만 남기도록 치환한 결과는?','SELECT REGEXP_REPLACE(\'02-123 A\',\'[^0-9]\',\'\') AS cleaned FROM dual',[],O('CLEANED',[('02123',)]),W('(02-123 A)','숫자 아닌 문자를 치환하지 않은 원본이다.','(- A)','숫자 대신 비숫자를 남긴 반대 결과다.','(2123)','문자열의 선행0은 숫자변환 없이 보존된다.'),['[^0-9]는 숫자가 아닌 한 문자를 뜻한다.','하이픈,공백,A를 빈 치환으로 제거하고0,2,1,2,3을 남긴다.'],'문자열 치환은 숫자형 변환이 아니므로 선행0을 보존한다.')
sqlq(20,'regexp-class-group-difference','(ab)+ 전체 일치 패턴을 통과하는 행은?','SELECT id FROM T WHERE REGEXP_LIKE(txt,\'^(ab)+$\',\'c\') ORDER BY id',[T('T','id:NUMBER,txt:VARCHAR2(20)',[(1,'abab'),(2,'abba'),(3,'aaa'),(4,'ab')])],O('ID',[(1,),(4,)]),W('(1) / (2) / (3) / (4)','[ab]+와(ab)+를 혼동했다.','(4)','반복+는ab가두번나오는abab도허용한다.','(2) / (3)','ab덩어리의반복이아니다.'),['괄호(ab)가 한 반복 단위다.','abab는두번,ab는한번 반복이지만abba와aaa는 그 단위로 구성되지 않는다.'],'그룹 반복과 문자 클래스 반복은 다르다.',ordered=True)
sqlq(20,'regexp-case-insensitive','i 옵션을 명시한 대소문자 무시 결과는?','SELECT id FROM T WHERE REGEXP_LIKE(txt,\'^ab$\',\'i\') ORDER BY id',[T('T','id:NUMBER,txt:VARCHAR2(20)',[(1,'AB'),(2,'ab'),(3,'aB'),(4,'abc')])],O('ID',[(1,),(2,),(3,)]),W('(2)','c옵션처럼대소문자를구분했다.','(1) / (2) / (3) / (4)','끝앵커$는추가c를허용하지않는다.','(1) / (3)','소문자ab도매칭된다.'),['i가대소문자차이를무시하여AB,ab,aB를같은패턴으로본다.','전체길이2를요구하므로abc는제외한다.'],'대소문자옵션과전체일치조건을독립적으로적용한다.',ordered=True)
sqlq(20,'regexp-no-match-null','일치가 없는 REGEXP_SUBSTR의 결과는?','SELECT REGEXP_SUBSTR(\'ABC\',\'[0-9]+\',1,1,\'c\') AS token FROM dual',[],O('TOKEN',[(None,)]),W('(0)','REGEXP_INSTR의미일치위치0과혼동했다.','(ABC)','원본전체를반환하지않는다.','0행','dual의행은남고추출값이NULL이다.'),['ABC안에는숫자묶음이없다.','REGEXP_SUBSTR는일치문자열을찾지못하여NULL값을반환한다.'],'함수값NULL과조회결과0행은다르다.')

def stateq(n,slug,stem,inputs,commands,query,output,wrong,steps,memory):
    sqlq(n,slug,stem,query,inputs,output,wrong,steps,memory,ordered='ORDER BY' in query,constraints=['초기 입력은 이미 COMMIT되었다. 추가 동시 변경·트리거·자동 커밋은 없다.','명시한 명령은 같은 Oracle19c 세션에서 순서대로 수행한다.'])
    item=pack['questions'][-1]
    item['sql']='\n'.join(commands+[query])
    item['fixture']['setupSql']+='\nCOMMIT;\n'+'\n'.join(commands)

stateq(21,'update-filter-rows','가산 조건에 맞는 행만 갱신했다. 같은 세션의 최종 조회는?', [T('T','id:NUMBER,v:NUMBER',[(1,10),(2,20),(3,None)])],['UPDATE T SET v=v+5 WHERE v>=20;'],'SELECT id,v FROM T ORDER BY id',O('ID,V',[(1,10),(2,25),(3,None)]),W('(1, 15) / (2, 25) / (3, 5)','WHERE조건과NULL산술을무시했다.','(1, 10) / (2, 20) / (3, NULL)','같은세션은자신의미확정변경을볼수있다.','(1, 10) / (2, 25)','UPDATE는NULL조건행을삭제하지않는다.'),['v>=20이TRUE인id2만대상이다. id3의비교는UNKNOWN이다.','id2의기존20에5를더해25가되고나머지는유지된다.'],'UPDATE는WHERE를통과한행의값을변경한다.')
stateq(21,'delete-null-condition','=NULL 조건으로 삭제한 뒤 남은 행은?', [T('T','id:NUMBER,v:NUMBER',[(1,10),(2,None)])],['DELETE FROM T WHERE v=NULL;'],'SELECT id,v FROM T ORDER BY id',O('ID,V',[(1,10),(2,None)]),W('(1, 10)','=NULL은IS NULL과다르다.','0행','조건이없는DELETE가아니다.','(2, NULL)','비NULL행도= NULL이TRUE가아니다.'),['각v=NULL은값에관계없이UNKNOWN이다.','TRUE인행이없어DELETE는0행에영향을준다.'],'DML의NULL조건도3값논리로평가한다.')
stateq(21,'insert-column-order','명시한 열 목록 순서대로 INSERT한 결과는?', [T('T','id:NUMBER,v:NUMBER',[])],['INSERT INTO T(v,id) VALUES(40,7);'],'SELECT id,v FROM T',O('ID,V',[(7,40)]),W('(40, 7)','열목록v,id를테이블정의순서와혼동했다.','(7, NULL)','v에40을명시했다.','0행','자료형호환이되는적법한INSERT다.'),['VALUES첫40은목록첫열v로간다. 둘째7은id로간다.','SELECT는id,v순서이므로7,40을보인다.'],'INSERT열목록과SELECT출력순서는서로다를수있다.')
stateq(21,'update-all-original-expressions','한 UPDATE에서 두 열을 교환했다. 결과는?', [T('T','id:NUMBER,a:NUMBER,b:NUMBER',[(1,10,20)])],['UPDATE T SET a=b,b=a WHERE id=1;'],'SELECT a,b FROM T',O('A,B',[(20,10)]),W('(20, 20)','앞대입후바뀐a를다시읽는순차변수대입으로오해했다.','(10, 10)','b대입을먼저수행한값으로덮지않는다.','(10, 20)','UPDATE가행을갱신했다.'),['각대입의오른쪽열식은그행의기존값을참조한다.','기존b20이a로,기존a10이b로들어간다.'],'SQL한UPDATE의다중열대입을순차적인프로그램변수대입으로읽지않는다.')
stateq(21,'insert-select-filter','SELECT 결과를 새 표에 INSERT한 행은?', [T('S','id:NUMBER,v:NUMBER',[(1,5),(2,15),(3,None)]),T('D','id:NUMBER,v:NUMBER',[])],['INSERT INTO D(id,v) SELECT id,v*2 FROM S WHERE v>=10;'],'SELECT id,v FROM D',O('ID,V',[(2,30)]),W('(1, 10) / (2, 30) / (3, NULL)','WHERE필터를누락했다.','(2, 15)','SELECT의v*2계산을반영하지않았다.','(1, 10) / (2, 30)','v>=10조건에서id1은탈락한다.'),['S에서v>=10이TRUE인id2만선택한다.','v15를두배30으로계산한SELECT행을D에삽입한다.'],'INSERT SELECT는SELECT가만든행집합을삽입한다.')
stateq(21,'merge-update-insert','키가 유일한 소스와 대상에 MERGE한 결과는?', [T('D','id:NUMBER,v:NUMBER',[(1,10),(2,20)]),T('S','id:NUMBER,v:NUMBER',[(2,7),(3,9)])],['MERGE INTO D USING S ON(D.id=S.id) WHEN MATCHED THEN UPDATE SET D.v=S.v WHEN NOT MATCHED THEN INSERT(id,v) VALUES(S.id,S.v);'],'SELECT id,v FROM D ORDER BY id',O('ID,V',[(1,10),(2,7),(3,9)]),W('(2, 7) / (3, 9)','소스에없는대상id1을자동삭제하지않는다.','(1, 10) / (2, 20) / (2, 7) / (3, 9)','매칭id2는삽입대신UPDATE분기다.','(1, 10) / (2, 7)','미매칭id3의INSERT분기를빠뜨렸다.'),['소스id2는대상과매칭되어v를7로갱신한다.','소스id3는미매칭이라새행을삽입하고대상id1은유지한다.'],'MERGE의정의된분기밖동작을추가로가정하지않는다.')

trx=[T('T','id:NUMBER,v:NUMBER',[(1,10)])]
stateq(22,'partial-then-commit','부분 롤백 후 COMMIT한 최종 값은?',trx,['UPDATE T SET v=20 WHERE id=1;','SAVEPOINT s;','UPDATE T SET v=30 WHERE id=1;','ROLLBACK TO s;','COMMIT;'],'SELECT v FROM T',O('V',[(20,)]),W('(10)','부분롤백은savepoint이전20변경을유지한다.','(30)','savepoint이후30변경은취소됐다.','(NULL)','롤백은값을NULL로지우는연산이아니다.'),['초기10에서20으로변경한뒤s를표시한다.','30변경을s까지되돌려20을남기고COMMIT으로확정한다.'],'ROLLBACK TO는경계뒤만되돌리고앞의변경은나중에확정할수있다.')
stateq(22,'full-after-partial','부분 롤백 뒤 전체 ROLLBACK까지 실행하면?',trx,['UPDATE T SET v=20 WHERE id=1;','SAVEPOINT s;','UPDATE T SET v=30 WHERE id=1;','ROLLBACK TO s;','ROLLBACK;'],'SELECT v FROM T',O('V',[(10,)]),W('(20)','SAVEPOINT는20을영구확정하지않았다.','(30)','부분·전체롤백모두무시했다.','0행','초기COMMIT된행은삭제되지않는다.'),['s까지되돌리면현재20이지만아직미확정이다.','전체ROLLBACK은그20변경도취소해초기확정값10으로돌린다.'],'savepoint앞의변경도같은트랜잭션이면전체롤백대상이다.')
stateq(22,'commit-boundary','COMMIT 전후 두 UPDATE 중 롤백되는 변경은?',trx,['UPDATE T SET v=20 WHERE id=1;','COMMIT;','UPDATE T SET v=30 WHERE id=1;','ROLLBACK;'],'SELECT v FROM T',O('V',[(20,)]),W('(10)','첫UPDATE는COMMIT으로확정됐다.','(30)','둘째UPDATE는ROLLBACK으로취소됐다.','(50)','트랜잭션값을더하지않는다.'),['20변경까지첫트랜잭션을확정한다.','두번째트랜잭션의30변경만취소된다.'],'ROLLBACK범위는마지막COMMIT이후다.')
stateq(22,'savepoint-name-reuse','같은 savepoint 이름을 다시 사용한 뒤 롤백하면?',trx,['SAVEPOINT s;','UPDATE T SET v=20 WHERE id=1;','SAVEPOINT s;','UPDATE T SET v=30 WHERE id=1;','ROLLBACK TO s;'],'SELECT v FROM T',O('V',[(20,)]),W('(10)','같은이름의새savepoint가이전위치를대체했다.','(30)','새s이후변경은취소됐다.','0행','행삭제작업은없다.'),['첫s는10상태지만20변경뒤s를다시표시해위치를옮긴다.','ROLLBACK TO s는최근s위치인20상태로되돌린다.'],'동일이름savepoint재사용은최근위치를가리킨다.')
stateq(22,'ddl-commits-prior','정상 CREATE TABLE 뒤 ROLLBACK을 수행했다. T의 값은?',trx,['UPDATE T SET v=20 WHERE id=1;','CREATE TABLE X(flag NUMBER);','ROLLBACK;'],'SELECT v FROM T',O('V',[(20,)]),W('(10)','OracleDDL전암묵적COMMIT을무시했다.','(NULL)','DDL은T.v를NULL로만들지않는다.','0행','T행을삭제한작업이없다.'),['UPDATE20후적법한CREATE TABLE전에현재트랜잭션이암묵확정된다.','후속ROLLBACK으로확정된20을취소할수없다.'],'OracleDDL은그앞의미확정DML에도확정경계를만든다.')
stateq(22,'delete-insert-rollback','삭제와 삽입을 한 트랜잭션에서 취소한 최종 행은?',trx,['DELETE FROM T WHERE id=1;','INSERT INTO T VALUES(2,99);','ROLLBACK;'],'SELECT id,v FROM T ORDER BY id',O('ID,V',[(1,10)]),W('(2, 99)','마지막미확정상태이며ROLLBACK전이다.','(1, 10) / (2, 99)','INSERT도같은트랜잭션이므로취소된다.','0행','DELETE역시취소되어초기행이복구된다.'),['미확정상태에서는초기행을지우고새행을넣었다.','전체롤백은두문장을함께취소해이미확정된초기상태를되살린다.'],'트랜잭션전체롤백은여러DML을한경계로되돌린다.')

def caseq(n,slug,stem,correct,wrong,why,steps,memory,condition=None,mock=None,related=None):
    q(n,'mock' if mock else 'application',slug,stem,[(correct,why)]+wrong,why,steps,memory,conditions=condition,mock=mock,objectives=related)

caseq(23,'check-null-versus-negative','T(id 기본키, age NUMBER CHECK(age>=0))이며 age에는 NOT NULL이 없다. 독립적인 새 행 (1,NULL), (2,-1), (NULL,20)의 삽입 가능 여부는?','(1,NULL)만 가능',W('세 행 모두 가능','음수CHECK위반과PK NULL금지가있다.','(1,NULL),(NULL,20) 가능','PK에는NULL을넣을수없다.','(2,-1)만 가능','CHECK가FALSE인음수행은거부된다.'),'NULL age의CHECK는UNKNOWN으로허용되며나머지는명시제약을위반한다.',['각새행은서로독립적으로검사하며다른입력은없다.','ageNULL은UNKNOWN통과,age-1은FALSE실패,PK NULL은NOT NULL위반이다.'],'CHECK와NOT NULL은다른제약이다.',condition=['Oracle19c. 초기T는빈표다. 각삽입은독립적으로시도한다. 기본키는id한열이다.'])
caseq(23,'unique-null-single','T(code NUMBER UNIQUE)만 정의했다. code에 NULL, NULL, 5, 5를 순서대로 독립 INSERT하고 성공 문장은 유지한다. 성공하는 삽입은?','앞의 NULL 두 번과 첫 5',W('첫 NULL과 첫 5','Oracle단일열UNIQUE는여러NULL을허용한다.','네 번 모두','둘째5는기존5와중복된다.','첫 5만','UNIQUE만으로NULL을금지하지않는다.'),'단일열UNIQUE는NULL둘을허용하지만비NULL5의중복은거부한다.',['초기빈표에서두NULL삽입은둘다제약위반이아니다.','첫5가들어간뒤다음5는중복으로실패한다.'],'단일열UNIQUE의NULL허용을PRIMARY KEY와구분한다.',condition=['Oracle19c. code는단일열UNIQUE이고NOT NULL은없다. 트리거·다른제약없음.'])
caseq(23,'fk-parent-required','부모 P(id PK)에 1이 있고, 자식 C(id PK,pid FK→P.id)는 비어 있다. pid는 NULL 허용이다. 새 자식 (10,1),(11,2),(12,NULL) 중 삽입 가능한 행은?','(10,1)과 (12,NULL)',W('(10,1)만','외래키pid에NOT NULL이없어NULL은허용된다.','세 행 모두','부모id2가없어(11,2)는참조무결성을위반한다.','(11,2)와 (12,NULL)','기존부모1을참조하는행이정상이며2는실패한다.'),'비NULL참조값은부모에있어야하며NULL허용은별도제약에따른다.',['pid1은부모에존재한다. pid2는없다.','pidNULL은NOT NULL이없으므로이FK만으로거부되지않는다.'],'참조무결성과필수참여를별도로검사한다.',condition=['Oracle19c. 각행의삽입은독립시도,즉시검사FK,그외제약없음.'])
caseq(23,'parent-delete-set-null','C.pid가 NULL 허용이고 P.id를 ON DELETE SET NULL로 참조한다. 부모1과 자식(10,1),(11,1)이 있다. 부모1 삭제 후 자식 상태는?','자식 두 행이 남고 pid는 모두 NULL',W('자식 두 행도 삭제','ON DELETE CASCADE와다르다.','자식 pid가모두0','SET NULL은숫자0이아니다.','항상부모삭제거부','명시한SET NULL옵션과NULL허용조건을반영해야한다.'),'SET NULL은참조열값을비우며자식행자체는유지한다.',['부모1을참조한자식두행을찾는다.','두행의pid만NULL로설정하고id10,11은남긴다.'],'CASCADE의행삭제와SET NULL의참조값변경을구분한다.',condition=['Oracle19c. 자식pid NULL허용,그외삭제제한·트리거없음.'])
caseq(23,'truncate-versus-delete-rollback','Oracle19c에서 이미 확정된 T의 모든 행을 TRUNCATE한 뒤 ROLLBACK했다. 결과는?','행은 비어 있고 T의 열 정의는 남는다',W('모든행이ROLLBACK으로복구','OracleTRUNCATE는DDL이다.','T객체와열정의가사라진다','DROP TABLE과혼동했다.','WHERE가없어TRUNCATE문법오류','TRUNCATE는전체행을대상으로한다.'),'OracleTRUNCATE는정의를유지한채전체행을비우며일반ROLLBACK복구대상이아니다.',['행제거동작이DELETE인지TRUNCATE인지확인한다.','TRUNCATE성공뒤ROLLBACK해도행은복구되지않고표정의는남는다.'],'객체정의보존과행복구가능성을각각판단한다.',condition=['Oracle19c. FK등TRUNCATE차단조건없음. 명령은성공했다.'])
caseq(23,'drop-versus-recreate','T를 정상 DROP TABLE한 직후 같은 이름으로 SELECT하려 한다. T와 같은 이름의 다른 객체·동의어는 없다. 판정은?','기존 T 객체가 없어 조회할 수 없다',W('열정의는남아0행조회','TRUNCATE와혼동했다.','최근COMMIT행을자동조회','DROP은기존표객체를제거했다.','같은이름으로자동CREATE','SELECT가테이블을자동생성하지않는다.'),'DROP TABLE은표객체를제거하므로그이름으로기존표를조회할수없다.',['DROP성공으로객체정의가없어진상태를확인한다.','추가복구·재생성·동의어가없어SELECT대상이해결되지않는다.'],'DROP뒤조회와TRUNCATE뒤빈조회는다르다.',condition=['Oracle19c. DROP성공. recycle bin이나FLASHBACK복구동작은실행하지않았다.'])

caseq(24,'read-only-grant','B는 A.T의 SELECT 권한만 직접 받았고 다른 권한 경로는 없다. B가 할 수 있는 작업은?','A.T 조회',W('A.T행갱신','UPDATE권한은받지않았다.','A.T행삽입','INSERT권한은받지않았다.','A.T조회권한을C에게재부여','WITH GRANT OPTION은받지않았다.'),'SELECT는조회만허용하며다른작업과재부여능력은별도다.',['권한종류SELECT와대상A.T를확인한다.','다른직접권한·역할·재부여옵션이없다는조건을적용한다.'],'권한의대상·작업·재부여능력을따로읽는다.',condition=['Oracle19c. A는T소유자,B는다른사용자. 역할·PUBLIC·시스템권한등다른경로없음.'])
caseq(24,'grant-chain-revoke','A가 B에게 객체 SELECT를 WITH GRANT OPTION으로 주고, B만이 C에게 이를 재부여했다. A가 B의 그 객체 권한을 회수하면 C의 이 경로는?','B에게 의존한 C의 권한도 회수된다',W('C의권한은항상독립적으로영구유지','객체권한종속부여의회수효과를무시했다.','C의모든다른표권한도자동회수','회수범위를불필요하게확대했다.','C가자동으로표소유자가된다','권한회수는소유권이전이아니다.'),'객체권한의종속재부여경로는상위권한회수의영향을받는다.',['유일한부여경로A→B→C를그린다.','B의기반객체권한이회수되면그에의존한C의권한도상실한다.'],'객체권한연쇄회수와시스템권한관리규칙을동일시하지않는다.',condition=['Oracle19c. C의다른직접부여·역할·PUBLIC경로없음. 대상은동일객체SELECT다.'])
caseq(24,'role-survives-direct-revoke','B가 A.T의 SELECT를 직접 받고 활성 역할 R을 통해서도 받았다. 직접 SELECT만 회수하고 R의 부여는 유지했다. B의 조회 가능성은?','활성 역할 R의 경로로 조회 가능',W('모든경로가자동회수되어불가능','직접회수와역할권한회수는다르다.','UPDATE만가능','권한종류가자동으로바뀌지않는다.','B가T를DROP해야조회가능','조회권한경로와무관한주장이다.'),'역할에유효한SELECT가남아있으므로직접권한회수만으로접근이사라지지않는다.',['권한경로는직접과활성R두개다.','직접경로를지운후R경로는그대로유지된다.'],'권한회수효과는남아있는경로를함께확인한다.',condition=['Oracle19c. 일반SQL조회이며R은활성화되어있다. 정의자권한저장프로그램상황이아니다.'])
caseq(24,'column-update-only','B에게 T의 salary 열 UPDATE 권한만 주었다. 다른 권한 경로가 없다. 이 권한이 직접 허용하는 수정 범위는?','salary 열의 수정',W('salary와name두열수정','name열UPDATE권한은받지않았다.','새행의모든열INSERT','UPDATE권한은INSERT권한이아니다.','테이블열추가','ALTER구조변경권한이아니다.'),'객체권한은열단위로제한할수있고그범위를넘는수정은허용되지않는다.',['권한의동작은UPDATE이고대상열은salary다.','다른열수정·행삽입·구조변경은서로다른능력이다.'],'같은테이블이어도열단위권한범위를구분한다.',condition=['Oracle19c. WHERE조건조회권한등의부수조건을묻지않고부여한UPDATE권한의직접범위만판단한다.'])
caseq(24,'system-not-data-read','B에게 CREATE TABLE 시스템 권한과 충분한 자기 tablespace quota만 있다. A.T에 대한 다른 권한은 없다. 이 사실만으로 가능하다고 할 수 있는 것은?','자기 스키마에 허용 조건의 테이블 생성',W('A.T의모든행조회','CREATE TABLE은타인객체SELECT권한이아니다.','A.T의소유권이전','시스템권한이임의소유권이전을뜻하지않는다.','모든사용자의암호변경','다른관리권한이다.'),'객체생성능력과기존타인표의데이터접근권한은별개다.',['CREATE TABLE의작업범위와할당량조건을확인한다.','기존A.T조회권한은주어지지않았다.'],'시스템권한하나를모든객체권한으로확대하지않는다.',condition=['Oracle19c. 접속가능한사용자,quota와기본객체생성조건충족. 다른시스템·객체권한없음.'])
caseq(24,'public-revoke-scope','A.T의 SELECT가 PUBLIC과 B 직접 경로로 부여되어 있다. A가 PUBLIC의 SELECT만 회수했다. B의 직접 경로는?','직접 부여가 남으므로 B는 계속 조회 가능',W('직접부여도자동동시에회수','PUBLIC경로와직접경로는구별된다.','B만자동INSERT권한획득','회수가다른권한을생성하지않는다.','A의소유권도회수','객체소유권제거가아니다.'),'특정수신자PUBLIC의권한회수는별도로부여한B직접권한을그자체로없애지않는다.',['회수대상이PUBLIC인지B인지확인한다.','B직접경로는변경하지않았으므로남아있다.'],'권한회수문장의수신자와기존모든경로를대조한다.',condition=['Oracle19c. B에게직접준SELECT는별도유효한부여이며함께회수하지않았다.'])

# Reserved mock sets use independently designed combined scenarios.  They are
# neither renamed nor renumbered copies of the practice items above.
def mc(setno,n,slug,stem,correct,wrong,why,steps,memory,extra=None):
    caseq(n,f'm{setno}-{slug}',stem,correct,wrong,why,steps,memory,condition=['Oracle Database 19c. 지문에 적은 입력·제약이 전체 조건이다.','다른 제약·트리거·동시 변경·추가 권한·정렬은 가정하지 않는다.']+(extra or []),mock=f'mock-{setno}')

mc(1,9,'null-and-limited-order','배송목록에서 미정 ETA(NULL)를 마지막에 두고, ETA가 빠른 것부터 표시하며 ETA까지 같은 행은 고유 order_id 오름차순으로 고른다. 상위10행 조회를 반복해도 경계가 흔들리지 않을 설계는?','ETA ASC NULLS LAST 다음 order_id ASC로 정렬 후 10행 제한',W('ETA DESC NULLS LAST 후10행 제한','늦은ETA부터나오는방향이다.','ETA ASC만 정렬 후10행 제한','동일ETA행사이순서를정하지않았다.','10행을먼저임의선택한뒤ETA정렬','전체우선순위상위10을보장하지않는다.'),'NULL배치,업무방향,동점안정성,제한순서를모두충족해야한다.',['미정ETA는NULLS LAST로끝에둔다.','빠른ETA ASC를먼저비교하고동점고유키로전체순서를만든후제한한다.'],'Top N은정렬방향과동점키,선택시점을함께검사한다.')
mc(1,10,'header-amount-inflation','주문 H(id PK,total)에 (1,100),(2,50), 상세 L(hid,qty)에 (1,1),(1,2),(2,1)가 있다. H.id=L.hid 내부 조인 후 H.total을 SUM했다. 합계가 주문 총액150과 달라지는 이유는?','주문1의 total100이 상세 두 행에 반복되어 합계250이 된다',W('조인은모든중복을없애므로합계150이다','JOIN은상세별행쌍을유지한다.','상세qty를곱하므로합계350이다','요청한SUM식은H.total이며qty곱셈이없다.','기본키가있으면상세는한개만매칭된다','H의PK는자식hid의중복을금지하지않는다.'),'집계단위가주문인데조인결과단위는상세행이어서주문금액이중복집계된다.',['주문1은두상세행에매칭되어100이두번나타난다.','주문2의50한번과합치면100+100+50=250이다.'],'조인후합계는원본업무단위가중복되지않는지확인한다.')
mc(1,10,'unique-pairs-self','서로 다른 두 학생의 조합을 순서 없이 한 번씩 만들려 한다. 학생id는1,2,3이며 유일·비NULL이다. 같은 표의 별칭 A,B를 결합해 A.id<B.id인 쌍만 고르면?','(1,2),(1,3),(2,3) 세 쌍',W('(1,2),(2,1),(1,3),(3,1),(2,3),(3,2) 여섯 쌍','이는서로다름조건이며<는역순쌍을제외한다.','(1,1),(2,2),(3,3) 세 쌍','자기쌍은<를만족하지않는다.','(1,2),(2,3) 두 쌍','인접id만고르는조건이아니다.'),'엄격부등식이자기쌍과대칭역순을함께제외한다.',['9개전체쌍에서A=B를제외한다.','남은대칭쌍중작은id가왼쪽인경우만선택한다.'],'셀프조인의부등식은순서없는조합을중복없이만들수있다.')
mc(1,11,'outer-or-null-leak','고객 C(id)에1,2, 주문 O(cid,status)에(1,0)이 있다. C LEFT JOIN O를cid로매칭한후 WHERE에 status=1 OR O.cid IS NULL을두었다. 이방법이 유료주문(status1)이없는고객도모두보존하는가?','아니다. 비유료 주문만 있는 고객1은 이미 매칭되어 NULL 확장되지 않고 필터에서 사라진다',W('그렇다.OR IS NULL은언제나ON필터와같다','실제비유료매칭행은O.cid가NULL이아니다.','고객1만남고2는사라진다','고객2의NULL확장행은OR조건을통과한다.','두고객모두반드시사라진다','미매칭고객2는IS NULL이TRUE다.'),'미매칭NULL과유료조건에실패한실제매칭행은서로다른상태다.',['고객1의결과는status0,cid1이라두OR항이모두FALSE다.','고객2는O.cidNULL이어서통과한다. 유료매칭을ON에두어야의도대로보존한다.'],'WHERE에OR IS NULL을추가해도ON조건이동과언제나동등하지않다.')
mc(1,11,'full-null-double','A(k)에NULL 한 행, B(k)에NULL 한 행이 있다. k등호로 FULL OUTER JOIN하면 결과 행 수와 키 상태는?','두 행이며 두 행 모두 양쪽 k가 NULL이다',W('한행이다.NULL끼리매칭된다','일반등호NULL=NULL은TRUE가아니다.','0행이다.NULL은모두제거된다','FULL은각미매칭행을보존한다.','두행이며한쪽NULL을0으로채운다','NULL확장은0치환이아니다.'),'두NULL행은매칭되지않아양쪽에서각각보존되어겉모습같은두행이된다.',['ON의NULL비교가UNKNOWN이므로매칭쌍은없다.','왼쪽미매칭확장한행과오른쪽미매칭확장한행을각각남긴다.'],'겉모습이같아도외부조인의두미매칭원본이두결과행을만들수있다.')
mc(1,12,'not-in-correct-filter','등급 A(code 비NULL)에1,2,3이 있고 차단표 B(code)에2,NULL이 있다. 차단표의 실제 코드만 제외해1,3을얻으려면 적절한 수정은?','NOT IN의 서브쿼리에서 B.code IS NOT NULL을 적용한다',W('바깥A.code에IS NOT NULL만추가','바깥값은원래비NULL이며차단표NULL문제가남는다.','NOT IN을그대로두고ORDER BY추가','정렬은UNKNOWN필터결과를바꾸지않는다.','차단표NULL을1로치환','차단되지않아야할코드1까지제외한다.'),'오염원은NOT IN비교집합의NULL이므로그NULL을제거해야한다.',['B에서NULL을제외하면비교집합은{2}다.','A1,3은2와다르므로TRUE,A2는FALSE다.'],'NOT IN의NULL대책은어느쪽NULL이문제인지조건과함께설계한다.')
mc(1,12,'scalar-grouping-cardinality','단일값 위치의 서브쿼리가 부서별 MAX(salary)를 GROUP BY dept로반환한다. 실제 부서는두개이고각MAX값이모두100이다. 바깥비교의판정은?','같은 값이어도 두 그룹 행이므로 스칼라 다중행 오류',W('두값이같으므로100한값으로자동축약','행수제약은값종류수가아니다.','MAX가있으므로항상한행','GROUP BY가여러그룹을만들수있다.','두MAX를더해200사용','추가SUM을요청하지않았다.'),'집계함수존재만으로스칼라행수가1이라고보장할수없다.',['dept별로두그룹을만들어각100을낸다.','스칼라위치는최대1행인데결과는2행이므로실패한다.'],'GROUP BY없는집계와GROUP BY있는집계의행수를구분한다.')
mc(1,12,'universal-using-not-exists','사용자 U의 모든 주문이 paid=1인지 검사하려 한다. paid는 NOT NULL이며 주문0개도 조건을충족한다고정했다. 적절한 논리식은?','paid<>1인 주문이 NOT EXISTS',W('paid=1인주문이EXISTS','한건만유료여도통과하여모두조건이아니다.','paid=1인주문이NOT EXISTS','유료주문이없음을묻는반대조건이다.','주문수가정확히1','유료여부와전체만족을판단하지못한다.'),'모든행이조건을만족함은그조건을위반한행이없음으로표현할수있다.',['위반주문paid<>1이하나라도있으면실패한다.','주문0개이면위반도없으므로정한업무규칙대로통과한다.'],'모든행조건은반례의NOT EXISTS로바꿀수있고NULL·빈집합정책이필요하다.')
mc(1,13,'projection-then-dedup','첫결과(id,name)는(1,A),(2,A), 둘째결과는(3,A)다. 각SELECT에서name만선택하여UNION하면몇행인가?','A 한 행',W('A세행','UNION ALL이아니며출력열name기준으로중복제거한다.','서로다른id세개이므로세행','id는SELECT결과에없어중복판정대상이아니다.','0행','공통행이제거되는차집합이아니다.'),'집합연산은원본행식별자가아니라SELECT로투영한행전체를비교한다.',['세원본모두투영후한열A행이다.','UNION의중복제거로한행이남는다.'],'어떤열을SELECT했는지가집합연산중복판정을바꾼다.')
mc(1,13,'all-filter-stage','A(v)에는1,1,2; B(v)에는1,3이있다. 각입력을v>=2로필터한뒤UNION ALL한결과의COUNT(*)는?','2',W('3','필터전1중복을남기지않는다.','5','양쪽필터를적용하지않았다.','1','2와3은서로다른두행이며한개가아니다.'),'행필터후남은A2,B3두행을ALL로결합한다.',['A는2한행,B는3한행으로줄어든다.','ALL은두행을그대로유지하여COUNT2다.'],'집합연산전에각SELECT의WHERE를먼저의미상적용한다.')
mc(1,14,'grouping-id-mask','ROLLUP(region,store)에서 region은유지되고store만소계NULL인행이있다. GROUPING(region),GROUPING(store)의쌍은?','(0,1)',W('(1,0)','어느키가집계로빠졌는지뒤집었다.','(1,1)','전체합계는둘다빠지지만지역소계는region이남는다.','(0,0)','상세(region,store)그룹의표시다.'),'지역소계수준은(region)이며store만그룹키에서제외된다.',['ROLLUP수준은(region,store),(region),()다.','중간수준에서region의GROUPING은0,store는1이다.'],'GROUPING은현재수준에서제외된키를표시한다.')
mc(1,14,'null-nvl-subtotal','ROLLUP(dept)의dept에실제NULL데이터도있다. dept가NULL이면일괄적으로전체합계라표시하는NVL설계의결함은?','실제 NULL 부서 그룹도 전체 합계로 잘못 표시한다',W('NVL은문자열을반환할수없다','적합한자료형일때문자표시를만들수있다.','ROLLUP은원본NULL행을무조건버린다','원본NULL도별도그룹이된다.','GROUPING은원본값을삭제한다','GROUPING은표시함수이지삭제함수가아니다.'),'실제NULL그룹과집계NULL을구별한뒤각라벨을정해야한다.',['NULL은데이터누락과합계용키생략두경로로생긴다.','GROUPING=1을합계라벨로,0이면서NULL이면미등록부서등으로구분한다.'],'소계라벨은NULL모양보다GROUPING상태에기반해야한다.')
mc(1,15,'aggregate-window-logical','부서별 SUM(sales)를 GROUP BY로구한뒤그합계를기준으로RANK를붙이려한다. 분석함수가번호를붙이는대상은?','그룹 집계 후의 부서별 결과 행',W('항상원본매출개별행','분석함수는GROUP BY결과위에서평가될수있다.','데이터파일블록','논리질의결과행을계산한다.','RANK는GROUP BY와같이못쓴다','그룹집계결과에분석계산을적용할수있다.'),'GROUP BY가만든결과행에분석함수를적용하여부서순위를계산한다.',['부서별로원본매출을요약한다.','부서합계들을비교하여부서결과행옆에순위를붙인다.'],'분석함수의입력은해당쿼리블록에서그룹화까지거친결과다.')
mc(1,15,'lag-filter-order','id1값10,id2값20,id3값30에서 WHERE id>=2를먼저적용한쿼리블록이id순LAG(v,1,0)를계산한다. id2의LAG는?','0',W('10','같은블록WHERE로id1이분석입력에서제외됐다.','20','현재값이아니라이전행을본다.','NULL','이전행없음기본값0을명시했다.'),'분석함수입력에는WHERE를통과한id2,3만있으므로id2앞행이없다.',['WHERE후결과는id2=20,id3=30이다.','그집합의첫행id2에는LAG기본값0을사용한다.'],'필터를분석전같은블록에둘지분석후바깥블록에둘지에따라결과가달라진다.')
mc(1,16,'nullable-window-count','id순값이NULL,5,NULL이다. 현재행부터다음행까지ROWS프레임에서COUNT(*)와COUNT(v)를계산할때첫행의값은?','(2,1)',W('(1,1)','프레임에는현재NULL행도존재한다.','(2,2)','COUNT(v)는NULL값을제외한다.','(3,1)','프레임은현재와다음한행으로제한된다.'),'첫프레임은NULL행과5행두개이며비NULL은5하나다.',['ROWS CURRENT ROW~1 FOLLOWING으로앞의두행을선택한다.','행수2와비NULL값수1을별도로센다.'],'윈도우프레임에서도COUNT의세는대상차이는유지된다.')
mc(1,16,'last-null-respect','id순값10,20,NULL에전체파티션ROWS프레임을지정한LAST_VALUE(v)는IGNORE NULLS를쓰지않았다. 첫행에붙는결과는?','NULL',W('20','IGNORE NULLS를명시하지않았다.','10','FIRST_VALUE또는현재행값으로읽었다.','0','NULL을자동0으로치환하지않는다.'),'기본RESPECT NULLS이며전체마지막행값NULL을반환한다.',['전체프레임마지막은id순세번째행이다.','그행값NULL을그대로읽으므로첫행에도NULL이붙는다.'],'전체끝경계와NULL처리옵션을둘다확인한다.')
mc(1,17,'dense-cut-groups','매출이100,90,90,80이다. 서로다른상위두매출값의행만보존한뒤COUNT(*)하면?','3',W('2','서로다른값종류수와그값에속한행수는다르다.','4','80은세번째서로다른값이다.','1','최고값만선택한것이아니다.'),'상위두값100과90에속한원본행은1+2=3개다.',['DENSE_RANK매출DESC값은1,2,2,3이다.','<=2인세행을보존한다.'],'상위n개값그룹은결과행수가n보다커질수있다.')
mc(1,17,'rownum-projected-page','정렬된인라인뷰에바깥블록이ROWNUM별칭rn을붙이고그보다바깥블록에서rn BETWEEN 2 AND 3을필터한다. 번호가이미고정된1,2,3,4행중남는것은?','rn2와rn3 두 행',W('0행','같은블록ROWNUM>1과다르며이미계산된별칭을필터한다.','rn1만','조건2이상3이하를만족하지않는다.','rn3와rn4','범위를한칸이동할근거가없다.'),'이미생성된번호열을다른블록의일반값으로필터할수있다.',['중간뷰가rn1~4를행에붙인상태를확인한다.','외부WHERE가숫자범위2~3을적용한다.'],'ROWNUM가생성되는블록과그별칭을필터하는블록을구분한다.')
mc(1,18,'hierarchy-multiple-roots','N(id,pid)는(1,NULL),(2,NULL),(3,1),(4,2)다. pid IS NULL인모든행을시작점으로하향탐색하면LEVEL1행수와전체행수는?','LEVEL1 두 행, 전체 네 행',W('LEVEL1 한행,전체세행','START WITH는조건에맞는여러루트를선택할수있다.','LEVEL1 네행,전체네행','자식3,4는LEVEL2다.','LEVEL1 두행,전체두행','CONNECT BY가자식으로확장한다.'),'두독립루트각각에서자식한개씩을연결한다.',['루트1,2가모두LEVEL1이다.','3은1의자식,4는2의자식으로LEVEL2이며네행을낸다.'],'START WITH는루트한개만강제하지않는다.')
mc(1,18,'root-versus-parent','경로1→2→3에서현재행3의직접부모id와CONNECT_BY_ROOT id는?','직접 부모2, 루트1',W('직접부모1,루트2','부모와루트를뒤집었다.','직접부모3,루트1','자기id와부모id는다르다.','직접부모2,루트3','루트는START WITH의시작행이다.'),'부모는바로윗관계행이며루트는경로의출발행이다.',['현재3에서한단계올라가면2다.','이번경로의시작은1로모든자손의루트값은1이다.'],'계층의직속관계와경로전체의출발점을구별한다.')
mc(1,19,'pivot-avg-weight','원본월1금액은10,30이고월2금액은90이다. 월별AVG PIVOT결과20,90을단순평균하면55다. 이값이원본전체AVG와다른이유는?','월별 건수가 달라 그룹 평균의 단순 평균은 원본 평균130/3과 다르다',W('AVG는NULL외모든값을무시한다','비NULL10,30,90을계산한다.','PIVOT이항상원본평균을보존한다','집계단위변경과가중치차이가있다.','원본평균도55다','합계130을3개로나누어야한다.'),'월별요약으로건수정보를버린뒤같은가중치로평균하면원본행가중치와달라진다.',['원본총합130,건수3으로원본평균은130/3이다.','월평균20,90의단순평균55는각월을동일한한단위로센다.'],'집계후재집계는원래분모·가중치를유지하는지확인한다.')
mc(1,19,'unpivot-zero-versus-missing','한행의Q1=0,Q2=NULL,Q3=5를기본UNPIVOT한뒤amount>=0을필터한다. 남는분기는?','Q1과 Q3',W('Q3만','숫자0은NULL이아니며>=0을만족한다.','Q1,Q2,Q3모두','기본UNPIVOT은Q2NULL변환행을제외한다.','Q1만','양수5도>=0을만족한다.'),'NULL제외와숫자범위조건을분리해적용한다.',['UNPIVOT은0행과5행을만들고NULL분기를제외한다.','둘다0이상이라필터를통과한다.'],'NULL·0·음수는서로다른상태다.')
mc(1,20,'alternation-anchors','ASCII에서패턴 ^A|B$ 를 c옵션으로검색한다. 문자열 AX와XB에대한판정은?','둘 다 일치한다',W('둘다불일치','대안전체를하나의양끝조건으로묶지않았다.','AX만일치','B$대안은XB끝B와일치한다.','XB만일치','^A대안은AX시작A와일치한다.'),'대안은시작A또는끝B이며문자열전체가A나B만이어야한다는뜻이아니다.',['AX는^A대안에맞는다.','XB는B$대안에맞는다. 전체A또는B만원하면괄호와양끝앵커를함께쓴다.'],'정규식대안|와괄호·앵커의적용범위를확인한다.')
mc(1,21,'update-subquery-null','T(id,v)에(1,10)이있다. UPDATE의v대입식은행을반환하지않는스칼라서브쿼리다. v는NULL허용이며다른제약없다. 같은세션의변경결과는?','id1의 v가 NULL이 된다',W('v10을그대로유지','스칼라0행은NULL값이며대입을건너뛰지않는다.','다중행스칼라오류','0행은허용되고복수행이오류다.','행1을삭제','UPDATE대입은행삭제가아니다.'),'대입식의스칼라값NULL을v에저장한다.',['서브쿼리0행을스칼라NULL로평가한다.','NULL허용열이므로그값으로대입한다.'],'스칼라0행은DML대입을생략시키는신호가아니다.')
mc(1,21,'merge-unmatched-delete','대상D에키1,2가있고소스S에는키2만있다. MERGE가매칭UPDATE와미매칭INSERT만정의하며DELETE절은없다. 대상키1은?','그대로 남는다',W('소스에없으므로자동삭제','정의하지않은동기화삭제를가정하면안된다.','키2로자동변경','키수정식을정의하지않았다.','INSERT분기로중복한행추가','분기는소스행기준이며소스에키1행이없다.'),'MERGE는정의된소스매칭분기의변경만수행한다.',['소스키2는대상키2UPDATE를실행한다.','대상에만있는키1을지울명령이없어보존된다.'],'MERGE는자동전체동기화명령이아니며실제분기를읽어야한다.')
mc(1,22,'failed-statement-prior-change','초기확정v10을UPDATE로20에바꾼뒤다른UPDATE한문장이즉시검사CHECK위반으로실패했다. DDL·COMMIT·전체ROLLBACK은없다. 첫변경20의상태는?','현재 트랜잭션의 미확정 변경으로 남는다',W('자동COMMIT되어영구확정','문장실패는확정명령이아니다.','초기10으로전체자동롤백','실패문장롤백과이전성공문장의범위를혼동했다.','NULL로변경','제약위반이값을NULL로치환하지않는다.'),'Oracle의문장원자성은실패한문장의변경을되돌리며이전성공문장을자동전체취소한다고볼수없다.',['첫UPDATE의성공경계와둘째실패문장을나눈다.','실패문장만취소되고첫미확정20은나중에COMMIT또는ROLLBACK대상으로남는다.'],'실패문장·트랜잭션·이미확정된이력의세경계를구별한다.')
mc(1,23,'unique-fk-not-one-to-one','자식C(pid)가부모P(id PK)를참조하는FK이지만C.pid에는UNIQUE가없다. 부모1을여러자식이참조할수있는가?','가능하다. FK는 자식 참조값의 유일성을 요구하지 않는다',W('불가능.FK가자동UNIQUE다','참조무결성과유일성은다르다.','부모PK를삭제해야가능하다','부모키는참조대상의유일성을지킨다.','자식pid가NULL일때만가능하다','비NULL1도여러자식이참조할수있다.'),'여러자식의동일부모참조는일대다관계의일반형태다.',['각자식pid1은부모존재조건을만족한다.','자식중복을막는UNIQUE가없으므로여러행을허용한다.'],'FK만보고관계의최대카디널리티를1:1로단정하지않는다.')
mc(1,24,'grant-option-not-admin','B가 A.T의SELECT를WITH GRANT OPTION으로받았다. 이것만으로B가새사용자를만들거나CREATE TABLE시스템권한을부여할수있는가?','아니다. 부여받은 객체 SELECT의 재부여 범위다',W('모든시스템권한을재부여가능','객체권한옵션을관리자능력으로확대했다.','SELECT권한도재부여불가능','WITH GRANT OPTION이그재부여를허용한다.','T소유자가자동B로바뀐다','권한부여와소유권이전은별개다.'),'객체권한재부여능력은해당객체·권한범위이며다른시스템권한과무관하다.',['받은권한은A.T SELECT이다.','옵션은그권한을재부여하는능력만추가한다.'],'재부여옵션의범위를권한종류밖으로일반화하지않는다.')

mc(2,9,'distinct-order-ambiguity','조회는 DISTINCT dept만 반환한다. 한 부서에 서로 다른 salary가 여러 개 있다. 부서별 대표 급여 정의 없이 원본 salary로 정렬하려는 설계의 문제는?','어떤 부서 급여로 정렬할지 결정되지 않았고 Oracle DISTINCT 정렬식 제약에도 맞지 않을 수 있다',W('DISTINCT가최댓값급여를자동선택한다','대표값집계를요청하지않았다.','DISTINCT가최솟값급여를자동선택한다','정렬의업무기준을암묵적으로만들지않는다.','salary가숫자이면언제나명확하다','자료형이대표값선택문제를해결하지않는다.'),'반환단위dept와정렬값salary의단위가달라대표집계또는일관된선택이필요하다.',['한dept에여러salary가연결되어단일정렬값이없다.','MAX등요구에맞는대표값을명시한그룹결과를정렬해야한다.'],'DISTINCT로열을줄일때정렬의단위와Oracle허용조건을확인한다.')
mc(2,10,'missing-join-predicate','상품 P(id PK) 3행과 주문 O(id PK,pid) 4행을 결합했는데 상품 연결 조건을 빠뜨려 모든 조합을 만들었다. 행 수는?','12행',W('4행','원래주문단위매칭수를가정했지만조건이없다.','7행','조인은두입력행수를더하지않는다.','3행','상품수만유지하는집계가아니다.'),'조건없는모든쌍은3×4개다.',['각상품이네주문모두와결합한다.','상품세개에각네쌍이므로12행이다.'],'누락된조인조건은의도하지않은데카르트곱을만들수있다.')
mc(2,10,'condition-or-expands','A(k,flag)에(1,1),(2,0), B(k)에1,2가 있다. ON이 A.k=B.k OR A.flag=1이면 매칭 쌍 수는?','3쌍',W('2쌍','flag1인A1은다른키B2와도OR조건으로매칭된다.','4쌍','A2와B1은등호FALSE,flag1도FALSE다.','1쌍','OR조건의일반키매칭을빠뜨렸다.'),'flag1조건이행쌍마다TRUE여서그A행은모든B행과만난다.',['A1은B1,B2와두쌍이다.','A2는B2와만일치하여한쌍,총3쌍이다.'],'ON의OR는추가매칭경로를열수있다.')
mc(2,11,'null-note-false-anti','고객1은 실제 주문(id10,memo NULL)이 있고 고객2는 주문이 없다. LEFT JOIN 후 O.memo IS NULL로 주문 없는 고객을 찾았다. 나오는 고객과 결함은?','고객1,2 모두 나오며 실제 주문의 NULL 메모를 미매칭과 혼동한다',W('고객2만나오므로항상정확','memo는실제주문에서도NULL가능하다.','고객1만나온다','고객2의NULL확장memo도IS NULL이다.','아무도나오지않는다','IS NULL은두행에서TRUE다.'),'미매칭검사는실제매칭행의NULL가능열을사용하면거짓양성이생긴다.',['고객1은실제memoNULL,고객2는확장memoNULL이다.','둘다필터를통과하므로비NULL보장주문키로검사해야한다.'],'안티조인판별열에는실제행에서의비NULL보장이필요하다.')
mc(2,11,'right-to-left-rewrite','A RIGHT OUTER JOIN B ON A.k=B.k를 같은 결과 열 의미로 재작성하려 한다. 보존 방향을 유지하는 것은?','B LEFT OUTER JOIN A에 동일한 키 조건 사용',W('A LEFT OUTER JOIN B','보존입력을A로바꾼다.','B INNER JOIN A','미매칭B보존을잃는다.','A CROSS JOIN B','키조건과외부보존의미가사라진다.'),'입력위치를바꾸면서RIGHT를LEFT로바꾸면동일한B보존을유지한다.',['원래RIGHT가보존하는입력은B다.','B를왼쪽으로옮기고LEFT를써같은입력을보존한다.'],'조인방향재작성은표이름의순서와보존대상을함께바꾼다.')
mc(2,12,'scalar-no-group-count','서브쿼리는 빈 주문표에서 GROUP BY 없이 COUNT(*)만 반환한다. 스칼라 위치에서 받는 값은?','0 한 값',W('NULL','COUNT의빈입력결과는0이다.','스칼라0행오류','서브쿼리도집계결과한행을반환하며0행은원래오류도아니다.','두행이상오류','그룹없는단일집계는한행이다.'),'빈원본과집계결과행수를구분하면COUNT0한행이다.',['원본주문행수는0이다.','COUNT(*)집계결과한행의값은0이므로스칼라0이된다.'],'COUNT집계0한행과행을전혀반환하지않는서브쿼리는다르다.')
mc(2,12,'all-null-veto','비NULLx=20을값집합{10,NULL}의모든값보다큰지 >ALL로비교한다. WHERE에서통과하는가?','통과하지 않는다. TRUE AND UNKNOWN은 UNKNOWN이다',W('통과한다.10보다크기만하면된다','ANY와ALL을혼동했다.','문법오류로실패한다','NULL을포함한비교는적법한3값논리다.','FALSE이므로NULL과무관하다','20>10은TRUE이고NULL비교때문에UNKNOWN이다.'),'ALL은모든비교가TRUE여야하는데NULL비교가UNKNOWN이다.',['20>10은TRUE,20>NULL은UNKNOWN이다.','AND결과UNKNOWN은WHERE를통과하지못한다.'],'ALL의NULL영향은ANY와다르게나타날수있다.')
mc(2,12,'uncorrelated-exists-mistake','C고객1,2가 있고 O에는 고객1의 주문만 있다. EXISTS 내부에 C와 O를 연결하는 상관조건이 없고 O의 전체 행 존재만 검사한다. 반환 고객은?','고객1과 고객2',W('고객1만','상관조건이없어고객2도같은존재판정을받는다.','고객2만','주문없는고객판정조건이아니다.','0행','O에는한행이있으므로EXISTS가TRUE다.'),'비상관EXISTS는바깥고객과무관하게O전체가비었는지만판단한다.',['O전체존재판정은TRUE다.','바깥각고객에같은TRUE가적용되어두행이남는다.'],'EXISTS가업무관계를검사하려면필요한상관조건을명시해야한다.')
mc(2,13,'set-arity-error','왼쪽 SELECT는 id,name 두 열이고 오른쪽 SELECT는 id 한 열이다. UNION ALL로 결합하려는 문장의 판단은?','열 개수가 달라 집합 연산이 성립하지 않는다',W('ALL이므로열개수가달라도된다','ALL은중복보존옵션이며열구조호환을없애지않는다.','name을자동NULL로추가한다','누락열을자동보충하지않는다.','오른쪽id를두열에복사한다','값을임의복제하지않는다.'),'각행의대응구조가같아야결합할수있다.',['왼쪽열수2와오른쪽1을비교한다.','자료형검토전에열개수조건부터실패한다.'],'UNION ALL에도열개수·대응자료형호환이필요하다.')
mc(2,13,'set-datatype-groups','Oracle19c에서 한 SELECT의 대응 열은 NUMBER, 다른 SELECT의 대응 열은 VARCHAR2 문자열 리터럴이다. 명시 변환 없이 집합 연산에서 이를 무조건 호환된다고 해도 되는가?','안 된다. 숫자와 문자 자료형 그룹의 호환을 명시적으로 맞춰야 한다',W('문자가숫자처럼보이면항상자동호환','집합연산은자료형그룹간암묵변환에제약이있다.','UNION을쓰면모두문자로자동변환','그렇게일반화할수없다.','열별칭을같게하면해결','별칭은자료형호환을바꾸지않는다.'),'Oracle집합연산은대응열의자료형그룹을확인하며명시변환으로의도를표현해야한다.',['대응위치의NUMBER와VARCHAR2를확인한다.','값모양이아니라자료형을맞춘후결합한다.'],'집합연산호환은표시문자모양으로판단하지않는다.')
mc(2,14,'rollup-order-business','지역별 소계가 필요하지만 GROUP BY ROLLUP(store,region)을 사용했다. store가 지역마다 유일한 번호라는 추가 규칙은 없다. 왜 요구와 다를 수 있는가?','중간 소계가 store별이며 region 단독 소계는 생성하지 않는다',W('ROLLUP은키순서를무시한다','접두키소계를만들므로순서에영향받는다.','region이두번째이므로region소계만생긴다','오른쪽키부터빠진다.','전체합계는어떤ROLLUP에도없다','빈그룹전체합계수준이있다.'),'ROLLUP(store,region)은(store,region),(store),()다.',['필요한수준(region)과실제수준(store)을대조한다.','키순서변경이나GROUPING SETS로필요소계를명시해야한다.'],'ROLLUP키순서는단순표시순서가아니라집계수준설계다.')
mc(2,14,'cube-empty-full','입력이 완전히 비어 있는 표에서 CUBE(d)의 그룹 결과를 만든다. GROUPING(d)=1인 전체합계행의 COUNT(*) 값은?','0',W('NULL','COUNT빈입력은0이다.','1','전체합계결과행하나와그안에서센입력행수는다르다.','원본dNULL행수에따라달라진다','입력전체가비어있다는조건이다.'),'빈그룹()전체집계는빈입력의COUNT0을반환한다.',['CUBE(d)에는(d)와()수준이있다.','전체합계수준의입력은0행이라COUNT0이다.'],'전체합계행의존재와집계대상행수를구분한다.')
mc(2,15,'rank-added-key-effect','점수90인 서로 다른 학생id1,2가 있다. RANK의 OVER ORDER BY를 score DESC에서 score DESC,id로 바꾸면 어떤 변화가 생기는가?','점수 동점이 id로 해소되어 서로 다른 순위를 받는다',W('점수가같으므로항상같은순위','RANK는ORDER BY키전체를비교한다.','둘다순위0이된다','순위는1부터다.','출력행이한개로줄어든다','분석순위는행제거집계가아니다.'),'점수만의동점과복합정렬키의동점은다르다.',['복합키는(90,1),(90,2)로서로다르다.','따라서RANK값이1,2로갈라진다.'],'동점보존순위에고유보조키를추가하면업무상동점의미가바뀔수있다.')
mc(2,15,'row-number-where-scope','같은 SELECT 블록에서 계산한 ROW_NUMBER 별칭 rn을 일반 WHERE rn<=3으로 바로 참조하려 한다. 일반적인 수정 방향은?','분석 계산을 안쪽 쿼리에 두고 바깥 WHERE에서 rn을 필터한다',W('ORDER BY만삭제하면rn을WHERE에서사용가능','별칭범위·분석처리단계문제가해결되지않는다.','rn을문자열상수로감싸면동일해진다','별칭이아닌리터럴을비교하게된다.','ROW_NUMBER를SUM으로바꾸면된다','요구한순위선택이아니다.'),'분석계산결과열을다음쿼리블록의입력으로만들어필터할수있다.',['WHERE에서아직그SELECT분석별칭을직접사용하는설계인지확인한다.','인라인뷰에서rn을출력하고외부에서일반열처럼비교한다.'],'분석결과로행을고르려면쿼리블록경계를설계한다.')
mc(2,16,'rows-peers-nondeterminism','id는 고유하지만 분석 ORDER BY에는 중복되는 timestamp만 두었다. ROWS로 현재까지 누적합을 계산할 때 같은 timestamp 행별 누적값의 문제는?','동점 내부 순서가 고정되지 않아 행별 누적값이 달라질 수 있다',W('ROWS가timestamp동점모두를항상동시포함','RANGE동료값기준과혼동했다.','고유id가자동정렬키로추가된다','명시하지않은보조키를보장하지않는다.','SUM은언제나각행원래값만낸다','누적프레임을무시했다.'),'ROWS는물리행위치를사용하므로동점순서를정하지않으면행별창이다르게될수있다.',['같은timestamp두행중어느것이먼저인지미정이다.','행별누적값을안정시키려면id같은보조키로전체순서를정한다.'],'ROWS의재현성에는분석ORDER BY의동점처리가필요하다.')
mc(2,16,'range-offset-keys','숫자 key1,key2 두 열로 분석 정렬하며 RANGE BETWEEN 2 PRECEDING AND CURRENT ROW를 쓰려 한다. Oracle19c에서 먼저 확인할 제약은?','값 오프셋 RANGE에서는 여러 정렬 키 사용이 제한된다',W('모든RANGE프레임은여러키가절대불가능','일부특정경계는복수키를허용한다.','ROWS도항상한키만가능','물리행프레임과값오프셋제약을혼동했다.','정렬별칭을바꾸면제약이사라진다','별칭이범위의미를바꾸지않는다.'),'2 PRECEDING같은값거리는단일정렬키의차이를기준으로하며Oracle문법제약을확인해야한다.',['프레임이값오프셋RANGE인지확인한다.','복수키가허용되는예외경계와현재경계를구별한다.'],'RANGE의복수정렬키허용은프레임경계형태에따라다르다.')
mc(2,17,'with-ties-needs-order','FETCH FIRST 3 ROWS WITH TIES로 동점인 추가 행을 반환하려 한다. 이 의도를 구현하려면 필요한 조건은?','마지막 선택 행과 동점인지 비교할 정렬 키를 ORDER BY로 지정한다',W('기본키의 동점을 자동으로 사용한다','명시하지 않은 기본키를 자동 정렬 기준으로 삼지 않는다.','SELECT의 첫 열을 자동으로 동점 기준으로 사용한다','그런 암묵적 기준은 없다.','ORDER BY를 생략하면 항상 모든 행을 반환한다','ORDER BY를 생략하면 추가 동점 행은 반환하지 않는다.'),'WITH TIES는 마지막 선택 행과 같은 정렬 키를 가진 추가 행을 포함한다. ORDER BY가 없으면 추가 동점 행을 반환하지 않는다.',['반환할 추가 행이 마지막 선택 행과 같은 정렬 키인지 판단해야 한다.','동점을 포함하려는 의도에 맞는 ORDER BY를 지정한다.'],'ORDER BY 생략을 무조건 문법 오류라고 단정하지 말고, 추가 동점 행이 반환되지 않는 동작을 구분한다.')
mc(2,17,'fetch-zero','Oracle19c에서 적법한 정렬 뒤 FETCH FIRST 0 ROWS ONLY를 지정했다. 입력은 여러 행이다. 결과는?','0행',W('첫행한개','0은선택할행수가없다는뜻이다.','모든행','0을제한없음으로해석하지않는다.','NULL한행','행제한은NULL행을생성하지않는다.'),'요청한최대행수가0이므로행을반환하지않는다.',['입력행수와요청행수를분리한다.','선택한계0을적용하면빈결과다.'],'행제한0은무제한이아니라빈결과다.')
mc(2,18,'cycle-without-guard','N의 부모 연결이 1→2→1로 순환한다. 이 경로를 시작점에서 NOCYCLE 없이 계속 확장하려는 Oracle 계층 질의의 위험은?','순환 관계로 오류가 발생할 수 있다',W('LEVEL이자동0으로초기화되어정상완료','그런순환처리규칙이아니다.','DISTINCT가탐색전순환을항상제거','출력중복제거는경로순환제어대체가아니다.','두행중하나를자동삭제','SELECT가원본을삭제하지않는다.'),'계층탐색경로에이미존재하는행으로돌아가는순환은별도처리가필요하다.',['1에서2를따라가고다시1을만나는경로를그린다.','NOCYCLE등의명시한처리없이단순트리라가정하면안된다.'],'계층데이터는트리라는가정을실제관계조건으로확인해야한다.')
mc(2,18,'hierarchy-pruning-location','루트1→중간2→잎3 경로에서 중간2를 통과한 가지 전체를 확장하지 않으려 한다. 단순 WHERE id<>2와 다른 설계가 필요한 이유는?','WHERE의 결과 행 제거만으로 자손 확장 자체를 차단하지 않기 때문이다',W('WHERE는어떤계층쿼리에도쓸수없다','사용가능하지만적용의미가다르다.','START WITH가항상모든행을루트로만든다','명시조건으로루트를고른다.','LEVEL은원본값이라조건에못쓴다','LEVEL은계층의사열이다.'),'경로확장제한은CONNECT BY조건등의관계선택과구별해설계한다.',['행2출력제거와2를통한3도탐색하지않음은다른요구다.','연결확장단계에서제외할조건을명시해야한다.'],'계층의출력필터와가지치기는같지않다.')
mc(2,19,'unpivot-type-family','q1은NUMBER, q2는DATE다. 한 amt 값 열로 UNPIVOT하려는 설계에서 필요한 검토는?','변환할 값 열의 자료형 그룹 호환',W('열이름길이가같아야한다','이름길이는핵심호환조건이아니다.','q1,q2값이우연히하나씩이면된다','행수로자료형호환을해결하지못한다.','UNPIVOT이모두문자로자동변환한다','무조건자동변환으로일반화하면안된다.'),'한출력값열에들어갈여러입력열은호환자료형그룹이어야한다.',['숫자와날짜를같은값열에모을의미를정한다.','필요하면명시변환하되날짜·숫자의원래의미손실을검토한다.'],'형태변환전출력값열의자료형을설계한다.')
mc(2,19,'pivot-implicit-count-star','PIVOT(COUNT(*) FOR mon ...) 입력에 mon 이외에 금액 amt까지 남아 있다. 의도는 shop별 월별 건수인데 결과가 amt별로 나뉜다. 원인은?','COUNT(*)는 amt를 집계 인수 열로 제거하지 않으므로 amt가 암묵 그룹 키로 남는다',W('COUNT가항상SUM으로변환된다','집계함수종류가자동으로바뀌지않는다.','PIVOT은shop열을전혀그룹화할수없다','미참조열이그룹키가된다.','amt가숫자여서항상합계가된다','자료형만으로집계를지정하지않는다.'),'COUNT(*)의입력열사용과암묵그룹규칙을함께읽어야한다.',['FOR열mon을제외한입력shop,amt가남는다.','원하는shop별건수라면입력뷰에불필요한amt를제거한다.'],'PIVOT에들어가는입력열을최소한으로구성한다.')
mc(2,20,'regex-question-mark','ASCII 패턴 ^colou?r$를 c옵션으로 적용한다. color,colour,colouur 중 맞는 문자열은?','color와 colour',W('colour만','?는앞u의0회도허용한다.','세문자열모두','u두개는0회또는1회범위를넘는다.','color와colouur','colouur는u반복2회로불일치다.'),'?는바로앞u의존재를0회또는1회로선택한다.',['u없음color,u한개colour는허용한다.','u두개colouur는허용하지않는다.'],'반복기호가적용되는바로앞요소와횟수범위를읽는다.')
mc(2,21,'insert-default-null','T(id PK, v NUMBER DEFAULT 9)이며 v는NULL허용이다. 첫INSERT는v열을생략하고둘째INSERT는v에명시NULL을넣었다. DEFAULT ON NULL은없다. 두v값은?','생략 행9, 명시 NULL 행NULL',W('두행모두9','일반DEFAULT는명시NULL을자동대체하지않는다.','두행모두NULL','열생략시기본값9가적용된다.','생략행NULL,명시NULL행9','적용상황을뒤집었다.'),'일반DEFAULT의열생략과명시NULL대입은다르다.',['열을생략한행은정의된기본값9를사용한다.','NULL을명시한행은NULL허용이므로그값을저장한다.'],'기본값과NULL대체기능을구별한다.')
mc(2,21,'update-target-key-conflict','T(id PRIMARY KEY)에는1,2가있다. 한 UPDATE로 id1을2로바꾸려한다. 즉시검사제약이며다른조건없다. 결과는?','기본키 중복으로 그 UPDATE가 실패하고 기존 두 행이 유지된다',W('id2기존행을자동덮어쓴다','UPDATE는중복키충돌을자동대체하지않는다.','두id2행을허용한다','PK유일성위반이다.','표전체가자동삭제된다','제약위반은객체삭제가아니다.'),'변경후키2가중복되어제약을만족하지못하므로문장이취소된다.',['기존id2행의존재를확인한다.','id1→2변경이중복을만들어해당문장전체가실패한다.'],'UPDATE도변경후값으로무결성제약을검사한다.')
mc(2,22,'commit-then-savepoint-invalid','SAVEPOINT a 이후 UPDATE하고 COMMIT했다. 바로 ROLLBACK TO a를시도했다. 기대할결과는?','savepoint가 소멸했으므로 되돌릴 수 없다',W('COMMIT전상태로정상복구','COMMIT은트랜잭션과savepoint수명을끝낸다.','새savepoint를자동생성후롤백','존재하지않는지점을자동복원하지않는다.','최근UPDATE가자동취소되어NULL','오류와값치환을혼동했다.'),'COMMIT은현재트랜잭션의모든savepoint를지운다.',['a생성후COMMIT이라는종료경계를확인한다.','다음명령의a는유효하지않으며이미확정한UPDATE는남는다.'],'COMMIT후과거savepoint를복구수단으로사용할수없다.')
mc(2,23,'check-multiple-null','T의 CHECK(a<b)만으로 반드시 a와b가둘다존재하고a가작다는업무규칙을보장하려한다. 추가로필요한것은?','a와 b 각각의 NOT NULL 제약',W('ORDER BY a,b','표시순서는입력무결성을강제하지않는다.','CHECK만으로이미둘다필수','한쪽NULL이면UNKNOWN으로통과할수있다.','두열의이름을같게만들기','열이름은필수입력규칙이아니다.'),'CHECK는UNKNOWN을거부하지않아양쪽필수입력은별도로요구해야한다.',['a나b가NULL이면비교는UNKNOWN이다.','두열NOT NULL과CHECK를함께두어존재와순서규칙을나눈다.'],'논리비교CHECK는NOT NULL의대체가아니다.')
mc(2,24,'role-grant-object-option','관리자는 여러 객체 권한을 역할R에 묶어 B에게 전달하려 한다. 역할의 목적에 가장 맞는 설명은?','권한을 묶어 사용자에게 관리하기 쉽게 부여한다',W('역할은항상표데이터를복사한다','권한관리객체이지데이터복사본이아니다.','역할을받으면모든시스템권한을얻는다','역할에실제로포함된권한범위다.','역할은로그인암호를대신한다','권한묶음과인증수단을혼동했다.'),'역할은허용작업들의묶음이며그실제내용과활성조건을확인해야한다.',['R에들어있는객체·권한목록을확인한다.','R부여로사용자관리의반복을줄이되범위를확대해가정하지않는다.'],'역할의이름보다실제포함권한과활성상태를확인한다.')

mc(3,9,'case-null-order-equivalent','정렬값 x는 NUMBER다. x ASC NULLS FIRST와 같은 NULL 우선 규칙을 CASE로 표현하려 한다. 올바른 정렬 키 조합은?','CASE WHEN x IS NULL THEN 0 ELSE 1 END ASC, x ASC',W('CASE WHEN x IS NULL THEN 1 ELSE 0 END ASC,x ASC','NULL이마지막으로간다.','CASE WHEN x IS NULL THEN 0 ELSE 1 END ASC,x DESC','NULL위치는같지만비NULL방향이반대다.','x ASC만사용','Oracle기본ASC는NULLS LAST다.'),'NULL그룹을작은우선값0으로주고나머지숫자는원래ASC로정렬한다.',['첫CASE키가NULL·비NULL을분리한다.','둘째키가비NULL값의오름차순을결정한다.'],'NULL우선순위와값방향을각각표현하면정렬의미를분해할수있다.')
mc(3,10,'join-exists-equivalence-condition','C의 각 행을 O와 내부 조인한 뒤 C열만 반환하는 결과와 C에서 O의 존재만 검사한 결과가 같은 중복 개수를 가지려면 중요한 조건은?','각 C행에 대해 O의 매칭 행이 최대 한 개여야 한다',W('O에같은고객주문이여러개있어야한다','내부조인만중복C행을만들어차이가난다.','C에NULL열이전혀없어야한다','일반출력NULL은매칭개수조건의핵심이아니다.','두표의전체행수가같아야한다','전체행수같음은각행매칭수를보장하지않는다.'),'EXISTS는바깥행을증식시키지않으므로JOIN과맞추려면매칭다중성을제한해야한다.',['한C행에O가두개매칭되면JOIN은두행,EXISTS는한행이다.','매칭0또는1이면둘의C행중복개수가같아진다.'],'JOIN과EXISTS의동등성에는매칭다중성조건이필요하다.')
mc(3,10,'band-gaps-no-match','등급 구간은[0,10],[20,30] 두 개이며 양끝을 포함한다. 급여15인 직원 한 행을 범위 INNER JOIN한 결과는?','매칭이 없어 0행',W('가까운첫등급으로자동매칭','가장가까운구간선택은정의하지않았다.','둘째등급으로자동매칭','15는하한20미만이다.','NULL등급한행보존','INNER JOIN에는미매칭보존이없다.'),'범위조건을직접만족하는구간이없으며중간공백을자동보정하지않는다.',['15는0~10에도20~30에도속하지않는다.','TRUE행쌍이없어내부조인결과는비었다.'],'등급구간의겹침뿐아니라공백도조인결과에영향을준다.')
mc(3,11,'filtered-count-preserve','모든 고객을 남기면서 유료주문 건수만 세려 한다. LEFT JOIN으로 전체 주문을 붙인 뒤 조건부 COUNT를 쓰는 설계에서 적절한 집계 대상은?','CASE WHEN paid=1 THEN 주문의 비NULL 키 END',W('CASE WHEN paid=1 THEN 1 ELSE 0 END','COUNT는숫자0도세므로비유료까지포함한다.','COUNT(*)만사용','미매칭확장행과비유료행까지센다.','고객키만COUNT','고객키는유료여부와관계없이비NULL이다.'),'COUNT는비NULL을세므로해당조건밖의행은NULL로만들어야한다.',['유료매칭행에는비NULL키를반환한다.','비유료·미매칭행에는NULL이되어COUNT에서제외된다.'],'조건부COUNT의ELSE0은0도세어진다는점을확인한다.')
mc(3,11,'outer-swapped-column-null','A LEFT JOIN B에서 B에 매칭이 없는 A행은 B열이 NULL이다. 표 위치만 B LEFT JOIN A로 바꾸고 나머지를 같은 뜻이라 설명하면 왜 틀릴 수 있는가?','보존되는 입력이 A에서 B로 바뀐다',W('LEFT JOIN은표순서와항상무관하다','방향성있는외부조인이다.','NULL은항상A열에만생긴다','보존방향과미매칭여부에따라다르다.','INNER JOIN으로자동변환된다','문법변경그자체의결과가아니다.'),'LEFT라는단어는구체적인왼쪽입력을보존한다.',['원문왼쪽은A,재작성왼쪽은B다.','미매칭A와미매칭B의보존이바뀌므로일반적으로동등하지않다.'],'외부조인은교환할때보존방향도함께조정해야한다.')
mc(3,12,'in-duplicates-no-extra','A(x)에1,2가 있고 B(v)에2,2,2가 있다. A에서 x IN(B의v)로 고른 결과의 x2는 몇 번 나오는가?','한 번',W('세번','IN은소속조건이며매칭행만큼바깥을증식시키지않는다.','0번','2는목록에존재한다.','두번','A에x2행은한개다.'),'IN의목록중복은참거짓소속판정을증식시키지않는다.',['x1은소속FALSE,x2는TRUE다.','바깥A의x2한행만남는다.'],'IN의비교목록중복과바깥원본중복은별개다.')
mc(3,12,'correlated-min-ties','E(id,d,sal)는(1,7,10),(2,7,10),(3,7,20)이다. 부서별 MIN(sal)와 같은 급여인 모든 행을 상관 서브쿼리로 선택하면?','id1과 id2',W('id1만','최소급여동점행도모두같음조건을만족한다.','id3만','MAX조건이아니다.','스칼라오류','상관MIN집계는부서마다단일값10을반환한다.'),'서브쿼리의최솟값한개와그값을가진바깥행여러개를구별한다.',['부서7의MIN은10이다.','바깥id1,2의sal이10과같으므로둘다남는다.'],'단일스칼라값이바깥행하나만선택한다는뜻은아니다.')
mc(3,12,'exists-null-only-rewrite','B(v)에는NULL만있다. 비상관 EXISTS로 B행존재를묻는것과 숫자1 IN(B의v)를묻는것의판정은?','EXISTS는 TRUE, IN은 UNKNOWN',W('둘다TRUE','1=NULL은TRUE가아니다.','둘다FALSE','NULL값이어도B행은존재한다.','EXISTS는UNKNOWN,IN은FALSE','존재판정과NULL동등비교를뒤집었다.'),'행의존재와값의소속은NULL에서다른논리질문이다.',['B는한행이므로EXISTS는TRUE다.','1 IN(NULL)은1=NULL비교로UNKNOWN이다.'],'EXISTS와IN을치환하려면검사하려는의미와NULL조건을확인한다.')
mc(3,13,'intersection-symmetry','같은 호환 열 구조의 결과 A,B에 대해 A INTERSECT B와 B INTERSECT A를 정렬 없는 중복 제거 집합으로 비교하면?','같은 행 집합이다',W('항상반대부호가된다','집합행에숫자부호변환을하지않는다.','A가더많은행이면첫식만중복유지','INTERSECT는방향에관계없이중복제거한다.','NULL이있으면반드시다르다','양쪽공통NULL행의집합취급은대칭이다.'),'공통행이라는조건은양쪽입력의위치를바꾸어도동일하다.',['양쪽모두에존재하는행만선택한다.','A에도있고B에도있음은B에도있고A에도있음과같다.'],'INTERSECT의대칭성과MINUS의방향성을구분한다.')
mc(3,13,'difference-reconstruct-union','A에1,1,2, B에2,3이있다. (A MINUS B) UNION (A INTERSECT B)의 결과는?','1,2 각 한 행',W('1,1,2 세행','중복제거집합연산들의조합이다.','1,2,3 각한행','B에만있는3은어느부분에도포함되지않는다.','2만한행','차집합부분의1도합쳐진다.'),'A를B와공통인부분과아닌부분으로나눴다다시합치면A의서로다른행집합이다.',['A MINUS B는1,교집합은2다.','두부분UNION은1,2로A의중복제거결과와같다.'],'집합분해·재결합은중복보존까지복구하지는않는다.')
mc(3,14,'summing-rollup-double','d1의원본금액10,20을ROLLUP(d)로집계하면상세소계30과전체합계30이있다. 이두집계결과의SUM을다시구해원본총액이라고하면?','60으로 이중 계산되어 원본 총액30과 다르다',W('항상30이므로올바르다','서로겹치는집계수준을모두더했다.','0이된다','합계행을자동제외하지않는다.','NULL이된다','두집계값모두30으로비NULL이다.'),'여러집계수준은같은원본행을반복포함하므로모두더하면중복계산된다.',['부서소계30과전체합계30이동일원본을포함한다.','결과행SUM은30+30=60이므로한수준만선택해야한다.'],'소계와총계를다시모두더하면같은원본을중복계산할수있다.')
mc(3,14,'grouping-null-count-fields','NULL부서에금액NULL한행이있다. ROLLUP(d)의실제NULL그룹에서COUNT(*)와COUNT(amount),GROUPING(d)는?','(1,0,0)',W('(0,0,1)','실제원본그룹한행이며집계생성NULL이아니다.','(1,1,0)','금액NULL은COUNT(amount)에서제외된다.','(1,0,1)','GROUPING1은전체합계수준이다.'),'원본NULL그룹의존재와금액NULL,그룹수준표시를각각판단한다.',['실제dNULL행하나가그룹을만들어COUNT(*)1이다.','amount는NULL로COUNT0이며d는그룹키로남아GROUPING0이다.'],'NULL의열별역할과소계용NULL표시를함께구분한다.')
mc(3,15,'ntile-more-buckets','행이3개이고고유id순으로NTILE(5)를계산한다. 실제반환버킷번호는?','1,2,3',W('1,3,5','빈버킷을중간에교대로끼우지않는다.','1,1,1','버킷수5는최대한나누는요청이다.','1,2,3,4,5다섯행','분석함수는없는원본행을생성하지않는다.'),'버킷수가행수보다크면실제행에는앞번호버킷이하나씩배정된다.',['세행을첫세버킷에한개씩배분한다.','남은버킷은행을생성하지않아표시되지않는다.'],'NTILE은행수보다많은출력행을만들지않는다.')
mc(3,15,'null-partition-count','d가NULL인행두개와d1행한개가있다. COUNT(*) OVER(PARTITION BY d)를계산할때NULL행에붙는값은?','각 NULL 행에2',W('각NULL행에1','분석PARTITION에서NULL값들은같은그룹으로묶인다.','각NULL행에0','COUNT(*)는NULL키행도센다.','모든행에3','PARTITION BY를무시했다.'),'NULL파티션은두행으로구성되어각행에같은개수2가붙는다.',['d1파티션과dNULL파티션을나눈다.','NULL파티션의행두개를COUNT(*)로센다.'],'그룹·파티션의NULL묶음과WHERE등호UNKNOWN을혼동하지않는다.')
mc(3,16,'range-current-peers-only','k,v 행이 (1,5),(1,7),(2,10)이다. SUM(v) OVER(ORDER BY k RANGE BETWEEN CURRENT ROW AND CURRENT ROW)를 계산하면 k=1인 두 행에 붙는 값은?','각각12',W('5와7각각','물리한행ROWS창과다르다.','각각22','현재값1과다른k2는범위밖이다.','각각0','현재값동료행들이프레임에있다.'),'RANGE의양끝현재값은같은정렬값의동료행전체를포함한다.',['현재k1과같은값1두행을찾는다.','v5+7=12를두행에동일하게붙인다.'],'RANGE CURRENT ROW는반드시물리한행이아니다.')
mc(3,16,'moving-average-null-denominator','고유id순v값은10,NULL,30이다. 현재와앞한행ROWS프레임의AVG(v)에서마지막행값은?','30',W('15','NULL을0으로보고분모2로나누지않는다.','20','두행전10은현재창밖이다.','NULL','NULL이섞였다는이유로AVG전체가NULL이되지는않는다.'),'마지막창은NULL과30이며AVG는비NULL30한개만계산한다.',['프레임에들어오는두행을먼저선택한다.','AVG분모는비NULL값수1이고분자30이므로30이다.'],'윈도우AVG의분모도비NULL집계값개수다.')
mc(3,17,'offset-beyond-result','필터 후 결과가3행인데 안정정렬 뒤 OFFSET 5 ROWS FETCH NEXT 2 ROWS ONLY를적용했다. 결과는?','0행',W('마지막두행을반환','OFFSET은뒤에서세는명령이아니다.','앞에서다시순환해두행','결과가끝나면순환하지않는다.','NULL두행생성','부족분을NULL행으로채우지않는다.'),'건너뛸개수가결과행수보다커남은행이없다.',['정렬된3행을모두지난뒤아직OFFSET이남는다.','반환할입력이없으므로빈결과다.'],'행제한은부족분을중복·가상행으로채우지않는다.')
mc(3,17,'percent-rounding','Oracle19c에서 결과7행에 FETCH FIRST 50 PERCENT ROWS ONLY를 적용한다. 양수비율이고그외필터없다. 선택행수는?','4행',W('3행','계산한3.5행은다음정수로올림한다.','7행','50퍼센트제한을무시했다.','0행','소수행결과가빈결과를뜻하지않는다.'),'7×50%=3.5이며행수는위정수4로올림된다.',['비율을행수에곱하여3.5를얻는다.','Oracle의비율행제한반올림이아닌올림규칙을적용한다.'],'PERCENT행제한의정수화규칙을DBMS문서로확인한다.')
mc(3,18,'overlapping-starts','N은1→2→3의연결이며START WITH가id1과id2를모두선택한다. 같은id3이결과에여러번나올수있는가?','가능하다. 서로 다른 시작 경로에서 각각 도달할 수 있다',W('불가능.id가유일하면출력도자동유일','원본키유일성이여러탐색경로의출력중복을없애지않는다.','SELECT가id3원본을복제저장한다','반환중복과데이터저장은다르다.','항상순환오류다','중복시작경로와사이클은다르다.'),'시작점1경로와시작점2경로가같은자손3에도달한다.',['루트1의경로1→2→3에서id3이한번나온다.','루트2의경로2→3에서도다시나오며이번LEVEL은다르다.'],'원본키유일성과경로별결과유일성은별개다.')
mc(3,18,'level-not-global-number','두 루트의 각 자식 한 명씩을 포함한 숲에서 LEVEL=2로 필터하면 무엇을 뜻하는가?','각 시작 루트에서 한 단계 아래인 모든 행',W('최종표시순서두번째한행','LEVEL은ROWNUM이아니다.','id값2인행만','깊이와식별자는다르다.','모든잎행','잎은다른깊이에도있을수있다.'),'LEVEL은각경로의상대깊이이며여러루트에서같은값을가질수있다.',['루트마다LEVEL1부터깊이를계산한다.','LEVEL2는각루트의직접자식단계다.'],'LEVEL조건은순번·식별자·잎조건과다르다.')
mc(3,19,'pivot-unlisted-category','shop1의mon1금액10,mon3금액30이있다. PIVOT은SUM(amt)를mon IN(1 AS m1,2 AS m2)로만펼친다. 출력월열은?','m1=10, m2=NULL이며 mon3용 열은 생성되지 않는다',W('m1=10,m2=30','목록밖mon3을월2에옮기지않는다.','m1=40,m2=40','FOR범주별집계구분을무시했다.','자동m3열30이추가된다','일반명시IN목록이자동동적확장을하지않는다.'),'명시한PIVOT범주목록에대해서만출력열을만든다.',['mon1은m1집계에포함되고mon2입력은없다.','mon3은명시된출력범주에없으므로새열이되지않는다.'],'PIVOT IN목록밖의범주가자동열로추가된다고가정하지않는다.')
mc(3,19,'pivot-count-expression-null','shop1·mon1의amt가NULL,NULL이고mon2의amt는5다. COUNT(amt) PIVOT의m1,m2값은?','0,1',W('2,1','COUNT(*)와COUNT(amt)를혼동했다.','NULL,1','COUNT의빈비NULL입력결과는0이다.','2,5','COUNT를행수·금액합으로섞었다.'),'COUNT(amt)는각범주의비NULL값만센다.',['mon1두행은amt가모두NULL이라COUNT0이다.','mon2에는비NULL5한개이므로COUNT1이다.'],'PIVOT의집계인수를확인해야행수와값수를구분할수있다.')
mc(3,20,'regex-repeat-bounds','정규식 ^[A-Z]{2,3}[0-9]{2}$, c옵션을 적용한다. AB12,ABC12,AB123 중 일치하는 문자열은?','AB12와 ABC12',W('AB12만','영문3자도{2,3}범위다.','세문자열모두','숫자는정확히2자여야해AB123은실패한다.','ABC12와AB123','AB12도정상이며AB123은숫자수가많다.'),'앞영문은2~3개,뒤숫자는정확히2개이며양끝이전체를제한한다.',['문자종류별개수를나누어센다.','AB12는2+2,ABC12는3+2로성공하고AB123은2+3으로실패한다.'],'반복범위는각바로앞패턴에따로적용한다.')
mc(3,21,'delete-exists-no-cascade','고객 C에1,2가 있고 주문 O에는고객1의행이있다. 주문존재가TRUE인고객을DELETE했다. FK·트리거·연쇄삭제는없다. O의행은?','그대로 남는다',W('고객삭제가언제나주문도삭제','연쇄삭제조건이없다.','고객번호가자동NULL','SET NULL참조옵션도없다.','새고객2에게자동이동','관계를재배정하는명령이아니다.'),'DELETE대상은고객표이며존재검사에읽은표를자동변경하지않는다.',['O는고객1의대상선택근거로읽었다.','실제변경대상C에서만행을지우며O는유지된다.'],'DML의변경대상과조건검사에읽은입력을구분한다.')
mc(3,21,'insert-from-self-count','T에1,2두행이있고중복허용이다. T를한번읽은SELECT의각v+10을같은T에INSERT하는단일문장을실행했다. 새로추가하는값은?','11과12 두 값',W('11,12,21,22를계속생성','단일INSERT SELECT가새로넣은행을무한재입력하지않는다.','1과2','SELECT의+10계산을누락했다.','10한행','원본각행의값을사용한다.'),'단일문장의SELECT가정의한입력두행에서변환한결과두행을삽입한다.',['기존읽기대상v1,2에각10을더한다.','결과11,12를추가하며같은문장삽입분을재귀반복하지않는다.'],'INSERT SELECT와재귀반복작업은서로다르다.')
mc(3,22,'rollback-later-savepoint','SAVEPOINT a 후변경, SAVEPOINT b 후변경을했다. ROLLBACK TO a 이후 b로다시ROLLBACK TO하려한다. b의상태는?','a 이후의 savepoint b는 소멸하여 유효하지 않다',W('b가남아취소한변경을자동다시살린다','롤백이전진복구기능을제공하지않는다.','b가자동COMMIT된다','savepoint는확정단위가아니다.','a도반드시COMMIT되어끝난다','부분롤백은트랜잭션을종료하지않는다.'),'이른지점으로부분롤백하면그뒤의변경과그뒤savepoint도제거된다.',['시간순서a→b를확인한다.','a로되돌린후a보다뒤의b는더이상유효하지않다.'],'부분롤백후남아있는savepoint의범위를확인한다.')
mc(3,23,'composite-primary-key','PRIMARY KEY(year,no)인 표에(2025,1),(2026,1)이있다. 각열단독중복과키유일성의판정은?','no가 같아도 두 열 조합이 달라 허용된다',W('no1중복만으로반드시실패','복합PK의유일성은조합전체기준이다.','year열은PK에포함되어도NULL허용','PK구성열은NULL불가다.','복합PK는두열모두각각UNIQUE를자동요구','각단독유일성과복합유일성은다르다.'),'두행의전체키(2025,1),(2026,1)는서로다르다.',['복합키구성열을빠짐없이비교한다.','no부분이같더라도year가달라키중복이아니다.'],'복합키는전체조합의유일성과각구성열비NULL을요구한다.')
mc(3,24,'insert-select-source-right','B가 대상D의INSERT권한은있지만소스S의SELECT권한은없다. S를조회한결과를D에INSERT하려면현재부족한능력은?','S를 읽는 SELECT 권한',W('D의INSERT권한을한번더주기','이미있는대상권한을반복해도소스접근문제를해결하지못한다.','S의DELETE권한','소스행을삭제할요구가아니다.','D의DROP권한','대상구조제거와무관하다.'),'데이터이동문장은대상변경권한과소스읽기권한을각각필요로한다.',['D쓰기경로는허용되어있다.','S를읽는단계가권한부족이므로그권한을검토해야한다.'],'한문장이여러객체를다룰때각객체의작업권한을분리한다.')

mc(4,9,'collation-condition','한국어·영문·대소문자가 섞인 이름을 정렬한 정확한 순서를 문항의 정답으로 정하려 한다. 입력 문자와 ASC만 제시했을 때 추가로 확인할 조건은?','적용 collation과 문자 정렬 관련 세션 조건',W('행을 삽입한 날짜만','삽입 시각은 문자 비교 규칙을 결정하지 않는다.','테이블 파일 크기만','물리 파일 크기는 문자 정렬 의미가 아니다.','열 별칭의 길이만','별칭 길이는 값 비교 규칙과 무관하다.'),'문자 정렬 결과는 적용한 비교·정렬 규칙에 영향을 받을 수 있다.',['숫자 순서와 문자 언어별 정렬의 차이를 구분한다.','정확한 문자 출력 순서를 채점하려면 해당 정렬 환경을 명시해야 한다.'],'정확한 문자열 순서를 묻는 문제는 정렬 환경을 빠뜨리지 않는다.')
mc(4,10,'multi-stage-cartesian','고객1의 주문이2개이고 연락처가3개다. 고객→주문, 고객→연락처를 각각 키로 내부 조인한다. 주문과 연락처 사이 추가 연결 조건은 없다. 고객1의 결과 행 수는?','6행',W('5행','두 자식 집합의 행 수를 더하지 않는다.','3행','각 연락처에 주문2개씩 조합된다.','2행','연락처 다중성이 결과에 반영된다.'),'독립적인 두 일대다 관계를 한 결과에 붙이면 자식 사이 가능한 조합이 생긴다.',['고객1과 주문 조인으로 두 행을 만든다.','각 행이 연락처 세 행과 결합하여2×3=6행이다.'],'여러 자식 표를 함께 조인할 때 조합에 의한 행 증가를 확인한다.')
mc(4,10,'join-range-time-exclusive','시간 구간 G는 [0,10),[10,20)로 설계했다. 시점10인 이벤트를 시작 이상·끝 미만 조건으로 조인하면?','두 번째 구간 한 개와 매칭',W('양쪽 구간 두 개와 매칭','첫 구간의 끝10은 미포함이다.','첫 번째 구간만 매칭','첫 구간은10 미만을 요구한다.','어느 구간과도 매칭되지 않음','두 번째 구간은 시작10을 포함한다.'),'반열린 구간이 경계값의 이중 매칭을 피한다.',['첫 구간은10<10이 거짓이라 탈락한다.','두 번째는10>=10과10<20이 모두 참이다.'],'시간 구간의 포함·미포함 경계를 조인 조건에 그대로 반영한다.')
mc(4,11,'left-chain-preservation','A에1,2가 있고 B는A1에 연결된 한 행만 있으며 C는 비어 있다. A LEFT JOIN B 뒤 C를 B키로 INNER JOIN했다. 최종 A행은?','모두 사라져0행',W('A1,A2가 항상 보존된다','뒤의 INNER JOIN은 매칭 없는 중간 행을 제거한다.','A1만 남는다','C가 비어 A1도 매칭할 수 없다.','A2만 남는다','NULL 확장 B키도 C와 매칭되지 않는다.'),'앞선 LEFT 보존이 뒤의 모든 연산에서 자동 유지되는 것은 아니다.',['첫 LEFT 결과에는A1 매칭 행과A2 NULL 확장 행이 있다.','빈 C와의 INNER JOIN에서 두 행 모두 매칭이 없어 제거된다.'],'여러 조인을 연결할 때 각 단계의 보존 여부를 차례로 확인한다.')
mc(4,11,'outer-filter-left-on','A의행1,2를 B에 LEFT JOIN하면서 ON에 A.id=1을 추가했다. B에는 두 id와 각각 매칭할 행이 있다. 최종 WHERE는 없다. A.id2는?','B열이 NULL인 미매칭 행으로 남는다',W('ON에서 탈락하므로 A행도 제거된다','LEFT는 매칭하지 못한 A행을 보존한다.','id1로 값이 바뀐다','ON은 키 값을 변경하지 않는다.','B의id2와 정상 매칭된다','ON의A.id=1 조건이 거짓이다.'),'ON의 왼쪽 조건은 매칭을 제한하지만 왼쪽 행 보존 자체를 없애지 않는다.',['A2는A.id=1이 거짓이어서 어떤 B와도 매칭하지 못한다.','LEFT의 미매칭 보존 단계에서A2와NULL B열을 반환한다.'],'왼쪽 행 제거 요구와 ON의 왼쪽 조건 추가는 다르다.')
mc(4,12,'in-outer-duplicates','A(x)에2,2,3이 있고 B(v)에2가 있다. A에서 x IN(B.v)를 만족한 행의 COUNT(*)와 COUNT(DISTINCT x)는?','(2,1)',W('(1,1)','IN은 바깥 원본의 중복 행을 제거하지 않는다.','(2,2)','DISTINCT x는 두2값을 하나로 센다.','(3,2)','3은 B에 없어 필터를 통과하지 않는다.'),'목록 소속 판정은 바깥 중복 보존과 별개다.',['A의 두2행이 각각 TRUE로 생존하고3은 탈락한다.','남은 행은2개이고 서로 다른 x값은 하나다.'],'IN은 집합 조건이지만 바깥 SELECT를 자동 DISTINCT로 만들지 않는다.')
mc(4,12,'correlated-grand-average-choice','직원 E에서 각 직원 급여와 전체 직원 평균을 비교하려 한다. 서브쿼리에 바깥 직원 id와 같은 id 조건을 추가하면 어떤 오류가 생길 수 있는가?','전체 평균 대신 그 직원 자신의 급여 평균과 비교하게 된다',W('전체 평균은 상관 조건과 무관하다','WHERE가 집계 대상을 제한한다.','급여가 자동0이 된다','상관 조건은 값 치환이 아니다.','id가 유일하면 여러 행 오류만 생긴다','고유id이면 오히려 최대 한 직원으로 제한된다.'),'상관 조건의 범위가 업무상 비교 기준을 바꾼다.',['요구한 평균은 전체 E행을 대상으로 한다.','id를 현재 직원으로 묶으면 자신만 남아 비NULL 급여는 자기 자신과 비교하게 된다.'],'상관 서브쿼리의 연결 조건이 집계 모집단을 바꾸는지 확인한다.')
mc(4,12,'exists-all-null-policy','모든 검사 결과가 pass=1인 대상을 찾고 싶고 pass NULL은 미검사라 실패로 취급한다. NOT EXISTS의 위반 조건으로 적절한 것은?','pass<>1 OR pass IS NULL',W('pass<>1만 사용','NULL 비교는 UNKNOWN이라 미검사를 위반 행으로 잡지 못한다.','pass=1만 사용','성공 행의 부재를 검사하는 반대 의미가 된다.','pass IS NOT NULL만 사용','실패0과 성공1을 모두 위반으로 잡는다.'),'업무에서 NULL을 실패로 정했으면 3값 논리의 UNKNOWN을 별도로 포함해야 한다.',['위반은 비1 값과 NULL 두 종류다.','두 종류를 OR로 묶고 그런 행의 NOT EXISTS를 검사한다.'],'모든 조건 검사는 NULL의 업무 의미를 명시해야 한다.')
mc(4,13,'union-count-distinct-null','A(v)는NULL,NULL이고 B(v)는NULL이다. UNION으로 합친 결과의 COUNT(*)와 COUNT(v)는?','(1,0)',W('(3,0)','UNION ALL처럼 원본 NULL행을 모두 유지했다.','(1,1)','COUNT(v)는 NULL값을 세지 않는다.','(0,0)','UNION은 NULL행을 아예 제거하지 않는다.'),'NULL 중복은 한 행으로 합쳐지지만 그 값은 여전히 NULL이다.',['UNION 후 NULL 한 행이 남는다.','COUNT(*)는 그 행을 세고 COUNT(v)는 NULL을 제외한다.'],'집합의 NULL 중복 제거와 집계의 NULL 제외는 다른 단계다.')
mc(4,13,'minus-column-order','A의행(a,b)=(1,2), B의행(a,b)=(2,1)이다. A에서 a,b를 선택하고 B에서 b,a를 선택한 뒤 MINUS하면?','0행',W('(1,2) 한 행','B의 SELECT가 열 순서를 바꾸어(1,2)를 반환한다.','(2,1) 한 행','왼쪽에 없는 행을 MINUS가 추가하지 않는다.','(1,2),(2,1) 두 행','차집합이 아니라 원본 모음으로 읽었다.'),'집합 연산은 원본 열 이름보다 SELECT 대응 위치의 값을 비교한다.',['A 투영은(1,2)다.','B의 b,a 투영도(1,2)이므로 왼쪽 행이 제외된다.'],'집합 연산은 SELECT 열의 순서에 민감하다.')
mc(4,14,'cube-versus-explicit-union','GROUPING SETS((a),(b))는 전체 합계와 상세(a,b)를 모두 생략하려는 요구다. CUBE(a,b)로 교체하면?','원하지 않은 상세(a,b)와 전체() 수준이 추가된다',W('언제나 동일하다','CUBE는 모든 부분집합 수준을 만든다.','a별 그룹만 남는다','두 키 CUBE에는b별 그룹도 있다.','모든 소계가 사라진다','집계 수준을 더 넓게 만드는 변화다.'),'명시한 두 수준과 모든 부분집합 네 수준은 다르다.',['요구는(a),(b) 두 수준뿐이다.','CUBE는 여기에(a,b),()를 더 만든다.'],'간결한 문법으로 바꾸기 전에 실제 집계 수준 집합을 대조한다.')
mc(4,14,'having-level-total-filter','부서별 소계와 전체 합계를 만들고 합계가50 이상인 결과 행만 HAVING으로 남긴다. d1=30,d2=40이면 남는 행은?','전체 합계70 한 행',W('d1과d2 두 행','각 소계는50 미만이다.','0행','전체 수준70도 HAVING의 검사 대상이다.','d2=40 한 행','최대값을 고르는 조건이 아니라50 이상 조건이다.'),'HAVING은 생성된 각 집계 수준의 집계값에 적용된다.',['소계30,40과 전체70을 먼저 계산한다.','50 이상은70만 만족한다.'],'소계 쿼리의 HAVING은 전체 합계 행에도 적용될 수 있다.')
mc(4,15,'rank-null-desc-oracle','Oracle 점수 DESC 순위에서 NULLS 옵션을 생략했다. 점수는90,NULL,80이고 RANK를 계산한다. NULL행이 먼저 순위1을 받을 수 있는 이유는?','Oracle DESC의 기본 NULL 위치가 FIRST이기 때문이다',W('NULL이 숫자100으로 변환되기 때문','정렬 위치와 값 변환은 다르다.','RANK가 NULL을 언제나 제외하기 때문','NULL행도 분석 대상이며 제외 규칙이 아니다.','NULL행은 순위가 항상NULL이기 때문','정렬된 행으로 순위를 받을 수 있다.'),'순위 계산의 정렬에도 DBMS의 NULL 기본 배치가 영향을 준다.',['DESC와 NULLS 옵션 생략을 확인한다.','Oracle은 NULL을 앞에 두므로 필요하면 NULLS LAST를 명시해야 한다.'],'점수 순위에서는 NULL 점수의 업무상 위치를 명시한다.')
mc(4,15,'ntile-tie-split','같은 점수90인 사람 네 명에 고유id 보조 정렬로 NTILE(2)를 계산했다. 점수 동점자들이 같은 버킷에 모두 남는가?','아니다. NTILE은 행 수를 나누므로 두 버킷으로 갈릴 수 있다',W('그렇다.모든 분석 함수는 점수 동점을 보존한다','NTILE과 순위 함수의 목적이 다르다.','모든행은 버킷0이 된다','버킷 번호는1부터 시작한다.','원본행 두 개만 남는다','분석함수는 행을 제거하지 않는다.'),'NTILE은 정렬된 행 수를 균등하게 나누는 기능이다.',['네 행을 두 버킷에 두 개씩 배분한다.','점수가 같아도 행 위치에 따라 서로 다른 버킷이 된다.'],'동일 값 그룹 보존과 균등 행 분할은 다른 요구다.')
mc(4,16,'sum-empty-following-frame','고유id순 마지막 행에서 ROWS BETWEEN 1 FOLLOWING AND 2 FOLLOWING으로 SUM(v)를 계산한다. 뒤 행이 전혀 없으면 값은?','NULL',W('0','SUM의 빈 입력은 COUNT처럼0이 아니다.','현재v값','현재 행은 프레임에 포함하지 않았다.','마지막 앞행값','FOLLOWING은 뒤쪽 방향이다.'),'마지막 행의 다음 두 위치는 존재하지 않아 프레임이 비었다.',['시작도1 FOLLOWING이어서 현재 행은 제외한다.','존재하는 행이 없는 SUM은 NULL이다.'],'빈 프레임의 집계 결과는 집계 함수별로 구분한다.')
mc(4,16,'range-date-distance','시간이10:00,10:30,12:00인 세 행을 시간순으로 분석한다. 현재 시각 기준 앞1시간 RANGE와 앞1행 ROWS가 12:00행에서 다를 수 있는 이유는?','앞 행10:30은 한 행 전이지만1시간 범위 밖이다',W('시간이 날짜 자료형이면 ROWS를 쓸 수 없다','ROWS는 정렬된 행 위치를 다룬다.','RANGE는 언제나 앞 한 행만 포함한다','값 거리 기준이다.','두 프레임은 행 수가 같으면 항상 같다','시간 간격의 크기가 다를 수 있다.'),'물리 이웃 위치와 시간 값의 거리가 일치하지 않는다.',['12:00의 앞1시간 범위 하한은11:00이다.','앞 행10:30은 ROWS에는 들어가지만 그 RANGE에는 빠진다.'],'시간 이동 창은 최근 몇 건과 최근 얼마 동안인지 구분한다.',extra=['시간은 같은 날짜이며 시간대 변화는 없다. 실제 RANGE 식은 적합한 INTERVAL 자료형으로 작성한다.'])
mc(4,17,'ties-composite-key','score DESC, id ASC로 정렬했으며 id는 고유다. FETCH FIRST 2 ROWS WITH TIES가 두 행보다 더 반환할 가능성은?','고유 id가 전체 정렬 키에 포함되어 추가 동점이 없다',W('score만 같으면 무조건 더 반환한다','WITH TIES는 정렬 키 전체를 비교한다.','항상 입력 절반을 더 반환한다','그런 규칙은 없다.','WITH TIES는 id열을 자동 무시한다','명시한 정렬식 모두가 동점 기준이다.'),'복합 키에 고유 id가 있어 서로 다른 행의 전체 키가 같지 않다.',['경계 행의 score와id를 함께 비교한다.','다른 행은id가 다르므로 복합 키 동점이 될 수 없다.'],'WITH TIES에 고유 키를 넣으면 업무상 점수 동점 확장이 사라질 수 있다.')
mc(4,17,'top-average-stage','상위10명의 평균 점수를 원한다. 전체 점수의 AVG를 먼저 한 행으로 만든 뒤 FETCH10을 붙이는 설계의 문제는?','이미 전체 평균 한 행이 되어 상위10명 선택을 수행하지 못한다',W('AVG는 반드시10행을 반환한다','그룹 없는 AVG는 한 행 집계다.','FETCH가 집계 이전 원본을 자동 다시 고른다','쿼리 단계의 의미를 그렇게 되돌리지 않는다.','ORDER BY를 없애면 상위10명이 된다','상위 기준을 더 잃는다.'),'요구는 상위 행 선택 후 그 선택 집합의 평균이다.',['안쪽에서 점수순 상위10명 행을 선택한다.','바깥에서 그 행들의 AVG를 계산하도록 집계 단계를 배치한다.'],'상위행 집계는 행 선택과 집계 순서가 결과를 결정한다.')
mc(4,18,'siblings-non-global-order','루트1 아래 자식2,3이 있고2 아래 자식4가 있다. ORDER SIBLINGS BY id DESC를 사용했다. 정렬의 직접 대상은?','같은 부모의 자식끼리이며 전체 id 내림차순과는 다르다',W('모든 행을4,3,2,1로 재배열','전체 ORDER BY와 혼동했다.','LEVEL값만 내림차순','정렬식은id다.','자식 없는 행만 정렬','형제 관계의 정렬이며 잎만 한정하지 않는다.'),'SIBLINGS는 부모별 형제 묶음 안에서 순서를 조절한다.',['루트1의 자식3,2를 id DESC로 정한다.','2의 자식4는2의 하위 경로에 남으므로 전체 전역 정렬과 다르다.'],'계층 형태를 유지하는 형제 정렬과 전체 결과 정렬을 구분한다.')
mc(4,18,'manager-count-self','직원 E(id,manager_id)는(1,NULL),(2,1),(3,1),(4,2)다. 상사 역할 m에 직속 부하 e를 LEFT JOIN하고 COUNT(e.id)하면 상사id2의 값은?','1',W('2','id2의 부하는id4 한 명이며 자신을 세지 않는다.','3','간접 부하까지 전체 조직을 세는 질의가 아니다.','0','id4의manager_id는2다.'),'셀프 조인의 직접 연결만 집계하므로 id4 한 행이 대상이다.',['e.manager_id=m.id 조건에서m2에 연결되는 e를 찾는다.','id4 한 행의 비NULL id를 COUNT해1이다.'],'직속 부하 집계와 모든 자손 집계는 다른 질의다.')
mc(4,19,'unpivot-count-roundtrip','원본 한 행의 q1=10,q2=NULL을 기본 UNPIVOT한 뒤 분기별 COUNT(*) PIVOT으로 되돌렸다. 원본 q1,q2 금액을 복원했다고 할 수 없는 이유는?','집계가 금액 대신 건수를 만들고 NULL 분기 행도 사라졌기 때문이다',W('UNPIVOT은 어떤 데이터에서도 오류다','적법한 변환이다.','PIVOT은 항상 기존 숫자를 그대로 복원한다','COUNT는 값이 아니라 건수를 계산한다.','NULL이 자동10으로 바뀌기 때문이다','그런 값 복제 규칙은 없다.'),'방향을 되돌려도 중간 NULL 처리와 집계함수가 다르면 원래 값이 복원되지 않는다.',['UNPIVOT 후 q1 금액10 한 행만 남는다.','COUNT로 펼치면 q1의 개수1을 계산하므로 금액10과 다르다.'],'변환의 역방향 문법과 정보 보존은 별도로 검증한다.')
mc(4,19,'pivot-two-measures','월별 매출 금액과 건수를 함께 보고 싶다. PIVOT에서 SUM(amount)와 COUNT(*) 두 집계를 사용하면 각 월에 무엇이 필요할 수 있는가?','서로 구별되는 두 집계 결과 열 이름',W('두 집계는 자동 같은 값이 된다','금액합과 건수는 다른 지표다.','COUNT가 있으면SUM이 무시된다','여러 집계를 사용할 수 있다.','월 구분이 완전히 사라진다','FOR 범주별 집계 구조가 유지된다.'),'같은 범주에서 다른 집계 지표를 반환하므로 결과 열을 명확히 구별해야 한다.',['각 월마다 금액합과 행수를 각각 계산한다.','집계 별칭을 사용해 의미와 열 이름 충돌을 분명히 한다.'],'PIVOT의 여러 집계는 각 출력 열의 의미를 구분해 표시한다.')
mc(4,20,'regex-space-not-trim','txt는 앞 공백 한 개 뒤에123이다. c옵션의 ^[0-9]+$ 패턴은 TRIM없이 일치하는가?','아니다. 시작 공백이 숫자 조건에 맞지 않는다',W('일치한다.정규식이 자동TRIM한다','공백을 제거하는 함수를 호출하지 않았다.','일치한다.앵커는공백을무시한다','앵커는문자열경계를지정한다.','NULL로 변환되어 행이 사라진다','비어 있지 않은 공백 포함 문자열이다.'),'전체 문자열 검사에서 공백도 실제 입력 문자다.',['첫 문자는 숫자가 아닌 공백이다.','^부터 숫자 한 개 이상만 허용하므로 실패한다.'],'정규식 검색에 전처리가 포함됐는지 명시적으로 확인한다.')
mc(4,21,'update-correlated-all-null','별도 원본 S(dept,salary)는 salary의 NULL을 허용한다. S에서 부서 A의 두 행은 급여가 모두 NULL이다. 갱신 대상 E의 부서 A 직원은 현재 급여 100이고 E.salary에는 NOT NULL 제약이 있다. UPDATE로 이 직원의 급여에 S의 해당 부서 AVG(salary)를 대입한다. 트리거가 없고 제약을 즉시 검사할 때 결과는?','NULL 대입이 NOT NULL을 위반해 문장이 실패한다',W('평균이 없으면 자동0을 저장','AVG는0대체를수행하지않는다.','기존급여를자동유지','NULL대입을건너뛰는규칙이없다.','NOT NULL이 자동 해제된다','DML이제약정의를그렇게바꾸지않는다.'),'집계결과NULL과대상열제약을함께확인해야한다.',['전체NULL입력의AVG는NULL이다.','그값을NOT NULL열에넣으려하므로즉시제약검사에서실패한다.'],'DML대입식의NULL가능성과대상열제약을함께검토한다.',extra=['문항의 평균 소스는 별도 보정 자료이며 대상 급여열과 다른 입력이다. 즉시 검사 제약, 트리거 없음.'])
mc(4,21,'delete-having-target','고객별 주문수가2개이상인고객의주문을모두삭제하려한다. 먼저GROUP BY/HAVING으로대상고객id를구하고DELETE의IN조건에서사용한다. 고객1은주문3개,고객2는1개다. 삭제되는행수는?','고객1의 주문3행',W('고객별요약행1개만삭제','DELETE대상은원본주문표이고id소속으로모든해당행을선택한다.','전체주문4행','고객2는HAVING조건에미달한다.','고객1의첫2행만삭제','HAVING>=2는개별삭제행수제한이아니다.'),'집계로고객집합을선택한뒤그고객에속한원본행전체를삭제한다.',['HAVING을통과한고객집합은{1}이다.','DELETE에서cid1인원본주문세행이대상이된다.'],'그룹선택기준과원본변경행수를구별한다.')
mc(4,22,'read-committed-two-sessions','Oracle 기본 READ COMMITTED에서 세션A가 v10을20으로UPDATE했지만아직COMMIT하지않았다. 세션B의일반SELECT는그20을더티리드하는가?','아니다. 다른 세션의 미확정20을 읽지 않는다',W('그렇다.최신메모리값은항상보인다','Oracle의읽기일관성을무시했다.','SELECT가A를자동COMMIT한다','다른세션을확정시키지않는다.','B는항상20을0으로바꿔읽는다','값치환규칙이아니다.'),'Oracle은일반조회에서다른트랜잭션의미확정변경을읽지않는다.',['A의변경은자기세션에는보이지만아직미확정이다.','B는읽기일관성에따라자신의조회시점에유효한확정데이터를본다.'],'자기변경가시성과타세션미확정변경가시성을구별한다.',extra=['초기10은확정됨. 일반SELECT이며SELECT FOR UPDATE가아니다. 다른변경과장애없음.'])
mc(4,23,'fk-default-delete-protect','부모P의id1을자식C가참조하고있다. FK는활성즉시검사이며ON DELETE옵션이없다. 자식을먼저처리하지않고부모1을삭제하려하면?','참조 무결성 때문에 부모 삭제가 거부된다',W('자식도기본으로자동삭제','CASCADE는명시옵션이다.','자식pid가자동0','그런기본값변경이없다.','FK가자동으로비활성화','DML이제약을자동해제하지않는다.'),'기본참조규칙에서참조받는부모를제거하면자식의유효한참조가깨진다.',['자식행이pid1을사용중인지확인한다.','연쇄삭제·SET NULL옵션이없으므로해당부모DELETE는실패한다.'],'부모삭제정책은외래키에실제정의된옵션을따른다.')
mc(4,24,'revoke-one-object-only','B는A.T1과A.T2의SELECT를각각직접받았다. A.T1의SELECT만회수했다. 다른경로는없다. 남는조회권한은?','A.T2의 SELECT',W('두표모두조회불가','회수대상은T1만이다.','T1만조회가능','회수대상을뒤집었다.','두표모두변경가능','SELECT회수는수정권한을생성하지않는다.'),'객체별부여권한의범위를독립적으로추적한다.',['T1과T2의별도권한경로를작성한다.','T1경로만제거하므로T2조회권한은남는다.'],'권한회수는명시한객체·동작·수신자범위를확인한다.')

mc(5,9,'sort-arithmetic-null','T(id,price,discount)는(1,100,NULL),(2,80,10),(3,60,0)이다. price-discount DESC NULLS LAST,id로 정렬해 id를 반환하면?','2,3,1',W('1,2,3','id1의 NULL 할인은 산술 결과를NULL로 만든다.','3,2,1','비NULL 순가격을 오름차순으로 읽었다.','2,1,3','NULLS LAST 때문에NULL은모든비NULL뒤다.'),'순가격은NULL,70,60이므로70,60,NULL순이다.',['NULL을 포함한100-NULL은NULL이다.','비NULL 순가격70과60을 내림차순으로 둔 뒤id1을 마지막에 둔다.'],'계산식의 NULL 전파와 결과 정렬 위치를 차례로 적용한다.')
mc(5,10,'distinct-after-project-join','A(k)에1,1이 있고 B(k,v)에(1,10),(1,20)이 있다. 키 등호 조인 후 SELECT DISTINCT A.k만 반환하면?','1 한 행',W('1 네 행','매칭은네쌍이지만마지막DISTINCT투영이중복을제거한다.','1 두 행','A원본중복만세면조인·DISTINCT단계를놓친다.','10,20 두 행','SELECT에B.v를포함하지않았다.'),'조인행수와최종투영의중복제거후행수는다르다.',['조인은2×2로네행을만든다.','A.k만선택하면모두1이고DISTINCT로한행이된다.'],'조인중복을설명할때최종SELECT·DISTINCT단계까지확인한다.')
mc(5,10,'nvl-null-sentinel-collision','NULL키를서로맞추려고양쪽키에NVL(k,-1)을적용해등호조인했다. 실제정상키-1도허용된다면문제는?','실제-1과NULL이 같은 치환값이 되어 의도하지 않은 매칭이 생길 수 있다',W('NVL은언제나NULL끼리만매칭한다','실제-1도같은값으로비교된다.','실제-1행이자동삭제된다','치환비교는행삭제명령이아니다.','NULL은여전히UNKNOWN이라효과가없다','NVL로비NULL치환값을비교한다.'),'대체값이실제도메인과충돌하면서로다른의미를같은키로만든다.',['NULL의치환값-1과실제-1을나란히놓는다.','둘의등호가TRUE가되어NULL과정상키가잘못매칭될수있다.'],'NULL대체조인은대체값의도메인충돌을확인한다.')
mc(5,11,'full-on-true-empty','A는두행이고B는빈표다. ON조건이상수TRUE인 FULL OUTER JOIN의행수는?','A의 두 행이 NULL 확장되어2행',W('0행','FULL은빈반대편과의미매칭A행을보존한다.','한행','A원본두행을집계하지않는다.','무한히많은행','상수조건이원본외행을생성하지않는다.'),'ON이TRUE여도B행이없어매칭쌍은없지만FULL보존단계가있다.',['A×B의매칭쌍은2×0=0개다.','A의두미매칭행을각각B열NULL로확장한다.'],'빈입력에서CROSS·INNER와OUTER의보존차이를확인한다.')
mc(5,11,'full-unmatched-where-side','A(k)에1, B(k)에2가 있다. FULL OUTER JOIN을등호로하고WHERE A.k IS NOT NULL을붙이면남는행은?','(A.k=1,B.k=NULL) 한 행',W('(NULL,2) 한행','오른쪽미매칭행은A.kNULL이라필터에서제거된다.','(1,NULL),(NULL,2) 두행','WHERE를적용하지않은중간결과다.','(1,2) 한행','불일치키를매칭하지않는다.'),'FULL중간결과의두미매칭행중왼쪽값이있는행만남긴다.',['중간결과는(1,NULL),(NULL,2)다.','A.k IS NOT NULL은첫행만TRUE다.'],'외부조인후WHERE는어느쪽미매칭보존을남길지다시결정할수있다.')
mc(5,12,'null-left-in-mixed','왼쪽비교값x가NULL이고 IN목록은1,2이다. x IN(1,2)와 x NOT IN(1,2)의3값논리판정은?','둘 다 UNKNOWN',W('IN은FALSE,NOT IN은TRUE','NULL동등비교는단순불일치FALSE가아니다.','둘다TRUE','NULL은임의값과같다고판정하지않는다.','IN은TRUE,NOT IN은FALSE','목록안에NULL도없고등호TRUE가없다.'),'각NULL비교가UNKNOWN이며그부정도UNKNOWN이다.',['NULL=1 OR NULL=2는UNKNOWN이다.','NOT UNKNOWN도UNKNOWN이므로WHERE는둘다통과시키지않는다.'],'NULL의3값논리에서부정은UNKNOWN을TRUE로바꾸지않는다.')
mc(5,12,'exists-aggregate-no-group','빈표 T에서 SELECT COUNT(*) FROM T를 서브쿼리로 넣은 EXISTS는?','TRUE',W('FALSE','집계값0과집계결과0행을혼동했다.','UNKNOWN','존재판정은행유무에대한TRUE/FALSE다.','COUNT가0이라문법오류','정상집계결과한행을반환한다.'),'GROUP BY없는COUNT는빈원본에도0값을가진한행을반환한다.',['T원본은비어도서브쿼리결과는COUNT0한행이다.','EXISTS는그값0이아니라한행존재를보고TRUE다.'],'EXISTS안에그룹없는집계를넣으면원본존재검사와의미가달라질수있다.')
mc(5,12,'relational-division-empty-required','모든 필수과목을 이수한 학생을 찾기 위해 “그 학생이 이수하지 않은 필수과목이 없다”라는 이중 NOT EXISTS를 사용한다. 필수과목표가 비어 있고0개요구도충족으로정했다면?','모든 학생이 통과한다',W('아무학생도통과하지않는다','반례필수과목이없으므로NOT EXISTS는TRUE다.','이수표가많은행만통과한다','필수과목이없다는조건에서수가기준이아니다.','모든학생이자동새과목에등록된다','SELECT조건이등록데이터를생성하지않는다.'),'전체충족조건은위반요구사항의부재로평가되며빈요구집합에는반례가없다.',['학생마다미이수필수과목을찾으려하지만필수과목자체가0개다.','반례서브쿼리가비어NOT EXISTS는모든학생에서TRUE다.'],'전체요구충족질의는요구집합이비었을때의업무규칙을명시한다.')
mc(5,13,'unionall-group-frequency','A(v)에1,1,2, B(v)에1,2,2가 있다. UNION ALL후 v별COUNT(*)로묶으면?','v1은3, v2도3',W('v1은1,v2도1','UNION중복제거뒤집계처럼읽었다.','v1은2,v2도2','각표내중복을일부누락했다.','v1은4,v2는2','입력값분포를잘못합쳤다.'),'ALL로모든원본발생을보존한뒤그룹빈도를센다.',['v1은A의2+B의1=3이다.','v2는A의1+B의2=3이다.'],'발생빈도를합칠때UNION의중복제거가정보를잃게하는지확인한다.')
mc(5,13,'intersect-not-join-product','A(v)에1두행, B(v)에1세행이있다. INTERSECT결과와등호INNER JOIN후v만선택한결과의행수차이는?','INTERSECT1행, JOIN6행',W('둘다1행','JOIN은별도DISTINCT없으면행쌍을유지한다.','둘다6행','INTERSECT는공통행을중복제거한다.','INTERSECT2행,JOIN3행','각입력행수를따로반환하는연산이아니다.'),'공통값집합과매칭행쌍은중복을다르게다룬다.',['INTERSECT는공통값1한행이다.','JOIN은두왼쪽행×세오른쪽행으로6쌍이다.'],'집합교집합과등호조인은중복개수에서일반적으로다르다.')
mc(5,14,'rollup-composite-unit','Oracle GROUP BY ROLLUP((a,b),c)에서 (a,b)를 한 묶음 단위로 취급했다. 생성하는 그룹 수준은?','(a,b,c), (a,b), ()',W('(a,b,c),(a,b),(a),()','묶은(a,b)를중간에a만남도록쪼개지않는다.','(a,b,c),(c),()','접두묶음은(a,b)다.','(a),(b),(c)만','ROLLUP의상세·전체수준을누락했다.'),'복합열묶음은ROLLUP의소계단위하나로취급된다.',['두단위(a,b)와c를나열했다고읽는다.','오른쪽c를뺀뒤(a,b)전체를빼므로세수준이다.'],'ROLLUP에서괄호로묶은열집합은소계단위를바꾼다.')
mc(5,14,'aggregate-null-all-levels','d1의금액NULL두행,d2의금액5한행이있다. ROLLUP(d)의전체수준 SUM(amount),COUNT(*),COUNT(amount)는?','(5,3,1)',W('(5,1,1)','COUNT(*)는금액NULL원본행도센다.','(NULL,3,1)','SUM은NULL을제외해비NULL5를합산한다.','(5,3,3)','COUNT(amount)는NULL을제외한다.'),'전체수준은모든원본세행을포함하되집계함수별NULL처리가다르다.',['SUM의비NULL금액은5하나다.','전체행수3,비NULL금액수1을별도로센다.'],'같은소계수준안에서도SUM과두COUNT가세는대상이다르다.')
mc(5,15,'lag-offset-partition','부서1의id순v값10,20과부서2의v값90한행이있다. PARTITION BY 부서의LAG(v,2,-1)을계산할때부서2행의값은?','-1',W('10','앞부서까지넘어두행앞을찾지않는다.','20','부서전체정렬직전행이분석파티션밖이다.','90','현재행을참조하는함수가아니다.'),'부서2파티션안에는현재한행뿐이어서두행앞이존재하지않는다.',['LAG오프셋검색의경계는현재파티션이다.','범위밖이므로명시기본값-1을사용한다.'],'LAG·LEAD의오프셋도PARTITION경계를넘지않는다.')
mc(5,15,'lead-ignore-null-values','고유id순v값은10,NULL,30이다. LEAD(v,1,-1) IGNORE NULLS를적용할때첫행의결과는?','30',W('NULL','IGNORE NULLS로다음NULL값을건너뛴다.','-1','이후비NULL30이있어기본값이아니다.','10','현재값을반환하지않는다.'),'IGNORE NULLS는다음대상값을찾을때NULL을건너뛴다.',['현재10뒤의첫값은NULL이라무시한다.','다음비NULL30을찾아반환한다.'],'행부재의default와값검색의IGNORE NULLS를구분한다.')
mc(5,16,'negative-values-window','id순v값은10,-20,15다. ROWS UNBOUNDED PRECEDING부터CURRENT ROW까지누적SUM의결과는?','10,-10,5',W('10,30,45','음수-20을양수로바꿨다.','10,10,15','누적합이감소하지않는다고가정했다.','10,-20,15','현재값만반환하고누적하지않았다.'),'누적SUM은값의부호를그대로합치므로감소할수있다.',['첫누적10,둘째10-20=-10이다.','셋째는-10+15=5다.'],'누적이라는이름이항상증가함을뜻하지는않는다.')
mc(5,16,'frame-whole-without-order','SUM(v) OVER(PARTITION BY d)에ORDER BY나프레임이없다. d1의값10,20에붙는SUM은?','두 행 모두30',W('첫행10,둘째30','ORDER BY가있는누적기본프레임으로읽었다.','첫행20,둘째10','합계함수는값교환이아니다.','두행모두10','첫행값만취하지않는다.'),'정렬순서없는파티션집계는파티션전체를집계한다.',['d1파티션은10과20두행이다.','전체합계30을원래각행옆에붙인다.'],'분석ORDER BY유무에따라전체집계와누적계산의의미를구분한다.')
mc(5,17,'bottom-n-null-policy','가장 낮은 실제 점수 두 명을 고르되 미채점NULL은 제외한다. 점수는NULL,30,10,20이다. 적절한 단계는?','WHERE로 NULL 제외 → 점수 ASC → 두 행 선택',W('점수ASC NULLS FIRST → 두행선택','미채점NULL이선택될수있다.','점수DESC → 두행선택','높은점수를고르는방향이다.','임의두행선택 → 점수ASC','전체최저두행을보장하지않는다.'),'최저실제값요구는NULL필터와정렬방향·제한단계를함께명시한다.',['NULL을제외하면30,10,20이남는다.','오름차순10,20,30에서10과20을선택한다.'],'미채점제외와NULL정렬위치지정은서로다른업무규칙이다.')
mc(5,17,'top-after-distinct','원본점수는100,100,90,80이다. 점수만DISTINCT로만든뒤DESC상위2행을선택했다. 이결과를사람수2명선택과동일하게볼수없는이유는?','선택 단위가 사람이 아니라 서로 다른 점수값이다',W('DISTINCT가고유학생id를새로만든다','그런식별자를생성하지않는다.','FETCH는중복원본을자동복원한다','투영에서잃은사람구분을복구하지않는다.','결과는항상100두행이다','DISTINCT후100은한행이다.'),'DISTINCT점수는100,90,80세값이며상위2는100,90이다.',['먼저원본사람행의중복점수구분을없앤다.','그후두행제한은두점수값을고르므로100점두사람중누구인지의문제가아니다.'],'Top N의행단위는그앞단계가만든결과단위다.')
mc(5,18,'leaf-before-where','1→2인계층을먼저만들고WHERE id=1만남기면서CONNECT_BY_ISLEAF도조회한다. 루트1은화면에자식이안보인다는이유로잎1로바뀌는가?','아니다. 계층 관계상 자식2가 있어 잎 표시는0이다',W('그렇다.WHERE가깊이와잎을항상다시계산한다','결과필터와계층관계생성을혼동했다.','루트행은항상잎1이다','루트와잎여부는독립개념이다.','WHERE가있으면의사열은전부NULL','그런규칙이없다.'),'출력에서자식을숨겼다고CONNECT BY관계의자식존재를바꾼것은아니다.',['연결조건으로1의자식2가있음을판정한다.','후속행필터가2의표시만제거하므로1의leaf0을유지한다.'],'계층의관계상태와최종화면의보이는행을구별한다.')
mc(5,18,'hierarchy-path-versus-id','id가1→20→3인경로에서LEVEL과id를같은값으로가정한코드의문제는?','id는 식별자이고 LEVEL은1,2,3의 상대 깊이라 다르다',W('LEVEL은항상1,20,3을그대로반환','식별자값을깊이로복사하지않는다.','id20은숫자가커서루트가된다','START WITH와관계조건이루트를정한다.','id가불연속이면계층질의불가능','키숫자의연속성은필수조건이아니다.'),'계층깊이는경로에서몇번연결했는지로정해진다.',['시작1은LEVEL1,그자식20은LEVEL2다.','다음3은LEVEL3이며id숫자크기와무관하다.'],'계층키의숫자모양에서깊이·순서를추측하지않는다.')
mc(5,19,'filter-before-pivot-group','shop1의월1금액10과월2금액20이있다. PIVOT입력인라인뷰에서mon=1만먼저남긴후월1,2SUM열을만들었다. 결과는?','월1=10, 월2=NULL',W('월1=10,월2=20','입력필터로월2행을제거했다.','월1=30,월2=NULL','월별구분을무시하고제거된값을합쳤다.','월1=10,월2=0','없는SUM입력은NULL이다.'),'PIVOT은자신에게전달된필터후입력만집계한다.',['인라인뷰를지나면월1금액10한행만남는다.','월2에해당하는집계입력이없어SUM은NULL이다.'],'PIVOT밖표시필터와PIVOT입력행필터의영향을구별한다.')
mc(5,19,'unpivot-detect-missing','q1=10,q2=NULL,q3=NULL에서 누락된 분기 이름을 찾고 싶다. UNPIVOT 뒤 amount IS NULL로 필터하려면 필요한 옵션은?','INCLUDE NULLS',W('기본옵션그대로','기본UNPIVOT은NULL행을먼저버려뒤에서찾지못한다.','NULLS FIRST','ORDER BY위치옵션이며UNPIVOT행보존이아니다.','WITH TIES','TopN동점옵션이다.'),'NULL분기를분석대상행으로보존해야후속IS NULL검사가가능하다.',['INCLUDE NULLS로q1,q2,q3세행을만든다.','그뒤amount IS NULL을적용하면q2,q3이남는다.'],'뒤에서필터할누락상태를변환단계에서먼저버리지않는다.')
mc(5,20,'regexp-backreference','ASCII패턴 ^([A-Z])\\1$를 c옵션으로 적용한다. AA,AB,BB 중 일치하는 것은?','AA와 BB',W('세문자열모두','역참조는앞에서잡은실제문자를다시요구한다.','AB만','서로다른두문자를요구하는패턴이아니다.','AA만','첫캡처는A뿐아니라B도될수있다.'),'괄호가첫대문자를캡처하고역참조가같은문자의반복을요구한다.',['AA는A를캡처해A와비교,BB는B를캡처해B와비교한다.','AB는캡처A와둘째B가달라실패한다.'],'역참조는문자종류가아니라실제로캡처한내용을비교한다.')
mc(5,21,'zero-update-and-rollback','초기확정T에id1만있다. WHERE id=99의UPDATE후COMMIT했다. 같은세션에서id1값을조회하면?','원래 값 그대로다',W('COMMIT이자동으로새id99를삽입한다','COMMIT은대상없는UPDATE를INSERT로바꾸지않는다.','id1이99로바뀐다','매칭대상행이없다.','값이NULL로변한다','영향받지않은행을NULL로만들지않는다.'),'UPDATE조건을통과한행이0개라값변경자체가없다.',['id99행의존재여부를확인한다.','영향행0의트랜잭션확정은기존id1행을그대로유지한다.'],'DML명령실행과실제영향행존재를구분한다.')
mc(5,21,'merge-on-column-update','MERGE의ON에서D.id=S.id로매칭하면서MATCHED UPDATE로D.id자체를바꾸려한다. Oracle19c의주요제약은?','ON 조건에서 참조한 대상 열을 UPDATE할 수 없다',W('기본키가아니면ON열을언제나수정가능','ON참조열에관한MERGE제약이다.','MATCHED절에서는어떤열도수정불가','일반대상열UPDATE는지원한다.','ON조건이자동새id로다시매칭된다','금지된대입을자동재처리하지않는다.'),'OracleMERGE는ON조건에서참조하는대상열의UPDATE를제한한다.',['ON의대상참조열D.id를확인한다.','같은열이UPDATE대상이므로다른설계를검토해야한다.'],'MERGE의ON매칭키를갱신열로쓰는제약을확인한다.')
mc(5,22,'valid-ddl-failure-precommit','미확정UPDATE뒤 문법적으로 적법한 CREATE TABLE을 실행했으나 이미 같은 객체가 있어 DDL은실패했다. Oracle의DDL전암묵COMMIT관점에서앞선UPDATE는?','DDL 전에 확정될 수 있으므로 뒤 ROLLBACK으로 복구된다고 가정하면 안 된다',W('DDL실패이면앞선DML은반드시미확정','문법적으로적법한DDL의실행전COMMIT효과를무시했다.','DDL실패가앞선DML을자동삭제','확정과취소는반대다.','모든DBMS에서반드시같다','DBMS별동작을구분해야한다.'),'DDL의성공후COMMIT만이아니라실행전COMMIT경계도존재한다.',['앞선UPDATE이후적법한DDL실행전확정경계를확인한다.','DDL자체실패가이미발생한확정경계를되돌리지않는다.'],'DDL실패와그앞DML의미확정상태를같다고단정하지않는다.')
mc(5,23,'alter-not-null-existing-data','T.v에NULL인 기존행이있다. 기존값을처리하지않고 v를NOT NULL로바꾸는ALTER TABLE을정상적즉시검사로시도한다. 판단은?','기존 NULL 데이터 때문에 제약 적용이 실패할 수 있다',W('기존NULL이자동0으로치환된다','제약추가는기본값치환작업이아니다.','기존NULL행이자동삭제된다','구조제약변경을데이터삭제로바꾸지않는다.','NOT NULL은이후INSERT만보고기존행은언제나무시','일반적인검증제약적용은기존데이터도검사한다.'),'제약을강화하려면기존데이터가새규칙을만족하는지확인해야한다.',['현재vNULL행이새NOT NULL에위반한다.','먼저업무상적절한값처리·보존정책을정한뒤제약을적용해야한다.'],'DDL변경전기존데이터와새무결성규칙의호환을확인한다.')
mc(5,24,'system-revoke-not-object-chain','A가 B에게 시스템 권한을 WITH ADMIN OPTION으로 주고 B가 C에게 같은 시스템 권한을 부여했다. A가 B의 시스템 권한을 회수했다. 객체권한의연쇄회수와동일하게C도자동회수된다고단정해도되는가?','안 된다. 시스템 권한 회수는 종속 객체 권한 회수와 다르다',W('된다.모든GRANT체인은항상같이회수된다','시스템권한과객체권한의회수규칙을혼동했다.','회수하면C가B의계정소유자가된다','권한회수는계정소유권이전이아니다.','시스템권한은어떤경우에도회수불가능','REVOKE로회수할수있다.'),'권한종류와옵션별공식회수규칙을따로적용해야한다.',['대상은객체SELECT가아니라시스템권한이다.','B의회수로C의시스템권한도자동소멸한다고일반화하지않고C경로를별도확인한다.'],'WITH ADMIN OPTION과WITH GRANT OPTION의종속회수를구별한다.')

# Note-only additions from independent source review; existing block IDs remain.
for target in pack['notes']:
    if target['objectiveId']=='S12':
        target['version']=2
        target['blocks'].append(dict(id='S12-any-all',kind='example',title='ANY와 ALL: 하나와 모두',text='비교값이 NUMBER 5이고 서브쿼리의 전체 결과가 3,7이라면 5>ANY는 3보다 크므로 TRUE, 5>ALL은 7보다 크지 않으므로 FALSE다. ANY는 비교 하나라도 TRUE면 TRUE이며 ALL은 모든 비교가 TRUE여야 한다. 비교 집합이 3,NULL이면 5>ANY는 TRUE, 5>ALL은 UNKNOWN이다. 비교 집합이 비면 ANY는 FALSE, ALL은 TRUE다. 빈 집합과 NULL 한 행을 구별한다.'))
    if target['objectiveId']=='S15':
        target['version']=2
        target['blocks'].append(dict(id='S15-offset-null-default',kind='example',title='LAG·LEAD의 위치와 NULL',text='T(id NUMBER,v NUMBER)의 전체 입력은 (1,10),(2,NULL),(3,30)이다. SELECT id,LAG(v,1,0) OVER(ORDER BY id) AS prev FROM T ORDER BY id; 결과는 (1,0),(2,10),(3,NULL)이다. 이전 행이 없는 첫 행만 default0을 쓴다. 실제 이전 행의 값이 NULL이면 기본 RESPECT NULLS에서 그 NULL을 반환한다. LEAD는 뒤쪽 행을 찾는다. id 값의 숫자 차이가 아니라 정렬된 행의 위치 오프셋이며 PARTITION 경계를 넘지 않는다. IGNORE NULLS는 대상 값 탐색에서 NULL을 건너뛴다.'))
        target['blocks'].append(dict(id='S15-ntile-buckets',kind='example',title='NTILE은 행 수를 나눈다',text='T(id NUMBER)에 1,2,3,4,5가 있다. SELECT id,NTILE(2) OVER(ORDER BY id) AS bucket FROM T ORDER BY id; 결과는 (1,1),(2,1),(3,1),(4,2),(5,2)다. 행 수5를 버킷2개로 나누면 몫2, 나머지1이다. 앞 번호 버킷부터 한 행씩 더 받아 첫 버킷3행·둘째2행이 된다. 점수 동점 보존 함수가 아니므로 동점자가 버킷 경계에서 갈릴 수 있다. 고유 정렬 키를 쓰면 배정 위치를 재현할 수 있다.'))
    if target['objectiveId'] in ['S11','S17','S21']:
        target['version']=2

save()
