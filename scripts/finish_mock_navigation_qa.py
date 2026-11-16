"""Finish mock-navigation QA only after the root hands the dedicated AVD back.

Compare the actual learner DB after capture, after Debug20 opens, and after
Release20 opens. Keep Release20 installed, restore the original display, and
stop only this task's native emulator-5590 and dedicated ADB5045 server.
No learner DB restore, reset, downgrade, or uninstall is performed.
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
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/mock-navigation-20261018'
PRIVATE = ROOT / 'private_evidence/mock-navigation-20261018'
ADB_EXE = 'C:/Android/Sdk/platform-tools/adb.exe'
SERVER = [ADB_EXE, '-P', '5045']
ADB = SERVER + ['-s', '127.0.0.1:5591']
NATIVE_ADB = SERVER + ['-s', 'emulator-5590']
OWNED_SERIALS = {'127.0.0.1:5591', 'emulator-5590'}
DEBUG_APK = ROOT / 'app/build/outputs/apk/debug/app-debug.apk'
RELEASE_APK = ROOT / 'app/build/outputs/apk/release/app-release.apk'
AAPT = 'C:/Android/Sdk/build-tools/35.0.0/aapt.exe'
JAVA = 'C:/Program Files/Android/Android Studio/jbr/bin/java.exe'
APKSIGNER = 'C:/Android/Sdk/build-tools/35.0.0/lib/apksigner.jar'
VERSION = '0.11.0'
VERSION_CODE = 20
PACKAGE = 'kr.sqld.study'


def now():
    return datetime.datetime.now().astimezone().isoformat()


def run(command, timeout=60):
    return subprocess.run(command, capture_output=True, check=True, timeout=timeout).stdout


def adb(*args):
    return run(ADB + list(args))


def text(*args):
    return adb(*args).decode('utf-8', errors='replace').strip()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def device_states():
    output = run(SERVER + ['devices']).decode('utf-8', errors='replace')
    return {line.split()[0]: line.split()[1] for line in output.splitlines()[1:] if line.strip()}


def guard_target():
    metadata = read_json(OUT / 'emulator-launch-metadata.json')
    assert metadata['adbServerPort'] == 5045 and metadata['serial'] == '127.0.0.1:5591'
    assert pathlib.Path(metadata['avdPath']).resolve() == (ROOT / '.android/avd/SQLNote_QA.avd').resolve()
    assert metadata['wiped'] is False and '-wipe-data' not in metadata['arguments']
    for base in [ADB, NATIVE_ADB]:
        def prop(name):
            return run(base + ['shell', 'getprop', name]).decode().strip()
        assert prop('ro.kernel.qemu') == '1', 'Target is not an emulator.'
        assert prop('ro.boot.qemu.avd_name') == 'SQLNote_QA', 'Wrong AVD.'
        assert prop('ro.build.version.sdk') == '34', 'Wrong Android API.'
    assert not set(device_states()) - OWNED_SERIALS, 'ADB5045 also serves another device; hand control back.'


def apk_identity(path):
    badging = run([AAPT, 'dump', 'badging', str(path)]).decode('utf-8', errors='replace')
    expected = "package: name='kr.sqld.study' versionCode='20' versionName='0.11.0'"
    assert expected in badging, 'Unexpected local APK version or package: ' + path.name
    certificates = run([JAVA, '-jar', APKSIGNER, 'verify', '--print-certs', str(path)]).decode()
    certificate = re.search(r'certificate SHA-256 digest: ([0-9a-f]+)', certificates)
    assert certificate, 'APK signature was not verified.'
    return {'sha256': sha256(path), 'certificateSha256': certificate.group(1)}


def installed_package(expect_debug):
    package = text('shell', 'dumpsys', 'package', PACKAGE)
    assert re.search(r'\bversionCode=20\b', package) and 'versionName=0.11.0' in package
    debuggable = bool(re.search(r'^\s+(?:pkgFlags|flags)=\[.*DEBUGGABLE', package, re.M))
    assert debuggable is expect_debug, 'Unexpected installed build type.'
    installed_path = text('shell', 'pm', 'path', PACKAGE)
    assert installed_path.startswith('package:/data/app/') and '\n' not in installed_path
    adb('shell', 'test', '-s', installed_path[len('package:'):])


def install(apk, identity, expect_debug):
    guard_target()
    assert sha256(apk) == identity['sha256'], 'APK changed while QA was running.'
    result = text('install', '-r', str(apk))
    assert 'Success' in result, result
    installed_package(expect_debug)


def capture_and_compare(stage, baseline):
    guard_target()
    installed_package(expect_debug=True)
    destination = PRIVATE / (stage + '-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    destination.mkdir(parents=True, exist_ok=False)
    adb('shell', 'am', 'force-stop', PACKAGE)
    payload = adb('exec-out', 'run-as', PACKAGE, 'tar', '-c', 'databases')
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
    report = {
        'checkedAt': now(),
        'stage': stage,
        'allStoredFieldsEqual': current == baseline,
        'changedStateFields': sorted(
            key for key in current['state'].keys() | baseline['state'].keys()
            if current['state'].get(key) != baseline['state'].get(key)
        ),
        'submissionRowsEqual': submissions == baseline['submissionRows'],
        'recoveryRowsEqual': recoveries == baseline['recoveryRows'],
        'counts': {
            key: len(state.get(key, []))
            for key in ['sessions', 'submissions', 'bookmarks', 'annotations', 'notes', 'courseProgress', 'inkDocuments']
        },
        'submissionRowCount': len(submissions),
        'recoveryRowCount': len(recoveries),
        'roomSchemaVersion': schema,
        'sqliteIntegrity': 'ok',
        'currentDatabaseTarSha256': hashlib.sha256(payload).hexdigest(),
        'currentDatabaseTarBytes': len(payload),
        'privateSnapshotDirectory': destination.name,
        'comparisonScope': (
            'Baseline versus actual DB after Release20 launched to ready home; same-version/same-certificate '
            'Debug20 installed with -r only for run-as access and never launched before this capture.'
            if stage == 'after-release'
            else 'Baseline versus actual Debug20 app DB at the named stage; synthetic test fixture DBs are separate.'
        ),
        'databaseResetOrReplacementPerformed': False,
    }
    write_json(OUT / (stage + '-record-preservation.json'), report)
    print(json.dumps(report), flush=True)
    assert report['allStoredFieldsEqual'], 'Learner records changed at ' + stage + '; current DB preserved privately, no DB restore performed.'
    return report


def launch_to_ready(stage, expect_debug):
    guard_target()
    installed_package(expect_debug)
    adb('shell', 'am', 'force-stop', PACKAGE)
    started_at = time.monotonic()
    launch = text('shell', 'am', 'start', '-W', '-n', PACKAGE + '/.MainActivity')
    assert 'Status: ok' in launch, 'MainActivity launch did not report success.'
    total_time = re.search(r'TotalTime: (\d+)', launch)
    destination = PRIVATE / (stage + '-ui-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    destination.mkdir(parents=True, exist_ok=False)
    remote_xml = '/data/local/tmp/mock-navigation-' + stage + '-ready.xml'
    ready = False
    app_owns_focus = False
    attempts = 0
    last_node_count = 0
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        attempts += 1
        try:
            run(ADB + ['shell', 'uiautomator', 'dump', remote_xml], timeout=30)
            xml = adb('exec-out', 'cat', remote_xml)
            (destination / 'latest.xml').write_bytes(xml)
            nodes = ET.fromstring(xml).findall('.//node')
            last_node_count = len(nodes)
            texts = {node.get('text', '') for node in nodes}
            packages = {node.get('package', '') for node in nodes}
            windows = text('shell', 'dumpsys', 'window')
            focus_line = next((line for line in windows.splitlines() if 'mCurrentFocus=' in line), '')
            app_owns_focus = PACKAGE in focus_line and 'MainActivity' in focus_line
            ready = '\ub0b4 \uacf5\ubd80' in texts and PACKAGE in packages and app_owns_focus
            if ready:
                break
        except (subprocess.SubprocessError, ET.ParseError):
            pass
        time.sleep(2)
    (destination / 'screen.png').write_bytes(adb('exec-out', 'screencap', '-p'))
    report = {
        'checkedAt': now(),
        'stage': stage,
        'versionName': VERSION,
        'versionCode': VERSION_CODE,
        'buildType': 'debug' if expect_debug else 'release',
        'launchReportedStatusOk': True,
        'homeReady': ready,
        'appOwnsFocusedWindow': app_owns_focus,
        'readinessCriterion': 'Actual app package and the existing home title were present in the rendered UI hierarchy, and MainActivity owned the focused window.',
        'launchTotalTimeMs': int(total_time.group(1)) if total_time else None,
        'elapsedThroughReadyCheckSeconds': round(time.monotonic() - started_at, 3),
        'hierarchyAttempts': attempts,
        'lastHierarchyNodeCount': last_node_count,
        'personalHierarchyAndScreenshotStoredOnlyInPrivateEvidence': True,
        'rawUiDirectory': destination.name,
    }
    write_json(OUT / (stage + '-launch-ready.json'), report)
    print(json.dumps(report), flush=True)
    assert ready, 'MainActivity did not become ready; private UI evidence captured, cleanup stopped.'
    return report


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
    baseline = read_json(PRIVATE / 'before/snapshot.json')
    saved_environment = read_json(OUT / 'environment-before.json')
    assert sha256(PRIVATE / 'before/database.tar') == preparation['databaseTarSha256']
    debug_identity = apk_identity(DEBUG_APK)
    release_identity = apk_identity(RELEASE_APK)
    assert debug_identity['certificateSha256'] == release_identity['certificateSha256'] == preparation['certificateSha256']
    installed_package(expect_debug=True)
    comparisons = [capture_and_compare('after-capture', baseline)]
    launches = [launch_to_ready('debug', expect_debug=True)]
    comparisons.append(capture_and_compare('after-debug-launch', baseline))
    install(RELEASE_APK, release_identity, expect_debug=False)
    launches.append(launch_to_ready('release', expect_debug=False))
    adb('shell', 'am', 'force-stop', PACKAGE)
    install(DEBUG_APK, debug_identity, expect_debug=True)
    # Do not launch Debug20 here: it is only an access build for Release20's DB.
    comparisons.append(capture_and_compare('after-release', baseline))
    install(RELEASE_APK, release_identity, expect_debug=False)
    restore_environment(saved_environment)
    restored = environment()
    assert restored == saved_environment, 'Display restoration did not match the baseline.'
    installed_package(expect_debug=False)
    adb('shell', 'sync')
    report = {
        'checkedAt': now(),
        'baselineVersion': preparation['sourceVersion'],
        'finalInstalledVersion': VERSION,
        'finalInstalledVersionCode': VERSION_CODE,
        'finalInstalledBuildType': 'release',
        'debugApkSha256': debug_identity['sha256'],
        'releaseApkSha256': release_identity['sha256'],
        'certificateSha256': release_identity['certificateSha256'],
        'allThreeRecordComparisonsEqual': all(result['allStoredFieldsEqual'] for result in comparisons),
        'debugAndReleaseHomeReady': all(result['homeReady'] for result in launches),
        'releaseDbCaptureUsedUnlaunchedSameVersionDebugAccessBuild': True,
        'originalDisplayAndAnimationsRestored': True,
        'restoredEnvironment': restored,
        'databaseResetOrReplacementPerformed': False,
        'oldVersionAutomaticDowngradePerformed': False,
        'qaAvdShutdownRequested': False,
        'adb5045ServerStopped': False,
    }
    write_json(OUT / 'finish-summary.json', report)
    guard_target()
    # TCP aliases cannot be used for the emulator-console kill command.
    run(NATIVE_ADB + ['emu', 'kill'])
    report['qaAvdShutdownRequested'] = True
    deadline = time.monotonic() + 25
    while any(state == 'device' for state in device_states().values()) and time.monotonic() < deadline:
        time.sleep(1)
    remaining = device_states()
    assert not set(remaining) - OWNED_SERIALS, 'ADB5045 acquired another device; server left running.'
    assert not any(state == 'device' for state in remaining.values()), 'QA AVD still connected; server left running.'
    run(SERVER + ['kill-server'])
    report['qaAvdDisconnected'] = True
    report['adb5045ServerStopped'] = True
    report['finishedAt'] = now()
    write_json(OUT / 'finish-summary.json', report)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists():
            write_json(OUT / 'finish-error.json', {
                'failedAt': now(),
                'errorType': type(error).__name__,
                'reason': str(error),
                'databaseResetOrReplacementPerformed': False,
                'oldVersionAutomaticDowngradePerformed': False,
                'automaticContinuationStopped': True,
            })
        raise
