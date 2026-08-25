import json
import tempfile
import unittest
from pathlib import Path

from scientific_figure_workflow import (
    load_json_object,
    validate_context1,
    validate_context2,
    validate_context3,
    validate_diagnosis,
    validate_run_manifest,
)


def valid_context1():
    return {
        "domain": "music generation",
        "mainline": "text prompt to synthesized audio",
        "conventions": [
            {
                "concept": "piano roll",
                "recurrence_evidence": "Appears in three retained method figures.",
                "visual_treatment": "stacked note grid",
                "terminology": "piano roll",
                "methodology_relevance": "shows the intermediate score representation",
            }
        ],
    }


def valid_context2():
    return {
        "mainline": "prompt to encoded representation to audio",
        "components": [
            {
                "id": "encoder",
                "label": "Prompt Encoder",
                "semantic_role": "transformation",
                "visual_treatment": "rounded container",
                "construction_provenance": "basic editable geometry",
                "special": "no",
                "source_context": "context-1-domain-conventions.json",
            },
            {
                "id": "audio",
                "label": "Audio",
                "semantic_role": "output",
                "visual_treatment": "waveform panel",
                "construction_provenance": "recurring domain convention",
                "special": "no",
                "source_context": "context-1-domain-conventions.json",
            },
        ],
        "relationships": [{"source_id": "encoder", "target_id": "audio"}],
    }


def valid_palette():
    return {
        "base_palette": {
            "id": "slate-blue",
            "colors": [
                {"hex": "#1F2937", "role": "ink"},
                {"hex": "#E5E7EB", "role": "background"},
            ],
        },
        "extensions": [
            {
                "hex": "#3B82F6",
                "role": "accent",
                "relationship": "controlled_contrast",
                "web_evidence": "https://example.test/palette-evidence",
            }
        ],
    }


def valid_context3():
    return {
        "selected_references": [
            {
                "crop_id": "crop-encoder",
                "reference_id": "reference-001",
                "crop_path": "references/figurebench/crops/encoder.png",
                "target_component_id": "encoder",
                "crop_contract": {
                    "borrow": "corner radius and stroke weight",
                    "must_change": "replace the source labels and arrangement",
                    "human_editable_reason": "the treatment is editable vector geometry",
                },
            },
            {
                "crop_id": "crop-audio",
                "reference_id": "reference-002",
                "crop_path": "references/figurebench/crops/audio.png",
                "target_component_id": "audio",
                "crop_contract": {
                    "borrow": "waveform enclosure",
                    "must_change": "use the run palette and output label",
                    "human_editable_reason": "the waveform is a simple path construction",
                },
            },
        ],
        "coverage_matrix": [
            {"component_id": "encoder", "crop_ids": ["crop-encoder"]},
            {"component_id": "audio", "crop_ids": ["crop-audio"]},
        ],
        "palette": valid_palette(),
        "taste_constraints": ["quiet hierarchy", "restrained spacing"],
    }


def valid_diagnosis():
    return {
        "verdicts": [
            {"component_id": "encoder", "verdict": "keep"},
            {"component_id": "audio", "verdict": "patch"},
        ]
    }


MANIFEST_PATHS = {
    "methodology": "input/methodology.md",
    "context1": "context/context-1-domain-conventions.json",
    "context2": "context/context-2-content-visual-plan.json",
    "context3": "context/context-3-visual-kit.json",
    "web_manifest": "references/web/manifest.json",
    "figurebench_candidates": "references/figurebench/candidates.json",
    "figurebench_crops": "references/figurebench/crops/manifest.json",
    "prompt1": "prompt-1/prompt.md",
    "prompt1_attachments": "prompt-1/attachments.json",
    "png1": "png1.png",
    "svg1": "svg-diagnostic/svg1.svg",
    "png1_5": "svg-diagnostic/png1.5.png",
    "diagnosis": "svg-diagnostic/diagnosis.json",
    "approved_crops": "svg-diagnostic/approved-crops/manifest.json",
    "prompt2": "prompt-2/prompt.md",
    "prompt2_attachments": "prompt-2/attachments.json",
    "png2": "png2-final.png",
}


class ContextArtifactTests(unittest.TestCase):
    def test_context1_requires_recurrence_evidence(self):
        with self.assertRaisesRegex(ValueError, "recurrence_evidence"):
            validate_context1(
                {"domain": "music generation", "conventions": [{"concept": "piano roll"}]}
            )

    def test_context1_normalizes_a_copy(self):
        context = valid_context1()
        context["domain"] = "  music generation  "

        normalized = validate_context1(context)

        self.assertEqual(normalized["domain"], "music generation")
        self.assertEqual(context["domain"], "  music generation  ")

    def test_context2_requires_visual_provenance_for_each_component(self):
        with self.assertRaisesRegex(ValueError, "construction_provenance"):
            validate_context2(
                {
                    "mainline": "prompt to audio",
                    "components": [
                        {"id": "audio", "label": "Audio", "semantic_role": "output"}
                    ],
                    "relationships": [],
                }
            )

    def test_context2_rejects_duplicate_components_and_unknown_relationships(self):
        duplicate = valid_context2()
        duplicate["components"].append(dict(duplicate["components"][0]))
        with self.assertRaisesRegex(ValueError, "ids must be unique"):
            validate_context2(duplicate)

        dangling = valid_context2()
        dangling["relationships"] = [{"source_id": "encoder", "target_id": "missing"}]
        with self.assertRaisesRegex(ValueError, "known component ids"):
            validate_context2(dangling)

    def test_context3_requires_crop_image_and_crop_contract(self):
        with self.assertRaisesRegex(ValueError, "crop_contract"):
            validate_context3(
                {
                    "selected_references": [
                        {"reference_id": "reference-001", "crop_path": "crops/a.png"}
                    ],
                    "palette": valid_palette(),
                    "taste_constraints": ["quiet hierarchy"],
                },
                {"encoder"},
            )

    def test_context3_requires_two_references_and_complete_coverage(self):
        single_reference = valid_context3()
        single_reference["selected_references"][1]["reference_id"] = "reference-001"
        with self.assertRaisesRegex(ValueError, "two distinct"):
            validate_context3(single_reference, {"encoder", "audio"})

        incomplete = valid_context3()
        incomplete["coverage_matrix"] = [{"component_id": "encoder", "crop_ids": ["crop-encoder"]}]
        with self.assertRaisesRegex(ValueError, "coverage_matrix"):
            validate_context3(incomplete, {"encoder", "audio"})

    def test_context3_accepts_basic_geometry_coverage_and_rejects_bad_palette_extension(self):
        basic_geometry = valid_context3()
        basic_geometry["coverage_matrix"][1] = {
            "component_id": "audio",
            "basic_geometry_justification": "A plain labelled rectangle is sufficient.",
        }
        normalized = validate_context3(basic_geometry, {"encoder", "audio"})
        self.assertEqual(normalized["coverage_matrix"][1]["component_id"], "audio")

        invalid_palette = valid_context3()
        invalid_palette["palette"]["extensions"][0]["relationship"] = "unrelated"
        with self.assertRaisesRegex(ValueError, "relationship"):
            validate_context3(invalid_palette, {"encoder", "audio"})

    def test_context3_normalizes_nested_crop_contract_without_mutating_input(self):
        context = valid_context3()
        context["selected_references"][0]["crop_contract"]["borrow"] = "  corner radius  "

        normalized = validate_context3(context, {"encoder", "audio"})

        self.assertEqual(
            normalized["selected_references"][0]["crop_contract"]["borrow"], "corner radius"
        )
        self.assertEqual(
            context["selected_references"][0]["crop_contract"]["borrow"], "  corner radius  "
        )

    def test_diagnosis_requires_one_declared_verdict_per_component(self):
        self.assertEqual(
            validate_diagnosis(valid_diagnosis(), {"encoder", "audio"})["verdicts"][0]["verdict"],
            "keep",
        )

        missing = valid_diagnosis()
        missing["verdicts"].pop()
        with self.assertRaisesRegex(ValueError, "exactly one verdict"):
            validate_diagnosis(missing, {"encoder", "audio"})

        invalid = valid_diagnosis()
        invalid["verdicts"][0]["verdict"] = "approve"
        with self.assertRaisesRegex(ValueError, "verdict"):
            validate_diagnosis(invalid, {"encoder", "audio"})


class RunManifestTests(unittest.TestCase):
    def test_manifest_requires_all_canonical_relative_artifacts_to_exist(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for relative_path in MANIFEST_PATHS.values():
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture", encoding="utf-8")

            normalized = validate_run_manifest({"artifacts": MANIFEST_PATHS}, root)

            self.assertEqual(normalized["artifacts"], MANIFEST_PATHS)

    def test_manifest_rejects_missing_or_absolute_artifact_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            missing = dict(MANIFEST_PATHS)
            missing.pop("png2")
            with self.assertRaisesRegex(ValueError, "png2"):
                validate_run_manifest({"artifacts": missing}, root)

            absolute = dict(MANIFEST_PATHS)
            absolute["png2"] = str(root / "png2-final.png")
            with self.assertRaisesRegex(ValueError, "relative"):
                validate_run_manifest({"artifacts": absolute}, root)

    def test_load_json_object_requires_a_json_object(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "artifact.json"
            path.write_text(json.dumps({"domain": "music generation"}), encoding="utf-8")
            self.assertEqual(load_json_object(path), {"domain": "music generation"})

            path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "object"):
                load_json_object(path)


if __name__ == "__main__":
    unittest.main()
