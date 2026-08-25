import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

import scientific_figure_workflow
from tests.test_artifacts import MANIFEST_PATHS
from tests.test_cli import ROOT, initialize_run, materialize_complete_run, write_json


REFERENCE_PACK = ROOT / "assets/figurebench-references"
PALETTE_LIBRARY = ROOT / "references/palette-library.json"


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def alter_one_pixel(path):
    with Image.open(path) as image:
        altered = image.convert(image.mode)
    pixel = altered.getpixel((0, 0))
    if isinstance(pixel, tuple):
        changed = tuple((channel + 1) % 256 for channel in pixel)
    else:
        changed = (pixel + 1) % 256
    altered.putpixel((0, 0), changed)
    altered.save(path, format="PNG")


class CompleteRunValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.run_root = Path(self.temporary_directory.name) / "run"
        initialize_run(self.run_root)
        materialize_complete_run(self.run_root)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def validate(self):
        return scientific_figure_workflow.validate_complete_run(
            self.run_root, REFERENCE_PACK, PALETTE_LIBRARY
        )

    def test_complete_valid_run_is_verified_without_mutation(self):
        before = snapshot(self.run_root)

        result = self.validate()

        self.assertEqual(result["images"], ["png1.png", "png2-final.png"])
        self.assertEqual(result["diagnostic_roots"], ["svg-diagnostic"])
        self.assertEqual(snapshot(self.run_root), before)

    def test_svg_chain_rejects_tampered_png15_decoded_pixels(self):
        alter_one_pixel(self.run_root / MANIFEST_PATHS["png1_5"])

        with self.assertRaisesRegex(ValueError, r"PNG1\.5.*decoded pixels"):
            self.validate()

    def test_svg_chain_rejects_tampered_approved_crop_pixels(self):
        alter_one_pixel(self.run_root / "svg-diagnostic/approved-crops/encoder.png")

        with self.assertRaisesRegex(ValueError, "approved SVG crop.*decoded pixels"):
            self.validate()

    def test_svg_chain_rejects_tampered_approved_crop_metadata(self):
        manifest_path = self.run_root / MANIFEST_PATHS["approved_crops"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["crops"][0]["diagnosis"] = "keep: forged metadata"
        write_json(manifest_path, manifest)

        with self.assertRaisesRegex(ValueError, "approved SVG crop manifest"):
            self.validate()

    def test_figurebench_chain_rejects_tampered_crop_pixels(self):
        alter_one_pixel(self.run_root / "references/figurebench/crops/container.png")

        with self.assertRaisesRegex(ValueError, "FigureBench crop.*decoded pixels"):
            self.validate()

    def test_prompt2_manifest_rejects_png15_attachment(self):
        path = self.run_root / MANIFEST_PATHS["prompt2_attachments"]
        attachments = json.loads(path.read_text(encoding="utf-8"))
        attachments.append(
            {
                "path": "svg-diagnostic/png1.5.png",
                "role": "approved_svg_crop",
                "target_component_id": "encoder",
                "diagnosis": "keep: forged diagnostic render attachment",
            }
        )
        write_json(path, attachments)

        with self.assertRaisesRegex(ValueError, "PNG1.5"):
            self.validate()

    def test_svg_chain_summary_never_returns_png15_as_attachment(self):
        context2 = json.loads(
            (self.run_root / MANIFEST_PATHS["context2"]).read_text(encoding="utf-8")
        )
        component_ids = [component["id"] for component in context2["components"]]

        result = scientific_figure_workflow.validate_svg_diagnostic_chain(
            self.run_root, component_ids
        )

        self.assertEqual(result["approved_crops"], 1)
        self.assertNotIn("png1.5.png", json.dumps(result).casefold())

    def test_atomic_json_writer_and_png_verifier_are_stable_exports(self):
        destination = self.run_root / "scratch/result.json"
        scientific_figure_workflow.write_json_atomic(destination, {"b": 2, "a": 1})

        self.assertEqual(
            destination.read_text(encoding="utf-8"),
            '{\n  "a": 1,\n  "b": 2\n}\n',
        )
        summary = scientific_figure_workflow.verify_png(
            self.run_root / MANIFEST_PATHS["png2"], "PNG2"
        )
        self.assertEqual(summary["format"], "PNG")
        self.assertIs(
            scientific_figure_workflow.validate_prompt_bundle,
            __import__("scientific_figure_workflow.prompts", fromlist=["validate_prompt_bundle"]).validate_prompt_bundle,
        )

    def test_atomic_json_writer_rejects_a_symlinked_ancestor(self):
        outside = Path(self.temporary_directory.name) / "outside"
        (outside / "nested").mkdir(parents=True)
        alias = self.run_root / "alias"
        alias.symlink_to(outside, target_is_directory=True)

        with self.assertRaisesRegex(ValueError, "symlink"):
            scientific_figure_workflow.write_json_atomic(
                alias / "nested/result.json", {"must_not": "escape"}
            )

        self.assertFalse((outside / "nested/result.json").exists())


if __name__ == "__main__":
    unittest.main()
