"""Run isolated navigation tests on the owned API34 AVD and collect actual app-root captures."""
import argparse
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/mock-navigation-20261018'
ADB = ['C:/Android/Sdk/platform-tools/adb.exe', '-P', '5045', '-s', '127.0.0.1:5591']


def adb(*args):
    return subprocess.run(ADB + list(args), capture_output=True, check=True).stdout


def text(*args):
    return adb(*args).decode('utf-8', errors='replace').strip()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action', choices=['profile','test'])
    parser.add_argument('--profile', choices=['tablet','phone200'], default='tablet')
    parser.add_argument('--classes', default='kr.sqld.study.UnitMockFlowCaptureTest')
    args=parser.parse_args()
    assert text('shell','getprop','ro.kernel.qemu')=='1'
    assert text('shell','getprop','ro.boot.qemu.avd_name')=='SQLNote_QA'
    folder=OUT/args.profile
    folder.mkdir(parents=True,exist_ok=True)
    if args.action=='profile':
        size,density,font={'tablet':('2560x1600','320','1.0'),'phone200':('720x1600','320','2.0')}[args.profile]
        adb('shell','wm','size',size)
        adb('shell','wm','density',density)
        adb('shell','settings','put','system','font_scale',font)
        for key in ['window_animation_scale','transition_animation_scale','animator_duration_scale']:
            adb('shell','settings','put','global',key,'0')
        environment={'avd':'SQLNote_QA','androidApi':34,'pixels':size,'densityDpi':int(density),'fontScale':float(font)}
        (folder/'environment.json').write_text(json.dumps(environment,indent=2),encoding='utf-8')
        print(json.dumps(environment))
        return
    for name in text('shell','run-as','kr.sqld.study','ls','cache').splitlines():
        if re.fullmatch(r'mock-flow-[a-z0-9-]+\.(png|json)',name):
            adb('shell','run-as','kr.sqld.study','rm','cache/'+name)
    command=ADB+['shell','am','instrument','-w','-r','-e','class',args.classes,
                 'kr.sqld.study.test/androidx.test.runner.AndroidJUnitRunner']
    with (folder/'instrumentation.log').open('wb') as log:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in process.stdout:
            log.write(line)
            log.flush()
        process.wait()
    result=(folder/'instrumentation.log').read_bytes()
    print(result.decode('utf-8',errors='replace')[-6500:])
    files=[]
    for name in text('shell','run-as','kr.sqld.study','ls','cache').splitlines():
        if re.fullmatch(r'mock-flow-[a-z0-9-]+\.(png|json)',name):
            payload=adb('exec-out','run-as','kr.sqld.study','cat','cache/'+name)
            if name.endswith('.png'):assert payload.startswith(b'\x89PNG\r\n\x1a\n'),name
            (folder/name).write_bytes(payload)
            files.append(name)
    passed=re.search(rb'OK \((\d+) tests?\)',result)
    summary={'classes':args.classes,'passed':bool(passed) and process.returncode==0,
             'testCount':int(passed[1]) if passed else None,'files':files,
             'inMemoryTestDatabase':True,'physicalDeviceTested':False}
    (folder/'test-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary))
    assert summary['passed'],'Instrumentation did not pass; see retained log.'


if __name__=='__main__':main()
