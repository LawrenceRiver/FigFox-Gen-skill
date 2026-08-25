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
        "base_palette_id": "workflow-role-01",
        "colours": [
            {"hex": "#2E5BFF", "rgb": [46, 91, 255], "role": "primary"},
            {"hex": "#F59E0B", "rgb": [245, 158, 11], "role": "accent"},
            {"hex": "#14B8A6", "rgb": [20, 184, 166], "role": "secondary"},
            {"hex": "#475569", "rgb": [71, 85, 105], "role": "ink"},
        ],
        "extensions": [
            {
                "hex": "#3B82F6",
                "rgb": [59, 130, 246],
                "role": "accent",
                "relationship": "controlled_contrast",
                "evidence_url": "https://example.test/palette-evidence",
                "evidence_summary": "A controlled accent relationship to the base group.",
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
                    "borrow": ["corner radius", "stroke weight"],
                    "must_change": ["source labels", "arrangement"],
                    "human_editable_reason": "the treatment is editable vector geometry",
                },
            },
            {
                "crop_id": "crop-audio",
                "reference_id": "reference-002",
                "crop_path": "references/figurebench/crops/audio.png",
                "target_component_id": "audio",
                "crop_contract": {
                    "borrow": ["waveform enclosure"],
                    "must_change": ["run palette", "output label"],
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


def write_manifest_files(root, artifacts=MANIFEST_PATHS):
    for relative_path in artifacts.values():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture", encoding="utf-8")


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

    def test_context1_rejects_every_required_field(self):
        for field in ("domain", "mainline"):
            with self.subTest(field=field):
                context = valid_context1()
                context.pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    validate_context1(context)
        for field in (
            "concept",
            "recurrence_evidence",
            "visual_treatment",
            "terminology",
            "methodology_relevance",
        ):
            with self.subTest(convention_field=field):
                context = valid_context1()
                context["conventions"][0].pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    validate_context1(context)
        with self.assertRaisesRegex(ValueError, "conventions"):
            validate_context1({"domain": "music", "mainline": "score to audio", "conventions": []})

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

    def test_context2_rejects_every_component_and_relationship_invariant(self):
        context = valid_context2()
        context.pop("mainline")
        with self.assertRaisesRegex(ValueError, "mainline"):
            validate_context2(context)

        context = valid_context2()
        context["components"] = []
        with self.assertRaisesRegex(ValueError, "components"):
            validate_context2(context)

        for field in (
            "id",
            "label",
            "semantic_role",
            "visual_treatment",
            "construction_provenance",
            "special",
            "source_context",
        ):
            with self.subTest(component_field=field):
                context = valid_context2()
                context["components"][0].pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    validate_context2(context)

        context = valid_context2()
        context["relationships"] = "encoder to audio"
        with self.assertRaisesRegex(ValueError, "relationships"):
            validate_context2(context)
        for field in ("source_id", "target_id"):
            with self.subTest(endpoint=field):
                context = valid_context2()
                context["relationships"][0].pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    validate_context2(context)

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
        context["selected_references"][0]["crop_contract"]["borrow"] = ["  corner radius  "]

        normalized = validate_context3(context, {"encoder", "audio"})

        self.assertEqual(
            normalized["selected_references"][0]["crop_contract"]["borrow"], ["corner radius"]
        )
        self.assertEqual(
            context["selected_references"][0]["crop_contract"]["borrow"], ["  corner radius  "]
        )

    def test_context3_requires_list_based_borrow_and_must_change_contracts(self):
        for field in ("borrow", "must_change"):
            with self.subTest(contract_field=field):
                context = valid_context3()
                context["selected_references"][0]["crop_contract"][field] = "ambiguous string"
                with self.assertRaisesRegex(ValueError, field):
                    validate_context3(context, {"encoder", "audio"})

                context = valid_context3()
                context["selected_references"][0]["crop_contract"][field] = ("ambiguous tuple",)
                with self.assertRaisesRegex(ValueError, field):
                    validate_context3(context, {"encoder", "audio"})

    def test_context3_rejects_every_selection_and_coverage_invariant(self):
        for field in ("crop_id", "reference_id", "crop_path", "target_component_id"):
            with self.subTest(selection_field=field):
                context = valid_context3()
                context["selected_references"][0].pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    validate_context3(context, {"encoder", "audio"})
        for field in ("borrow", "must_change", "human_editable_reason"):
            with self.subTest(contract_field=field):
                context = valid_context3()
                context["selected_references"][0]["crop_contract"].pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    validate_context3(context, {"encoder", "audio"})

        context = valid_context3()
        context["selected_references"] = []
        with self.assertRaisesRegex(ValueError, "selected_references"):
            validate_context3(context, {"encoder", "audio"})
        context = valid_context3()
        context["selected_references"][1]["crop_id"] = "crop-encoder"
        with self.assertRaisesRegex(ValueError, "crop_ids"):
            validate_context3(context, {"encoder", "audio"})
        context = valid_context3()
        context["selected_references"][0]["target_component_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "target_component_id"):
            validate_context3(context, {"encoder", "audio"})

        context = valid_context3()
        context["coverage_matrix"] = []
        with self.assertRaisesRegex(ValueError, "coverage_matrix"):
            validate_context3(context, {"encoder", "audio"})
        for field, value, reason in (
            ("component_id", None, "component_id"),
            ("component_id", "missing", "component_id"),
            ("crop_ids", [], "crop_ids"),
            ("crop_ids", ["missing"], "crop_ids"),
            ("basic_geometry_justification", "", "basic_geometry_justification"),
        ):
            with self.subTest(coverage_field=field, value=value):
                context = valid_context3()
                if field == "basic_geometry_justification":
                    context["coverage_matrix"][0].pop("crop_ids")
                    context["coverage_matrix"][0][field] = value
                elif value is None:
                    context["coverage_matrix"][0].pop(field)
                else:
                    context["coverage_matrix"][0][field] = value
                with self.assertRaisesRegex(ValueError, reason):
                    validate_context3(context, {"encoder", "audio"})
        context = valid_context3()
        context["coverage_matrix"][1]["component_id"] = "encoder"
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_context3(context, {"encoder", "audio"})

    def test_context3_rejects_every_palette_invariant(self):
        for field in ("base_palette_id", "colours"):
            with self.subTest(palette_field=field):
                context = valid_context3()
                context["palette"].pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    validate_context3(context, {"encoder", "audio"})
        for field, value, reason in (
            ("role", None, "role"),
            ("hex", "#2e5bff", "uppercase HEX"),
            ("rgb", [46, 91, 254], "rgb"),
        ):
            with self.subTest(colour_field=field):
                context = valid_context3()
                if value is None:
                    context["palette"]["colours"][0].pop(field)
                else:
                    context["palette"]["colours"][0][field] = value
                with self.assertRaisesRegex(ValueError, reason):
                    validate_context3(context, {"encoder", "audio"})
        for field, value, reason in (
            ("role", None, "role"),
            ("hex", "#3b82f6", "uppercase HEX"),
            ("rgb", [59, 130, 245], "rgb"),
            ("relationship", "unrelated", "relationship"),
            ("evidence_url", "http://example.test/evidence", "HTTPS"),
            ("evidence_summary", "", "evidence_summary"),
        ):
            with self.subTest(extension_field=field):
                context = valid_context3()
                if value is None:
                    context["palette"]["extensions"][0].pop(field)
                else:
                    context["palette"]["extensions"][0][field] = value
                with self.assertRaisesRegex(ValueError, reason):
                    validate_context3(context, {"encoder", "audio"})
        for field in (
            "additional_palette_ids",
            "palette_source",
            "user_reference_palette_id",
            "figurebench_palette_id",
            "base_palette",
        ):
            with self.subTest(forbidden_palette_field=field):
                context = valid_context3()
                context["palette"][field] = ["other"]
                with self.assertRaisesRegex(ValueError, field):
                    validate_context3(context, {"encoder", "audio"})
        context = valid_context3()
        context["palette"]["extensions"] = "not a list"
        with self.assertRaisesRegex(ValueError, "extensions"):
            validate_context3(context, {"encoder", "audio"})
        context = valid_context3()
        context["palette"]["extensions"][0]["hex"] = "#2E5BFF"
        context["palette"]["extensions"][0]["rgb"] = [46, 91, 255]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_context3(context, {"encoder", "audio"})

    def test_context3_rejects_an_unapproved_base_palette_group(self):
        context = valid_context3()
        context["palette"]["base_palette_id"] = "unapproved-group"

        with self.assertRaisesRegex(ValueError, "approved base palette group"):
            validate_context3(context, {"encoder", "audio"})

    def test_context3_rejects_missing_taste_constraints(self):
        for constraints, reason in (([], "taste_constraints"), ([""], "taste_constraints")):
            with self.subTest(constraints=constraints):
                context = valid_context3()
                context["taste_constraints"] = constraints
                with self.assertRaisesRegex(ValueError, reason):
                    validate_context3(context, {"encoder", "audio"})

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

    def test_diagnosis_rejects_each_record_invariant(self):
        diagnosis = valid_diagnosis()
        diagnosis["verdicts"] = []
        with self.assertRaisesRegex(ValueError, "verdicts"):
            validate_diagnosis(diagnosis, {"encoder", "audio"})
        for field in ("component_id", "verdict"):
            with self.subTest(verdict_field=field):
                diagnosis = valid_diagnosis()
                diagnosis["verdicts"][0].pop(field)
                with self.assertRaisesRegex(ValueError, field):
                    validate_diagnosis(diagnosis, {"encoder", "audio"})
        diagnosis = valid_diagnosis()
        diagnosis["verdicts"][1]["component_id"] = "encoder"
        with self.assertRaisesRegex(ValueError, "exactly one verdict"):
            validate_diagnosis(diagnosis, {"encoder", "audio"})
        diagnosis = valid_diagnosis()
        diagnosis["verdicts"][1]["component_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "exactly one verdict"):
            validate_diagnosis(diagnosis, {"encoder", "audio"})


class RunManifestTests(unittest.TestCase):
    def test_manifest_requires_all_canonical_relative_artifacts_to_exist(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_manifest_files(root)

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

    def test_manifest_rejects_every_path_invariant(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_manifest_files(root)
            for key in MANIFEST_PATHS:
                with self.subTest(missing_key=key):
                    artifacts = dict(MANIFEST_PATHS)
                    artifacts.pop(key)
                    with self.assertRaisesRegex(ValueError, key):
                        validate_run_manifest({"artifacts": artifacts}, root)

            artifacts = dict(MANIFEST_PATHS)
            artifacts["png2"] = "png2.png"
            with self.assertRaisesRegex(ValueError, "png2.*png2-final"):
                validate_run_manifest({"artifacts": artifacts}, root)

            artifacts = dict(MANIFEST_PATHS)
            artifacts["png2"] = "../png2-final.png"
            with self.assertRaisesRegex(ValueError, "stay under root"):
                validate_run_manifest({"artifacts": artifacts}, root)

            artifacts = dict(MANIFEST_PATHS)
            artifacts["extra"] = "missing.txt"
            with self.assertRaisesRegex(ValueError, "does not exist"):
                validate_run_manifest({"artifacts": artifacts}, root)

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
