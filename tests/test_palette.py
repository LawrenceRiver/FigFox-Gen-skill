import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scientific_figure_rag.palette import compile_colour_contract, select_palettes


ROOT = Path(__file__).resolve().parents[1]


class PaletteSelectionTests(unittest.TestCase):
    def test_selects_tag_and_role_matching_palettes_without_image_fields(self):
        result = select_palettes(
            {"tags": ["biomedical", "contrast"], "required_roles": ["ink", "accent"]}
        )

        self.assertEqual(result["palettes"][0]["id"], "biomedical-contrast-01")
        self.assertNotIn("image", json.dumps(result).lower())
        self.assertEqual(result["selection_basis"]["top_k"], 3)

    def test_preserves_groups_and_returns_colour_roles(self):
        result = select_palettes({"tags": ["workflow"], "required_roles": ["primary", "accent"]})

        palette = result["palettes"][0]
        self.assertEqual(palette["id"], "workflow-role-01")
        self.assertGreaterEqual(len(palette["colours"]), 4)
        self.assertIn("primary", {colour["role"] for colour in palette["colours"]})
        self.assertIn("accent", {colour["role"] for colour in palette["colours"]})


class ColourContractTests(unittest.TestCase):
    def test_locks_assignments_to_exact_values_from_an_approved_library_group(self):
        contract = compile_colour_contract(
            {
                "brief_domains": ["biomedical"],
                "source": {"kind": "approved_library", "palette_id": "biomedical-contrast-01"},
                "assignments": {"canvas": "#E7EFFA", "ink": "#14517C", "accent": "#D8383A"},
            }
        )

        self.assertEqual(
            contract["allowed_hex"],
            ["#14517C", "#2F7FC1", "#E7EFFA", "#96C37D", "#F3D266", "#D8383A", "#A9B8C6"],
        )
        self.assertEqual(contract["assignments"]["accent"], "#D8383A")

    def test_rejects_an_invented_colour_even_when_the_role_is_valid(self):
        with self.assertRaisesRegex(ValueError, "not in the selected source"):
            compile_colour_contract(
                {
                    "brief_domains": ["biomedical"],
                    "source": {"kind": "approved_library", "palette_id": "biomedical-contrast-01"},
                    "assignments": {"accent": "#112233"},
                }
            )

    def test_accepts_an_ephemeral_svg_palette_only_when_its_domain_is_unrelated(self):
        contract = compile_colour_contract(
            {
                "brief_domains": ["diffusion", "computer vision"],
                "source": {
                    "kind": "cross_domain_svg",
                    "source_domains": ["marine ecology"],
                    "colours": [
                        {"role": "canvas", "hex": "#F7F4EE", "rgb": [247, 244, 238]},
                        {"role": "ink", "hex": "#203040", "rgb": [32, 48, 64]},
                        {"role": "primary", "hex": "#3A7CA5", "rgb": [58, 124, 165]},
                    ],
                },
                "assignments": {"canvas": "#F7F4EE", "ink": "#203040", "primary": "#3A7CA5"},
            }
        )

        self.assertEqual(contract["source"]["kind"], "cross_domain_svg")
        self.assertEqual(contract["allowed_hex"], ["#F7F4EE", "#203040", "#3A7CA5"])

    def test_rejects_a_cross_domain_svg_palette_from_the_current_domain(self):
        with self.assertRaisesRegex(ValueError, "unrelated"):
            compile_colour_contract(
                {
                    "brief_domains": ["diffusion"],
                    "source": {
                        "kind": "cross_domain_svg",
                        "source_domains": ["diffusion"],
                        "colours": [{"role": "primary", "hex": "#3A7CA5", "rgb": [58, 124, 165]}],
                    },
                    "assignments": {"primary": "#3A7CA5"},
                }
            )


class PaletteCliTests(unittest.TestCase):
    def test_cli_returns_palette_selection_from_planning_json(self):
        plan = {"tags": ["biomedical", "contrast"], "required_roles": ["ink", "accent"]}
        script = ROOT / "scripts/figurebench_rag.py"
        with tempfile.TemporaryDirectory() as temporary_directory:
            plan_path = Path(temporary_directory) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(script), "palettes", "--planning-json", str(plan_path)],
                capture_output=True,
                text=True,
                check=True,
            )

        self.assertEqual(json.loads(completed.stdout)["palettes"][0]["id"], "biomedical-contrast-01")

    def test_cli_compiles_a_frozen_colour_contract(self):
        plan = {
            "brief_domains": ["biomedical"],
            "source": {"kind": "approved_library", "palette_id": "biomedical-contrast-01"},
            "assignments": {"ink": "#14517C", "accent": "#D8383A"},
        }
        script = ROOT / "scripts/figurebench_rag.py"
        with tempfile.TemporaryDirectory() as temporary_directory:
            plan_path = Path(temporary_directory) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(script), "colour-contract", "--plan-json", str(plan_path)],
                capture_output=True,
                text=True,
                check=True,
            )

        result = json.loads(completed.stdout)
        self.assertEqual(result["assignments"]["accent"], "#D8383A")
        self.assertEqual(result["source"]["palette_id"], "biomedical-contrast-01")


class SkillDocumentationTests(unittest.TestCase):
    def test_ui_default_prompt_starts_a_complete_labelled_image_generation_task(self):
        metadata = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")

        self.assertIn("$genlike-scientific-svg", metadata)
        self.assertIn("image-generation task", metadata)
        self.assertIn("complete labelled research figure", metadata)
        self.assertIn("first image draft", metadata)
        self.assertIn("semantic SVG reconstruction", metadata)
        self.assertIn("final PNG", metadata)

    def test_skill_documents_inline_colour_planning_and_image_free_palette_library(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        palette_reference = (ROOT / "references/palette-rag.md").read_text(encoding="utf-8")

        self.assertIn("Color Planning", skill)
        self.assertIn("does not add a model call", skill)
        self.assertIn("palette-library.json", palette_reference)
        self.assertIn("must not store screenshots", palette_reference)

    def test_docs_require_colour_source_isolation_direct_image_generation_and_skill_installation(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        palette_reference = (ROOT / "references/palette-rag.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README_ZH.md").read_text(encoding="utf-8")

        self.assertIn("unrelated to the brief's domain", skill)
        self.assertIn("temporary crop", skill)
        self.assertIn("temporary crop", palette_reference)
        self.assertIn("directly generate the first scientific raster draft", skill)
        self.assertIn("must not use a rendered SVG as its input", skill)
        self.assertIn("generate every required label directly", skill)
        self.assertIn("missing, incorrect, or overflowing text", skill)
        self.assertIn("plan-first, image-generation-first", readme.lower())
        self.assertIn("先规划、再图像生成", readme_zh)
        self.assertIn("only exact HEX values", palette_reference)
        self.assertIn("npx skills@latest add LawrenceRiver/genlike-scientific-svg-skill", readme)
        self.assertIn("npx skills@latest add LawrenceRiver/genlike-scientific-svg-skill", readme_zh)
        self.assertNotIn("git clone", readme)
        self.assertNotIn("git clone", readme_zh)

    def test_skill_documents_semantic_png_to_svg_reconstruction_before_second_image_call(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        rag_reference = (ROOT / "references/figurebench-rag.md").read_text(encoding="utf-8")

        self.assertIn("semantic PNG-to-SVG reconstruction", skill)
        self.assertIn("second image-generation call", skill)
        self.assertIn("not a pixel trace", skill)
        self.assertIn("overlay the SVG text and structural layer", skill)
        self.assertIn("flat exact-HEX fills", skill)
        self.assertIn("complex scientific assets", skill)
        self.assertIn("png-to-svg-brief", rag_reference)

    def test_readmes_lead_with_install_then_record_real_methodology_driven_runs(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README_ZH.md").read_text(encoding="utf-8")

        self.assertNotIn("## What it is", readme)
        self.assertNotIn("## 这是什么", readme_zh)
        self.assertLess(
            readme.index("npx skills@latest add LawrenceRiver/genlike-scientific-svg-skill"),
            readme.index("## Workflow"),
        )
        for method in ("Latent Diffusion", "MusiCoT", "AlphaFold 3"):
            self.assertIn(method, readme)
        self.assertIn("Methodology input", readme)
        self.assertIn("Computer Vision", readme)

    def test_readme_links_all_five_direct_image_generation_outputs(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for asset in (
            "workflow-en.png",
            "workflow-zh.png",
            "latent-diffusion.png",
            "musicot.png",
            "alphafold3.png",
        ):
            self.assertTrue((ROOT / "assets" / "runs" / asset).is_file())
            self.assertIn(f"assets/runs/{asset}", readme)

    def test_readmes_acknowledge_reference_sources_without_making_rag_the_hook(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README_ZH.md").read_text(encoding="utf-8")

        self.assertIn("## Acknowledgements", readme)
        self.assertIn("Nature Portfolio", readme)
        self.assertIn("## 鸣谢", readme_zh)
        self.assertIn("Nature Portfolio", readme_zh)
        self.assertNotIn("FigureBench RAG · frozen colour", readme)

    def test_readme_has_a_bilingual_marketing_hook_and_four_image_preview_strip(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("让图像模型真正理解科研架构", readme)
        hook_end = readme.index("## Workflow")
        preview_strip = readme[:hook_end]
        for asset in (
            "workflow-en.png",
            "latent-diffusion.png",
            "musicot.png",
            "alphafold3.png",
        ):
            self.assertIn(f"assets/runs/{asset}", preview_strip)


if __name__ == "__main__":
    unittest.main()
