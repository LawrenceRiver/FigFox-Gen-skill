#!/usr/bin/env python3
"""Validate deterministic files and dependencies installed with the Skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


_REQUIRED_FILES = (
    "SKILL.md",
    "requirements.txt",
    "references/figurebench-visual-selection.md",
    "references/palette-library.json",
    "references/prompt-templates.md",
    "references/taste-rules.md",
    "scientific_figure_workflow/__init__.py",
    "scientific_figure_workflow/artifacts.py",
    "scientific_figure_workflow/reference_pack.py",
    "scientific_figure_workflow/palette.py",
    "scientific_figure_workflow/prompts.py",
    "scientific_figure_workflow/run_validation.py",
    "scripts/check_installation.py",
    "scripts/figure_workflow.py",
    "assets/figurebench-references/index.json",
)
_REQUIRED_REQUIREMENTS = {"pillow": "PIL"}
_PACKAGE_MODULES = (
    "scientific_figure_workflow",
    "scientific_figure_workflow.artifacts",
    "scientific_figure_workflow.reference_pack",
    "scientific_figure_workflow.palette",
    "scientific_figure_workflow.prompts",
    "scientific_figure_workflow.run_validation",
)
_PROBE_CODE = r'''
import importlib
import json
from pathlib import Path
import py_compile
import sys

root = Path(sys.argv[1]).resolve(strict=True)
python_files = json.loads(sys.argv[2])
modules = json.loads(sys.argv[3])
dependencies = json.loads(sys.argv[4])
sys.path.insert(0, str(root))
try:
    for relative in python_files:
        py_compile.compile(str(root / relative), doraise=True)
    package = importlib.import_module("scientific_figure_workflow")
    package_path = Path(package.__file__).resolve(strict=True)
    if not package_path.is_relative_to(root):
        raise RuntimeError("isolated probe imported workflow package outside target root")
    for module in modules:
        importlib.import_module(module)
    for dependency in dependencies:
        importlib.import_module(dependency)
    summary = package.validate_reference_pack(
        root / "assets/figurebench-references", expected_count=30
    )
    print(json.dumps({"package_file": str(package_path), "reference_pack": summary}, sort_keys=True))
except Exception as error:
    message = str(error).replace("\r", " ").replace("\n", " | ")
    print(f"{type(error).__name__}: {message}", file=sys.stderr)
    raise SystemExit(2)
'''


def _required_file(root: Path, relative: str) -> Path:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"installation is missing {relative}")
    return path


def _requirement_names(path: Path) -> set[str]:
    names: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        match = re.match(r"[A-Za-z0-9_.-]+", line)
        if match is None:
            raise ValueError("requirements.txt contains an invalid requirement")
        names.add(match.group(0).casefold().replace("_", "-"))
    return names


def _probe_target(root: Path) -> dict[str, Any]:
    python_files = [relative for relative in _REQUIRED_FILES if relative.endswith(".py")]
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            _PROBE_CODE,
            str(root),
            json.dumps(python_files),
            json.dumps(list(_PACKAGE_MODULES)),
            json.dumps(list(_REQUIRED_REQUIREMENTS.values())),
        ],
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip().replace("\r", " ").replace("\n", " | ")
        raise ValueError(message or "isolated target installation probe failed")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("isolated target installation probe returned invalid JSON") from error
    if not isinstance(result, dict) or not isinstance(result.get("reference_pack"), dict):
        raise ValueError("isolated target installation probe returned an invalid result")
    return result


def validate_installation(root: str | Path) -> dict[str, Any]:
    """Validate one installed repository without interpreting SKILL prose."""

    installation_root = Path(root).resolve()
    for relative in _REQUIRED_FILES:
        _required_file(installation_root, relative)

    requirement_names = _requirement_names(installation_root / "requirements.txt")
    missing_requirements = sorted(set(_REQUIRED_REQUIREMENTS) - requirement_names)
    if missing_requirements:
        raise ValueError(
            f"requirements.txt is missing {missing_requirements[0]}"
        )

    pack_root = installation_root / "assets/figurebench-references"
    expected_files = [f"reference-{number:03d}.png" for number in range(1, 31)]
    actual_files = sorted(path.name for path in pack_root.glob("*.png"))
    if actual_files != expected_files:
        raise ValueError(
            "reference pack requires exactly reference-001.png through reference-030.png"
        )
    probe = _probe_target(installation_root)
    pack_summary = probe["reference_pack"]
    total_bytes = sum((pack_root / name).stat().st_size for name in expected_files)
    if total_bytes <= 0:
        raise ValueError("reference pack total bytes must be positive")

    return {
        "root": str(installation_root),
        "required_files": list(_REQUIRED_FILES),
        "requirements": sorted(_REQUIRED_REQUIREMENTS),
        "reference_pack": {
            **pack_summary,
            "files": expected_files,
            "total_bytes": total_bytes,
        },
    }


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, f"{message}\n")


def main() -> int:
    parser = _Parser(description=__doc__)
    parser.add_argument("--root", default=REPOSITORY_ROOT)
    arguments = parser.parse_args()
    try:
        result = validate_installation(arguments.root)
    except (ImportError, OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
