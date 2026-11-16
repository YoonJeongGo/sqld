"""Validate additive lesson explanations without touching original course/questions/records."""
from pathlib import Path
import argparse, json, hashlib, shutil

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def check_table(t):
    assert t['columns'] and all(isinstance(c,str) and c for c in t['columns'])
    assert all(len(row)==len(t['columns']) and all(v is None or isinstance(v,str) for v in row) for row in t['rows'])
def validate(guide,lesson):
    assert guide['schemaVersion']==1 and guide['lessonId']==lesson['id']
    assert guide['source']==lesson, 'Original lesson snapshot changed'
    assert [e['exampleId'] for e in guide['examples']]==[e['id'] for e in lesson['examples']]
    assert [c['checkId'] for c in guide['checkGuides']]==[c['id'] for c in lesson['selfChecks']]
    assert all(c['hint'].strip() and c['reasoning'].strip() for c in guide['checkGuides'])
    assert all(guide[k] for k in ['purpose','overview','terms','pitfalls','questions','pdfRefs'])
    for term in guide['terms']:assert all(term[k].strip() for k in ['token','kind','meaning','role'])
    for ref in guide['pdfRefs']:
        assert 1<=ref['fromPage']<=ref['toPage']<= {'1-1':27,'1-2':27,'2-1':137,'2-2':112,'2-3':21}[ref['sectionId']]
    pairs=list(zip(lesson['examples'],guide['examples']))+[(s['example'],s['guide']) for s in guide.get('supplementalExamples',[])]
    assert len({e['id'] for e,g in pairs})==len(pairs)
    for example,detail in pairs:
        assert detail['exampleId']==example['id']
        assert all(detail[k] for k in ['why','effect','prerequisites','steps','comparison','verification'])
        assert len({s['id'] for s in detail['steps']})==len(detail['steps'])
        assert not {'guide-purpose','guide-comparison'} & {s['id'] for s in detail['steps']}
        assert len(detail['steps'])<=98
        for t in example.get('tables',[])+example.get('results',[]):check_table(t)
        for step in detail['steps']:
            assert step['title'].strip() and step['text'].strip()
            for focus in step.get('codeFocus',[]):
                assert focus['needle'] and focus.get('occurrence',0)>=0
                sql=example.get('sql','');start=0
                for i in range(focus.get('occurrence',0)+1):
                    at=sql.find(focus['needle'],start);assert at>=0,(example['id'],focus);start=at+len(focus['needle'])
            assert all(h and h in step['text'] for h in step.get('highlights',[])),(example['id'],step['id'],'highlight')
            if t:=step.get('table'):
                check_table(t)
                assert all(0<=r<len(t['rows']) for r in step.get('focusRows',[]))
                assert all(0<=c['row']<len(t['rows']) and 0<=c['column']<len(t['columns']) for c in step.get('focusCells',[]))
            else:assert not step.get('focusRows') and not step.get('focusCells')
    return {'lessonId':lesson['id'],'originalExamples':len(lesson['examples']),'checks':len(guide['checkGuides']),
            'supplements':len(guide.get('supplementalExamples',[])),'steps':sum(len(d['steps']) for e,d in pairs)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--sync',action='store_true');args=parser.parse_args()
    course=read(ROOT/'content/course-pack.json');reports=[]
    lessons=[l for l in course['lessons'] if not args.pilot or l['id'] in ['2-1-03','2-1-05','2-1-10']]
    for lesson in lessons:
        p=ROOT/f'content/lesson-guides/{lesson["id"]}.json'
        try: reports.append(validate(read(p),lesson))
        except Exception as e: raise RuntimeError(f'{lesson["id"]}: {e}') from e
    baseline=read(ROOT/'backups/explanation-upgrade-20261012/hashes.json')
    protected=[p for p in baseline if p.startswith('content/') and not p.startswith('content/lesson-guides/')]
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==baseline[p] for p in protected),'Original authored material changed'
    if args.sync:
        target=ROOT/'app/src/main/assets/lesson-guides';target.mkdir(parents=True,exist_ok=True)
        for lesson in lessons:shutil.copyfile(ROOT/f'content/lesson-guides/{lesson["id"]}.json',target/f'{lesson["id"]}.json')
    equality={l['id']:(ROOT/f'content/lesson-guides/{l["id"]}.json').read_bytes()==(ROOT/f'app/src/main/assets/lesson-guides/{l["id"]}.json').read_bytes() for l in lessons}
    assert all(equality.values()),'Assets must match source; run with --sync after review'
    result={'scope':'pilot' if args.pilot else 'all63','lessons':reports,'originalContentFilesUnchanged':len(protected),'assetEquality':equality,
            'limits':['Structure and binding checks do not certify learning effectiveness','Oracle/SQL Server not executed by this validator']}
    out=ROOT/'evidence/explanation-upgrade-20261012';out.mkdir(parents=True,exist_ok=True)
    (out/('pilot-validation.json' if args.pilot else 'validation.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'lessons':len(reports),**{k:sum(r[k] for r in reports) for k in ['originalExamples','checks','supplements','steps']},'protected':len(protected)},ensure_ascii=False))
if __name__=='__main__':main()
