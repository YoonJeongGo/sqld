"""Validate the authored visual pack, its native assets and stable course references.

This checks structure/source identity, not teaching effectiveness or SQL correctness.
"""
import argparse,hashlib,json,re,shutil,struct,zlib,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def require(ok,message):
    if not ok:raise ValueError(message)
def unique(values,label):require(len(values)==len(set(values)),f'Duplicate {label}')
def png_size(path):
    data=path.read_bytes();require(data[:8]==b'\x89PNG\r\n\x1a\n','Invalid PNG signature')
    pos=8;compressed=[];header=None;end=False
    while pos<len(data):
        length=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];payload=data[pos+8:pos+8+length]
        crc=struct.unpack('>I',data[pos+8+length:pos+12+length])[0]
        require(zlib.crc32(kind+payload)&0xffffffff==crc,'Corrupt PNG chunk')
        if kind==b'IHDR':header=struct.unpack('>IIBBBBB',payload)
        if kind==b'IDAT':compressed.append(payload)
        if kind==b'IEND':end=True
        pos+=length+12
    require(header is not None and end and pos==len(data),'Incomplete PNG')
    width,height,depth,color,compression,filter_method,interlace=header
    require(depth==8 and color in (2,6) and interlace==0,'Unexpected authored PNG format')
    decoded=zlib.decompress(b''.join(compressed));stride=width*(3 if color==2 else 4)+1
    require(len(decoded)==height*stride and all(decoded[i*stride]<=4 for i in range(height)),'PNG scanline mismatch')
    return width,height

def svg_text(path):
    svg=ET.fromstring(path.read_text(encoding='utf-8'))
    require(svg.tag=='{http://www.w3.org/2000/svg}svg','Invalid SVG root')
    box=list(map(float,svg.attrib['viewBox'].split()));require(box[2]*5==box[3]*8,'SVG aspect ratio')
    allowed={'svg','title','desc','rect','text','tspan','path','line','polyline','polygon','circle','ellipse','g','defs','marker'}
    for element in svg.iter():
        require(element.tag.rsplit('}',1)[-1] in allowed,'Unexpected SVG element')
        for key,value in element.attrib.items():
            key=key.rsplit('}',1)[-1].lower()
            require(not key.startswith('on') and key not in ('href','src','style'),'Unsafe SVG attribute')
            require('javascript:' not in value.lower(),'Unsafe SVG URL')
            require(all(re.fullmatch(r'#[\w-]+',u) for u in re.findall(r'url\((.*?)\)',value)),'External SVG URL')
    return '\n'.join(str(e.text).strip() for e in svg.iter() if e.tag.rsplit('}',1)[-1] in ('text','tspan') and e.text and e.text.strip())

def validate(pack,course,asset_root,pilot=False):
    require(set(pack)=={'schemaVersion','version','provenance','sources','visuals','guides'},'Visual pack fields')
    require(pack['schemaVersion']==1,'Visual schema')
    visuals=pack['visuals'];guides=pack['guides'];ids={l['id'] for l in course['lessons']}
    mapping={v['number']:v['lesson_ids'] for v in read(ROOT/'content/visual-source/manifest.json')}
    expected={11,14,18} if pilot else set(range(1,28))
    require({v['number'] for v in visuals}==expected and len(visuals)==len(expected),'Expected complete visual set')
    unique([v['id'] for v in visuals],'visual IDs');unique([g['lessonId'] for g in guides],'lesson guides')
    unique([s['id'] for s in pack['sources']],'source IDs');sources={s['id'] for s in pack['sources']}
    for source in pack['sources']:require(source['title'] and re.fullmatch(r'https://[^\s]+',source['url']),'Invalid source')
    linked=set();files=[]
    for v in visuals:
        number=v['number'];require(v['id']==f'visual-{number:02}','Unstable visual ID')
        require(v['lessonIds']==mapping[number],'Visual placement differs from supplied manifest')
        require(v['lessonIds'] and set(v['lessonIds'])<=ids,'Unknown lesson');unique(v['lessonIds'],'visual placement')
        linked.update(v['lessonIds'])
        for k in ['title','subtitle','alt','easy','resultReason','dataNotes','memory','transcript']:
            require(isinstance(v[k],str) and v[k].strip(),f'Empty {v["id"]}.{k}')
        require(len(v['readingSteps'])>=3 and all(x.strip() for x in v['readingSteps']),'Missing concrete reading guide')
        require(v['sourceIds'] and set(v['sourceIds'])<=sources,'Unknown source')
        for label in v['labels']:require(set(label)=={'label','meaning'} and all(label.values()),'Missing text label')
        for table in v['tables']:
            require(set(table)=={'title','columns','rows'} and table['columns'],'Visual table fields')
            require(all(len(row)==len(table['columns']) and all(x is None or isinstance(x,str) for x in row) for row in table['rows']),'Visual table cells')
        for kind in ['png','svg']:
            name=v[kind+'Asset'];require(name==f'course-visuals/visual-{number:02}.{kind}','Unsafe/unexpected asset path')
            path=asset_root/name;require(path.is_file(),'Missing '+name)
            if kind=='png':require(png_size(path)==(v['width'],v['height'])==(2400,1500),'PNG ratio or dimensions')
            else:require(svg_text(path)==v['transcript'],'SVG transcription drift')
            files.append({'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for g in guides:
        require(g['lessonId'] in ids and g['classification'] in ('유지','설명 보완','설명보완','오류 수정','오류수정','그림 안내 추가','그림안내추가'),'Lesson review classification')
        require(g['reason'].strip(),'Missing lesson review rationale')
        if g['lessonId'] not in linked:require(g.get('unlinkedReason','').strip(),'Missing no-image rationale')
    if not pilot:
        require({g['lessonId'] for g in guides}==ids,'All 63 lesson reviews required')
        require(len(linked)==40 and len(ids-linked)==23,'Manifest coverage changed')
    return {'visuals':len(visuals),'connections':sum(len(v['lessonIds']) for v in visuals),'linkedLessons':len(linked),'unlinkedLessons':sorted(ids-linked),'lessonGuides':len(guides),'files':files}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--sync-assets',action='store_true');args=parser.parse_args()
    source=ROOT/'content/course-visuals.json';pack=read(source);course=read(ROOT/'content/course-pack.json')
    result=validate(pack,course,ROOT/'content',args.pilot)
    assets=ROOT/'app/src/main/assets'
    if args.sync_assets:
        for f in result['files']:
            dest=assets/f['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'content'/f['path'],dest)
        (assets/'course-visuals.json').write_bytes(source.read_bytes())
    require((assets/'course-visuals.json').read_bytes()==source.read_bytes(),'Visual source/asset mismatch')
    for f in result['files']:require(hashlib.sha256((assets/f['path']).read_bytes()).hexdigest()==f['sha256'],'Image asset drift')
    result.update(status='pass',pilot=args.pilot,packSha256=hashlib.sha256(source.read_bytes()).hexdigest())
    output=ROOT/('evidence/visuals-pilot-validation.json' if args.pilot else 'evidence/visuals-validation.json')
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['files','unlinkedLessons']},ensure_ascii=False))
if __name__=='__main__':main()
