"""Normalize the user supplied 63-lesson material; never execute its scripts.

The source directory stays immutable. The committed content/course-pack.json is
the portable authoring source; rerunning this import requires the original pack.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "evidence/incoming-63lectures-20260928/SQLD_63_Visual_Notes"
PART_NOTES = {
    "1-1": ["S01", "M01", "M01", "M11", "M12 M04", "M02", "M03", "M04 M07", "M05 M10"],
    "1-2": ["S01", "M05 S23 M10", "S23", "S01 S21 S22 S23 S24", "M06", "M06", "M13"],
    "2-1": ["S23", "S25", "S23", "S26", "S21", "S02", "S06", "S21", "S21 S23",
            "S21", "S06", "S09 S02", "S03", "S04", "M09 S07", "S06 S23", "S05 S07",
            "S05", "S07", "S08", "S08 S02", "S10 M07", "S11 S07", "S10 S18", "S11"],
    "2-2": ["S12", "S12", "S12 S06", "S12", "S12", "S13", "S14", "S14", "S14",
            "S15 S16", "S15", "S16", "S16", "S17", "S18", "S18", "S19", "S20"],
    "2-3": ["S27", "S22 M08", "S24", "S28"],
}
EXPECTED_COUNTS = {"lessons": 63, "concepts": 490, "examples": 95, "selfChecks": 189,
                   "tables": 223, "sqlBlocks": 70, "diagrams": 63, "lectureMinutes": 1932}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cell(value):
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Unsupported table cell: {value!r}")
    return str(value)


def table(source):
    return {"title": source["name"], "columns": source["columns"],
            "rows": [[cell(value) for value in row] for row in source["rows"]]}


def correct_particles(value, names, changes, path=""):
    """Only fix a standalone postposition, never an occurrence inside a word."""
    if isinstance(value, dict):
        return {k: correct_particles(v, names, changes, f"{path}.{k}") for k, v in value.items()}
    if isinstance(value, list):
        return [correct_particles(v, names, changes, f"{path}[{i}]") for i, v in enumerate(value)]
    if not isinstance(value, str):
        return value
    result = value
    for name in names:
        consonant = (ord(name[-1]) - 0xAC00) % 28 != 0
        pairs = {"를": "을", "는": "은", "가": "이", "와": "과"} if consonant else {
            "을": "를", "은": "는", "과": "와", "이": "가"}
        for wrong, right in pairs.items():
            result = re.sub(re.escape(name + wrong) + r"(?=$|[\s,.;:!?·])", name + right, result)
    if result != value:
        changes.append({"path": path, "kind": "korean_particle", "before": value, "after": result})
    return result


def logical_order_svg(title: str) -> str:
    labels = [("FROM", "어느 표?"), ("WHERE", "어느 행?"), ("GROUP BY", "어떤 묶음?"),
              ("HAVING", "어느 그룹?"), ("SELECT", "무엇을 출력?"), ("ORDER BY", "어떤 순서?")]
    items = []
    for i, (label, detail) in enumerate(labels):
        x = 15 + i * 118
        items.append(f'<rect x="{x}" y="60" width="106" height="85" rx="10" fill="#ffffff" stroke="#b7d2d5"/>'
                     f'<text x="{x + 53}" y="94" text-anchor="middle" font-size="14" fill="#172b4d">{label}</text>'
                     f'<text x="{x + 53}" y="122" text-anchor="middle" font-size="12" fill="#58677f">{detail}</text>')
        if i < 5:
            items.append(f'<path d="M{x + 109} 103 L{x + 116} 103" stroke="#007d7a" stroke-width="2" marker-end="url(#arr)"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 215" role="img" '
            f'aria-label="{html.escape(title)} 개념도"><defs><marker id="arr" viewBox="0 0 10 10" '
            'refX="8" refY="5" markerWidth="3" markerHeight="3" orient="auto"><path d="M0 0 L10 5 L0 10" '
            'fill="#007d7a"/></marker></defs><rect width="720" height="215" rx="18" fill="#f0f6f8"/>'
            '<g font-family="sans-serif">' + "".join(items) +
            '<text x="360" y="185" text-anchor="middle" font-size="13" fill="#172b4d">'
            '개념적인 처리 순서이며, 실제 실행계획의 순서와는 다를 수 있습니다.</text></g></svg>')


def correct_svg(svg, lesson, changes):
    original = svg
    lesson_id = lesson["id"]
    if lesson_id == "1-2-03":
        replacements = {"원본 표": "저장할 값", "각 행의 값을 읽기": "INSERT · UPDATE 시 검사",
                        "조건 확인": "CHECK 조건", "TRUE만 통과": "FALSE이면 거부",
                        "결과 표": "제약조건 충족", "통과한 행 표시": "TRUE · UNKNOWN 허용"}
        for before, after in replacements.items():
            svg = svg.replace(">" + before + "<", ">" + after + "<")
    if lesson_id == "2-1-18":
        replacements = {"원본 표": "각 행의 값", "각 행의 값을 읽기": "CASE 입력 확인",
                        "조건 확인": "WHEN 순서대로", "TRUE만 통과": "첫 TRUE의 결과 선택",
                        "결과 표": "출력값 계산", "통과한 행 표시": "없으면 ELSE · 생략 시 NULL"}
        for before, after in replacements.items():
            svg = svg.replace(">" + before + "<", ">" + after + "<")
        svg = svg.replace('font-size="13"', 'font-size="12"')
    if lesson_id in {"2-1-06", "2-1-21"}:
        svg = logical_order_svg(lesson["title"])
    if "…" in svg:
        # The imported caption cuts off meaningful text. Use two complete lines.
        memory = lesson["memory"]
        split_at = memory.rfind(" ", 0, 47)
        if split_at < 20:
            split_at = min(45, len(memory))
        lines = [memory[:split_at].strip(), memory[split_at:].strip()]
        caption = ('<text x="360" y="178" text-anchor="middle" font-family="sans-serif" '
                   'font-size="12" fill="#172b4d">' +
                   "".join(f'<tspan x="360" dy="{0 if i == 0 else 18}">{html.escape(line)}</tspan>'
                           for i, line in enumerate(lines) if line) + '</text>')
        svg = re.sub(r"<text\b[^>]*>[^<]*…</text>", caption, svg)
    if original != svg:
        changes.append({"path": f"{lesson_id}.diagramSvg", "kind": "diagram_correction",
                        "beforeSha256": hashlib.sha256(original.encode()).hexdigest(),
                        "afterSha256": hashlib.sha256(svg.encode()).hexdigest()})
    return svg


def normalized(source_dir: Path):
    raw = json.loads((source_dir / "data/content.json").read_text(encoding="utf-8"))
    changes = []
    source = correct_particles(copy.deepcopy(raw), raw["meta"]["names"], changes)
    by_id = {lesson["id"]: lesson for lesson in source["lessons"]}
    grouping = by_id["2-2-09"]["concepts"]
    for concept in grouping:
        if concept["term"] == "비트 방향":
            old = concept["example"]
            concept["example"] = "a가 집계 기준에서 제외되면 10(2), b가 제외되면 01(1)"
            changes.append({"path": "2-2-09.concepts.비트 방향.example", "kind": "meaning_correction",
                            "before": old, "after": concept["example"]})
        if concept["term"] == "GROUPING_ID(a,b)":
            old = concept["example"]
            concept["example"] = "GROUPING(a) × 2 + GROUPING(b)"
            changes.append({"path": "2-2-09.concepts.GROUPING_ID(a,b).example", "kind": "meaning_clarification",
                            "before": old, "after": concept["example"]})
    lessons = []
    for lesson in source["lessons"]:
        examples = []
        for example in lesson["examples"]:
            # These are provenance labels only. Current execution evidence is a
            # separate report, so a source claim never becomes a fresh test pass.
            if example["mode"] == "sqlite":
                verification = "SQLite용 예제 · 원자료는 직접 실행 확인으로 기록했습니다. 앱에서는 실행하지 않습니다."
            elif example.get("check_sql"):
                verification = "Oracle 문법 예제 · 원자료의 SQLite 대체식 확인과 Oracle 실제 실행은 다릅니다. Oracle 실행 미확인."
            elif example["mode"] == "oracle":
                verification = "Oracle 문법 예제 · 예상 결과를 설명한 자료입니다. Oracle 실행 미확인."
            else:
                verification = "개념 설명 예제 · SQL 엔진 실행 결과가 아닙니다."
            examples.append({"id": example["id"], "title": example["title"], "question": example["question"],
                             "tables": [table(t) for t in example["tables"]], "sql": example["sql"],
                             "steps": example["steps"], "results": [table(t) for t in example["results"]],
                             "mode": example["mode"], "verification": verification})
        svg = (source_dir / "diagrams" / (lesson["id"] + ".svg")).read_text(encoding="utf-8")
        lessons.append({"id": lesson["id"], "partId": lesson["part"], "number": lesson["number"],
                        "title": lesson["title"], "lectureMinutes": lesson["lecture_minutes"],
                        "easy": lesson["easy"], "why": lesson["why"], "concepts": lesson["concepts"],
                        "examples": examples, "memory": lesson["memory"], "traps": lesson["traps"],
                        "selfChecks": [{"id": lesson["id"] + f"-Q{i + 1}", **question}
                                       for i, question in enumerate(lesson["quiz"])],
                        "relatedNoteIds": ["note-" + note for note in PART_NOTES[lesson["part"]][lesson["number"] - 1].split()],
                        "sourceIds": lesson["refs"], "bridge": lesson["bridge"],
                        "diagramSvg": correct_svg(svg, lesson, changes), "version": 1})
    pack = {"schemaVersion": 1, "version": "course-2026-09-28.1", "title": "SQLD 63강 학습자료",
            "parts": [{"id": key, "title": value} for key, value in source["parts"].items()],
            "lessons": lessons, "sources": [{"id": key, **value} for key, value in source["sources"].items()],
            "provenance": "사용자가 제공한 SQLD_63강_Canva_Codex_전체.zip의 창작 학습자료를 강의 목차에 맞춰 수록했습니다. 실제 강의 영상·강사 교재의 전문이나 공식 기출문제가 아닙니다.",
            "reviewNote": "기존 개념 노트와 별도로 강의 읽음·예제 확인·자기점검 진도를 기록합니다. 자기점검 189개는 스스로 답을 비교하는 활동이며 시험 점수에 합산하지 않습니다. 구조·참조·표 보존을 검사하고 CHECK·CASE·GROUPING_ID와 도해 문구를 수정했습니다. 사람 전문가 검수·Oracle 실제 실행·합격 효과 검증은 미실시입니다."}
    report = {"sourceContentSha256": digest(source_dir / "data/content.json"),
              "sourceFilesModified": False, "changes": changes, "counts": counts(pack),
              "notes": ["Original SQL strings and table cells are preserved (numeric cells serialized as display strings).",
                        "Unmodified source verification labels are provenance, not current engine evidence."]}
    return pack, report


def counts(pack):
    lessons = pack["lessons"]
    examples = [example for lesson in lessons for example in lesson["examples"]]
    return {"lessons": len(lessons), "concepts": sum(len(l["concepts"]) for l in lessons),
            "examples": len(examples), "selfChecks": sum(len(l["selfChecks"]) for l in lessons),
            "tables": sum(len(e["tables"]) + len(e["results"]) for e in examples),
            "sqlBlocks": sum(bool(e["sql"]) for e in examples), "diagrams": sum(bool(l["diagramSvg"]) for l in lessons),
            "lectureMinutes": sum(l["lectureMinutes"] for l in lessons)}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    if (ROOT / "content/course-pack.json").exists():
        parser.error("강의 정본이 이미 있습니다. 원자료를 다시 가져오면 앱의 정정을 덮어쓸 수 있습니다. content/course-pack.json을 편집하고 validate_course.py --sync-asset으로 검증·반영하세요. 원본 대조에는 쓰기 없는 normalized()를 사용하세요.")
    pack, report = normalized(args.source)
    assert report["counts"] == EXPECTED_COUNTS, report["counts"]
    # Fail closed before publishing either source or asset.
    from validate_course import validate_pack
    validate_pack(pack)
    raw = json.loads((args.source / "data/content.json").read_text(encoding="utf-8"))
    fixtures = []
    for lesson in raw["lessons"]:
        for example in lesson["examples"]:
            if example["mode"] == "sqlite" or example.get("check_sql"):
                fixtures.append({"id": example["id"], "mode": "equivalent" if example.get("check_sql") else "direct",
                                 "displaySql": example["sql"], "sql": example.get("check_sql") or example["sql"],
                                 "tables": example["tables"], "results": example["results"]})
    write_json(ROOT / "evidence/course-content-fixtures.json", {
        "schemaVersion": 1, "sourceContentSha256": report["sourceContentSha256"],
        "scope": "Literal fixture data only; supplied scripts and setup SQL are never executed. Equivalent SQL does not validate Oracle execution.",
        "fixtures": fixtures})
    for output in (ROOT / "content/course-pack.json", ROOT / "app/src/main/assets/course-pack.json"):
        write_json(output, pack)
    report["normalizedSha256"] = digest(ROOT / "content/course-pack.json")
    write_json(ROOT / "evidence/course-content-import.json", report)
    print(json.dumps({"status": "pass", "counts": report["counts"], "corrections": len(report["changes"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
