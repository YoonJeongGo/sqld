"""Validate separate SQL walkthrough assets and their source/answer boundaries."""
import collections
import hashlib
import json
import re
import unittest
from pathlib import Path

from build_walkthroughs import (ROOT, OUT, ASSETS, EVIDENCE, SOURCE_KEYS,
    source_questions, equal_rows, translation, parts, substitute, rows_norm)

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def validate():
    questions={q['id']:q for q in source_questions()};index=read(OUT/'index.json')
    coverage=read(OUT/'coverage.json'); covered={r['questionId']:r for r in coverage}
    assert len(covered)==len(coverage)==len(questions)==661
    assert covered.keys()==questions.keys()
    assert index['schemaVersion']==1 and isinstance(index['version'],str)
    entries=index['entries']; applied={e['questionId'] for e in entries}
    assert len(applied)==len(entries)
    assert applied=={r['questionId'] for r in coverage if r['status']=='applied'}
    assert all(questions[qid].get('sql') for qid in applied)
    files=[e['file'] for e in entries+index['learningExamples']]
    assert len(files)==len(set(files))
    assert all(re.fullmatch(r'[\w.-]+\.json',f,re.ASCII) for f in files)
    hashes={};steps=0;tables=0
    for e in entries+index['learningExamples']:
        d=read(OUT/e['file']);source=d['source'];sql=source['sql']
        assert d['id']==e.get('questionId',e.get('id'))
        if 'questionId' in e:
            q=questions[e['questionId']]
            assert source=={k:q[k] for k in SOURCE_KEYS},d['id']+' source drift'
        ids=set()
        for s in d['steps']:
            steps+=1
            assert s['id'] not in ids; ids.add(s['id'])
            assert s['title'].strip() and s['text'].strip()
            assert s['codeFocus']
            for prefix in ('FROM','GROUP BY','ORDER BY'):
                if s['title'].startswith(prefix+' ·'):assert s['codeFocus'][0]['needle'].startswith(prefix+' '),(d['id'],s['id'],'wrong clause highlight')
            for f in s['codeFocus']:
                assert f['needle'] and isinstance(f['occurrence'],int) and f['occurrence']>=0
                assert len(list(re.finditer(re.escape(f['needle']),sql)))>f['occurrence'],(d['id'],s['id'],f)
            assert all(h in s['text'] for h in s['highlights'])
            if t:=s.get('table'):
                tables+=1;assert t['title'].startswith('학습용 중간 결과 · ')
                assert t['columns'] and all(len(r)==len(t['columns']) for r in t['rows']),(d['id'],s['id'])
                assert all(v is None or isinstance(v,str) for r in t['rows'] for v in r)
                assert all(0<=r<len(t['rows']) for r in s['focusRows'])
                assert all(0<=c['row']<len(t['rows']) and 0<=c['column']<len(t['columns']) for c in s['focusCells'])
            else:assert not s['focusRows'] and not s['focusCells']
        assert d['verification']['oracleEngineExecuted'] is False
        assert d['verification']['expectedRowsMatch'] is True
        assert all(t['token'] and t['kind'] and t['meaning'] and t['role'] for t in d['terms'])
        assert all(u.startswith('https://docs.oracle.com/') for u in d['sourceUrls'])
        assert (ASSETS/e['file']).read_bytes()==(OUT/e['file']).read_bytes()
        hashes[e['file']]=hashlib.sha256((OUT/e['file']).read_bytes()).hexdigest()
        final=next(s['table'] for s in reversed(d['steps']) if s.get('table',{}).get('title')=='학습용 중간 결과 · 최종 결과')
        if 'questionId' in e:
            expected=rows_norm(questions[e['questionId']]['fixture']['expectedRows'])
            # String values remain exact here, including leading zeros and NULL.
            assert equal_rows(final['rows'],expected,questions[e['questionId']]['fixture']['ordered']),d['id']
    assert (ASSETS/'index.json').read_bytes()==(OUT/'index.json').read_bytes()
    runs=read(EVIDENCE/'engine-checks.json')
    assert {x['id'] for x in runs}=={e.get('questionId',e.get('id')) for e in entries+index['learningExamples']}
    assert all(x['match'] for x in runs)
    summary=dict(status='PASS',questions=661,sqlQuestions=sum(bool(q.get('sql')) for q in questions.values()),applied=len(entries),learningExamples=len(index['learningExamples']),steps=steps,intermediateTables=tables,sourceSnapshotEquality=True,assetMirrorEquality=True,allCodeFocusRangesValid=True,allFinalTablesMatchOriginalFixture=True,oracleEngineExecuted=False,sha256=hashes)
    EVIDENCE.mkdir(parents=True,exist_ok=True);(EVIDENCE/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='sha256'},ensure_ascii=False))

class Boundaries(unittest.TestCase):
    def test_duplicate_bag_is_not_set(self): self.assertFalse(equal_rows([[1],[1]],[[1]],False))
    def test_unordered_bag(self): self.assertTrue(equal_rows([[2],[1],[1]],[[1],[2],[1]],False))
    def test_ordered_difference(self):self.assertFalse(equal_rows([[1],[2]],[[2],[1]],True))
    def test_sql_null_not_string(self):self.assertFalse(equal_rows([[None]],[['NULL']]))
    def test_leading_zero_text_preserved(self):self.assertFalse(equal_rows([['02']],[['2']]))
    def test_number_format(self):self.assertTrue(equal_rows([[1.0]],[['1']]))
    def test_null_defaults_final(self):self.assertIn('x DESC NULLS FIRST',translation('SELECT x FROM T ORDER BY x DESC'))
    def test_null_defaults_window(self):self.assertIn('v DESC NULLS FIRST',translation('SELECT RANK() OVER(ORDER BY v DESC) FROM T'))
    def test_explicit_nulls_retained(self):self.assertEqual('SELECT x FROM T ORDER BY x DESC NULLS LAST',translation('SELECT x FROM T ORDER BY x DESC NULLS LAST'))
    def test_subquery_order_not_outer(self):self.assertEqual('y',parts('SELECT (SELECT x FROM T ORDER BY x) FROM U ORDER BY y')['ORDER BY'])
    def test_literal_not_clause(self):self.assertEqual("'FROM'",parts("SELECT 'FROM' FROM T")['SELECT'])
    def test_substitute_does_not_change_string_literal(self):self.assertEqual("2='x'",substitute("x='x'",['T.x'],[2]))
    def test_qualified_columns(self):self.assertEqual('1=2',substitute('A.k=B.k',['A.k','B.k'],[1,2]))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Boundaries)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    validate()
