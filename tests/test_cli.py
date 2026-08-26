import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tests.test_artifacts import MANIFEST_PATHS
from tests.test_prompts import c1, c2, c3


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/figure_workflow.py"
COMMANDS = {
    "check-installation", "validate-context", "rank-references", "crop-references",
    "validate-reference-coverage", "validate-palette", "select-palette", "build-creative-director-prompt",
    "validate-creative-director", "build-prompt1", "validate-run",
}


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_png(path: Path, colour=(30, 60, 90)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (24, 16), colour).save(path, format="PNG")


def invoke_cli(command, run_root=None, *arguments):
    command_line = [sys.executable, str(SCRIPT), command]
    if run_root is not None:
        command_line.extend(("--run", str(run_root)))
    command_line.extend(map(str, arguments))
    return subprocess.run(command_line, cwd=ROOT, text=True, capture_output=True)


def initialize_run(root: Path):
    (root / "input").mkdir(parents=True)
    (root / "input/methodology.md").write_text("Encode a prompt and synthesize audio.", encoding="utf-8")
    write_json(root / MANIFEST_PATHS["context1"], c1())
    write_json(root / MANIFEST_PATHS["context2"], c2())
    context3 = c3()
    context3["selected_references"][0].update(crop_id="container", crop_path="references/figurebench/crops/container.png")
    context3["selected_references"][1].update(crop_id="arrow", crop_path="references/figurebench/crops/arrow.png")
    context3["selected_references"][0]["crop_contract"] = {"borrow": ["corner radius"], "must_change": ["source labels"], "human_editable_reason": "editable geometry"}
    context3["selected_references"][1]["crop_contract"] = {"borrow": ["waveform path"], "must_change": ["output label"], "human_editable_reason": "editable path"}
    context3["coverage_matrix"][0]["crop_ids"] = ["container"]
    context3["coverage_matrix"][1]["crop_ids"] = ["arrow"]
    write_json(root / MANIFEST_PATHS["context3"], context3)
    write_json(root / MANIFEST_PATHS["web_manifest"], {
        "format": "scholarly-domain-figure-manifest-v1",
        "sources": [
            {"id": "paper-1", "title": "Fixture one", "figure": "Figure 1", "source_url": "https://arxiv.org/abs/0001.00001", "evidence_url": "https://arxiv.org/html/0001.00001/figure.svg", "crop_path": "references/web/crops/piano-roll.png", "inspection": "Visible structured grid."},
            {"id": "paper-2", "title": "Fixture two", "figure": "Figure 2", "source_url": "https://arxiv.org/abs/0001.00002", "evidence_url": "https://arxiv.org/html/0001.00002/figure.svg", "crop_path": "references/web/crops/paper-2.png", "inspection": "Visible encoder."},
            {"id": "paper-3", "title": "Fixture three", "figure": "Figure 3", "source_url": "https://arxiv.org/abs/0001.00003", "evidence_url": "https://arxiv.org/html/0001.00003/figure.svg", "crop_path": "references/web/crops/paper-3.png", "inspection": "Visible output."},
        ],
    })
    for name, colour in (("piano-roll.png", (30, 60, 90)), ("paper-2.png", (45, 75, 105)), ("paper-3.png", (60, 90, 120))):
        write_png(root / f"references/web/crops/{name}", colour)
    write_json(root / MANIFEST_PATHS["figurebench_crop_request"], {
        "crops": [
            {"id": "container", "reference_id": "reference-001", "bounds": [0.0, 0.0, 0.5, 0.5], "target_component_id": "encoder", "crop_contract": {"borrow": ["corner radius"], "must_change": ["source labels"], "human_editable_reason": "editable geometry"}},
            {"id": "arrow", "reference_id": "reference-002", "bounds": [0.25, 0.25, 0.75, 0.75], "target_component_id": "audio", "crop_contract": {"borrow": ["waveform path"], "must_change": ["output label"], "human_editable_reason": "editable path"}},
        ],
        "basic_geometry": [],
    })
    write_png(root / MANIFEST_PATHS["png1"], (10, 80, 120))


class WorkflowCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.run_root = Path(self.temporary_directory.name) / "run"
        initialize_run(self.run_root)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_cli(self, command, *arguments, expected=0):
        completed = invoke_cli(command, self.run_root, *arguments)
        self.assertEqual(completed.returncode, expected, completed.stderr)
        if expected == 0:
            self.assertEqual(completed.stderr, "")
            return json.loads(completed.stdout)
        self.assertEqual(completed.stdout, "")
        self.assertNotIn("Traceback", completed.stderr)
        return completed

    def test_help_exposes_single_pass_command_set(self):
        completed = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        command_line = next(line for line in completed.stdout.splitlines() if line.startswith("  {"))
        self.assertEqual(set(command_line.strip()[1:-1].split(",")), COMMANDS)
        self.assertNotIn("build-prompt2", completed.stdout)
        self.assertNotIn("inspect-svg", completed.stdout)

    def test_single_pass_run(self):
        self.assertEqual(self.run_cli("validate-context", "--context", 1)["context"], 1)
        self.assertEqual(self.run_cli("validate-context", "--context", 2)["context"], 2)
        self.assertEqual(self.run_cli("validate-context", "--context", 3)["context"], 3)
        selected = self.run_cli("select-palette", "--seed", 11)
        self.assertEqual(selected["palette_count"], 13)
        self.assertEqual(selected["base_palette_id"], "epitope-blue-coral-01")
        self.assertEqual(self.run_cli("rank-references")["candidates"], 30)
        self.run_cli("crop-references")
        self.run_cli("validate-reference-coverage")
        self.assertEqual(self.run_cli("validate-palette")["base_palette_id"], "epitope-blue-coral-01")

        creative_prompt = self.run_cli("build-creative-director-prompt")
        self.assertEqual(creative_prompt["path"], "creative-director/prompt.md")
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
        self.assertEqual(self.run_cli("validate-creative-director")["status"], "no_external_svg_needed")
        self.assertEqual(self.run_cli("build-prompt1")["path"], "prompt-1")
        write_json(self.run_root / "run-manifest.json", {"artifacts": dict(MANIFEST_PATHS)})
        result = self.run_cli("validate-run")
        self.assertEqual(result["images"], ["png1.png"])
        self.assertEqual(result["creative_director"], "no_external_svg_needed")

    def test_build_prompt1_requires_creative_director_brief(self):
        self.run_cli("rank-references")
        self.run_cli("crop-references")
        completed = self.run_cli("build-prompt1", expected=2)
        self.assertIn("Creative Director prompt and brief", completed.stderr)


if __name__ == "__main__":
    unittest.main()
