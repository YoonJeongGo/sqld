"""Mutation tests for content quarantine. Uses temporary synthetic input only."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

import validate_content as validator


def sample():
    objective = dict(id="S01", subjectId="sql", topicId="C", title="Test objective",
                     prerequisites=[], synonyms=[], scopeStatus="provisional")
    note = dict(id="note-S01", version=1, objectiveId="S01", title="Test note", summary="Summary",
                sourceIds=["test-source"], verification="document_review",
                blocks=[dict(id=kind, kind=kind, title=kind, text="Substantive synthetic test block") for kind in
                        ["definition", "explain", "example", "compare", "remember", "misconception", "recall"]],
                recallQuestionIds=[f"r{i}" for i in range(3)])
    question = dict(id="q", version=1, subjectId="sql", topicId="C", objectiveIds=["S01"], familyId="family-q",
                    kind="application", title="NVL example", stem="What is the resulting value?",
                    choices=[dict(id="a", text="0", reason="NULL replaced by zero"),
                             dict(id="b", text="NULL", reason="NVL changes NULL"),
                             dict(id="c", text="1", reason="No one constant"),
                             dict(id="d", text="No rows", reason="One input row")], correctChoiceIds=["a"],
                    explanation=dict(summary="Zero", prerequisites=[], conditions=["Only shown input exists"],
                                     steps=[dict(title="Result", text="NVL replacement", table=dict(title="최종 결과", columns=["V"], rows=[["0"]]))],
                                     memory="NULL replacement", relatedNoteId="note-S01"),
                    sourceIds=["test-source"], sourceType="original_practice", verification="document_review", status="published",
                    dialect="Oracle", dialectVersion="19c", difficulty="basic", difficultyReason="One rule",
                    importanceReason="Core rule", tables=[dict(title="T", columns=["x"], rows=[[None]])],
                    sql="SELECT NVL(x,0) FROM T", validationEvidence=["Synthetic test, not learning content"],
                    fixture=dict(schemaSql="CREATE TABLE T(x NUMBER)", setupSql="INSERT INTO T VALUES(NULL)",
                                 query="SELECT NVL(x,0) FROM T", expectedRows=[["0"]], ordered=False,
                                 constraints=["One input row"], sessionSettings=["Oracle19c"], verificationMethod="document_review", evidence="Synthetic"))
    recall = []
    for i in range(3):
        item = copy.deepcopy(question)
        item.update(id=f"r{i}", familyId=f"family-r{i}", kind="recall", title=f"Recall {i}", stem=f"Synthetic rule {i}", sql=None, fixture=None)
        recall.append(item)
    return dict(objectives=[objective], notes=[note], questions=[question] + recall)


class QuarantineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sqld-validator-")
        self.original_root = validator.ROOT
        validator.ROOT = Path(self.temp.name)
        (validator.ROOT / "content").mkdir()
        self.part = sample()
        self.source = dict(sources=[dict(sourceId="test-source", publisher=["Synthetic", "Test"], title="Reference",
                                        url="https://example.test", checkedAt="2026-09-14", accessStatus="retrieved",
                                        usageScope={"fact": "test only"}, license=["No external text"])])

    def tearDown(self):
        validator.ROOT = self.original_root
        self.temp.cleanup()

    def run_check(self):
        root = validator.ROOT
        for name, content in [("part-a", self.part), ("part-b", dict(objectives=[], notes=[], questions=[])), ("sources", self.source)]:
            (root / f"content/{name}.json").write_text(json.dumps(content), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            report = validator.build()
        pack = json.loads((root / "app/src/main/assets/content-pack.json").read_text(encoding="utf-8"))
        return report, pack

    def codes(self):
        report, _ = self.run_check()
        return {i["code"] for i in report["issues"]}

    def write_priority(self, **changes):
        entry = dict(objectiveId="S01", level="core", reason="Prerequisite for reading tables",
                     focusPoints=["Rows and columns"], sourceIds=["test-source"],
                     frequencyStatus="not_measured", frequencyNote="No measured frequency available")
        entry.update(changes)
        path = validator.ROOT / "content/study-priorities.json"
        path.write_text(json.dumps(dict(checkedAt="2026-09-14", methodology="Learning guidance only",
                                       priorities=[entry])), encoding="utf-8")

    def test_priority_cannot_claim_unsupported_frequency_or_untraceable_sources(self):
        self.write_priority(frequencyStatus="official_90_percent", sourceIds=["invented-source"])
        codes = self.codes()
        self.assertIn("frequency_status", codes)
        self.assertIn("source_ref", codes)

    def test_priority_remains_explicitly_attributed_and_survives_pack_generation(self):
        self.write_priority(frequencyStatus="educator_emphasis", frequencyNote="Named author's emphasis; sample not supplied")
        report, pack = self.run_check()
        self.assertFalse(any(i["kind"] == "priority" for i in report["issues"]))
        self.assertEqual("educator_emphasis", pack["studyPriorities"][0]["frequencyStatus"])
        self.assertEqual("Learning guidance only", pack["priorityMethodology"])

    def test_author_quarantine_is_counted_even_when_structure_is_valid(self):
        self.part["questions"][0]["status"] = "quarantined"
        report, pack = self.run_check()
        self.assertEqual(1, report["counts"]["quarantinedQuestions"])
        self.assertEqual(["author_quarantined"], report["quarantined"][0]["reasons"])
        self.assertEqual("quarantined", pack["questions"][0]["status"])

    def add_synthetic_review(self, stem, agrees=True):
        q = self.part["questions"][0]
        # Synthetic evidence tests accounting/quarantine, not a real content review.
        inputs = [dict(question={"id": q["id"]}, sourceQuestionSha256=validator.digest(q))]
        public = dict(questions=inputs, inputSha256=validator.digest(inputs))
        decisions = dict(inputSha256=public["inputSha256"], method="independent_ai_blind_reasoning",
                         decisions=[dict(questionId=q["id"], choiceIds=["a" if agrees else "b"], reasoning="Synthetic test")])
        result = dict(inputSha256=public["inputSha256"], decisionsSha256=validator.digest(decisions),
                      counts={"answer_agrees": int(agrees), "answer_disagrees": int(not agrees)},
                      results=[dict(questionId=q["id"], status="answer_agrees" if agrees else "answer_disagrees",
                                    sourceQuestionSha256=validator.digest(q))])
        for suffix, value in [("input", public), ("decisions", decisions), ("comparison", result)]:
            validator.atomic_write(validator.ROOT / f"qa/content-{stem}-{suffix}.json", value)

    def test_valid_originals_remain_unmodified_and_source_fields_normalize(self):
        original = copy.deepcopy(self.part)
        report, pack = self.run_check()
        self.assertTrue(report["gates"]["structurePassed"])
        self.assertEqual(4, report["counts"]["eligibleQuestions"])
        self.assertEqual(original, self.part)
        self.assertEqual("Synthetic; Test", pack["sources"][0]["publisher"])
        self.assertEqual("fact: test only", pack["sources"][0]["usageScope"])

    def test_question_correction_is_exported_for_android_without_changing_question(self):
        q = self.part["questions"][0]
        q["version"] = 2
        q["correction"] = dict(previousVersion=1, reason="Clarify NULL condition", date="2026-09-14",
                               previousFamilyId="historical-family")
        before = copy.deepcopy(q)
        report, pack = self.run_check()
        self.assertEqual([dict(questionId=q["id"], fromVersion=1, toVersion=2,
                               reason="Clarify NULL condition", at="2026-09-14")], pack["corrections"])
        self.assertEqual(before, next(x for x in pack["questions"] if x["id"] == q["id"]))
        self.assertEqual(before, self.part["questions"][0])
        self.assertEqual(1, report["counts"]["corrections"])

    def test_duplicate_choice_id_quarantines_only_corrupted_question(self):
        self.part["questions"][0]["choices"][1]["id"] = "a"
        report, pack = self.run_check()
        self.assertEqual(1, report["counts"]["quarantinedQuestions"])
        self.assertEqual("quarantined", pack["questions"][0]["status"])
        self.assertTrue(all(q["status"] == "published" for q in pack["questions"][1:]))

    def test_duplicate_choice_text_is_invalid(self):
        self.part["questions"][0]["choices"][1]["text"] = "0"
        self.assertIn("choice_text_unique", self.codes())

    def test_spaces_are_significant_in_choice_values(self):
        for choice, text in zip(self.part["questions"][0]["choices"], ["A B", "AB", " A B ", "B"]):
            choice["text"] = text
        self.assertNotIn("choice_text_unique", self.codes())

    def test_exactly_one_existing_answer_required(self):
        self.part["questions"][0]["correctChoiceIds"] = ["a", "z"]
        self.assertIn("one_correct_choice", self.codes())

    def test_missing_explanation_and_reason_are_not_published(self):
        self.part["questions"][0]["choices"][1]["reason"] = ""
        self.part["questions"][0]["explanation"]["steps"] = []
        report, pack = self.run_check()
        self.assertEqual(1, report["counts"]["schemaUnsafeOmitted"])
        self.assertEqual(3, len(pack["questions"]))

    def test_missing_source_reference(self):
        self.part["questions"][0]["sourceIds"] = ["missing"]
        self.assertIn("source_ref", self.codes())

    def test_numeric_cells_are_not_silently_coerced(self):
        self.part["questions"][0]["tables"][0]["rows"] = [[0]]
        self.assertIn("table_cell_type", self.codes())

    def test_row_width_is_checked(self):
        self.part["questions"][0]["tables"][0]["rows"] = [[None, "extra"]]
        self.assertIn("table_width", self.codes())

    def test_missing_sql_fixture(self):
        self.part["questions"][0]["fixture"] = None
        self.assertIn("missing_sql_fixture", self.codes())

    def test_fixture_preserves_literal_whitespace_and_case(self):
        q = self.part["questions"][0]
        q["sql"] = "SELECT TRIM(' A B ') FROM DUAL"
        q["fixture"]["query"] = "SELECT TRIM('AB') FROM DUAL"
        self.assertIn("fixture_query_mismatch", self.codes())
        self.assertNotEqual(validator.canonical_sql("SELECT 'A' FROM T"), validator.canonical_sql("SELECT 'a' FROM T"))

    def test_dml_setup_sequence_and_final_select_are_accepted(self):
        q = self.part["questions"][0]
        q["sql"] = "UPDATE T SET x=0; SELECT x FROM T"
        q["fixture"]["setupSql"] += "; COMMIT; UPDATE T SET x=0;"
        q["fixture"]["query"] = "SELECT x FROM T"
        self.assertNotIn("fixture_query_mismatch", self.codes())

    def test_bag_comparison_keeps_duplicate_multiplicity(self):
        self.part["questions"][0]["fixture"]["expectedRows"] = [["0"], ["0"]]
        self.assertIn("fixture_explanation_result_mismatch", self.codes())

    def test_bag_comparison_keeps_null_and_empty_distinct(self):
        q = self.part["questions"][0]
        q["fixture"]["expectedRows"] = [[None]]
        q["explanation"]["steps"][0]["table"]["rows"] = [[""]]
        self.assertIn("fixture_explanation_result_mismatch", self.codes())

    def test_unordered_result_accepts_permutation(self):
        q = self.part["questions"][0]
        q["fixture"]["expectedRows"] = [[None], ["0"], ["0"]]
        q["explanation"]["steps"][0]["table"]["rows"] = [["0"], [None], ["0"]]
        self.assertNotIn("fixture_explanation_result_mismatch", self.codes())

    def test_family_overlap_and_incomplete_mock_are_quarantined(self):
        q = copy.deepcopy(self.part["questions"][0])
        q.update(id="mock-q", kind="mock", mockSetId="mock-1", sourceType="original_mock")
        self.part["questions"].append(q)
        codes = self.codes()
        self.assertIn("practice_mock_family_overlap", codes)
        self.assertIn("duplicate_family", codes)
        self.assertIn("mock_sets_incomplete", codes)

    def test_missing_recall_minimum_is_reported(self):
        self.part["questions"] = self.part["questions"][:3]
        self.part["notes"][0]["recallQuestionIds"] = ["r0", "r1"]
        report, _ = self.run_check()
        self.assertFalse(report["gates"]["objectiveMinimumsPassed"])

    def test_table_column_renaming_does_not_hide_sql_template_candidate(self):
        first = self.part["questions"][0]
        renamed = copy.deepcopy(first)
        renamed.update(id="renamed", familyId="another-family", stem="Renamed dataset", sql="SELECT NVL(amount,0) FROM Payments")
        renamed["fixture"]["query"] = renamed["sql"]
        self.part["questions"].append(renamed)
        report, _ = self.run_check()
        pair = next(x for x in report["nearDuplicateCandidates"] if x["left"] == "q" and x["right"] == "renamed")
        self.assertTrue(pair["sameIdentifierNormalizedSql"])
        self.assertEqual("manual_review_candidate_only", pair["disposition"])

    def test_current_independent_disagreement_quarantines_one_question(self):
        self.add_synthetic_review("disagreement", agrees=False)
        report, pack = self.run_check()
        self.assertEqual(1, report["counts"]["quarantinedQuestions"])
        self.assertIn("independent_answer_disagreement", [i["code"] for i in report["issues"]])
        self.assertEqual("quarantined", pack["questions"][0]["status"])

    def test_manual_template_duplicate_is_quarantined_even_when_wording_differs(self):
        left, right = self.part["questions"][:2]
        validator.atomic_write(validator.ROOT / "evidence/content-duplicate-review.json", dict(decisions=[dict(
            left=left["id"], right=right["id"], leftSha256=validator.digest(left), rightSha256=validator.digest(right),
            decision="same_family_template", reason="Synthetic manual finding, unrelated to production content")]))
        report, pack = self.run_check()
        self.assertIn("manual_same_family_template", [i["code"] for i in report["issues"]])
        self.assertEqual("quarantined", next(q for q in pack["questions"] if q["id"] == right["id"])["status"])

    def test_overlapping_review_passes_count_one_unique_question(self):
        self.add_synthetic_review("one")
        self.add_synthetic_review("two")
        report, _ = self.run_check()
        review = report["independentReview"]
        self.assertEqual(2, review["recordedReviewPasses"])
        self.assertEqual(1, review["reviewedSnapshotQuestions"])
        self.assertEqual(1, review["currentUnchanged"])
        self.part["questions"][0]["version"] = 2
        report, _ = self.run_check()
        self.assertEqual(0, report["independentReview"]["currentUnchanged"])
        self.assertEqual(1, report["independentReview"]["currentChanged"])

    def test_prior_answer_exposure_is_not_erased_by_rereview(self):
        self.add_synthetic_review("exposed")
        path = validator.ROOT / "qa/content-exposed-decisions.json"
        decisions = json.loads(path.read_text(encoding="utf-8"))
        decisions["priorAnswerExposure"] = True
        validator.atomic_write(path, decisions)
        path = validator.ROOT / "qa/content-exposed-comparison.json"
        comparison = json.loads(path.read_text(encoding="utf-8"))
        comparison["decisionsSha256"] = validator.digest(decisions)
        validator.atomic_write(path, comparison)
        report, _ = self.run_check()
        self.assertEqual(1, report["independentReview"]["currentWithDeclaredPriorAnswerExposure"])
        self.assertTrue(report["independentReview"]["batches"][0]["priorAnswerExposureDeclared"])

    def test_publication_transition_is_proven_without_carrying_semantic_edits(self):
        q = self.part["questions"][0]
        q["status"] = "quarantined"
        self.add_synthetic_review("publication")
        q["status"] = "published"
        report, _ = self.run_check()
        self.assertEqual(0, report["independentReview"]["currentUnchanged"])
        self.assertEqual(1, report["independentReview"]["currentWithVerifiedStatusOnlyChange"])
        self.assertEqual(1, report["independentReview"]["currentUnchangedOrStatusOnly"])
        q["explanation"]["memory"] += " Edited meaning"
        report, _ = self.run_check()
        self.assertEqual(0, report["independentReview"]["currentUnchangedOrStatusOnly"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
