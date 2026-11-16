"""S Pen button emulator checks. Keep learner payloads outside distributable evidence."""
import argparse, datetime, hashlib, io, json, pathlib, re, sqlite3, subprocess, tarfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/spen-button-20261018'
PRIVATE=ROOT/'private_evidence/spen-button-20261018'
ADB=['C:/Android/Sdk/platform-tools/adb.exe','-P','5045','-s','127.0.0.1:5591']

def adb(*args):
    return subprocess.run(ADB+list(args),capture_output=True,check=True).stdout

def text(*args):return adb(*args).decode('utf-8',errors='replace').strip()

def assert_target():
    assert text('shell','getprop','ro.kernel.qemu')=='1'
    assert text('shell','getprop','ro.boot.qemu.avd_name')=='SQLNote_QA'

def snapshot(label):
    destination=PRIVATE/label
    if label == 'before' and destination.exists():
        raise RuntimeError('The before baseline already exists; it must not be overwritten.')
    destination.mkdir(parents=True,exist_ok=True)
    adb('shell','am','force-stop','kr.sqld.study')
    payload=adb('exec-out','run-as','kr.sqld.study','tar','-c','databases')
    (destination/'database.tar').write_bytes(payload)
    archive_info = {'capturedAt': datetime.datetime.now().astimezone().isoformat(), 'databaseTarSha256': hashlib.sha256(payload).hexdigest(), 'databaseTarBytes': len(payload), 'serial': '127.0.0.1:5591', 'avd': 'SQLNote_QA', 'appLaunchedByCapture': False}
    (OUT/f'database-{label}-archive.json').write_text(json.dumps(archive_info,indent=2),encoding='utf-8')
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:archive.extractall(destination,filter='data')
    with sqlite3.connect(destination/'databases/sqlnote.db') as db:
        state=json.loads(db.execute('SELECT payload FROM study_state WHERE id=1').fetchone()[0])
        # Match JSON's array representation in the saved baseline, not tuple vs list types.
        submissions=[list(row) for row in db.execute('SELECT * FROM grading_submissions ORDER BY id').fetchall()]
        recoveries=[list(row) for row in db.execute('SELECT * FROM recovery_points ORDER BY id').fetchall()]
    data={'state':state,'submissionRows':submissions,'recoveryRows':recoveries}
    (destination/'snapshot.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    return data

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['before','after','profile','test','restore']);p.add_argument('--profile',default='tablet',choices=['tablet','tablet-portrait','phone','phone200','desktop','short']);p.add_argument('--classes',default='kr.sqld.study.StylusButtonTest');a=p.parse_args()
    assert_target();OUT.mkdir(parents=True,exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True)
    if a.action=='before':
        state = snapshot('before')
        environment={'size':text('shell','wm','size'),'density':text('shell','wm','density'),'font':text('shell','settings','get','system','font_scale'),
          'animations':{k:text('shell','settings','get','global',k) for k in ['window_animation_scale','transition_animation_scale','animator_duration_scale']}}
        (OUT/'environment-before.json').write_text(json.dumps(environment,indent=2),encoding='utf-8')
        baseline = {'counts': {k: len(state['state'].get(k, [])) for k in ['sessions','submissions','bookmarks','annotations','notes','courseProgress','inkDocuments']}, 'submissionRowCount': len(state['submissionRows']), 'recoveryRowCount': len(state['recoveryRows']), 'appLaunchedByCapture': False}
        (OUT/'database-before-summary.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
        print('Private DB backup and display settings saved.')
        print(json.dumps(baseline))
    elif a.action=='after':
        current=snapshot('after');before=json.loads((PRIVATE/'before/snapshot.json').read_text(encoding='utf-8'))
        report={'allStoredFieldsEqual':current==before,'changedStateFields':[k for k in current['state'].keys()|before['state'].keys() if current['state'].get(k)!=before['state'].get(k)],'submissionRowsEqual':current['submissionRows']==before['submissionRows'],'recoveryRowsEqual':current['recoveryRows']==before['recoveryRows'],'submissionRowCount':len(current['submissionRows']),'recoveryRowCount':len(current['recoveryRows']),'counts':{k:len(current['state'].get(k,[])) for k in ['sessions','submissions','bookmarks','annotations','notes','courseProgress','inkDocuments']}}
        (OUT/'record-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report));assert report['allStoredFieldsEqual']
    elif a.action=='profile':
        size,density,font={'tablet':('2560x1600','320','1.0'),'tablet-portrait':('1600x2560','320','1.0'),'phone':('720x1600','320','1.0'),'phone200':('720x1600','320','2.0'),'desktop':('1920x1080','160','1.0'),'short':('1280x720','320','1.0')}[a.profile]
        adb('shell','wm','size',size);adb('shell','wm','density',density);adb('shell','settings','put','system','font_scale',font)
        for key in ['window_animation_scale','transition_animation_scale','animator_duration_scale']:adb('shell','settings','put','global',key,'0')
        folder=OUT/a.profile;folder.mkdir(exist_ok=True)
        (folder/'environment.json').write_text(json.dumps({'emulator':'SQLNote_QA API34','pixels':size,'densityDpi':int(density),'fontScale':float(font)},indent=2),encoding='utf-8')
        print(a.profile,size,density,font)
    elif a.action=='test':
        folder=OUT/a.profile;folder.mkdir(exist_ok=True)
        # Remove only this task's named screenshot cache, so a failed test cannot hand off an old PNG.
        for name in text('shell','run-as','kr.sqld.study','ls','cache').splitlines():
            if re.fullmatch(r'flow-[a-z0-9-]+\.(png|json)',name):adb('shell','run-as','kr.sqld.study','rm','cache/'+name)
        command=ADB+['shell','am','instrument','-w','-r']+([] if a.classes=='all' else ['-e','class',a.classes])+['kr.sqld.study.test/androidx.test.runner.AndroidJUnitRunner']
        with (folder/'instrumentation.log').open('wb') as log:
            process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            for line in process.stdout:log.write(line);log.flush()
            process.wait()
        result=(folder/'instrumentation.log').read_bytes()
        print(result.decode('utf-8',errors='replace')[-7000:])
        filenames=text('shell','run-as','kr.sqld.study','ls','cache').splitlines()
        for name in filenames:
            if re.fullmatch(r'flow-[a-z0-9-]+\.png',name):
                png=adb('exec-out','run-as','kr.sqld.study','cat','cache/'+name)
                assert png.startswith(b'\x89PNG\r\n\x1a\n'),name
                (folder/name).write_bytes(png)
            elif re.fullmatch(r'flow-[a-z0-9-]+\.json',name):
                (folder/name).write_bytes(adb('exec-out','run-as','kr.sqld.study','cat','cache/'+name))
        assert process.returncode==0 and b'OK (' in result,'Instrumentation did not pass; see the preserved log.'
    elif a.action=='restore':
        saved=json.loads((OUT/'environment-before.json').read_text())
        for key in ['size','density']:
            value=saved[key].split('Override '+key+': ')[-1] if 'Override '+key+':' in saved[key] else 'reset'
            adb('shell','wm',key,value.strip())
        if saved['font']=='null':adb('shell','settings','delete','system','font_scale')
        else:adb('shell','settings','put','system','font_scale',saved['font'])
        for key,value in saved['animations'].items():
            if value=='null':adb('shell','settings','delete','global',key)
            else:adb('shell','settings','put','global',key,value)
        print('Display settings restored.')

if __name__=='__main__':main()
