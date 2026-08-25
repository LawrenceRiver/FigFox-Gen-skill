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
    "build-creative-director-prompt",
    "validate-creative-director",
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


def initialize_run(root):
    (root / "input").mkdir(parents=True)
    (root / "input/methodology.md").write_text(
        "Encode a prompt and synthesize audio.", encoding="utf-8"
    )
    write_json(root / MANIFEST_PATHS["context1"], c1())
    write_json(root / MANIFEST_PATHS["context2"], c2())
    context3 = c3()
    context3["selected_references"][0]["crop_id"] = "container"
    context3["selected_references"][1]["crop_id"] = "arrow"
    context3["coverage_matrix"][0]["crop_ids"] = ["container"]
    context3["coverage_matrix"][1]["crop_ids"] = ["arrow"]
    write_json(root / MANIFEST_PATHS["context3"], context3)
    write_json(
        root / MANIFEST_PATHS["web_manifest"],
        {
            "format": "scholarly-domain-figure-manifest-v1",
            "sources": [
                {
                    "id": "paper-1-piano-roll",
                    "title": "Fixture paper one",
                    "figure": "Figure 1",
                    "source_url": "https://arxiv.org/abs/0001.00001",
                    "evidence_url": "https://arxiv.org/html/0001.00001/figure-1.png",
                    "crop_path": "references/web/crops/piano-roll.png",
                    "inspection": "A retained piano-roll panel with aligned note bars.",
                },
                {
                    "id": "paper-2-encoder",
                    "title": "Fixture paper two",
                    "figure": "Figure 2",
                    "source_url": "https://arxiv.org/abs/0001.00002",
                    "evidence_url": "https://arxiv.org/html/0001.00002/figure-2.png",
                    "crop_path": "references/web/crops/paper-2.png",
                    "inspection": "A retained encoder block and directional connector panel.",
                },
                {
                    "id": "paper-3-decoder",
                    "title": "Fixture paper three",
                    "figure": "Figure 3",
                    "source_url": "https://arxiv.org/abs/0001.00003",
                    "evidence_url": "https://arxiv.org/html/0001.00003/figure-3.png",
                    "crop_path": "references/web/crops/paper-3.png",
                    "inspection": "A retained decoder and structured-output panel.",
                },
            ],
        },
    )
    write_json(
        root / MANIFEST_PATHS["figurebench_crop_request"],
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
                        "human_editable_reason": "the treatment is editable vector geometry",
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
                        "human_editable_reason": "the waveform is a simple path construction",
                    },
                },
            ],
            "basic_geometry": [],
        },
    )
    write_png(root / "references/web/crops/piano-roll.png")
    write_png(root / "references/web/crops/paper-2.png", (45, 75, 105))
    write_png(root / "references/web/crops/paper-3.png", (60, 90, 120))
    write_png(root / MANIFEST_PATHS["png1"], (10, 80, 120))
    write_png(root / MANIFEST_PATHS["png2"], (20, 100, 140))
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80" '
        'viewBox="0 0 120 80"><rect x="5" y="5" width="110" height="70" '
        'fill="#FFFFFF" stroke="#475569"/><path d="M20 40 L100 40" '
        'stroke="#2E5BFF"/><text x="30" y="30">Prompt Encoder</text></svg>'
    )
    svg_path = root / MANIFEST_PATHS["svg1"]
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg, encoding="utf-8")
    write_json(root / MANIFEST_PATHS["diagnosis"], diagnosis())
    write_json(
        root / MANIFEST_PATHS["approved_crop_request"],
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


def invoke_cli(command, run_root=None, *arguments):
    command_line = [sys.executable, str(SCRIPT), command]
    if run_root is not None:
        command_line.extend(("--run", str(run_root)))
    command_line.extend(map(str, arguments))
    return subprocess.run(command_line, cwd=ROOT, text=True, capture_output=True)


def materialize_complete_run(root):
    for command in (
        "rank-references",
        "crop-references",
        "build-creative-director-prompt",
        "build-prompt1",
        "render-svg",
        "crop-svg",
        "build-prompt2",
    ):
        completed = invoke_cli(command, root)
        if completed.returncode != 0:
            raise AssertionError(f"{command} failed: {completed.stderr}")
    write_json(root / "run-manifest.json", {"artifacts": dict(MANIFEST_PATHS)})


class WorkflowCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.run_root = Path(self.temporary_directory.name) / "run"
        initialize_run(self.run_root)

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

        figurebench_request = self.run_root / MANIFEST_PATHS["figurebench_crop_request"]
        figurebench_request_bytes = figurebench_request.read_bytes()
        cropped = self.run_cli("crop-references", "--run", self.run_root)
        self.assertEqual(cropped["crops"], 2)
        self.assertEqual(figurebench_request.read_bytes(), figurebench_request_bytes)
        figurebench_manifest = json.loads(
            (self.run_root / MANIFEST_PATHS["figurebench_crops"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            figurebench_manifest["request"],
            "references/figurebench/crops/request.json",
        )
        self.assertEqual(
            {item["crop_path"] for item in figurebench_manifest["crops"]},
            {
                "references/figurebench/crops/container.png",
                "references/figurebench/crops/arrow.png",
            },
        )
        self.assertTrue((self.run_root / "references/figurebench/crops/container.png").is_file())
        self.assertTrue((self.run_root / "references/figurebench/crops/arrow.png").is_file())

        coverage = self.run_cli("validate-reference-coverage", "--run", self.run_root)
        self.assertEqual(coverage["covered_component_ids"], ["audio", "encoder"])
        palette_result = self.run_cli("validate-palette", "--run", self.run_root)
        self.assertEqual(palette_result["base_palette_id"], "workflow-role-01")

        creative_prompt = self.run_cli(
            "build-creative-director-prompt", "--run", self.run_root
        )
        self.assertEqual(creative_prompt["path"], "creative-director/prompt.md")
        write_json(
            self.run_root / "creative-director/brief.json",
            {
                "format": "creative-director-brief-v1",
                "brief": "no_external_svg_needed",
                "ideas": [
                    {
                        "id": "context-baseline",
                        "target_component_id": "encoder",
                        "concept": "Keep the validated construction plan.",
                        "visual_intent": "Preserve clear editable geometry.",
                        "construction_plan": "Use Contexts 1–3 without a new external treatment.",
                        "requires_svg_evidence": False,
                        "svg_crops": [],
                    }
                ],
            },
        )
        creative_validation = self.run_cli(
            "validate-creative-director", "--run", self.run_root
        )
        self.assertEqual(creative_validation["status"], "no_external_svg_needed")

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

        svg_request = self.run_root / MANIFEST_PATHS["approved_crop_request"]
        svg_request_bytes = svg_request.read_bytes()
        svg_crops = self.run_cli("crop-svg", "--run", self.run_root)
        self.assertEqual(svg_crops["crops"], 1)
        self.assertEqual(svg_request.read_bytes(), svg_request_bytes)
        saved_svg_manifest = json.loads(
            (self.run_root / MANIFEST_PATHS["approved_crops"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            saved_svg_manifest["request"],
            "svg-diagnostic/approved-crops/request.json",
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

        write_json(self.run_root / "run-manifest.json", {"artifacts": dict(MANIFEST_PATHS)})
        validated = self.run_cli("validate-run", "--run", self.run_root)
        self.assertEqual(validated["images"], ["png1.png", "png2-final.png"])
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

    def test_build_prompt1_rejects_missing_scholarly_evidence(self):
        self.run_cli("crop-references", "--run", self.run_root)
        write_json(
            self.run_root / MANIFEST_PATHS["web_manifest"],
            {"format": "scholarly-domain-figure-manifest-v1", "sources": []},
        )

        completed = self.run_cli("build-prompt1", "--run", self.run_root, expected=2)

        self.assertIn("3 or 4 distinct scholarly papers", completed.stderr)

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

    def test_cli_contains_no_reusable_writer_png_or_run_validators(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        function_names = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        self.assertFalse(
            function_names
            & {"_atomic_json", "_verify_png", "_expected_attachments", "_validate_bundle_files"}
        )
        validate_run = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_cmd_validate_run"
        )
        called_names = {
            node.func.id
            for node in ast.walk(validate_run)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertEqual(called_names, {"_run_root", "validate_complete_run"})
        for handler_name in ("_cmd_crop_references", "_cmd_crop_svg"):
            handler = next(
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name == handler_name
            )
            handler_calls = {
                node.func.id
                for node in ast.walk(handler)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            self.assertIn("write_json_atomic", handler_calls)


if __name__ == "__main__":
    unittest.main()
