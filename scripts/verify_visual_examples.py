"""Recalculate supplied visual examples without touching app/content/user data.

Inputs and depicted expected cells are bound to manifest plus both SVG and scene
text. SQLite correspondence queries do NOT verify Oracle syntax/semantics. Run:
    python scripts/verify_visual_examples.py

The default reads preserved sources shipped in content/visual-source and SVGs
in content/course-visuals (including the original V20, not its corrected copy).
An explicitly supplied --source may point to an extracted SQLD_27_Visuals folder
with data/manifest.json, data/scenes.json and the manifest's original SVG paths.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "content"


class SourceFiles:
    """Resolve either packaged preserved sources or an explicit original pack."""

    def __init__(self, base):
        self.base = Path(base).resolve()
        self.packaged = (self.base / "visual-source").is_dir()
        data_dir = self.base / ("visual-source" if self.packaged else "data")
        self.manifest = data_dir / "manifest.json"
        self.scenes = data_dir / "scenes.json"
        for path in (self.manifest, self.scenes):
            if not path.is_file():
                raise FileNotFoundError(f"Required preserved source is missing: {path}")

    def svg(self, n, entry):
        if self.packaged:
            directory = self.base / "course-visuals"
            if n == 20:
                # Original scenes include the original arrow label. Never silently
                # substitute the corrected app asset or weaken exact text binding.
                directory /= "originals"
            path = directory / f"visual-{n:02d}.svg"
        else:
            path = self.base / entry["svg"]
        path = path.resolve()
        if not path.is_relative_to(self.base):
            raise ValueError(f"SVG path escapes supplied source directory: {entry['svg']}")
        if not path.is_file():
            raise FileNotFoundError(f"Required original SVG is missing: {path}")
        return path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cell(value):
    return "NULL" if value is None else str(value)


def find_sequences(values, needle):
    return [i for i in range(len(values) - len(needle) + 1)
            if values[i:i + len(needle)] == needle]


def bag(rows):
    # Preserve duplicates, column order, NULL and numeric/string distinction.
    # Integer and float equality is suitable for these exact small averages.
    return Counter(tuple(row) for row in rows)


def ident(name):
    return '"' + name.replace('"', '""') + '"'


class Visual:
    def __init__(self, n, sources, manifest, scenes):
        self.n = n
        self.m = next(a for a in manifest if a["number"] == n)
        scene = next(a for a in scenes if a["number"] == n)
        self.scene = scene
        self.elements = [e for e in scene["elements"] if e["k"] == "text"]
        self.texts = [e["text"] for e in self.elements]
        self.scene_lines = [line for t in self.texts for line in t.splitlines()]
        self.svg_path = sources.svg(n, self.m)
        self.svg_lines = ["".join(e.itertext()) for e in ET.parse(self.svg_path).iter()
                          if e.tag.rsplit("}", 1)[-1] == "text"]
        assert self.scene_lines == self.svg_lines, f"visual {n}: scene/SVG text mismatch"
        self.bindings = []

    def table(self, index):
        table = self.m["source_tables"][index]
        sequence = table["headers"] + [cell(v) for row in table["rows"] for v in row]
        scene_matches = find_sequences(self.scene_lines, sequence)
        svg_matches = find_sequences(self.svg_lines, sequence)
        assert scene_matches and svg_matches, f"V{self.n} table{index}: cells not in artwork"
        self.bindings.append({
            "kind": "manifest_table_also_bound_to_artwork",
            "pointer": f"manifest[number={self.n}].source_tables[{index}]",
            "title": table["title"], "headers": table["headers"],
            "rows": table["rows"], "flatCellCountIncludingHeaders": len(sequence),
            "sceneFlatTextStartIndices": scene_matches,
            "svgTextStartIndices": svg_matches,
        })
        return table

    def text(self, value):
        assert value in self.texts, f"V{self.n}: missing scene text {value!r}"
        parts = value.splitlines()
        assert find_sequences(self.svg_lines, parts), f"V{self.n}: missing SVG text"
        i = self.texts.index(value)
        e = self.elements[i]
        self.bindings.append({"kind": "scene_text_also_bound_to_svg", "text": value,
                              "sceneTextIndex": i, "x": e["x"], "y": e["y"]})
        return value

    def matching(self, pattern):
        found = [t for t in self.texts if re.fullmatch(pattern, t)]
        assert len(found) == 1, (self.n, pattern, found)
        return self.text(found[0])

    def new_db(self, tables):
        db = sqlite3.connect(":memory:")
        for name, table in tables:
            columns = table["headers"]
            rows = table["rows"]
            # No type coercion: preserve input JSON integers/strings/nulls.
            db.execute(f"CREATE TABLE {ident(name)} ({','.join(ident(c) for c in columns)})")
            db.executemany(f"INSERT INTO {ident(name)} VALUES ({','.join('?' for _ in columns)})", rows)
        db.commit()
        return db


def run_checks(base):
    sources = SourceFiles(base)
    manifest = json.loads(sources.manifest.read_text("utf-8"))
    scenes = json.loads(sources.scenes.read_text("utf-8"))
    checks = []
    visual_sources = {}

    def visual(n):
        obj = Visual(n, sources, manifest, scenes)
        visual_sources[n] = obj
        return obj

    def check(v, name, db, sql, expected, *, classification="authored_sql_for_depicted_operation",
              source_sql=None, params=(), note="", extra=None):
        cursor = db.execute(sql, params)
        actual = [list(row) for row in cursor.fetchall()]
        expected = [list(row) for row in expected]
        passed = bag(actual) == bag(expected)
        item = {"visualNumber": v.n, "check": name, "engine": "SQLite",
                "engineVersion": sqlite3.sqlite_version, "sqlClassification": classification,
                "sourceSqlOrClause": source_sql, "executedSql": sql,
                "parameters": list(params), "expectedFromSource": expected,
                "actual": actual, "comparison": "unordered_multiset_including_duplicates_and_nulls",
                "passed": passed, "note": note}
        if extra:
            item["extraEvidence"] = extra
        checks.append(item)

    # Pilot 11: the Oracle NUMBER(1) statement is not executed as Oracle SQL.
    v = visual(11)
    before, after = v.table(0), v.table(1)
    source_sql = v.matching(r"ALTER TABLE .+ ADD .+ NUMBER\(1\);")
    db = v.new_db([("학생", before)])
    add_sql = "ALTER TABLE 학생 ADD COLUMN 학년 INTEGER"
    db.execute(add_sql)
    check(v, "ALTER retains both students and adds nullable grade", db,
          "SELECT 학번, 이름, 학년 FROM 학생", after["rows"],
          classification="sqlite_correspondence_not_oracle_original",
          source_sql=source_sql, extra={"executedSetupStatement": add_sql,
          "columnNames": [r[1] for r in db.execute('PRAGMA table_info("학생")')]},
          note="No DEFAULT or NOT NULL. NUMBER(1) precision and Oracle DDL commit behavior are not tested.")
    db.close()

    # 14 is deliberately separate from the existing course's member/order data.
    v = visual(14)
    left, right = v.table(0), v.table(1)
    clause = v.text("조건: L.학번 = R.학번")
    db = v.new_db([("L", left), ("R", right)])
    for kind, idx in [("LEFT", 2), ("RIGHT", 3), ("FULL", 4)]:
        expected = v.table(idx)
        check(v, kind + " OUTER JOIN matches depicted rows", db,
              f"SELECT L.이름, R.과목 FROM L {kind} OUTER JOIN R ON L.학번=R.학번",
              expected["rows"], source_sql=clause,
              note="Real SQLite LEFT/RIGHT/FULL syntax; only this supplied L/R dataset, no FK constraint, no extra WHERE.")
    db.close()

    v = visual(18)
    original, result = v.table(0), v.table(1)
    where = v.matching(r"① WHERE 점수 >= \d+").split("WHERE ", 1)[1]
    having = v.matching(r"③ HAVING COUNT\(\*\) >= \d+").split("HAVING ", 1)[1]
    v.text("② GROUP BY 과목")
    db = v.new_db([("점수표", original)])
    check(v, "WHERE then GROUP BY then HAVING", db,
          f"SELECT 과목, COUNT(*), AVG(점수) FROM 점수표 WHERE {where} GROUP BY 과목 HAVING {having}",
          result["rows"], source_sql=f"WHERE {where}; GROUP BY 과목; HAVING {having}")
    intermediate = []
    for i, text in enumerate(v.texts):
        if text.endswith(" 그룹"):
            v.text(text)
            stats = v.text(v.texts[i + 2])
            match = re.fullmatch(r"인원 (\d+)  /  평균 (\d+)", stats)
            assert match
            intermediate.append([text[:-3], int(match[1]), int(match[2])])
    check(v, "Intermediate groups before HAVING", db,
          f"SELECT 과목, COUNT(*), AVG(점수) FROM 점수표 WHERE {where} GROUP BY 과목",
          intermediate, note="Intermediate expected numbers are parsed from the actual scene labels, absent from manifest tables.")
    db.close()

    v = visual(12)
    original = v.table(0)
    db = v.new_db([("점수표", original)])
    expected = []
    for label, pattern in [("COUNT(*)", r"(\d+)줄"), ("COUNT(점수)", r"(\d+)개:.*"),
                           ("AVG(점수)", r".* = (\d+)")]:
        v.text(label)
        result_text = v.text(v.texts[v.texts.index(label) + 1])
        match = re.fullmatch(pattern, result_text)
        assert match
        expected.append(int(match[1]))
    check(v, "NULL excluded but zero included by COUNT(column) and AVG", db,
          "SELECT COUNT(*), COUNT(점수), AVG(점수) FROM 점수표", [expected],
          note="Oracle empty-string-to-NULL behavior is not tested in SQLite.")
    db.close()

    v = visual(13)
    left, right, result = v.table(0), v.table(1), v.table(2)
    v.text(v.m["warning"])
    db = v.new_db([("학생", left), ("수강", right)])
    check(v, "INNER JOIN repeats student for each matching course", db,
          "SELECT 학생.이름, 수강.과목 FROM 학생 JOIN 수강 ON 학생.학번=수강.학번",
          result["rows"], source_sql="학생.학번 = 수강.학번")
    db.close()

    v = visual(15)
    result = v.table(0)
    first = v.matching(r"R: 이름 열 1개 · 사람 \d+명")
    second = v.matching(r"S: 과목 열 1개 · 과목 \d+개")
    nr, ns = int(re.search(r"사람 (\d+)명", first)[1]), int(re.search(r"과목 (\d+)개", second)[1])
    start = v.texts.index(second) + 1
    names = [v.text(t) for t in v.texts[start:start + nr]]
    subjects = [v.text(t) for t in v.texts[start + nr:start + nr + ns]]
    db = v.new_db([("R", {"headers": ["이름"], "rows": [[x] for x in names]}),
                   ("S", {"headers": ["과목"], "rows": [[x] for x in subjects]})])
    check(v, "CROSS product from depicted people and subjects", db,
          "SELECT R.이름, S.과목 FROM R CROSS JOIN S", result["rows"],
          note="Inputs bound to person/subject scene labels; manifest contains only the result table.")
    db.close()

    v = visual(16)
    original, result = v.table(0), v.table(1)
    from_clause = v.text("FROM 사원 E JOIN 사원 M")
    on_clause = v.text("ON E.관리자번호 = M.사번")
    db = v.new_db([("사원", original)])
    check(v, "INNER SELF JOIN via manager number", db,
          f"SELECT E.이름, M.이름 {from_clause} {on_clause}", result["rows"],
          classification="original_from_on_fragment_with_authored_select",
          source_sql=f"{from_clause}\n{on_clause}")
    db.close()

    v = visual(17)
    original, total_result, department_result = v.table(0), v.table(1), v.table(2)
    db = v.new_db([("사원", original)])
    check(v, "Uncorrelated global AVG comparison", db,
          "SELECT 이름 FROM 사원 WHERE 점수 > (SELECT AVG(점수) FROM 사원)", total_result["rows"])
    check(v, "Correlated department AVG comparison", db,
          "SELECT E.이름 FROM 사원 E WHERE E.점수 > (SELECT AVG(I.점수) FROM 사원 I WHERE I.부서=E.부서)",
          department_result["rows"], note="Result semantics only, not proof of physical execution count/order.")
    global_mean = int(re.search(r"= (\d+)$", v.matching(r"\(.+\) ÷ \d+ = \d+"))[1])
    check(v, "Depicted overall average", db, "SELECT AVG(점수) FROM 사원", [[global_mean]])
    department_means = []
    for text in v.texts:
        match = re.fullmatch(r"(\S+) 평균 (\d+)", text)
        if match:
            v.text(text)
            department_means.append([match[1], int(match[2])])
    check(v, "Depicted department averages", db,
          "SELECT 부서, AVG(점수) FROM 사원 GROUP BY 부서", department_means)
    db.close()

    v19 = visual(19)
    sales_rows = []
    for text in v19.texts:
        for line in text.splitlines():
            match = re.fullmatch(r"(\S+): (\S+) (\d+) · (\S+) (\d+)", line)
            if match:
                v19.text(text)
                sales_rows += [[match[1], match[2], int(match[3])], [match[1], match[4], int(match[5])]]
    assert sales_rows, "Missing depicted detailed sales input"
    sales = {"headers": ["지역", "과목", "금액"], "rows": sales_rows}
    rollup_result = v19.table(0)
    original_sql = v19.matching(r"SELECT 지역, 과목, SUM\(금액\) FROM 매출 GROUP BY ROLLUP\(지역, 과목\);")
    db = v19.new_db([("매출", sales)])
    detail_sql = "SELECT 지역, 과목, SUM(금액) FROM 매출 GROUP BY 지역, 과목"
    region_sql = "SELECT 지역, NULL, SUM(금액) FROM 매출 GROUP BY 지역"
    subject_sql = "SELECT NULL, 과목, SUM(금액) FROM 매출 GROUP BY 과목"
    total_sql = "SELECT NULL, NULL, SUM(금액) FROM 매출"
    check(v19, "ROLLUP grouping-set correspondence", db,
          " UNION ALL ".join([detail_sql, region_sql, total_sql]), rollup_result["rows"],
          classification="sqlite_union_all_correspondence_not_original_rollup",
          source_sql=original_sql,
          note="ROLLUP syntax is not supported/executed here. Explicit grouping sets independently compute depicted 7 rows.")
    v20 = visual(20)
    cube_tables = [v20.table(i) for i in range(4)]
    v20.text(v20.m["memory"])
    check(v20, "CUBE grouping-set correspondence", db,
          " UNION ALL ".join([detail_sql, region_sql, subject_sql, total_sql]),
          [row for t in cube_tables for row in t["rows"]],
          classification="sqlite_union_all_correspondence_not_original_cube",
          source_sql=v20.m["memory"], note="Input is source-bound visual19 detail reused by visual20; CUBE syntax not executed.",
          extra={"inputVisualNumber": 19, "inputRows": sales_rows,
          "knownNonNumericIssue": "Original V20 lower arrow says region removed instead of subject; checked separately by visual audit."})
    db.close()

    v = visual(21)
    original, grouped, windowed = v.table(0), v.table(1), v.table(2)
    db = v.new_db([("점수표", original)])
    check(v, "GROUP BY comparison", db, "SELECT 과목, AVG(점수) FROM 점수표 GROUP BY 과목", grouped["rows"])
    window_clause = "AVG(점수) OVER(PARTITION BY 과목)"
    v.matching(r"AVG\(점수\) OVER\(PARTITION BY 과목\) → 4줄")
    check(v, "Window AVG retains each depicted student row", db,
          f"SELECT 이름, 과목, 점수, {window_clause} FROM 점수표", windowed["rows"],
          classification="original_window_expression_with_authored_select", source_sql=window_clause,
          note="V21 has 장정훈100; V18 has 장정훈60. Independent source inputs, not one pipeline.")
    db.close()

    v = visual(22)
    whole = v.table(0)
    original = {"headers": whole["headers"][:3], "rows": [r[:3] for r in whole["rows"]]}
    v.text(v.m["warning"])
    db = v.new_db([("학생", original)])
    check(v, "RANK DENSE_RANK ROW_NUMBER with separate tie rules", db,
          "SELECT 학번, 이름, 점수, RANK() OVER(ORDER BY 점수 DESC), "
          "DENSE_RANK() OVER(ORDER BY 점수 DESC), ROW_NUMBER() OVER(ORDER BY 점수 DESC, 학번 ASC) FROM 학생",
          whole["rows"], source_sql=v.m["warning"],
          note="Input uses only source first three columns; calculated ranking columns compared with depicted last three.")
    db.close()

    v = visual(24)
    vertical, horizontal = v.table(0), v.table(1)
    subjects = horizontal["headers"][1:]
    db = v.new_db([("성적", vertical)])
    expressions = [f"SUM(CASE WHEN 과목=? THEN 점수 END) AS {ident(subject)}" for subject in subjects]
    pivot_sql = f"SELECT 이름, {', '.join(expressions)} FROM 성적 GROUP BY 이름"
    check(v, "PIVOT correspondence with conditional aggregation", db, pivot_sql,
          horizontal["rows"], classification="sqlite_case_aggregate_correspondence_not_original_pivot",
          params=subjects, note="No PIVOT keyword executed. Supplied (name,subject) uniqueness and no NULL cells limit this fixture.")
    db.close()
    db = v.new_db([("가로표", horizontal)])
    unpivot_sql = " UNION ALL ".join(f"SELECT 이름, ?, {ident(s)} FROM 가로표" for s in subjects)
    check(v, "UNPIVOT correspondence for non-NULL unique cells", db, unpivot_sql,
          vertical["rows"], classification="sqlite_union_all_correspondence_not_original_unpivot",
          params=subjects, note="Oracle/SQL Server UNPIVOT syntax and NULL-inclusion defaults are not executed/tested.")
    db.close()

    # Four independent V27 panels. Do not merge JOIN enrolment with division.
    v = visual(27)
    selection_input, selection_result = v.table(0), v.table(1)
    condition = v.matching(r"학과 = \S+")
    dept = condition.split("=", 1)[1].strip()
    db = v.new_db([("학생", selection_input)])
    check(v, "Relational selection sigma", db,
          "SELECT 이름, 학과 FROM 학생 WHERE 학과=?", selection_result["rows"], params=[dept],
          source_sql=condition, classification="sql_correspondence_for_relational_algebra")
    db.close()
    projection_input, projection_result = v.table(2), v.table(3)
    db = v.new_db([("학생", projection_input)])
    check(v, "Set projection pi removes duplicate departments", db,
          "SELECT DISTINCT 학과 FROM 학생", projection_result["rows"],
          classification="sql_distinct_correspondence_for_relational_projection")
    column_index = projection_input["headers"].index(projection_result["headers"][0])
    bag_expected = [[r[column_index]] for r in projection_input["rows"]]
    check(v, "SQL SELECT without DISTINCT retains source multiplicity", db,
          "SELECT 학과 FROM 학생", bag_expected,
          note="Expected bag is the source input's department column; compared with distinct projection in separate check.")
    db.close()
    join_left, join_right = v.table(4), v.table(5)
    join_result_text = v.matching(r"\d+ \S+–\S+   /   \d+ \S+–\S+")
    join_result = [[int(m[0]), m[1], m[2]] for m in re.findall(r"(\d+) (\S+)–(\S+)", join_result_text)]
    db = v.new_db([("학생", join_left), ("수강", join_right)])
    check(v, "Relational join panel via student identifier", db,
          "SELECT 학생.학번, 학생.이름, 수강.과목 FROM 학생 JOIN 수강 ON 학생.학번=수강.학번",
          join_result, classification="sql_correspondence_for_relational_algebra")
    db.close()
    division = v.table(6)
    criterion = v.matching(r"기준: \S+ · \S+")
    required = criterion.split(": ", 1)[1].split(" · ")
    # Result labels are at the right side of the lower-right division panel.
    answer_elements = [e for e in v.elements if e["x"] >= 1300 and 630 <= e["y"] <= 750
                       and set(e["text"].splitlines()) <= {r[0] for r in division["rows"]}]
    assert answer_elements, "Division result artwork layout changed: review binding"
    division_expected = [[line] for e in answer_elements for line in v.text(e["text"]).splitlines()]
    people = {"headers": ["person_id", "label"],
              "rows": [[i + 1, r[0]] for i, r in enumerate(division["rows"])]}
    enrolment = {"headers": ["person_id", "subject"], "rows": []}
    for person_id, row in enumerate(division["rows"], 1):
        for subject, flag in zip(division["headers"][1:], row[1:]):
            assert flag in ("O", "X")
            if flag == "O":
                enrolment["rows"].append([person_id, subject])
    db = v.new_db([("people", people), ("enrolment", enrolment),
                   ("required", {"headers": ["subject"], "rows": [[s] for s in required]})])
    check(v, "Relational division requires all depicted courses", db,
          "SELECT p.label FROM people p WHERE NOT EXISTS (SELECT 1 FROM required r "
          "WHERE NOT EXISTS (SELECT 1 FROM enrolment e WHERE e.person_id=p.person_id AND e.subject=r.subject))",
          division_expected, classification="sql_double_not_exists_correspondence_for_relational_division",
          note="Local fixture row IDs represent depicted people, not names as join keys. This panel has its own O/X input; JOIN panel not reused.",
          extra={"inputMatrix": division, "derivedEnrolmentRows": enrolment["rows"], "requiredSubjects": required})
    db.close()

    references = [
        {"url": "https://sqlite.org/lang_select.html", "sections": "2.1 FROM/joins; WHERE; aggregate query; DISTINCT",
         "readDate": "2026-09-29", "type": "primary_documentation_read", "note": "NULL extension and row/group filtering; initial www URL timed out, canonical non-www fetch succeeded."},
        {"url": "https://www.sqlite.org/lang_aggfunc.html", "sections": "avg(X), count(X), count(*), sum(X)",
         "readDate": "2026-09-29", "type": "primary_documentation_read", "note": "COUNT(column) and AVG exclude NULL; COUNT(*) counts rows."},
        {"url": "https://www.sqlite.org/lang_altertable.html", "sections": "4 ADD COLUMN",
         "readDate": "2026-09-29", "type": "primary_documentation_read", "note": "SQLite ADD COLUMN limitations; does not establish Oracle data type behavior."},
        {"url": "https://www.sqlite.org/windowfunctions.html", "sections": "row_number, rank, dense_rank and output ordering",
         "readDate": "2026-09-29", "type": "primary_documentation_read", "note": "Peer ranking and independent window/output ordering."},
        {"url": "https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/ALTER-TABLE.html",
         "sections": "add_column_clause / DEFAULT", "readDate": "2026-09-29", "type": "primary_documentation_read_not_engine_execution",
         "note": "Read nullable column/default restrictions; Oracle engine and NUMBER precision were not exercised."},
        {"url": "https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/SELECT.html",
         "sections": "ROLLUP / CUBE / GROUPING SETS", "readDate": "2026-09-29", "type": "primary_documentation_read_not_engine_execution",
         "note": "Grouping combinations support the correspondence fixture; Oracle syntax was not executed."},
    ]
    return {
        "schemaVersion": 1, "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "engine": {"name": "SQLite", "version": sqlite3.sqlite_version, "pythonVersion": sys.version,
                   "database": ":memory:", "oracleExecuted": False, "sqlServerExecuted": False},
        "scope": "Recalculate depicted original visual data/results; not application SQL execution, human review or efficacy proof.",
        "source": {"directory": str(sources.base),
                   "layout": "packaged_preserved_sources" if sources.packaged else "original_extracted_pack",
                   "manifest": sources.manifest.relative_to(sources.base).as_posix(),
                   "scenes": sources.scenes.relative_to(sources.base).as_posix(),
                   "manifestSha256": digest(sources.manifest), "scenesSha256": digest(sources.scenes)},
        "summary": {"checks": len(checks), "passed": sum(c["passed"] for c in checks),
                    "failed": sum(not c["passed"] for c in checks),
                    "visualNumbers": sorted(visual_sources)},
        "checks": checks,
        "sourceBindings": [{"visualNumber": n, "svg": v.svg_path.relative_to(sources.base).as_posix(),
                            "originalManifestSvg": v.m["svg"], "svgSha256": digest(v.svg_path),
                            "sceneAndSvgTextsEqual": True, "bindings": v.bindings}
                           for n, v in sorted(visual_sources.items())],
        "notVerified": [
            "Oracle/SQL Server execution, NUMBER(1) precision, Oracle implicit DDL commit and empty-string NULL rules.",
            "Oracle ROLLUP/CUBE/PIVOT/UNPIVOT/CONNECT BY syntax: numeric correspondences do not validate native grammar.",
            "V23 hierarchy, V25 transaction flow/SAVEPOINT and V26 GRANT/REVOKE are visual/document reviews; not engine checks in this script.",
            "V1-10 are not part of this numerical/SQL execution script; this does not mark them reviewed or invalid.",
            "PNG pixel OCR is not performed by this script; separate recorded visual inspection checked rendered PNGs.",
            "Narrative clarity, UI accessibility and learning effect are not proven by these result comparisons.",
            "Unordered bag comparisons do not assert an output order when artwork has no final ORDER BY.",
        ],
        "documentationConsultedAtImplementation": references,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/visuals-example-checks.json")
    args = parser.parse_args()
    report = run_checks(args.source.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 1 if report["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
