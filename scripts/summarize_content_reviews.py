"""Account for preserved AI review snapshots and explicitly reread revisions.

This does not judge answers, execute SQL, or upgrade author publication status.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path

import validate_content as v

ROOT = v.ROOT


def snapshot_question(path, question_id):
    data = v.stable_read(ROOT / path)[0]
    rows = data if isinstance(data, list) else data.get("questions", [])
    return next((row.get("question", row) for row in rows
                 if row.get("question", row).get("id") == question_id), None)


def summarize():
    questions = {q["id"]: q for name in ("part-a.json", "part-b.json")
                 for q in v.stable_read(ROOT / "content" / name)[0]["questions"]}
    old_answer_hashes = {}
    answers, masked, masked_without_declared_exposure = set(), set(), set()
    current_answers, status_only, batches = set(), set(), []
    for batch in v.load_reviews():
        batches.append({"file": batch["stem"] + "-comparison.json", "hashesValid": batch["valid"],
                        "choiceIdsAndOrderMasked": batch["masked"],
                        "priorAnswerExposureDeclared": batch["prior_answer_exposure"],
                        "counts": batch["comparison"]["counts"]})
        if not batch["valid"]:
            continue
        for row in batch["comparison"]["results"]:
            if row["status"] != "answer_agrees":
                continue
            qid, sha = row["questionId"], row["sourceQuestionSha256"]
            old_answer_hashes.setdefault(qid, set()).add(sha)
            answers.add(qid)
            if batch["masked"]:
                masked.add(qid)
                if not batch["prior_answer_exposure"]:
                    masked_without_declared_exposure.add(qid)
            if qid in questions and v.digest(questions[qid]) == sha:
                current_answers.add(qid)
            elif qid in questions and v.status_only_transition(questions[qid], sha):
                status_only.add(qid)

    explanations, current_explanations, explanation_files, current_followups = set(), set(), [], []
    old_explanation_hashes = {}
    files = list(sorted((ROOT / "qa").glob("content-*-explanations.json")))
    files += list(sorted((ROOT / "qa").glob("priority-*-explanations.json")))
    files += [ROOT / "evidence/content-blind-risk-explanation-review.json"]
    for path in files:
        if not path.exists():
            continue
        data, metadata = v.stable_read(path)
        valid = True
        if data.get("snapshotPath"):
            source_path = ROOT / Path(data["snapshotPath"])
            valid = (source_path.exists() and hashlib.sha256(source_path.read_bytes()).hexdigest()
                     == data.get("snapshotFileSha256"))
        rows = data.get("results", data.get("records", []))
        explanation_files.append({"file": metadata["path"], "fileSha256": metadata["sha256"],
                                  "recordedRows": len(rows), "referencedSnapshotHashValid": valid,
                                  "boundary": data.get("boundary", "")})
        if not valid:
            continue
        for row in rows:
            qid, sha = row.get("questionId"), row.get("sourceQuestionSha256")
            if not qid or not sha:
                continue
            explanations.add(qid)
            old_explanation_hashes.setdefault(qid, set()).add(sha)
            current = qid in questions and (v.digest(questions[qid]) == sha
                                             or v.status_only_transition(questions[qid], sha))
            if current:
                current_explanations.add(qid)
                if row.get("issues"):
                    current_followups.append({"questionId": qid, "file": metadata["path"],
                                              "issues": row["issues"]})

    amendments, amendment_files, rejected_amendments = set(), [], []
    for path in sorted(list((ROOT / "qa").glob("content-*-amendments.json")) + list((ROOT / "qa").glob("priority-*-amendments.json"))):
        data, metadata = v.stable_read(path)
        amendment_files.append({"file": metadata["path"], "fileSha256": metadata["sha256"],
                                "boundary": data.get("boundary", "")})
        for row in data.get("results", []):
            qid = row.get("questionId")
            valid = (qid in questions and v.digest(questions[qid]) == row.get("sourceQuestionSha256")
                     and qid in answers
                     and row.get("previousSourceQuestionSha256") in (old_answer_hashes.get(qid, set()) | old_explanation_hashes.get(qid, set()))
                     and isinstance(row.get("publicInputUnchanged"), bool)
                     and bool(row.get("reviewedFields")) and bool(row.get("reasoning"))
                     and row.get("status") == "reviewed_no_semantic_issue_found")
            if row.get("currentFullReadSnapshot"):
                snapshot = snapshot_question(row["currentFullReadSnapshot"], qid)
                valid = valid and snapshot is not None and v.digest(snapshot) == row.get("sourceQuestionSha256")
            if row.get("previousFullSnapshot"):
                snapshot = snapshot_question(row["previousFullSnapshot"], qid)
                valid = valid and snapshot is not None and v.digest(snapshot) == row.get("previousSourceQuestionSha256")
            if valid:
                amendments.add(qid)
            else:
                rejected_amendments.append({"questionId": qid, "file": metadata["path"],
                                           "reason": "Current/prior hash or explicit reread evidence does not match"})
    duplicate_path = ROOT / "evidence/content-duplicate-review.json"
    duplicate_decisions = v.stable_read(duplicate_path)[0].get("decisions", []) if duplicate_path.exists() else []
    for followup in current_followups:
        for decision in duplicate_decisions:
            if (followup["questionId"] in [decision["left"], decision["right"]]
                    and decision.get("status") == "replaced_and_independently_rechecked"
                    and decision.get("leftSha256") == v.digest(questions.get(decision["left"]))
                    and decision.get("rightSha256") == v.digest(questions.get(decision["right"]))):
                followup["resolution"] = "Related duplicate question replaced and independently rechecked; original finding retained"
                followup["resolutionEvidence"] = "evidence/content-duplicate-review.json"
    traceable_answers = current_answers | status_only | amendments
    traceable_explanations = current_explanations | amendments
    report = {
        "schemaVersion": 1, "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "boundary": "Evidence accounting only. Preserved independent AI reasoning and explanation reads are not human expert review, Oracle execution, official syllabus verification, or statistical proof of learning efficacy. Rereading after prior answer exposure is not first-time blind review. No changed revision inherits a review without an exact hash, proved status-only transition, or explicit independently reread amendment.",
        "authoredQuestions": len(questions),
        "recordedAnswerComparedDistinctQuestions": len(answers),
        "recordedChoiceMaskedDistinctQuestions": len(masked),
        "recordedChoiceMaskedWithoutDeclaredPriorExposureDistinctQuestions": len(masked_without_declared_exposure),
        "currentExactHashAnswerCompared": len(current_answers),
        "currentStatusOnlyTransitionCompared": len(status_only - current_answers),
        "currentExplicitlyRereadAmendments": len(amendments),
        "currentTraceableAnswerReview": len(traceable_answers),
        "recordedExplanationReadDistinctQuestions": len(explanations),
        "currentExactOrStatusOnlyExplanationRead": len(current_explanations),
        "currentTraceableExplanationRead": len(traceable_explanations),
        "allCurrentAnswersTraceablyReviewed": set(questions) <= traceable_answers,
        "allCurrentExplanationsTraceablyRead": set(questions) <= traceable_explanations,
        "currentMissingAnswerReview": sorted(set(questions) - traceable_answers),
        "currentMissingExplanationRead": sorted(set(questions) - traceable_explanations),
        "currentRecordedFollowups": current_followups, "rejectedAmendments": rejected_amendments,
        "answerBatches": batches, "explanationFiles": explanation_files, "amendmentFiles": amendment_files,
        "currentQuestionHashes": {qid: v.digest(q) for qid, q in questions.items()},
    }
    v.atomic_write(ROOT / "evidence/content-review-summary.json", report)
    print(json.dumps({key: value for key, value in report.items()
                      if isinstance(value, (int, bool))}, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    summarize()
