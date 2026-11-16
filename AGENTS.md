# SQL 노트
- Read docs/MASTER-REQUEST.txt and docs/requirements.md. Korean offline personal Android app; content correctness and preservation precede counts.
- No paid APIs, accounts, credentials, network permission, public deployment, push, destructive reset, or first Git commit without explicit authorization.
- Kotlin / Compose / Material 3 / Room / DataStore. Build and test via scripts/build.ps1; content via python scripts/validate_content.py.
- Preserve stable question/choice/block IDs, immutable submissions, session snapshots, and ExamSpec. Never destructive Room migration. Backup replacement must validate, preview, save recovery point, and commit atomically.
- Content authored in content/part-*.json, source metadata in content/sources.json, merged validated pack in app assets. Unreviewed/quarantined items never enter normal sessions. Do not copy licensed exams or invent provenance, official verification, engine execution, expert review, or device proof.
- Keep author review, independent AI review, engine tests, human review, emulator QA, and physical device QA separate in evidence.
- New content must pass schema/reference/answer/explanation checks; reserve mock families before first diagnostic use; stable choiceId grading only.
- Report actual counts and incomplete requirements. See docs/decisions.md, docs/sources-and-scope.md, docs/QA.md.
