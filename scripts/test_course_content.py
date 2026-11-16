"""Meaningful failure-path checks for the imported course content pipeline."""
import copy
import json
from pathlib import Path
import sqlite3
import unittest

from import_course import DEFAULT_INPUT, EXPECTED_COUNTS, normalized, table
from validate_course import ROOT, execute_fixture, outer_ordered, validate_pack, validate_svg


# This is an independently reviewed allowlist, not loaded from the correction
# document under test.  A future edit must explicitly revise this contract.
TEXT_CORRECTIONS = [
    {
        "path": "lessons[1-1-06].easy",
        "before": "업무에서 계속 정보를 관리할 대상의 종류다. “학생”은 엔터티, “학번 1001인 유성재”은 그 엔터티의 한 사례다.",
        "after": "업무에서 계속 정보를 관리할 대상의 종류다. “학생”은 엔터티, “학번 1001인 유성재”는 그 엔터티의 한 사례다.",
        "kind": "korean_particle",
    },
    {
        "path": "lessons[2-1-25].examples[2-1-25-E02].steps[0]",
        "before": "코드는 둘 다 1이지만 이름은 박강열과 박보성로 다르다.",
        "after": "코드는 둘 다 1이지만 이름은 박강열과 박보성으로 다르다.",
        "kind": "korean_particle",
    },
]
DIVISION_BEFORE = {
    "id": "2-3-04-E02",
    "title": "디비전은 모두 갖춘 사람 찾기",
    "question": "필수과목 DB와 JAVA를 모두 들은 학생은?",
    "tables": [
        {"title": "수강", "columns": ["이름", "과목"], "rows": [
            ["박상현", "DB"], ["박상현", "JAVA"], ["박상현", "Python"],
            ["양선규", "DB"], ["김현수", "DB"], ["김현수", "JAVA"], ["유성재", "JAVA"]]},
        {"title": "필수", "columns": ["과목"], "rows": [["DB"], ["JAVA"]]},
    ],
    "sql": "SELECT DISTINCT r.이름 FROM 수강 r WHERE NOT EXISTS (SELECT 1 FROM 필수 f WHERE NOT EXISTS (SELECT 1 FROM 수강 r2 WHERE r2.이름=r.이름 AND r2.과목=f.과목));",
    "steps": [
        "박상현은 DB·JAVA 둘 다 있으므로 통과한다. Python 추가 수강은 방해하지 않는다.",
        "양선규는 JAVA가 없고 유성재는 DB가 없어 탈락한다.",
        "김현수는 DB·JAVA가 모두 있어 통과한다. 결과는 박상현·김현수 두 이름이다.",
    ],
    "results": [{"title": "디비전 결과", "columns": ["이름"], "rows": [["박상현"], ["김현수"]]}],
    "mode": "sqlite",
    "verification": "SQLite용 예제 · 원자료는 직접 실행 확인으로 기록했습니다. 앱에서는 실행하지 않습니다.",
}
DIVISION_AFTER = copy.deepcopy(DIVISION_BEFORE)
DIVISION_AFTER["tables"][0] = {
    "title": "수강", "columns": ["학번", "이름", "과목"], "rows": [
        ["1001", "박상현", "DB"], ["1001", "박상현", "JAVA"], ["1001", "박상현", "Python"],
        ["1002", "양선규", "DB"], ["1003", "김현수", "DB"], ["1003", "김현수", "JAVA"],
        ["1004", "유성재", "JAVA"]],
}
DIVISION_AFTER["sql"] = "SELECT DISTINCT r.이름 FROM 수강 r WHERE NOT EXISTS (SELECT 1 FROM 필수 f WHERE NOT EXISTS (SELECT 1 FROM 수강 r2 WHERE r2.학번=r.학번 AND r2.과목=f.과목));"
DIVISION_AFTER["steps"] = [
    "학번 1001인 박상현의 수강은 DB·JAVA·Python이다. 필수 DB·JAVA가 모두 있어 통과하고, 추가 과목 Python은 방해하지 않는다.",
    "학번 1002인 양선규는 JAVA가 없고, 학번 1004인 유성재는 DB가 없어 탈락한다.",
    "학번 1003인 김현수도 DB·JAVA가 모두 있어 통과한다. 결과의 이름은 박상현·김현수이며 원래 예제와 같다.",
    "안쪽 r2.학번=r.학번으로 같은 학생을 연결하고 이름은 출력에만 사용한다. 이 예시의 이름은 서로 다르다. 동명이인까지 별도로 표시하려면 SELECT DISTINCT r.학번, r.이름처럼 식별자도 출력한다.",
]


class CourseContentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / "content/course-pack.json").read_text(encoding="utf-8"))
        cls.fixtures = json.loads((ROOT / "evidence/course-content-fixtures.json").read_text(encoding="utf-8"))["fixtures"]

    def reviewed_import(self, imported):
        """Permit exactly two prose fixes, one identified example and versions.

        Start with every original field; the final whole-object equality still
        detects any removal, addition or unreviewed edit anywhere in the course.
        """
        expected = copy.deepcopy(imported)
        lessons = {lesson["id"]: lesson for lesson in expected["lessons"]}
        self.assertEqual("course-2026-09-28.1", expected["version"])
        self.assertEqual(TEXT_CORRECTIONS[0]["before"], lessons["1-1-06"]["easy"])
        lessons["1-1-06"]["easy"] = TEXT_CORRECTIONS[0]["after"]
        natural = next(e for e in lessons["2-1-25"]["examples"] if e["id"] == "2-1-25-E02")
        self.assertEqual(TEXT_CORRECTIONS[1]["before"], natural["steps"][0])
        natural["steps"][0] = TEXT_CORRECTIONS[1]["after"]
        algebra = lessons["2-3-04"]
        position = next(i for i, e in enumerate(algebra["examples"]) if e["id"] == DIVISION_BEFORE["id"])
        self.assertEqual(DIVISION_BEFORE, algebra["examples"][position])
        algebra["examples"][position] = copy.deepcopy(DIVISION_AFTER)
        self.assertEqual(1, algebra["version"])
        algebra["version"] = 2
        expected["version"] = "2026.09.29.1"
        return expected

    def test_full_pack_counts_and_asset_match(self):
        self.assertEqual(EXPECTED_COUNTS, validate_pack(self.pack))
        self.assertEqual((ROOT / "content/course-pack.json").read_bytes(),
                         (ROOT / "app/src/main/assets/course-pack.json").read_bytes())

    def test_all_existing_notes_remain_reachable(self):
        main = json.loads((ROOT / "app/src/main/assets/content-pack.json").read_text(encoding="utf-8"))
        self.assertEqual({n["id"] for n in main["notes"]},
                         {n for lesson in self.pack["lessons"] for n in lesson["relatedNoteIds"]})

    def test_source_import_is_reproducible_and_read_only(self):
        if not DEFAULT_INPUT.exists():
            self.skipTest("Original supplied archive is not part of source distribution")
        source = DEFAULT_INPUT / "data/content.json"
        before = source.read_bytes()
        actual, report = normalized(DEFAULT_INPUT)
        self.assertEqual(self.pack, self.reviewed_import(actual))
        self.assertEqual(before, source.read_bytes())
        self.assertFalse(report["sourceFilesModified"])

    def test_every_table_and_sql_block_retained(self):
        if not DEFAULT_INPUT.exists():
            self.skipTest("Original supplied archive is not part of source distribution")
        raw = json.loads((DEFAULT_INPUT / "data/content.json").read_text(encoding="utf-8"))
        original = {e["id"]: e for lesson in raw["lessons"] for e in lesson["examples"]}
        for lesson in self.pack["lessons"]:
            for example in lesson["examples"]:
                with self.subTest(example=example["id"]):
                    before = original[example["id"]]
                    if example["id"] == DIVISION_BEFORE["id"]:
                        # Validate both sides against fixed reviewed values;
                        # never skip all comparisons for a corrected example.
                        self.assertEqual(DIVISION_BEFORE["sql"], before["sql"])
                        self.assertEqual(DIVISION_BEFORE["tables"], [table(t) for t in before["tables"]])
                        self.assertEqual(DIVISION_AFTER["sql"], example["sql"])
                        self.assertEqual(DIVISION_AFTER["tables"], example["tables"])
                    else:
                        self.assertEqual(before["sql"], example["sql"])
                        self.assertEqual([table(t) for t in before["tables"]], example["tables"])
                    self.assertEqual([table(t) for t in before["results"]], example["results"])

    def test_exact_reviewed_correction_document_and_display_match(self):
        correction = json.loads((ROOT / "content/course-visual-corrections.json").read_text(encoding="utf-8"))
        self.assertEqual((1, "applied", "2-3-04", "2-3-04-E02"), tuple(
            correction[key] for key in ("schemaVersion", "status", "lessonId", "exampleId")))
        self.assertEqual(DIVISION_BEFORE, correction["before"])
        self.assertEqual(DIVISION_AFTER, correction["after"])
        self.assertEqual(["tables[0].columns", "tables[0].rows", "sql", "steps"],
                         [change["path"] for change in correction["changes"]])
        self.assertEqual(TEXT_CORRECTIONS, [
            {key: change[key] for key in ("path", "before", "after", "kind")}
            for change in correction["otherTextCorrections"]])
        lessons = {lesson["id"]: lesson for lesson in self.pack["lessons"]}
        self.assertEqual(TEXT_CORRECTIONS[0]["after"], lessons["1-1-06"]["easy"])
        natural = next(e for e in lessons["2-1-25"]["examples"] if e["id"] == "2-1-25-E02")
        self.assertEqual(TEXT_CORRECTIONS[1]["after"], natural["steps"][0])
        division = next(e for e in lessons["2-3-04"]["examples"] if e["id"] == DIVISION_AFTER["id"])
        self.assertEqual(DIVISION_AFTER, division)
        self.assertEqual(2, lessons["2-3-04"]["version"])

    def test_division_execution_fixture_matches_display_sql_and_tables(self):
        example = next(e for lesson in self.pack["lessons"] for e in lesson["examples"]
                       if e["id"] == DIVISION_AFTER["id"])
        fixture = next(f for f in self.fixtures if f["id"] == example["id"])
        self.assertEqual("direct", fixture["mode"])
        self.assertEqual(example["sql"], fixture["sql"])
        self.assertEqual(example["sql"], fixture["displaySql"])
        self.assertEqual(example["tables"], [table(t) for t in fixture["tables"]])
        self.assertEqual(example["results"], [table(t) for t in fixture["results"]])

    def test_division_does_not_merge_two_students_with_the_same_name(self):
        fixture = copy.deepcopy(next(f for f in self.fixtures if f["id"] == DIVISION_AFTER["id"]))
        fixture["id"] = "division-homonym-regression"
        # Each Park lacks a different required course.  Neither qualifies.
        # Kim qualifies, and Yang also qualifies with an additional course.
        fixture["tables"][0]["rows"] = [
            ["1001", "박상현", "DB"], ["1002", "박상현", "JAVA"],
            ["1003", "김현수", "DB"], ["1003", "김현수", "JAVA"],
            ["1004", "양선규", "DB"], ["1004", "양선규", "JAVA"], ["1004", "양선규", "Python"],
        ]
        fixture["results"][0]["rows"] = [["김현수"], ["양선규"]]
        self.assertEqual("pass", execute_fixture(fixture)["status"])
        # The original name-based condition must fail the same counterexample.
        fixture["sql"] = DIVISION_BEFORE["sql"]
        with self.assertRaisesRegex(ValueError, "result mismatch"):
            execute_fixture(fixture)

    def test_duplicate_lesson_rejected(self):
        pack = copy.deepcopy(self.pack)
        pack["lessons"][1]["id"] = pack["lessons"][0]["id"]
        with self.assertRaisesRegex(ValueError, "Duplicate lesson"):
            validate_pack(pack)

    def test_unknown_note_reference_rejected(self):
        pack = copy.deepcopy(self.pack)
        pack["lessons"][0]["relatedNoteIds"] = ["note-nonexistent"]
        with self.assertRaisesRegex(ValueError, "Unknown reference"):
            validate_pack(pack)

    def test_renumbered_self_check_rejected(self):
        pack = copy.deepcopy(self.pack)
        pack["lessons"][0]["selfChecks"][0]["id"] = "Q-new"
        with self.assertRaisesRegex(ValueError, "stable id"):
            validate_pack(pack)

    def test_ragged_or_numeric_display_table_rejected(self):
        for invalid in (["one"], [1, "name", "dept", "90"]):
            pack = copy.deepcopy(self.pack)
            pack["lessons"][0]["examples"][0]["tables"][0]["rows"][0] = invalid
            with self.subTest(row=invalid), self.assertRaises(ValueError):
                validate_pack(pack)

    def test_missing_explanation_rejected(self):
        pack = copy.deepcopy(self.pack)
        pack["lessons"][0]["selfChecks"][0]["explanation"] = ""
        with self.assertRaisesRegex(ValueError, "Invalid text"):
            validate_pack(pack)

    def test_svg_script_foreign_object_and_external_reference_rejected(self):
        bodies = ['<script>alert(1)</script>', '<foreignObject/>', '<rect onclick="x()"/>',
                  '<path fill="url(https://example.invalid/x)"/>', '<image href="https://example.invalid/x"/>',
                  '<rect style="fill:red"/>']
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(ValueError):
                validate_svg('<svg xmlns="http://www.w3.org/2000/svg">' + body + '</svg>')

    def test_svg_entity_declaration_rejected(self):
        with self.assertRaisesRegex(ValueError, "declarations"):
            validate_svg('<!DOCTYPE svg [<!ENTITY secret SYSTEM "file:///private">]><svg xmlns="http://www.w3.org/2000/svg"/>')

    def test_corrected_check_case_grouping_semantics(self):
        by_id = {l["id"]: l for l in self.pack["lessons"]}
        check = by_id["1-2-03"]["diagramSvg"]
        self.assertIn("FALSE이면 거부", check)
        self.assertIn("TRUE · UNKNOWN 허용", check)
        self.assertNotIn("TRUE만 통과", check)
        case = by_id["2-1-18"]["diagramSvg"]
        self.assertIn("첫 TRUE의 결과 선택", case)
        self.assertNotIn("통과한 행 표시", case)
        grouping = {c["term"]: c for c in by_id["2-2-09"]["concepts"]}
        self.assertIn("GROUPING(a)", grouping["GROUPING_ID(a,b)"]["example"])
        self.assertIn("a가 집계 기준에서 제외되면 10(2)", grouping["비트 방향"]["example"])

    def test_order_by_and_full_memory_captions_preserved(self):
        by_id = {l["id"]: l for l in self.pack["lessons"]}
        for lid in ("2-1-06", "2-1-21"):
            self.assertIn("ORDER BY", by_id[lid]["diagramSvg"])
        for lid in ("2-1-13", "2-2-03", "2-3-02"):
            self.assertNotIn("…", by_id[lid]["diagramSvg"])

    def test_all_engine_fixtures_match(self):
        modes = {"direct": 0, "equivalent": 0}
        for fixture in self.fixtures:
            with self.subTest(example=fixture["id"]):
                result = execute_fixture(fixture)
                self.assertEqual("pass", result["status"])
                modes[result["mode"]] += 1
        self.assertEqual({"direct": 50, "equivalent": 10}, modes)

    def test_wrong_expected_answer_is_detected(self):
        fixture = copy.deepcopy(self.fixtures[0])
        fixture["results"][0]["rows"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "result mismatch"):
            execute_fixture(fixture)

    def test_unordered_comparison_preserves_duplicate_counts(self):
        fixture = {"id": "bag", "mode": "direct", "tables": [],
                   "sql": "SELECT 1 UNION ALL SELECT 1;",
                   "results": [{"columns": ["n"], "rows": [[1]]}]}
        with self.assertRaisesRegex(ValueError, "result mismatch"):
            execute_fixture(fixture)

    def test_window_order_is_not_global_order(self):
        self.assertFalse(outer_ordered("SELECT SUM(x) OVER(ORDER BY x) FROM t"))
        self.assertTrue(outer_ordered("SELECT SUM(x) OVER(ORDER BY x) FROM t ORDER BY x"))
        self.assertFalse(outer_ordered("SELECT 'ORDER BY x' FROM t"))

    def test_engine_rejects_file_access_and_extension_loading(self):
        sqls = ["ATTACH DATABASE 'file:test?mode=memory' AS other;", "PRAGMA database_list;",
                "SELECT load_extension('anything');", "SELECT writefile('anything','x');"]
        for sql in sqls:
            fixture = {"id": "unsafe", "mode": "direct", "tables": [], "sql": sql, "results": []}
            with self.subTest(sql=sql), self.assertRaises((ValueError, sqlite3.DatabaseError)):
                execute_fixture(fixture)

    def test_engine_interrupts_unbounded_recursion(self):
        fixture = {"id": "bounded", "mode": "direct", "tables": [],
                   "sql": "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n) SELECT SUM(x) FROM n;",
                   "results": [{"columns": ["n"], "rows": []}]}
        with self.assertRaisesRegex(sqlite3.OperationalError, "interrupted"):
            execute_fixture(fixture)


if __name__ == "__main__":
    unittest.main(verbosity=2)
