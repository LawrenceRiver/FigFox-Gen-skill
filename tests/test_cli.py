import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tests.test_artifacts import MANIFEST_PATHS
from tests.test_prompts import c1, c2, c3, diagnosis


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "figure_workflow.py"
COMMANDS = {
    "check-installation",
    "validate-context",
    "rank-references",
    "crop-references",
    "validate-reference-coverage",
    "validate-palette",
    "build-prompt1",
    "inspect-svg",
    "render-svg",
    "validate-diagnosis",
    "crop-svg",
    "build-prompt2",
    "validate-run",
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_png(path, colour=(30, 60, 90)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (24, 16), colour).save(path, format="PNG")


class WorkflowCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.run_root = Path(self.temporary_directory.name) / "run"
        (self.run_root / "input").mkdir(parents=True)
        (self.run_root / "input/methodology.md").write_text(
            "Encode a prompt and synthesize audio.", encoding="utf-8"
        )
        write_json(self.run_root / MANIFEST_PATHS["context1"], c1())
        write_json(self.run_root / MANIFEST_PATHS["context2"], c2())
        context3 = c3()
        context3["selected_references"][0]["crop_id"] = "container"
        context3["selected_references"][1]["crop_id"] = "arrow"
        context3["coverage_matrix"][0]["crop_ids"] = ["container"]
        context3["coverage_matrix"][1]["crop_ids"] = ["arrow"]
        write_json(self.run_root / MANIFEST_PATHS["context3"], context3)
        write_json(self.run_root / MANIFEST_PATHS["web_manifest"], {"sources": []})
        write_json(
            self.run_root / MANIFEST_PATHS["figurebench_crops"],
            {
                "crops": [
                    {
                        "id": "container",
                        "reference_id": "reference-001",
                        "bounds": [0.0, 0.0, 0.5, 0.5],
                        "target_component_id": "encoder",
                        "crop_contract": {
                            "borrow": ["corner radius", "stroke weight"],
                            "must_change": ["source labels", "arrangement"],
                            "human_editable_reason": "editable vector geometry",
                        },
                    },
                    {
                        "id": "arrow",
                        "reference_id": "reference-002",
                        "bounds": [0.25, 0.25, 0.75, 0.75],
                        "target_component_id": "audio",
                        "crop_contract": {
                            "borrow": ["waveform enclosure"],
                            "must_change": ["run palette", "output label"],
                            "human_editable_reason": "simple path construction",
                        },
                    },
                ],
                "basic_geometry": [],
            },
        )
        write_png(self.run_root / "references/web/crops/piano-roll.png")
        write_png(self.run_root / MANIFEST_PATHS["png1"], (10, 80, 120))
        write_png(self.run_root / MANIFEST_PATHS["png2"], (20, 100, 140))
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80" '
            'viewBox="0 0 120 80"><rect x="5" y="5" width="110" height="70" '
            'fill="#FFFFFF" stroke="#475569"/><path d="M20 40 L100 40" '
            'stroke="#2E5BFF"/><text x="30" y="30">Prompt Encoder</text></svg>'
        )
        svg_path = self.run_root / MANIFEST_PATHS["svg1"]
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path.write_text(svg, encoding="utf-8")
        write_json(self.run_root / MANIFEST_PATHS["diagnosis"], diagnosis())
        write_json(
            self.run_root / MANIFEST_PATHS["approved_crops"],
            {
                "crops": [
                    {
                        "crop_id": "encoder",
                        "target_component_id": "encoder",
                        "diagnosis_id": "encoder",
                        "bounds": {"x": 0.0, "y": 0.0, "width": 0.5, "height": 1.0},
                    }
                ]
            },
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_cli(self, command, *arguments, expected=0):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), command, *map(str, arguments)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, expected, completed.stderr)
        if expected == 0:
            self.assertEqual(completed.stderr, "")
            self.assertEqual(completed.stdout.count("\n"), 1)
            return json.loads(completed.stdout)
        self.assertEqual(completed.stdout, "")
        self.assertNotIn("Traceback", completed.stderr)
        self.assertEqual(completed.stderr.count("\n"), 1)
        return completed

    def test_help_exposes_exact_command_set(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        command_line = next(line for line in completed.stdout.splitlines() if line.startswith("  {"))
        self.assertEqual(set(command_line.strip()[1:-1].split(",")), COMMANDS)

    def test_complete_run_uses_every_deterministic_command(self):
        installation = self.run_cli("check-installation", "--root", ROOT)
        self.assertEqual(installation["reference_pack"]["references"], 30)

        for context_number in (1, 2, 3):
            result = self.run_cli(
                "validate-context", "--run", self.run_root, "--context", context_number
            )
            self.assertEqual(result["context"], context_number)

        ranked = self.run_cli("rank-references", "--run", self.run_root)
        self.assertEqual(ranked["candidates"], 30)
        self.assertTrue((self.run_root / MANIFEST_PATHS["figurebench_candidates"]).is_file())

        cropped = self.run_cli("crop-references", "--run", self.run_root)
        self.assertEqual(cropped["crops"], 2)
        self.assertTrue((self.run_root / "references/figurebench/crops/container.png").is_file())
        self.assertTrue((self.run_root / "references/figurebench/crops/arrow.png").is_file())

        coverage = self.run_cli("validate-reference-coverage", "--run", self.run_root)
        self.assertEqual(coverage["covered_component_ids"], ["audio", "encoder"])
        palette_result = self.run_cli("validate-palette", "--run", self.run_root)
        self.assertEqual(palette_result["base_palette_id"], "workflow-role-01")

        prompt1 = self.run_cli("build-prompt1", "--run", self.run_root)
        self.assertEqual(prompt1["attachments"], 3)
        self.assertTrue((self.run_root / MANIFEST_PATHS["prompt1"]).is_file())
        self.assertTrue((self.run_root / MANIFEST_PATHS["prompt1_attachments"]).is_file())

        inspected = self.run_cli("inspect-svg", "--run", self.run_root)
        self.assertFalse(inspected["raster_only"])
        rendered = self.run_cli("render-svg", "--run", self.run_root)
        self.assertEqual(rendered["path"], "svg-diagnostic/png1.5.png")
        diagnosis_result = self.run_cli("validate-diagnosis", "--run", self.run_root)
        self.assertEqual(diagnosis_result["verdicts"], 2)

        svg_crops = self.run_cli("crop-svg", "--run", self.run_root)
        self.assertEqual(svg_crops["crops"], 1)
        saved_svg_manifest = json.loads(
            (self.run_root / MANIFEST_PATHS["approved_crops"]).read_text(encoding="utf-8")
        )
        self.assertNotIn("component_ids", saved_svg_manifest)
        self.assertTrue(
            (self.run_root / "svg-diagnostic/approved-crops/encoder.png").is_file()
        )

        prompt2 = self.run_cli("build-prompt2", "--run", self.run_root)
        self.assertEqual(prompt2["attachments"], 2)
        attachments = json.loads(
            (self.run_root / MANIFEST_PATHS["prompt2_attachments"]).read_text(encoding="utf-8")
        )
        self.assertEqual(sum(item["role"] == "png1_visual_truth" for item in attachments), 1)
        self.assertFalse(any("png1.5" in item["path"].casefold() for item in attachments))

        write_json(
            self.run_root / "run-manifest.json", {"artifacts": dict(MANIFEST_PATHS)}
        )
        validated = self.run_cli("validate-run", "--run", self.run_root)
        self.assertEqual(validated["model_images"], ["png1.png", "png2-final.png"])
        self.assertEqual(validated["diagnostic_roots"], ["svg-diagnostic"])

    def test_expected_failure_is_one_stderr_line_exit_two_without_traceback(self):
        write_json(self.run_root / MANIFEST_PATHS["context1"], {"domain": "broken"})
        completed = self.run_cli(
            "validate-context", "--run", self.run_root, "--context", 1, expected=2
        )
        self.assertIn("context1", completed.stderr)

    def test_build_prompt2_cli_rejects_png15_attachment(self):
        write_json(
            self.run_root / MANIFEST_PATHS["approved_crops"],
            {
                "crops": [
                    {
                        "path": "svg-diagnostic/png1.5.png",
                        "target_component_id": "encoder",
                        "diagnosis": "keep: clear geometry",
                    }
                ]
            },
        )
        write_png(self.run_root / MANIFEST_PATHS["png1_5"])
        completed = self.run_cli("build-prompt2", "--run", self.run_root, expected=2)
        self.assertIn("PNG1.5", completed.stderr)

    def test_cli_scripts_do_not_import_network_search_or_model_sdks(self):
        forbidden_roots = {
            "anthropic",
            "arxiv",
            "boto3",
            "google",
            "httpx",
            "openai",
            "requests",
            "scholarly",
            "serpapi",
        }
        for path in (SCRIPT, ROOT / "scripts/check_installation.py"):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                imported = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported.add(node.module.split(".")[0])
                self.assertFalse(imported & forbidden_roots)


if __name__ == "__main__":
    unittest.main()
