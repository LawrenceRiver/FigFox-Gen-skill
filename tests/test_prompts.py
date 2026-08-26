import json
import tempfile
import unittest
from pathlib import Path

from scientific_figure_workflow.prompts import (
    build_creative_director_prompt,
    build_prompt1_bundle,
    validate_prompt_bundle,
    write_bundle,
)


def c1():
    return {
        "domain": "music generation",
        "dominant_colour_count": 2,
        "mainline": "prompt to encoded representation to audio",
        "conventions": [{
            "concept": "piano roll",
            "recurrence_evidence": "Appears in three retained method figures.",
            "visual_treatment": "stacked note grid",
            "terminology": "piano roll",
            "methodology_relevance": "shows the intermediate score representation",
            "eligible_source_crops": [{
                "path": "references/web/crops/piano-roll.png",
                "target_component_id": "audio",
                "borrow": ["staff-like spacing"],
                "must_change": ["source arrangement"],
            }],
        }],
    }


def c2():
    return {
        "mainline": "prompt to encoded representation to audio",
        "components": [
            {
                "id": "encoder", "label": "Prompt Encoder", "semantic_role": "transformation",
                "visual_treatment": "rounded container", "construction_provenance": "basic editable geometry",
                "special": "no", "source_context": "context-1-domain-conventions.json",
            },
            {
                "id": "audio", "label": "Audio", "semantic_role": "output",
                "visual_treatment": "waveform panel", "construction_provenance": "recurring domain convention",
                "special": "no", "source_context": "context-1-domain-conventions.json",
            },
        ],
        "relationships": [{"source_id": "encoder", "target_id": "audio", "label": "decodes to"}],
    }


def palette():
    return {
        "base_palette_id": "workflow-role-01",
        "dominant_colour_roles": ["primary", "accent"],
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
                "crop_id": "crop-container", "reference_id": "reference-001",
                "crop_path": "references/figurebench/crops/container.png",
                "target_component_id": "encoder",
                "crop_contract": {
                    "borrow": ["corner radius", "stroke weight"],
                    "must_change": ["source labels", "arrangement"],
                    "human_editable_reason": "editable vector geometry",
                },
            },
            {
                "crop_id": "crop-arrow", "reference_id": "reference-002",
                "crop_path": "references/figurebench/crops/arrow.png",
                "target_component_id": "audio",
                "crop_contract": {
                    "borrow": ["waveform enclosure"],
                    "must_change": ["run palette", "output label"],
                    "human_editable_reason": "editable path geometry",
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


def creative_director():
    return {
        "format": "creative-director-brief-v1",
        "brief": "Use a mature paper-SVG construction as a targeted variant.",
        "ideas": [{
            "id": "intermediate-shape-language",
            "target_component_id": "audio",
            "concept": "Use an editable intermediate panel rather than an invented icon.",
            "visual_intent": "Keep the intermediate representation compact and human-editable.",
            "construction_plan": "Borrow enclosure and connector grammar, then change labels and proportions.",
            "requires_svg_evidence": True,
            "svg_crops": [{
                "path": "references/web/crops/creative-director/intermediate-shape-language.png",
                "target_component_id": "audio",
                "source_url": "https://arxiv.org/html/2402.14285",
                "evidence_url": "https://arxiv.org/html/2402.14285v4/figure.svg",
                "source_format": "svg",
                "borrow": ["editable enclosure", "connector rhythm"],
                "must_change": ["source labels", "source proportions"],
                "human_editable_reason": "The crop uses editable rectangles and paths.",
            }],
        }],
    }


class PromptTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        for relative_path in (
            "input/user.png",
            "references/web/crops/piano-roll.png",
            "references/figurebench/crops/container.png",
            "references/figurebench/crops/arrow.png",
            "references/web/crops/creative-director/intermediate-shape-language.png",
        ):
            path = self.root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fixture")

    def tearDown(self):
        self.temporary_directory.cleanup()


class Prompt1BundleTests(PromptTestCase):
    def test_creative_director_prompt_and_crop_enter_prompt1(self):
        director_prompt = build_creative_director_prompt("method", c1(), c2(), c3())
        self.assertIn("Creative Director", director_prompt["prompt"])
        self.assertIn("paper SVG", director_prompt["prompt"])
        self.assertIn("Human construction order is mandatory", director_prompt["prompt"])
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root, creative_director())
        creative = [item for item in bundle["attachments"] if item["role"] == "creative_director_svg"]
        self.assertEqual(len(creative), 1)
        self.assertEqual(creative[0]["target_component_id"], "audio")
        self.assertIn("This is the only image-generation pass", bundle["prompt"])
        write_bundle(bundle, self.root / "prompt-1")

    def test_prompt1_contains_all_mapped_figurebench_crops(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)
        self.assertEqual(
            {item["path"] for item in bundle["attachments"] if item["role"] == "figurebench_component"},
            {"references/figurebench/crops/container.png", "references/figurebench/crops/arrow.png"},
        )
        self.assertNotIn("SVG1", bundle["prompt"])
        self.assertNotIn("PNG2", bundle["prompt"])

    def test_prompt1_has_ordered_sections_and_bans(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), "input/user.png", self.root)
        prompt = bundle["prompt"]
        headings = [
            "## 1. Figure purpose and scientific mainline",
            "## 5. Creative Director brief and paper-SVG evidence",
            "## 7. Palette-group contract",
            "## 10. Anti-AI visual constraints",
            "## 11. Direct PNG generation instruction",
        ]
        for heading in headings:
            self.assertIn(heading, prompt)
        self.assertIn("selected multi-colour palette group", prompt)
        self.assertIn("reference-fidelity lock", prompt.casefold())
        self.assertIn("match its composition, spacing, hierarchy, and visual grammar", prompt.casefold())
        self.assertIn("Use multiple colours from that group", prompt)
        self.assertIn("at most three dominant colours", prompt)
        self.assertIn("must not become a fourth dominant hue", prompt)
        self.assertIn("Dominant colour roles (maximum three):", prompt)
        for phrase in ("upper title-band", "sticker-like cutout", "pasted raster badge"):
            self.assertIn(phrase, prompt)
        for phrase in ("base geometry first", "plain arrows", "real sample", "repeated grid must be regular"):
            self.assertIn(phrase, prompt)

    def test_prompt_bundle_round_trips(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)
        write_bundle(bundle, self.root / "prompt-1")
        stored = {
            "format": bundle["format"],
            "phase": "prompt1",
            "prompt": (self.root / "prompt-1/prompt.md").read_text(encoding="utf-8"),
            "component_ids": bundle["component_ids"],
            "attachments": json.loads((self.root / "prompt-1/attachments.json").read_text(encoding="utf-8")),
        }
        self.assertEqual(validate_prompt_bundle(stored, self.root), validate_prompt_bundle(bundle, self.root))

    def test_bundle_rejects_unsafe_attachment_paths(self):
        bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, self.root)
        bundle["attachments"][0]["path"] = "../outside.png"
        with self.assertRaises(ValueError):
            validate_prompt_bundle(bundle, self.root)


class PromptTemplateTests(unittest.TestCase):
    def test_template_describes_single_pass(self):
        text = (Path(__file__).resolve().parents[1] / "references/prompt-templates.md").read_text(encoding="utf-8")
        for heading in ("Context extraction", "Creative Director prompt", "Prompt 1 generation", "Validation"):
            self.assertIn(heading, text)
        self.assertIn("only image-generation pass", text)
        self.assertIn("reference-fidelity lock", text.casefold())
        self.assertIn("do not beautify", text.casefold())
        self.assertNotIn("SVG1", text)
        self.assertNotIn("PNG2", text)


if __name__ == "__main__":
    unittest.main()
