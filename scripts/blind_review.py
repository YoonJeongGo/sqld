"""Blind content review support; automatic comparison does not solve questions.

prepare prints only allowlisted inputs. A reviewer must write independent decisions
before compare opens the original answer keys. SHA-256 pins content to avoid silently
applying a review to changing author files. No external services or SQL engine.
"""
import argparse
import hashlib
import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def write(path, value):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def public_question(q):
    allowed = ("id", "version", "title", "stem", "sql", "tables", "dialect", "dialectVersion")
    result = {key: q[key] for key in allowed if key in q}
    result["choices"] = [{"id": c["id"], "text": c["text"]} for c in q["choices"]]
    fixture = q.get("fixture")
    if fixture:
        result["fixtureInput"] = {key: fixture[key] for key in
            ("schemaSql", "setupSql", "query", "constraints", "sessionSettings", "ordered")
            if key in fixture}
    return result

def prepare(args):
    questions, seen = [], set()
    choice_map = {}
    mask_output = getattr(args, "choice_map_output", None)
    only = set(args.ids.split(",")) if args.ids else None
    for path in args.parts:
        for q in read(path)["questions"]:
            if only and q["id"] not in only:
                continue
            if q["id"] in seen:
                raise ValueError("Duplicate question: " + q["id"])
            seen.add(q["id"])
            public = public_question(q)
            if mask_output:
                secrets.SystemRandom().shuffle(public["choices"])
                choice_map[q["id"]] = {}
                for index, choice in enumerate(public["choices"]):
                    masked_id = f"r{index + 1}"
                    choice_map[q["id"]][masked_id] = choice["id"]
                    choice["id"] = masked_id
            questions.append({"sourceFile": str(Path(path).resolve().relative_to(ROOT)),
                              "sourceQuestionSha256": digest(q),
                              "publicInputSha256": digest(public), "question": public})
    output = {"schemaVersion": 1, "createdAt": datetime.now(timezone.utc).isoformat(),
              "method": "allowlist_without_answers_explanations_expected_results",
              "questions": questions}
    output["inputSha256"] = digest(questions)
    if mask_output:
        output["method"] = "allowlist_without_answers_explanations_expected_results_and_masked_choice_ids"
        output["choiceMapSha256"] = digest(choice_map)
        write(mask_output, choice_map)
    write(args.output, output)
    print(json.dumps(output, ensure_ascii=False, indent=2))

def compare(args):
    blind = read(args.input)
    decisions = read(args.decisions)
    if decisions["inputSha256"] != blind["inputSha256"]:
        raise ValueError("Decision file does not reference this blind input")
    if blind["inputSha256"] != digest(blind["questions"]):
        raise ValueError("Blind input was changed after preparation")
    masked = decisions.get("method") == "independent_ai_blind_reasoning_masked_choice_ids"
    if decisions.get("method") != "independent_ai_blind_reasoning" and not masked:
        raise ValueError("Explicit independent-review method required")
    choice_map = read(args.choice_map) if masked and args.choice_map else None
    if masked and choice_map is None:
        raise ValueError("Masked-choice review requires its separately stored choice map")
    if masked and blind.get("choiceMapSha256") and digest(choice_map) != blind["choiceMapSha256"]:
        raise ValueError("Choice-ID map changed after preparation")
    decision_map = {d["questionId"]: d for d in decisions["decisions"]}
    if len(decision_map) != len(decisions["decisions"]):
        raise ValueError("Duplicate decisions")
    results = []
    for item in blind["questions"]:
        qid = item["question"]["id"]
        if qid not in decision_map:
            results.append({"questionId": qid, "status": "not_reviewed"})
            continue
        decision = decision_map[qid]
        if not decision.get("reasoning"):
            raise ValueError("Independent reasoning missing for " + qid)
        authored = next((q for q in read(ROOT / item["sourceFile"])["questions"] if q["id"] == qid), None)
        if authored is None or digest(authored) != item["sourceQuestionSha256"]:
            results.append({"questionId": qid, "status": "source_changed_requires_review"})
            continue
        chosen = sorted(choice_map[qid][choice] for choice in decision["choiceIds"]) if masked else sorted(decision["choiceIds"])
        expected = sorted(authored["correctChoiceIds"])
        valid_choices = {c["id"] for c in authored["choices"]}
        if not set(chosen) <= valid_choices:
            raise ValueError("Decision has invalid choice ID for " + qid)
        match = chosen == expected
        results.append({"questionId": qid, "status": "answer_agrees" if match else "answer_disagrees",
                        "independentChoiceIds": chosen, "authoredChoiceIds": expected,
                        "conditionsOrIssues": decision.get("conditionsOrIssues", []),
                        "sourceQuestionSha256": item["sourceQuestionSha256"]})
    output = {"schemaVersion": 1, "comparedAt": datetime.now(timezone.utc).isoformat(),
              "inputSha256": blind["inputSha256"],
              "decisionsSha256": digest(decisions),
              "boundary": "Only recorded questions reviewed; no DBMS execution or human expert review.",
              "counts": {status: sum(r["status"] == status for r in results) for status in
                         ("answer_agrees", "answer_disagrees", "source_changed_requires_review", "not_reviewed")},
              "results": results}
    if masked:
        output["choiceMapSha256"] = digest(choice_map)
    write(args.output, output)
    print(json.dumps(output, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("parts", nargs="+")
    prep.add_argument("--ids")
    prep.add_argument("--output", required=True)
    prep.add_argument("--choice-map-output", help="Mask both choice IDs and order; write the correspondence separately, never to prepare output")
    comp = sub.add_parser("compare")
    comp.add_argument("--input", required=True)
    comp.add_argument("--decisions", required=True)
    comp.add_argument("--choice-map", help="For masked-choice review only; opened after independent decisions are saved")
    comp.add_argument("--output", required=True)
    args = parser.parse_args()
    (prepare if args.action == "prepare" else compare)(args)

if __name__ == "__main__":
    main()
