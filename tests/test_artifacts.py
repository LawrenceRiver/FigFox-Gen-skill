import tempfile
import unittest
from pathlib import Path

from scientific_figure_workflow import (
    run_artifact_paths,
    validate_context1,
    validate_context2,
    validate_context3,
    validate_creative_director,
    validate_run_manifest,
)


def valid_context1():
    return {
        "domain": "music generation",
        "mainline": "text prompt to synthesized audio",
        "conventions": [{
            "concept": "piano roll",
            "recurrence_evidence": "Appears in three retained method figures.",
            "visual_treatment": "stacked note grid",
            "terminology": "piano roll",
            "methodology_relevance": "shows the intermediate score representation",
        }],
    }


def valid_context2():
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
        "relationships": [{"source_id": "encoder", "target_id": "audio"}],
    }


def valid_context3():
    return {
        "selected_references": [
            {
                "crop_id": "crop-encoder", "reference_id": "reference-001",
                "crop_path": "references/figurebench/crops/encoder.png",
                "target_component_id": "encoder",
                "crop_contract": {
                    "borrow": ["corner radius"], "must_change": ["source labels"],
                    "human_editable_reason": "editable rectangle geometry",
                },
            },
            {
                "crop_id": "crop-audio", "reference_id": "reference-002",
                "crop_path": "references/figurebench/crops/audio.png",
                "target_component_id": "audio",
                "crop_contract": {
                    "borrow": ["waveform enclosure"], "must_change": ["output label"],
                    "human_editable_reason": "editable path geometry",
                },
            },
        ],
        "coverage_matrix": [
            {"component_id": "encoder", "crop_ids": ["crop-encoder"]},
            {"component_id": "audio", "crop_ids": ["crop-audio"]},
        ],
        "palette": {
            "base_palette_id": "workflow-role-01",
            "colours": [
                {"hex": "#2E5BFF", "rgb": [46, 91, 255], "role": "primary"},
                {"hex": "#F59E0B", "rgb": [245, 158, 11], "role": "accent"},
                {"hex": "#14B8A6", "rgb": [20, 184, 166], "role": "secondary"},
                {"hex": "#475569", "rgb": [71, 85, 105], "role": "ink"},
            ],
            "extensions": [],
        },
        "taste_constraints": ["quiet hierarchy", "restrained spacing"],
    }


def valid_creative_director():
    return {
        "format": "creative-director-brief-v1",
        "brief": "no_external_svg_needed",
        "ideas": [{
            "id": "baseline",
            "target_component_id": "encoder",
            "concept": "Use the validated construction plan.",
            "visual_intent": "Keep the figure direct and editable.",
            "construction_plan": "Use Contexts 1–3 without a new external treatment.",
            "requires_svg_evidence": False,
            "svg_crops": [],
        }],
    }


MANIFEST_PATHS = {
    "methodology": "input/methodology.md",
    "context1": "context/context-1-domain-conventions.json",
    "context2": "context/context-2-content-visual-plan.json",
    "context3": "context/context-3-visual-kit.json",
    "web_manifest": "references/web/manifest.json",
    "figurebench_candidates": "references/figurebench/candidates.json",
    "figurebench_crop_request": "references/figurebench/crops/request.json",
    "figurebench_crops": "references/figurebench/crops/manifest.json",
    "creative_director_prompt": "creative-director/prompt.md",
    "creative_director_brief": "creative-director/brief.json",
    "prompt1": "prompt-1/prompt.md",
    "prompt1_attachments": "prompt-1/attachments.json",
    "png1": "png1.png",
}


def write_manifest_files(root, artifacts=MANIFEST_PATHS):
    for relative_path in artifacts.values():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture", encoding="utf-8")


class ContextArtifactTests(unittest.TestCase):
    def test_contexts_validate_and_normalize(self):
        context1 = valid_context1()
        context1["domain"] = "  music generation  "
        self.assertEqual(validate_context1(context1)["domain"], "music generation")
        context2 = validate_context2(valid_context2())
        self.assertEqual([item["id"] for item in context2["components"]], ["encoder", "audio"])
        self.assertEqual(set(item["component_id"] for item in validate_context3(valid_context3(), {"encoder", "audio"})["coverage_matrix"]), {"encoder", "audio"})

    def test_context2_rejects_dangling_relationship(self):
        context = valid_context2()
        context["relationships"][0]["target_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "known component ids"):
            validate_context2(context)

    def test_context3_requires_coverage_for_every_component(self):
        context = valid_context3()
        context["coverage_matrix"] = context["coverage_matrix"][:1]
        with self.assertRaisesRegex(ValueError, "cover every Context 2 component"):
            validate_context3(context, {"encoder", "audio"})


class CreativeDirectorArtifactTests(unittest.TestCase):
    def test_no_external_evidence_brief_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            normalized = validate_creative_director(valid_creative_director(), Path(directory), {"encoder", "audio"})
        self.assertEqual(normalized["svg_evidence_status"], "no_external_svg_needed")

    def test_svg_evidence_requires_safe_crop_and_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            crop = root / "references/web/crops/creative-director/idea.png"
            crop.parent.mkdir(parents=True)
            crop.write_bytes(b"png")
            brief = valid_creative_director()
            brief["ideas"][0].update({
                "requires_svg_evidence": True,
                "svg_crops": [{
                    "path": "references/web/crops/creative-director/idea.png",
                    "target_component_id": "encoder",
                    "source_url": "https://arxiv.org/abs/1234.5678",
                    "evidence_url": "https://arxiv.org/html/1234.5678/figure.svg",
                    "source_format": "svg",
                    "borrow": ["editable enclosure"],
                    "must_change": ["source labels"],
                    "human_editable_reason": "rectangles and paths remain editable",
                }],
            })
            self.assertEqual(validate_creative_director(brief, root, {"encoder", "audio"})["svg_evidence_status"], "paper_svg_crops_verified")
            brief["ideas"][0]["svg_crops"][0]["source_url"] = "http://example.test"
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                validate_creative_director(brief, root, {"encoder", "audio"})


class RunManifestTests(unittest.TestCase):
    def test_canonical_paths_are_single_pass(self):
        paths = run_artifact_paths()
        self.assertEqual(paths["png1"], "png1.png")
        self.assertNotIn("svg1", paths)
        self.assertNotIn("png2", paths)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_manifest_files(root)
            manifest = {"artifacts": dict(paths)}
            self.assertEqual(validate_run_manifest(manifest, root)["artifacts"], paths)

    def test_manifest_rejects_unknown_artifact(self):
        paths = run_artifact_paths()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_manifest_files(root)
            manifest = {"artifacts": {**paths, "obsolete": "obsolete.txt"}}
            (root / "obsolete.txt").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must not include"):
                validate_run_manifest(manifest, root)


if __name__ == "__main__":
    unittest.main()
