"""Validate the separate lesson pack and optional isolated SQLite evidence.

No supplied Python/JS/scripts are executed. SQL is restricted to an in-memory
database, with no ATTACH, PRAGMA, extension loading, file functions or network.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evidence/course-content-fixtures.json"
EXPECTED = {"lessons": 63, "concepts": 490, "examples": 95, "selfChecks": 189,
            "tables": 223, "sqlBlocks": 70, "diagrams": 63, "lectureMinutes": 1932}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(values, description):
    require(len(values) == len(set(values)), f"Duplicate {description}")


def text(value, description, allow_empty=False):
    require(isinstance(value, str) and (allow_empty or bool(value.strip())), f"Invalid text {description}")
    require("\x00" not in value and "\ufffd" not in value, f"Invalid character {description}")


def validate_svg(svg):
    require(isinstance(svg, str) and 0 < len(svg) < 200_000, "Invalid SVG size")
    require(not re.search(r"<!DOCTYPE|<!ENTITY|<\?", svg, re.I), "SVG declarations are forbidden")
    root = ET.fromstring(svg)
    ns = "{http://www.w3.org/2000/svg}"
    require(root.tag == ns + "svg", "Missing SVG root namespace")
    allowed = {"svg", "defs", "marker", "rect", "path", "text", "tspan", "g", "circle", "ellipse", "line", "polyline", "polygon", "title", "desc"}
    for element in root.iter():
        require(element.tag.startswith(ns) and element.tag[len(ns):] in allowed, f"Unsafe SVG element {element.tag}")
        for name, value in element.attrib.items():
            local = name.split("}")[-1].lower()
            require(not local.startswith("on") and local not in {"style", "href", "src"}, f"Unsafe SVG attribute {name}")
            require("javascript:" not in value.lower() and "data:" not in value.lower(), "Unsafe SVG URL")
            urls = re.findall(r"url\((.*?)\)", value, re.I)
            require(all(re.fullmatch(r"#[A-Za-z0-9_-]+", url) for url in urls), "External SVG reference")
    require("…" not in "".join(root.itertext()), "Truncated SVG caption")


def validate_table(table):
    require(set(table) == {"title", "columns", "rows"}, "Unknown/missing table field")
    text(table["title"], "table title")
    require(isinstance(table["columns"], list) and len(table["columns"]) > 0, "Empty table columns")
    for column in table["columns"]:
        text(column, "table column")
    unique(table["columns"], "table column")
    require(isinstance(table["rows"], list), "Invalid rows")
    for row in table["rows"]:
        require(isinstance(row, list) and len(row) == len(table["columns"]), "Ragged table")
        for value in row:
            require(value is None or isinstance(value, str), "Table cells must be strings or null")


def validate_pack(pack, main_pack=None, exact_counts=True):
    from import_course import counts
    require(set(pack) == {"schemaVersion", "version", "title", "parts", "lessons", "sources", "provenance", "reviewNote"}, "Pack fields mismatch")
    require(pack["schemaVersion"] == 1, "Unsupported course schema")
    for key in ("version", "title", "provenance", "reviewNote"):
        text(pack[key], key)
    part_ids = [p["id"] for p in pack["parts"]]
    source_ids = [s["id"] for s in pack["sources"]]
    lesson_ids = [l["id"] for l in pack["lessons"]]
    unique(part_ids, "part id")
    unique(source_ids, "source id")
    unique(lesson_ids, "lesson id")
    require(part_ids == ["1-1", "1-2", "2-1", "2-2", "2-3"], "Unexpected part order")
    for part in pack["parts"]:
        require(set(part) == {"id", "title"}, "Part fields mismatch")
        text(part["title"], "part title")
    for source in pack["sources"]:
        require(set(source) == {"id", "title", "url"}, "Source fields mismatch")
        text(source["title"], "source title")
        require(re.match(r"^https://[^/\s]+/[^\s]*$", source["url"]), "Source must be an HTTPS reference")
    if main_pack is None:
        main_pack = json.loads((ROOT / "app/src/main/assets/content-pack.json").read_text(encoding="utf-8"))
    note_ids = {n["id"] for n in main_pack["notes"]}
    expected_lesson_fields = {"id", "partId", "number", "title", "lectureMinutes", "easy", "why", "concepts", "examples", "memory", "traps", "selfChecks", "relatedNoteIds", "sourceIds", "bridge", "diagramSvg", "version"}
    example_ids, check_ids = [], []
    for lesson in pack["lessons"]:
        lid = lesson["id"]
        require(set(lesson) == expected_lesson_fields, f"Lesson fields mismatch {lid}")
        require(lesson["partId"] in part_ids and lid == lesson["partId"] + f'-{lesson["number"]:02}', f"Invalid lesson key {lid}")
        require(type(lesson["lectureMinutes"]) is int and lesson["lectureMinutes"] > 0, f"Invalid minutes {lid}")
        require(type(lesson["version"]) is int and lesson["version"] > 0, f"Invalid version {lid}")
        for key in ("title", "easy", "why", "memory", "bridge"):
            text(lesson[key], lid + "." + key)
        for key, allowed in (("relatedNoteIds", note_ids), ("sourceIds", set(source_ids))):
            require(lesson[key] and all(ref in allowed for ref in lesson[key]), f"Unknown reference {lid}.{key}")
            unique(lesson[key], lid + "." + key)
        require(lesson["concepts"] and lesson["examples"] and lesson["traps"], f"Missing lesson content {lid}")
        for concept in lesson["concepts"]:
            require(set(concept) == {"term", "meaning", "example"}, "Concept fields mismatch")
            for key, value in concept.items():
                text(value, lid + ".concept." + key)
        for trap in lesson["traps"]:
            text(trap, lid + ".trap")
        for example in lesson["examples"]:
            eid = example["id"]
            example_ids.append(eid)
            require(set(example) == {"id", "title", "question", "tables", "sql", "steps", "results", "mode", "verification"}, f"Example fields mismatch {eid}")
            require(re.fullmatch(re.escape(lid) + r"-E\d{2}", eid), f"Invalid example id {eid}")
            require(example["mode"] in {"theory", "sqlite", "oracle"}, f"Invalid mode {eid}")
            for key in ("title", "question", "verification"):
                text(example[key], eid + "." + key)
            text(example["sql"], eid + ".sql", allow_empty=True)
            require(example["steps"] and example["results"], f"Missing example explanation/result {eid}")
            for step in example["steps"]:
                text(step, eid + ".step")
            for table in example["tables"] + example["results"]:
                validate_table(table)
        require(len(lesson["selfChecks"]) == 3, f"Expected 3 self-checks {lid}")
        for i, check in enumerate(lesson["selfChecks"]):
            require(set(check) == {"id", "question", "answer", "explanation"}, "Self-check fields mismatch")
            require(check["id"] == lid + f"-Q{i + 1}", "Changed self-check stable id")
            check_ids.append(check["id"])
            for key in ("question", "answer", "explanation"):
                text(check[key], check["id"] + "." + key)
        validate_svg(lesson["diagramSvg"])
    unique(example_ids, "example id")
    unique(check_ids, "self-check id")
    actual = counts(pack)
    if exact_counts:
        require(actual == EXPECTED, f"Content count mismatch: {actual}")
        for part, count in zip(part_ids, [9, 7, 25, 18, 4]):
            require([l["number"] for l in pack["lessons"] if l["partId"] == part] == list(range(1, count + 1)), "Lecture sequence mismatch")
    return actual


def statements(sql):
    pending = ""
    for character in sql:
        pending += character
        if character == ";" and sqlite3.complete_statement(pending):
            yield pending.strip()
            pending = ""
    if pending.strip():
        require(sqlite3.complete_statement(pending + ";"), "Incomplete SQL statement")
        yield pending.strip()


def quote_identifier(identifier):
    require(isinstance(identifier, str) and identifier and "\x00" not in identifier, "Invalid identifier")
    return '"' + identifier.replace('"', '""') + '"'


def canonical_row(row):
    return tuple(("number", Decimal(str(v)).normalize()) if type(v) in (int, float)
                 else ("null", "") if v is None else ("text", v) for v in row)


def outer_ordered(sql):
    # Ignore quoted strings/identifiers and ORDER BY inside OVER/subqueries.
    clean = re.sub(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"", " ", sql)
    depth = 0
    top = []
    for char in clean:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif depth == 0:
            top.append(char)
    return bool(re.search(r"\bORDER\s+BY\b", "".join(top), re.I))


def execute_fixture(fixture):
    require(fixture["mode"] in {"direct", "equivalent"}, "Invalid fixture mode")
    require(len(fixture["sql"]) < 100_000, "Oversize SQL fixture")
    conn = sqlite3.connect(":memory:")
    try:
        conn.enable_load_extension(False)
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 2_000_000)
        conn.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 100_000)
        conn.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, 0)
        for table in fixture["tables"]:
            # Recreate data types from literal JSON values, not source setup SQL.
            types = []
            for col in range(len(table["columns"])):
                values = [row[col] for row in table["rows"] if row[col] is not None]
                types.append("" if not values else "NUMERIC" if all(type(v) in (int, float) for v in values) else "TEXT")
            definitions = ",".join(quote_identifier(c) + " " + t for c, t in zip(table["columns"], types))
            conn.execute(f"CREATE TABLE {quote_identifier(table['name'])} ({definitions})")
            placeholders = ",".join("?" for _ in table["columns"])
            conn.executemany(f"INSERT INTO {quote_identifier(table['name'])} VALUES ({placeholders})", table["rows"])
        conn.commit()
        safe_functions = {"count", "sum", "avg", "min", "max", "round", "upper", "substr", "length", "coalesce", "nullif", "rank", "dense_rank", "row_number", "lag", "lead", "last_value", "cume_dist", "printf", "regexp", "like"}
        forbidden = {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH, sqlite3.SQLITE_PRAGMA,
                     sqlite3.SQLITE_DROP_TABLE, sqlite3.SQLITE_DROP_VIEW, sqlite3.SQLITE_ALTER_TABLE,
                     sqlite3.SQLITE_CREATE_VTABLE, sqlite3.SQLITE_CREATE_TRIGGER, sqlite3.SQLITE_CREATE_TEMP_TRIGGER}
        def authorize(action, arg1, arg2, database, trigger):
            if action in forbidden:
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_FUNCTION and (arg2 or arg1 or "").lower() not in safe_functions:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        conn.set_authorizer(authorize)
        remaining = [1_000]
        def progress():
            remaining[0] -= 1
            return int(remaining[0] <= 0)
        conn.set_progress_handler(progress, 1_000)
        def regexp(pattern, value):
            require(pattern == "^(DB|JAVA)$", "Only the reviewed literal regex fixture is enabled")
            return None if value is None else int(re.search(pattern, value) is not None)
        conn.create_function("regexp", 2, regexp)
        outputs = []
        for statement in statements(fixture["sql"]):
            require(re.match(r"^(SELECT\b|WITH\b|INSERT\s+INTO\b|UPDATE\b|DELETE\s+FROM\b|CREATE\s+VIEW\b|BEGIN\b|SAVEPOINT\b|ROLLBACK\b|COMMIT\b)", statement, re.I), "SQL statement not allowed")
            cursor = conn.execute(statement)
            if cursor.description is not None:
                rows = cursor.fetchmany(10_001)
                require(len(rows) <= 10_000, "Too many SQL result rows")
                outputs.append((statement, len(cursor.description), rows))
        require(len(outputs) == len(fixture["results"]), "SQL result table count mismatch")
        comparisons = []
        for (statement, columns, actual), expected in zip(outputs, fixture["results"]):
            require(columns == len(expected["columns"]), "SQL result column count mismatch")
            a, b = [canonical_row(row) for row in actual], [canonical_row(row) for row in expected["rows"]]
            ordered = outer_ordered(statement)
            require(a == b if ordered else Counter(a) == Counter(b), f"SQL result mismatch {fixture['id']}: actual={actual!r}; expected={expected['rows']!r}")
            comparisons.append({"rows": len(actual), "columns": columns, "comparison": "ordered" if ordered else "multiset"})
        return {"id": fixture["id"], "mode": fixture["mode"], "status": "pass", "comparisons": comparisons}
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", action="store_true", help="Run committed isolated SQLite fixtures")
    parser.add_argument("--sync-asset", action="store_true", help="Copy validated source bytes to app asset")
    args = parser.parse_args()
    source_path = ROOT / "content/course-pack.json"
    asset_path = ROOT / "app/src/main/assets/course-pack.json"
    pack = json.loads(source_path.read_text(encoding="utf-8"))
    report = {"status": "pass", "counts": validate_pack(pack),
              "sourceSha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
              "limitations": ["No human expert review", "No Oracle or SQL Server engine execution", "No official exam provenance", "Self-checks are not scored exam items"]}
    if args.engine:
        fixture_pack = json.loads(FIXTURES.read_text(encoding="utf-8"))
        by_id = {e["id"]: e for l in pack["lessons"] for e in l["examples"]}
        fixtures = fixture_pack["fixtures"]
        unique([f["id"] for f in fixtures], "fixture id")
        from import_course import table
        for fixture in fixtures:
            example = by_id[fixture["id"]]
            require([table(t) for t in fixture["tables"]] == example["tables"], "Fixture input differs from app content")
            require([table(t) for t in fixture["results"]] == example["results"], "Fixture result differs from app content")
            require(fixture["displaySql"] == example["sql"], "Fixture displayed SQL differs from app content")
            if fixture["mode"] == "direct":
                require(fixture["sql"] == example["sql"], "Direct execution must use exact displayed SQL")
        results = [execute_fixture(f) for f in fixtures]
        report["sqlite"] = {"version": sqlite3.sqlite_version, "direct": sum(r["mode"] == "direct" for r in results),
                            "equivalent": sum(r["mode"] == "equivalent" for r in results),
                            "notExecuted": len(by_id) - len(results), "results": results}
        require(report["sqlite"]["direct"] == 50 and report["sqlite"]["equivalent"] == 10, "Unexpected engine coverage")
    if args.sync_asset:
        asset_path.write_bytes(source_path.read_bytes())
    require(asset_path.read_bytes() == source_path.read_bytes(), "Course asset differs from validated source")
    output = ROOT / ("evidence/course-content-engine.json" if args.engine else "evidence/course-content-validation.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "sqlite"}, ensure_ascii=False))
    if "sqlite" in report:
        print(json.dumps({key: value for key, value in report["sqlite"].items() if key != "results"}))


if __name__ == "__main__":
    main()
