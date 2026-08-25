#!/usr/bin/env python3
"""Deterministic CLI for the evidence-guided two-pass figure workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Callable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

_BOOTSTRAP_ERROR: ImportError | None = None
try:
    from check_installation import validate_installation  # noqa: E402
    from scientific_figure_workflow import (  # noqa: E402
        build_prompt1_bundle,
        build_prompt2_bundle,
        find_user_reference,
        inspect_editable_svg,
        load_palette_library,
        load_json_object,
        load_reference_index,
        materialize_figurebench_crops,
        materialize_svg_crops,
        rank_candidates,
        render_svg,
        run_artifact_paths,
        validate_complete_run,
        validate_context1,
        validate_context2,
        validate_context3,
        validate_diagnosis,
        validate_palette,
        validate_reference_coverage,
        validate_web_manifest,
        write_json_atomic,
        write_bundle,
    )
except ImportError as error:  # handled at the subprocess boundary below
    _BOOTSTRAP_ERROR = error


_CONTEXT_PATHS = {
    1: "context/context-1-domain-conventions.json",
    2: "context/context-2-content-visual-plan.json",
    3: "context/context-3-visual-kit.json",
}
_RUN_ARTIFACTS = run_artifact_paths() if _BOOTSTRAP_ERROR is None else {}
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


def _contexts(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context1 = load_json_object(root / _CONTEXT_PATHS[1])
    context2 = load_json_object(root / _CONTEXT_PATHS[2])
    context3 = load_json_object(root / _CONTEXT_PATHS[3])
    return context1, context2, context3


def _palette_library() -> list[dict[str, Any]]:
    return load_palette_library(_PALETTE_LIBRARY)


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
    write_json_atomic(root / _RUN_ARTIFACTS["figurebench_candidates"], {"candidates": ranked})
    return {"candidates": len(ranked), "path": _RUN_ARTIFACTS["figurebench_candidates"]}


def _cmd_crop_references(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    request = load_json_object(root / _RUN_ARTIFACTS["figurebench_crop_request"])
    output_dir = root / "references/figurebench/crops"
    result = materialize_figurebench_crops(
        _REFERENCE_PACK,
        request,
        output_dir,
    )
    write_json_atomic(root / _RUN_ARTIFACTS["figurebench_crops"], result)
    return {"crops": len(result["crops"]), "paths": [item["crop_path"] for item in result["crops"]]}


def _cmd_validate_reference_coverage(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context2 = validate_context2(load_json_object(root / _CONTEXT_PATHS[2]))
    request = load_json_object(root / _RUN_ARTIFACTS["figurebench_crop_request"])
    return validate_reference_coverage(context2, request, request.get("basic_geometry", []))


def _cmd_validate_palette(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context3 = load_json_object(root / _CONTEXT_PATHS[3])
    return validate_palette(context3.get("palette"), _palette_library())


def _cmd_build_prompt1(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    context1, context2, context3 = _contexts(root)
    validate_web_manifest(
        load_json_object(root / _RUN_ARTIFACTS["web_manifest"]), root, context1
    )
    methodology = (root / _RUN_ARTIFACTS["methodology"]).read_text(encoding="utf-8")
    bundle = build_prompt1_bundle(
        methodology, context1, context2, context3, find_user_reference(root), root
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
    request = load_json_object(root / _RUN_ARTIFACTS["approved_crop_request"])
    context2 = load_json_object(root / _CONTEXT_PATHS[2])
    result = materialize_svg_crops(
        root / _RUN_ARTIFACTS["png1_5"],
        request,
        load_json_object(root / _RUN_ARTIFACTS["diagnosis"]),
        _component_ids(context2),
        output_path.parent,
    )
    write_json_atomic(output_path, result)
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


def _cmd_validate_run(arguments: argparse.Namespace) -> dict[str, Any]:
    root = _run_root(arguments.run)
    return validate_complete_run(root, _REFERENCE_PACK, _PALETTE_LIBRARY)


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
