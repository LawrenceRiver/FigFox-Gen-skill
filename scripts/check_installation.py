#!/usr/bin/env python3
"""Validate deterministic files and dependencies installed with the Skill."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

_BOOTSTRAP_ERROR: ImportError | None = None
try:
    from scientific_figure_workflow import validate_reference_pack  # noqa: E402
except ImportError as error:  # handled by both standalone and unified CLI boundaries
    _BOOTSTRAP_ERROR = error


_REQUIRED_FILES = (
    "SKILL.md",
    "requirements.txt",
    "references/figurebench-visual-selection.md",
    "references/palette-library.json",
    "references/prompt-templates.md",
    "references/svg-diagnostic.md",
    "references/taste-rules.md",
    "scientific_figure_workflow/__init__.py",
    "scientific_figure_workflow/artifacts.py",
    "scientific_figure_workflow/reference_pack.py",
    "scientific_figure_workflow/palette.py",
    "scientific_figure_workflow/prompts.py",
    "scientific_figure_workflow/svg_diagnostics.py",
    "scripts/check_installation.py",
    "scripts/figure_workflow.py",
    "assets/figurebench-references/index.json",
)
_REQUIRED_REQUIREMENTS = {
    "cairosvg": "cairosvg",
    "defusedxml": "defusedxml",
    "pillow": "PIL",
    "tinycss2": "tinycss2",
}
_PACKAGE_MODULES = (
    "scientific_figure_workflow.artifacts",
    "scientific_figure_workflow.reference_pack",
    "scientific_figure_workflow.palette",
    "scientific_figure_workflow.prompts",
    "scientific_figure_workflow.svg_diagnostics",
)


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


def validate_installation(root: str | Path) -> dict[str, Any]:
    """Validate one installed repository without interpreting SKILL prose."""

    if _BOOTSTRAP_ERROR is not None:
        raise ImportError(str(_BOOTSTRAP_ERROR)) from _BOOTSTRAP_ERROR
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
    pack_summary = validate_reference_pack(pack_root, expected_count=30)
    total_bytes = sum((pack_root / name).stat().st_size for name in expected_files)
    if total_bytes <= 0:
        raise ValueError("reference pack total bytes must be positive")

    if installation_root == REPOSITORY_ROOT:
        for module in _PACKAGE_MODULES:
            importlib.import_module(module)
        for module in _REQUIRED_REQUIREMENTS.values():
            importlib.import_module(module)

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
