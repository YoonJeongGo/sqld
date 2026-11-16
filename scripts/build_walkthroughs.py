"""Build separately versioned, source-bound SQL reading aids. Never edits original packs.

The executable subset below is deliberately bounded to authored SELECT fixtures.
SQLite is a comparison engine, NOT an Oracle certification or a physical plan.
"""
from __future__ import annotations
import collections
import copy
import decimal
import hashlib
import json
import math
import re
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content/sql-walkthroughs"
ASSETS = ROOT / "app/src/main/assets/sql-walkthroughs"
EVIDENCE = ROOT / "evidence/sql-walkthroughs-20261006"
VERSION = '2026.10.06.1'
URL = "https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/"
URLS = [URL+x for x in ("SELECT.html", "Nulls.html", "Aggregate-Functions.html", "Joins.html", "Using-Subqueries.html", "Analytic-Functions.html", "IN-Condition.html", "Comparison-Conditions.html")]
SOURCE_KEYS = "id version title stem sql tables choices correctChoiceIds dialect dialectVersion".split()
RUNS = []

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def norm(v):
    if v is None: return None
    if isinstance(v,bool): return str(v).upper()
    if isinstance(v, (int, float, decimal.Decimal)):
        d=decimal.Decimal(str(v)); return format(d.normalize(), 'f')
    return str(v)

def display(v):
    return "NULL" if v is None else str(norm(v))

def rows_norm(rows): return [[norm(x) for x in row] for row in rows]

def equal_rows(actual, expected, ordered=False):
    numeric_columns={i for i in range(len(actual[0]) if actual else 0) if any(r[i] is not None for r in actual) and all(r[i] is None or isinstance(r[i],(int,float,decimal.Decimal)) for r in actual)}
    def key(v,i):
        if v is None: return (0, '')
        if i in numeric_columns:
            try: return (1, decimal.Decimal(str(v)).quantize(decimal.Decimal('0.000000001')))
            except decimal.InvalidOperation: return (2, str(v))
        return (2,norm(v))
    a=[tuple(key(v,i) for i,v in enumerate(r)) for r in actual]
    b=[tuple(key(v,i) for i,v in enumerate(r)) for r in expected]
    return a==b if ordered else collections.Counter(a)==collections.Counter(b)

def spans(sql):
    """Characters at parenthesis depth 0, excluding quoted content."""
    depth=0; quote=None; i=0
    while i<len(sql):
        c=sql[i]
        if quote:
            if c==quote:
                if i+1<len(sql) and sql[i+1]==quote: i+=2; continue
                quote=None
        elif c in "'\"": quote=c
        elif c=='(': depth+=1
        elif c==')': depth-=1
        elif depth==0: yield i
        i+=1

def top_positions(sql, words):
    allowed=set(spans(sql)); found=[]
    pat=r'(?<![\w])('+ '|'.join(re.escape(w) for w in sorted(words,key=len,reverse=True))+r')(?![\w])'
    for m in re.finditer(pat,sql,re.I):
        if m.start() in allowed: found.append((m.start(),m.end(),m.group().upper()))
    return found

def parts(sql):
    p=top_positions(sql,['SELECT','FROM','WHERE','GROUP BY','HAVING','ORDER BY'])
    return {name:sql[end:(p[i+1][0] if i+1<len(p) else len(sql))].strip() for i,(start,end,name) in enumerate(p)}

def split_list(s):
    positions=set(spans(s)); cuts=[i for i,c in enumerate(s) if c==',' and i in positions]
    return [x.strip() for x in [s[a+1:b] for a,b in zip([-1]+cuts,cuts+[len(s)])]]

def strip_alias(s):
    ps=top_positions(s,['AS'])
    return s[:ps[-1][0]].strip() if ps else s

def oracle_sort_keys(s):
    return ', '.join(k if re.search(r'\bNULLS\s+(FIRST|LAST)\b',k,re.I) else k+(' NULLS FIRST' if re.search(r'\bDESC\s*$',k,re.I) else ' NULLS LAST') for k in split_list(s))

def translation(sql):
    # The only syntax rewrite: make Oracle's NULL sort defaults explicit.
    def over_fix(m):
        body=m.group(1); p=top_positions(body,['ORDER BY','ROWS','RANGE'])
        order=next((x for x in p if x[2]=='ORDER BY'),None)
        if order:
            end=next((x[0] for x in p if x[0]>order[0]),len(body))
            body=body[:order[1]]+' '+oracle_sort_keys(body[order[1]:end].strip())+' '+body[end:]
        return 'OVER('+body.strip()+')'
    sql=re.sub(r'OVER\s*\(([^()]*)\)',over_fix,sql,flags=re.I)
    p=top_positions(sql,['ORDER BY'])
    if p:
        a,b,_=p[-1]; sql=sql[:b]+' '+oracle_sort_keys(sql[b:].strip())
    return sql

def run(db, sql):
    c=db.execute(translation(sql)); return [x[0] for x in c.description],c.fetchall()

def db_for(q):
    db=sqlite3.connect(':memory:')
    db.create_function('NVL',2,lambda a,b:b if a is None else a)
    db.create_function('MOD',2,lambda a,b:None if a is None or b is None else (a if b==0 else a-math.trunc(a/b)*b))
    db.executescript(q['fixture']['schemaSql'])
    db.executescript(q['fixture']['setupSql'])
    if not db.execute("SELECT 1 FROM sqlite_master WHERE lower(name)='dual'").fetchone():
        db.execute('CREATE TABLE DUAL(dummy TEXT)'); db.execute("INSERT INTO DUAL VALUES('X')")
    return db

def table(title, columns, rows):
    return {'title':'학습용 중간 결과 · '+title,'columns':columns,'rows':rows_norm(rows)}

def sql_literal(v):
    if v is None: return 'NULL'
    if isinstance(v,(int,float)): return display(v)
    return "'"+str(v).replace("'","''")+"'"

def substitute(expr, columns, row):
    mapping={c.lower():sql_literal(v) for c,v in zip(columns,row)}
    bare=collections.Counter(c.split('.')[-1].lower() for c in columns)
    for c,v in zip(columns,row):
        if bare[c.split('.')[-1].lower()]==1: mapping[c.split('.')[-1].lower()]=sql_literal(v)
    tokens=re.compile(r"'(?:''|[^'])*'|[\w]+(?:\.[\w]+)?",re.UNICODE)
    return tokens.sub(lambda m: mapping.get(m.group().lower(),m.group()) if not m.group().startswith("'") else m.group(),expr)

def truth(v): return 'UNKNOWN → 제외' if v is None else ('TRUE → 통과' if v else 'FALSE → 제외')

def find_functions(expr, names):
    found=[]
    for m in re.finditer(r'\b('+ '|'.join(names)+r')\s*\(',expr,re.I):
        start=m.start(); opening=m.end()-1; depth=1; i=opening+1; quote=False
        while i<len(expr) and depth:
            c=expr[i]
            if c=="'": quote=not quote
            elif not quote:
                if c=='(':depth+=1
                if c==')':depth-=1
            i+=1
        if depth==0: found.append((expr[start:i],m.group(1).upper(),expr[opening+1:i-1]))
    return list(dict.fromkeys(found))

def terms_for(q):
    sql=q['sql']; out=[]
    definitions={
      'SELECT':('키워드','결과에 보여 줄 열과 계산식을 고른다.','이 문제의 최종 출력 열을 정한다.'),
      'FROM':('키워드','값을 읽을 표 또는 조회 결과를 지정한다.','원본 표에서 설명을 시작하는 위치다.'),
      'WHERE':('키워드','각 행에서 조건이 TRUE인 행만 남긴다.','FALSE와 UNKNOWN인 행은 제외한다.'),
      'ON':('키워드','두 표의 어떤 행을 짝지을지 지정하는 조인 조건이다.','이 문제에서는 행 쌍의 일치 여부를 검사한다.'),
      'AS':('키워드','결과 열에 읽기 쉬운 임시 이름을 붙인다.','원본 컬럼명을 바꾸는 명령이 아니다.'),
      'DISTINCT':('키워드','지정한 값 또는 출력 열 조합의 중복을 제거한다.','SELECT 뒤라면 전체 출력 열 조합, 집계 함수 안이라면 그 인자에 적용한다.'),
      'GROUP BY':('키워드','그룹 기준값이 같은 입력 행을 묶는다.','각 묶음에서 집계를 계산하며 출력 정렬을 보장하지 않는다.'),
      'HAVING':('키워드','그룹 조건이 TRUE인 그룹만 남긴다.','집계 전 개별 행을 거르는 WHERE와 구별한다.'),
      'ORDER BY':('키워드','지정한 키에 따라 순서를 정한다.','OVER 내부 정렬은 계산용이며 최종 결과 순서는 바깥 ORDER BY가 정한다.'),
      'NULL':('특수 값','알려지지 않았거나 없는 값을 나타내는 표지다.','0이나 공백과 다르다. 일반 비교는 UNKNOWN이며 IS NULL로 검사한다.'),
      'COUNT':('함수','행 또는 NULL이 아닌 계산값의 개수를 센다.','COUNT(*)는 모든 행, COUNT(식)는 그 식이 NULL이 아닌 행을 센다.'),
      'SUM':('함수','NULL을 제외한 값을 더한다.','집계 대상값이 없으면 NULL이다.'),
      'AVG':('함수','NULL을 제외한 값들의 합을 그 값들의 개수로 나눈다.','0은 계산에 포함하지만 NULL은 분자와 분모에서 제외한다.'),
      'MIN':('함수','NULL을 제외한 최소값을 구한다.','NULL만 있거나 입력이 없으면 NULL이다.'),
      'MAX':('함수','NULL을 제외한 최대값을 구한다.','NULL만 있거나 입력이 없으면 NULL이다.'),
      'NVL':('함수','첫 값이 NULL이면 두 번째 값을 사용한다.','이 자료의 숫자 예제에서는 NULL을 명시한 숫자로 대체한다.'),
      'COALESCE':('함수','왼쪽부터 처음 만나는 NULL이 아닌 값을 반환한다.','0과 공백은 NULL이 아니므로 대체되지 않는다.'),
      'NULLIF':('함수','두 값이 같으면 NULL, 다르면 첫 값을 반환한다.','이 문제의 식에서 제외할 값을 NULL로 바꾸는 역할을 한다.'),
      'CASE':('표현식','조건이나 값을 차례로 비교해 해당 결과를 고른다.','처음 일치하는 WHEN 결과를 쓰며 ELSE 생략 후 불일치면 NULL이다.'),
      'JOIN':('키워드','두 입력의 조건에 맞는 행 쌍을 결합한다.','한 행이 여러 행과 맞으면 여러 결과 행이 생긴다.'),
      'LEFT JOIN':('키워드','왼쪽 행을 모두 보존하는 외부 조인이다.','오른쪽 일치 행이 없으면 오른쪽 열을 NULL로 채운다.'),
      'IN':('연산자','왼쪽 값과 목록의 값이 같은지 비교한다.','일치가 없고 NULL 비교가 남으면 UNKNOWN이 될 수 있다.'),
      'NOT IN':('연산자','목록의 모든 값과 다르다는 조건이다.','목록에 NULL이 있으면 일치 항목은 FALSE, 나머지도 UNKNOWN이 되어 TRUE를 얻지 못할 수 있다.'),
      'ANY':('연산자','비교 중 하나라도 TRUE이면 통과한다.','> ANY는 각 비교를 OR로 연결해 판단하며 NULL과 빈 집합도 따진다.'),
      'EXISTS':('연산자','안쪽 조회가 한 행이라도 반환하는지 검사한다.','안쪽 SELECT 값이 NULL이어도 행이 존재하면 TRUE다.'),
      'OVER':('키워드','현재 행과 함께 계산할 분석 함수의 범위를 지정한다.','GROUP BY처럼 원래 행 수를 줄이지 않는다.'),
      'PARTITION BY':('키워드','분석 함수를 계산할 행 묶음을 나눈다.','각 파티션에서 순위나 합계 계산을 새로 시작한다.'),
      'RANK':('함수','동점을 같은 순위로 두고 다음 순위에 간격을 둔다.','앞선 행 수를 반영한다.'),
      'DENSE_RANK':('함수','동점을 같은 순위로 두고 다음 순위를 연속해 매긴다.','앞선 서로 다른 정렬값의 수를 반영한다.'),
      'ROW_NUMBER':('함수','정렬된 행마다 서로 다른 번호를 매긴다.','동점 비교를 끝내는 키가 없으면 동점 행의 번호는 확정되지 않는다.'),
      'AND':('논리 연산자','연결한 조건이 모두 TRUE일 때 TRUE다.','FALSE가 하나면 FALSE이고, FALSE 없이 UNKNOWN이 남으면 UNKNOWN이다.'),
      'OR':('논리 연산자','연결한 조건 중 하나라도 TRUE면 TRUE다.','TRUE 없이 UNKNOWN이 있으면 UNKNOWN, 모두 FALSE면 FALSE다.'),
      'NOT':('논리 연산자','TRUE와 FALSE를 뒤집는다.','UNKNOWN을 뒤집어도 UNKNOWN이다.'),
      'IS NULL':('조건 연산자','값이 NULL인지 검사한다.','NULL이면 TRUE, NULL이 아니면 FALSE다. =NULL 비교와 다르다.'),
      'BETWEEN':('조건 연산자','아래 경계 이상, 위 경계 이하인지 검사한다.','경계를 모두 포함하며 NULL 비교는 UNKNOWN이 될 수 있다.'),
      'LIKE':('조건 연산자','문자값이 패턴에 맞는지 검사한다.','%는 0개 이상 문자, _는 문자 한 개다. ESCAPE로 패턴 기호를 실제 문자로 지정할 수 있다.'),
      'ALL':('조건 연산자','안쪽 목록의 모든 값과 비교한 조건이 TRUE일 때 TRUE다.','대상 목록이 비어 있으면 TRUE다.'),
      'UNION':('집합 연산자','두 조회 결과를 합치고 중복 행을 제거한다.','NULL이 포함된 동일 열 조합도 중복으로 처리한다.'),
      'UNION ALL':('집합 연산자','두 조회 결과의 모든 행을 그대로 이어 붙인다.','같은 값과 NULL 행의 중복도 보존한다.'),
      'INTERSECT':('집합 연산자','두 조회 결과에 공통으로 있는 행을 구한다.','열 전체 조합으로 비교하고 중복은 제거한다.'),
      'MINUS':('집합 연산자','왼쪽에 있고 오른쪽에 없는 행을 구한다.','열 전체 조합으로 비교하고 중복은 제거한다.'),
      'LAG':('함수','정렬된 파티션에서 앞쪽 행의 값을 가져온다.','그 행 자체가 없을 때 기본값을 쓴다. 실제 행의 NULL은 기본값으로 바꾸지 않는다.'),
      'LEAD':('함수','정렬된 파티션에서 뒤쪽 행의 값을 가져온다.','식별자 숫자를 더하는 것이 아니라 정렬된 위치를 이동한다.'),
      'NTILE':('함수','정렬된 행을 지정한 수의 묶음으로 나눈다.','나머지 행은 앞 묶음부터 배정하므로 크기 차이는 최대 한 행이다.'),
      'PERCENT_RANK':('함수','순위의 상대 위치를 (RANK-1)/(행 수-1)로 계산한다.','동점은 같은 값이며 파티션 한 행이면 0이다.'),
      'CUME_DIST':('함수','현재 동점 묶음까지의 행 수를 전체 행 수로 나눈다.','동점의 마지막 위치까지 포함한다.'),
      'FIRST_VALUE':('함수','현재 프레임의 첫 값을 가져온다.','기본 RESPECT NULLS는 첫 값이 NULL이면 NULL을 유지한다.'),
      'LAST_VALUE':('함수','현재 프레임의 마지막 값을 가져온다.','파티션 전체가 아니라 명시된 현재 프레임 끝을 본다.'),
      'ROWS':('키워드','정렬된 행의 위치로 프레임을 정한다.','1 PRECEDING은 현재 행 바로 앞 한 행이다.'),
      'RANGE':('키워드','정렬값의 범위로 프레임을 정한다.','동점 행을 함께 포함하며 숫자 1 PRECEDING은 값의 거리 1이다.'),
      'SUBSTR':('함수','문자열에서 지정 위치와 길이만큼 문자를 꺼낸다.','현재 자료에서 지정한 시작 위치와 개수를 확인한다.'),
      'LENGTH':('함수','문자열의 문자 수를 구한다.','중첩 함수가 있으면 안쪽에서 나온 문자열의 길이를 센다.'),
      'REPLACE':('함수','문자열에서 찾은 부분을 지정 문자열로 바꾼다.','현재 입력에서 실제로 일치하는 모든 부분을 바꾼다.'),
      'TRIM':('함수','양 끝의 지정 문자를 제거한다.','문자 생략 시 양 끝 공백을 제거하며 가운데 공백은 보존한다.'),
      'UPPER':('함수','영문을 대문자로 바꾼다.','현재 문자열의 영문 대소문자만 바뀐다.'),
      'LOWER':('함수','영문을 소문자로 바꾼다.','현재 문자열의 영문 대소문자만 바뀐다.'),
      'MOD':('함수','나눗셈의 나머지를 구한다.','현재 숫자 입력에서 몫에 해당하는 부분을 빼고 남은 값을 확인한다.'),
      'ABS':('함수','숫자의 절댓값을 구한다.','음수이면 부호가 바뀌고 양수와 0은 그대로다.'),
      'SIGN':('함수','숫자가 음수/0/양수인지 -1/0/1로 반환한다.','소수 부분을 버리는 함수가 아니라 부호를 나타낸다.'),
      'CEIL':('함수','현재 숫자 이상인 가장 작은 정수를 구한다.','음수에서도 수직선의 큰 쪽 정수를 고른다.'),
      'FLOOR':('함수','현재 숫자 이하인 가장 큰 정수를 구한다.','음수에서도 수직선의 작은 쪽 정수를 고른다.'),
    }
    for token,(kind,meaning,role) in definitions.items():
        if re.search(r'(?<![\w])'+re.escape(token)+r'(?![\w])',sql,re.I):
            out.append(dict(token=token,kind=kind,meaning=meaning,role=role))
    for t in q.get('tables',[]):
        out.append(dict(token=t['title'],kind='테이블명',meaning='관련 정보를 행과 열로 저장한 표의 이름이다.',role='원본의 '+', '.join(t['columns'])+' 열을 제공한다.'))
        for col in t['columns']:
            out.append(dict(token=col,kind='컬럼명',meaning='표에서 한 종류의 정보를 담는 열의 이름이다.',role=t['title']+' 표의 '+col+' 값을 읽는다.'))
    for alias in re.findall(r'\bAS\s+([\w]+)',sql,re.I):
        out.append(dict(token=alias,kind='별칭',meaning='출력 열에 붙인 임시 이름이다.',role='바로 앞 계산식의 결과를 '+alias+'로 보여 준다.'))
    for name,alias in re.findall(r'\b(?:FROM|JOIN)\s+(\w+)\s+(\w+)',sql,re.I):
        if alias.upper() not in {'WHERE','JOIN','LEFT','RIGHT','FULL','INNER','OUTER','CROSS','ON','ORDER','GROUP','HAVING','UNION','INTERSECT','MINUS','USING','NATURAL'}:
            out.append(dict(token=alias,kind='테이블 별칭',meaning='같은 표를 짧게 부르는 이름이다.',role=f'{alias}.컬럼은 {name} 표의 컬럼을 가리킨다. 같은 표를 두 번 읽을 때 바깥 행과 안쪽 행을 구분한다.'))
    for op in ['>=','<=','<>','=','>','<','+','*']:
        if op in sql:
            meaning={'=':'두 값을 같은지 비교한다.','<>':'두 값이 다른지 비교한다.','>':'왼쪽 값이 더 큰지 비교한다.','<':'왼쪽 값이 더 작은지 비교한다.','>=':'왼쪽 값이 크거나 같은지 비교한다.','<=':'왼쪽 값이 작거나 같은지 비교한다.','+':'숫자를 더한다.','*':'a*b는 곱셈, SELECT * 또는 T.*는 전체 열, COUNT(*)는 모든 입력 행을 뜻한다.'}[op]
            out.append(dict(token=op,kind='연산자',meaning=meaning,role='현재 파란 구문의 실제 값 대입을 함께 확인한다.'))
    return out

class Walk:
    def __init__(self,q): self.q=q; self.steps=[]; self.categories=set()
    def add(self,title,text,focus,t=None,focus_rows=None,focus_cells=None,occurrence=0):
        assert focus in self.q['sql'], (self.q['id'],focus)
        linked=[focus] if focus in text else []
        if not linked and '→' in text:
            formula=text.split('→')[0].split('\n')[-1].strip()
            if 0<len(formula)<=120:linked.append(formula)
        for source_table in self.q.get('tables',[]):
            for column in source_table['columns']:
                qualified=source_table['title']+'.'+column
                candidate=qualified if qualified in text else column
                if re.search(r'(?<![\w])'+re.escape(candidate)+r'(?![A-Za-z0-9_])',text) and candidate not in linked:linked.append(candidate)
        s=dict(id=f'step-{len(self.steps)+1:02d}',title=title,text=text,codeFocus=[dict(needle=focus,occurrence=occurrence)],highlights=linked[:6],focusRows=focus_rows or [],focusCells=focus_cells or [])
        if t: s['table']=t
        self.steps.append(s)
    def finish(self,engine_mode='SQLite에서 호환 SELECT 실행; Oracle NULL 정렬 기본값 명시; 숫자 NVL/MOD는 등록 함수', extra=None):
        return dict(id=self.q['id'],source={k:copy.deepcopy(self.q[k]) for k in SOURCE_KEYS},intro='입력 표의 값으로 SQL의 뜻을 따라 읽는 학습용 논리 과정입니다. 실제 DB의 물리 실행 순서나 실행계획을 측정한 자료가 아닙니다. 이전·다음으로 한 단계씩 확인하세요.',steps=self.steps,terms=terms_for(self.q),verification={'method':'독립 값 계산 및 원본 fixture 대조','engine':'SQLite','engineVersion':sqlite3.sqlite_version,'oracleEngineExecuted':False,'queryMode':engine_mode,'expectedRowsMatch':True,'notes':extra or ['Oracle 19c 원문 엔진 실행은 미실시. 원본 정답·보기·입력표는 변경하지 않았다.','아래 중간표는 설명용이며 실제 엔진 내부에 같은 임시표가 생긴다는 뜻이 아니다.']},sourceUrls=URLS)

def generic(q):
    sql=q['sql'].strip().rstrip(';'); p=parts(sql); w=Walk(q)
    if not sql.upper().startswith('SELECT'): raise ValueError('DDL/DML/트랜잭션 문항: 상태 변경·커밋 경계를 Oracle 엔진에서 확인하지 못하여 기존 해설 유지')
    if ';' in sql: raise ValueError('여러 문장/상태 변경: 별도의 Oracle 실행 검증 필요')
    special=re.findall(r'\b(TO_CHAR|TO_DATE|DATE|ADD_MONTHS|MONTHS_BETWEEN|TRUNC|ROUND|DECODE|LPAD|RPAD|INSTR|REGEXP_\w+|CAST|ROLLUP|CUBE|GROUPING|CONNECT|START|PIVOT|UNPIVOT|ROWNUM|FETCH|OFFSET|MINUS|ALL|ANY|RATIO_TO_REPORT|IGNORE|RESPECT)\b',sql,re.I)
    if special:
        raise ValueError('/'.join(dict.fromkeys(special))+'의 DBMS별 구문·값 의미를 새 단계자료로 검증하지 못하여 기존 해설 유지')
    if "''" in sql or '||' in sql or '/' in sql: raise ValueError('빈 문자열·문자 결합·나눗셈의 DBMS 차이를 별도 검증하지 않아 기존 해설 유지')
    if re.search(r'SUBSTR\s*\([^,]+,\s*(?:0|-)',sql,re.I): raise ValueError('SUBSTR의 시작 위치/문자 길이 DBMS 차이를 별도 확인해야 함')
    if re.search(r'SUBSTR\s*\([^,]+,[^,]+,\s*0\s*\)',sql,re.I): raise ValueError('SUBSTR 길이 0의 Oracle NULL 반환과 SQLite 빈 문자열 차이')
    if 'OVER' in sql.upper(): raise ValueError('분석 함수: 전용 윈도 범위 설명이 필요')
    if len(re.findall(r'\bSELECT\b',sql,re.I))>1: raise ValueError('서브쿼리/집합: 전용 안쪽 값 전달 설명이 필요')
    db=db_for(q)
    cols, final=run(db,sql)
    assert equal_rows(final,q['fixture']['expectedRows'],q['fixture']['ordered']), f'원본 fixture 불일치: {final}'
    # Read all columns with qualified labels so duplicate join column names remain distinct.
    src=p['FROM']; refs=[]
    for m in re.finditer(r'(?:^|\bJOIN\s+)([\w]+)(?:\s+(?!ON\b|LEFT\b|RIGHT\b|FULL\b|INNER\b|OUTER\b|CROSS\b|NATURAL\b|JOIN\b|USING\b)([\w]+))?',src,re.I):
        name,alias=m.groups(); alias=alias or name
        t=next((t for t in q['tables'] if t['title'].lower()==name.lower()),None)
        if t: refs.extend((alias+'.'+c,c) for c in t['columns'])
    if refs: raw_select=','.join(x[0] for x in refs); rawcols=[x[0] for x in refs]
    else: raw_select='*'; rawcols=[]
    actualcols,raw=run(db,'SELECT '+raw_select+' FROM '+src)
    if not rawcols: rawcols=actualcols
    if 'JOIN' in src.upper():
        w.categories.add('join')
        if ' ON ' in src.upper():
            j=re.match(r'(.+?)\s+(?:(LEFT|RIGHT|FULL|INNER|CROSS)(?:\s+OUTER)?\s+)?JOIN\s+(.+?)\s+ON\s+(.+)',src,re.I)
            if not j: raise ValueError('복합 JOIN 구문은 별도 설명 필요')
            left,jtype,right,on=j.groups()
            paircols,pairs=run(db,'SELECT '+raw_select+',('+on+') AS truth_value FROM '+left+' CROSS JOIN '+right)
            rows=[]
            for r in pairs: rows.append(list(r[:-1])+[truth(r[-1])])
            details='\n'.join(substitute(on,rawcols,r[:-1])+' → '+truth(r[-1]) for r in pairs)
            w.add('ON · 어느 행끼리 연결되는가',f'{on}에 양쪽 행의 값을 대입합니다. 각 TRUE 행 쌍마다 조인 결과 한 행이 생깁니다. 같은 키의 행이 여러 개면 그 조합을 모두 남깁니다.\n'+details,on,table('조인 후보와 조건 판단',rawcols+['ON 판단'],rows),focus_rows=[i for i,r in enumerate(pairs) if r[-1]==1])
        elif 'NATURAL JOIN' in src.upper():
            left,right=q['tables']; common=[c for c in left['columns'] if c in right['columns']]
            details=[]; inspected=[]
            for a in left['rows']:
                for b in right['rows']:
                    pairs=[(a[left['columns'].index(c)],b[right['columns'].index(c)]) for c in common]
                    tests=[None if x is None or y is None else x==y for x,y in pairs]
                    value=False if False in tests else (None if None in tests else True)
                    details.append(' AND '.join(f'{c}: {display(x)}={display(y)}' for c,(x,y) in zip(common,pairs))+' → '+truth(value))
                    inspected.append(a+b+[truth(value)])
            w.add('NATURAL JOIN · 공통 열을 모두 비교','두 표에서 이름이 같은 '+', '.join(common)+'를 모두 비교합니다. k 하나만 같은 것으로는 부족합니다.\n'+'\n'.join(details),'NATURAL JOIN',table('공통 열 조합 검사',[left['title']+'.'+c for c in left['columns']]+[right['title']+'.'+c for c in right['columns']]+['판정'],inspected),focus_rows=[i for i,r in enumerate(inspected) if r[-1]=='TRUE → 통과'])
        elif 'USING' in src.upper():
            w.add('USING · 공통 키 하나로 표시','USING(k)는 양쪽 k가 같은 행을 연결하고 결과의 k를 한 열로 보여 줍니다. FULL OUTER JOIN에서 한쪽만 존재하는 행도 보존하므로 그쪽 키가 결과 k에 남습니다.','USING(k)',table('USING의 결합 입력',rawcols,raw))
        text=f'{src} 결과는 {len(raw)}행입니다. '+ ('일치하지 않은 보존 쪽 행은 반대쪽 열을 NULL로 채웁니다. 이 NULL은 원본에 저장된 행이 아니라 외부 조인이 만든 값입니다.' if re.search(r'\b(LEFT|RIGHT|FULL)\b',src,re.I) else '조건을 통과한 모든 행 쌍을 유지합니다. 중복을 임의로 하나로 줄이지 않습니다.')
        w.add('FROM · 조인 후 입력',text,'FROM '+src,table('조인 후 행',rawcols,raw))
    else:
        text=f'{src}에서 '+', '.join(rawcols)+f' 값을 읽습니다. 입력 {len(raw)}행을 출발점으로 삼습니다. '+('DUAL은 계산식 한 행을 확인할 때 쓰는 표이며 dummy 값은 계산식의 대상이 아닙니다.' if src.upper()=='DUAL' else '여기서 보이는 순서는 설명을 위한 나열이며 원본 테이블에 고정된 행 순서가 있다는 뜻이 아닙니다.')
        w.add('FROM · 어떤 값에서 시작하는가',text,'FROM '+src,table('시작 입력',rawcols,raw))
    where=p.get('WHERE'); base=' FROM '+src+(' WHERE ('+where+')' if where else '')
    if where:
        w.categories.add('filter')
        cs,tests=run(db,'SELECT '+raw_select+',('+where+') AS condition_result FROM '+src)
        for i,r in enumerate(tests):
            text=substitute(where,rawcols,r[:-1])+' → '+truth(r[-1])+'. '
            text+=('값을 알 수 없는 비교가 남아 UNKNOWN입니다. WHERE는 TRUE만 남기므로 이 행은 제외됩니다.' if r[-1] is None else ('조건이 TRUE여서 이 행은 남습니다.' if r[-1] else '조건이 FALSE여서 이 행은 제외됩니다.'))
            w.add(f'WHERE · 입력 {i+1}번째 행',text,where,table('현재 행의 조건 판단',rawcols+['판단'],[list(r[:-1])+[truth(r[-1])]]),focus_rows=[0])
        _,filtered=run(db,'SELECT '+raw_select+base)
        w.add('WHERE · 남은 행 확인',f'{len(raw)}행 중 TRUE인 {len(filtered)}행만 남습니다. 이후 계산은 이 행들로 합니다.',where,table('조건 통과 후 입력',rawcols,filtered))
    else: filtered=raw
    selected=p['SELECT']; distinct=selected.upper().startswith('DISTINCT ')
    expressions=split_list(selected[9:].strip() if distinct else selected)
    group=p.get('GROUP BY'); having=p.get('HAVING')
    aggregates=find_functions(selected+(' '+having if having else ''),['COUNT','SUM','AVG','MIN','MAX'])
    groups=[([],filtered,'',[])]
    if group:
        w.categories.add('group')
        gexpr=split_list(group); gcols, keys=run(db,'SELECT '+group+base+' GROUP BY '+group)
        groups=[]
        for idx,key in enumerate(keys):
            conditions=' AND '.join(e+' IS '+sql_literal(v) if v is None else e+'='+sql_literal(v) for e,v in zip(gexpr,key))
            extra=(' AND ' if where else ' WHERE ')+conditions
            _, members=run(db,'SELECT '+raw_select+base+extra)
            label=', '.join(e+'='+display(v) for e,v in zip(gexpr,key))
            w.add('GROUP BY · '+label,f'{label}인 {len(members)}행을 같은 그룹으로 묶습니다. 이 그룹 안의 '+', '.join(rawcols)+' 값으로 계산합니다. NULL 그룹 키도 같은 NULL 그룹으로 묶입니다.','GROUP BY '+group,table('그룹 입력 · '+label,rawcols,members),focus_rows=list(range(len(members))))
            groups.append((key,members,extra,gexpr))
    if aggregates:
        w.categories.add('aggregate')
        for key,members,extra,gexpr in groups:
            label=', '.join(e+'='+display(v) for e,v in zip(gexpr,key)) or '전체 입력'
            for agg, fn, arg in aggregates:
                distinct_arg=arg.upper().startswith('DISTINCT '); argclean=arg[9:].strip() if distinct_arg else arg
                if argclean=='*': values=[1 for r in members]; inputrows=[list(r)+['행 1개','포함'] for r in members]
                else:
                    _, values_rows=run(db,'SELECT '+raw_select+','+argclean+base+extra)
                    values=[r[-1] for r in values_rows]
                    inputrows=[list(r[:-1])+[r[-1], 'NULL → 제외' if r[-1] is None else '포함'] for r in values_rows]
                vals=[v for v in values if v is not None]
                if distinct_arg: vals=list(dict.fromkeys(vals))
                _, aggrows=run(db,'SELECT '+agg+base+extra); result=aggrows[0][0]
                if fn=='COUNT': why=f'계산 대상 {len(vals)}개 → {display(result)}'
                elif fn=='AVG': why=f'합계 {display(sum(vals))} ÷ 비NULL 값 {len(vals)}개 = {display(result)}' if vals else '비NULL 값이 없어 평균은 NULL'
                elif fn=='SUM': why=' + '.join(display(v) for v in vals)+f' = {display(result)}' if vals else '비NULL 값이 없어 합계는 NULL'
                else: why=f'대상값 [{", ".join(display(v) for v in vals)}] 중 '+('최소' if fn=='MIN' else '최대')+f' = {display(result)}' if vals else '비NULL 값이 없어 결과는 NULL'
                text=f'{label}에서 {agg}를 계산합니다. '+('별표는 값 하나가 아니라 행 전체를 가리킵니다. NULL이 있는 행도 셉니다. ' if argclean=='*' else f'먼저 각 행의 {argclean} 값을 구하고 NULL을 제외합니다. ')+('동일한 계산값은 한 번만 사용합니다. ' if distinct_arg else '')+why+'.'
                w.add('집계 · '+agg,text,agg,table('집계 대상 · '+label,rawcols+[argclean+' 계산값','집계 포함 여부'],inputrows),focus_cells=[dict(row=i,column=len(rawcols)) for i in range(len(inputrows))])
        if having:
            w.categories.add('having')
            hcols,hrows=run(db,'SELECT '+(group+',' if group else '')+','.join(a[0] for a in aggregates)+',('+having+') AS judgment'+base+(' GROUP BY '+group if group else ''))
            shown=[list(r[:-1])+[truth(r[-1])] for r in hrows]
            details='\n'.join(', '.join(c+'='+display(v) for c,v in zip(hcols[:-1],r[:-1]))+' → '+truth(r[-1]) for r in hrows)
            w.add('HAVING · 그룹을 남길지 판단',f'{having}는 개별 입력 행이 아니라 그룹별 집계 결과에 적용합니다.\n'+details,having,table('그룹별 조건',hcols[:-1]+['HAVING 판단'],shown),focus_rows=[i for i,r in enumerate(hrows) if r[-1]==1])
        for key,members,extra,gexpr in groups:
            if having:
                _,surviving=run(db,'SELECT '+','.join(a[0] for a in aggregates)+base+extra+(' GROUP BY '+group if group else '')+' HAVING '+having)
                if not surviving:continue
            for original in expressions:
                expr=strip_alias(original)
                contained=[a[0] for a in aggregates if a[0] in expr]
                if not contained or expr in contained:continue
                actual=expr
                for agg in sorted(contained,key=len,reverse=True):
                    _,values=run(db,'SELECT '+agg+base+extra)
                    actual=actual.replace(agg,sql_literal(values[0][0]))
                actual=substitute(actual,gexpr,key)
                _,value=run(db,'SELECT '+actual)
                label=', '.join(e+'='+display(v) for e,v in zip(gexpr,key)) or '전체 입력'
                w.add('SELECT · 집계 후 바깥 계산',f'{label}: 집계값을 바깥 식에 넣으면 {expr} → {actual} = {display(value[0][0])}입니다. 집계 대상 행의 값을 먼저 바꾸는 것과, 집계한 결과값을 나중에 바꾸는 것은 다릅니다.',expr,table('집계 후 계산',['원래 출력식','실제 값 대입','계산 결과'],[[expr,actual,value[0][0]]]),focus_cells=[dict(row=0,column=1),dict(row=0,column=2)])
    # Projection with input and expression values side by side for non-aggregate queries.
    before_order='SELECT '+selected+base+(' GROUP BY '+group if group else '')+(' HAVING '+having if having else '')
    if not aggregates and not group:
        exp=[strip_alias(x) for x in expressions]
        if not any('*'==e or e.endswith('.*') for e in exp):
            _, calculated=run(db,'SELECT '+raw_select+','+','.join(exp)+base)
            for i,r in enumerate(calculated):
                text='\n'.join(substitute(e,rawcols,r[:len(rawcols)])+' = '+display(v) for e,v in zip(exp,r[len(rawcols):]))
                w.add(f'SELECT · 남은 {i+1}번째 행 계산',text+'\n원본 값을 고쳐 쓰는 것이 아니라 출력할 값으로 계산합니다.',selected,table('입력값과 출력식',rawcols+exp,[r]),focus_cells=[dict(row=0,column=c) for c in range(len(rawcols),len(r))])
    precols, pre=run(db,before_order)
    if distinct:
        w.categories.add('distinct')
        _, allrows=run(db,before_order.replace('SELECT DISTINCT ','SELECT ',1))
        w.add('DISTINCT · 같은 출력 조합을 합치기',f'출력 열 전체 조합이 같은 행만 하나로 합칩니다. {len(allrows)}행에서 서로 다른 조합 {len(pre)}행이 남습니다. NULL도 중복 조합 판단의 대상으로 남습니다.',selected,table('중복 제거 뒤',precols,pre))
    else:
        w.add('SELECT · 결과 열 확인',', '.join(precols)+f' 순서로 {len(pre)}행을 출력합니다. '+('집계값을 이용하는 바깥 계산식도 이 결과 열에서 확인합니다.' if aggregates else 'SELECT만으로 중복 행을 없애지는 않습니다.'),selected,table('출력 열',precols,pre))
    if p.get('ORDER BY'):
        w.categories.add('sort')
        w.add('ORDER BY · 마지막 표시 순서',p['ORDER BY']+'의 왼쪽 키부터 비교하고 같을 때 다음 키를 봅니다. ASC는 오름차순, DESC는 내림차순입니다. Oracle의 NULL 기본 위치는 ASC 마지막, DESC 처음이며 명시한 NULLS 절이 우선합니다.','ORDER BY '+p['ORDER BY'],table('정렬한 결과',cols,final))
    w.add('최종 결과와 원래 답 연결',f'최종 {len(final)}행입니다. '+('바깥 ORDER BY로 정한 순서를 따릅니다.' if q['fixture']['ordered'] else 'ORDER BY가 없으므로 여기 나열한 행 순서는 보장하지 않습니다. 행의 값과 중복 개수를 확인하세요.')+' 원래 보기별 해설에서 같은 결과인지 확인하세요.',selected,table('최종 결과',cols,final))
    RUNS.append(dict(id=q['id'],engine='SQLite',version=sqlite3.sqlite_version,originalSql=sql,executedSql=translation(sql),expectedRows=q['fixture']['expectedRows'],actualRows=rows_norm(final),ordered=q['fixture']['ordered'],match=True,categories=sorted(w.categories)))
    db.close()
    return w.finish(),sorted(w.categories)

def source_questions():
    return sum([json.loads((ROOT/('content/part-'+p+'.json')).read_text(encoding='utf-8'))['questions'] for p in ['a','b']],[])

def record_run(q, executed, final, categories, mode='SQL-compatible'):
    assert equal_rows(final,q['fixture']['expectedRows'],q['fixture']['ordered']), (q['id'],final,q['fixture']['expectedRows'])
    RUNS.append(dict(id=q['id'],engine='SQLite',version=sqlite3.sqlite_version,originalSql=q['sql'],executedSql=executed,expectedRows=q['fixture']['expectedRows'],actualRows=rows_norm(final),ordered=q['fixture']['ordered'],match=True,categories=categories,mode=mode))

def final_step(w,cols,rows):
    w.add('최종 결과와 원래 답 연결',f'최종 {len(rows)}행입니다. '+('바깥 ORDER BY의 순서를 따릅니다.' if w.q['fixture']['ordered'] else 'ORDER BY가 없으므로 표시한 행의 나열 순서는 보장하지 않습니다.')+' 기존 보기별 해설도 함께 확인하세요.','SELECT',table('최종 결과',cols,rows))

def window_walk(q):
    sql=q['sql']; p=parts(sql)
    if any(p.get(k) for k in ('WHERE','GROUP BY','HAVING')): raise ValueError('분석 함수 앞의 필터·집계가 있는 조합은 중간 입력 별도 작성 필요')
    if re.search(r'\b(IGNORE|RESPECT|RATIO_TO_REPORT)\b',sql,re.I): raise ValueError('분석 함수의 NULL 무시/비율 전용 의미를 독립 실행으로 확인하지 못하여 기존 해설 유지')
    if len(re.findall(r'\bSELECT\b',sql,re.I))!=1: raise ValueError('분석 함수의 인라인 뷰는 별도 단계 작성 필요')
    functions=list(re.finditer(r'(\w+)\(([^()]*)\)\s+OVER\(([^()]*)\)',sql,re.I))
    if not functions: raise ValueError('현재 분석 함수 패턴에서 단계 범위를 확인할 수 없음')
    db=db_for(q); cols,final=run(db,sql); w=Walk(q); t=q['tables'][0]
    rawcols,raw=run(db,'SELECT * FROM '+p['FROM']); id_index=rawcols.index('id')
    w.add('FROM · 원래 행을 유지',', '.join(rawcols)+f' 열을 가진 {len(raw)}행입니다. 분석 함수는 GROUP BY처럼 행을 합쳐 줄이지 않고 각 행 옆에 계산값을 붙입니다.','FROM '+p['FROM'],table('분석 함수 입력',rawcols,raw))
    for m in functions:
        full,fn,arg,over=m.group(),m.group(1).upper(),m.group(2),m.group(3)
        positions=top_positions(over,['PARTITION BY','ORDER BY','ROWS','RANGE'])
        wp={name:over[end:(positions[i+1][0] if i+1<len(positions) else len(over))].strip() for i,(_,end,name) in enumerate(positions)}
        partkeys=split_list(wp['PARTITION BY']) if wp.get('PARTITION BY') else []
        order=wp.get('ORDER BY'); orderexpr=[re.sub(r'\s+(ASC|DESC|NULLS).*','',x,flags=re.I).strip() for x in split_list(order)] if order else []
        for row in raw:
            current_id=row[id_index]
            condition=' AND '.join(key+' IS '+sql_literal(row[rawcols.index(key)]) for key in partkeys)
            base=' FROM '+p['FROM']+(' WHERE '+condition if condition else '')
            _,ordered=run(db,'SELECT *'+base+(' ORDER BY '+order if order else ''))
            pos=next(i for i,r in enumerate(ordered) if r[id_index]==current_id)
            n=len(ordered); argv=split_list(arg) if arg else []
            keys=[tuple(r[rawcols.index(k)] for k in orderexpr) for r in ordered] if order else [()]*n
            if (fn in ('ROW_NUMBER','LAG','LEAD','NTILE') or wp.get('ROWS')) and len(set(keys))!=len(keys): raise ValueError('행 위치 분석 함수의 정렬 동점을 구별할 키가 없어 개별 행 값을 확정하지 않음')
            if wp.get('RANGE') and (not order or 'DESC' in order.upper() or any(v is None for k in keys for v in k)): raise ValueError('RANGE의 DESC/NULL 프레임은 별도 검증 필요')
            frame=list(ordered); why=''; result=None
            if fn in ('RANK','DENSE_RANK','ROW_NUMBER','PERCENT_RANK','CUME_DIST'):
                rank=keys.index(keys[pos])+1
                dense=len(set(keys[:pos+1])); peer_end=max(i for i,k in enumerate(keys) if k==keys[pos])+1
                if fn=='RANK': result=rank; why=f'동점 묶음 앞에 {rank-1}행 → RANK={rank}. 동점 다음 순위에는 앞선 행 수만큼 간격이 생깁니다.'
                elif fn=='DENSE_RANK': result=dense; why=f'현재 값까지 서로 다른 정렬값 묶음 {dense}개 → DENSE_RANK={dense}.'
                elif fn=='ROW_NUMBER': result=pos+1; why=f'정렬 키 {order}가 동점까지 구분하므로 현재 행은 {pos+1}번째입니다.'
                elif fn=='PERCENT_RANK': result=0 if n==1 else (rank-1)/(n-1); why=f'(RANK {rank} - 1) / (파티션 {n}행 - 1) = {display(result)}.'
                else: result=peer_end/n; why=f'현재 동점 묶음까지 {peer_end}행 / 파티션 {n}행 = {display(result)}.'
            elif fn=='NTILE':
                k=int(argv[0]); size,extra=divmod(n,k); allocation=[size+(i<extra) for i in range(k)]; end=0
                for b,size in enumerate(allocation,1):
                    end+=size
                    if pos<end: result=b; break
                why=f'{n}행을 {k}묶음에 나누며 앞 묶음부터 큰 크기를 배정합니다. 묶음 크기 {allocation}, 현재 행은 {result}번 묶음입니다.'
            elif fn in ('LAG','LEAD'):
                offset=int(argv[1]) if len(argv)>1 else 1; target=pos+(-offset if fn=='LAG' else offset)
                if 0<=target<n:
                    frame=[ordered[target]]; result=ordered[target][rawcols.index(argv[0])]
                    why=f'현재 id={current_id}의 '+('앞' if fn=='LAG' else '뒤')+f' {offset}번째 행은 id={ordered[target][id_index]}. 그 행의 {argv[0]}={display(result)}를 가져옵니다. 실제 행의 NULL은 기본값으로 대체하지 않습니다.'
                else:
                    frame=[]; result=int(argv[2]) if len(argv)>2 else None
                    why=f'현재 id={current_id}의 '+('앞' if fn=='LAG' else '뒤')+f' {offset}번째 행이 없어 기본값 {display(result)}를 사용합니다.'
            else:
                if wp.get('ROWS'):
                    spec=wp['ROWS'].upper()
                    if spec=='BETWEEN 1 PRECEDING AND CURRENT ROW': frame=ordered[max(0,pos-1):pos+1]
                    elif spec=='BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING': frame=ordered[pos+1:]
                    elif spec=='BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING': frame=ordered
                    else: raise ValueError('작성하지 않은 ROWS 프레임: '+spec)
                    why='ROWS는 정렬된 행의 위치로 범위를 정합니다. '
                elif wp.get('RANGE'):
                    if wp['RANGE'].upper()!='BETWEEN 1 PRECEDING AND CURRENT ROW' or len(orderexpr)!=1: raise ValueError('작성하지 않은 RANGE 범위')
                    k=rawcols.index(orderexpr[0]); value=row[k]
                    frame=[r for r in ordered if value-1<=r[k]<=value]
                    why=f'RANGE는 행 한 개가 아니라 값의 거리입니다. 현재 {orderexpr[0]}={value}, {value-1}~{value} 범위를 포함합니다. '
                elif order:
                    last_peer=max(i for i,k in enumerate(keys) if k==keys[pos]); frame=ordered[:last_peer+1]
                    why='프레임 생략 시 RANGE UNBOUNDED PRECEDING~CURRENT ROW이므로 현재 정렬값과 동점인 행까지 포함합니다. '
                else: why='OVER에 ORDER BY가 없어 파티션 전체가 계산 대상입니다. '
                values=[r[rawcols.index(argv[0])] for r in frame] if argv and argv[0]!='*' else [1]*len(frame)
                nonnull=[v for v in values if v is not None]
                if fn=='SUM': result=sum(nonnull) if nonnull else None; why+=' + '.join(display(v) for v in nonnull)+f' = {display(result)}.' if nonnull else '계산할 비NULL 값이 없어 NULL입니다.'
                elif fn=='COUNT': result=len(nonnull); why+=f'대상 행/비NULL 값 {result}개를 셉니다.'
                elif fn in ('FIRST_VALUE','LAST_VALUE'): result=values[0 if fn=='FIRST_VALUE' else -1] if values else None; why+=f'현재 프레임의 '+('첫' if fn=='FIRST_VALUE' else '마지막')+f' 값은 {display(result)}입니다.'
                else: raise ValueError('미작성 분석 함수: '+fn)
            # Independent frame arithmetic is compared with SQLite for this exact source row.
            _,one=run(db,'SELECT id,'+full+' AS answer FROM '+p['FROM'])
            expected=next(r[1] for r in one if r[0]==current_id)
            assert equal_rows([[result]],[[expected]],True),(q['id'],fn,current_id,result,expected)
            label=' · '.join(key+'='+display(row[rawcols.index(key)]) for key in partkeys) or '전체 파티션'
            marked=[list(r)+['현재 보는 행' if r[id_index]==current_id else '계산 대상 행'] for r in frame]
            w.add(f'{fn} · id={current_id}',label+'. '+why+' OVER 안의 정렬은 계산 기준이며 최종 화면 순서와 구별합니다.',full,table(f'현재 id={current_id}의 계산 범위',rawcols+['역할'],marked),focus_rows=[i for i,r in enumerate(frame) if r[id_index]==current_id])
    final_step(w,cols,final); record_run(q,translation(sql),final,['window','sort'],'SQLite + independent Python window frame calculation')
    db.close(); return w.finish(extra=['각 행의 프레임·순위·참조값을 Python으로 별도 계산하고 SQLite의 해당 값과 대조했다.','Oracle 19c 원문 실행 미실시. OVER 정렬은 최종 행 순서가 아니다.']),['window','sort']

def subquery_walk(q):
    sql=q['sql']; w=Walk(q); db=db_for(q); qid=q['id']; executed=sql; category=['subquery']
    if qid=='S12-A01-above-own-dept-average':
        category.append('correlated'); t=q['tables'][0]; _,outer=run(db,'SELECT * FROM E')
        inner='SELECT AVG(x.sal) FROM E x WHERE x.d=e.d'
        for row in outer:
            id,d,sal=row; _,matches=run(db,'SELECT * FROM E WHERE d='+str(d)); vals=[r[2] for r in matches if r[2] is not None]; avg=sum(vals)/len(vals) if vals else None
            w.add(f'안쪽 조회 · 현재 e.id={id}',f'바깥 행 e.id={id}, e.d={d}를 안쪽 x.d=e.d에 대입합니다. 같은 부서 d={d}의 급여 '+', '.join(display(r[2]) for r in matches)+f' 중 NULL을 빼면 합계 {sum(vals)}, 개수 {len(vals)} → 평균 {display(avg)}입니다. 이는 행별 의미 설명이며 실제 엔진이 매 행마다 같은 방식으로 재실행한다는 주장은 아닙니다.',inner,table('현재 부서의 평균 입력',t['columns'],matches),focus_cells=[dict(row=i,column=2) for i in range(len(matches))])
            value=None if sal is None or avg is None else int(sal>avg)
            w.add(f'바깥 비교 · e.id={id}',f'e.sal={display(sal)} > 안쪽 평균 {display(avg)} → {truth(value)}. 현재 부서 평균과 비교하며 전체 부서 평균을 쓰지 않습니다.','e.sal>(SELECT AVG(x.sal) FROM E x WHERE x.d=e.d)',table('현재 행 비교',['id','급여','같은 부서 평균','판정'],[[id,sal,avg,truth(value)]]),focus_rows=[0])
    elif qid in ('S12-A02-exists-no-multiply','S12-A03-null-safe-not-exists'):
        negative='NOT EXISTS' in sql; outername='A' if negative else 'C'; innername='B' if negative else 'O'; col='k' if negative else 'id'; innercol='k' if negative else 'cid'
        _,outer=run(db,'SELECT * FROM '+outername); _,inside=run(db,'SELECT * FROM '+innername)
        for row in outer:
            value=row[0]; matches=[r for r in inside if value is not None and r[0] is not None and r[0]==value]; result=not bool(matches) if negative else bool(matches)
            needle=('NOT ' if negative else '')+re.search(r'EXISTS\(.+?\)',sql,re.I).group()
            text=f'{outername}.{col}={display(value)}와 {innername}.{innercol}을 비교합니다. TRUE인 안쪽 행은 {len(matches)}개입니다. '+('일치하는 행이 없을 때 NOT EXISTS는 TRUE입니다. NULL=NULL은 UNKNOWN이므로 일치 행으로 세지 않습니다.' if negative else 'EXISTS는 행의 존재만 검사하므로 안쪽 SELECT NULL이어도 TRUE입니다. 일치 행이 여러 개라도 바깥 행은 한 번 남습니다.')+f' 현재 판정: {truth(int(result))}.'
            w.add('존재 검사 · '+display(value),text,needle,table('현재 바깥 행과 일치하는 안쪽 행',q['tables'][1]['columns'],matches))
    elif qid=='S12-A05-scalar-aggregate-empty':
        _,rows=run(db,'SELECT v,(v>100) FROM T'); w.add('안쪽 WHERE · 100보다 큰 값', '\n'.join(f'{r[0]}>100 → {truth(r[1])}' for r in rows),'v>100',table('안쪽 행 검사',['v','판정'],[[r[0],truth(r[1])] for r in rows]))
        w.add('안쪽 AVG · 빈 집계 대상','TRUE인 행이 0개입니다. GROUP BY 없는 AVG는 결과 행 하나를 만들되 그 값은 NULL입니다. 스칼라 서브쿼리는 이 NULL 한 값을 바깥 SELECT에 전달합니다.','SELECT AVG(v) FROM T WHERE v>100',table('안쪽 집계값',['AVG(v)'],[[None]]))
    elif qid in ('S12-A04-not-in-empty','S12-A06-any-null-mixed','S12-A07-all-empty'):
        t=q['tables'][1]; _,inside=run(db,'SELECT * FROM B'); _,outer=run(db,'SELECT * FROM A'); inner=re.search(r'SELECT \w+ FROM B',sql).group()
        w.add('안쪽 목록 · 어떤 값이 나오는가',f'B의 {t["columns"][0]}에서 나온 목록은 ['+', '.join(display(r[0]) for r in inside)+f']입니다. {len(inside)}행이며 빈 목록은 NULL 한 개가 있는 목록과 다릅니다.',inner,table('안쪽 목록',t['columns'],inside))
        if 'ANY' in sql:
            condition=' OR '.join('x>'+sql_literal(r[0]) for r in inside) or '0'; executed=re.sub(r'x>ANY\(SELECT v FROM B\)', '('+condition+')',sql)
            _,checked=run(db,'SELECT x,('+condition+') FROM A')
            for x,value in checked:
                comparisons=', '.join(f'{x}>{display(r[0])}='+('UNKNOWN' if r[0] is None else str(x>r[0]).upper()) for r in inside)
                w.add('ANY · x='+str(x),comparisons+'. 하나라도 TRUE이면 OR 전체는 TRUE입니다. TRUE가 없고 UNKNOWN이 있으면 UNKNOWN입니다. → '+truth(value),'x>ANY(SELECT v FROM B)',table('현재 ANY 판단',['x','판정'],[[x,truth(value)]]),focus_rows=[0])
        elif 'ALL' in sql:
            assert not inside; executed=sql.replace('x>ALL(SELECT v FROM B)','1=1')
            w.add('ALL · 빈 목록과 비교','비교해야 할 대상이 0개이므로 위반하는 비교도 없습니다. 빈 집합에 대한 ALL은 TRUE여서 x=1과 x=2 모두 남습니다.','x>ALL(SELECT v FROM B)',table('빈 ALL의 판단',['x','판정'],[[r[0],'TRUE → 통과'] for r in outer]))
        else:
            assert not inside; w.add('NOT IN · 빈 목록과 비교','빈 목록에는 왼쪽 값과 같을 항목이 없습니다. 따라서 1도 NULL도 빈 목록에 대한 NOT IN은 TRUE입니다. 목록에 NULL 한 행이 있는 경우와 다릅니다.','k NOT IN(SELECT k FROM B)',table('빈 NOT IN의 판단',['k','판정'],[[r[0],'TRUE → 통과'] for r in outer]))
    elif qid in ('S12-A08-tuple-in','S12-SUP-A01-paired-membership'):
        source=q['tables'][0]; target=q['tables'][1]; needle=re.search(r'\([\w,]+\) IN\s*\(SELECT .+?\)',sql).group(); p=parts(sql); _,checks=run(db,'SELECT *,('+p['WHERE']+') FROM '+p['FROM'])
        w.add('안쪽 목록 · 열 조합 함께 읽기','안쪽 조회는 각 행의 두 열을 한 쌍으로 반환합니다. 첫 번째 열 목록과 두 번째 열 목록을 따로 섞어서 검사하지 않습니다.',re.search(r'SELECT [\w,]+ FROM (?:B|Allowed)',sql).group(),table('허용된 열 쌍',target['columns'],target['rows']))
        for r in checks:
            vals=r[:-1]; w.add('바깥 행 · 열 쌍 비교',', '.join(c+'='+display(v) for c,v in zip(source['columns'],vals))+'에서 지정된 두 열의 조합이 같은 안쪽 행을 찾습니다. → '+truth(r[-1]),needle,table('현재 조합 판단',source['columns']+['판정'],[list(vals)+[truth(r[-1])]]),focus_rows=[0])
    else: raise ValueError('별도 작성하지 않은 서브쿼리')
    cols,final=run(db,executed); final_step(w,cols,final); record_run(q,translation(executed),final,category,'ANY/ALL은 해당 fixture에 대한 OR/빈집합 참으로 명시 변환' if executed!=sql else 'SQL-compatible')
    db.close(); return w.finish(engine_mode='SQLite 비교 실행; ANY/ALL은 현재 실제 목록에 대한 OR 또는 빈집합 규칙으로 명시 변환. Oracle 원문 실행 아님'),category

def set_walk(q):
    sql=q['sql']; db=db_for(q); w=Walk(q); data={t['title']:[tuple(r) for r in t['rows']] for t in q['tables']}; qid=q['id']; keys=q['tables'][0]['columns']
    for t in q['tables']:
        focus='SELECT '+','.join(t['columns'])+' FROM '+t['title']
        w.add('부분 조회 · '+t['title'],t['title']+'의 '+', '.join(t['columns'])+f'를 읽으면 {len(t["rows"])}행입니다. 이 단계에서는 원본 중복과 NULL 행을 그대로 유지합니다.',focus,table('부분 조회 '+t['title'],t['columns'],t['rows']))
    if qid=='S13-A01-union-null-combined':
        combined=list(dict.fromkeys(data['A']+data['B'])); phrase='UNION은 두 입력을 모은 뒤 전체 열 조합의 중복을 제거합니다. 값 1과 2의 반복, NULL 행의 반복도 한 번씩 남습니다.'; focus='UNION'
    elif qid=='S13-A02-all-count':
        combined=data['A']+data['B']; phrase='UNION ALL은 중복을 지우지 않아 A의 4행 + B의 3행 = 7행입니다. 이 중 v가 NULL인 2행도 존재합니다.';focus='UNION ALL'
    elif qid=='S13-A03-intersection-two-columns':
        combined=[r for r in dict.fromkeys(data['X']) if r in data['Y']];phrase='INTERSECT는 전체 열 조합이 양쪽에 모두 있는 행만 한 번씩 남깁니다. (1,10), (2,NULL)이 공통이며 (1,20)과 (2,20)은 다릅니다.';focus='INTERSECT'
    elif qid=='S13-A04-minus-dedup':
        combined=[r for r in dict.fromkeys(data['A']) if r not in data['B']];phrase='MINUS는 왼쪽 A에 있으면서 오른쪽 B에는 없는 전체 열 조합만 남기며 중복은 제거합니다. 2와 NULL은 양쪽에 있어 제외하고 1은 한 번 남습니다.';focus='MINUS'
    elif qid=='S13-A05-parenthesized-difference':
        inner=list(dict.fromkeys(data['B']+data['C'])); w.add('괄호 안 · B UNION C 먼저 이해','안쪽 B의 2와 C의 3,4를 합치면 2,3,4입니다. 이 결과를 바깥 MINUS의 오른쪽 입력으로 사용합니다.','SELECT v FROM B UNION SELECT v FROM C',table('오른쪽 차집합 입력',keys,inner)); combined=[r for r in dict.fromkeys(data['A']) if r not in inner];phrase='A의 1,2,3에서 안쪽 결과 2,3,4와 같은 값을 제외하면 1만 남습니다.';focus='MINUS'
    elif qid=='S13-A06-difference-count-empty':
        combined=[];phrase='같은 입력 A에서 A 자신을 빼므로 남는 행은 0개입니다. NULL도 집합 비교에서 같은 조합으로 제거됩니다.';focus='MINUS'
    else: raise ValueError('미작성 집합 유형')
    w.add('집합 연산 · 행 조합 확인',phrase+' 이는 NULL= NULL 일반 비교와 구별되는 집합의 중복/동일 행 판단입니다.',focus,table('집합 연산 결과',keys,combined))
    if 'COUNT' in sql:
        if qid=='S13-A02-all-count': values=[[len(combined),sum(r[0] is not None for r in combined)]];text='COUNT(*)는 7행 전부, COUNT(v)는 v가 NULL인 2행을 제외하여 5입니다.'
        else: values=[[0]];text='바깥 COUNT(*)는 빈 입력 행 수를 세어 0을 담은 결과 한 행을 만듭니다.'
        w.add('바깥 집계 · 행과 값 구별',text,'COUNT(*)',table('바깥 집계값',['COUNT(*)','COUNT(v)'] if len(values[0])==2 else ['COUNT(*)'],values))
    else: values=combined
    executed=re.sub(r'\bMINUS\b','EXCEPT',sql)
    cols,final=run(db,executed); assert equal_rows(values,final)
    final_step(w,cols,final); record_run(q,executed,final,['set'], 'MINUS만 SQLite EXCEPT로 명시 변환; Python 행집합 연산 독립 대조')
    db.close(); return w.finish(engine_mode='SQLite에서 MINUS는 EXCEPT로 명시 변환, UNION/INTERSECT 원문 실행. Python 행집합·bag 계산 독립 대조'),['set']

def learning_example():
    rows=[[1001,'박강열',10,900],[1002,'유성재',20,700],[1003,'양지훈',20,500],[1004,'박보성',30,600],[1005,'이승현',30,300],[1006,'김현수',None,800]]
    cols=['EMP_ID','EMP_NAME','DEPT_ID','SALARY']
    sql='SELECT EMP_NAME, SALARY\nFROM EMPLOYEE\nWHERE DEPT_ID NOT IN (\n    SELECT DEPT_ID\n    FROM EMPLOYEE\n    WHERE SALARY >= 700\n)\nAND SALARY > ANY (\n    SELECT SALARY\n    FROM EMPLOYEE\n    WHERE DEPT_ID = 30\n);'
    q=dict(id='learning-employee-not-in-any',version=1,title='NOT IN과 ANY를 실제 사원 값으로 따라 읽기',stem='사용자가 제공한 설명 방식 확인용 가상 예제입니다. 실제 기출문제가 아닙니다. 이름·부서·급여는 모두 가상입니다.',sql=sql,tables=[dict(title='EMPLOYEE',columns=cols,rows=rows_norm(rows))],choices=[dict(id='a',text='박강열, 김현수',reason='두 사람 모두 ANY는 TRUE지만 NOT IN이 FALSE/UNKNOWN이어서 남지 않는다.'),dict(id='b',text='유성재, 박보성',reason='NOT IN은 각각 FALSE/UNKNOWN이므로 남지 않는다.'),dict(id='c',text='박강열만 출력된다',reason='박강열의 DEPT_ID=10은 안쪽 목록에 있어 NOT IN이 FALSE다.'),dict(id='d',text='한 행도 출력되지 않는다',reason='두 조건의 AND가 TRUE인 행이 없다.')],correctChoiceIds=['d'],dialect='Oracle',dialectVersion='19c',fixture=dict(expectedRows=[],ordered=False))
    w=Walk(q)
    w.add('바깥 SELECT · 무엇을 구하는 문제인가','최종적으로 EMP_NAME(사원 이름), SALARY(급여)를 보여 달라는 문제입니다. 지금은 출력 목표만 읽습니다. 이 첫 줄을 먼저 계산한다는 뜻이 아니며 실제 값은 FROM과 조건을 확인한 뒤 구합니다.','SELECT EMP_NAME, SALARY')
    w.add('바깥 FROM · 어떤 표인가','EMPLOYEE는 사원 표입니다. EMP_ID는 사원 식별자, EMP_NAME은 이름, DEPT_ID는 부서 번호, SALARY는 가상 급여입니다. 처음에는 사원 6명 모두가 비교 후보입니다.','FROM EMPLOYEE',table('시작 사원 6명',cols,rows))
    first=[r for r in rows if r[3]>=700]
    for r in rows:
        w.add('첫 번째 안쪽 WHERE · '+r[1],f'{r[1]}의 SALARY={r[3]}을 SALARY >= 700에 대입합니다. {r[3]} >= 700은 '+('TRUE이므로 이 사원을 남깁니다.' if r[3]>=700 else 'FALSE이므로 이 안쪽 조회에서는 제외합니다.'),'SALARY >= 700',table('현재 사원의 급여 검사',cols+['판정'],[r+[truth(int(r[3]>=700))]]),focus_cells=[dict(row=0,column=3)])
    w.add('첫 번째 안쪽 SELECT · 부서만 가져오기','남은 박강열의 DEPT_ID=10, 유성재의 DEPT_ID=20, 김현수의 DEPT_ID=NULL을 읽습니다. 따라서 목록은 (10, 20, NULL)입니다. 급여 조건으로 사람을 고른 뒤 그 사람의 부서 번호를 가져온 것입니다.','SELECT DEPT_ID',table('급여 조건 통과자의 부서',['EMP_ID','EMP_NAME','DEPT_ID'],[r[:3] for r in first]),focus_cells=[dict(row=i,column=2) for i in range(len(first))])
    notin=[]
    for r in rows:
        d=r[2]; value=False if d in (10,20) else None; notin.append(value)
        comparisons=[None if d is None or x is None else d!=x for x in (10,20,None)]
        text=' AND '.join(f'{display(d)} <> {display(x)} ({"UNKNOWN" if v is None else str(v).upper()})' for x,v in zip((10,20,None),comparisons))
        w.add('바깥 NOT IN · '+r[1],f'{r[1]}의 DEPT_ID={display(d)}를 각 값과 다르다고 비교합니다. '+text+' → '+truth(value)+'. FALSE가 하나라도 있으면 AND는 FALSE이고, FALSE 없이 UNKNOWN이 남으면 UNKNOWN입니다.','DEPT_ID NOT IN',table('NOT IN 판단',['EMP_NAME','DEPT_ID','NOT IN'],[[r[1],d,truth(value)]]),focus_rows=[0])
    second=[r for r in rows if r[2]==30]
    w.add('두 번째 안쪽 WHERE · 30번 부서','EMPLOYEE에서 DEPT_ID=30인 사원은 박보성(600), 이승현(300)입니다. 김현수는 DEPT_ID=NULL이므로 NULL=30은 UNKNOWN이어서 포함하지 않습니다.','DEPT_ID = 30',table('30번 부서 사원',cols,second),focus_cells=[dict(row=i,column=2) for i in range(len(second))])
    w.add('두 번째 안쪽 SELECT · 급여 목록','박보성의 SALARY=600과 이승현의 SALARY=300을 가져오므로 (600, 300)입니다. 이 목록에는 부서 번호나 이름이 아니라 급여가 들어갑니다.','SELECT SALARY',table('ANY에 넘길 급여',['EMP_NAME','SALARY'],[[r[1],r[3]] for r in second]),focus_cells=[dict(row=i,column=1) for i in range(len(second))])
    anyvalues=[]
    for r in rows:
        sal=r[3]; value=(sal>600 or sal>300);anyvalues.append(value)
        w.add('바깥 ANY · '+r[1],f'{r[1]}의 SALARY={sal}: ({sal}>600 → {str(sal>600).upper()}) OR ({sal}>300 → {str(sal>300).upper()}) = {str(value).upper()}. ANY는 비교 하나라도 TRUE이면 TRUE입니다.','SALARY > ANY',table('ANY 판단',['EMP_NAME','SALARY','> 600','> 300','ANY'],[[r[1],sal,str(sal>600).upper(),str(sal>300).upper(),str(value).upper()]]),focus_rows=[0])
    def and3(a,b): return False if a is False or b is False else (None if a is None or b is None else True)
    combined=[and3(a,b) for a,b in zip(notin,anyvalues)]
    output=[[r[1],r[3]] for r,v in zip(rows,combined) if v is True]
    w.add('AND · 두 조건을 함께 적용','WHERE는 두 조건의 AND가 TRUE인 행만 남깁니다. 이승현은 UNKNOWN AND FALSE = FALSE입니다. UNKNOWN을 FALSE와 같은 값으로 바꾸는 규칙이 아니라, AND 진리표의 결과입니다.','AND',table('두 조건의 최종 판단',['EMP_NAME','NOT IN','ANY','AND'],[[r[1],display(a) if a is not None else 'UNKNOWN',str(b).upper(),truth(v)] for r,a,b,v in zip(rows,notin,anyvalues,combined)]))
    w.add('SELECT · 마지막에 정답 연결','TRUE인 행이 없으므로 EMP_NAME, SALARY를 출력할 행도 없습니다. 정답은 ④ 한 행도 출력되지 않는다입니다. ①은 NOT IN에서 둘 다 남지 않고, ②도 NOT IN이 TRUE가 아니며, ③ 박강열은 목록의 10과 같아 제외됩니다.','SELECT EMP_NAME, SALARY',table('최종 결과',['EMP_NAME','SALARY'],output))
    w.add('전체 과정을 이해한 뒤 · 빠른 확인','이 예제의 NOT IN 목록에 NULL이 들어 있어 TRUE인 행이 없다는 점으로 빠르게 0행을 판단할 수 있습니다. 단, 빈 안쪽 조회 결과와 NULL 한 행은 다릅니다. 먼저 두 안쪽 목록이 누구의 어떤 값에서 나왔는지 설명할 수 있어야 합니다.','DEPT_ID NOT IN')
    db=sqlite3.connect(':memory:'); db.execute('CREATE TABLE EMPLOYEE(EMP_ID INTEGER,EMP_NAME TEXT,DEPT_ID INTEGER,SALARY INTEGER)'); db.executemany('INSERT INTO EMPLOYEE VALUES(?,?,?,?)',rows)
    executed='SELECT EMP_NAME,SALARY FROM EMPLOYEE WHERE DEPT_ID NOT IN (SELECT DEPT_ID FROM EMPLOYEE WHERE SALARY>=700) AND (SALARY>600 OR SALARY>300)'
    _,actual=run(db,executed); assert actual==output==[]
    assert notin==[False,False,False,None,None,None] and anyvalues==[True,True,True,True,False,True] and combined==[False,False,False,None,False,None]
    record_run(q,executed,actual,['not-in','any','null','subquery'],'Python 3값 논리 및 실제 ANY 목록을 OR로 바꾼 SQLite 비교 실행')
    doc=w.finish(engine_mode='Python 3값 논리 계산 + 실제 ANY 급여 목록 (600,300)의 OR식으로 명시 변환한 SQLite 검산; Oracle 원문 실행 아님')
    doc['sourceUrls']=[URL+'IN-Condition.html',URL+'Comparison-Conditions.html',URL+'Nulls.html',URL+'Logical-Conditions.html']
    db.close();return doc

def main():
    qs=source_questions(); entries=[]; coverage=[]; failures=[]
    for q in qs:
        if not q.get('sql'):
            coverage.append(dict(questionId=q['id'],status='existing-concept-explanation',reason='SQL 코드 없음: 기존 개념·표 해설 보존. 가짜 SQL 단계 미생성.')); continue
        try:
            if q['id'].startswith('S12-'): doc,categories=subquery_walk(q)
            elif q['id'].startswith('S13-'):doc,categories=set_walk(q)
            elif 'OVER(' in q['sql'] or 'OVER (' in q['sql']: doc,categories=window_walk(q)
            else: doc,categories=generic(q)
            path=q['id']+'.json'; dump(OUT/path,doc)
            entries.append(dict(questionId=q['id'],file=path))
            coverage.append(dict(questionId=q['id'],status='applied',categories=categories,reason='현재 입력값 및 fixture 일치. SQLite 비교 검산; Oracle 19c 실행 미실시.'))
        except (ValueError,AssertionError,sqlite3.Error,KeyError) as e:
            reason=str(e)
            if reason=='wrong number of arguments to function REPLACE()':reason='Oracle REPLACE의 생략 인자 동작을 SQLite 원문으로 검증할 수 없어 기존 해설 유지'
            if reason=='cannot commit - no transaction is active':reason='초기 설정에 뷰·UPDATE·COMMIT이 포함되어 세션/트랜잭션 의미를 Oracle에서 검증하지 못함'
            if reason=="원본 fixture 불일치: [('',)]":reason='SQLite는 범위 밖 SUBSTR을 빈 문자열로 반환하지만 원본 Oracle 예상값은 NULL: 다른 엔진 결과를 채택하지 않고 기존 해설 유지'
            coverage.append(dict(questionId=q['id'],status='existing-explanation',reason=reason))
    example=learning_example(); dump(OUT/(example['id']+'.json'),example)
    learning=[dict(id=example['id'],title=example['source']['title'],noteIds=['note-S06','note-S12'],file=example['id']+'.json')]
    index=dict(schemaVersion=1,version=VERSION,entries=entries,learningExamples=learning)
    dump(OUT/'index.json',index); dump(OUT/'coverage.json',coverage)
    dump(EVIDENCE/'engine-checks.json',RUNS)
    ASSETS.mkdir(parents=True,exist_ok=True)
    for entry in entries: shutil.copyfile(OUT/entry['file'],ASSETS/entry['file'])
    for entry in learning: shutil.copyfile(OUT/entry['file'],ASSETS/entry['file'])
    shutil.copyfile(OUT/'index.json',ASSETS/'index.json')
    summary=dict(questionCount=len(qs),sqlQuestionCount=sum(bool(q.get('sql')) for q in qs),applied=len(entries),notAppliedSql=sum(x['status']=='existing-explanation' for x in coverage),nonSql=sum(x['status']=='existing-concept-explanation' for x in coverage),learningExamples=len(learning),engine='SQLite '+sqlite3.sqlite_version,oracleEngineExecuted=False,assetBytes=sum((ASSETS/f).stat().st_size for f in ['index.json']+[e['file'] for e in entries+learning]),categories=dict(collections.Counter(c for row in coverage for c in row.get('categories',[]))))
    dump(EVIDENCE/'summary.json',summary)
    dump(EVIDENCE/'source-file-hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'content/part-a.json',ROOT/'content/part-b.json',ROOT/'content/course-pack.json',ROOT/'app/src/main/assets/content-pack.json',ROOT/'app/src/main/assets/course-pack.json']})
    report=['# SQL 따라 읽기 자료 적용표','',
      '대상은 기존 앱의 독자 문항 661개이며 SQL이 있는 217개를 전수 분류했다. PDF 기출문항을 복제하거나 기존 문제의 정답·ID·난이도·보기·원본 표를 고치지 않았다. PDF 페이지 정보는 현재 원본 문항에 없어 만들어 적지 않았다.','',
      f'- 새 단계 해설 적용: **{len(entries)} / 217문항**. 전체 SQL 문항 적용 완료가 아니다.',
      f'- 기존 해설 유지: **{summary["notAppliedSql"]}문항**. 미적용 이유는 아래 문항별 목록에 기록했다.',
      '- SQL 없는 개념 문항 444개: 기존 개념·표 해설 유지. 가짜 SQL 실행 단계를 생성하지 않았다.',
      '- 사용자 EMPLOYEE 기준 예제 1개: 기존 문제와 별개의 가상 학습 예제. note-S06 및 note-S12에 연결할 수 있다. 6명의 양쪽 조건과 UNKNOWN AND FALSE까지 계산하고 끝에 정답을 제시한다.',
      '- 기존 63강·95예제·189확인문제는 수정하지 않았다. 새 자료를 기존 예제와 같은 데이터라고 합치지 않았다.','',
      '## 적용 내용','',
      '단순 행 수 요약 대신 WHERE 각 행의 실값 대입, JOIN 후보 쌍과 일치/미일치, 그룹별 원본 값과 집계 대상, COUNT(*)/COUNT(식), NVL 적용 시점, HAVING 판단, SELECT 계산값, DISTINCT 조합, 정렬을 별도 단계로 만든다. 필요한 절만 포함한다. 서브쿼리는 안쪽 값이 어디에서 나오는지, 상관 서브쿼리는 현재 바깥 행이 어떤 안쪽 조건값을 제공하는지 보여 준다. 분석 함수는 현재 행마다 실제 파티션/프레임을 표시한다.','',
      '| 유형 | 적용 문항 수 (중복 집계) |','|---|---:|']
    report += [f'| {k} | {v} |' for k,v in sorted(summary['categories'].items())]
    report += ['', '## 검증과 한계','',
      '- 빌드: `python scripts/build_walkthroughs.py`. 각 적용 원문의 값 결과를 기존 fixture와 대조한다. 순서가 명시된 경우 순서까지, 아니면 중복을 보존하는 bag으로 비교한다.',
      '- 검증: `python scripts/validate_walkthroughs.py`. 13개 경계 검사, 원본 스냅샷 동일성, SQL 강조 위치, 단계 ID, 표의 행/열 크기, 셀 범위, 최종 예상표, 앱 자산 미러를 검사한다. 실제 결과는 `evidence/sql-walkthroughs-20261006/validation.json`에 기록한다.',
      f'- 실제 비교 엔진은 **SQLite {sqlite3.sqlite_version}**다. **Oracle 19c 실행은 하지 않았다.** Oracle 공식 문서 의미 대조·SQLite 검산·Python 독립 값 계산을 구별한다. SQLite 통과를 Oracle 전체 호환 증명으로 쓰지 않는다.',
      '- SQLite에서 Oracle 기본 NULL 정렬 위치를 ASC NULLS LAST / DESC NULLS FIRST로 명시하고, 숫자 NVL/MOD 함수를 등록했다. ANY는 현재 실제 목록의 OR로, 빈 ALL은 TRUE로, MINUS는 EXCEPT로 명시 변환한다. 원본 SQL은 보존하며 실행한 비교 SQL은 engine-checks.json에 따로 남긴다.',
      '- 윈도 15문항의 프레임·순위·참조값은 Python으로 다시 계산해 SQLite와 비교했다. 범위 밖 DESC/NULL RANGE 또는 동점을 끝내지 못하는 행 위치 함수는 자동 적용하지 않는다.',
      '- Oracle 전용 함수·계층·PIVOT·그룹 확장·상태 변경 등의 미적용 사유는 기능 삭제가 아니다. 원래 해설을 그대로 읽을 수 있다. SQL 없는 문항에 새 SQL 과정을 붙이지 않는다.',
      '- 이 자료는 학습용 논리 설명이며 물리 실행 계획, 실제 엔진 임시표, 사람 전문가 검수, 학습 효과 검증 결과가 아니다. 앱 UI/필기/회전/실물 Galaxy 검증은 별도 QA가 맡는다.',
      f'- 자산 크기 실측: 인덱스와 {len(entries)+len(learning)}개 개별 JSON 합계 **{summary["assetBytes"]:,} bytes**. APK 압축 증가량·읽기 속도·메모리 개선은 이 숫자로 주장하지 않는다.','',
      '## 문항별 적용/미적용','', '| 문제 ID | 단원 | 상태 | 근거 |','|---|---|---|---|']
    qmap={q['id']:q for q in qs}
    for row in coverage:
        if not qmap[row['questionId']].get('sql'):continue
        status='적용' if row['status']=='applied' else '기존 해설 유지'
        report.append('| '+row['questionId']+' | '+', '.join(qmap[row['questionId']]['objectiveIds'])+' | '+status+' | '+row['reason'].replace('|','/')+' |')
    report += ['', '## 자료 관리와 되돌리기','',
      '`content/sql-walkthroughs/`가 새 자료의 기준이며 `scripts/build_walkthroughs.py`로 만든다. `app/src/main/assets/sql-walkthroughs/`는 동일한 배포 미러다. 원본 content-pack/course-pack 빌더를 실행하지 않는다. 원본 질문 ID와 source 전체 스냅샷이 다르면 앱은 잘못된 단계 연결을 거절해야 한다.',
      '되돌릴 때는 새 UI 연결을 끄고 새 sql-walkthroughs 인덱스/자산만 이전 백업으로 복원한다. 학습 DB·답안·필기·기존 콘텐츠는 이 스크립트의 입력 대상도 수정 대상도 아니다.','',
      '## 공식 의미 참고','']
    report += ['- ['+u.rsplit('/',1)[1].replace('.html','')+']('+u+')' for u in URLS+[URL+'Logical-Conditions.html']]
    (ROOT/'docs/sql-walkthrough-coverage.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':main()
