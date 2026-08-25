"""Deterministic publication and provenance checks for a complete figure run."""

from __future__ import annotations

import copy
import json
import os
from collections.abc import Collection, Mapping
from pathlib import Path, PurePosixPath
import tempfile
from typing import Any

from PIL import Image

from .artifacts import (
    load_json_object,
    run_artifact_paths,
    validate_context1,
    validate_context2,
    validate_context3,
    validate_diagnosis,
    validate_run_manifest,
    validate_web_manifest,
)
from .palette import validate_palette
from .prompts import (
    build_prompt1_bundle,
    build_prompt2_bundle,
    validate_prompt_bundle,
)
from .reference_pack import (
    apply_crop_manifest,
    load_reference_index,
    rank_candidates,
    validate_reference_coverage,
)
from .svg_diagnostics import apply_svg_crop_manifest, inspect_editable_svg, render_svg


_FIGUREBENCH_REQUEST = "references/figurebench/crops/request.json"
_FIGUREBENCH_MANIFEST = "references/figurebench/crops/manifest.json"
_FIGUREBENCH_CROP_ROOT = "references/figurebench/crops"
_SVG_REQUEST = "svg-diagnostic/approved-crops/request.json"
_SVG_MANIFEST = "svg-diagnostic/approved-crops/manifest.json"
_SVG_CROP_ROOT = "svg-diagnostic/approved-crops"
_FIGUREBENCH_FORMAT = "figurebench-materialized-crops-v1"
_SVG_FORMAT = "approved-svg-materialized-crops-v1"


def _real_root(value: str | Path, label: str) -> Path:
    root = Path(value)
    if not root.is_dir():
        raise ValueError(f"{label} must be an existing directory")
    return root.resolve(strict=True)


def _reject_symlink_ancestors(path: Path) -> None:
    absolute = Path(os.path.abspath(os.fspath(path)))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink() and current.parent != Path(absolute.anchor):
            raise ValueError("JSON output path must not contain a symlink destination")


def write_json_atomic(path: str | Path, value: Any) -> Path:
    """Serialize one JSON value deterministically and publish it atomically."""

    target = Path(path)
    _reject_symlink_ancestors(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    _reject_symlink_ancestors(target)
    if not target.parent.is_dir():
        raise ValueError("JSON output parent must be a real directory")
    try:
        payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
    except (TypeError, ValueError) as error:
        raise ValueError("JSON output cannot be serialized") from error
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        if target.is_symlink():
            raise ValueError("JSON output path must not be a symlink")
        os.replace(temporary, target)
        return target
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _decoded_png(path: Path, label: str) -> tuple[tuple[int, int], str, bytes]:
    try:
        with Image.open(path) as image:
            if image.format != "PNG" or image.width <= 0 or image.height <= 0:
                raise ValueError(f"{label} must be a real nonempty PNG")
            image.load()
            return image.size, image.mode, image.tobytes()
    except ValueError:
        raise
    except Exception as error:
        raise ValueError(f"{label} must be a real nonempty PNG") from error


def verify_png(path: str | Path, label: str) -> dict[str, Any]:
    """Validate a PNG and return its decoded structural facts."""

    size, mode, _ = _decoded_png(Path(path), label)
    return {"format": "PNG", "width": size[0], "height": size[1], "mode": mode}


def _compare_png(expected: Path, actual: Path, label: str) -> None:
    expected_decoded = _decoded_png(expected, f"expected {label}")
    actual_decoded = _decoded_png(actual, label)
    if expected_decoded != actual_decoded:
        raise ValueError(f"{label} decoded pixels, dimensions, or mode do not match deterministic materialization")


def _canonical_figurebench_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    crops = value.get("crops")
    if not isinstance(crops, list):
        raise ValueError("materialized FigureBench crops require a crops list")
    normalized = []
    for record in crops:
        if not isinstance(record, Mapping):
            raise ValueError("materialized FigureBench crops must be objects")
        crop = copy.deepcopy(dict(record))
        filename = crop.get("crop_path")
        if not isinstance(filename, str) or Path(filename).name != filename:
            raise ValueError("materialized FigureBench crop_path must be a filename")
        crop["crop_path"] = f"{_FIGUREBENCH_CROP_ROOT}/{filename}"
        normalized.append(crop)
    return {
        "format": _FIGUREBENCH_FORMAT,
        "request": _FIGUREBENCH_REQUEST,
        "crops": normalized,
    }


def materialize_figurebench_crops(
    reference_root: str | Path,
    request: Mapping[str, Any],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Apply a preserved FigureBench request and return its canonical manifest."""

    result = apply_crop_manifest(Path(reference_root), request, Path(output_dir))
    return _canonical_figurebench_manifest(result)


def materialize_svg_crops(
    rendered_png: str | Path,
    request: Mapping[str, Any],
    diagnosis: Mapping[str, Any],
    component_ids: Collection[str],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Apply a preserved SVG crop request with an external Context 2 anchor."""

    crops = request.get("crops") if isinstance(request, Mapping) else None
    anchored = {
        "component_ids": list(component_ids),
        "diagnosis": diagnosis,
        "crops": crops,
    }
    result = apply_svg_crop_manifest(Path(rendered_png), anchored, Path(output_dir))
    manifest = {
        "format": _SVG_FORMAT,
        "request": _SVG_REQUEST,
        "crops": result["crops"],
    }
    return manifest


def _safe_run_file(root: Path, relative: str, label: str) -> Path:
    declared = PurePosixPath(relative)
    if declared.is_absolute() or ".." in declared.parts:
        raise ValueError(f"{label} must be a safe run-relative path")
    path = root.joinpath(*declared.parts)
    if not path.is_file() or not path.resolve(strict=True).is_relative_to(root):
        raise ValueError(f"{label} requires an existing file under the run root")
    return path


def _assert_manifest(expected: Mapping[str, Any], actual: Mapping[str, Any], label: str) -> None:
    if dict(actual) != dict(expected):
        raise ValueError(f"{label} does not match deterministic materialization")


def validate_svg_diagnostic_chain(
    run_root: str | Path, component_ids: Collection[str]
) -> dict[str, Any]:
    """Replay SVG rendering/cropping in temporary storage and compare decoded output."""

    root = _real_root(run_root, "run root")
    ids = list(component_ids)
    diagnosis = load_json_object(root / "svg-diagnostic/diagnosis.json")
    normalized_diagnosis = validate_diagnosis(diagnosis, ids)
    request = load_json_object(root / _SVG_REQUEST)
    stored_manifest = load_json_object(root / _SVG_MANIFEST)
    inspection = inspect_editable_svg(root / "svg-diagnostic/svg1.svg")

    with tempfile.TemporaryDirectory() as temporary_directory:
        replay_root = Path(temporary_directory) / "run"
        replay_svg_root = replay_root / "svg-diagnostic"
        replay_svg_root.mkdir(parents=True)
        replay_png = replay_svg_root / "png1.5.png"
        render_svg(root / "svg-diagnostic/svg1.svg", replay_png)
        _compare_png(replay_png, root / "svg-diagnostic/png1.5.png", "PNG1.5")
        replay_crop_root = replay_svg_root / "approved-crops"
        replay_manifest = materialize_svg_crops(
            replay_png,
            request,
            normalized_diagnosis,
            ids,
            replay_crop_root,
        )
        _assert_manifest(replay_manifest, stored_manifest, "approved SVG crop manifest")
        for record in replay_manifest["crops"]:
            relative = record.get("path")
            if not isinstance(relative, str):
                raise ValueError("approved SVG crop manifest requires path")
            name = PurePosixPath(relative).name
            _compare_png(
                replay_crop_root / name,
                _safe_run_file(root, relative, "approved SVG crop"),
                f"approved SVG crop {name}",
            )
    return {
        "status": "valid",
        "editable_nodes": inspection["editable_nodes"],
        "verdicts": len(normalized_diagnosis["verdicts"]),
        "approved_crops": len(stored_manifest["crops"]),
    }


def load_palette_library(path: str | Path) -> list[dict[str, Any]]:
    """Load the approved palette groups from a palette-library JSON object."""

    value = load_json_object(path)
    palettes = value.get("palettes")
    if not isinstance(palettes, list):
        raise ValueError("palette library requires palettes list")
    return palettes


def _load_json_array(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{label} contains invalid JSON: {error.msg}") from error
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{label} must be a list of objects")
    return value


def find_user_reference(run_root: str | Path) -> str | None:
    """Return the canonical optional user-reference path for one run."""

    root = _real_root(run_root, "run root")
    candidates = sorted(path for path in (root / "input").glob("user-reference.*") if path.is_file())
    if len(candidates) > 1:
        raise ValueError("run input requires at most one user-reference file")
    return candidates[0].relative_to(root).as_posix() if candidates else None


def _replacement_crops(root: Path) -> dict[str, Any]:
    path = root / "references/web/crops/replacements/manifest.json"
    return load_json_object(path) if path.is_file() else {"crops": []}


def _validate_stored_bundle(root: Path, expected: Mapping[str, Any], phase: int) -> None:
    directory = root / f"prompt-{phase}"
    stored = {
        "format": expected["format"],
        "phase": f"prompt{phase}",
        "prompt": (directory / "prompt.md").read_text(encoding="utf-8"),
        "component_ids": expected["component_ids"],
        "attachments": _load_json_array(
            directory / "attachments.json", f"prompt-{phase} attachments"
        ),
    }
    normalized_stored = validate_prompt_bundle(stored, root)
    normalized_expected = validate_prompt_bundle(expected, root)
    if normalized_stored != normalized_expected:
        raise ValueError(f"prompt-{phase} bundle does not match deterministic compilation")


def _validate_figurebench_chain(
    root: Path,
    reference_root: Path,
    context2: Mapping[str, Any],
    context3: Mapping[str, Any],
) -> dict[str, Any]:
    request = load_json_object(root / _FIGUREBENCH_REQUEST)
    stored_manifest = load_json_object(root / _FIGUREBENCH_MANIFEST)
    coverage = validate_reference_coverage(
        context2, request, request.get("basic_geometry", [])
    )
    if coverage["coverage_matrix"] != context3["coverage_matrix"]:
        raise ValueError("Context 3 coverage_matrix does not match preserved FigureBench request")
    with tempfile.TemporaryDirectory() as temporary_directory:
        replay_root = Path(temporary_directory) / "run/references/figurebench/crops"
        replay_manifest = materialize_figurebench_crops(
            reference_root,
            request,
            replay_root,
        )
        _assert_manifest(replay_manifest, stored_manifest, "FigureBench crop manifest")
        for record in replay_manifest["crops"]:
            relative = record["crop_path"]
            name = PurePosixPath(relative).name
            _compare_png(
                replay_root / name,
                _safe_run_file(root, relative, "FigureBench crop"),
                f"FigureBench crop {name}",
            )
    fields = (
        "crop_id",
        "reference_id",
        "crop_path",
        "target_component_id",
        "crop_contract",
    )
    expected_selections = {
        record["crop_id"]: {field: record[field] for field in fields}
        for record in stored_manifest["crops"]
    }
    actual_selections = {
        record["crop_id"]: {field: record[field] for field in fields}
        for record in context3["selected_references"]
    }
    if actual_selections != expected_selections:
        raise ValueError("Context 3 selected references do not match materialized FigureBench crops")
    return {"crops": len(stored_manifest["crops"]), "coverage": coverage}


def validate_complete_run(
    run_root: str | Path,
    reference_pack_root: str | Path,
    palette_library_path: str | Path,
) -> dict[str, Any]:
    """Validate every deterministic artifact and provenance edge through final PNG2."""

    root = _real_root(run_root, "run root")
    references = _real_root(reference_pack_root, "reference pack root")
    artifacts = run_artifact_paths()
    manifest = validate_run_manifest(load_json_object(root / "run-manifest.json"), root)
    if manifest["artifacts"] != artifacts:
        raise ValueError("run manifest must declare the exact canonical artifact structure")

    context1 = validate_context1(load_json_object(root / artifacts["context1"]))
    context2 = validate_context2(load_json_object(root / artifacts["context2"]))
    component_ids = [component["id"] for component in context2["components"]]
    context3 = validate_context3(
        load_json_object(root / artifacts["context3"]), component_ids
    )
    validate_palette(context3["palette"], load_palette_library(palette_library_path))
    validate_web_manifest(
        load_json_object(root / artifacts["web_manifest"]), root, context1
    )

    candidates = load_json_object(root / artifacts["figurebench_candidates"])
    expected_candidates = rank_candidates(context2, load_reference_index(references))
    if candidates != {"candidates": expected_candidates}:
        raise ValueError("FigureBench candidates do not match deterministic ranking")
    figurebench = _validate_figurebench_chain(root, references, context2, context3)

    verify_png(root / artifacts["png1"], "PNG1")
    svg = validate_svg_diagnostic_chain(root, component_ids)
    verify_png(root / artifacts["png2"], "PNG2")

    methodology = (root / artifacts["methodology"]).read_text(encoding="utf-8")
    prompt1 = build_prompt1_bundle(
        methodology,
        context1,
        context2,
        context3,
        find_user_reference(root),
        root,
    )
    _validate_stored_bundle(root, prompt1, 1)
    prompt2 = build_prompt2_bundle(
        methodology,
        context1,
        context2,
        context3,
        artifacts["png1"],
        load_json_object(root / artifacts["diagnosis"]),
        load_json_object(root / artifacts["approved_crops"]),
        _replacement_crops(root),
        root,
    )
    _validate_stored_bundle(root, prompt2, 2)

    images = sorted(path.name for path in root.glob("*.png"))
    if images != ["png1.png", "png2-final.png"]:
        raise ValueError("run requires exactly PNG1 and PNG2 as image artifacts")
    diagnostic_roots = sorted(
        path.name for path in root.glob("svg-diagnostic*") if path.is_dir()
    )
    if diagnostic_roots != ["svg-diagnostic"]:
        raise ValueError("run requires exactly one svg-diagnostic artifact root")
    prompt_roots = sorted(path.name for path in root.glob("prompt-*") if path.is_dir())
    if prompt_roots != ["prompt-1", "prompt-2"]:
        raise ValueError("run requires exactly two prompt artifact roots")
    return {
        "status": "valid",
        "artifacts": len(manifest["artifacts"]),
        "images": images,
        "diagnostic_roots": diagnostic_roots,
        "figurebench_crops": figurebench["crops"],
        "approved_svg_crops": svg["approved_crops"],
    }
