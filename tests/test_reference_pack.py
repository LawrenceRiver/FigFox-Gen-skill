import json
import tempfile
import unittest
from pathlib import Path

from scientific_figure_workflow.reference_pack import (
    load_reference_index,
    rank_candidates,
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
