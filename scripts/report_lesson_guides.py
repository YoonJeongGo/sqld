"""Rebuild the traceable lesson/example/PDF map from reviewed authored guides."""
import collections, json, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(path): return json.loads(path.read_text(encoding='utf-8'))

def main():
    course=read(ROOT/'content/course-pack.json')
    pack=read(ROOT/'app/src/main/assets/content-pack.json')
    visuals=read(ROOT/'content/course-visuals.json')
    guides=[read(ROOT/f'content/lesson-guides/{lesson["id"]}.json') for lesson in course['lessons']]
    rows=[]
    lines=['# 63강 추가 해설 연결표 — 2026-10-12','',
           '원본 내용은 유지하고 별도 설명을 보완했다. 아래 개수는 적용 위치의 목록이며 학습효과나 공식 출제범위 충족률을 뜻하지 않는다.',
           '원본 PDF 페이지는 제공된 파일의 물리 페이지다. 앱의 창작 예제와 PDF 예제는 서로 다른 입력값일 수 있다.', '',
           '| 강의 | 보완 목적 | 원본 예제 / 확인문제 | 새 단계 | 원본 PDF 참조 | 그림 |','|---|---|---:|---:|---|---|']
    for lesson,guide in zip(course['lessons'],guides):
        assert guide['source']==lesson
        pictures=[v['id'] for v in visuals['visuals'] if lesson['id'] in v['lessonIds']]
        examples=guide['examples']+[s['guide'] for s in guide.get('supplementalExamples',[])]
        pdf=' / '.join(f'{p["sectionId"]} p{p["fromPage"]}–{p["toPage"]}' for p in guide['pdfRefs'])
        step_count=sum(len(e['steps']) for e in examples)
        rows.append({'lessonId':lesson['id'],'status':'원본 유지 + 설명 보완','purpose':guide['purpose'],
                     'originalExampleIds':[e['id'] for e in lesson['examples']],
                     'supplementalExampleIds':[s['example']['id'] for s in guide.get('supplementalExamples',[])],
                     'checkIds':[c['id'] for c in lesson['selfChecks']],
                     'authoredSteps':step_count,'pdfRefs':guide['pdfRefs'],'visualIds':pictures,
                     'reviewNotes':guide['reviewNotes']})
        clean=guide['purpose'].replace('|','/').replace('\n',' ')
        lines.append(f'| {lesson["id"]} {lesson["title"]} | {clean} | {len(lesson["examples"])} / {len(lesson["selfChecks"])} | {step_count} | {pdf} | {", ".join(pictures) or "기존 표·개념도 유지"} |')
    links=[{'questionId':q['id'],'lessonIds':[l['id'] for l in course['lessons'] if q['explanation']['relatedNoteId'] in l['relatedNoteIds']],
            'display':'채점 후 별도 강의 예제로 연결; 해당 문항 전용 신규 정답풀이 아님'} for q in pack['questions']]
    assert all(link['lessonIds'] for link in links)
    totals={'lessons':len(guides),'originalExamples':sum(len(g['examples']) for g in guides),
            'selfChecks':sum(len(g['checkGuides']) for g in guides),'supplements':sum(len(g.get('supplementalExamples',[])) for g in guides),
            'authoredSteps':sum(r['authoredSteps'] for r in rows),'linkedQuestions':len(links),
            'visualFiles':len(visuals['visuals']),'linkedVisualLessons':sum(bool(r['visualIds']) for r in rows),
            'guideSourceBytes':sum((ROOT/f'content/lesson-guides/{g["lessonId"]}.json').stat().st_size for g in guides)}
    lines += ['', '## 예제와 자료의 구분', '',
              '- 원본 95예제·189확인문제의 순서와 ID를 유지한다. FK와 INSERT 순서 가상 예제 2개는 별도 표시하며 시험 문제 수에 합산하지 않는다.',
              '- 그림 27장의 기존 자산과 설명을 재사용한다. 연결 없는 23강은 원본 표·개념도를 유지하며 관련 없는 그림을 넣지 않는다.',
              '- 전체 661문항은 채점 후 관련 강의와 연결된다. 기존 문항별 SQL 따라 읽기 133개를 661개의 신규 문항별 해설로 계산하지 않는다.',
              '- 원본 PDF 전체 문항의 신규 해설, 공식 시험 전 범위 검증, 학습자 전이 평가, Oracle/SQL Server 실제 실행은 미완료다.',
              '- 강의별 주의점과 예제 ID는 evidence/explanation-upgrade-20261012/coverage.json에서 확인한다.', '']
    (ROOT/'docs/lesson-guide-coverage-20261012.md').write_text('\n'.join(lines),encoding='utf-8')
    (ROOT/'evidence/explanation-upgrade-20261012/coverage.json').write_text(json.dumps({'counts':totals,'lessons':rows,'questionLinks':links},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(totals,ensure_ascii=False))

if __name__=='__main__':main()
