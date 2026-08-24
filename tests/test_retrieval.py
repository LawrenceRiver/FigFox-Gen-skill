import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scientific_figure_rag.index import (
    build_index,
    build_iteration_brief,
    build_png_to_svg_reconstruction_brief,
    derive_geometry_lexicon,
    export_public_bundle,
    query_index,
)


class RetrievalTest(unittest.TestCase):
    def test_indexes_local_figures_and_prioritizes_method_and_structure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory) / "figurebench"
            dataset.mkdir()
            (dataset / "transformer.png").write_bytes(b"not a real image")
            (dataset / "transformer.json").write_text(
                json.dumps(
                    {
                        "caption": "Overview of a transformer encoder with attention blocks and residual links.",
                        "domain": "machine learning",
                        "figure_type": "method_overview",
                        "layout": "horizontal_flow",
                        "topology": ["input", "encoder", "attention", "output"],
                        "visual_primitives": ["rounded_module", "directed_arrow"],
                    }
                ),
                encoding="utf-8",
            )
            (dataset / "cell.png").write_bytes(b"not a real image")
            (dataset / "cell.json").write_text(
                json.dumps(
                    {
                        "caption": "Microscopy images of cell morphology under treatment.",
                        "domain": "biology",
                        "figure_type": "result_panel",
                        "layout": "grid",
                        "topology": ["control", "treatment"],
                        "visual_primitives": ["raster_panel", "scale_bar"],
                    }
                ),
                encoding="utf-8",
            )
            index_path = Path(temporary_directory) / "index.sqlite"

            summary = build_index(dataset, index_path)
            results = query_index(
                index_path,
                methodology="A transformer encoder improves attention routing for sequence modeling.",
                figure_intent="Explain a method overview with directed processing stages.",
                requested_structure={
                    "figure_type": "method_overview",
                    "layout": "horizontal_flow",
                    "topology": ["input", "encoder", "attention", "output"],
                    "visual_primitives": ["rounded_module", "directed_arrow"],
                },
                top_k=1,
            )

            self.assertEqual(summary["indexed"], 2)
            self.assertEqual(results[0]["source_path"], str(dataset / "transformer.png"))
            self.assertGreater(results[0]["scores"]["semantic"], 0)
            self.assertGreater(results[0]["scores"]["structure"], 0)
            self.assertNotIn("image_bytes", results[0])

    def test_geometry_lexicon_and_refinement_brief_keep_generation_contract(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory) / "figurebench"
            image = dataset / "raw/images/1111.00001/1111.00001_method.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"not a real image")
            manifest = dataset / "manifests/splits/geometry_source_v1/sources.jsonl"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps(
                    {
                        "relative_path": "images/1111.00001/1111.00001_method.png",
                        "partition": "extraction_library_source",
                        "source_id": "1111.00001",
                        "source_group_id": "group_a",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            index_path = Path(temporary_directory) / "index.sqlite"
            build_index(dataset, index_path)

            lexicon = derive_geometry_lexicon(index_path)
            brief = build_iteration_brief(
                generation_contract={
                    "modules": ["input", "encoder", "output"],
                    "arrows": [["input", "encoder"], ["encoder", "output"]],
                    "labels": ["Input", "Encoder", "Output"],
                    "primary_layout": "horizontal_flow",
                },
                geometry_lexicon=lexicon,
            )

            self.assertEqual(lexicon["indexed_figures"], 1)
            self.assertEqual(brief["protected_generation_contract"]["modules"], ["input", "encoder", "output"])
            self.assertIn("module semantics", brief["forbidden_changes"])
            self.assertIn("container geometry", brief["allowed_changes"])

    def test_png_to_svg_reconstruction_brief_preserves_meaning_and_prunes_ai_artifacts(self):
        reconstruction = build_png_to_svg_reconstruction_brief(
            first_draft_png="/tmp/latent-diffusion-first-draft.png",
            generation_contract={
                "canvas": {"width": 1600, "height": 900},
                "modules": [
                    {"id": "input", "bounds": [40, 220, 220, 120], "label": "Input"},
                    {"id": "encoder", "bounds": [350, 220, 220, 120], "label": "Encoder"},
                ],
                "arrows": [{"from": "input", "to": "encoder"}],
                "labels": ["Input", "Encoder"],
                "primary_layout": "horizontal_flow",
                "colour_contract": {
                    "source": {"kind": "approved_library", "palette_id": "top-journal-neutral-01"},
                    "allowed_hex": ["#FFFFFF", "#172033", "#2563EB"],
                },
                "scientific_assets": [{"id": "protein", "kind": "complex_raster_asset"}],
            },
            geometry_lexicon={"composition_families": ["sequential-band composition"]},
            inspection={
                "issues": [
                    {"kind": "gradient_fill", "target": "encoder"},
                    {"kind": "misaligned_arrow", "target": "input->encoder"},
                ]
            },
        )

        self.assertEqual(reconstruction["phase"], "semantic PNG-to-SVG reconstruction")
        self.assertEqual(reconstruction["raster_source"], "/tmp/latent-diffusion-first-draft.png")
        self.assertEqual(reconstruction["semantic_truth"]["modules"][1]["id"], "encoder")
        self.assertEqual(reconstruction["semantic_truth"]["arrows"], [{"from": "input", "to": "encoder"}])
        self.assertEqual(reconstruction["palette_policy"]["palette_id"], "top-journal-neutral-01")
        self.assertIn("gradient_fill", reconstruction["reconstruction_targets"])
        self.assertTrue(any("do not pixel-trace" in rule for rule in reconstruction["svg_reconstruction_rules"]))
        self.assertIn("second image-generation call", reconstruction["second_generation_boundary"])
        self.assertIn("module semantics", reconstruction["forbidden_changes"])

    def test_png_to_svg_reconstruction_rejects_an_unidentified_palette_group(self):
        with self.assertRaisesRegex(ValueError, "frozen palette source"):
            build_png_to_svg_reconstruction_brief(
                first_draft_png="/tmp/draft.png",
                generation_contract={
                    "colour_contract": {"allowed_hex": ["#FFFFFF", "#112233"]},
                },
                geometry_lexicon={},
                inspection={},
            )

    def test_public_export_excludes_raw_image_paths_and_corpus_text(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory) / "dataset"
            dataset.mkdir()
            image = dataset / "private.png"
            image.write_bytes(b"not a real image")
            (dataset / "private.json").write_text(
                json.dumps({"caption": "Private long-form source text must not be exported.", "layout": "grid"}),
                encoding="utf-8",
            )
            index_path = Path(temporary_directory) / "index.sqlite"
            bundle_path = Path(temporary_directory) / "public.jsonl"
            build_index(dataset, index_path)

            summary = export_public_bundle(index_path, bundle_path)
            payload = bundle_path.read_text(encoding="utf-8")

            self.assertEqual(summary["exported"], 1)
            self.assertNotIn(str(image), payload)
            self.assertNotIn("Private long-form", payload)
            self.assertIn("CC-BY-4.0", payload)

    def test_cli_writes_a_geometry_lexicon(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory) / "dataset"
            dataset.mkdir()
            (dataset / "figure.png").write_bytes(b"not a real image")
            (dataset / "figure.json").write_text(json.dumps({"layout": "grid"}), encoding="utf-8")
            index_path = Path(temporary_directory) / "index.sqlite"
            lexicon_path = Path(temporary_directory) / "lexicon.json"
            script = Path(__file__).resolve().parents[1] / "scripts/figurebench_rag.py"

            subprocess.run(
                [sys.executable, str(script), "index", "--dataset", str(dataset), "--index", str(index_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(script), "lexicon", "--index", str(index_path), "--output", str(lexicon_path)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(json.loads(lexicon_path.read_text(encoding="utf-8"))["indexed_figures"], 1)

    def test_cli_writes_a_png_to_svg_reconstruction_brief(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            contract_path = temporary / "contract.json"
            lexicon_path = temporary / "lexicon.json"
            inspection_path = temporary / "inspection.json"
            output_path = temporary / "reconstruction.json"
            script = Path(__file__).resolve().parents[1] / "scripts/figurebench_rag.py"
            contract_path.write_text(
                json.dumps(
                    {
                        "modules": [{"id": "input", "label": "Input"}],
                        "arrows": [],
                        "labels": ["Input"],
                    }
                ),
                encoding="utf-8",
            )
            lexicon_path.write_text(json.dumps({"composition_families": ["balanced multi-region composition"]}), encoding="utf-8")
            inspection_path.write_text(json.dumps({"issues": [{"kind": "glow"}]}), encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "png-to-svg-brief",
                    "--first-draft-png",
                    "/tmp/first-draft.png",
                    "--generation-contract-json",
                    str(contract_path),
                    "--lexicon-json",
                    str(lexicon_path),
                    "--inspection-json",
                    str(inspection_path),
                    "--output",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            reconstruction = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(reconstruction["phase"], "semantic PNG-to-SVG reconstruction")
            self.assertEqual(reconstruction["reconstruction_targets"], ["glow"])

    def test_image_geometry_features_are_recorded_as_inferred_structure(self):
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            self.skipTest("Pillow is required for image-geometry extraction")
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory) / "dataset"
            dataset.mkdir()
            image_path = dataset / "diagram.png"
            image = Image.new("RGB", (300, 120), "white")
            draw = ImageDraw.Draw(image)
            draw.rectangle((15, 30, 100, 90), outline="black", width=4)
            draw.rectangle((190, 30, 275, 90), outline="black", width=4)
            draw.line((102, 60, 188, 60), fill="black", width=4)
            image.save(image_path)
            index_path = Path(temporary_directory) / "index.sqlite"

            build_index(dataset, index_path)
            lexicon = derive_geometry_lexicon(index_path)

            primitives = lexicon["primitive_distribution"]
            self.assertIn("inferred_geometric_modules", primitives)
            self.assertIn("inferred_directional_flow", primitives)

    def test_indexes_huggingface_layout_without_using_official_test_images(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory) / "figurebench"
            development = dataset / "images/1234.56789/method.png"
            test = dataset / "test_images/paper/evaluation.png"
            development.parent.mkdir(parents=True)
            test.parent.mkdir(parents=True)
            development.write_bytes(b"not a real image")
            test.write_bytes(b"not a real image")
            index_path = Path(temporary_directory) / "index.sqlite"

            summary = build_index(dataset, index_path)
            results = query_index(
                index_path,
                methodology="method",
                figure_intent="overview",
                requested_structure={},
            )

            self.assertEqual(summary["indexed"], 1)
            self.assertEqual(results[0]["source_path"], str(development))
            self.assertEqual(results[0]["source_group_id"], "upstream_1234.56789")

    def test_setup_cli_builds_portable_rag_from_an_existing_dataset(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory) / "figurebench"
            image = dataset / "images/1234.56789/method.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"not a real image")
            cache = Path(temporary_directory) / "cache"
            script = Path(__file__).resolve().parents[1] / "scripts/setup_figurebench_rag.py"

            completed = subprocess.run(
                [sys.executable, str(script), "--dataset", str(dataset), "--cache-dir", str(cache)],
                check=True,
                capture_output=True,
                text=True,
            )

            summary = json.loads(completed.stdout)
            self.assertEqual(summary["source_mode"], "existing_local_dataset")
            self.assertEqual(summary["indexed"], 1)
            self.assertTrue((cache / "figurebench.sqlite").exists())
            self.assertTrue((cache / "geometry-lexicon.json").exists())


if __name__ == "__main__":
    unittest.main()
