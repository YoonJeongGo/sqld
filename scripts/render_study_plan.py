"""Render the validated dated plan as a readable PDF, HTML, and Markdown."""
import json
import html
from pathlib import Path
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
PLAN=json.loads((ROOT/'content/study-plan.json').read_text(encoding='utf-8'))
OUT=ROOT/'output/study-plan'; OUT.mkdir(parents=True,exist_ok=True)
PDFOUT=ROOT/'output/pdf';PDFOUT.mkdir(parents=True,exist_ok=True)
days=[d for d in PLAN['days'] if d['studyDay']]
pdfmetrics.registerFont(TTFont('Malgun','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBold','C:/Windows/Fonts/malgunbd.ttf'))
BG='#F6F3EB';INK='#142B43';TEAL='#007D7A';MUTED='#536574';CORAL='#C75B4B';LINE='#D9E3DF'
W,H=842,595
pdf=PDFOUT/'SQLD_40일_전체학습계획_5시간_6시간.pdf'
c=canvas.Canvas(str(pdf),pagesize=(W,H))
c.setTitle('SQLD 40일 전체 학습 계획 - 5시간 기본 / 6시간 확장')
c.setAuthor('Personal study plan')
styles={
 'title':ParagraphStyle('title',fontName='MalgunBold',fontSize=18,leading=25,textColor=HexColor(INK),wordWrap='CJK'),
 'head':ParagraphStyle('head',fontName='MalgunBold',fontSize=11,leading=15,textColor=HexColor(TEAL),wordWrap='CJK'),
 'body':ParagraphStyle('body',fontName='Malgun',fontSize=10.2,leading=14.5,textColor=HexColor(INK),wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='Malgun',fontSize=9.2,leading=13,textColor=HexColor(MUTED),wordWrap='CJK'),
}

def para(text,x,y,w,style='body'):
    p=Paragraph(html.escape(text).replace('\n','<br/>'),styles[style]);_,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return y-h

def base(page,label):
    c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(INK));c.setFont('MalgunBold',10);c.drawString(30,H-24,'SQLD / 매일 쌓는 복습')
    c.setFillColor(HexColor(MUTED));c.setFont('Malgun',8);c.drawRightString(W-30,H-24,label)
    c.setStrokeColor(HexColor(LINE));c.line(30,30,W-30,30)
    c.setFont('Malgun',7.5);c.drawString(30,17,'2026.10.05 - 11.13 | 주말 및 10/8·9 휴식 | 휴식·식사는 순공부 시간과 별도')
    c.drawRightString(W-30,17,f'{page:02} / 17')

def heading(text,x,y,w):
    y-=8;y=para(text,x,y,w,'head');return y-5

def compact_ids(items):
    result=[]
    for prefix in dict.fromkeys(x.rsplit('-',1)[0] for x in items):
        nums=[int(x.rsplit('-',1)[1]) for x in items if x.rsplit('-',1)[0]==prefix]
        result.append(prefix+' '+(','.join(f'{n:02}' for n in nums) if len(nums)<3 else f'{min(nums):02}~{max(nums):02}'))
    return ' / '.join(result)

base(1,'PLAN OVERVIEW')
y=para('40일의 방향을 한 장에\n강의로 이해하고, PDF로 풀고, 앱으로 떠올리기',38,535,760,'title')
y=para('28공부일  ·  104강  ·  교재 5권 324쪽  ·  앱은 매일 복습용',38,y-20,760,'head')
for i,(label,value,sub) in enumerate([('5시간 기본','140시간','직접 풀이·복습 81시간 19분'),('6시간 확장','168시간','같은 진도 + 약점 보완 28시간'),('강의 전체','58시간 41분','104강을 1배속으로 시청')]):
    x=38+i*257;c.setFillColor(HexColor('#FFFFFF'));c.roundRect(x,325,242,104,12,fill=1,stroke=0)
    para(label,x+16,412,210,'head');para(value,x+16,386,210,'title');para(sub,x+16,347,210,'small')
y=heading('진도 흐름',38,302,760)
for t in ['10/5~10/28  이론 63강 + 정규식 특강 / PDF 전체 범위 첫 학습','10/29~11/5  개념완성 25강 / 미풀이·약점 회수','11/6~11/12  모의고사 5회와 해설 15강 / 오답 보완','11/13  밀린 분량·반복 오답·준비물 정리']:
    y=para(t,42,y,750)-10
y=para('이번 주 10/8·9와 모든 주말은 쉬는 날이다. 11/14는 사용자가 정한 시험 목표일이다. 현재 접수 내역의 시험일·장소·입실 시간을 따로 확인한다. 합격 보장이나 공식 일정 확인 완료를 뜻하지 않는다.',38,y-4,750,'small')
assert y>40
c.showPage()

for spread in range(14):
    base(spread+2,'DAILY PLAN / 기본 300분 + 선택 60분')
    for side in range(2):
        d=days[spread*2+side];x=30+side*397;w=365;y=544
        weekday='월화수목금토일'[date.fromisoformat(d['date']).weekday()]
        y=para(f'D{d["studyDay"]:02}  {d["date"][5:].replace("-",".")} ({weekday})',x,y,w,'head')-6
        display_titles={5:'SELECT·WHERE 기본\nUPDATE·DELETE·MERGE',6:'WHERE 확장·정렬·DISTINCT\n단일행 함수',9:'INNER·OUTER·CROSS\nSELF·ANSI JOIN',10:'서브쿼리 기본·단일행\n다중행·다중컬럼',12:'ROLLUP·CUBE\nGROUPING SETS·GROUPING',13:'OVER·순위·집계\n기타 윈도우 함수'}
        y=para(display_titles.get(d['studyDay'],d['title']),x,y,w,'title')-7
        y=para(d['phase'],x,y,w,'small')
        y=heading('오늘 들을 강의',x,y,w)
        if d['lectures']:
            for l in d['lectures']:
                y=para(f'{l["title"]} · {l["minutes"]}분',x,y,w,'small')-2
        else:y=para('새 강의 없음. 밀린 강의 또는 반복 오답을 정리한다.',x,y,w,'small')
        y=heading('PDF / 파일 쪽수 기준',x,y,w)
        for r in d['pdfs']:
            y=para(f'{r["sectionId"]}  {r["fromPage"]}~{r["toPage"]}쪽',x,y,w,'body')-1
        if d['studyDay']>=17:y=para('위 범위는 약점 참고용. 전체 재독이나 해당 문제풀이 회차의 출제 범위를 뜻하지 않는다.',x,y-2,w,'small')
        y=heading('5시간 기본 배분',x,y,w)
        for b in d['blocks']:
            y=para(f'{b["title"]}  {b["minutes"]}분',x,y,w,'body')-1
        y=heading('앱 복습 연결',x,y,w)
        y=para(compact_ids(d['lessonIds']),x,y,w,'small')-3
        y=para('개념 가리기 → 이유 설명 → 일반 연습 → 오답 표시',x,y,w,'small')
        y=heading('6시간이면 +60분',x,y,w)
        y=para(' / '.join(f'{b["title"]} {b["minutes"]}분' for b in d['extension']),x,y,w,'small')
        assert y>39,(d['date'],y)
    c.showPage()

base(16,'HOW TO STUDY')
y=para('시간을 채우는 것보다\n오늘 배운 규칙을 다시 꺼내기',38,535,760,'title')
sections=[
 ('강의·PDF·앱의 역할','강의는 처음 이해하는 곳, PDF는 해설 없이 직접 푸는 곳, 앱은 설명을 가리고 회상하고 연습하는 곳이다. 앱 노트 읽음을 실제 영상 시청 또는 PDF 풀이 완료로 취급하지 않는다.'),
 ('앱에서 사용하는 순서','홈의 학습 계획 → 날짜 → 5시간/6시간 선택 → 강의·PDF 계획 확인 → 오늘 범위 복습. 정답 번호 대신 왜 다른 보기가 틀린지 설명한다. 앱의 예약 모의고사는 일반 복습에 포함하지 않는다.'),
 ('문제풀이 자료가 없을 때','3-1 회차별 문제와 3-2 모의고사 원문은 첨부한 5개 이론 PDF만으로 확인할 수 없다. 강의 첨부 원문이 있으면 먼저 풀고 강의로 검토한다. 없으면 PDF 오답 또는 앱의 미열람 모의로 대체하고, 그 자료 자체의 해설로 별도 채점한다. 강의는 다른 예제 학습이며 점수를 섞지 않는다.'),
 ('밀린 날 처리','이론에서 못 푼 문제를 표시해 문제풀이 주간에 회수한다. 6시간 선택일의 추가 시간이나 11/13의 120분을 사용한다. 11/6·11/9처럼 해설이 긴 날은 오답 분석을 끝내지 못할 수 있으므로 남은 문항 목록을 남긴다. 휴일에는 자동으로 과제를 추가하지 않는다.'),
 ('준비 상태 확인','처음 보는 모의 3회에서 75~80점 이상, 반복 오답 감소, 풀이 이유 설명을 개인 점검 목표로 삼는다. 이미 본 문제의 높은 점수를 새 문제 대응력으로 계산하지 않는다. 이 목표는 합격 보장이나 공식 합격 기준이 아니다.')]
for title,body in sections:
    y=heading(title,38,y-6,755);y=para(body,38,y,755)-5
assert y>38,y
c.showPage()
base(17,'SOURCE & CHECK')
y=para('교재를 읽을 때 지킬 기준',38,535,755,'title')
for title,body in [
 ('쪽수가 겹치는 이유','한 PDF 쪽에 앞 단원의 문제와 다음 단원의 제목이 같이 있는 경우가 있다. 이전 단원은 다음 소제목 직전까지, 다음 단원은 그 소제목부터 읽는다. 단일행 함수 13·14강은 SQL 기본 60~71쪽, NULL 15·16강은 72~82쪽을 공유한다.'),
 ('앱에 부족한 조건은 PDF에서 확인','CHECK 표현 제한, INSERT ALL, 날짜 ROUND, SQL Server TOP, 부분 ROLLUP, LEVEL 행 생성, 정규식 POSIX·이스케이프, 뷰 표현식 별칭·OR REPLACE, ROLE 구문을 해당 날에 확인한다. 모든 항목의 출제 비중이 같다는 뜻은 아니다.'),
 ('정답 충돌은 별도 표시','SQL 기본 121·123쪽 조인 해설, SQL 활용 45쪽 UNION 순서 및 46~48쪽 ROLLUP 표 등 기존 감사에서 발견한 충돌은 정답 암기 대상으로 삼지 않는다. 이번 계획은 모든 교재 문제의 정답을 검증한 결과가 아니다.'),
 ('자료 기준','사용자가 제공한 104강 제목·분량, 5개 PDF의 324쪽, 현재 SQL 노트의 63강·노트·일반 연습 연결을 사용했다. 앞서 언급한 별도 파이널 10회/30강은 이번 104강 목록에 없으므로 기본 계획에 포함하지 않았다.'),
 ('보존과 실행','기존 노트·예제·문제·정답·진도·오답·메모는 유지한다. 학습 계획 화면은 별도 일정 안내이며 새 학습 완료 기록을 임의로 만들지 않는다. 사용자가 가진 PDF와 강의는 원래 자료에서 열어 공부한다.')]:
    y=heading(title,38,y-8,755);y=para(body,38,y,755)-4
assert y>38,y
c.save()

css='''body{margin:0;background:#f6f3eb;color:#142b43;font:16px/1.65 "Malgun Gothic",sans-serif}main{max-width:1150px;margin:auto;padding:32px}h1{font-size:36px;line-height:1.3}h2{font-size:22px;color:#007d7a}a{color:#007d7a}.banner,.day{background:white;border:1px solid #d9e3df;border-radius:18px;padding:24px;margin:18px 0}.meta{color:#536574}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.day h3{font-size:22px;margin:0 0 12px}.tag{color:#007d7a;font-weight:700}.extra{background:#edf6f0;padding:14px;border-radius:12px}ul{padding-left:22px}nav{display:flex;flex-wrap:wrap;gap:12px}details{margin:12px 0}table{border-collapse:collapse;width:100%}th,td{padding:9px;border-bottom:1px solid #d9e3df;text-align:left}button{padding:12px 20px;border-radius:24px;border:0;background:#007d7a;color:white;font:inherit;cursor:pointer}@media(max-width:800px){.grid{grid-template-columns:1fr}main{padding:16px}h1{font-size:28px}}@media print{button,nav{display:none}.day{break-inside:avoid}}'''
parts=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SQLD 전체 학습 계획</title><style>'+css+'</style><main><h1>SQLD 40일<br>매일 쌓는 복습</h1><div class="banner"><b>2026.10.05 - 11.13 · 28공부일</b><p>5시간 기본 140시간 / 6시간 확장 168시간<br>104강 영상 58시간 41분 + PDF 직접 풀이 + 앱 복습</p><p>주말과 10/8·9 휴식. 6시간은 기본 진도에 약점 보완 60분을 더합니다.</p><button onclick="window.print()">인쇄 / PDF 저장</button></div><nav>']
parts += [f'<a href="#day{d["studyDay"]}">{d["date"][5:]}</a>' for d in days]
parts += ['</nav><div class="grid">']
for d in days:
    e=html.escape
    parts.append(f'<article class="day" id="day{d["studyDay"]}"><div class="tag">D{d["studyDay"]:02} · {d["date"]}</div><h3>{e(d["title"])}</h3><div class="meta">{e(d["phase"])}</div><h2>강의</h2><ul>')
    parts += [f'<li>{e(l["title"])} · {l["minutes"]}분</li>' for l in d['lectures']]
    if not d['lectures']:parts.append('<li>새 강의 없음</li>')
    parts.append('</ul><h2>PDF</h2><ul>')
    parts += [f'<li>{e(r["title"])} · {r["fromPage"]}~{r["toPage"]}쪽<br><span class="meta">{e(" / ".join(r["focus"]))}</span></li>' for r in d['pdfs']]
    parts.append('</ul><h2>5시간 기본</h2>')
    parts += [f'<details><summary>{e(b["title"])} · {b["minutes"]}분</summary><p>{e(b["detail"])}</p></details>' for b in d['blocks']]
    parts.append(f'<h2>앱 복습</h2><p>{e(compact_ids(d["lessonIds"]))}</p><div class="extra"><b>6시간이면 +60분</b>')
    parts += [f'<details><summary>{e(b["title"])} · {b["minutes"]}분</summary><p>{e(b["detail"])}</p></details>' for b in d['extension']]
    parts.append('</div></article>')
parts.append('</div><div class="banner"><h2>사용 안내</h2><ul>')
parts += [f'<li>{html.escape(n)}</li>' for n in PLAN['notes']]
parts.append('</ul></div></main></html>')
(OUT/'전체계획표.html').write_text(''.join(parts),encoding='utf-8')

md=['# SQLD 40일 전체 학습 계획','', '기간: 2026-10-05~11-13. 주말 및 10/8·9 휴식. 28일 × 5시간=140시간 / 6시간=168시간. 영상 총 58시간 41분.','', '| 날짜 | 강의·오늘 주제 | 영상 | PDF 범위 |','|---|---|---:|---|']
for d in days:
    refs=' / '.join(f'{r["sectionId"]} {r["fromPage"]}~{r["toPage"]}쪽' for r in d['pdfs'])
    md.append(f'| {d["date"]} | {d["title"]} | {sum(l["minutes"] for l in d["lectures"])}분 | {refs} |')
md+=['','## 사용 안내','']+['- '+n for n in PLAN['notes']]
for d in days:
    md+=['',f'## {d["date"]} · {d["title"]}','']
    md += [f'- {b["title"]} {b["minutes"]}분: {b["detail"]}' for b in d['blocks']]
    md+=['','추가 60분:']+[f'- {b["title"]} {b["minutes"]}분: {b["detail"]}' for b in d['extension']]
(OUT/'전체계획표.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(pdf)
print(OUT/'전체계획표.html')
