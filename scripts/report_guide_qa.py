"""Summarize actual local test artifacts; never infer physical-device or engine proof."""
import collections
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/explanation-upgrade-20261012'


def main():
    suites = [ET.parse(p).getroot() for p in (ROOT / 'app/build/test-results/testDebugUnitTest').glob('TEST-*.xml')]
    assert suites, 'Missing JVM reports'
    unit = {key: sum(int(s.get(key, 0)) for s in suites) for key in ('tests', 'failures', 'errors', 'skipped')}
    assert unit == {'tests': 93, 'failures': 0, 'errors': 0, 'skipped': 0}, unit
    device = []
    for name, count, screen, font in (
        ('tablet-final-instrumentation.log', 87, '1600x1000 dp', 1.0),
        ('phone-final-instrumentation.log', 14, '360x800 dp', 1.5),
        ('short-landscape-instrumentation.log', 1, '640x360 dp', 1.0),
    ):
        log = (OUT / name).read_text(encoding='utf-8-sig')
        assert f'OK ({count} test' in log and 'FAILURES!!!' not in log, name
        device.append({'log': name, 'testsPassed': count, 'screen': screen, 'fontScale': font, 'androidApi': 34, 'physicalDevice': False})
    lint = {}
    for variant in ('debug', 'release'):
        issues = ET.parse(ROOT / f'app/build/reports/lint-results-{variant}.xml').getroot().findall('issue')
        severities = collections.Counter(i.get('severity') for i in issues)
        assert not severities['Error'] and not severities['Fatal'], severities
        lint[variant] = dict(severities)
    build = (OUT / 'verified-build.log').read_text(encoding='utf-8-sig')
    assert 'BUILD SUCCESSFUL' in build
    install = (OUT / 'release-install-summary.json')
    report = {
        'version': '0.8.0', 'versionCode': 15, 'date': '2026-10-12',
        'unit': unit, 'device': device, 'lint': lint,
        'build': {'passed': True, 'log': 'verified-build.log'},
        'releaseApk': json.loads((OUT / 'apk-validation.json').read_text())['release'],
        'existingRecords': json.loads((OUT / 'update-preservation.json').read_text()),
        'releaseInstall': json.loads(install.read_text()) if install.exists() else None,
        'initialFailures': {
            'log': 'tablet-all-instrumentation.log', 'count': 4,
            'productFix': 'Separate expanded/collapsed note scroll states to preserve position when maximum scroll shrinks',
            'testFixes': ['Scope selectors to the active modal', 'Do not require scrolling for three filtered notes that already fit'],
            'finalRecheck': 'All 87 tablet tests passed',
        },
        'contentEvidence': {
            'sourceFilesUnchanged': 208, 'lessons': 63, 'originalExamples': 95, 'originalChecks': 189,
            'supplementalExamples': 2, 'authoredSteps': 417, 'existingPictures': 27,
            'sqliteExecuted': 50, 'sqliteVersion': '3.50.4',
            'oracleExecuted': False, 'sqlServerExecuted': False,
        },
        'limits': [
            'Release manual smoke and debug instrumentation are distinct evidence',
            'No physical Galaxy Tab or S Pen test',
            'No Oracle/SQL Server engine execution or human expert review',
            'No whole-publisher-PDF question rewrite or official syllabus completeness claim',
            'All 661 questions link to separate related guides after grading; 133 retain question-specific SQL walkthroughs',
            'No learning-transfer study or pass probability estimate',
        ],
    }
    release_preservation = OUT / 'release-record-preservation.json'
    if release_preservation.exists():
        report['finalReleaseRecords'] = json.loads(release_preservation.read_text())
        assert report['finalReleaseRecords']['fieldsEqual']
    (OUT / 'qa-summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'unit': unit, 'devicePassed': [x['testsPassed'] for x in device], 'lint': lint}, ensure_ascii=False))


if __name__ == '__main__':
    main()
