"""Validate reviewed standalone author files and build the additional offline app bank.

Original content-pack/course-pack and all learner data are read only.
Independent AI review is exact-byte-bound and is not human or DBMS execution proof.
"""
from pathlib import Path
import argparse,collections,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'evidence/unit-practice-20261015'
PARTS=['1-1','1-2','2-1','2-2','2-3']
TYPE_LABELS={'concept':'개념 회상','recall':'개념 회상','discriminate':'조건 구분','apply':'상황 적용','application':'상황 적용','case':'사례 판단','review':'개념 복습','mock':'단원 모의'}
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 pending=path.with_suffix('.pending');pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');pending.replace(path)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--import-staging',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
 course=read(ROOT/'content/course-pack.json');base=read(ROOT/'app/src/main/assets/content-pack.json')
 lessons={x['id']:x for x in course['lessons']};notes={x['id']:x for x in base['notes']};objectives={x['id']:x for x in base['objectives']}
 registry={x['sourceId']:x for x in base['sources']}
 bank={'version':'2026.10.15.1','parts':[],'links':[],'questions':[],'sources':[]};counts={};all_ids=set(x['id'] for x in base['questions']);sources={}
 for part in PARTS:
  authored=ROOT/f'content/part-unit-{part}.json'
  staging=ROOT/f'qa/workbooks-20261015/data/{part}.json'
  source=staging if args.import_staging else authored
  raw=read(source)
  assert raw['partId']==part,part
  review=read(EVIDENCE/f'review-{part}.json')
  assert review['sourceSha256']==digest(source),(part,'review binding mismatch')
  assert review['status']=='pass' and review['reviewerRole']=='independent_ai' and not review.get('unresolvedIssues'),part
  assert len(raw['mocks'])==3 and all(len(form)==50 for form in raw['mocks']),part
  lesson_ids=[x['id'] for x in course['lessons'] if x['partId']==part]
  assert collections.Counter(x['lessonId'] for x in raw['review'])=={x:3 for x in lesson_ids},part
  assert set(review['reviewedQuestionIds'])=={q['id'] for q in raw['review']+sum(raw['mocks'],[])},part
  part_entry={'id':part,'title':next(p['title'] for p in course['parts'] if p['id']==part),'reviewIds':[],'forms':[]}
  stemset=set()
  for form_number,items in [(0,raw['review'])]+[(i+1,qs) for i,qs in enumerate(raw['mocks'])]:
   ids=[]
   assert len(set(q['lessonId'] for q in items))==len(lesson_ids),(part,form_number,'lesson coverage')
   if form_number:
    assert collections.Counter(q['difficulty'] for q in items)=={'basic':10,'intermediate':30,'advanced':10},(part,form_number,'author difficulty distribution')
   for number,item in enumerate(items,1):
    qid=item['id'];assert qid.startswith('unit-') and qid not in all_ids,qid;all_ids.add(qid)
    assert item['lessonId'] in lesson_ids,qid
    assert len(item['choices'])==4 and len(set(item['choices']))==4 and item['answerIndex'] in range(4),qid
    assert len(item['stem'])>=10 and len(item['explanation'])>=35,qid
    assert not re.search(r'[\ufffd]|\?{3,}',item['stem']+item['explanation']),qid
    key=(re.sub(r'\s+','',item['stem']),item.get('sql',''),json.dumps(item.get('tables',[]),ensure_ascii=False),tuple(sorted(item['choices'])))
    assert key not in stemset,(qid,'exact repeated question');stemset.add(key)
    for table in item.get('tables',[]):
     assert table['headers'] and all(len(row)==len(table['headers']) for row in table['rows']),qid
    lesson=lessons[item['lessonId']];note=notes[lesson['relatedNoteIds'][0]];objective=objectives[note['objectiveId']]
    correct=f'{qid}-c{item["answerIndex"]+1}'
    source_ref=item.get('source') or ('https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/index.html' if part.startswith('2-') else 'https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/data-integrity.html')
    source_url=source_ref if source_ref.startswith('https://') else registry.get(source_ref,{}).get('url')
    assert source_url and source_url.startswith('https://'),(qid,'unknown source reference',source_ref)
    if part=='2-3' and 'SQL Server' in item['stem'] and 'oracle.com' in source_url:
     page='truncate-table-transact-sql' if 'TRUNCATE' in item['stem']+item.get('sql','') else 'set-transaction-isolation-level-transact-sql'
     source_url=f'https://learn.microsoft.com/en-us/sql/t-sql/statements/{page}?view=sql-server-ver16'
    source_id='unit-doc-'+hashlib.sha256(source_url.encode()).hexdigest()[:12]
    sources[source_id]={'sourceId':source_id,'publisher':'Oracle' if 'oracle.com' in source_url else 'Reference document','title':source_url.rsplit('/',1)[-1],'url':source_url,'checkedAt':'2026-10-15','accessStatus':'reference_only','usageScope':'Original practice based on documented concepts; no copied exam questions','license':'Referenced documentation; original question authorship'}
    choices=[{'id':f'{qid}-c{i+1}','text':text,'reason':item['explanation'] if i==item['answerIndex'] else f'이 보기의 주장: {text}\n판단 근거: {item["explanation"]}'} for i,text in enumerate(item['choices'])]
    tables=[{'title':t['title'],'columns':t['headers'],'rows':t['rows']} for t in item.get('tables',[])]
    rawsteps=item.get('steps') or []
    steps=[{'title':'조건과 값을 따라 확인','text':item['explanation']}]+[{'title':f'추가 확인 {i+1}','text':str(s)} for i,s in enumerate(rawsteps)]
    q={'id':qid,'version':1,'subjectId':objective['subjectId'],'topicId':objective['topicId'],'objectiveIds':[objective['id']],
       'familyId':re.sub(r'(?<=mock-)[123](?=-)', 'family',qid) if form_number else qid,
       'kind':'mock' if form_number else ('recall' if item['difficulty']=='basic' else 'application'),
       'title':lesson['title']+' · '+TYPE_LABELS.get(item['type'],item['type']),'stem':item['stem'],'choices':choices,'correctChoiceIds':[correct],
       'explanation':{'summary':item['explanation'],'prerequisites':[lesson['title']],'conditions':['지문의 DBMS와 입력 데이터 조건을 기준으로 판단한다.'],'steps':steps,'memory':item.get('pitfall') or '조건과 실제 값을 먼저 대조하고 결과를 판단한다.','relatedNoteId':note['id']},
       'sourceIds':[source_id],'sourceType':'original_mock' if form_number else 'original_practice','verification':'independent_ai_review','status':'published',
       'dialect':'conceptual' if part.startswith('1-') or item['lessonId']=='2-3-04' else ('SQL Server' if 'SQL Server' in item['stem'] else 'Oracle'),'dialectVersion':('n/a' if part.startswith('1-') or item['lessonId']=='2-3-04' else (re.search(r'SQL Server\s+(\d{4})',item['stem']).group(1) if re.search(r'SQL Server\s+(\d{4})',item['stem']) else ('n/a' if 'SQL Server' in item['stem'] else '19c'))),
       'difficulty':item['difficulty'],'difficultyReason':'Author target; no empirical exam-equivalence calibration','sql':item.get('sql') or None,'tables':tables,
       'mockSetId':f'unit:{part}:{form_number}' if form_number else None,'validationEvidence':[f'independent-review:review-{part}.json',f'authored-sha256:{digest(source)}','Original practice; no human expert or Oracle engine execution claim']}
    bank['questions'].append(q);bank['links'].append({'questionId':qid,'lessonId':item['lessonId'],'type':item['type']});ids.append(qid)
   if form_number:part_entry['forms'].append({'id':f'unit:{part}:{form_number}','number':form_number,'questionIds':ids})
   else:part_entry['reviewIds']=ids
  if args.import_staging:
   authored.write_bytes(source.read_bytes())
  all_items=raw['review']+sum(raw['mocks'],[])
  bank['parts'].append(part_entry);counts[part]={'review':len(raw['review']),'mocks':[len(x) for x in raw['mocks']],'types':dict(collections.Counter(x['type'] for x in raw['review'])),
   'sqlQuestions':sum(bool(q.get('sql')) for q in all_items),'tableQuestions':sum(bool(q.get('tables')) for q in all_items),
   'maxTableRows':max((len(t['rows']) for q in all_items for t in q.get('tables',[])),default=0),
   'maxTableColumns':max((len(t['headers']) for q in all_items for t in q.get('tables',[])),default=0)}
 bank['sources']=list(sources.values())
 target=ROOT/'content/unit-question-bank.json'
 if args.check:
  assert read(target)==bank,'Generated bank differs from reviewed author files'
  assert target.read_bytes()==(ROOT/'app/src/main/assets/unit-question-bank.json').read_bytes(),'Authored bank and app asset differ'
 else:
  write(target,bank)
  (ROOT/'app/src/main/assets/unit-question-bank.json').write_bytes(target.read_bytes())
  write(EVIDENCE/'content-validation.json',{'passed':True,'counts':counts,'questions':len(bank['questions']),'originalQuestionCount':len(base['questions']),'totalLoadedQuestions':len(base['questions'])+len(bank['questions']),'officialDifficultyEquivalenceVerified':False,'humanExpertReviewed':False,'oracleEngineExecuted':False})
 print(json.dumps({'questions':len(bank['questions']),'counts':counts},ensure_ascii=False))
if __name__=='__main__':main()
