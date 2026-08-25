import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scientific_figure_workflow import validate_context3
from scientific_figure_workflow.reference_pack import (
    apply_crop_manifest,
    load_reference_index,
    rank_candidates,
    validate_reference_coverage,
    validate_reference_pack,
)


ROOT = Path(__file__).resolve().parents[1]


def attribution_for(source_id):
    return (
        f"Original figure source: arXiv:{source_id}; original-figure license: CC-BY-4.0; "
        f"evidence: https://arxiv.org/abs/{source_id}. "
        "FigureBench dataset license (separate; does not determine original-figure rights): "
        "CC-BY-4.0; metadata: "
        "https://huggingface.co/datasets/WestlakeNLP/FigureBench/blob/main/README.md."
    )


def context2_fixture():
    return {
        "mainline": "input to grouped output",
        "components": [
            {
                "id": "group",
                "semantic_role": "grouping",
                "visual_treatment": "rounded_container",
                "construction_provenance": "basic editable geometry",
                "special": "no",
                "source_context": "fixture",
            },
            {
                "id": "branch",
                "semantic_role": "routing",
                "visual_treatment": "branching_arrow",
                "construction_provenance": "basic editable geometry",
                "special": "no",
                "source_context": "fixture",
            },
        ],
        "layout_family": "horizontal_flow",
        "human_editable_signals": ["flat fill"],
        "relationships": [],
    }


def references_fixture(count=30):
    references = []
    for position in range(1, count + 1):
        references.append(
            {
                "id": f"reference-{position:03d}",
                "file": f"reference-{position:03d}.png",
                "partition": "dev",
                "source_id": f"fixture-paper-{position:03d}",
                "source_kind": "paper",
                "license": "CC-BY-4.0",
                "attribution": attribution_for(f"fixture-paper-{position:03d}"),
                "components": ["branching_arrow"],
                "layout_family": "grid",
                "human_editable_signals": ["flat fill"],
                "description": "Fixture reference",
                "extra_future_field": {"accepted": True},
            }
        )
    references[-1]["components"] = ["rounded_container", "branching_arrow"]
    references[-1]["layout_family"] = "horizontal_flow"
    references[-1]["human_editable_signals"] = ["flat fill", "consistent stroke"]
    return references


class ReferencePackTests(unittest.TestCase):
    def test_distributed_pack_has_exactly_thirty_indexed_images(self):
        summary = validate_reference_pack(ROOT / "assets/figurebench-references")
        self.assertEqual(summary["references"], 30)
        self.assertEqual(summary["missing"], [])
        self.assertEqual(summary["partitions"], ["dev"])

    def test_candidate_ranking_prioritizes_needed_geometry_and_layout(self):
        ranked = rank_candidates(context2_fixture(), references_fixture(30))
        self.assertEqual(len(ranked), 30)
        self.assertIn("rounded_container", ranked[0]["matched_components"])
        self.assertTrue(all(item["partition"] == "dev" for item in ranked))

    def test_candidate_ranking_uses_exact_five_three_two_weights(self):
        ranked = rank_candidates(context2_fixture(), references_fixture(30))

        self.assertEqual(ranked[0]["score"], 15)
        self.assertEqual(len(ranked[0]["matched_components"]), 2)
        self.assertEqual(len(ranked[0]["matched_layouts"]), 1)
        self.assertEqual(len(ranked[0]["matched_human_editable_signals"]), 1)

    def test_index_rejects_dataset_license_as_original_figure_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            records = references_fixture(30)
            for record in records:
                record.pop("extra_future_field")
                record["attribution"] = (
                    "FigureBench development set license: CC-BY-4.0; original source: "
                    f"arXiv:{record['source_id']}."
                )
                (root / record["file"]).write_bytes(b"png")
            (root / "index.json").write_text(json.dumps(records), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "original-figure license evidence"):
                validate_reference_pack(root)

    def test_index_accepts_original_publisher_license_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            records = references_fixture(30)
            for record in records:
                record.pop("extra_future_field")
                record["attribution"] = (
                    f"Original figure source: {record['source_id']}; original-figure license: "
                    "CC-BY-4.0; evidence: https://proceedings.mlr.press/v202/example.html. "
                    "FigureBench dataset license (separate; does not determine original-figure "
                    "rights): CC-BY-4.0; metadata: "
                    "https://huggingface.co/datasets/WestlakeNLP/FigureBench/blob/main/README.md."
                )
                (root / record["file"]).write_bytes(b"png")
            (root / "index.json").write_text(json.dumps(records), encoding="utf-8")

            self.assertEqual(validate_reference_pack(root)["references"], 30)

    def test_load_and_validation_reject_invalid_maintained_index(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            records = references_fixture(30)
            for record in records:
                record.pop("extra_future_field")
            records[1]["id"] = records[0]["id"]
            (root / "index.json").write_text(json.dumps(records), encoding="utf-8")
            for record in records:
                (root / record["file"]).write_bytes(b"png")

            with self.assertRaisesRegex(ValueError, "ids must be unique"):
                load_reference_index(root)

            records = references_fixture(30)
            for record in records:
                record.pop("extra_future_field")
            records[0]["attribution"] = ""
            (root / "index.json").write_text(json.dumps(records), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "attribution"):
                validate_reference_pack(root)

    def test_ranking_is_stable_and_uses_layout_source_diversity_for_equal_scores(self):
        references = references_fixture(30)
        references[0].update({
            "components": ["rounded_container"],
            "layout_family": "horizontal_flow",
            "human_editable_signals": ["flat fill"],
            "source_id": "same-source",
        })
        references[1].update({
            "components": ["rounded_container"],
            "layout_family": "vertical_flow",
            "human_editable_signals": ["flat fill"],
            "source_id": "other-source",
        })
        references[2].update({
            "components": ["rounded_container"],
            "layout_family": "vertical_flow",
            "human_editable_signals": ["flat fill"],
            "source_id": "third-source",
        })
        references[29].update({
            "components": ["branching_arrow"],
            "layout_family": "grid",
            "human_editable_signals": ["flat fill"],
            "source_id": "fourth-source",
        })

        ranked = rank_candidates(context2_fixture(), references)

        self.assertEqual([item["id"] for item in ranked[:3]], [
            "reference-001", "reference-002", "reference-004"
        ])


class ReferenceCropTests(unittest.TestCase):
    def make_pack(self, root: Path) -> Path:
        pack_root = root / "pack"
        pack_root.mkdir()
        records = []
        for position, base in enumerate((12, 78), start=1):
            reference_id = f"reference-{position:03d}"
            file_name = f"{reference_id}.png"
            image = Image.new("RGB", (100, 50))
            image.putdata([
                ((x + base) % 256, (3 * y + base) % 256, (7 * x + 11 * y + base) % 256)
                for y in range(image.height)
                for x in range(image.width)
            ])
            image.save(pack_root / file_name)
            records.append({
                "id": reference_id,
                "file": file_name,
                "partition": "dev",
                "source_id": f"crop-fixture-{position:03d}",
                "source_kind": "paper",
                "license": "CC-BY-4.0",
                "attribution": attribution_for(f"crop-fixture-{position:03d}"),
                "components": ["rounded_container"],
                "layout_family": "horizontal_flow",
                "human_editable_signals": ["flat fill"],
                "description": "Crop fixture reference",
            })
        (pack_root / "index.json").write_text(json.dumps({"references": records}), encoding="utf-8")
        return pack_root

    def crop(self, crop_id="crop-container", reference_id="reference-001", target="encoder"):
        return {
            "id": crop_id,
            "reference_id": reference_id,
            "bounds": [0.1, 0.2, 0.6, 0.8],
            "target_component_id": target,
            "crop_contract": {
                "borrow": ["corner family", "stroke rhythm"],
                "must_change": ["label", "proportions"],
                "human_editable_reason": "flat primitives with a consistent outline",
            },
        }

    def test_crop_manifest_writes_mapped_rgb_crop_and_contract(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pack_root = self.make_pack(root)
            output = root / "crops"

            result = apply_crop_manifest(pack_root, {"crops": [self.crop()]}, output)

            crop = result["crops"][0]
            self.assertTrue((output / crop["crop_path"]).is_file())
            self.assertEqual(crop["crop_contract"], self.crop()["crop_contract"])
            with Image.open(output / crop["crop_path"]) as image:
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(image.size, (50, 30))
                self.assertEqual(image.getpixel((0, 0)), (22, 42, 192))
                self.assertEqual(image.getpixel((49, 29)), (71, 129, 86))

    def test_crop_manifest_rejects_unknown_reference_id(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            with self.assertRaisesRegex(ValueError, "reference_id"):
                apply_crop_manifest(self.make_pack(root), {"crops": [self.crop(reference_id="unknown")]}, root / "crops")

    def test_crop_manifest_rejects_out_of_range_bounds(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            crop = self.crop()
            crop["bounds"] = [0, 0, 1.1, 0.5]
            with self.assertRaisesRegex(ValueError, "bounds"):
                apply_crop_manifest(self.make_pack(root), {"crops": [crop]}, root / "crops")

    def test_crop_manifest_rejects_empty_contract(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            crop = self.crop()
            crop["crop_contract"] = {}
            with self.assertRaisesRegex(ValueError, "crop_contract"):
                apply_crop_manifest(self.make_pack(root), {"crops": [crop]}, root / "crops")

    def test_crop_manifest_contract_requires_lists(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            crop = self.crop()
            crop["crop_contract"]["borrow"] = ("corner family",)
            with self.assertRaisesRegex(ValueError, "borrow"):
                apply_crop_manifest(self.make_pack(root), {"crops": [crop]}, root / "crops")

    def test_crop_manifest_rejects_duplicate_crop_ids(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            with self.assertRaisesRegex(ValueError, "ids must be unique"):
                apply_crop_manifest(self.make_pack(root), {"crops": [self.crop(), self.crop()]}, root / "crops")

    def test_crop_manifest_rejects_symlinked_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pack_root = self.make_pack(root)
            outside = root / "outside"
            outside.mkdir()
            output = root / "run/references/figurebench/crops"
            output.parent.mkdir(parents=True)
            output.symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "symlink"):
                apply_crop_manifest(pack_root, {"crops": [self.crop()]}, output)

            self.assertFalse((outside / "crop-container.png").exists())

    def test_crop_manifest_rejects_symlinked_output_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pack_root = self.make_pack(root)
            output = root / "crops"
            output.mkdir()
            outside = root / "outside.png"
            outside.write_bytes(b"preserve")
            (output / "crop-container.png").symlink_to(outside)

            with self.assertRaisesRegex(ValueError, "symlink"):
                apply_crop_manifest(pack_root, {"crops": [self.crop()]}, output)

            self.assertEqual(outside.read_bytes(), b"preserve")

    def test_candidate_ranking_matches_natural_language_context2(self):
        context = {
            "mainline": "Text Prompt to Text Encoder to a diffusion enclosure and audio decoder",
            "components": [
                {
                    "id": "text_encoder",
                    "label": "Text Encoder",
                    "semantic_role": "text transformation",
                    "visual_treatment": "compact rounded process container with centered label",
                },
                {
                    "id": "training_lane",
                    "label": "TRAINING",
                    "semantic_role": "subordinate supervision path",
                    "visual_treatment": "quiet lower dashed enclosure with orthogonal connectors",
                },
            ],
            "relationships": [],
        }

        ranked = rank_candidates(
            context, load_reference_index(ROOT / "assets/figurebench-references")
        )

        self.assertGreater(ranked[0]["score"], 0)
        self.assertTrue(
            ranked[0]["matched_components"]
            or ranked[0]["matched_layouts"]
            or ranked[0]["matched_human_editable_signals"]
        )

    def test_coverage_requires_two_distinct_references(self):
        context = {"components": [{"id": "encoder"}, {"id": "decoder"}]}
        manifest = {"crops": [self.crop(target="encoder"), self.crop("crop-decoder", target="decoder")]}

        with self.assertRaisesRegex(ValueError, "two distinct reference_id"):
            validate_reference_coverage(context, manifest, [])

    def test_coverage_requires_every_component_to_have_crop_or_complete_basic_geometry(self):
        context = {"components": [{"id": "encoder"}, {"id": "decoder"}, {"id": "legend"}]}
        manifest = {
            "crops": [
                self.crop(target="encoder"),
                self.crop("crop-decoder", reference_id="reference-002", target="decoder"),
            ]
        }

        with self.assertRaisesRegex(ValueError, "cover every Context 2 component"):
            validate_reference_coverage(context, manifest, [])

        basic_geometry = [{
            "component_id": "legend",
            "primitive": "rectangle and text",
            "construction_steps": ["draw rectangle", "place label"],
            "human_editable_reason": "simple editable SVG primitives",
        }]
        result = validate_reference_coverage(context, manifest, basic_geometry)
        self.assertEqual(result["covered_component_ids"], ["decoder", "encoder", "legend"])

    def test_crop_outputs_and_coverage_matrix_feed_context3_without_conversion(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pack_root = self.make_pack(root)
            manifest = {
                "crops": [
                    self.crop(target="encoder"),
                    self.crop("crop-decoder", reference_id="reference-002", target="decoder"),
                ]
            }
            context2 = {"components": [{"id": "encoder"}, {"id": "decoder"}]}
            selected_references = apply_crop_manifest(pack_root, manifest, root / "crops")["crops"]
            coverage_matrix = validate_reference_coverage(context2, manifest, [])["coverage_matrix"]

            context3 = {
                "selected_references": selected_references,
                "coverage_matrix": coverage_matrix,
                "palette": {
                    "base_palette_id": "workflow-role-01",
                    "colours": [
                        {"hex": "#2E5BFF", "rgb": [46, 91, 255], "role": "primary"},
                        {"hex": "#F59E0B", "rgb": [245, 158, 11], "role": "accent"},
                        {"hex": "#14B8A6", "rgb": [20, 184, 166], "role": "secondary"},
                        {"hex": "#475569", "rgb": [71, 85, 105], "role": "ink"},
                    ],
                },
                "taste_constraints": ["quiet hierarchy"],
            }

            normalized = validate_context3(context3, {"encoder", "decoder"})
            self.assertEqual(normalized["coverage_matrix"], coverage_matrix)

    def test_coverage_rejects_incomplete_basic_geometry_exception(self):
        context = {"components": [{"id": "encoder"}, {"id": "decoder"}, {"id": "legend"}]}
        manifest = {
            "crops": [
                self.crop(target="encoder"),
                self.crop("crop-decoder", reference_id="reference-002", target="decoder"),
            ]
        }
        incomplete_geometry = [{"component_id": "legend", "primitive": "rectangle"}]

        with self.assertRaisesRegex(ValueError, "construction_steps"):
            validate_reference_coverage(context, manifest, incomplete_geometry)
