"""ADB helpers restricted to the explicitly selected emulator; no physical-device mutations."""
import argparse, json, pathlib, re, subprocess, time, datetime, os, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = pathlib.Path.home() / 'AppData/Local/Android/Sdk/platform-tools/adb.exe'
DEVICE = os.environ.get('SQLNOTE_ADB_DEVICE','emulator-5590')
SERVER_PORT = os.environ.get('SQLNOTE_ADB_PORT','5037')
OUT = ROOT / 'evidence'

def adb(*args, binary=False):
    result = subprocess.run([str(ADB), '-P', SERVER_PORT, '-s', DEVICE, *map(str, args)], capture_output=True, check=True)
    return result.stdout if binary else result.stdout.decode('utf-8', errors='replace').strip()

def assert_emulator():
    if adb('shell', 'getprop', 'ro.kernel.qemu') != '1':
        raise RuntimeError('Refusing to mutate a non-emulator device')
    if adb('shell','getprop','ro.boot.qemu.avd_name') != 'SQLNote_QA':
        raise RuntimeError('Refusing to mutate an emulator outside the SQLD project')

def dump():
    # ADB can exit 0 even when UIAutomator fails to reach idle. Never reuse stale XML.
    for attempt in range(3):
        result=adb('shell','uiautomator','dump','/sdcard/sqlnote-qa.xml')
        if 'dumped to' in result.lower() and 'error' not in result.lower():
            raw=adb('shell','cat','/sdcard/sqlnote-qa.xml')
            return raw, ET.fromstring(raw)
        if attempt<2:time.sleep(1)
    raise RuntimeError(f'Fresh UI hierarchy unavailable: {result}')

def capture(name):
    raw, tree = dump()
    (OUT/f'{name}.xml').write_text(raw,encoding='utf-8')
    (OUT/f'{name}.png').write_bytes(adb('exec-out','screencap','-p',binary=True))
    nodes=[{'text':n.get('text'),'description':n.get('content-desc'),'clickable':n.get('clickable'),'bounds':n.get('bounds')} for n in tree.iter('node') if n.get('text') or n.get('content-desc')]
    (OUT/f'{name}-nodes.json').write_text(json.dumps(nodes,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/f'{name}-environment.json').write_text(json.dumps({'device':DEVICE,'avd':'SQLNote_QA','capturedAt':datetime.datetime.now().astimezone().isoformat(),'size':adb('shell','wm','size'),'density':adb('shell','wm','density'),'fontScale':adb('shell','settings','get','system','font_scale')},indent=2),encoding='utf-8')
    print(json.dumps({'image':str(OUT/f'{name}.png'),'nodes':nodes},ensure_ascii=False))

def tap(label):
    _,tree=dump()
    matches=[n for n in tree.iter('node') if n.get('text')==label or n.get('content-desc')==label]
    parents={child:parent for parent in tree.iter() for child in parent}
    targets=[]
    for node in matches:
        target=node
        while target.get('clickable')!='true' and target in parents:target=parents[target]
        if target.get('clickable')!='true':target=node
        if target not in targets:targets.append(target)
    matches=[n for n in targets if n.get('clickable')=='true']
    if len(matches)!=1: raise RuntimeError(f'Expected exactly one observed node for {label!r}, got {len(matches)}')
    x1,y1,x2,y2=map(int,re.findall(r'\d+',matches[0].get('bounds')))
    adb('shell','input','tap',(x1+x2)//2,(y1+y2)//2)
    print(f'Tapped observed {label}')

def scroll_to(label):
    for _ in range(18):
        _,tree=dump()
        parents={child:parent for parent in tree.iter() for child in parent}
        found=False
        for n in tree.iter('node'):
            if n.get('text')!=label and n.get('content-desc')!=label:continue
            while n.get('clickable')!='true' and n in parents:n=parents[n]
            if n.get('clickable')=='true':found=True
        if found:
            print(f'Observed {label}');return
        dimensions=re.findall(r'(\d+)x(\d+)',adb('shell','wm','size'))[-1]
        width,height=map(int,dimensions)
        regions=[]
        for n in tree.iter('node'):
            if n.get('scrollable')!='true':continue
            values=re.findall(r'\d+',n.get('bounds',''))
            if len(values)!=4:continue
            left,top,right,bottom=map(int,values)
            if bottom-top>100 and right-left>100:regions.append((left,top,right,bottom))
        if regions:
            left,top,right,bottom=max(regions,key=lambda b:(b[2]-b[0])*(b[3]-b[1]))
            x=(left+right)//2
            adb('shell','input','swipe',x,int(top+(bottom-top)*.8),x,int(top+(bottom-top)*.2),350)
        else:
            adb('shell','input','swipe',width//2,int(height*.7),width//2,int(height*.28),350)
    raise RuntimeError(f'Not found after bounded scrolling: {label}')

def baseline_path():
    # Network ADB targets contain a colon, which is not valid in Windows filenames.
    device_name=re.sub(r'[^A-Za-z0-9._-]','_',DEVICE)
    return OUT/f'emulator-baseline-{device_name}.json'

def baseline():
    path=baseline_path()
    if not path.exists():
        state={'size':adb('shell','wm','size'),'density':adb('shell','wm','density'),'fontScale':adb('shell','settings','get','system','font_scale'),'night':adb('shell','cmd','uimode','night')}
        path.write_text(json.dumps(state,indent=2),encoding='utf-8')

def restore():
    state=json.loads(baseline_path().read_text(encoding='utf-8'))
    size=re.search(r'Override size: (\d+x\d+)',state['size'])
    density=re.search(r'Override density: (\d+)',state['density'])
    adb('shell','wm','size',size.group(1) if size else 'reset')
    adb('shell','wm','density',density.group(1) if density else 'reset')
    adb('shell','settings','put','system','font_scale',state['fontScale'])
    night='yes' if 'yes' in state['night'] else 'auto' if 'auto' in state['night'] else 'no'
    adb('shell','cmd','uimode','night',night)
    print('Restored observed emulator display preferences')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['capture','tap','scroll-to','window','restore','baseline']);parser.add_argument('value',nargs='?');parser.add_argument('--density',default='320');parser.add_argument('--font',default='1.0');parser.add_argument('--night',default='no')
    args=parser.parse_args();assert_emulator();OUT.mkdir(exist_ok=True)
    if args.action=='capture':capture(args.value)
    elif args.action=='tap':tap(args.value)
    elif args.action=='scroll-to':scroll_to(args.value)
    elif args.action=='baseline':baseline()
    elif args.action=='restore':restore()
    elif args.action=='window':
        baseline();adb('shell','wm','size',args.value);adb('shell','wm','density',args.density);adb('shell','settings','put','system','font_scale',args.font);adb('shell','cmd','uimode','night',args.night);print('Applied emulator window configuration')
