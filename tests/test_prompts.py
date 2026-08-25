import json
import tempfile
import unittest
from pathlib import Path

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


class Prompt1BundleTests(unittest.TestCase):
    def test_prompt1_contains_every_mapped_figurebench_crop(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, Path("run"))

        self.assertEqual(
            {item["path"] for item in bundle["attachments"] if item["role"] == "figurebench_component"},
            {"references/figurebench/crops/container.png", "references/figurebench/crops/arrow.png"},
        )
        self.assertIn("Do not add decoration without a named scientific role", bundle["prompt"])

    def test_prompt1_emits_the_ten_ordered_sections_and_all_contracts(self):
        bundle = build_prompt1_bundle("long explanatory method prose", c1(), c2(), c3(), "input/user.png", Path("run"))
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
        self.assertNotIn("Appears in three retained method figures", prompt)

    def test_prompt1_rejects_unmapped_figurebench_crops_missing_visual_treatments_and_bad_palette(self):
        broken_coverage = c3()
        broken_coverage["coverage_matrix"][1]["crop_ids"] = ["missing-crop"]
        with self.assertRaisesRegex(ValueError, "crop_ids"):
            build_prompt1_bundle("method", c1(), c2(), broken_coverage, None, Path("run"))

        broken_plan = c2()
        broken_plan["components"][0]["visual_treatment"] = ""
        with self.assertRaisesRegex(ValueError, "visual_treatment"):
            build_prompt1_bundle("method", c1(), broken_plan, c3(), None, Path("run"))

        broken_palette = c3()
        broken_palette["palette"]["colours"][0]["hex"] = "#000000"
        broken_palette["palette"]["colours"][0]["rgb"] = [0, 0, 0]
        with self.assertRaisesRegex(ValueError, "base palette"):
            build_prompt1_bundle("method", c1(), c2(), broken_palette, None, Path("run"))

    def test_prompt1_prohibits_every_disallowed_ai_figure_pattern(self):
        prompt = build_prompt1_bundle("method", c1(), c2(), c3(), None, Path("run"))["prompt"]
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

        with self.assertRaisesRegex(ValueError, "complete FigureBench"):
            build_prompt1_bundle("method", c1(), c2(), context3, None, Path("run"))


class Prompt2BundleTests(unittest.TestCase):
    def test_prompt2_uses_png1_and_svg_crops_but_never_png15(self):
        bundle = build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), svg_crops(), {}, Path("run"))
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
            {"crops": [{"path": "references/web/crops/real-waveform.png", "target_component_id": "audio", "reason": "mature source"}]},
            Path("run"),
        )
        prompt = bundle["prompt"]
        for block in ("Preserve", "Accept variation", "Patch", "Reject", "Replace"):
            self.assertIn(f"## {block}", prompt)
        self.assertIn("PNG1 is the image to modify", prompt)
        self.assertIn("references/web/crops/real-waveform.png", {item["path"] for item in bundle["attachments"]})
        self.assertIn("No PNG2-to-SVG loop", prompt)

    def test_prompt2_carries_context1_conventions_context2_structure_and_context3_palette(self):
        prompt = build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), svg_crops(), {}, Path("run"))["prompt"]

        for phrase in ("piano roll", "Prompt Encoder", "encoder -> audio", "#2E5BFF", "crop-container"):
            self.assertIn(phrase, prompt)

    def test_prompt2_rejects_png15_spelling_and_role_tricks_and_incomplete_diagnosis(self):
        for bad_path in ("svg-diagnostic/png1.5.png", "SVG-DIAGNOSTIC\\PNG1.5.PNG", "assets/%70ng1.5.png"):
            crops = {"crops": [{"path": bad_path, "target_component_id": "encoder"}]}
            with self.subTest(bad_path=bad_path), self.assertRaisesRegex(ValueError, "PNG1.5"):
                build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), crops, {}, Path("run"))

        role_trick = {"crops": [{"path": "okay.png", "target_component_id": "encoder", "role": "svg_diagnostic_render"}]}
        with self.assertRaisesRegex(ValueError, "svg_diagnostic_render"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), role_trick, {}, Path("run"))

        incomplete = {"verdicts": [{"component_id": "encoder", "verdict": "keep"}]}
        with self.assertRaisesRegex(ValueError, "exactly one verdict"):
            build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", incomplete, svg_crops(), {}, Path("run"))


class PromptTemplateAndWritingTests(unittest.TestCase):
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
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, Path("run"))
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "prompt-1"
            write_bundle(bundle, output_dir)
            self.assertEqual((output_dir / "prompt.md").read_text(encoding="utf-8"), bundle["prompt"])
            self.assertEqual(json.loads((output_dir / "attachments.json").read_text(encoding="utf-8")), bundle["attachments"])


if __name__ == "__main__":
    unittest.main()
