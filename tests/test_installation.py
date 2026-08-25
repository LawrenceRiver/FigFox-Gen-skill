import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_installation.py"


class InstallationCliTests(unittest.TestCase):
    def test_public_files_describe_the_complete_two_pass_png_workflow(self):
        public_files = (
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "README_ZH.md",
        )
        obsolete_claims = (
            "optional faithful PNG-to-SVG verification",
            "one direct PNG + optional SVG verification",
            "一次直接 PNG + 可选 SVG 验证",
            "SVG verification was skipped",
            "跳过 SVG 验证",
        )
        for path in public_files:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("PNG1", text)
                self.assertIn("SVG1", text)
                self.assertIn("PNG2", text)
                for claim in obsolete_claims:
                    self.assertNotIn(claim, text)

    def test_openai_metadata_starts_the_complete_skill_in_one_sentence(self):
        text = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        match = re.search(r'^  default_prompt: ("(?:[^"\\]|\\.)*")$', text, re.MULTILINE)
        self.assertIsNotNone(match, "default_prompt must be one quoted YAML string")
        prompt = json.loads(match.group(1))
        required_phrases = (
            "$FigFox-Gen-skill",
            "Methodology",
            "optional reference",
            "Contexts 1–3",
            "mapped FigureBench crops",
            "PNG1",
            "base Codex",
            "SVG1",
            "diagnosis",
            "PNG2",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, prompt)
        self.assertEqual(prompt.count("."), 1)
        self.assertTrue(prompt.endswith("."))
        self.assertIn('allow_implicit_invocation: true', text)

    def test_public_docs_explain_the_bundled_thirty_image_reference_pack(self):
        english = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
        chinese = " ".join((ROOT / "README_ZH.md").read_text(encoding="utf-8").split())
        self.assertIn("exactly 30 complete", english)
        self.assertIn("ordinary users do not download figurebench", english.casefold())
        self.assertIn("恰好 30 张完整", chinese)
        self.assertIn("普通用户无需下载 FigureBench", chinese)

    def test_public_docs_reject_obsolete_sources_and_stopping_rules(self):
        public_text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in ("SKILL.md", "README.md", "README_ZH.md", "agents/openai.yaml")
        )
        forbidden = (
            "FigureBench semantic–structural RAG",
            "FigureBench 语义–结构 RAG",
            "Topology + colour planning",
            "拓扑与配色规划",
            "unrelated-domain SVG",
            "不相关领域的 SVG",
            "FigureBench stays local",
            "FigureBench 保留在本地",
            "first image draft as the final PNG",
            "return the SVG too",
            "同时交付 SVG",
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, public_text)

    def test_public_docs_do_not_embed_or_link_retired_workflow_bitmaps(self):
        retired_assets = (
            "assets/runs/workflow-en.png",
            "assets/runs/workflow-zh.png",
        )
        for path in (ROOT / "README.md", ROOT / "README_ZH.md"):
            text = path.read_text(encoding="utf-8")
            for asset in retired_assets:
                self.assertNotIn(asset, text, f"{path.name} links retired workflow pixels")

    def test_legacy_rag_surface_is_absent_and_unreferenced(self):
        removed_paths = (
            "scientific_figure_rag",
            "scripts/figurebench_rag.py",
            "scripts/setup_figurebench_rag.py",
            "scripts/curate_reference_pack.py",
            "references/figurebench-rag.md",
            "references/palette-rag.md",
            "requirements-rag.txt",
            "tests/test_retrieval.py",
            "tests/test_curation.py",
        )
        for relative in removed_paths:
            self.assertFalse((ROOT / relative).exists(), relative)

        needles = (
            "scientific_figure_rag",
            "figurebench_rag.py",
            "setup_figurebench_rag.py",
            "curate_reference_pack.py",
            "figurebench-rag.md",
            "palette-rag.md",
            "requirements-rag.txt",
        )
        live_paths = [
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "README_ZH.md",
            ROOT / "agents/openai.yaml",
        ]
        for directory in ("scientific_figure_workflow", "scripts", "references"):
            live_paths.extend(
                path for path in (ROOT / directory).rglob("*")
                if path.is_file() and path.suffix in {".py", ".md", ".json", ".yaml", ".txt"}
            )
        live_paths.extend(
            path for path in (ROOT / "tests").glob("test_*.py")
            if path.name not in {"test_installation.py", "test_retrieval.py", "test_curation.py"}
        )
        for path in live_paths:
            text = path.read_text(encoding="utf-8")
            for needle in needles:
                self.assertNotIn(needle, text, f"{needle} remains in {path.relative_to(ROOT)}")

    def test_installed_repository_is_complete_and_reports_reference_bytes(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(ROOT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(completed.stdout.count("\n"), 1)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["reference_pack"]["references"], 30)
        self.assertEqual(summary["reference_pack"]["files"], [
            f"reference-{number:03d}.png" for number in range(1, 31)
        ])
        self.assertGreater(summary["reference_pack"]["total_bytes"], 0)

    def test_missing_install_asset_fails_concisely(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", temporary_directory],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertNotIn("Traceback", completed.stderr)
        self.assertEqual(completed.stderr.count("\n"), 1)
        self.assertIn("SKILL.md", completed.stderr)

    def test_isolated_checker_ignores_pythonpath_but_unified_cli_reports_bootstrap_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            poison_root = Path(temporary_directory)
            package = poison_root / "PIL"
            package.mkdir()
            (package / "__init__.py").write_text(
                'raise ImportError("simulated missing Pillow")\n', encoding="utf-8"
            )
            environment = dict(os.environ)
            environment["PYTHONPATH"] = str(poison_root)
            invocations = (
                ([sys.executable, str(SCRIPT), "--root", str(ROOT)], 0),
                (
                    [
                        sys.executable,
                        str(ROOT / "scripts/figure_workflow.py"),
                        "check-installation",
                        "--root",
                        str(ROOT),
                    ],
                    2,
                ),
            )
            for invocation, expected_code in invocations:
                with self.subTest(script=Path(invocation[1]).name):
                    completed = subprocess.run(
                        invocation,
                        cwd=ROOT,
                        env=environment,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(completed.returncode, expected_code)
                    self.assertNotIn("Traceback", completed.stderr)
                    if expected_code == 0:
                        self.assertEqual(completed.stderr, "")
                        self.assertEqual(json.loads(completed.stdout)["reference_pack"]["references"], 30)
                    else:
                        self.assertEqual(completed.stdout, "")
                        self.assertEqual(completed.stderr.count("\n"), 1)
                        self.assertIn("simulated missing Pillow", completed.stderr)

    def test_root_option_compiles_and_imports_the_target_installation_in_isolation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "installed-skill"
            shutil.copytree(
                ROOT,
                target,
                ignore=shutil.ignore_patterns(
                    ".git", ".superpowers", "docs", "tests", "work", "__pycache__"
                ),
            )
            artifacts = target / "scientific_figure_workflow/artifacts.py"
            original_artifacts = artifacts.read_bytes()
            corruptions = (
                (artifacts, b"def invalid syntax(:\n", "SyntaxError"),
                (
                    target / "scientific_figure_workflow/__init__.py",
                    b"import definitely_missing_target_dependency\n",
                    "definitely_missing_target_dependency",
                ),
            )
            for path, payload, expected in corruptions:
                with self.subTest(expected=expected):
                    original = path.read_bytes()
                    path.write_bytes(payload)
                    completed = subprocess.run(
                        [sys.executable, str(SCRIPT), "--root", str(target)],
                        cwd=ROOT,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(completed.returncode, 2)
                    self.assertEqual(completed.stdout, "")
                    self.assertNotIn("Traceback", completed.stderr)
                    self.assertIn(expected, completed.stderr)
                    path.write_bytes(original)
            artifacts.write_bytes(original_artifacts)


if __name__ == "__main__":
    unittest.main()
