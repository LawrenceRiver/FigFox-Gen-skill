#!/usr/bin/env python3
"""Deterministic CLI for the evidence-guided two-pass figure workflow."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Callable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

_BOOTSTRAP_ERROR: ImportError | None = None
try:
    from check_installation import validate_installation  # noqa: E402
    from scientific_figure_workflow import (  # noqa: E402
        apply_crop_manifest,
        apply_svg_crop_manifest,
        build_prompt1_bundle,
        build_prompt2_bundle,
        inspect_editable_svg,
        load_json_object,
        load_reference_index,
        rank_candidates,
        render_svg,
        validate_context1,
        validate_context2,
        validate_context3,
        validate_diagnosis,
        validate_palette,
        validate_reference_coverage,
        validate_run_manifest,
        write_bundle,
    )
except ImportError as error:  # handled at the subprocess boundary below
    _BOOTSTRAP_ERROR = error


_CONTEXT_PATHS = {
    1: "context/context-1-domain-conventions.json",
    2: "context/context-2-content-visual-plan.json",
    3: "context/context-3-visual-kit.json",
}
_RUN_ARTIFACTS = {
    "methodology": "input/methodology.md",
    "context1": _CONTEXT_PATHS[1],
    "context2": _CONTEXT_PATHS[2],
    "context3": _CONTEXT_PATHS[3],
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
_REFERENCE_PACK = REPOSITORY_ROOT / "assets/figurebench-references"
_PALETTE_LIBRARY = REPOSITORY_ROOT / "references/palette-library.json"


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, f"{message}\n")


def _run_root(value: str | Path) -> Path:
    root = Path(value)
    if not root.is_dir():
        raise ValueError("run root must be an existing directory")
    return root.resolve(strict=True)


def _component_ids(context2: dict[str, Any]) -> list[str]:
    normalized = validate_context2(context2)
    return [component["id"] for component in normalized["components"]]


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or path.is_symlink():
        raise ValueError("JSON output path must not contain a symlink destination")
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _contexts(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context1 = load_json_object(root / _CONTEXT_PATHS[1])
    context2 = load_json_object(root / _CONTEXT_PATHS[2])
    context3 = load_json_object(root / _CONTEXT_PATHS[3])
    return context1, context2, context3


def _palette_library() -> list[dict[str, Any]]:
    library = load_json_object(_PALETTE_LIBRARY)
    palettes = library.get("palettes")
    if not isinstance(palettes, list):
        raise ValueError("palette library requires palettes list")
    return palettes


def _cmd_check_installation(arguments: argparse.Namespace) -> dict[str, Any]:
    return validate_installation(arguments.root)


def _cmd_validate_context(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    value = load_json_object(root / _CONTEXT_PATHS[arguments.context])
    if arguments.context == 1:
        normalized = validate_context1(value)
    elif arguments.context == 2:
        normalized = validate_context2(value)
    else:
        context2 = load_json_object(root / _CONTEXT_PATHS[2])
        normalized = validate_context3(value, _component_ids(context2))
    return {"context": arguments.context, "artifact": normalized}


def _cmd_rank_references(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context2 = validate_context2(load_json_object(root / _CONTEXT_PATHS[2]))
    ranked = rank_candidates(context2, load_reference_index(_REFERENCE_PACK))
    _atomic_json(root / _RUN_ARTIFACTS["figurebench_candidates"], {"candidates": ranked})
    return {"candidates": len(ranked), "path": _RUN_ARTIFACTS["figurebench_candidates"]}


def _cmd_crop_references(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    manifest = load_json_object(root / _RUN_ARTIFACTS["figurebench_crops"])
    output_dir = root / "references/figurebench/crops"
    result = apply_crop_manifest(_REFERENCE_PACK, manifest, output_dir)
    return {"crops": len(result["crops"]), "paths": [item["crop_path"] for item in result["crops"]]}


def _cmd_validate_reference_coverage(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context2 = validate_context2(load_json_object(root / _CONTEXT_PATHS[2]))
    manifest = load_json_object(root / _RUN_ARTIFACTS["figurebench_crops"])
    return validate_reference_coverage(context2, manifest, manifest.get("basic_geometry", []))


def _cmd_validate_palette(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context3 = load_json_object(root / _CONTEXT_PATHS[3])
    return validate_palette(context3.get("palette"), _palette_library())


def _optional_user_reference(root: Path) -> str | None:
    references = sorted(path for path in (root / "input").glob("user-reference.*") if path.is_file())
    if len(references) > 1:
        raise ValueError("run input requires at most one user-reference file")
    return references[0].relative_to(root).as_posix() if references else None


def _cmd_build_prompt1(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context1, context2, context3 = _contexts(root)
    methodology = (root / _RUN_ARTIFACTS["methodology"]).read_text(encoding="utf-8")
    bundle = build_prompt1_bundle(
        methodology, context1, context2, context3, _optional_user_reference(root), root
    )
    write_bundle(bundle, root / "prompt-1")
    return {"phase": "prompt1", "attachments": len(bundle["attachments"]), "path": "prompt-1"}


def _cmd_inspect_svg(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    return inspect_editable_svg(root / _RUN_ARTIFACTS["svg1"])


def _cmd_render_svg(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    path = render_svg(
        root / _RUN_ARTIFACTS["svg1"], root / _RUN_ARTIFACTS["png1_5"]
    )
    return {"path": path.relative_to(root).as_posix()}


def _cmd_validate_diagnosis(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context2 = load_json_object(root / _CONTEXT_PATHS[2])
    diagnosis = load_json_object(root / _RUN_ARTIFACTS["diagnosis"])
    normalized = validate_diagnosis(diagnosis, _component_ids(context2))
    return {"verdicts": len(normalized["verdicts"]), "diagnosis": normalized}


def _cmd_crop_svg(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    output_path = root / _RUN_ARTIFACTS["approved_crops"]
    coordinates = load_json_object(output_path)
    context2 = load_json_object(root / _CONTEXT_PATHS[2])
    anchored_manifest = {
        "component_ids": _component_ids(context2),
        "diagnosis": load_json_object(root / _RUN_ARTIFACTS["diagnosis"]),
        "crops": coordinates.get("crops"),
    }
    result = apply_svg_crop_manifest(
        root / _RUN_ARTIFACTS["png1_5"], anchored_manifest, output_path.parent
    )
    _atomic_json(output_path, result)
    return {"crops": len(result["crops"]), "path": _RUN_ARTIFACTS["approved_crops"]}


def _replacement_crops(root: Path) -> dict[str, Any]:
    path = root / "references/web/crops/replacements/manifest.json"
    return load_json_object(path) if path.is_file() else {"crops": []}


def _cmd_build_prompt2(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context1, context2, context3 = _contexts(root)
    bundle = build_prompt2_bundle(
        (root / _RUN_ARTIFACTS["methodology"]).read_text(encoding="utf-8"),
        context1,
        context2,
        context3,
        _RUN_ARTIFACTS["png1"],
        load_json_object(root / _RUN_ARTIFACTS["diagnosis"]),
        load_json_object(root / _RUN_ARTIFACTS["approved_crops"]),
        _replacement_crops(root),
        root,
    )
    write_bundle(bundle, root / "prompt-2")
    return {"phase": "prompt2", "attachments": len(bundle["attachments"]), "path": "prompt-2"}


def _verify_png(path: Path, name: str) -> None:
    from PIL import Image

    try:
        with Image.open(path) as image:
            if image.format != "PNG" or image.width <= 0 or image.height <= 0:
                raise ValueError(f"{name} must be a real nonempty PNG")
            image.verify()
    except OSError as error:
        raise ValueError(f"{name} must be a real nonempty PNG") from error


def _expected_attachments(bundle: dict[str, Any]) -> bytes:
    attachments = sorted(bundle["attachments"], key=lambda item: (item["path"], item["role"]))
    return (json.dumps(attachments, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _validate_bundle_files(root: Path, bundle: dict[str, Any], phase: int) -> None:
    directory = root / f"prompt-{phase}"
    if (directory / "prompt.md").read_text(encoding="utf-8") != bundle["prompt"]:
        raise ValueError(f"prompt-{phase}/prompt.md does not match the compiled bundle")
    if (directory / "attachments.json").read_bytes() != _expected_attachments(bundle):
        raise ValueError(f"prompt-{phase}/attachments.json does not match the compiled bundle")


def _cmd_validate_run(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    manifest = validate_run_manifest(load_json_object(root / "run-manifest.json"), root)
    if manifest["artifacts"] != _RUN_ARTIFACTS:
        raise ValueError("run manifest must declare the exact canonical artifact structure")

    context1, context2, context3 = _contexts(root)
    normalized1 = validate_context1(context1)
    normalized2 = validate_context2(context2)
    component_ids = _component_ids(normalized2)
    normalized3 = validate_context3(context3, component_ids)
    validate_palette(normalized3["palette"], _palette_library())
    load_json_object(root / _RUN_ARTIFACTS["web_manifest"])

    candidates = load_json_object(root / _RUN_ARTIFACTS["figurebench_candidates"])
    expected_candidates = rank_candidates(normalized2, load_reference_index(_REFERENCE_PACK))
    if candidates != {"candidates": expected_candidates}:
        raise ValueError("FigureBench candidates do not match deterministic ranking")
    crop_manifest = load_json_object(root / _RUN_ARTIFACTS["figurebench_crops"])
    coverage = validate_reference_coverage(
        normalized2, crop_manifest, crop_manifest.get("basic_geometry", [])
    )
    if coverage["coverage_matrix"] != normalized3["coverage_matrix"]:
        raise ValueError("Context 3 coverage_matrix does not match reference coverage")

    diagnosis = load_json_object(root / _RUN_ARTIFACTS["diagnosis"])
    validate_diagnosis(diagnosis, component_ids)
    inspect_editable_svg(root / _RUN_ARTIFACTS["svg1"])
    for key in ("png1", "png1_5", "png2"):
        _verify_png(root / _RUN_ARTIFACTS[key], key)

    methodology = (root / _RUN_ARTIFACTS["methodology"]).read_text(encoding="utf-8")
    prompt1 = build_prompt1_bundle(
        methodology, normalized1, normalized2, normalized3, _optional_user_reference(root), root
    )
    _validate_bundle_files(root, prompt1, 1)
    prompt2 = build_prompt2_bundle(
        methodology,
        normalized1,
        normalized2,
        normalized3,
        _RUN_ARTIFACTS["png1"],
        diagnosis,
        load_json_object(root / _RUN_ARTIFACTS["approved_crops"]),
        _replacement_crops(root),
        root,
    )
    _validate_bundle_files(root, prompt2, 2)

    model_images = sorted(path.name for path in root.glob("*.png"))
    if model_images != ["png1.png", "png2-final.png"]:
        raise ValueError("run requires exactly PNG1 and PNG2 as model image artifacts")
    diagnostic_roots = sorted(
        path.name for path in root.glob("svg-diagnostic*") if path.is_dir()
    )
    if diagnostic_roots != ["svg-diagnostic"]:
        raise ValueError("run requires exactly one svg-diagnostic artifact root")
    prompt_roots = sorted(path.name for path in root.glob("prompt-*") if path.is_dir())
    if prompt_roots != ["prompt-1", "prompt-2"]:
        raise ValueError("run requires exactly two prompt artifact roots")
    return {
        "artifacts": len(manifest["artifacts"]),
        "model_images": model_images,
        "diagnostic_roots": diagnostic_roots,
        "status": "valid",
    }


def _parser() -> _Parser:
    parser = _Parser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    installation = commands.add_parser("check-installation")
    installation.add_argument("--root", default=REPOSITORY_ROOT)
    installation.set_defaults(handler=_cmd_check_installation)

    handlers: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
        "rank-references": _cmd_rank_references,
        "crop-references": _cmd_crop_references,
        "validate-reference-coverage": _cmd_validate_reference_coverage,
        "validate-palette": _cmd_validate_palette,
        "build-prompt1": _cmd_build_prompt1,
        "inspect-svg": _cmd_inspect_svg,
        "render-svg": _cmd_render_svg,
        "validate-diagnosis": _cmd_validate_diagnosis,
        "crop-svg": _cmd_crop_svg,
        "build-prompt2": _cmd_build_prompt2,
        "validate-run": _cmd_validate_run,
    }
    context = commands.add_parser("validate-context")
    context.add_argument("--run", required=True)
    context.add_argument("--context", required=True, type=int, choices=(1, 2, 3))
    context.set_defaults(handler=_cmd_validate_context)
    for name, handler in handlers.items():
        command = commands.add_parser(name)
        command.add_argument("--run", required=True)
        command.set_defaults(handler=handler)
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    try:
        if _BOOTSTRAP_ERROR is not None:
            raise ImportError(str(_BOOTSTRAP_ERROR)) from _BOOTSTRAP_ERROR
        result = arguments.handler(arguments)
    except (ImportError, OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
