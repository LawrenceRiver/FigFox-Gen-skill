import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scientific_figure_workflow.prompts import (
    build_prompt1_bundle,
    build_prompt2_bundle,
    write_bundle,
)


def c1():
    return {
        "domain": "music generation",
        "mainline": "prompt to encoded representation to audio",
        "conventions": [
            {
                "concept": "piano roll",
                "recurrence_evidence": "Appears in three retained method figures.",
                "visual_treatment": "stacked note grid",
                "terminology": "piano roll",
                "methodology_relevance": "shows the intermediate score representation",
                "eligible_source_crops": [
                    {
                        "path": "references/web/crops/piano-roll.png",
                        "target_component_id": "audio",
                        "borrow": ["staff-like spacing"],
                        "must_change": ["the source arrangement"],
                    }
                ],
            }
        ],
    }


def c2():
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
        "relationships": [
            {"source_id": "encoder", "target_id": "audio", "label": "decodes to"}
        ],
    }


def palette():
    return {
        "base_palette_id": "workflow-role-01",
        "colours": [
            {"hex": "#2E5BFF", "rgb": [46, 91, 255], "role": "primary"},
            {"hex": "#F59E0B", "rgb": [245, 158, 11], "role": "accent"},
            {"hex": "#14B8A6", "rgb": [20, 184, 166], "role": "secondary"},
            {"hex": "#475569", "rgb": [71, 85, 105], "role": "ink"},
        ],
        "extensions": [],
    }


def c3():
    return {
        "selected_references": [
            {
                "crop_id": "crop-container",
                "reference_id": "reference-001",
                "crop_path": "references/figurebench/crops/container.png",
                "target_component_id": "encoder",
                "crop_contract": {
                    "borrow": ["corner radius", "stroke weight"],
                    "must_change": ["source labels", "arrangement"],
                    "human_editable_reason": "the treatment is editable vector geometry",
                },
            },
            {
                "crop_id": "crop-arrow",
                "reference_id": "reference-002",
                "crop_path": "references/figurebench/crops/arrow.png",
                "target_component_id": "audio",
                "crop_contract": {
                    "borrow": ["waveform enclosure"],
                    "must_change": ["run palette", "output label"],
                    "human_editable_reason": "the waveform is a simple path construction",
                },
            },
        ],
        "coverage_matrix": [
            {"component_id": "encoder", "crop_ids": ["crop-container"]},
            {"component_id": "audio", "crop_ids": ["crop-arrow"]},
        ],
        "palette": palette(),
        "taste_constraints": ["quiet hierarchy", "restrained spacing"],
    }


def diagnosis():
    return {
        "verdicts": [
            {"component_id": "encoder", "verdict": "keep", "reason": "clear geometry"},
            {"component_id": "audio", "verdict": "patch", "reason": "label needs correction"},
        ]
    }


def svg_crops():
    return {
        "crops": [
            {
                "path": "svg-diagnostic/approved-crops/encoder.png",
                "target_component_id": "encoder",
                "diagnosis": "keep: clear geometry",
            }
        ]
    }


class PromptTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        for relative_path in (
            "input/user.png",
            "references/web/crops/piano-roll.png",
            "references/web/crops/replacements/real-waveform.png",
            "references/figurebench/crops/container.png",
            "references/figurebench/crops/arrow.png",
            "png1.png",
            "svg-diagnostic/approved-crops/encoder.png",
        ):
            path = self.root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fixture")

    def tearDown(self):
        self.temporary_directory.cleanup()


class Prompt1BundleTests(PromptTestCase):
    def test_prompt1_contains_every_mapped_figurebench_crop(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)

        self.assertEqual(
            {item["path"] for item in bundle["attachments"] if item["role"] == "figurebench_component"},
            {"references/figurebench/crops/container.png", "references/figurebench/crops/arrow.png"},
        )
        self.assertIn("Do not add decoration without a named scientific role", bundle["prompt"])

    def test_prompt1_emits_the_ten_ordered_sections_and_all_contracts(self):
        methodology = "long explanatory method prose with an explicit user requirement"
        bundle = build_prompt1_bundle(methodology, c1(), c2(), c3(), "input/user.png", self.root)
        prompt = bundle["prompt"]
        sections = (
            "1. Figure purpose and scientific mainline",
            "2. Exact block and structure names",
            "3. Semantic relationships and reading order",
            "4. Content-to-visual mapping for every element",
            "5. Crop-to-component mapping",
            "6. Single-palette contract",
            "7. Layout and taste constraints",
            "8. Exact labels and text-density limits",
            "9. Anti-AI visual constraints",
            "10. Direct PNG generation instruction",
        )
        self.assertEqual([prompt.index(section) for section in sections], sorted(prompt.index(section) for section in sections))
        self.assertIn("Prompt Encoder", prompt)
        self.assertIn("encoder -> audio: decodes to", prompt)
        self.assertIn("Target: encoder", prompt)
        self.assertIn("Borrow: corner radius; stroke weight", prompt)
        self.assertIn("Must change: source labels; arrangement", prompt)
        self.assertIn("references/web/crops/piano-roll.png", prompt)
        self.assertIn("#2E5BFF", prompt)
        self.assertEqual(bundle["attachments"][0]["role"], "user_reference")
        self.assertIn("Appears in three retained method figures", prompt)
        self.assertIn("never copy explanatory prose into the figure", prompt)
        self.assertIn("BEGIN METHODOLOGY SOURCE OF TRUTH", prompt)
        self.assertIn(methodology, prompt)
        self.assertIn("BEGIN NORMALIZED CONTEXT 1 JSON", prompt)
        self.assertIn(json.dumps(c1(), indent=2, sort_keys=True), prompt)

    def test_prompt1_rejects_unmapped_figurebench_crops_missing_visual_treatments_and_bad_palette(self):
        broken_coverage = c3()
        broken_coverage["coverage_matrix"][1]["crop_ids"] = ["missing-crop"]
        with self.assertRaisesRegex(ValueError, "crop_ids"):
            build_prompt1_bundle("method", c1(), c2(), broken_coverage, None, self.root)

        broken_plan = c2()
        broken_plan["components"][0]["visual_treatment"] = ""
        with self.assertRaisesRegex(ValueError, "visual_treatment"):
            build_prompt1_bundle("method", c1(), broken_plan, c3(), None, self.root)

        broken_palette = c3()
        broken_palette["palette"]["colours"][0]["hex"] = "#000000"
        broken_palette["palette"]["colours"][0]["rgb"] = [0, 0, 0]
        with self.assertRaisesRegex(ValueError, "base palette"):
            build_prompt1_bundle("method", c1(), c2(), broken_palette, None, self.root)

    def test_prompt1_prohibits_every_disallowed_ai_figure_pattern(self):
        prompt = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)["prompt"]
        for phrase in (
            "unexplained dots, floating symbols, or purposeless boxes",
            "arbitrary high-contrast colours between adjacent modules",
            "shapes with no human construction provenance",
            "numbered 1/2/3/4 planning labels",
            "generic blue-title-strip-inside-every-box pattern",
            "repeated card grids that make the figure look like a slide deck",
            "fake cartoon objects",
        ):
            self.assertIn(phrase, prompt)

    def test_prompt1_rejects_a_complete_figurebench_reference_disguised_as_a_crop(self):
        context3 = c3()
        context3["selected_references"][0]["crop_path"] = "references/figurebench/reference-001.png"

        with self.assertRaisesRegex(ValueError, "FigureBench crop root|existing file"):
            build_prompt1_bundle("method", c1(), c2(), context3, None, self.root)

    def test_prompt1_user_reference_has_a_structural_contract_but_no_palette_authority(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), "input/user.png", self.root)

        attachment = bundle["attachments"][0]
        self.assertEqual(attachment["role"], "user_reference")
        self.assertIn("contract", attachment)
        for phrase in (
            "strong guidance for structure, emphasis, layout",
            "visibly human-made basic visualization",
            "Ignore generated-looking, fake, or decorative parts",
            "Never source palette colours from the user reference",
        ):
            self.assertIn(phrase, bundle["prompt"])

    def test_prompt1_allows_only_the_two_narrow_user_requirement_overrides(self):
        prompt = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)["prompt"]

        self.assertIn("Only an explicit user requirement in the supplied Methodology or normalized Context", prompt)
        self.assertIn("numbered 1/2/3/4 planning labels or the generic blue-title-strip-inside-every-box pattern", prompt)
        self.assertIn("does not permit any other anti-AI constraint to be overridden", prompt)

    def test_prompt1_accepts_all_context2_relationship_endpoint_aliases(self):
        aliases = c2()
        aliases["relationships"] = [{
            "from_component_id": "encoder",
            "to_component_id": "audio",
            "label": "alias relationship",
        }]

        prompt = build_prompt1_bundle("method", c1(), aliases, c3(), None, self.root)["prompt"]

        self.assertIn("encoder -> audio: alias relationship.", prompt)

    def test_prompt1_rejects_complete_or_noncanonical_figurebench_and_domain_paths(self):
        complete = self.root / "assets/figurebench-references/renamed.png"
        complete.parent.mkdir(parents=True)
        complete.write_bytes(b"complete")
        context3 = c3()
        context3["selected_references"][0]["crop_path"] = "assets/figurebench-references/renamed.png"
        with self.assertRaisesRegex(ValueError, "FigureBench crop root"):
            build_prompt1_bundle("method", c1(), c2(), context3, None, self.root)

        context1 = c1()
        outside = self.root / "references/web/not-crops/piano-roll.png"
        outside.parent.mkdir(parents=True)
        outside.write_bytes(b"outside")
        context1["conventions"][0]["eligible_source_crops"][0]["path"] = "references/web/not-crops/piano-roll.png"
        with self.assertRaisesRegex(ValueError, "domain-paper crop root"):
            build_prompt1_bundle("method", context1, c2(), c3(), None, self.root)

    def test_prompt1_rejects_user_reference_outside_input_and_unsafe_paths(self):
        for path in ("references/web/crops/piano-roll.png", "../escape.png", "/tmp/escape.png", r"C:\\escape.png", r"\\server\\share\\escape.png"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                build_prompt1_bundle("method", c1(), c2(), c3(), path, self.root)


class Prompt2BundleTests(PromptTestCase):
    def test_prompt2_uses_png1_and_svg_crops_but_never_png15(self):
        bundle = build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), svg_crops(), {}, self.root)
        paths = {item["path"] for item in bundle["attachments"]}

        self.assertIn("png1.png", paths)
        self.assertIn("svg-diagnostic/approved-crops/encoder.png", paths)
        self.assertNotIn("svg-diagnostic/png1.5.png", paths)

    def test_prompt2_emits_all_verdict_blocks_and_uses_replacement_crops(self):
        all_verdicts = diagnosis()
        all_verdicts["verdicts"] = [
            {"component_id": "encoder", "verdict": "accept_variation", "reason": "valid simplification"},
            {"component_id": "audio", "verdict": "replace", "reason": "avoid fake icon"},
        ]
        bundle = build_prompt2_bundle(
            "method", c1(), c2(), c3(), "png1.png", all_verdicts, svg_crops(),
            {"crops": [{"path": "references/web/crops/replacements/real-waveform.png", "target_component_id": "audio", "reason": "mature source"}]},
            self.root,
        )
        prompt = bundle["prompt"]
        for block in ("Preserve", "Accept variation", "Patch", "Reject", "Replace"):
            self.assertIn(f"## {block}", prompt)
        self.assertIn("PNG1 is the image to modify", prompt)
        self.assertIn("references/web/crops/replacements/real-waveform.png", {item["path"] for item in bundle["attachments"]})
        self.assertIn("No PNG2-to-SVG loop", prompt)

    def test_prompt2_requires_and_preserves_a_replacement_reason(self):
        replacement_diagnosis = {
            "verdicts": [
                {"component_id": "encoder", "verdict": "keep"},
                {"component_id": "audio", "verdict": "replace", "reason": "fake icon"},
            ]
        }
        missing_reason = {"crops": [{
            "path": "references/web/crops/replacements/real-waveform.png",
            "target_component_id": "audio",
        }]}
        with self.assertRaisesRegex(ValueError, "reason"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", replacement_diagnosis, svg_crops(), missing_reason, self.root)

        bundle = build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", replacement_diagnosis, svg_crops(), {"crops": [{
            "path": "references/web/crops/replacements/real-waveform.png",
            "target_component_id": "audio",
            "reason": "mature waveform construction corrects the fake icon",
        }]}, self.root)
        replacement = next(item for item in bundle["attachments"] if item["role"] == "replacement_crop")
        self.assertEqual(replacement["reason"], "mature waveform construction corrects the fake icon")
        output_dir = self.root / "prompt-2"
        write_bundle(bundle, output_dir)
        written = json.loads((output_dir / "attachments.json").read_text(encoding="utf-8"))
        self.assertIn(replacement, written)

    def test_prompt2_carries_context1_conventions_context2_structure_and_context3_palette(self):
        methodology = "methodology source-of-truth: do not omit this requirement"
        prompt = build_prompt2_bundle(methodology, c1(), c2(), c3(), "png1.png", diagnosis(), svg_crops(), {}, self.root)["prompt"]

        for phrase in ("piano roll", "Prompt Encoder", "encoder -> audio", "#2E5BFF", "crop-container"):
            self.assertIn(phrase, prompt)
        self.assertIn(methodology, prompt)
        for number in (1, 2, 3):
            self.assertIn(f"BEGIN NORMALIZED CONTEXT {number} JSON", prompt)

    def test_prompt2_rejects_png15_spelling_and_role_tricks_and_incomplete_diagnosis(self):
        for bad_path in ("svg-diagnostic/png1.5.png", "SVG-DIAGNOSTIC\\PNG1.5.PNG", "assets/%70ng1.5.png"):
            crops = {"crops": [{"path": bad_path, "target_component_id": "encoder"}]}
            with self.subTest(bad_path=bad_path), self.assertRaisesRegex(ValueError, "PNG1.5"):
                build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), crops, {}, self.root)

        role_trick = {"crops": [{"path": "okay.png", "target_component_id": "encoder", "role": "svg_diagnostic_render"}]}
        with self.assertRaisesRegex(ValueError, "svg_diagnostic_render"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), role_trick, {}, self.root)

        incomplete = {"verdicts": [{"component_id": "encoder", "verdict": "keep"}]}
        with self.assertRaisesRegex(ValueError, "exactly one verdict"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", incomplete, svg_crops(), {}, self.root)

        with self.assertRaisesRegex(ValueError, "PNG1.5"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "PNG1.5.PNG", diagnosis(), svg_crops(), {}, self.root)

    def test_prompt2_rejects_symlink_to_png15_and_unsafe_or_wrong_provenance_paths(self):
        (self.root / "svg-diagnostic/png1.5.png").write_bytes(b"diagnostic")
        alias = self.root / "svg-diagnostic/approved-crops/alias.png"
        os.symlink(self.root / "svg-diagnostic/png1.5.png", alias)
        with self.assertRaisesRegex(ValueError, "PNG1.5"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), {"crops": [{"path": "svg-diagnostic/approved-crops/alias.png", "target_component_id": "encoder"}]}, {}, self.root)

        for bad_png1 in ("../png1.png", "/tmp/png1.png", r"C:\\png1.png", r"\\server\\share\\png1.png"):
            with self.subTest(bad_png1=bad_png1), self.assertRaises(ValueError):
                build_prompt2_bundle("method", c1(), c2(), c3(), bad_png1, diagnosis(), svg_crops(), {}, self.root)

        wrong_svg = {"crops": [{"path": "references/web/crops/piano-roll.png", "target_component_id": "encoder"}]}
        with self.assertRaisesRegex(ValueError, "approved SVG crop root"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), wrong_svg, {}, self.root)

        wrong_replacement = {"crops": [{"path": "references/web/crops/piano-roll.png", "target_component_id": "audio"}]}
        rejected = {"verdicts": [{"component_id": "encoder", "verdict": "keep"}, {"component_id": "audio", "verdict": "replace"}]}
        with self.assertRaisesRegex(ValueError, "replacement crop root"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", rejected, svg_crops(), wrong_replacement, self.root)


class PromptTemplateAndWritingTests(PromptTestCase):
    def test_templates_include_four_model_facing_stages_and_direct_svg_guardrails(self):
        templates = (Path(__file__).resolve().parents[1] / "references" / "prompt-templates.md").read_text(encoding="utf-8")
        for heading in ("Context extraction", "Prompt 1 generation", "Direct editable SVG transcription", "Prompt 2 revision"):
            self.assertIn(heading, templates)
        for phrase in (
            "PNG1 is the only visual truth",
            "one direct transcription",
            "No HTML or canvas wrapper",
            "No embedded raster wrapper",
            "No Python, local scripting, or draw.io",
            "No fresh SVG design from the prompt or Methodology",
        ):
            self.assertIn(phrase, templates)

    def test_write_bundle_writes_the_stable_prompt_and_attachment_manifest(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)
        self.assertEqual(bundle["component_ids"], ["audio", "encoder"])
        output_dir = self.root / "prompt-1"
        write_bundle(bundle, output_dir)
        self.assertEqual((output_dir / "prompt.md").read_text(encoding="utf-8"), bundle["prompt"])
        self.assertEqual(json.loads((output_dir / "attachments.json").read_text(encoding="utf-8")), sorted(bundle["attachments"], key=lambda item: (item["path"], item["role"])))

    def test_write_bundle_rejects_inconsistent_or_unserializable_input_without_partial_outputs(self):
        output_dir = self.root / "prompt-1"
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)
        inconsistent = copy.deepcopy(bundle)
        inconsistent["attachments"][0]["role"] = "approved_svg_crop"
        with self.assertRaises(ValueError):
            write_bundle(inconsistent, output_dir)
        self.assertFalse((output_dir / "prompt.md").exists())
        self.assertFalse((output_dir / "attachments.json").exists())

        unserializable = copy.deepcopy(bundle)
        unserializable["attachments"][0]["borrow"] = {"not-json"}
        with self.assertRaises(ValueError):
            write_bundle(unserializable, output_dir)
        self.assertFalse((output_dir / "prompt.md").exists())
        self.assertFalse((output_dir / "attachments.json").exists())

        invalid_metadata = copy.deepcopy(bundle)
        invalid_metadata["attachments"][0]["concept"] = ""
        with self.assertRaises(ValueError):
            write_bundle(invalid_metadata, output_dir)
        self.assertFalse((output_dir / "prompt.md").exists())
        self.assertFalse((output_dir / "attachments.json").exists())

    def test_write_bundle_rejects_unknown_attachment_target(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)
        bundle["attachments"][0]["target_component_id"] = "unknown"

        with self.assertRaisesRegex(ValueError, "component_ids"):
            write_bundle(bundle, self.root / "prompt-1")

    def test_write_bundle_is_byte_deterministic_for_reordered_mappings(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)
        reordered = {key: bundle[key] for key in reversed(list(bundle))}
        reordered["attachments"] = [
            {key: attachment[key] for key in reversed(list(attachment))}
            for attachment in reversed(bundle["attachments"])
        ]
        with tempfile.TemporaryDirectory() as second_directory:
            second_root = Path(second_directory) / "run"
            shutil.copytree(self.root, second_root)

            write_bundle(bundle, self.root / "prompt-1")
            write_bundle(reordered, second_root / "prompt-1")

            self.assertEqual(
                (self.root / "prompt-1/attachments.json").read_bytes(),
                (second_root / "prompt-1/attachments.json").read_bytes(),
            )

    def test_write_bundle_restores_the_prior_pair_after_second_replace_failure(self):
        initial = build_prompt1_bundle("old method", c1(), c2(), c3(), None, self.root)
        output_dir = self.root / "prompt-1"
        write_bundle(initial, output_dir)
        old_prompt = (output_dir / "prompt.md").read_bytes()
        old_attachments = (output_dir / "attachments.json").read_bytes()
        updated = build_prompt1_bundle("new method", c1(), c2(), c3(), None, self.root)
        real_replace = os.replace
        calls = 0

        def fail_only_second_replace(source, destination):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated second replacement failure")
            return real_replace(source, destination)

        with patch("scientific_figure_workflow.prompts.os.replace", side_effect=fail_only_second_replace):
            with self.assertRaisesRegex(OSError, "simulated second"):
                write_bundle(updated, output_dir)

        self.assertEqual((output_dir / "prompt.md").read_bytes(), old_prompt)
        self.assertEqual((output_dir / "attachments.json").read_bytes(), old_attachments)



if __name__ == "__main__":
    unittest.main()
