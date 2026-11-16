"""Package the verified local APK and source without caches, AVDs or signing keys."""
import argparse,collections,hashlib,json,pathlib,shutil,zipfile,datetime,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
def digest(data):return hashlib.sha256(data).hexdigest()
def contains_learner_records(value):
    """Runtime records are private even when they were created by an emulator test."""
    if isinstance(value,dict):
        fields=set(value)
        if value.get('format')=='sqlnote-backup':return True
        if {'sessions','submissions','settings'}<=fields:return True
        if {'sessionId','questionId','choiceIds','outcome','submittedAt'}<=fields:return True
        if {'question','choiceOrder','draft'}<=fields:return True
        if {'sourceId','sourceHash','edits','cursor'}<=fields:return True
        if {'noteId','blockId','quote','memo','at'}<=fields:return True
        if {'checkId','draft','revealed','rating'}<=fields:return True
        return any(contains_learner_records(v) for v in value.values())
    if isinstance(value,list):return any(contains_learner_records(v) for v in value)
    return False

def private_evidence(path):
    if path.suffix.lower() in {'.db','.sqlite','.sqlite3','.keystore','.jks','.p12','.pfx','.pem','.key'} or path.name.endswith(('-wal','-shm')):
        return True
    parts=path.relative_to(ROOT).parts
    if 'evidence' in parts and any(part.lower().startswith('private') for part in parts):return True
    if path.suffix.lower()!='.json':
        return False
    data=json.loads(path.read_text(encoding='utf-8-sig'))
    return contains_learner_records(data)

def check_apk_has_no_learner_records(archive):
    for name in archive.namelist():
        if not name.startswith('assets/') or name.endswith('/'):continue
        path=pathlib.PurePosixPath(name)
        assert path.suffix.lower() not in {'.db','.sqlite','.sqlite3','.keystore','.jks','.p12','.pfx','.pem','.key'},f'Private file in APK: {name}'
        assert not path.name.endswith(('-wal','-shm')),f'Database journal in APK: {name}'
        assert not any(part.lower().startswith('private') for part in path.parts),f'Private asset in APK: {name}'
        if path.suffix.lower()=='.json':
            assert not contains_learner_records(json.loads(archive.read(name).decode('utf-8-sig'))),f'Learner/test record in APK: {name}'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--build-type',choices=('debug','release'),default='debug')
    args=parser.parse_args()
    build_type=args.build_type
    DIST.mkdir(exist_ok=True)
    source=ROOT/f'app/build/outputs/apk/{build_type}/app-{build_type}.apk'
    pack_bytes=(ROOT/'app/src/main/assets/content-pack.json').read_bytes()
    pack=json.loads(pack_bytes)
    course_bytes=(ROOT/'app/src/main/assets/course-pack.json').read_bytes()
    course=json.loads(course_bytes)
    unit_bytes=None;unit_bank=None
    if (ROOT/'content/unit-question-bank.json').exists():
        unit_bytes=(ROOT/'content/unit-question-bank.json').read_bytes()
        assert unit_bytes==(ROOT/'app/src/main/assets/unit-question-bank.json').read_bytes()
        unit_bank=json.loads(unit_bytes)
        assert len(unit_bank['parts'])==5 and len(unit_bank['questions'])==939
        assert all(len(p['forms'])==3 and all(len(f['questionIds'])==50 for f in p['forms']) for p in unit_bank['parts'])
    assert course_bytes==(ROOT/'content/course-pack.json').read_bytes(),'Course asset differs from authored source'
    assert len(course['lessons'])==63
    plan_bytes=(ROOT/'content/study-plan.json').read_bytes()
    plan=json.loads(plan_bytes)
    assert plan_bytes==(ROOT/'app/src/main/assets/study-plan.json').read_bytes(),'Study plan asset differs from source'
    assert plan_bytes==(ROOT/'output/study-plan/study-plan.json').read_bytes(),'Exported study plan differs from source'
    from validate_visuals import validate as validate_visuals
    visual_bytes=(ROOT/'content/course-visuals.json').read_bytes()
    visuals=json.loads(visual_bytes)
    assert visual_bytes==(ROOT/'app/src/main/assets/course-visuals.json').read_bytes()
    validate_visuals(visuals,course,ROOT/'content')
    def check_visual_assets(archive):
        assert archive.read('assets/study-plan.json')==plan_bytes,'APK study plan differs from source'
        assert archive.read('assets/course-visuals.json')==visual_bytes
        for visual in visuals['visuals']:
            for field in ('pngAsset','svgAsset'):
                path=visual[field]
                assert archive.read('assets/'+path)==(ROOT/'content'/path).read_bytes(),path
    report=json.loads((ROOT/'evidence/content-validation.json').read_text(encoding='utf-8'))
    assert all(report['gates'][k] for k in ('structurePassed','objectiveMinimumsPassed','quantitiesMet'))
    assert len(pack['questions'])>=600 and all(q['status']=='published' for q in pack['questions'])
    gradle=(ROOT/'app/build.gradle.kts').read_text(encoding='utf-8')
    version=re.search(r'versionName\s*=\s*"([^"]+)"',gradle).group(1)
    code=int(re.search(r'versionCode\s*=\s*(\d+)',gradle).group(1))
    if version=='0.11.0':assert code==20,'SQL-note 0.11.0 must use versionCode 20'
    if version in ('0.9.0','0.10.0','0.10.1','0.11.0'):
        assert unit_bank is not None,'Missing reviewed unit bank'
        subprocess.run([sys.executable,str(ROOT/'scripts/build_unit_questions.py'),'--check'],check=True,stdout=subprocess.DEVNULL)
    repository=(ROOT/'app/src/main/java/kr/sqld/study/StudyRepository.kt').read_text(encoding='utf-8')
    backup_schema=int(re.search(r'const val CURRENT_VERSION\s*=\s*(\d+)',repository).group(1))
    walk_index=None;walk_assets={};walk_coverage=[]
    if version in ('0.7.0','0.8.0','0.8.1','0.9.0','0.10.0','0.10.1','0.11.0'):
        walk_root=ROOT/'content/sql-walkthroughs'
        walk_index=json.loads((walk_root/'index.json').read_text(encoding='utf-8'))
        walk_coverage=json.loads((walk_root/'coverage.json').read_text(encoding='utf-8'))
        filenames=['index.json']+[entry['file'] for entry in walk_index['entries']+walk_index['learningExamples']]
        assert len(filenames)==len(set(filenames)),'Duplicate walkthrough asset file'
        assert all(re.fullmatch(r'[A-Za-z0-9_.-]+\.json',name) and '..' not in name for name in filenames)
        expected=set(filenames)
        assert {p.name for p in walk_root.glob('*.json')}==expected|{'coverage.json'},'Unindexed authored walkthrough files'
        asset_root=ROOT/'app/src/main/assets/sql-walkthroughs'
        assert {p.name for p in asset_root.glob('*.json')}==expected,'Unindexed runtime walkthrough files'
        for name in filenames:
            data=(walk_root/name).read_bytes()
            assert data==(asset_root/name).read_bytes(),f'Walkthrough asset differs from source: {name}'
            walk_assets['assets/sql-walkthroughs/'+name]=data
        assert {row['questionId'] for row in walk_coverage}=={q['id'] for q in pack['questions']}
        assert {row['questionId'] for row in walk_coverage if row['status']=='applied'}=={entry['questionId'] for entry in walk_index['entries']}
    def check_walkthrough_assets(archive):
        if walk_index is None:return
        actual={name for name in archive.namelist() if name.startswith('assets/sql-walkthroughs/') and not name.endswith('/')}
        assert actual==set(walk_assets),'APK walkthrough list differs from source'
        for name,data in walk_assets.items():assert archive.read(name)==data,f'APK walkthrough differs from source: {name}'
    guide_assets={}
    if version in ('0.8.0','0.8.1','0.9.0','0.10.0','0.10.1','0.11.0'):
        from validate_lesson_guides import validate as validate_guide
        for lesson in course['lessons']:
            relative=f'lesson-guides/{lesson["id"]}.json'
            data=(ROOT/'content'/relative).read_bytes()
            validate_guide(json.loads(data),lesson)
            assert data==(ROOT/'app/src/main/assets'/relative).read_bytes(),relative
            guide_assets['assets/'+relative]=data
    def check_guide_assets(archive):
        if not guide_assets:return
        actual={name for name in archive.namelist() if name.startswith('assets/lesson-guides/') and not name.endswith('/')}
        assert actual==set(guide_assets),'APK lesson guides differ from authored list'
        for name,data in guide_assets.items():assert archive.read(name)==data,name
    with zipfile.ZipFile(source) as z:
        assert z.read('assets/content-pack.json')==pack_bytes,'APK content pack differs from reviewed source'
        assert z.read('assets/course-pack.json')==course_bytes,'APK course pack differs from reviewed source'
        check_visual_assets(z)
        check_walkthrough_assets(z)
        check_guide_assets(z)
        check_apk_has_no_learner_records(z)
        if unit_bytes is not None:assert z.read('assets/unit-question-bank.json')==unit_bytes
    apk=DIST/f'SQL-note-{version}-{build_type}.apk';shutil.copy2(source,apk)
    tests=ROOT/'evidence/jvm-results';tests.mkdir(exist_ok=True)
    for file in (ROOT/'app/build/test-results/testDebugUnitTest').glob('TEST-*.xml'):shutil.copy2(file,tests/file.name)
    for variant in ('debug','release'):
        for extension in ('xml','txt','html'):
            file=ROOT/f'app/build/reports/lint-results-{variant}.{extension}'
            if file.exists():shutil.copy2(file,ROOT/'evidence'/file.name)
    notes={n['id']:n for n in pack['notes']}
    summary=[]
    objectives={o['id']:o for o in pack['objectives']}
    for subject in ('model','sql'):
        qs=[q for q in pack['questions'] if q['subjectId']==subject]
        summary.append({'subjectId':subject,'notes':sum(objectives[n['objectiveId']]['subjectId']==subject for n in notes.values()),'questions':len(qs),'kinds':dict(collections.Counter(q['kind'] for q in qs))})
    manifest={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'appId':'kr.sqld.study','versionName':version,'versionCode':code,'buildType':build_type,'releaseClaim':False,'contentVersion':pack['version'],'contentPackSha256':digest(pack_bytes),'notes':len(notes),'questions':len(pack['questions']),'sources':len(pack['sources']),'countsBySubject':summary,'priorities':dict(collections.Counter(p['level'] for p in pack.get('studyPriorities',[]))),'apk':{'file':apk.name,'bytes':apk.stat().st_size,'sha256':digest(apk.read_bytes())},'limitations':['Official DataQ current scope not verified','No human expert review or Oracle/SQL Server execution','API34 emulator QA, not Galaxy physical-device QA','Publisher emphasis is not verified exam frequency','Existing development signing identity; no public release']}
    if build_type=='release':
        debug_source=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
        with zipfile.ZipFile(debug_source) as z:
            assert z.read('assets/content-pack.json')==pack_bytes,'Debug APK content pack differs from reviewed source'
            assert z.read('assets/course-pack.json')==course_bytes,'Debug APK course pack differs from reviewed source'
            check_visual_assets(z)
            check_walkthrough_assets(z)
            check_guide_assets(z)
            check_apk_has_no_learner_records(z)
            if unit_bytes is not None:assert z.read('assets/unit-question-bank.json')==unit_bytes
        debug_apk=DIST/f'SQL-note-{version}-debug.apk';shutil.copy2(debug_source,debug_apk)
        manifest['debugApk']={'file':debug_apk.name,'bytes':debug_apk.stat().st_size,'sha256':digest(debug_apk.read_bytes())}
    manifest['course']={'version':course['version'],'sha256':digest(course_bytes),'lessons':len(course['lessons']),
        'concepts':sum(len(x['concepts']) for x in course['lessons']),
        'examples':sum(len(x['examples']) for x in course['lessons']),
        'selfChecks':sum(len(x['selfChecks']) for x in course['lessons']),
        'progress':'Separate self-assessment, never added to scored question totals','backupSchema':backup_schema}
    study_days=[d for d in plan['days'] if d['studyDay'] is not None]
    manifest['studyPlan']={'sha256':digest(plan_bytes),'startDate':plan['startDate'],'endDate':plan['endDate'],
        'studyDays':len(study_days),'restDays':len(plan['days'])-len(study_days),
        'lectures':sum(len(d['lectures']) for d in study_days),'videoMinutes':sum(l['minutes'] for d in study_days for l in d['lectures']),
        'baseMinutes':sum(b['minutes'] for d in study_days for b in d['blocks']),
        'extensionMinutes':sum(b['minutes'] for d in study_days for b in d['extension']),
        'completionTracking':'Schedule only; existing course progress is not video/PDF completion'}
    linked={lesson for visual in visuals['visuals'] for lesson in visual['lessonIds']}
    manifest['visuals']={'version':visuals['version'],'sha256':digest(visual_bytes),'pictures':len(visuals['visuals']),
        'lessonAssociations':sum(len(v['lessonIds']) for v in visuals['visuals']),
        'linkedLessons':len(linked),'unlinkedLessons':len(course['lessons'])-len(linked),
        'readingGuides':len(visuals['guides']),'originalPicture20Retained':True}
    roots=('app/src','app/schemas','content','scripts','docs','qa','gradle')
    files={ROOT/n for n in ('README.md','AGENTS.md','.gitignore','settings.gradle.kts','build.gradle.kts','gradle.properties','gradlew','gradlew.bat','app/build.gradle.kts')}
    files.add(ROOT/'app/lint.xml')
    files.update(ROOT.glob('PRODUCT_*.md'))
    files.update(ROOT.glob('PERSONA_SCENARIOS.md'))
    files.update(ROOT.glob('REMAINING_PRODUCT_RISKS.md'))
    files.update(ROOT.glob('FINAL_PRODUCT_GATE.md'))
    for folder in roots:
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.tmp','.pending'})
    # Include task-owned evidence and dedicated QA captures. Keep AVD binaries/DB copies/logcat out.
    for p in (ROOT/'evidence').iterdir():
        if p.name.startswith('guide-'):continue # existing user0 backup/navigation captures stay private
        if p.name in ('visuals-emulator-launch.log','visuals-emulator-error.log'):
            continue
        if p.is_file() and p.suffix!='.apk' and 'logcat' not in p.name.lower() and p.name not in ('final-delivery-package.log','readability-package.log','usability-package-final.log','course-package.log','optimization-package.log','sidebar-package.log','visuals-package.log') and (p.suffix=='.json' or p.name.startswith(('visuals-','sidebar-','optimization-','course-','readability-','usability-','priority-','dedicated-','final-delivery-','instrumentation-final-','lint-results-'))):files.add(p)
    files.update(p for p in (ROOT/'evidence/visuals-corrections').glob('*') if p.is_file())
    files.update(tests.glob('*.xml'))
    for name in ('independent-plan-check.json','jvm-test-summary.json','source-preservation.json',
                 'release-assets-validation.json','phone-study-plan-instrumentation.log',
                 'release-study-plan-instrumentation.log','record-preservation.json','release-validation.json',
                 'debug-update-state-comparison.json','release-state-comparison.json','qa-summary.json',
                 'plan-document-validation.json','final-study-plan-instrumentation.log','final-apk-hashes.json',
                 'release-update-state-comparison.json','final-vs-original-state-comparison.json',
                 'independent_plan_check.py','release-install.txt','release-installed-package.txt','release-apksigner.txt'):
        p=ROOT/'evidence/study-plan-20261005'/name
        if p.is_file():files.add(p)
    files.update((ROOT/'evidence/study-plan-20261005').glob('plan-*.png'))
    for name in ('baseline-state-summary.json','color-contrast.json','color-contrast-independent-review.json','protected-source-check.json',
                 'qa-summary.json','update-state-comparison.json','release-state-comparison.json',
                 'final-apk-hashes.json','content-preservation.json','source-diff.json',
                 'phone-instrumentation.log','tablet-instrumentation.log','release-install.txt',
                 'jvm-test-summary.json','build.log','release-installed-package.txt',
                 'final-phone-plan-instrumentation.log','final-tablet-plan-instrumentation.log',
                 'before-font200-plan.png','before-vs-pre-sql-state-comparison.json',
                 'sql-reading-state-comparison.json','final-update-state-comparison.json',
                 'before-vs-final-state-comparison.json','final-installed-environment.json',
                 'final-content-preservation.json','final-release-apksigner.txt','static-color-contrast.json'):
        p=ROOT/'evidence/ui-redesign-20261005'/name
        if p.is_file():files.add(p)
    files.update(p for p in (ROOT/'evidence/ui-redesign-20261005').glob('ui-*.png') if not p.stem.endswith('-export'))
    functional=ROOT/'evidence/product-functional-qa-20261005'
    # Select reports and anonymized summaries only; never package user backups.
    for pattern in ('*.md','*summary.json','*preservation.json','*build*.log','*tests.log','TEST-*.xml','baseline-lint-*.txt'):
        files.update(functional.glob(pattern))
    files.update((functional/'final-unit').glob('TEST-*.xml'))
    for pattern in ('*.md','*instrumentation.log','*summary.json','*comparison.json','*evidence.json','final-*.png','release-061-*.png'):
        files.update(p for p in (functional/'runtime').glob(pattern) if 'private' not in p.name and 'user0' not in p.name and 'export' not in p.name)
    # Test-only diagnostic captures contain synthetic in-memory data, never user0 records.
    for pattern in ('final-phone320-font200-*.log','memo-nav-*.png','memo-nav-*.txt'):
        files.update((functional/'runtime').glob(pattern))
    for name in ('final-user0-preservation.json','final-user10-preservation.json','runtime-checklist.json','release-real-ime-check.json','final-installed-release.json'):
        p=functional/'runtime'/name
        if p.is_file():files.add(p)  # Reviewed counts/hashes only; no learner payload.
    files.update((functional/'runtime').glob('release-061-320dp-font200-real-ime-*-environment.json'))
    spacing=ROOT/'evidence/ui-spacing-20261006'
    for pattern in ('*.md','*summary.json','*preservation.json','build*.log'):
        files.update(spacing.glob(pattern))
    for pattern in ('*.md','*summary.json','*preservation.json','*observations.json','*instrumentation.log','before-phone*.png','before-tablet*.png','after-phone*.png','after-tablet*.png'):
        files.update(p for p in (spacing/'runtime').glob(pattern) if not any(token in p.name for token in ('private','user0','export')))
    manual_footer=spacing/'runtime/manual-footer-check.json'
    if manual_footer.is_file():files.add(manual_footer)
    if version in ('0.7.0','0.8.0','0.8.1','0.9.0','0.10.0','0.10.1','0.11.0'):
        reader=ROOT/'evidence/sql-reader-20261006'
        # Explicit public evidence only. Raw learner/QA exports, screenshots of user0,
        # accessibility node dumps, DBs, and data-transfer helper scripts stay local.
        for pattern in ('*.md','*summary.json','*preservation.json','*hashes.json','build*.log','*validation.log','*instrumentation.log','*tests.log'):
            files.update(p for p in reader.glob(pattern) if not any(t in p.name.lower() for t in ('private','backup','export','user0','user10')))
        final_captures = (
            'public-sql-reader-final-tablet', 'public-sql-reader-final-pen-settings',
            'public-sql-reader-final-mcq-phone', 'public-sql-reader-phone320-font150-fixed',
            'public-sql-reader-phone320-text-fixed', 'public-sql-reader-final-subquery',
            'public-sql-reader-final-subquery-wide',
        )
        for capture in final_captures:
            for suffix in ('.png', '-environment.json'):
                p=reader/'runtime'/f'{capture}{suffix}'
                assert p.is_file(),f'Missing final release capture: {p.name}'
                files.add(p)
        for pattern in ('*instrumentation.log','*summary.json','*preservation.json','*hashes.json','*checklist.json'):
            files.update(p for p in (reader/'runtime').glob(pattern) if not any(t in p.name.lower() for t in ('private','backup','export','user0','user10','nodes','logcat')))
        content_checks=ROOT/'evidence/sql-walkthroughs-20261006'
        for name in ('engine-checks.json','source-file-hashes.json','summary.json','validation.json'):
            p=content_checks/name
            if p.is_file():files.add(p)
        for name in ('docs/sql-reader-0.7.0.md','docs/sql-walkthrough-coverage.md','scripts/build_walkthroughs.py','scripts/validate_walkthroughs.py',
                     'qa/walkthrough-review/review_generated.py','qa/walkthrough-review/review_reference_example.py'):
            p=ROOT/name
            assert p.is_file(),f'Missing SQL reader source/review deliverable: {name}'
            files.add(p)
    files.update((ROOT/'output/study-plan').glob('*'))
    if version in ('0.8.0','0.8.1','0.9.0','0.10.0','0.10.1','0.11.0'):
        guide_evidence=ROOT/'evidence/explanation-upgrade-20261012'
        for pattern in ('*review.json','*validation.json','*engine*.json','*preservation.json','*ui.log','*instrumentation.log','*summary.json','coverage.json','verified-build.log','release-signature.log','guide-pilot-*.png','guide-phone-*.png','guide-final-*.png','guide-final-release-*-environment.json'):
            files.update(guide_evidence.glob(pattern))
        manifest['lessonGuides']={'report':'docs/explanation-upgrade-0.8.0.md','lessons':len(guide_assets),
            'assetBytes':sum(map(len,guide_assets.values())),
            'originalExamples':sum(len(l['examples']) for l in course['lessons']),
            'originalChecks':sum(len(l['selfChecks']) for l in course['lessons']),
            'scope':'Separate added course explanations and links from graded questions; not a rewrite of all PDF questions',
            'sourceBinding':'Exact original lesson snapshots; mismatched guides rejected'}
    files.add(ROOT/'output/pdf/SQLD_40일_전체학습계획_5시간_6시간.pdf')
    files.update(p for p in (ROOT/'evidence/usability-before').glob('*.json') if p.name in ('source-hashes.json','display.json'))
    for folder in ('timer-before-restart','timer-before-reboot','timer-after-reboot','annotation-after-selection'):
        files.update((ROOT/'evidence'/folder).glob('*.json'))
    if version in ('0.8.1','0.9.0','0.10.0','0.10.1','0.11.0'):
        readability=ROOT/'evidence/body-readability-20261013'
        for pattern in ('*.json','*.log','*/*.png','*/environment.json','*/instrumentation.log','*/body-layout-*.json'):
            files.update(readability.glob(pattern))
        manifest['bodyReadability']={'report':'docs/body-readability-0.8.1.md','scope':'Presentation only; source content and learner records retained'}
    files={p for p in files if not private_evidence(p)}
    if unit_bank is not None:
        unit_evidence=ROOT/'evidence/unit-practice-20261015'
        for pattern in ('*review*.json','content-validation.json','*summary.json','*preservation.json','build*.log','*instrumentation.log','release-*.log','*/*.png','*/environment.json','*/instrumentation.log'):
            files.update(unit_evidence.glob(pattern))
        files={p for p in files if not private_evidence(p)}
        manifest['baseQuestions']=len(pack['questions'])
        manifest['questions']=len(pack['questions'])+len(unit_bank['questions'])
        manifest['sources']=len({s['sourceId'] for s in pack['sources']+unit_bank['sources']})
        for row in manifest['countsBySubject']:
            questions=[q for q in pack['questions']+unit_bank['questions'] if q['subjectId']==row['subjectId']]
            row['questions']=len(questions);row['kinds']=dict(collections.Counter(q['kind'] for q in questions))
        manifest['unitPractice']={'report':'docs/unit-practice-0.9.0.md','additionalQuestions':len(unit_bank['questions']),'reviewQuestions':sum(len(p['reviewIds']) for p in unit_bank['parts']),
            'unitMockForms':sum(len(p['forms']) for p in unit_bank['parts']),'questionsPerForm':50,'totalLoadedQuestions':len(pack['questions'])+len(unit_bank['questions']),
            'bankSha256':digest(unit_bytes),'difficulty':'Author target; not empirically calibrated to official exams','review':'Independent AI review, not human expert or Oracle engine proof'}
    if version in ('0.10.0','0.10.1','0.11.0'):
        flow=ROOT/'evidence/learning-flow-20261018'
        for pattern in ('*.json','*.log','*/*.png','*/environment.json','*/*instrumentation.log','*/*summary.json','*/flow-*.json'):
            files.update(flow.glob(pattern))
        files={p for p in files if not private_evidence(p) and p!=flow/'package-final.log'}
        manifest['learningFlow']={'report':'docs/learning-flow-0.10.0.md','scope':'Home and lesson navigation; existing content and learner data preserved',
            'path':['overview','concepts','examples','checks'],'progressMeaning':'Self-confirmed learning steps, not mastery or exam score'}
    if version in ('0.10.1','0.11.0'):
        spen=ROOT/'evidence/spen-button-20261018'
        for pattern in ('*.json','*.log','*/environment.json','*/*instrumentation.log'):
            files.update(spen.glob(pattern))
        files={p for p in files if not private_evidence(p) and p!=spen/'package-final.log'}
        manifest['stylusButton']={'report':'docs/spen-button-0.10.1.md','behavior':'Hold stylus button to erase; release restores selected pen/highlighter without changing settings',
            'verificationBoundary':'Synthetic MotionEvent dispatch and emulator tests; physical Galaxy Tab/S Pen not verified'}
    if version=='0.11.0':
        mock_report=ROOT/'docs/mock-navigation-0.11.0.md'
        assert mock_report.is_file(),'Missing mock navigation change and QA report'
        files.add(mock_report)
        mock=ROOT/'evidence/mock-navigation-20261018'
        # Only public reports and synthetic UI captures belong in the source delivery.
        # Raw learner snapshots, DBs, node dumps, packaging logs and archives stay local.
        for p in mock.rglob('*'):
            if not p.is_file() or p.suffix.lower() not in {'.json','.log','.png'}:continue
            relative=p.relative_to(mock)
            if any(any(token in part.lower() for token in ('private','user0','user10','backup','export','nodes','logcat')) for part in relative.parts):continue
            if p.name.lower()=='package-final.log':continue
            if not private_evidence(p):files.add(p)
        manifest['mockNavigation']={'report':'docs/mock-navigation-0.11.0.md',
            'scope':'Mock exam > part > form > question; review stays separate; strict exam footer navigation',
            'preservation':'Existing question IDs, session snapshots, grading, learner records and stylus support retained',
            'verificationBoundary':'Recorded automated and emulator checks only; not physical Galaxy Tab or exam-difficulty validation'}
    # Final pass also covers any evidence added by version-specific sections above.
    files={p for p in files if not private_evidence(p) and p.name.lower()!='package-final.log'}
    archive=DIST/f'SQL-note-{version}-source.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            assert p.is_file(),f'Missing deliverable: {p}'
            z.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    manifest['sourceArchive']={'file':archive.name,'bytes':archive.stat().st_size,'sha256':digest(archive.read_bytes()),'files':len(files)}
    if version in ('0.6.0','0.6.1','0.6.2','0.7.0','0.8.0','0.8.1','0.9.0','0.10.0','0.10.1','0.11.0'):
        manifest['visualDesign']={'canvaDesignId':'DAHXJHn4ZsE','implementedAs':'Native Compose UI, no remote image or login dependency','reference':'docs/ui-redesign-design-source-2026-10-05.md','qa':'docs/ui-redesign-qa-2026-10-05.md'}
    if version=='0.6.1':
        manifest['functionalQa']={'report':'FINAL_PRODUCT_GATE.md','scope':'Offline learning interactions and record recovery; not a store release or learning-efficacy guarantee'}
    if version=='0.6.2':
        manifest['uiSpacingQa']={'report':'docs/ui-spacing-0.6.2.md','scope':'Adaptive action spacing and Korean heading wrapping; same offline learning records and content'}
    if version in ('0.7.0','0.8.0','0.8.1','0.9.0','0.10.0','0.10.1','0.11.0'):
        manifest['sqlReader']={'report':'docs/sql-reader-0.7.0.md','coverage':'docs/sql-walkthrough-coverage.md',
            'version':walk_index['version'],'questionWalkthroughs':len(walk_index['entries']),
            'learningExamples':len(walk_index['learningExamples']),
            'coverageCounts':dict(collections.Counter(row['status'] for row in walk_coverage)),
            'assetFiles':len(walk_assets),'assetBytes':sum(len(data) for data in walk_assets.values()),
            'indexSha256':digest(walk_assets['assets/sql-walkthroughs/index.json']),
            'backupSchema':backup_schema,'legacyBackupReadable':[1,2],
            'storage':'Local SQL-document-coordinate ink; original IDs and immutable submissions retained',
            'verificationBoundary':'Adapted SQLite fixture comparisons are not Oracle/SQL Server execution or physical S Pen validation',
            'privacy':'APK assets checked for learner/test runtime records; raw backups, DBs and signing keys excluded'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
