import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/curate_figurebench_reference_pack.py"


def make_image(path: Path, colour=(20, 40, 60)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (1400, 800), colour).save(path)


class ReferencePackCliTests(unittest.TestCase):
    def test_prepare_scans_images_only_and_creates_max_1200_thumbnails(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            dataset = root / "dataset"
            make_image(dataset / "images/paper-a/figure.png")
            make_image(dataset / "test_images/never-include.png")
            review = root / "review"
            manifest = root / "candidates.json"

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "prepare", "--dataset", str(dataset), "--output", str(review), "--manifest", str(manifest)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            candidates = json.loads(manifest.read_text(encoding="utf-8"))["candidates"]
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["source_path"], "images/paper-a/figure.png")
            with Image.open(review / candidates[0]["thumbnail"]) as thumbnail:
                self.assertLessEqual(max(thumbnail.size), 1200)

    def test_materialize_requires_thirty_reviewed_unique_development_images(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            dataset = root / "dataset"
            selections = []
            for position in range(1, 31):
                relative_path = f"images/paper-{position:03d}/figure.png"
                make_image(dataset / relative_path, (position, 40, 60))
                selections.append({
                    "source_path": relative_path,
                    "source_id": f"paper-{position:03d}",
                    "source_kind": "paper",
                    "license": "CC-BY-4.0",
                    "attribution": "FigureBench / verify original source",
                    "components": ["rounded_container"],
                    "layout_family": "horizontal_flow",
                    "human_editable_signals": ["flat fill", "consistent stroke"],
                    "description": "Editable grouped flow",
                    "rights_reviewed": True,
                    "human_editability_reviewed": True,
                })
            selection_path = root / "selection.json"
            selection_path.write_text(json.dumps({"selections": selections}), encoding="utf-8")
            output = root / "pack"

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "materialize", "--dataset", str(dataset), "--selection", str(selection_path), "--output", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(list(output.glob("reference-*.png"))), 30)
            self.assertEqual(len(json.loads((output / "index.json").read_text(encoding="utf-8"))["references"]), 30)
            with Image.open(output / "reference-001.png") as normalized:
                self.assertEqual(normalized.mode, "RGB")
                self.assertLessEqual(max(normalized.size), 1600)

