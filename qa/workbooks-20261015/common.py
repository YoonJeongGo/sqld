"""Standalone authored worksheet data; never modifies the installed app's content."""
from pathlib import Path
import hashlib,json,random
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'qa/workbooks-20261015/data'
OUT.mkdir(parents=True,exist_ok=True)

def table(title,headers,rows):
    return {'title':title,'headers':headers,'rows':[[None if x is None else str(x) for x in row] for row in rows]}

def question(qid,lesson,kind,difficulty,stem,choices,answer,why,sql='',tables=None,steps=None,pitfall='',source=''):
    assert len(choices)==4 and len(set(choices))==4,(qid,choices)
    assert answer in range(4)
    order=list(range(4));random.Random(int(hashlib.sha256(qid.encode()).hexdigest()[:16],16)).shuffle(order)
    return {'id':qid,'lessonId':lesson,'type':kind,'difficulty':difficulty,'stem':stem,
        'choices':[str(choices[i]) for i in order],'answerIndex':order.index(answer),
        'explanation':why,'sql':sql,'tables':tables or [],'steps':steps or [],'pitfall':pitfall,'source':source}

def save(part,title,review,mocks):
    assert len(mocks)==3 and all(len(x)==50 for x in mocks),(part,[len(x) for x in mocks])
    allq=review+[q for exam in mocks for q in exam]
    assert len({x['id'] for x in allq})==len(allq)
    value={'schemaVersion':1,'partId':part,'title':title,'authorship':'original_practice',
        'dbms':'Oracle Database 19c unless the question explicitly states another DBMS',
        'difficultyClaim':'SQLD-level author target, not empirically calibrated or official questions',
        'review':review,'mocks':mocks}
    (OUT/f'{part}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    print(part,'review',len(review),'mocks',[len(x) for x in mocks])
