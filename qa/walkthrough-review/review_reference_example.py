"""Independent value review of the user's EMPLOYEE example; NOT Oracle execution."""
from __future__ import annotations

import json
import platform
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROWS = [
    (1001, "박강열", 10, 900),
    (1002, "유성재", 20, 700),
    (1003, "양지훈", 20, 500),
    (1004, "박보성", 30, 600),
    (1005, "이승현", 30, 300),
    (1006, "김현수", None, 800),
]


def sql_or(values):
    values = list(values)
    if True in values:
        return True
    return None if None in values else False


def sql_and(values):
    values = list(values)
    if False in values:
        return False
    return None if None in values else True


def equals(left, right):
    return None if left is None or right is None else left == right


def greater(left, right):
    return None if left is None or right is None else left > right


def sql_not(value):
    return None if value is None else not value


def label(value):
    return "UNKNOWN" if value is None else str(value).upper()


def main():
    sub1 = [r[2] for r in ROWS if r[3] >= 700]
    sub2 = [r[3] for r in ROWS if r[2] == 30]
    assert sub1 == [10, 20, None]
    assert sub2 == [600, 300]
    decisions = []
    for emp_id, name, dept, salary in ROWS:
        not_in = sql_not(sql_or(equals(dept, value) for value in sub1))
        any_gt = sql_or(greater(salary, value) for value in sub2)
        combined = sql_and([not_in, any_gt])
        decisions.append({"emp_id": emp_id, "name": name, "dept": dept,
                          "salary": salary, "not_in": label(not_in),
                          "greater_any": label(any_gt), "and": label(combined),
                          "included": combined is True})
    assert [d["not_in"] for d in decisions] == ["FALSE", "FALSE", "FALSE", "UNKNOWN", "UNKNOWN", "UNKNOWN"]
    assert [d["greater_any"] for d in decisions] == ["TRUE", "TRUE", "TRUE", "TRUE", "FALSE", "TRUE"]
    assert [d["and"] for d in decisions] == ["FALSE", "FALSE", "FALSE", "UNKNOWN", "FALSE", "UNKNOWN"]
    assert not any(d["included"] for d in decisions)
    # In particular UNKNOWN AND FALSE is FALSE; UNKNOWN is not simply FALSE.
    truth = [True, False, None]
    expected_and = [True, False, None, False, False, False, None, False, None]
    expected_or = [True, True, True, True, False, None, True, None, None]
    assert [sql_and([a, b]) for a in truth for b in truth] == expected_and
    assert [sql_or([a, b]) for a in truth for b in truth] == expected_or
    assert sql_not(None) is None
    assert sql_or([]) is False  # greater than ANY of an empty result is FALSE.
    assert sql_not(sql_or([])) is True  # NOT IN empty result is TRUE.

    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE EMPLOYEE(EMP_ID INTEGER, EMP_NAME TEXT, DEPT_ID INTEGER, SALARY INTEGER)")
    con.executemany("INSERT INTO EMPLOYEE VALUES(?,?,?,?)", ROWS)
    translated = """SELECT EMP_ID,
      DEPT_ID NOT IN (SELECT DEPT_ID FROM EMPLOYEE WHERE SALARY >= 700),
      (SALARY > 600 OR SALARY > 300),
      (DEPT_ID NOT IN (SELECT DEPT_ID FROM EMPLOYEE WHERE SALARY >= 700))
        AND (SALARY > 600 OR SALARY > 300)
      FROM EMPLOYEE ORDER BY EMP_ID"""
    db_trace = con.execute(translated).fetchall()
    db_label = lambda v: "UNKNOWN" if v is None else "TRUE" if v else "FALSE"
    assert [[d["emp_id"], d["not_in"], d["greater_any"], d["and"]] for d in decisions] == [
        [row[0], *[db_label(v) for v in row[1:]]] for row in db_trace]
    result = {
        "status": "PASS", "scope": "User-supplied reference example; independent Python three-valued value trace and SQLite transformed-query cross-check",
        "python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
        "oracle19cExecuted": False,
        "transformation": "Oracle > ANY subquery syntax was replaced by >600 OR >300 after independently computing the exact non-NULL two-value subquery result. This is not Oracle SQL execution.",
        "subquery1": sub1, "subquery2": sub2, "decisions": decisions,
        "finalRows": [], "finalRowCount": 0, "correctOption": 4,
        "notes": ["Names and salaries are the user's supplied fictional example.", "No top-level ORDER BY in the original example; no result ordering is claimed.", "Both outer conditions were evaluated for explanation even though NOT IN suffices to conclude zero result rows."]
    }
    dest = ROOT / "qa/walkthrough-review/reference-example-result.json"
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "sqlite": result["sqlite"], "oracle19cExecuted": False,
                      "rowDecisions": len(decisions), "finalRows": 0, "report": str(dest)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
