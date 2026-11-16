"""Finish the dedicated unit-flow capture task after the root's capture completes.

Run only when the capture owner has handed ADB back. Reads learner records before
restoring the exact original release APK; it never replaces or resets the DB.
"""

import datetime
import hashlib
import io
import json
import pathlib
import re
import sqlite3
import subprocess
import tarfile
import time


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/unit-flow-capture-20261018'
PRIVATE = ROOT / 'private_evidence/unit-flow-capture-20261018'
ADB_EXE = 'C:/Android/Sdk/platform-tools/adb.exe'
ADB_SERVER = [ADB_EXE, '-P', '5045']
ADB = ADB_SERVER + ['-s', '127.0.0.1:5591']
OWNED_SERIALS = {'127.0.0.1:5591', 'emulator-5590'}


def run(command):
    return subprocess.run(command, capture_output=True, check=True, timeout=60).stdout


def adb(*args):
    return run(ADB + list(args))


def text(*args):
    return adb(*args).decode('utf-8', errors='replace').strip()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def device_states():
    output = run(ADB_SERVER + ['devices']).decode('utf-8', errors='replace')
    return {line.split()[0]: line.split()[1] for line in output.splitlines()[1:] if line.strip()}


def connected_serials():
    return set(device_states())


def guard_target():
    assert text('shell', 'getprop', 'ro.kernel.qemu') == '1', 'Target is not an emulator.'
    assert text('shell', 'getprop', 'ro.boot.qemu.avd_name') == 'SQLNote_QA', 'Wrong AVD.'
    assert text('shell', 'getprop', 'ro.build.version.sdk') == '34', 'Wrong Android API.'
    unexpected = connected_serials() - OWNED_SERIALS
    assert not unexpected, 'ADB5045 also serves other devices; stop and hand control back.'


def environment():
    return {
        'size': text('shell', 'wm', 'size'),
        'density': text('shell', 'wm', 'density'),
        'font': text('shell', 'settings', 'get', 'system', 'font_scale'),
        'animations': {
            key: text('shell', 'settings', 'get', 'global', key)
            for key in ['window_animation_scale', 'transition_animation_scale', 'animator_duration_scale']
        },
    }


def capture_current():
    destination = PRIVATE / ('after-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    destination.mkdir(parents=True, exist_ok=False)
    adb('shell', 'am', 'force-stop', 'kr.sqld.study')
    payload = adb('exec-out', 'run-as', 'kr.sqld.study', 'tar', '-c', 'databases')
    (destination / 'database.tar').write_bytes(payload)
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        assert all(name == 'databases' or name.startswith('databases/') for name in archive.getnames())
        archive.extractall(destination, filter='data')
    with sqlite3.connect(destination / 'databases/sqlnote.db') as db:
        assert db.execute('PRAGMA integrity_check').fetchall() == [('ok',)], 'Current DB integrity failed.'
        state = json.loads(db.execute('SELECT payload FROM study_state WHERE id=1').fetchone()[0])
        submissions = [list(row) for row in db.execute('SELECT * FROM grading_submissions ORDER BY id')]
        recoveries = [list(row) for row in db.execute('SELECT * FROM recovery_points ORDER BY id')]
        schema = db.execute('PRAGMA user_version').fetchone()[0]
    current = {'state': state, 'submissionRows': submissions, 'recoveryRows': recoveries}
    (destination / 'snapshot.json').write_text(json.dumps(current, ensure_ascii=False), encoding='utf-8')
    return current, destination, payload, schema


def restore_environment(saved):
    for key in ['size', 'density']:
        match = re.search(r'Override ' + key + r':\s*([^\r\n]+)', saved[key])
        adb('shell', 'wm', key, match.group(1).strip() if match else 'reset')
    if saved['font'] == 'null':
        adb('shell', 'settings', 'delete', 'system', 'font_scale')
    else:
        adb('shell', 'settings', 'put', 'system', 'font_scale', saved['font'])
    for key, value in saved['animations'].items():
        if value == 'null':
            adb('shell', 'settings', 'delete', 'global', key)
        else:
            adb('shell', 'settings', 'put', 'global', key, value)


def main():
    guard_target()
    preparation = read_json(OUT / 'preparation-summary.json')
    saved_environment = read_json(OUT / 'environment-before.json')
    before = read_json(PRIVATE / 'before/snapshot.json')
    baseline_tar = PRIVATE / 'before/database.tar'
    assert hashlib.sha256(baseline_tar.read_bytes()).hexdigest() == preparation['databaseTarSha256']
    original_apk = PRIVATE / 'installed-before.apk'
    assert hashlib.sha256(original_apk.read_bytes()).hexdigest() == preparation['originalInstalledApkSha256']
    package = text('shell', 'dumpsys', 'package', 'kr.sqld.study')
    assert 'versionCode=19 ' in package and 'versionName=0.10.1' in package, 'Unexpected installed app version.'
    assert re.search(r'^\s+(?:pkgFlags|flags)=\[.*DEBUGGABLE', package, re.M), 'DB capture requires the existing debug access build.'

    current, destination, payload, schema = capture_current()
    comparison = {
        'checkedAt': datetime.datetime.now().astimezone().isoformat(),
        'allStoredFieldsEqual': current == before,
        'changedStateFields': sorted(
            key for key in current['state'].keys() | before['state'].keys()
            if current['state'].get(key) != before['state'].get(key)
        ),
        'submissionRowsEqual': current['submissionRows'] == before['submissionRows'],
        'recoveryRowsEqual': current['recoveryRows'] == before['recoveryRows'],
        'counts': {
            key: len(current['state'].get(key, []))
            for key in ['sessions', 'submissions', 'bookmarks', 'annotations', 'notes', 'courseProgress', 'inkDocuments']
        },
        'submissionRowCount': len(current['submissionRows']),
        'recoveryRowCount': len(current['recoveryRows']),
        'roomSchemaVersion': schema,
        'sqliteIntegrity': 'ok',
        'currentDatabaseTarSha256': hashlib.sha256(payload).hexdigest(),
        'currentDatabaseTarBytes': len(payload),
        'privateSnapshotDirectory': destination.name,
        'comparisonScope': 'Original baseline versus actual debug-access app DB after capture; captured before restoring the non-debuggable release. No post-release DB read or release launch is claimed.',
        'databaseResetOrReplacementPerformed': False,
    }
    write_json(OUT / 'record-preservation.json', comparison)
    print(json.dumps(comparison), flush=True)
    assert comparison['allStoredFieldsEqual'], 'Records changed; current DB captured privately. No release restore or shutdown performed.'

    guard_target()
    installed = text('install', '-r', str(original_apk))
    assert 'Success' in installed, installed
    package = text('shell', 'dumpsys', 'package', 'kr.sqld.study')
    assert 'versionCode=19 ' in package and 'versionName=0.10.1' in package
    assert not re.search(r'^\s+(?:pkgFlags|flags)=\[.*DEBUGGABLE', package, re.M)
    restore_environment(saved_environment)
    restored = environment()
    assert restored == saved_environment, 'Display restoration did not match the baseline.'
    report = {
        'checkedAt': datetime.datetime.now().astimezone().isoformat(),
        'exactOriginalReleaseReinstalled': True,
        'restoredReleaseVersion': '0.10.1',
        'restoredReleaseVersionCode': 19,
        'releaseLaunchedByCleanup': False,
        'originalDisplayAndAnimationsRestored': True,
        'restoredEnvironment': restored,
        'databaseComparisonPerformedBeforeReleaseRestore': True,
        'qaAvdShutdownRequested': False,
        'adb5045ServerStopped': False,
    }
    write_json(OUT / 'cleanup-summary.json', report)
    guard_target()
    # Emulator console commands require the native emulator serial, not its TCP alias.
    native = ADB_SERVER + ['-s', 'emulator-5590']
    assert run(native + ['shell', 'getprop', 'ro.boot.qemu.avd_name']).decode().strip() == 'SQLNote_QA'
    run(native + ['emu', 'kill'])
    report['qaAvdShutdownRequested'] = True
    deadline = time.monotonic() + 25
    while any(state == 'device' for state in device_states().values()) and time.monotonic() < deadline:
        time.sleep(1)
    remaining = device_states()
    assert not set(remaining) - OWNED_SERIALS, 'ADB5045 acquired another device; server left running.'
    assert not any(state == 'device' for state in remaining.values()), 'QA AVD is still connected; server left running.'
    # ADB can retain this task's known TCP serial as offline after emu kill.
    # Those entries are safe to clear by stopping this task's dedicated server.
    run(ADB_SERVER + ['kill-server'])
    report['adb5045ServerStopped'] = True
    report['qaAvdDisconnected'] = True
    report['finishedAt'] = datetime.datetime.now().astimezone().isoformat()
    write_json(OUT / 'cleanup-summary.json', report)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
