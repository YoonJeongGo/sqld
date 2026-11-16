"""Validate original content and atomically build the Android asset.

This is structural/heuristic validation, not SQL execution or expert review.
Authored files are read only. Invalid questions are quarantined in the report;
schema-safe questions remain in the asset with status=quarantined.
"""
from __future__ import annotations

import argparse
import collections
import copy
import datetime as dt
import difflib
import hashlib
import json
import re
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026.09.14.2"
EXAM = dict(id="sqld-provisional-2026-09-14", version=1, title="SQLD 검토용 기준",
            checkedAt="2026-09-14", effectiveDate=None,
            sourceIds=["dataq-sqld", "eduwill-sqld2026"],
            verification="provisional_official_unavailable", modelCount=10,
            sqlCount=40, pointsPerQuestion=2, minutes=90, passPoints=60,
            subjectMinimumPercent=40)
TARGETS = {"recall": 150, "application": 200, "mock": 250}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def status_only_transition(question, previous_sha):
    """Prove a reviewed quarantined record changed only its publication state."""
    if question.get("status") != "published":
        return False
    previous = dict(question, status="quarantined")
    return digest(previous) == previous_sha


def stable_read(path):
    """Avoid consuming a partially written or concurrently changed author file."""
    for attempt in range(12):
        try:
            before = path.stat()
            raw = path.read_bytes()
            data = json.loads(raw.decode("utf-8-sig"))
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns):
                return data, {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(raw).hexdigest(),
                              "bytes": len(raw), "modifiedNs": after.st_mtime_ns}
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            if attempt == 11:
                raise
        time.sleep(.1)
    raise RuntimeError(f"Content changed continually: {path}")


def atomic_write(path, value, json_format=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".pending")
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n" if json_format else value
    pending.write_text(text, encoding="utf-8", newline="\n")
    pending.replace(path)


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "; ".join(as_text(x) for x in value)
    if isinstance(value, dict):
        return "; ".join(f"{key}: {as_text(item)}" for key, item in value.items())
    return str(value)


def canonical_text(value):
    return re.sub(r"\s+", "", value).casefold()


def canonical_sql(value):
    """Normalize layout outside quoted tokens; preserve SQL literal values."""
    chunks = re.split(r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\")", value)
    return "".join(chunk if index % 2 else canonical_text(chunk) for index, chunk in enumerate(chunks))


def sql_signature(value):
    """Only a candidate heuristic. Literal replacement does not prove equivalence."""
    value = re.sub(r"--[^\n]*|/\*.*?\*/", " ", value, flags=re.S)
    value = re.sub(r"'(?:''|[^'])*'", "'?literal'", value)
    value = re.sub(r"\b\d+(?:\.\d+)?\b", "?number", value)
    return canonical_text(value)


def identifier_sql_signature(value):
    """Candidate skeleton also detects systematic table/column/alias renaming."""
    keywords = set(("select distinct from where group by having order asc desc nulls last first join inner left right full outer cross natural on using "
                    "and or not in exists any all between like escape union intersect minus as with case when then else end over partition rows range "
                    "unbounded preceding following current row fetch next only ties offset connect prior start siblings is null insert into values update "
                    "set delete merge matched commit rollback savepoint create table alter drop truncate grant revoke count sum avg min max nvl nvl2 "
                    "coalesce nullif decode substr length round trunc mod replace trim upper lower to_char to_date add_months months_between sysdate date "
                    "timestamp extract regexp_like regexp_substr regexp_replace rank dense_rank row_number lag lead first_value last_value ntile grouping "
                    "grouping_id rollup cube sets pivot unpivot include exclude number varchar varchar2 char int integer smallint decimal numeric primary "
                    "foreign key unique references check constraint default dual rownum level connect_by_isleaf connect_by_iscycle connect_by_root "
                    "sys_connect_by_path nocycle recursive").split())
    names, output = {}, []
    for token in re.findall(r"'(?:''|[^'])*'|\w+|[^\s]", value.casefold()):
        if token.startswith("'"):
            output.append("STRING")
        elif token.isdecimal():
            output.append("NUMBER")
        elif token in keywords:
            output.append(token)
        elif re.match(r"\w", token):
            names.setdefault(token, f"identifier{len(names)}")
            output.append(names[token])
        else:
            output.append(token)
    return "".join(output)


class Validation:
    def __init__(self):
        self.issues = []
        self.unsafe = set()

    def issue(self, kind, item, code, detail, severity="error", schema=False):
        self.issues.append(dict(kind=kind, id=item, code=code, severity=severity, detail=detail))
        if schema:
            self.unsafe.add((kind, item))

    def string(self, obj, field, kind, item, required=True):
        value = obj.get(field)
        if not isinstance(value, str) or (required and not value.strip()):
            self.issue(kind, item, "field_string", field, schema=True)

    def strings(self, obj, field, kind, item, nonempty=False):
        value = obj.get(field)
        if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value) or (nonempty and not value):
            self.issue(kind, item, "field_string_list", field, schema=True)
            return []
        return value

    def table(self, obj, kind, item, label):
        if not isinstance(obj, dict):
            self.issue(kind, item, "table_object", label, schema=True)
            return
        columns = self.strings(obj, "columns", kind, item, True)
        self.string(obj, "title", kind, item, False)
        rows = obj.get("rows")
        if not isinstance(rows, list):
            self.issue(kind, item, "table_rows", label, schema=True)
            return
        for index, row in enumerate(rows):
            if not isinstance(row, list) or len(row) != len(columns):
                self.issue(kind, item, "table_width", f"{label} row {index}", schema=True)
            elif any(cell is not None and not isinstance(cell, str) for cell in row):
                self.issue(kind, item, "table_cell_type", f"{label} row {index}: only JSON string/null permitted", schema=True)

    def errors(self, kind, item):
        return [x for x in self.issues if x["kind"] == kind and x["id"] == item and x["severity"] == "error"]


def load_reviews():
    """Pin one consistent review snapshot for both quarantine and coverage counts."""
    stems = ["evidence/content-blind", "evidence/content-blind-risk"]
    stems += [str(p.relative_to(ROOT)).replace("\\", "/").removesuffix("-comparison.json")
              for p in sorted(list((ROOT / "qa").glob("content-*-comparison.json")) + list((ROOT / "qa").glob("priority-*-comparison.json")))]
    batches = []
    for stem in stems:
        comparison_path = ROOT / f"{stem}-comparison.json"
        if not comparison_path.exists():
            continue
        comparison, _ = stable_read(comparison_path)
        public_input, _ = stable_read(ROOT / f"{stem}-input.json")
        decisions, _ = stable_read(ROOT / f"{stem}-decisions.json")
        masked = decisions.get("method") == "independent_ai_blind_reasoning_masked_choice_ids"
        valid = (decisions.get("method") in ["independent_ai_blind_reasoning", "independent_ai_blind_reasoning_masked_choice_ids"]
                 and digest(public_input.get("questions", [])) == public_input.get("inputSha256")
                 == comparison.get("inputSha256") == decisions.get("inputSha256")
                 and digest(decisions) == comparison.get("decisionsSha256"))
        if public_input.get("choiceMapSha256"):
            valid = valid and comparison.get("choiceMapSha256") == public_input["choiceMapSha256"]
        batches.append(dict(stem=stem, comparison=comparison, valid=valid, masked=masked,
                            prior_answer_exposure=decisions.get("priorAnswerExposure", False) is True))
    return batches


def build():
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    v = Validation()
    parts, inputs = [], []
    for filename in ["part-a.json", "part-b.json"]:
        part, metadata = stable_read(ROOT / "content" / filename)
        parts.append(part)
        inputs.append(metadata)
    registry, meta = stable_read(ROOT / "content/sources.json")
    inputs.append(meta)
    raw_sources = registry.get("sources", registry.get("records", registry.get("registry", {}).get("records", [])))
    sources = []
    for source in raw_sources:
        source_id = source.get("sourceId")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("Source registry sourceId must remain a nonempty string")
        result = {key: as_text(source.get(key)) for key in
                  ["sourceId", "publisher", "title", "url", "checkedAt", "license", "usageScope", "accessStatus"]}
        for key in ["version", "publicationDate"]:
            result[key] = as_text(source[key]) if source.get(key) is not None else None
        sources.append(result)
    objectives = sum([p["objectives"] for p in parts], [])
    notes = sum([p["notes"] for p in parts], [])
    questions = sum([p["questions"] for p in parts], [])
    maps = {}
    for kind, records, field in [("source", sources, "sourceId"), ("objective", objectives, "id"),
                                 ("note", notes, "id"), ("question", questions, "id")]:
        ids = [x.get(field) for x in records]
        for item, count in collections.Counter(ids).items():
            if not isinstance(item, str) or not item or count != 1:
                v.issue(kind, item, "unique_id", f"Count {count}; nonempty unique IDs required", schema=True)
        maps[kind] = {x.get(field): x for x in records}
    legacy_versions = {}
    legacy_path = ROOT / "content/legacy-note-versions.json"
    if legacy_path.exists():
        legacy, meta = stable_read(legacy_path)
        inputs.append(meta)
        legacy_versions = legacy.get("noteVersions", {})
        for nid, version in legacy_versions.items():
            if nid not in maps["note"] or type(version) is not int or version < 1 or version > maps["note"][nid].get("version", 0):
                v.issue("note", nid, "legacy_read_version", "Invalid deployed legacy note version")
    guide = {}
    guide_path = ROOT / "content/study-priorities.json"
    if guide_path.exists():
        guide, meta = stable_read(guide_path)
        inputs.append(meta)
        for field in ["checkedAt", "methodology"]:
            v.string(guide, field, "priority", "methodology")
        entries = guide.get("priorities", [])
        if not isinstance(entries, list):
            v.issue("priority", "entries", "priority_list", "Priority list required")
            entries = []
        counts = collections.Counter(e.get("objectiveId") for e in entries)
        for oid in maps["objective"]:
            if counts[oid] != 1:
                v.issue("priority", oid, "priority_coverage", "Exactly one priority required per objective")
        for entry in entries:
            oid = entry.get("objectiveId")
            if oid not in maps["objective"]:
                v.issue("priority", oid, "objective_ref", oid)
            if entry.get("level") not in ["core", "important", "foundation"]:
                v.issue("priority", oid, "priority_level", "Invalid learning priority")
            if entry.get("frequencyStatus") not in ["not_measured", "educator_emphasis"]:
                v.issue("priority", oid, "frequency_status", "Only unmeasured or attributed educator emphasis supported")
            for field in ["reason", "frequencyNote"]:
                v.string(entry, field, "priority", oid)
            v.strings(entry, "focusPoints", "priority", oid, True)
            for ref in v.strings(entry, "sourceIds", "priority", oid, True):
                if ref not in maps["source"]:
                    v.issue("priority", oid, "source_ref", ref)
        if len(entries) > 1 and all(e.get("level") == "core" for e in entries):
            v.issue("priority", "all", "priority_selectivity", "Do not mark every objective core")
    for o in objectives:
        oid = o.get("id")
        for field in ["id", "subjectId", "topicId", "title", "scopeStatus"]:
            v.string(o, field, "objective", oid)
        if o.get("subjectId") not in ["model", "sql"] or o.get("topicId") not in list("ABCDE"):
            v.issue("objective", oid, "subject_topic", "Invalid subject or topic")
        for ref in v.strings(o, "prerequisites", "objective", oid):
            if ref not in maps["objective"] or ref == oid:
                v.issue("objective", oid, "prerequisite_ref", ref)
        v.strings(o, "synonyms", "objective", oid)
    for note in notes:
        nid = note.get("id")
        for field in ["id", "objectiveId", "title", "summary", "verification"]:
            v.string(note, field, "note", nid)
        if type(note.get("version")) is not int or note["version"] < 1:
            v.issue("note", nid, "version", "Positive integer required", schema=True)
        if note.get("objectiveId") not in maps["objective"]:
            v.issue("note", nid, "objective_ref", note.get("objectiveId"))
        for ref in v.strings(note, "sourceIds", "note", nid, True):
            if ref not in maps["source"]:
                v.issue("note", nid, "source_ref", ref)
        blocks = note.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            v.issue("note", nid, "blocks", "Nonempty blocks required", schema=True)
            blocks = []
        block_ids = []
        for block in blocks:
            for field in ["id", "kind", "title", "text"]:
                v.string(block, field, "note", nid)
            block_ids.append(block.get("id"))
        if len(set(block_ids)) != len(block_ids):
            v.issue("note", nid, "duplicate_block_id", "Stable block IDs must be unique")
        kinds = {b.get("kind") for b in blocks}
        for required in ["definition", "explain", "example", "compare", "remember", "misconception", "recall"]:
            if required not in kinds:
                v.issue("note", nid, "pedagogy_block", required)
        for ref in v.strings(note, "recallQuestionIds", "note", nid, True):
            q = maps["question"].get(ref)
            if not q or q.get("kind") != "recall" or note.get("objectiveId") not in q.get("objectiveIds", []):
                v.issue("note", nid, "recall_ref", ref)
    for q in questions:
        qid = q.get("id")
        for field in ["id", "subjectId", "topicId", "familyId", "kind", "title", "stem", "sourceType",
                      "verification", "status", "dialect", "dialectVersion", "difficulty", "difficultyReason", "importanceReason"]:
            v.string(q, field, "question", qid)
        if type(q.get("version")) is not int or q["version"] < 1:
            v.issue("question", qid, "version", "Positive integer required", schema=True)
        enumerations = dict(subjectId=["model", "sql"], topicId=list("ABCDE"), kind=["recall", "application", "mock"],
                            sourceType=["original_practice", "original_mock"], verification=["document_review", "engine_verified", "cross_reviewed", "draft"],
                            status=["published", "quarantined", "draft"], dialect=["conceptual", "Oracle", "SQL Server"], difficulty=["basic", "intermediate"])
        for field, values in enumerations.items():
            if q.get(field) not in values:
                v.issue("question", qid, "enum", field)
        if q.get("dialectVersion") != {"Oracle": "19c", "SQL Server": "2022", "conceptual": "n/a"}.get(q.get("dialect")):
            v.issue("question", qid, "dialect_version", "Contract dialect/version pair mismatch")
        for ref in v.strings(q, "objectiveIds", "question", qid, True):
            objective = maps["objective"].get(ref)
            if not objective:
                v.issue("question", qid, "objective_ref", ref)
            elif objective["subjectId"] != q.get("subjectId"):
                v.issue("question", qid, "objective_subject", ref)
        for ref in v.strings(q, "sourceIds", "question", qid, True):
            if ref not in maps["source"]:
                v.issue("question", qid, "source_ref", ref)
            elif maps["source"][ref]["accessStatus"] != "retrieved":
                v.issue("question", qid, "source_not_retrieved", ref, "warning")
        v.strings(q, "validationEvidence", "question", qid, True)
        choices = q.get("choices")
        if not isinstance(choices, list) or len(choices) != 4 or any(not isinstance(c, dict) for c in choices):
            v.issue("question", qid, "four_choices", "Exactly four choice objects required", schema=True)
            choices = []
        for choice in choices:
            for field in ["id", "text", "reason"]:
                v.string(choice, field, "question", qid)
        if len({c.get("id") for c in choices}) != 4:
            v.issue("question", qid, "choice_id_unique", "Four distinct IDs required")
        # Whitespace may be the tested SQL string value (TRIM, CHAR, empty string).
        # Do not collapse or strip it when deciding whether two choices are equal.
        if len({c.get("text", "") for c in choices}) != 4:
            v.issue("question", qid, "choice_text_unique", "Four distinct choice texts required")
        correct = v.strings(q, "correctChoiceIds", "question", qid, True)
        if len(correct) != 1 or correct[0] not in [c.get("id") for c in choices]:
            v.issue("question", qid, "one_correct_choice", "Exactly one existing choice ID required")
        explanation = q.get("explanation")
        if not isinstance(explanation, dict):
            v.issue("question", qid, "explanation", "Object required", schema=True)
            explanation = {}
        for field in ["summary", "memory", "relatedNoteId"]:
            v.string(explanation, field, "question", qid)
        v.strings(explanation, "prerequisites", "question", qid)
        v.strings(explanation, "conditions", "question", qid, True)
        related_note = maps["note"].get(explanation.get("relatedNoteId"))
        if not related_note or related_note.get("objectiveId") not in q.get("objectiveIds", []):
            v.issue("question", qid, "related_note_ref", explanation.get("relatedNoteId"))
        steps = explanation.get("steps")
        if not isinstance(steps, list) or not steps:
            v.issue("question", qid, "explanation_steps", "Nonempty steps required", schema=True)
            steps = []
        for step in steps:
            for field in ["title", "text"]:
                v.string(step, field, "question", qid)
            if step.get("table") is not None:
                v.table(step["table"], "question", qid, "explanation step")
        tables = q.get("tables")
        if not isinstance(tables, list):
            v.issue("question", qid, "tables", "List required", schema=True)
            tables = []
        for table in tables:
            v.table(table, "question", qid, "input table")
        if q.get("sql") is not None and not isinstance(q["sql"], str):
            v.issue("question", qid, "sql_type", "String or null required", schema=True)
        fixture = q.get("fixture")
        if q.get("sql") and q.get("kind") in ["application", "mock"] and not fixture:
            v.issue("question", qid, "missing_sql_fixture", "SQL application requires reproducible input/expected result metadata")
        if fixture is not None:
            if not isinstance(fixture, dict):
                v.issue("question", qid, "fixture_type", "Object required", schema=True)
            else:
                for field in ["schemaSql", "setupSql", "query", "verificationMethod", "evidence"]:
                    v.string(fixture, field, "question", qid, field not in ["schemaSql", "setupSql"])
                v.strings(fixture, "constraints", "question", qid, True)
                v.strings(fixture, "sessionSettings", "question", qid, True)
                if type(fixture.get("ordered")) is not bool:
                    v.issue("question", qid, "fixture_ordered", "Boolean required", schema=True)
                rows = fixture.get("expectedRows")
                if not isinstance(rows, list) or any(not isinstance(r, list) or any(x is not None and not isinstance(x, str) for x in r) for r in rows):
                    v.issue("question", qid, "fixture_rows_type", "Rows must use string/null cells", schema=True)
                elif rows and len({len(row) for row in rows}) != 1:
                    v.issue("question", qid, "fixture_rows_width", "Expected rows must have a consistent width")
                if q.get("sql"):
                    displayed = canonical_sql(q["sql"].rstrip(";"))
                    queried = canonical_sql(fixture.get("query", "").rstrip(";"))
                    prepared = canonical_sql(fixture.get("setupSql", "").rstrip(";"))
                    # DML/TCL fixtures prepare initial rows, execute displayed mutations,
                    # then query the final state. Preserve statement order in the check.
                    mutation_prefix = displayed[:-len(queried)].rstrip(";") if queried and displayed.endswith(queried) else None
                    sequence_matches = mutation_prefix is not None and prepared.endswith(mutation_prefix)
                    if displayed != queried and not sequence_matches:
                        v.issue("question", qid, "fixture_query_mismatch", "Displayed SQL is absent from ordered fixture setup + final query")
                if tables and not fixture.get("schemaSql", "").strip():
                    v.issue("question", qid, "fixture_missing_schema", "Input table requires typed DDL")
                final_tables = [step["table"] for step in steps if isinstance(step.get("table"), dict)
                                and "최종" in step["table"].get("title", "")]
                if final_tables and isinstance(rows, list) and all(isinstance(row, list) for row in rows):
                    final_rows = final_tables[-1].get("rows", [])
                    if fixture.get("ordered"):
                        agrees = rows == final_rows
                    else:
                        # Bag comparison retains duplicate multiplicity and string/null distinction.
                        agrees = collections.Counter(map(digest, rows)) == collections.Counter(map(digest, final_rows))
                    if not agrees:
                        v.issue("question", qid, "fixture_explanation_result_mismatch", "Expected rows and final explanation table disagree")
                if fixture.get("ordered") and not re.search(r"\bORDER\s+(?:SIBLINGS\s+)?BY\b", fixture.get("query", ""), re.I):
                    v.issue("question", qid, "ordered_without_order_by", "Manual check needed: ordered result lacks ORDER BY", "warning")
                if fixture.get("verificationMethod") == "engine_verified" or q.get("verification") == "engine_verified":
                    v.issue("question", qid, "engine_evidence_requires_audit", "This validator does not execute the stated DBMS", "warning")
        mock_id = q.get("mockSetId")
        if mock_id is not None and (not isinstance(mock_id, str) or mock_id not in [f"mock-{i}" for i in range(1, 6)]):
            v.issue("question", qid, "mock_set_id", "Unknown mock set", schema=not isinstance(mock_id, str))
        if (q.get("kind") == "mock") != bool(mock_id) or (q.get("sourceType") == "original_mock") != bool(mock_id):
            v.issue("question", qid, "mock_reservation", "kind/sourceType/mockSetId must all identify a reserved mock")

    corrections = []
    for q in questions:
        correction = q.get("correction")
        if correction is None:
            continue
        if (not isinstance(correction, dict)
                or type(correction.get("previousVersion")) is not int
                or type(q.get("version")) is not int
                or not 0 < correction["previousVersion"] < q["version"]
                or not isinstance(correction.get("reason"), str) or not correction["reason"].strip()
                or not isinstance(correction.get("date"), str) or not correction["date"].strip()):
            v.issue("question", q["id"], "correction_shape", "Correction needs prior/current versions, reason and date")
            continue
        corrections.append(dict(questionId=q["id"], fromVersion=correction["previousVersion"],
                                toVersion=q["version"], reason=correction["reason"], at=correction["date"]))

    review_snapshot = load_reviews()
    for batch in review_snapshot:
        if not batch["valid"]:
            continue
        for result in batch["comparison"].get("results", []):
            q = maps["question"].get(result.get("questionId"))
            if result.get("status") == "answer_disagrees" and q and digest(q) == result.get("sourceQuestionSha256"):
                v.issue("question", q["id"], "independent_answer_disagreement", batch["stem"])

    families = collections.defaultdict(list)
    exact = collections.defaultdict(list)
    for q in questions:
        families[q.get("familyId")].append(q)
        signature = digest([canonical_text(q.get("stem", "")), canonical_sql(q.get("sql", "") or ""),
                            q.get("tables", []), sorted(c.get("text", "") for c in q.get("choices", []))])
        exact[signature].append(q)
    repeated_families = []
    for family, group in families.items():
        if len(group) > 1:
            repeated_families.append({"familyId": family, "questionIds": [q["id"] for q in group]})
            for q in group:
                v.issue("question", q["id"], "duplicate_family", family)
    exact_duplicates = []
    for group in exact.values():
        if len(group) > 1:
            exact_duplicates.append([q["id"] for q in group])
            for q in group[1:]:
                v.issue("question", q["id"], "exact_duplicate", group[0]["id"])
    near_duplicates = []
    sql_signatures = {q["id"]: sql_signature(q.get("sql") or "") for q in questions}
    identifier_signatures = {q["id"]: identifier_sql_signature(q.get("sql") or "") for q in questions}
    for i, left in enumerate(questions):
        for right in questions[i + 1:]:
            if left.get("subjectId") != right.get("subjectId"):
                continue
            a, b = canonical_text(left.get("stem", "")), canonical_text(right.get("stem", ""))
            ratio = 0.0
            if min(len(a), len(b)) >= 18 and min(len(a), len(b)) / max(len(a), len(b)) >= .82:
                ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
            same_sql = bool(left.get("sql") and right.get("sql") and sql_signatures[left["id"]] == sql_signatures[right["id"]])
            same_identifiers = bool(left.get("sql") and right.get("sql") and identifier_signatures[left["id"]] == identifier_signatures[right["id"]])
            if ratio >= .88 or same_sql or same_identifiers:
                near_duplicates.append(dict(left=left["id"], right=right["id"], stemSimilarity=round(ratio, 3),
                                            sameLiteralNormalizedSql=same_sql, sameIdentifierNormalizedSql=same_identifiers,
                                            disposition="manual_review_candidate_only"))
    practice_families = {q.get("familyId") for q in questions if not q.get("mockSetId") and q.get("kind") != "mock"}
    mock_families = {q.get("familyId") for q in questions if q.get("mockSetId") or q.get("kind") == "mock"}
    overlap = sorted(practice_families & mock_families)
    duplicate_review_path = ROOT / "evidence/content-duplicate-review.json"
    if duplicate_review_path.exists():
        duplicate_review, _ = stable_read(duplicate_review_path)
        decisions = {(x["left"], x["right"]): x for x in duplicate_review.get("decisions", [])}
        detected_pairs = {(x["left"], x["right"]) for x in near_duplicates}
        for pair_ids, decision in decisions.items():
            if pair_ids not in detected_pairs and all(qid in maps["question"] for qid in pair_ids):
                near_duplicates.append(dict(left=pair_ids[0], right=pair_ids[1],
                                            stemSimilarity=None, sameLiteralNormalizedSql=False,
                                            sameIdentifierNormalizedSql=False,
                                            discoveredBy="independent_manual_review",
                                            disposition="manual_review_candidate_only"))
        for pair in near_duplicates:
            decision = decisions.get((pair["left"], pair["right"]))
            if decision and decision.get("leftSha256") == digest(maps["question"][pair["left"]]) and decision.get("rightSha256") == digest(maps["question"][pair["right"]]):
                pair["disposition"] = decision["decision"]
                pair["manualReason"] = decision["reason"]
                if decision["decision"] == "same_family_template":
                    v.issue("question", pair["right"], "manual_same_family_template", pair["left"])
            elif decision:
                pair["disposition"] = "previous_review_source_changed"
    for q in questions:
        if q.get("mockSetId") and q.get("familyId") in overlap:
            v.issue("question", q["id"], "practice_mock_family_overlap", q["familyId"])
    mock_sets = []
    for i in range(1, 6):
        set_id = f"mock-{i}"
        group = [q for q in questions if q.get("mockSetId") == set_id]
        clean = [q for q in group if q.get("status") == "published" and q.get("verification") != "draft" and not v.errors("question", q["id"])]
        counts = collections.Counter(q["subjectId"] for q in clean)
        complete = len(clean) == 50 and counts["model"] == 10 and counts["sql"] == 40
        mock_sets.append(dict(id=set_id, authored=len(group), eligibleBeforeSetGate=len(clean), model=counts["model"], sql=counts["sql"], complete=complete))
    all_mock_complete = all(s["complete"] for s in mock_sets)
    if not all_mock_complete:
        for q in questions:
            if q.get("mockSetId"):
                v.issue("question", q["id"], "mock_sets_incomplete", "All five 10+40 sets must pass before mock release")

    bad_notes = {n["id"] for n in notes if v.errors("note", n["id"])}
    bad_objectives = {o["id"] for o in objectives if v.errors("objective", o["id"])}
    for q in questions:
        if q.get("explanation", {}).get("relatedNoteId") in bad_notes or any(x in bad_objectives for x in q.get("objectiveIds", [])):
            v.issue("question", q["id"], "invalid_dependency", "Related note/objective failed validation")
    merged_questions = []
    for original in questions:
        if ("question", original["id"]) in v.unsafe:
            continue
        q = copy.deepcopy(original)
        if v.errors("question", q["id"]):
            q["status"] = "quarantined"
        merged_questions.append(q)
    eligible = [q for q in merged_questions if q["status"] == "published" and q["verification"] != "draft"]
    practice = [q for q in eligible if not q.get("mockSetId") and q["kind"] != "mock"]
    coverage = []
    for o in objectives:
        oq = [q for q in practice if o["id"] in q["objectiveIds"]]
        on = [n for n in notes if n["objectiveId"] == o["id"] and n["id"] not in bad_notes]
        count = collections.Counter(q["kind"] for q in oq)
        coverage.append(dict(objectiveId=o["id"], title=o["title"], subjectId=o["subjectId"], notes=len(on),
                             recall=count["recall"], application=count["application"],
                             minimumMet=len(on) >= 1 and count["recall"] >= 3))
    positions = collections.Counter()
    answer_ids = collections.Counter()
    longest_unique = shortest_unique = 0
    correct_lengths, wrong_lengths = [], []
    for q in eligible:
        for index, choice in enumerate(q["choices"]):
            size = len(canonical_text(choice["text"]))
            if choice["id"] in q["correctChoiceIds"]:
                positions[str(index + 1)] += 1
                answer_ids[choice["id"]] += 1
                correct_lengths.append(size)
                wrong = [len(canonical_text(c["text"])) for c in q["choices"] if c["id"] != choice["id"]]
                longest_unique += int(size > max(wrong))
                shortest_unique += int(size < min(wrong))
            else:
                wrong_lengths.append(size)
    bias = dict(scope="Eligible authored choice arrays; runtime shuffling is tested separately in StudyEngineTest",
                answerArrayPositions=dict(positions), semanticCorrectChoiceIds=dict(answer_ids),
                longestCorrectUnique=longest_unique, shortestCorrectUnique=shortest_unique,
                longestCorrectRate=round(longest_unique / max(len(eligible), 1), 4),
                medianCorrectLength=statistics.median(correct_lengths) if correct_lengths else 0,
                medianWrongLength=statistics.median(wrong_lengths) if wrong_lengths else 0,
                warnings=[])
    if eligible and max(positions.values(), default=0) / len(eligible) > .4:
        bias["warnings"].append("One authored answer array position exceeds 40%")
    if bias["longestCorrectRate"] > .4:
        bias["warnings"].append("Unique longest choice is correct in >40%; manual wording audit required")
    if len(answer_ids) == 1 and eligible:
        bias["warnings"].append("All semantic correctChoiceIds use one ID. IDs must remain invisible; display order must be shuffled and persisted.")
    reviewed, masked_reviewed, prior_exposed_reviewed, review_batches = [], [], [], []
    status_transitions = []
    for batch in review_snapshot:
        stem, comparison, masked_choices, valid_evidence = batch["stem"], batch["comparison"], batch["masked"], batch["valid"]
        review_batches.append(dict(evidenceFile=f"{stem}-comparison.json", evidenceHashesValid=valid_evidence,
                                   choiceIdsAndOrderMasked=masked_choices, priorAnswerExposureDeclared=batch["prior_answer_exposure"], counts=comparison.get("counts", {}),
                                   limitation="Original semantic choice IDs were visible; common correct-ID bias was possible" if not masked_choices else "Choice IDs and array order randomized; map read only for comparison"))
        if valid_evidence:
            passed_rows = [r for r in comparison.get("results", []) if r["status"] == "answer_agrees"]
            reviewed.extend(passed_rows)
            if masked_choices:
                masked_reviewed.extend(passed_rows)
            if batch["prior_answer_exposure"]:
                prior_exposed_reviewed.extend(passed_rows)
            for row in passed_rows:
                q = maps["question"].get(row["questionId"])
                if q and status_only_transition(q, row["sourceQuestionSha256"]):
                    status_transitions.append(dict(questionId=q["id"], previousSourceQuestionSha256=row["sourceQuestionSha256"],
                                                   currentSourceQuestionSha256=digest(q), changedFields=["status"],
                                                   evidenceFile=f"{stem}-comparison.json", choiceIdsAndOrderMasked=masked_choices))
        else:
            v.issue("review_evidence", stem, "review_evidence_hash_mismatch", "Not included in independent-review counts", "warning")
    unique_reviewed = {r["questionId"] for r in reviewed}
    unchanged = sorted({r["questionId"] for r in reviewed if r["questionId"] in maps["question"]
                        and digest(maps["question"][r["questionId"]]) == r["sourceQuestionSha256"]})
    masked_unchanged = sorted({r["questionId"] for r in masked_reviewed if r["questionId"] in maps["question"]
                               and digest(maps["question"][r["questionId"]]) == r["sourceQuestionSha256"]})
    exposed_unchanged = sorted({r["questionId"] for r in prior_exposed_reviewed if r["questionId"] in maps["question"]
                               and digest(maps["question"][r["questionId"]]) == r["sourceQuestionSha256"]})
    traceable = set(unchanged) | {row["questionId"] for row in status_transitions}
    review = dict(reviewedSnapshotQuestions=len(unique_reviewed), recordedReviewPasses=len(reviewed),
                  currentUnchanged=len(unchanged), currentChanged=len(unique_reviewed) - len(unchanged),
                  currentWithMaskedChoiceIds=len(masked_unchanged), currentUnmaskedOnly=len(set(unchanged) - set(masked_unchanged)),
                  currentWithDeclaredPriorAnswerExposure=len(exposed_unchanged),
                  currentWithVerifiedStatusOnlyChange=len({row["questionId"] for row in status_transitions}),
                  currentUnchangedOrStatusOnly=len(traceable), statusOnlyTransitions=status_transitions,
                  allCurrentQuestionAnswersCompared=bool(questions) and set(maps["question"]) <= set(unchanged),
                  allCurrentQuestionAnswersChoiceMasked=bool(questions) and set(maps["question"]) <= set(masked_unchanged),
                  allCurrentAnswersUnchangedOrStatusOnly=bool(questions) and set(maps["question"]) <= traceable,
                  unchangedQuestionIds=unchanged, batches=review_batches,
                  boundary="Union of distinct question IDs from recorded reasoning snapshots; overlapping passes counted once. Changed revisions need a matching reviewed hash. Choice masking does not erase prior answer exposure. These are independent AI passes, not DBMS execution or human expert review.")
    authored_counts = collections.Counter(q.get("kind") for q in questions)
    eligible_counts = collections.Counter(q["kind"] for q in eligible)
    report = dict(schemaVersion=1, validatedAt=now, contentVersion=VERSION, inputs=inputs,
                  boundary="Automatic schema, references, coverage, heuristic duplication and bias only. Author document_review is not independent verification, Oracle execution, expert review, or official syllabus confirmation.",
                  officialExamVerification=EXAM["verification"], counts=dict(objectives=len(objectives), notes=len(notes), authoredQuestions=len(questions),
                    eligibleQuestions=len(eligible), eligiblePractice=len(practice), byAuthoredKind=dict(authored_counts), byEligibleKind=dict(eligible_counts),
                    uniqueFamilies=len(families), quarantinedQuestions=sum(bool(v.errors("question", q["id"])) or q.get("status")=="quarantined" for q in questions),
                    schemaUnsafeOmitted=sum(("question", q["id"]) in v.unsafe for q in questions), sources=len(sources), corrections=len(corrections)),
                  targets={kind: dict(required=target, authored=authored_counts[kind], eligible=eligible_counts[kind], gap=max(0, target - eligible_counts[kind])) for kind, target in TARGETS.items()},
                  objectives=coverage, mockSets=mock_sets, allMockSetsEnabled=all_mock_complete,
                  familyOverlap=overlap, repeatedFamilies=repeated_families, exactDuplicateGroups=exact_duplicates,
                  nearDuplicateCandidates=near_duplicates, duplicateBoundary="Heuristics cannot prove semantic family independence. Near matches are review candidates, not automatically counted as duplicates.",
                  bias=bias, independentReview=review, issues=v.issues,
                  gates=dict(structurePassed=not any(i["severity"] == "error" and i["code"] != "mock_sets_incomplete" for i in v.issues), objectiveMinimumsPassed=all(c["minimumMet"] for c in coverage),
                             quantitiesMet=all(eligible_counts[kind] >= count for kind, count in TARGETS.items()), officialScopeConfirmed=False,
                             sqlEngineVerified=False, expertReviewed=False, fullIndependentContentReview=False),
                  quarantined=[dict(id=q["id"], reasons=[x["code"] for x in v.errors("question", q["id"])] or ["author_quarantined"],
                                    representation="omitted_schema_unsafe" if ("question", q["id"]) in v.unsafe else "asset_status_quarantined")
                               for q in questions if v.errors("question", q["id"]) or q.get("status")=="quarantined"])
    pack = dict(schemaVersion=1, version=VERSION, examSpec=EXAM,
                objectives=[o for o in objectives if o["id"] not in bad_objectives],
                notes=[n for n in notes if n["id"] not in bad_notes], questions=merged_questions, sources=sources,
                corrections=corrections, studyPriorities=guide.get("priorities", []),
                priorityCheckedAt=guide.get("checkedAt", ""), priorityMethodology=guide.get("methodology", ""),
                legacyNoteVersions=legacy_versions)
    asset_path = ROOT / "app/src/main/assets/content-pack.json"
    atomic_write(asset_path, pack)
    report["assetSha256"] = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    atomic_write(ROOT / "evidence/content-validation.json", report)
    lines = ["# 콘텐츠 자동 검증 및 커버리지", "", f"검사 시각: {now} · pack {VERSION}", "",
             "공식 상세 출제기준·변경 공지·정오표는 DataQ 직접 접근 실패로 대조를 완료하지 못했다. 10+40문항·90분·2점·60점·과목40%는 잠정 기준이며 공식 현행 확인 상태가 아니다.", "",
             "이 보고서는 JSON 구조·참조·커버리지와 중복/편향 후보를 자동 검사했다. 저술자 document_review는 문서 규칙에 따른 자체 검토를 뜻하며 독립 검수·Oracle 실행·사람 전문가 검수와 같지 않다.", "",
             f"원본 {len(questions)}문항 중 앱 사용 가능 {len(eligible)}문항, 격리 {report['counts']['quarantinedQuestions']}문항. 검증 도구는 원저술 파일을 수정하지 않는다. 노트 {len(notes)}개, 학습목표 {len(objectives)}개, 출처 {len(sources)}개.", "",
             "| 구분 | 목표 | 저술 | 앱 사용 가능 | 부족 |", "|---|---:|---:|---:|---:|"]
    for kind, values in report["targets"].items():
        lines.append(f"| {kind} | {values['required']} | {values['authored']} | {values['eligible']} | {values['gap']} |")
    lines += ["", "| 학습목표 | 노트 | 회상 | 적용 | 노트1+회상3 |", "|---|---:|---:|---:|---|"]
    for c in coverage:
        lines.append(f"| {c['objectiveId']} {c['title']} | {c['notes']} | {c['recall']} | {c['application']} | {'충족' if c['minimumMet'] else '미충족'} |")
    lines += ["", "모의고사는 5세트 각각 모델링10+SQL40문항이 모두 통과해야 활성화된다. 예약 문항은 일반 연습에서 제외한다.", "",
              "| 세트 | 저술 | 통과 후보 모델링 | 통과 후보 SQL | 완성 |", "|---|---:|---:|---:|---|"]
    for s in mock_sets:
        lines.append(f"| {s['id']} | {s['authored']} | {s['model']} | {s['sql']} | {'충족' if s['complete'] else '미충족'} |")
    lines += ["", f"family 중복 그룹 {len(repeated_families)}개, practice/mock family 교집합 {len(overlap)}개, 동일 지문·SQL·입력·보기 그룹 {len(exact_duplicates)}개, 근접 중복 후보 {len(near_duplicates)}쌍이다. 자동 검사로 의미상 독립성을 확정할 수 없으며 후보는 수동 검토가 필요하다.", "",
              f"정답 배열 위치 분포: {dict(positions)}. 의미 ID 분포: {dict(answer_ids)}. 정답만 유일하게 긴 보기 비율 {bias['longestCorrectRate']:.1%}. 앱은 보기 순서를 세션 시작 시 섞고 저장한다.", ""]
    lines.extend(f"- 편향 검토: {warning}" for warning in bias["warnings"])
    lines += ["", f"독립 풀이 검수 증거는 당시 {review['reviewedSnapshotQuestions']}문항이다. 현재 원본 hash 그대로 {review['currentUnchanged']}개, 변경된 개정판 {review['currentChanged']}개다. 변경본에 기존 검수 통과를 자동 승계하지 않는다. 기존 증거는 보존했다.", "",
              f"현재 원본과 일치하는 검수 중 원래 보기 ID와 순서까지 가린 문항은 {review['currentWithMaskedChoiceIds']}개, 원래 ID가 보인 검수만 있는 문항은 {review['currentUnmaskedOnly']}개다. 초기20 및 B적용80은 원래 ID가 보였으므로 공통 정답 ID 추측의 한계가 있다. 중복 풀이 패스는 고유 문항 수로 중복 집계하지 않는다.", "",
              f"현재 해시와 일치하는 재검토 중 검토자의 이전 정답 노출이 명시된 문항은 {review['currentWithDeclaredPriorAnswerExposure']}개다. 정답을 본 뒤 보기 ID를 다시 가려 계산해도 최초 완전 blind 검토로 승격하지 않는다.", "",
              f"본문·정답·해설은 그대로이고 quarantined→published 상태만 바뀐 것으로 전체 객체 해시를 역산해 증명한 문항은 {review['currentWithVerifiedStatusOnlyChange']}개다. 이는 statusOnlyTransitions에 따로 기록한다. 내용이 변경된 뒤 실제 재독한 amendments를 포함하는 최종 집계는 evidence/content-review-summary.json을 참조한다.", "",
              "격리 및 경고 상세는 evidence/content-validation.json의 issues/quarantined, 재현 가능한 입력 hash는 inputs를 참조한다. SQL fixture는 저술자의 예상 결과이며 이 스크립트는 DBMS에 접속하거나 SQL을 실행하지 않는다.", ""]
    for item in report["quarantined"]:
        lines.append(f"- 격리 {item['id']}: {', '.join(item['reasons'])}")
    atomic_write(ROOT / "docs/coverage.md", "\n".join(lines) + "\n", False)
    print(json.dumps({"counts": report["counts"], "gates": report["gates"], "targets": report["targets"],
                      "errorCounts": dict(collections.Counter(i["code"] for i in v.issues if i["severity"] == "error")), "nearDuplicateCandidates": len(near_duplicates),
                      "asset": str(asset_path)}, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when any automatic structure or quantity gate is unmet")
    args = parser.parse_args()
    result = build()
    sys.exit(1 if args.strict and not all(result["gates"][k] for k in ["structurePassed", "objectiveMinimumsPassed", "quantitiesMet"]) else 0)
