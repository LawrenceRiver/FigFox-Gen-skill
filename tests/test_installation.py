import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_installation.py"


class InstallationCliTests(unittest.TestCase):
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

    def test_missing_runtime_dependency_fails_without_import_traceback(self):
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
                [sys.executable, str(SCRIPT), "--root", str(ROOT)],
                [
                    sys.executable,
                    str(ROOT / "scripts/figure_workflow.py"),
                    "check-installation",
                    "--root",
                    str(ROOT),
                ],
            )
            for invocation in invocations:
                with self.subTest(script=Path(invocation[1]).name):
                    completed = subprocess.run(
                        invocation,
                        cwd=ROOT,
                        env=environment,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(completed.returncode, 2)
                    self.assertEqual(completed.stdout, "")
                    self.assertNotIn("Traceback", completed.stderr)
                    self.assertEqual(completed.stderr.count("\n"), 1)
                    self.assertIn("simulated missing Pillow", completed.stderr)


if __name__ == "__main__":
    unittest.main()
