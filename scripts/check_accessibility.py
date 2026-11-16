"""Deterministic palette ratios + observed Android semantics target dimensions.
Does not claim TalkBack, font rendering, or complete WCAG conformance.
"""
import json, pathlib, re, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence'
PALETTES={
    'light':{'body':('253632','F7F5EF'),'secondaryText':('505E57','F7F5EF'),'primary':('205C52','F7F5EF'),'button':('FFFFFF','205C52'),'noteAccent':('173E36','DCECE4'),'annotation':('503909','F2E7C9'),'error':('9D342A','F7F5EF'),'errorPanel':('410800','FFDAD4')},
    'dark':{'body':('E4E8DE','161F1C'),'secondaryText':('C0CCC1','161F1C'),'primary':('A5D7C3','161F1C'),'button':('0C382C','A5D7C3'),'noteAccent':('D0EDDF','284A3D'),'annotation':('FFE7AB','4D4127'),'error':('FFB4A7','161F1C'),'errorPanel':('FFDAD4','62332B')}
}
def luminance(value):
    components=[int(value[i:i+2],16)/255 for i in (0,2,4)]
    c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in components]
    return .2126*c[0]+.7152*c[1]+.0722*c[2]
def contrast(a,b):
    x,y=sorted((luminance(a),luminance(b)));return (y+.05)/(x+.05)
def inspect(path,density):
    tree=ET.parse(path); results=[]
    for node in tree.iter('node'):
        if node.get('clickable')!='true' or node.get('enabled')!='true':continue
        bounds=list(map(int,re.findall(r'-?\d+',node.get('bounds',''))))
        if len(bounds)!=4:continue
        x,y,xx,yy=bounds
        texts=[n.get('text') or n.get('content-desc') for n in node.iter() if n.get('text') or n.get('content-desc')]
        width=(xx-x)/density; height=(yy-y)/density
        results.append({'label':' / '.join(texts)[:120],'widthDp':width,'heightDp':height,'meets48':width>=48 and height>=48})
    return results
if __name__=='__main__':
    colors=[{'theme':theme,'role':name,'foreground':'#'+a,'background':'#'+b,'ratio':round(contrast(a,b),3),'passesNormalText':contrast(a,b)>=4.5} for theme,pairs in PALETTES.items() for name,(a,b) in pairs.items()]
    dimensions={}
    for name,density in [('dedicated-home',2),('dedicated-strict-ungraded',2),('dedicated-font200-question',2),('dedicated-tablet-note',1),('dedicated-tablet-sql-ungraded',1),('dedicated-tablet-sql-explanation',1),('dedicated-tablet-portrait',1),('dedicated-narrow-window',1.25),('dedicated-final-phone-question',2)]:
        path=OUT/f'{name}.xml'
        if path.exists():dimensions[name]=inspect(path,density)
    report={'paletteChecks':colors,'observedTouchTargets':dimensions,'limitations':['Palette pairs only, not every blended pixel/control state.','Nodes clipped by scrolling can have a visible fragment below 48dp; inspect screenshots.','TalkBack spoken order and external keyboard are not tested by this script.']}
    (OUT/'accessibility-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'palettePairs':len(colors),'passed':sum(x['passesNormalText'] for x in colors),'minimumContrast':min(x['ratio'] for x in colors),'captureCount':len(dimensions)},ensure_ascii=False))
    raise SystemExit(0 if all(x['passesNormalText'] for x in colors) else 1)
