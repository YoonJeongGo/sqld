"""One-time reviewed-material import. Never run the source archive's generators.

After integration, edit content/course-visuals.json as the sole authoring source;
validate_visuals.py --sync-assets publishes an identical offline asset pack.
"""
import argparse,json,shutil,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'evidence/incoming-visuals-27-20260929/SQLD_27_Visuals'
PILOT={11,14,18}

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');args=parser.parse_args()
    target=ROOT/'content/course-visuals.json'
    if target.exists():
        assert not args.pilot and read(target)['version']=='2026.09.29.pilot','Existing authored material must not be overwritten'
    reviews=read(ROOT/'evidence/visuals-review-a.json')+read(ROOT/'evidence/visuals-review-b.json')
    provenance=ROOT/'content/visual-source';provenance.mkdir(exist_ok=True)
    for name in ['manifest.json','scenes.json','sources.json']:
        source=INPUT/'data'/name;dest=provenance/name
        if dest.exists():assert dest.read_bytes()==source.read_bytes(),'Provenance must remain immutable'
        else:shutil.copy2(source,dest)
    by_number={x['number']:x for x in reviews};manifest=read(INPUT/'data/manifest.json')
    visuals=[];assets=ROOT/'content/course-visuals';assets.mkdir(exist_ok=True)
    for item in manifest:
        n=item['number']
        if args.pilot and n not in PILOT:continue
        guide=by_number[n];assert guide['lessonIds']==item['lesson_ids']
        assert all(guide['review'][k] for k in ['pngViewed','svgRead','scenesRead'])
        name=f'visual-{n:02}';correction=''
        for kind in ['png','svg']:
            source=INPUT/item[kind]
            if n==20:
                original=assets/'originals';original.mkdir(exist_ok=True);shutil.copy2(source,original/f'{name}.{kind}')
                source=ROOT/f'evidence/visuals-corrections/20-corrected.{kind}'
                correction='그림 정정: (과목) 소계에서 전체 합계로 가는 화살표의 잘못된 ‘지역 제거’를 ‘과목 제거’로 바로잡았어요. 표와 계산 결과는 같아요.'
            shutil.copy2(source,assets/f'{name}.{kind}')
        svg=ET.fromstring((assets/f'{name}.svg').read_text(encoding='utf-8'))
        words=[str(e.text).strip() for e in svg.iter() if e.tag.rsplit('}',1)[-1] in ('text','tspan') and e.text and e.text.strip()]
        tables=[{'title':f"그림 {n} · {t['title']} {i+1}",'columns':t['headers'],'rows':[[None if v is None else str(v) for v in row] for row in t['rows']]} for i,t in enumerate(item['source_tables'])]
        visuals.append(dict(id=name,number=n,title=item['title'],subtitle=item['subtitle'],lessonIds=item['lesson_ids'],pngAsset=f'course-visuals/{name}.png',svgAsset=f'course-visuals/{name}.svg',width=2400,height=1500,alt=item['alt'],easy=guide['easy'],readingSteps=guide['readingSteps'],resultReason=guide['resultReason'],labels=guide['labels'],dataNotes=guide['dataNotes'],warnings=list(dict.fromkeys([item['warning']]+guide['warnings'])),memory=item['memory'],sourceIds=item['sources'],tables=tables,transcript='\n'.join(words),correction=correction))
    if args.pilot:
        guides=[dict(lessonId=lid,classification='그림 안내 추가',reason='시범 강의: 새 그림의 독립 데이터와 기존 SQL 예제의 전환 확인',exampleReadingGuide=by_number[n]['dataNotes']) for n,lid in [(11,'2-1-04'),(14,'2-1-23'),(18,'2-1-20')]]
    else:
        entries=read(ROOT/'evidence/visuals-lesson-review.json')['lessons']
        keys=['lessonId','classification','reason','easySupplement','exampleReadingGuide','syntaxCaution','unlinkedReason']
        guides=[{k:x.get(k,'') for k in keys} for x in entries]
    source=read(INPUT/'data/sources.json')
    pack=dict(schemaVersion=1,version='2026.09.29.pilot' if args.pilot else '2026.09.29.1',provenance='사용자 제공 핵심 그림 27장 · 가상 학습 데이터 · 기존 SQL 예제와 별도 자료. 독립 AI 대조이며 사람 전문가 검수·학습효과 검증은 하지 않았습니다.',sources=[dict(id=k,**v) for k,v in source.items()],visuals=visuals,guides=guides)
    target.write_text(json.dumps(pack,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Imported reviewed figures:',len(visuals),'lesson guides:',len(guides))
if __name__=='__main__':main()
