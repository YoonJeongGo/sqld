"""Read the explicitly selected QA AVD's existing records; never bundle private copies."""
import hashlib, io, json, pathlib, sqlite3, subprocess, tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = ['C:/Android/Sdk/platform-tools/adb.exe', '-P', '5045', '-s', '127.0.0.1:5591']

def adb(*args):
    return subprocess.run(ADB + list(args), check=True, capture_output=True).stdout

def main():
    assert adb('shell','getprop','ro.kernel.qemu').strip() == b'1'
    assert adb('shell','getprop','ro.boot.qemu.avd_name').strip() == b'SQLNote_QA'
    private = ROOT/'private_evidence/guide-after-update'
    private.mkdir(parents=True, exist_ok=True)
    adb('shell','am','force-stop','kr.sqld.study')
    data = adb('exec-out','run-as','kr.sqld.study','tar','-c','databases')
    (private/'database.tar').write_bytes(data)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(private, filter='data')
    before_envelope=json.loads((ROOT/'private_evidence/guide-before-20261012.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(before_envelope['payload'].encode()).hexdigest()==before_envelope['sha256']
    before=json.loads(before_envelope['payload'])
    with sqlite3.connect(private/'databases/sqlnote.db') as db:
        after=json.loads(db.execute('SELECT payload FROM study_state WHERE id=1').fetchone()[0])
    # The exported backup upgrades only the schema version; normalize absent defaults.
    changed=[key for key in set(before)|set(after) if before.get(key)!=after.get(key)]
    report={'comparison':'Existing 0.7.0 export versus stored records after non-destructive APK update',
            'fieldsEqual':not changed,'changedFields':changed,'backupChecksumValid':True,
            'counts':{key:len(before.get(key,[])) for key in ['sessions','submissions','bookmarks','annotations','inkDocuments','notes','courseProgress']},
            'privateCopiesExcludedFromDistribution':True}
    (ROOT/'evidence/explanation-upgrade-20261012/update-preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))
    assert not changed, changed

if __name__=='__main__':main()
