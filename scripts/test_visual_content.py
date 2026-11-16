"""Failure-path regression checks for the supplied illustrations.

Run with ``python scripts/test_visual_content.py``.  The canonical version marks
whether this is the three-picture pilot or the complete pack.  Asset mutations
stay in TemporaryDirectory; imported source archives and authored files are read
only.  These tests exercise validation boundaries, not teaching effectiveness.
"""
import copy
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET

from validate_visuals import ROOT, validate


class VisualContentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((ROOT / "content/course-visuals.json").read_text(encoding="utf-8"))
        cls.course = json.loads((ROOT / "content/course-pack.json").read_text(encoding="utf-8"))
        # Explicit authoring version, not inferred from a possibly incomplete set.
        cls.pilot = cls.pack["version"].endswith(".pilot")
        cls.asset_root = ROOT / "content"

    def validate_pack(self, pack=None, asset_root=None):
        return validate(self.pack if pack is None else pack, self.course,
                        self.asset_root if asset_root is None else asset_root,
                        pilot=self.pilot)

    @contextmanager
    def temporary_assets(self):
        with tempfile.TemporaryDirectory(prefix="sqlnote-visual-test-") as folder:
            root = Path(folder)
            for visual in self.pack["visuals"]:
                for key in ("pngAsset", "svgAsset"):
                    target = root / visual[key]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(self.asset_root / visual[key], target)
            yield root

    def test_authored_pack_and_bundled_assets_validate(self):
        authored = self.validate_pack()
        bundled = self.validate_pack(asset_root=ROOT / "app/src/main/assets")
        self.assertEqual(3 if self.pilot else 27, authored["visuals"])
        self.assertEqual(authored, bundled)
        self.assertEqual((ROOT / "content/course-visuals.json").read_bytes(),
                         (ROOT / "app/src/main/assets/course-visuals.json").read_bytes())

    def test_unknown_lesson_reference_rejected(self):
        pack = copy.deepcopy(self.pack)
        pack["visuals"][0]["lessonIds"] = ["9-9-99"]
        with self.assertRaises(ValueError):
            self.validate_pack(pack)

    def test_real_but_unlinked_lesson_cannot_replace_alter_placement(self):
        # Both IDs exist.  An existence check or a total coverage count is not
        # enough: picture 11 describes ALTER, not the SQL command categories.
        self.assertIn("1-2-04", {lesson["id"] for lesson in self.course["lessons"]})
        pack = copy.deepcopy(self.pack)
        visual = next(v for v in pack["visuals"] if v["number"] == 11)
        self.assertEqual(["2-1-04"], visual["lessonIds"])
        visual["lessonIds"] = ["1-2-04"]
        # Do not let the separate no-image-rationale requirement accidentally
        # catch this mutation instead of the exact placement contract.
        next(g for g in pack["guides"] if g["lessonId"] == "2-1-04")["unlinkedReason"] = (
            "Synthetic review rationale; the picture has been incorrectly moved.")
        with self.assertRaisesRegex(ValueError, "placement differs"):
            self.validate_pack(pack)

    def test_duplicate_visual_guide_or_placement_rejected(self):
        mutations = []
        pack = copy.deepcopy(self.pack)
        pack["visuals"][1]["id"] = pack["visuals"][0]["id"]
        mutations.append(("visual ID", pack))
        pack = copy.deepcopy(self.pack)
        pack["visuals"][0]["lessonIds"].append(pack["visuals"][0]["lessonIds"][0])
        mutations.append(("same picture placed twice in one lesson", pack))
        pack = copy.deepcopy(self.pack)
        pack["guides"].append(copy.deepcopy(pack["guides"][0]))
        mutations.append(("lesson guide", pack))
        for label, pack in mutations:
            with self.subTest(mutation=label), self.assertRaises(ValueError):
                self.validate_pack(pack)

    def test_missing_or_blank_reading_steps_rejected(self):
        for steps in ([], ["Look at the input", "Read the result"], ["Input", "   ", "Result"]):
            pack = copy.deepcopy(self.pack)
            pack["visuals"][0]["readingSteps"] = steps
            with self.subTest(steps=steps), self.assertRaisesRegex(ValueError, "reading guide"):
                self.validate_pack(pack)

    def test_asset_paths_cannot_escape_or_load_external_content(self):
        paths = ("../visual-11.png", "course-visuals/../../outside.png",
                 "C:/outside.png", "https://example.invalid/visual.png")
        for key in ("pngAsset", "svgAsset"):
            for name in paths:
                pack = copy.deepcopy(self.pack)
                pack["visuals"][0][key] = name
                with self.subTest(field=key, path=name), self.assertRaisesRegex(ValueError, "asset path"):
                    self.validate_pack(pack)

    def test_png_pixel_chunk_corruption_rejected(self):
        with self.temporary_assets() as assets:
            path = assets / self.pack["visuals"][0]["pngAsset"]
            data = bytearray(path.read_bytes())
            position = 8
            while position < len(data):
                length = struct.unpack_from(">I", data, position)[0]
                if data[position + 4:position + 8] == b"IDAT" and length:
                    data[position + 8] ^= 1  # Keep the old CRC, corrupt pixel data.
                    break
                position += length + 12
            else:
                self.fail("Authored PNG has no pixel chunk")
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "Corrupt PNG chunk"):
                self.validate_pack(asset_root=assets)

    def test_svg_active_content_and_external_references_rejected(self):
        bodies = (
            '<script>alert(1)</script>',
            '<image href="https://example.invalid/picture.png"/>',
            '<text onclick="alert(1)">click</text>',
            '<rect fill="url(https://example.invalid/paint)"/>',
            '<text href="file:///private.txt">read</text>',
        )
        with self.temporary_assets() as assets:
            path = assets / self.pack["visuals"][0]["svgAsset"]
            original = path.read_text(encoding="utf-8")
            self.assertIn("</svg>", original)
            for body in bodies:
                path.write_text(original.replace("</svg>", body + "</svg>"), encoding="utf-8")
                with self.subTest(payload=body), self.assertRaisesRegex(
                        ValueError, "Unexpected SVG element|Unsafe SVG attribute|External SVG URL"):
                    self.validate_pack(asset_root=assets)

    def test_asset_text_and_accessible_transcript_must_agree(self):
        with self.temporary_assets() as assets:
            path = assets / self.pack["visuals"][0]["svgAsset"]
            tree = ET.fromstring(path.read_text(encoding="utf-8"))
            text = next(node for node in tree.iter()
                        if node.tag.rsplit("}", 1)[-1] == "text" and node.text)
            text.text += " [changed picture text]"
            path.write_text(ET.tostring(tree, encoding="unicode"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "transcription drift"):
                self.validate_pack(asset_root=assets)

    def test_missing_file_or_wrong_aspect_ratio_rejected(self):
        with self.temporary_assets() as assets:
            (assets / self.pack["visuals"][0]["pngAsset"]).unlink()
            with self.assertRaisesRegex(ValueError, "Missing"):
                self.validate_pack(asset_root=assets)
        with self.temporary_assets() as assets:
            path = assets / self.pack["visuals"][0]["svgAsset"]
            tree = ET.fromstring(path.read_text(encoding="utf-8"))
            tree.set("viewBox", "0 0 2400 1600")
            path.write_text(ET.tostring(tree, encoding="unicode"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "aspect ratio"):
                self.validate_pack(asset_root=assets)


if __name__ == "__main__":
    unittest.main(verbosity=2)
