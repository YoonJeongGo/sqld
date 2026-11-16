"""Capture only the SQLD QA app's committed state after stopping its own process.
Intended for synthetic QA records, never an arbitrary/physical device.
"""
import argparse,json,pathlib,sqlite3,subprocess
from device_qa import adb,assert_emulator,ROOT,DEVICE

def capture(label):
    assert_emulator()
    if not label.replace('-','').replace('_','').isalnum():raise ValueError('Simple label required')
    adb('shell','am','force-stop','kr.sqld.study')
    dest=ROOT/'evidence'/label;dest.mkdir(exist_ok=True)
    listing=adb('shell','run-as','kr.sqld.study','ls','databases').splitlines()
    for name in ('sqlnote.db','sqlnote.db-wal','sqlnote.db-shm'):
        if name in listing:(dest/name).write_bytes(adb('exec-out','run-as','kr.sqld.study','cat','databases/'+name,binary=True))
    db=sqlite3.connect((dest/'sqlnote.db').as_uri()+'?mode=ro',uri=True)
    payload=db.execute('SELECT payload FROM study_state WHERE id=1').fetchone()[0]
    state=json.loads(payload)
    (dest/'state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    session=state['sessions'][-1] if state['sessions'] else {}
    summary={'device':DEVICE,'avd':'SQLNote_QA','sessionId':session.get('id'),'mode':session.get('mode'),'current':session.get('current',0),'remainingMillis':session.get('remainingMillis'),'bootCount':session.get('bootCount'),'clockAnomaly':session.get('clockAnomaly',False),'submissions':len(state.get('submissions',[])),'drafts':[i.get('draft',[]) for i in session.get('items',[])],'submittedAt':session.get('submittedAt')}
    (dest/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))
    db.close()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('label');capture(parser.parse_args().label)
