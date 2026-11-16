"""Tests of review input redaction and masked-ID comparison, using synthetic text."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import blind_review as review
from test_content_validator import sample


class MaskedReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sqld-blind-")
        self.original_root = review.ROOT
        review.ROOT = Path(self.temp.name)
        self.root = review.ROOT
        self.part = sample()
        self.part["questions"] = self.part["questions"][:1]
        q = self.part["questions"][0]
        q["choices"][0]["reason"] = "SECRET_OPTION_REASON"
        q["explanation"]["summary"] = "SECRET_EXPLANATION"
        q["fixture"]["expectedRows"] = [["SECRET_EXPECTED_RESULT"]]
        q["fixture"]["evidence"] = "SECRET_AUTHOR_EVIDENCE"
        (self.root / "part.json").write_text(json.dumps(self.part), encoding="utf-8")

    def tearDown(self):
        review.ROOT = self.original_root
        self.temp.cleanup()

    def prepare(self):
        args = SimpleNamespace(parts=[str(self.root / "part.json")], ids=None,
                               output=str(self.root / "input.json"), choice_map_output=str(self.root / "map.json"))
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            review.prepare(args)
        return review.read(args.output), review.read(args.choice_map_output), stdout.getvalue()

    def decisions(self, public, mapping):
        chosen = next(masked for masked, original in mapping["q"].items() if original == "a")
        decision = dict(inputSha256=public["inputSha256"], method="independent_ai_blind_reasoning_masked_choice_ids",
                        decisions=[dict(questionId="q", choiceIds=[chosen], reasoning="Synthetic test decision")])
        review.write(self.root / "decisions.json", decision)
        return SimpleNamespace(input=str(self.root / "input.json"), decisions=str(self.root / "decisions.json"),
                               choice_map=str(self.root / "map.json"), output=str(self.root / "comparison.json"))

    def test_prepare_redacts_answers_reasons_expected_rows_and_id_mapping(self):
        public, mapping, output = self.prepare()
        self.assertNotIn("SECRET_", output)
        q = public["questions"][0]["question"]
        self.assertEqual(["r1", "r2", "r3", "r4"], [c["id"] for c in q["choices"]])
        self.assertTrue(all(set(c) == {"id", "text"} for c in q["choices"]))
        self.assertNotIn("correctChoiceIds", q)
        self.assertNotIn("expectedRows", q["fixtureInput"])
        self.assertEqual(review.digest(mapping), public["choiceMapSha256"])
        self.assertEqual({"a", "b", "c", "d"}, set(mapping["q"].values()))

    def test_masked_choice_maps_to_author_choice_only_in_comparison(self):
        public, mapping, _ = self.prepare()
        args = self.decisions(public, mapping)
        with contextlib.redirect_stdout(io.StringIO()):
            review.compare(args)
        result = review.read(args.output)
        self.assertEqual(1, result["counts"]["answer_agrees"])
        self.assertEqual(public["choiceMapSha256"], result["choiceMapSha256"])

    def test_tampered_map_is_rejected(self):
        public, mapping, _ = self.prepare()
        args = self.decisions(public, mapping)
        mapping["q"]["r1"], mapping["q"]["r2"] = mapping["q"]["r2"], mapping["q"]["r1"]
        review.write(args.choice_map, mapping)
        with self.assertRaisesRegex(ValueError, "map changed"):
            review.compare(args)

    def test_changed_author_revision_is_not_awarded_old_review(self):
        public, mapping, _ = self.prepare()
        args = self.decisions(public, mapping)
        altered = copy.deepcopy(self.part)
        altered["questions"][0]["version"] = 2
        review.write(self.root / "part.json", altered)
        with contextlib.redirect_stdout(io.StringIO()):
            review.compare(args)
        result = review.read(args.output)
        self.assertEqual(0, result["counts"]["answer_agrees"])
        self.assertEqual(1, result["counts"]["source_changed_requires_review"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
