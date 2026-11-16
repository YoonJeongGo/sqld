"""Independent structural and explicitly enumerated value checks; does not import the authoring builder."""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "content/sql-walkthroughs"
ASSETS = ROOT / "app/src/main/assets/sql-walkthroughs"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def same_rows(actual, expected):
    return collections.Counter(map(tuple, actual)) == collections.Counter(map(tuple, expected))


def main():
    index = read(SOURCE / "index.json")
    questions = {q["id"]: q for part in ("a", "b") for q in read(ROOT / f"content/part-{part}.json")["questions"]}
    docs = {}
    failures = []
    def check(condition, message):
        if not condition:
            failures.append(message)
    check(len({e["questionId"] for e in index["entries"]}) == len(index["entries"]), "duplicate index question")
    for entry in index["entries"]:
        doc = read(SOURCE / entry["file"])
        key = entry["questionId"]
        docs[key] = doc
        q = questions[key]
        check(doc["id"] == key, key + ": ID mismatch")
        check(all(value == q.get(field) for field, value in doc["source"].items()), key + ": source snapshot mismatch")
        check((SOURCE / entry["file"]).read_bytes() == (ASSETS / entry["file"]).read_bytes(), key + ": asset mismatch")
        check(doc["verification"].get("oracleEngineExecuted") is False, key + ": unsupported Oracle engine claim")
        steps = doc["steps"]
        check(bool(steps) and len({s["id"] for s in steps}) == len(steps), key + ": empty/duplicate steps")
        for step in steps:
            for clause in ("FROM", "GROUP BY", "ORDER BY"):
                if step["title"].startswith(clause + " ·"):
                    check(any(f["needle"].startswith(clause + " ") for f in step.get("codeFocus", [])),
                          key + ": semantic clause focus missing keyword " + clause)
            for focus in step.get("codeFocus", []):
                start = 0
                needle = focus["needle"]
                for _ in range(focus.get("occurrence", 0) + 1):
                    start = doc["source"]["sql"].find(needle, start)
                    check(bool(needle) and start >= 0, key + ": bad SQL focus " + str(focus))
                    if start < 0:
                        break
                    start += len(needle)
            check(all(text and text in step["text"] for text in step.get("highlights", [])), key + ": absent explanation emphasis")
            table = step.get("table")
            if table:
                check(all(len(row) == len(table["columns"]) for row in table["rows"]), key + ": ragged table")
                check(all(0 <= cell["row"] < len(table["rows"]) and 0 <= cell["column"] < len(table["columns"]) for cell in step.get("focusCells", [])), key + ": bad focus cell")
                check(all(0 <= row < len(table["rows"]) for row in step.get("focusRows", [])), key + ": bad focus row")
        expected = q.get("fixture", {}).get("expectedRows")
        if expected is not None:
            actual = steps[-1].get("table", {}).get("rows", [])
            equal = actual == expected if q["fixture"].get("ordered") else same_rows(actual, expected)
            check(equal, key + ": final table exact-value ordered/bag mismatch")

    # Hand-derived checks against original input values, independent of the builder's SQL-to-step logic.
    cases = []
    def table_case(key, title, expected, nth=0, ordered=False):
        matching = [s for s in docs[key]["steps"] if s["title"].startswith(title)]
        check(len(matching) > nth, key + ": missing semantic stage " + title)
        if len(matching) > nth:
            actual = matching[nth]["table"]["rows"]
            ok = actual == expected if ordered else same_rows(actual, expected)
            check(ok, key + ": independent intermediate mismatch " + title)
            cases.append({"questionId": key, "stage": title, "occurrence": nth, "ordered": ordered, "passed": ok})

    table_case("S06-A02", "WHERE · 입력 1", [["1", "FALSE → 제외"]])
    table_case("S06-A02", "WHERE · 입력 2", [["2", "UNKNOWN → 제외"]])
    table_case("S06-A02", "WHERE · 입력 3", [[None, "UNKNOWN → 제외"]])
    table_case("S07-A01", "집계 · COUNT(*)", [["80", "행 1개", "포함"], [None, "행 1개", "포함"], ["0", "행 1개", "포함"]])
    table_case("S07-A01", "집계 · COUNT(점수)", [["80", "80", "포함"], [None, None, "NULL → 제외"], ["0", "0", "포함"]])
    table_case("S07-A02", "집계 · AVG(NVL(x,0))", [["10", "10", "포함"], [None, "0", "포함"]])
    table_case("S07-A02", "집계 · AVG(x)", [["10", "10", "포함"], [None, None, "NULL → 제외"]])
    table_case("S07-A05", "최종 결과", [["0", None]])
    table_case("S08-A01", "GROUP BY · 부서=A", [["A", "10"], ["A", "20"]])
    table_case("S08-A01", "HAVING", [["A", "30", "TRUE → 통과"], ["B", "5", "FALSE → 제외"]])
    table_case("S10-A01-duplicate-multiplication", "FROM", [["1", "7", "7", "10"], ["1", "7", "7", "20"], ["2", "7", "7", "10"], ["2", "7", "7", "20"]])
    table_case("S11-A01-on-paid-preserve", "FROM", [["1", "10", "1", "1"], ["2", None, None, None], ["3", None, None, None]])
    table_case("S11-A02-where-paid-remove", "WHERE · 입력 4", [["3", None, None, None, "UNKNOWN → 제외"]])
    table_case("S11-A02-where-paid-remove", "WHERE · 남은", [["1", "10", "1", "1"]])
    table_case("S11-A03-count-outer-null", "집계 · COUNT(*)", [["3", None, None, None, "행 1개", "포함"]], 2)
    table_case("S11-A03-count-outer-null", "집계 · COUNT(O.id)", [["3", None, None, None, None, "NULL → 제외"]], 2)
    table_case("S11-A04-full-both-unmatched", "FROM", [["1", None], ["2", "2"], [None, "3"]])
    table_case("S11-A05-using-key-result", "최종 결과", [["1"], ["2"], ["3"]])
    table_case("S11-A06-natural-extra-key", "최종 결과", [["2", "1"]])

    # At least one explicit intermediate check for each currently authored advanced pattern.
    table_case("S12-A01-above-own-dept-average", "바깥 비교 · e.id=4", [["4", None, "50", "UNKNOWN → 제외"]])
    table_case("S12-A02-exists-no-multiply", "존재 검사 · 1", [["1"], ["1"]])
    table_case("S12-A03-null-safe-not-exists", "존재 검사 · NULL", [])
    table_case("S12-A04-not-in-empty", "NOT IN", [["1", "TRUE → 통과"], [None, "TRUE → 통과"]])
    table_case("S12-A05-scalar-aggregate-empty", "안쪽 AVG", [[None]])
    table_case("S12-A06-any-null-mixed", "ANY · x=1", [["1", "UNKNOWN → 제외"]])
    table_case("S12-A07-all-empty", "ALL", [["1", "TRUE → 통과"], ["2", "TRUE → 통과"]])
    table_case("S12-A08-tuple-in", "바깥 행", [["2025", "2", "FALSE → 제외"]], 1)
    table_case("S12-SUP-A01-paired-membership", "바깥 행", [["2", "10", "2", "FALSE → 제외"]], 1)
    table_case("S13-A01-union-null-combined", "집합 연산", [["1"], ["2"], [None], ["3"]])
    table_case("S13-A02-all-count", "집합 연산", [["1"], ["1"], ["2"], [None], ["2"], ["3"], [None]])
    table_case("S13-A03-intersection-two-columns", "집합 연산", [["1", "10"], ["2", None]])
    table_case("S13-A04-minus-dedup", "집합 연산", [["1"]])
    table_case("S13-A05-parenthesized-difference", "괄호 안", [["2"], ["3"], ["4"]])
    table_case("S13-A06-difference-count-empty", "바깥 집계", [["0"]])
    table_case("S15-A01-ranks-side-by-side", "RANK · id=3", [["1", "1", "90", "계산 대상 행"], ["2", "1", "90", "계산 대상 행"], ["3", "1", "70", "현재 보는 행"]])
    table_case("S15-A02-unique-number-with-tie-key", "ROW_NUMBER · id=1", [["2", "1", "90", "계산 대상 행"], ["1", "1", "90", "현재 보는 행"], ["3", "1", "70", "계산 대상 행"]], ordered=True)
    table_case("S15-A03-partition-sum-maintains-rows", "SUM · id=4", [["4", "2", "80", "현재 보는 행"]])
    table_case("S15-A04-lag-null-default", "LAG · id=3", [["2", None, "계산 대상 행"]])
    table_case("S15-A05-lead-gap-not-id", "LEAD · id=80", [])
    table_case("S15-A06-ntile-unequal", "최종 결과", [["1", "1"], ["2", "1"], ["3", "1"], ["4", "2"], ["5", "2"]])
    table_case("S16-A01-range-peer-cumulative", "SUM · id=1", [["1", "1", "10", "현재 보는 행"], ["2", "1", "20", "계산 대상 행"]])
    table_case("S16-A02-rows-two-window", "SUM · id=3", [["2", "1", "20", "계산 대상 행"], ["3", "3", "5", "현재 보는 행"]], ordered=True)
    table_case("S16-A03-range-value-distance", "SUM · id=3", [["3", "3", "5", "현재 보는 행"]])
    table_case("S16-A04-last-value-full", "LAST_VALUE · id=1", [["1", "1", "10", "현재 보는 행"], ["2", "1", "20", "계산 대상 행"], ["3", "3", "5", "계산 대상 행"]])
    table_case("S16-A05-future-count-boundary", "COUNT · id=3", [])
    table_case("S16-A06-partition-boundaries", "SUM · id=3", [["3", "2", "100", "현재 보는 행"]])
    table_case("S15-SUP-A01-percent-rank-top-tie", "최종 결과", [["1", "0"], ["2", "0.5"], ["3", "0.5"]])
    table_case("S15-SUP-A02-cume-desc-peers", "최종 결과", [["1", "0.25"], ["2", "0.75"], ["3", "0.75"], ["4", "1"]])
    table_case("S16-SUP-A02-first-value-moving-frame", "FIRST_VALUE · id=3", [["2", "4", "계산 대상 행"], ["3", "7", "현재 보는 행"]], ordered=True)

    learning_checks = []
    for entry in index.get("learningExamples", []):
        doc = read(SOURCE / entry["file"])
        check((SOURCE / entry["file"]).read_bytes() == (ASSETS / entry["file"]).read_bytes(), entry["id"] + ": teaching asset mismatch")
        if entry["id"] == "learning-employee-not-in-any":
            import review_reference_example as ref
            expected_rows = [[None if value is None else str(value) for value in row] for row in ref.ROWS]
            check(doc["source"]["tables"][0]["rows"] == expected_rows, "EMPLOYEE original fictional values mismatch")
            and_stage = next(s for s in doc["steps"] if s["title"].startswith("AND"))
            expected_trace = [[r[1], n, a, c] for r, n, a, c in zip(ref.ROWS,
                ["FALSE", "FALSE", "FALSE", "UNKNOWN", "UNKNOWN", "UNKNOWN"],
                ["TRUE", "TRUE", "TRUE", "TRUE", "FALSE", "TRUE"],
                ["FALSE → 제외", "FALSE → 제외", "FALSE → 제외", "UNKNOWN → 제외", "FALSE → 제외", "UNKNOWN → 제외"])]
            check(and_stage["table"]["rows"] == expected_trace, "EMPLOYEE combined three-valued trace mismatch")
            final = next(s for s in doc["steps"] if s["title"].startswith("SELECT · 마지막"))
            check(final["table"]["rows"] == [], "EMPLOYEE final result must be zero rows")
            learning_checks.append(entry["id"])

    result = {"status": "PASS" if not failures else "FAIL", "appliedDocumentsChecked": len(docs),
              "allStepsChecked": sum(len(d["steps"]) for d in docs.values()),
              "explicitValueChecks": cases, "failureCount": len(failures), "failures": failures,
              "learningExamplesChecked": learning_checks,
              "oracle19cExecuted": False,
              "limits": ["Structural/source/final-table comparison covers every currently indexed document.",
                         "Intermediate semantic checks are enumerated by ID and stage, not every sentence in every document.",
                         "This script does not certify Oracle execution or learning efficacy."]}
    (ROOT / "qa/walkthrough-review/generated-review-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "appliedDocumentsChecked", "allStepsChecked", "failureCount", "failures")}, ensure_ascii=True))
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
