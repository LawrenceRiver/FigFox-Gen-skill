import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

import scientific_figure_workflow
from tests.test_artifacts import MANIFEST_PATHS
from tests.test_cli import ROOT, initialize_run, invoke_cli, write_json


REFERENCE_PACK = ROOT / "assets/figurebench-references"
PALETTE_LIBRARY = ROOT / "references/palette-library.json"


class CompleteRunValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.run_root = Path(self.temporary_directory.name) / "run"
        initialize_run(self.run_root)
        for command in ("rank-references", "crop-references", "build-creative-director-prompt"):
            result = invoke_cli(command, self.run_root)
            self.assertEqual(result.returncode, 0, result.stderr)
        write_json(self.run_root / MANIFEST_PATHS["creative_director_brief"], {
            "format": "creative-director-brief-v1",
            "brief": "no_external_svg_needed",
            "ideas": [{
                "id": "baseline", "target_component_id": "encoder",
                "concept": "Use the validated plan.", "visual_intent": "Keep it editable.",
                "construction_plan": "Use Contexts 1–3 without a new external treatment.",
                "requires_svg_evidence": False, "svg_crops": [],
            }],
        })
        result = invoke_cli("build-prompt1", self.run_root)
        self.assertEqual(result.returncode, 0, result.stderr)
        write_json(self.run_root / "run-manifest.json", {"artifacts": dict(MANIFEST_PATHS)})

    def tearDown(self):
        self.temporary_directory.cleanup()

    def validate(self):
        return scientific_figure_workflow.validate_complete_run(
            self.run_root, REFERENCE_PACK, PALETTE_LIBRARY
        )

    def test_complete_single_pass_run_is_valid(self):
        result = self.validate()
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["images"], ["png1.png"])
        self.assertEqual(result["creative_director"], "no_external_svg_needed")

    def test_extra_generated_image_is_rejected(self):
        Image.new("RGB", (4, 4), (1, 2, 3)).save(self.run_root / "unexpected.png")
        with self.assertRaisesRegex(ValueError, "exactly PNG1"):
            self.validate()

    def test_prompt_manifest_tamper_is_rejected(self):
        prompt_path = self.run_root / MANIFEST_PATHS["prompt1"]
        prompt_path.write_text(prompt_path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "does not match deterministic"):
            self.validate()


if __name__ == "__main__":
    unittest.main()
