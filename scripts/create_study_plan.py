"""Author the dated study plan; source lesson/question content is never modified."""
import csv
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/study-plan'
OUT.mkdir(parents=True, exist_ok=True)
course = json.loads((ROOT/'content/course-pack.json').read_text(encoding='utf-8'))
lessons = {x['id']: x for x in course['lessons']}
pdfmap = {x['lessonId']: x for x in json.loads((ROOT/'content/study-plan-pdf-map.json').read_text(encoding='utf-8'))}
pdf_titles = {'1-1':'1-1_데이터 모델링의 이해.pdf','1-2':'1-2_데이터 모델과 SQL.pdf','2-1':'2_1_SQL 기본.pdf','2-2':'2_2_SQL 활용.pdf','2-3':'2_3_관리구문과 트랜잭션.pdf'}

def ids(section, first, last):
    return [f'{section}-{i:02}' for i in range(first, last+1)]

groups = [
    ids('1-1',1,6), ids('1-1',7,9)+ids('1-2',1,2), ids('1-2',3,7),
    ids('2-1',1,5), ids('2-1',6,10), ids('2-1',11,14), ids('2-1',15,18),
    ids('2-1',19,21), ids('2-1',22,25), ids('2-2',1,4), ids('2-2',5,6),
    ids('2-2',7,9), ids('2-2',10,13), ids('2-2',14,16), ids('2-2',17,18), ids('2-3',1,4)
]
titles = ['DB·모델링·스키마·ERD·엔터티','속성·관계·식별자·릴레이션·키','무결성·SQL 분류·정규화·반정규화','CREATE·자료형·제약·ALTER·INSERT','SELECT·WHERE 기본·UPDATE·DELETE·MERGE','WHERE 확장·정렬·DISTINCT·단일행 함수','NULL·NULL 함수·CASE·DECODE','집계 함수·GROUP BY·HAVING','INNER·OUTER·CROSS·SELF·ANSI JOIN','서브쿼리 기본·단일행·다중행·다중컬럼','스칼라·인라인뷰·상관 서브쿼리·집합','ROLLUP·CUBE·GROUPING SETS·GROUPING','OVER·순위·집계·기타 윈도우 함수','TOP-N·계층형 질의','PIVOT·UNPIVOT·정규식 + 특강','뷰·트랜잭션·DCL·관계대수']
focus = [
    ['엔터티·속성·관계를 자기 말로 설명','외부/개념/내부 스키마와 독립성 구별'],
    ['키의 유일성·최소성과 복합키 판단','식별 관계와 필수 참여를 구별'],
    ['함수 종속을 기준으로 1~3NF 판단','반정규화의 읽기 이득과 변경 비용 설명'],
    ['DDL과 행 변경 구별; DEFAULT와 명시 NULL','교재에서 CHECK 제한·INSERT ALL·자료형 세부 조건 보완'],
    ['괄호·AND/OR로 남는 행을 직접 표시','MERGE는 일치 분기와 갱신 뒤 삭제 조건 확인'],
    ['LIKE %/_·DISTINCT 출력 조합·정렬 키 판단','INITCAP·POWER·날짜 ROUND·변환 형식은 교재로 보충'],
    ['TRUE/FALSE/UNKNOWN과 NULL 계산을 손으로 추적','행별 합계 뒤 SUM과 SUM끼리 합산을 구별'],
    ['그룹을 먼저 만들고 COUNT/SUM/AVG 계산','입력 0행·실제 NULL 그룹·HAVING의 결과 행 수'],
    ['조인 결과를 행 쌍으로 그리기','미일치 행·ON/WHERE·COUNT(*)와 COUNT(열) 구별'],
    ['단일행/다중행/다중컬럼 연산자 대응','NOT IN + NULL, EXISTS, 쌍 비교의 반례'],
    ['상관 조건을 바깥 행과 연결','UNION/ALL/MINUS의 중복과 ORDER BY 필요성'],
    ['그룹 집합을 열거하고 소계 행 수 세기','부분 ROLLUP은 교재로 보완; GROUPING 0/1 구별'],
    ['PARTITION·ORDER·프레임을 나눈 뒤 계산','동점 순위·ROWS/RANGE·LAG/LEAD·LAST_VALUE'],
    ['정렬 후 행 제한과 동점 포함 조건','SQL Server TOP·형제 정렬·LEVEL 행 생성 보완'],
    ['PIVOT 집계와 UNPIVOT NULL 행 수','POSIX·이스케이프·정규식 인수는 교재와 특강 연결'],
    ['COMMIT 경계·SAVEPOINT·권한 전파','뷰 표현식 별칭·OR REPLACE·ROLE 구문 보완']
]
concept_minutes = [29,24,32,28,39,37,25,26,26,22,30,26,25,34,27,40,39,44,36,35,37,35,29,31,31]
mock_minutes = [32,77,54,37,60,65,23,60,54,23,52,68,27,57,56]
lecture_number = {x['id']:i+1 for i,x in enumerate(course['lessons'])}

def theory_lecture(lid):
    l=lessons[lid]
    return {'number':lecture_number[lid],'title':f'{lid} {l["title"]}','minutes':l['lectureMinutes'],'kind':'이론'}

def pdf_refs(lids, goals):
    refs=[]
    for key in dict.fromkeys(pdfmap[x]['pdfKey'] for x in lids):
        maps=[pdfmap[x] for x in lids if pdfmap[x]['pdfKey']==key]
        refs.append({'sectionId':key,'title':pdf_titles[key],'fromPage':min(x['fromPage'] for x in maps),'toPage':max(x['toPage'] for x in maps),'focus':goals})
    return refs

def block(title, minutes, detail):
    return {'title':title,'minutes':minutes,'detail':detail}

notes = [
    '2026-10-05~11-13의 평일 중 10/8·10/9를 제외한 28일 계획. 11/14는 사용자가 목표로 삼은 시험일이며 공식 일정 확인 완료 표시가 아니다.',
    '5시간은 순공부 300분, 6시간은 같은 기본 진도에 약점 보완 60분을 추가한다. 휴식·식사 시간은 별도다. 추가 시간에 다음 강의를 미리 배정하지 않아 두 버전의 진도는 같다.',
    '104강은 이론 63강·개념완성 25강·모의고사 해설 15강·정규식 특강 1강이다. 1배속 시청 3521분(58시간 41분). 정지·재생·필기는 별도 풀이/오답 시간이나 6시간 추가 블록을 사용한다.',
    '교재 쪽수는 PDF 파일의 첫 쪽을 1로 센다. 경계 쪽이 겹치면 오늘 소제목부터 다음 소제목 직전까지 읽는다. 단일행 함수 13~14강과 NULL 15~16강은 각각 같은 PDF 단원을 나눠 듣는다.',
    '강의 3-1의 회차별 문제 주제 및 3-2 모의고사 원문은 제공된 5개 이론 PDF만으로 확인할 수 없다. 해당 첨부 문제를 확보했을 때만 해설보다 먼저 푼다. 없으면 지정한 교재 문제/앱 모의고사로 대체하고 서로 같은 문제라고 간주하지 않는다.',
    '앱은 복습 도구다. 오늘 범위를 설명 가리기로 회상하고 기존 연습문제로 적용한다. 앱 모의고사 예약 문항은 평일 복습에 끌어오지 않는다. 강의 시청·PDF 풀이 완료를 앱 강의 노트 읽음과 같다고 기록하지 않는다.',
    'PDF 정답·해설이 충돌하는 문항은 맞힘/틀림 통계에서 제외하고 확인 목록에 남긴다. 알려진 예: SQL 기본 121·123쪽 조인 해설, SQL 활용 45쪽 UNION 순서·46~48쪽 ROLLUP 표. 전체 정답 검증 완료라는 뜻은 아니다.',
    '밀리면 다음 공부일의 추가 60분 또는 11/13 정리 시간을 쓴다. 5시간 계획에서 시간이 모자라면 이미 이해한 해설의 재시청부터 줄이고 직접 풀이 시간을 남긴다. 휴일에 밀린 분량을 자동 배정하지 않는다.',
    '이해 점검: 답 번호 대신 근거를 말하고 숫자/NULL/조건이 바뀐 작은 반례를 풀어 본다. 마지막 주 새 모의고사 3회에서 75~80점 이상과 과목별 약점 감소를 준비 점검 목표로 삼는다. 합격 보장/공식 기준이 아닌 개인 계획 목표다.'
]
start=date(2026,10,5);end=date(2026,11,13)
study_dates=[start+timedelta(days=i) for i in range(40) if (start+timedelta(days=i)).weekday()<5 and start+timedelta(days=i) not in (date(2026,10,8),date(2026,10,9))]
days=[]
for index,dt in enumerate(study_dates):
    n=index+1
    d={'date':dt.isoformat(),'studyDay':n,'title':'','phase':'','restReason':'','lectures':[],'pdfs':[],'lessonIds':[],'blocks':[],'extension':[]}
    if n<=16:
        lids=groups[index]
        d.update(title=titles[index],phase='개념과 교재 1회독',lessonIds=lids,lectures=[theory_lecture(x) for x in lids],pdfs=pdf_refs(lids,focus[index]))
        if n==15: d['lectures'].append({'number':104,'title':'4-1 정규식 특강','minutes':57,'kind':'특강'})
        w=sum(x['minutes'] for x in d['lectures'])
        d['blocks']=[block('회상·준비',15,'전날 핵심 3개를 자료 없이 설명한다. 첫날은 DB/SQL의 아는 것과 모르는 것을 표시한다.'),block('강의',w,'배정된 강의를 1배속 기준으로 듣는다. 단원마다 멈추고 결과를 먼저 예상한다.'),block('PDF 직접 풀이',225-w,'지정 쪽의 개념·예제를 확인하고 관련 문제를 해설을 가린 채 먼저 푼다. 어려운 문제는 표시 후 오답 시간에 돌아온다.'),block('앱 복습',40,'오늘 범위의 강의/개념 노트를 가리고 회상한다. 연습 10~15문항을 풀되 문제 수보다 이유 설명을 우선한다.'),block('오답 정리',20,'오답·확신 없이 맞힌 문제의 이유 한 줄과 반례 한 개를 남긴다. PDF와 앱 설명 충돌은 확인 목록으로 분리한다.')]
        d['extension']=[block('어려운 강의 재확인',20,'정지·필기로 부족했던 부분이나 이해가 안 된 구간만 다시 듣는다.'),block('PDF 약점 재풀이',25,'오늘 틀린 유형 또는 앱에서 다루지 않는 세부 조건을 직접 풀어 본다.'),block('누적 앱 복습',15,'이전 공부일의 오답을 가리고 다시 설명한다. 새 진도를 늘리지 않는다.')]
    elif n<=22:
        group_index=n-17
        first,last=[(1,4),(5,8),(9,13),(14,17),(18,21),(22,25)][group_index]
        review_groups=[groups[0]+groups[1]+groups[2],groups[3]+groups[4],groups[5]+groups[6]+groups[7]+groups[8],groups[9]+groups[10]+groups[11],groups[12]+groups[13]+groups[14],groups[15]][group_index]
        goals=[['키·정규화·무결성의 지난 오답'],['DDL/DML·제약조건·MERGE의 지난 오답'],['함수·NULL·집계·JOIN의 지난 오답'],['서브쿼리·집합·그룹 함수의 지난 오답'],['윈도우·TOP-N·계층·정규식의 지난 오답'],['뷰·TCL·DCL·관계대수의 지난 오답']][group_index]
        d.update(title=f'개념완성 문제풀이 {first:02}~{last:02}회',phase='문제풀이와 누락 보완',lessonIds=review_groups,pdfs=pdf_refs(review_groups,goals))
        d['lectures']=[{'number':63+i,'title':f'3-1 개념완성 제{i:02}회','minutes':concept_minutes[i-1],'kind':'문제풀이'} for i in range(first,last+1)]
        w=sum(x['minutes'] for x in d['lectures'])
        d['blocks']=[block('해설 전 직접 풀이',75,'해당 회차 첨부 문제가 있으면 먼저 푼다. 없으면 아래 PDF 범위의 이전 오답·미풀이 문제로 대체한다. 회차별 주제는 확인되지 않았으며 아래 복습 주제와 같은 회차라는 뜻은 아니다.'),block('문제풀이 강의',w,'첨부 문제로 풀었으면 강의 해설과 비교한다. PDF로 대체했으면 그 PDF 해설로 별도 채점하고 강의는 별개 예제 학습으로 본다. 서로 다른 문제의 오답·점수를 합치지 않는다.'),block('PDF 약점 보완',20,'아래 쪽 전체를 다시 읽지 않는다. 이론 주간에 표시한 미풀이·오답 및 빠진 세부 조건을 회수한다.'),block('앱 누적 복습',25,'지정된 복습 범위에서 10~15문항 또는 이전 오답을 재풀이한다.'),block('오답 이유 정리',180-w,'잘못 읽은 조건·모르는 개념·계산 실수를 나누어 한 줄씩 기록한다.')]
        d['extension']=[block('미완료 직접 풀이',40,'75분 안에 못 푼 첨부 문제나 PDF 약점 문제를 이어서 푼다.'),block('앱 이전 오답',20,'이틀 이상 지난 오답을 해설 없이 다시 풀고 설명한다.')]
    elif n<=27:
        m=n-22
        lids=[ids('1-1',7,9)+ids('1-2',2,6),ids('2-1',13,21),ids('2-1',22,25)+ids('2-2',1,6),ids('2-2',7,16),ids('2-2',17,18)+ids('2-3',1,4)][m-1]
        d.update(title=f'모의고사 {m}회 + 해설',phase='실전 점검',lessonIds=lids,pdfs=pdf_refs(lids,['오늘 모의에서 틀린 항목이 우선. 아래는 누적 복습 후보이며 해당 모의의 실제 출제 주제 배정이 아니다.']))
        d['lectures']=[{'number':88+(m-1)*3+j+1,'title':f'3-2 {m}회 모의고사 {j+1:02} ({["01~10","11~30","31~50"][j]})','minutes':mock_minutes[(m-1)*3+j],'kind':'모의고사'} for j in range(3)]
        w=sum(x['minutes'] for x in d['lectures'])
        d['blocks']=[block('모의 먼저 풀기',90,f'강의 {m}회 원문이 있으면 해설 전에 푼다. 없으면 앱 모의 {m}회 중 미열람 세트로 대체한다. 이미 본 세트라면 연습으로 표시하고 최초 실전 점수로 사용하지 않는다. 앱 점수와 다른 문제의 강의 해설을 섞어 채점하지 않는다.'),block('모의 해설 강의',w,'같은 원문으로 풀었다면 오답 이유와 비교한다. 앱 세트로 대체했다면 앱 해설로 별도 채점하고, 강의는 별개 예제 학습으로 본다.'),block('PDF·오답 보완',195-w,'틀린 주제의 PDF/앱 설명으로 돌아간다. 아래는 추천 후보이며 실제 오답 단원을 우선한다. 시간 안에 분석하지 못한 문제는 목록에 남겨 추가 시간 또는 11/13의 120분에 처리한다.'),block('앱 짧은 회상',15,'오늘 헷갈린 규칙 3개를 설명한다. 모의 점수와 일반 복습 기록은 구분한다.')]
        d['extension']=[block('오답 재풀이',40,'오늘 모의의 확신 없던 문제까지 해설을 가리고 다시 푼다.'),block('반례 만들기',20,'NULL·중복·경계값 하나를 바꿔 결과를 다시 계산한다.')]
    else:
        lids=ids('1-1',7,9)+ids('1-2',2,6)+ids('2-1',15,23)+ids('2-2',3,3)+ids('2-2',7,16)+ids('2-3',1,4)
        d.update(title='최종 회상·밀린 분량·컨디션 정리',phase='마무리',lessonIds=lids,pdfs=pdf_refs(lids,['새 단원 전체를 읽지 않고 개인 오답/표시한 부분만 확인']))
        d['blocks']=[block('밀린 분량·반복 오답',120,'놓친 공부일 분량이 있으면 이 시간을 먼저 쓴다. 없으면 가장 자주 틀린 유형을 새 숫자로 다시 풀어 본다.'),block('PDF 최종 확인',75,'키·정규화·NULL·JOIN·윈도우·트랜잭션 중 약점만 확인. 정답 충돌 문항은 암기하지 않는다.'),block('앱 가리고 설명',60,'별표·현재 오답과 개념 가리기로 회상한다. 새 모의고사를 추가로 소진하지 않는다.'),block('준비물·한 장 정리',45,'자주 틀리는 조건을 한 장으로 정리하고 접수 내역의 장소·입실 시간·신분증을 확인한다.')]
        d['extension']=[block('남은 약점 정리',30,'남은 오답 중 두 유형만 보완한다.'),block('가벼운 회상',30,'외운 문장보다 풀이 순서를 말한다. 이미 마쳤다면 더 공부하기 위해 수면을 줄이지 않는다.')]
    days.append(d)

bydate={x['date']:x for x in days}
calendar=[]
for i in range(40):
    dt=start+timedelta(days=i)
    calendar.append(bydate.get(dt.isoformat(),{'date':dt.isoformat(),'studyDay':None,'title':'휴식','phase':'휴식','restReason':'이번 주 목·금 휴식' if dt.weekday()<5 else '주말 휴식','lectures':[],'pdfs':[],'lessonIds':[],'blocks':[],'extension':[]}))
plan={'schemaVersion':1,'title':'SQLD 40일 학습 계획','startDate':start.isoformat(),'endDate':end.isoformat(),'notes':notes,'days':calendar}
text=json.dumps(plan,ensure_ascii=False,indent=2)+'\n'
(ROOT/'content/study-plan.json').write_text(text,encoding='utf-8')
(ROOT/'app/src/main/assets/study-plan.json').write_text(text,encoding='utf-8')
(OUT/'study-plan.json').write_text(text,encoding='utf-8')
with (OUT/'전체계획표.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['날짜','공부일','단계','오늘 주제','강의','영상 분','PDF 범위','앱 복습 강의 ID','5시간 배분','6시간 추가'])
    for d in calendar:
        w.writerow([d['date'],d['studyDay'] or '',d['phase'],d['title'],' / '.join(x['title'] for x in d['lectures']),sum(x['minutes'] for x in d['lectures']),'; '.join(f'{x["sectionId"]} {x["fromPage"]}~{x["toPage"]}쪽' for x in d['pdfs']),', '.join(d['lessonIds']),'; '.join(f'{x["title"]} {x["minutes"]}분' for x in d['blocks']),'; '.join(f'{x["title"]} {x["minutes"]}분' for x in d['extension'])])
lecture_ids=[x['number'] for d in days for x in d['lectures']]
assert sorted(lecture_ids)==list(range(1,105)),Counter(lecture_ids)
assert all(sum(x['minutes'] for x in d['blocks'])==300 and sum(x['minutes'] for x in d['extension'])==60 for d in days)
assert all(x['minutes']>0 for d in days for x in d['blocks'])
assert sum(x['minutes'] for d in days for x in d['lectures'])==3521
assert len(days)==28 and len(calendar)==40
assert {x for g in groups for x in g}==set(lessons)
for key,count in [('1-1',27),('1-2',27),('2-1',137),('2-2',112),('2-3',21)]:
    covered={p for d in days[:16] for ref in d['pdfs'] if ref['sectionId']==key for p in range(ref['fromPage'],ref['toPage']+1)}
    assert covered==set(range(1,count+1)),(key,covered)
print(json.dumps({'studyDays':len(days),'restDays':12,'lectures':len(lecture_ids),'videoMinutes':3521,'fiveHourMinutes':28*300,'sixHourMinutes':28*360,'canonical':'content/study-plan.json'},ensure_ascii=False))
