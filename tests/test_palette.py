import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scientific_figure_rag.palette import select_palettes


ROOT = Path(__file__).resolve().parents[1]


class PaletteSelectionTests(unittest.TestCase):
    def test_selects_tag_and_role_matching_palettes_without_image_fields(self):
        result = select_palettes(
            {"tags": ["biomedical", "contrast"], "required_roles": ["ink", "accent"]}
        )

        self.assertEqual(result["palettes"][0]["id"], "biomedical-contrast-01")
        self.assertNotIn("image", json.dumps(result).lower())
        self.assertEqual(result["selection_basis"]["top_k"], 3)

    def test_preserves_groups_and_returns_colour_roles(self):
        result = select_palettes({"tags": ["workflow"], "required_roles": ["primary", "accent"]})

        palette = result["palettes"][0]
        self.assertEqual(palette["id"], "workflow-role-01")
        self.assertGreaterEqual(len(palette["colours"]), 4)
        self.assertIn("primary", {colour["role"] for colour in palette["colours"]})
        self.assertIn("accent", {colour["role"] for colour in palette["colours"]})


class PaletteCliTests(unittest.TestCase):
    def test_cli_returns_palette_selection_from_planning_json(self):
        plan = {"tags": ["biomedical", "contrast"], "required_roles": ["ink", "accent"]}
        script = ROOT / "scripts/figurebench_rag.py"
        with tempfile.TemporaryDirectory() as temporary_directory:
            plan_path = Path(temporary_directory) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(script), "palettes", "--planning-json", str(plan_path)],
                capture_output=True,
                text=True,
                check=True,
            )

        self.assertEqual(json.loads(completed.stdout)["palettes"][0]["id"], "biomedical-contrast-01")


class SkillDocumentationTests(unittest.TestCase):
    def test_skill_documents_inline_colour_planning_and_image_free_palette_library(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        palette_reference = (ROOT / "references/palette-rag.md").read_text(encoding="utf-8")

        self.assertIn("Color Planning", skill)
        self.assertIn("does not add a model call", skill)
        self.assertIn("palette-library.json", palette_reference)
        self.assertIn("must not store screenshots", palette_reference)


if __name__ == "__main__":
    unittest.main()
