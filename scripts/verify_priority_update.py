"""Verify this additive update against the preserved v0.1.0 content and review hashes."""
import json, hashlib, pathlib, collections, datetime

ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
    before=read('evidence/priority-update-before.json')
    pack=read('app/src/main/assets/content-pack.json')
    notes={n['id']:n for n in pack['notes']};questions={q['id']:q for q in pack['questions']}
    for qid,sha in before['questionHashes'].items():assert digest(questions[qid])==sha,qid
    for nid,old in before['notes'].items():
        blocks={b['id']:b for b in notes[nid]['blocks']}
        for bid,sha in old['blocks'].items():assert digest(blocks[bid])==sha,(nid,bid)
    assert pack['legacyNoteVersions']=={nid:n['version'] for nid,n in before['notes'].items()}
    added=set(questions)-set(before['questionHashes'])
    approved=set();explained=set();reviewed_notes=set()
    for side in ['a','b']:
        comparison=read(f'qa/priority-{side}-comparison.json')
        for row in comparison['results']:
            assert row['status']=='answer_agrees' and not row.get('conditionsOrIssues'),row['questionId']
            q=questions[row['questionId']]
            assert digest(dict(q,status='quarantined'))==row['sourceQuestionSha256'],q['id']
            approved.add(q['id'])
        for row in read(f'qa/priority-{side}-explanations.json')['results']:
            q=questions[row['questionId']]
            assert not row.get('issues') and digest(dict(q,status='quarantined'))==row['sourceQuestionSha256'],q['id']
            explained.add(q['id'])
        report=read(f'evidence/priority-note-review-{side}.json')
        for row in report.get('results',report.get('notes',[])):
            assert digest(notes[row['noteId']])==row.get('sourceNoteSha256',row.get('hash')),row['noteId']
            reviewed_notes.add(row['noteId'])
    changed_notes={n['id'] for n in notes.values() if n['id'] not in before['notes'] or len(n['blocks'])!=len(before['notes'][n['id']]['blocks'])}
    assert changed_notes<=reviewed_notes
    assert added==approved==explained
    assert all(q['status']=='published' for q in questions.values())
    priorities=pack['studyPriorities']
    assert set(p['objectiveId'] for p in priorities)==set(n['objectiveId'] for n in notes.values())
    result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,
            'preservedQuestions':len(before['questionHashes']),'preservedNoteBlocks':sum(len(n['blocks']) for n in before['notes'].values()),
            'addedNotes':len(notes)-len(before['notes']),'expandedExistingNotes':len(changed_notes)-(len(notes)-len(before['notes'])),
            'addedBlocks':sum(len(n['blocks']) for n in notes.values())-sum(len(n['blocks']) for n in before['notes'].values()),
            'newQuestionsIndependentlySolvedAndExplanationsRead':len(added),'notes':len(notes),'questions':len(questions),
            'priorities':dict(collections.Counter(p['level'] for p in priorities)),
            'educatorEmphasisCount':sum(p['frequencyStatus']=='educator_emphasis' for p in priorities),
            'boundary':'Content identity, AI review evidence, and metadata. Not human expert review, DBMS execution, device QA, or exam-frequency validation.'}
    (ROOT/'evidence/priority-update-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
