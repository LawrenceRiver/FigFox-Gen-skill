"""Deterministic publication and provenance checks for a single PNG1 run."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import Image

from .artifacts import (
    load_json_object,
    run_artifact_paths,
    validate_context1,
    validate_context2,
    validate_context3,
    validate_creative_director,
    validate_run_manifest,
    validate_web_manifest,
)
from .palette import validate_palette
from .prompts import build_creative_director_prompt, build_prompt1_bundle, validate_prompt_bundle
from .reference_pack import apply_crop_manifest, load_reference_index, rank_candidates, validate_reference_coverage

_FIGUREBENCH_REQUEST = "references/figurebench/crops/request.json"
_FIGUREBENCH_MANIFEST = "references/figurebench/crops/manifest.json"
_FIGUREBENCH_CROP_ROOT = "references/figurebench/crops"
_FIGUREBENCH_FORMAT = "figurebench-materialized-crops-v1"


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
    """Serialize JSON deterministically and publish it atomically."""

    target = Path(path)
    _reject_symlink_ancestors(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.parent.is_dir() or target.is_symlink():
        raise ValueError("JSON output path must be a real file location")
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
        return target
    finally:
        temporary.unlink(missing_ok=True)


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
    size, mode, _ = _decoded_png(Path(path), label)
    return {"format": "PNG", "width": size[0], "height": size[1], "mode": mode}


def _compare_png(expected: Path, actual: Path, label: str) -> None:
    if _decoded_png(expected, f"expected {label}") != _decoded_png(actual, label):
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
    return {"format": _FIGUREBENCH_FORMAT, "request": _FIGUREBENCH_REQUEST, "crops": normalized}


def materialize_figurebench_crops(
    reference_root: str | Path, request: Mapping[str, Any], output_dir: str | Path
) -> dict[str, Any]:
    return _canonical_figurebench_manifest(
        apply_crop_manifest(Path(reference_root), request, Path(output_dir))
    )


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


def find_user_reference(run_root: str | Path) -> str | None:
    root = _real_root(run_root, "run root")
    candidates = sorted(path for path in (root / "input").glob("user-reference.*") if path.is_file())
    if len(candidates) > 1:
        raise ValueError("run input requires at most one user-reference file")
    return candidates[0].relative_to(root).as_posix() if candidates else None


def load_palette_library(path: str | Path) -> list[dict[str, Any]]:
    palettes = load_json_object(path).get("palettes")
    if not isinstance(palettes, list):
        raise ValueError("palette library requires palettes list")
    return palettes


def _load_json_array(path: Path, label: str) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{label} must be a list of objects")
    return value


def _validate_stored_bundle(root: Path, expected: Mapping[str, Any]) -> None:
    directory = root / "prompt-1"
    stored = {
        "format": expected["format"],
        "phase": "prompt1",
        "prompt": (directory / "prompt.md").read_text(encoding="utf-8"),
        "component_ids": expected["component_ids"],
        "attachments": _load_json_array(directory / "attachments.json", "prompt-1 attachments"),
    }
    if validate_prompt_bundle(stored, root) != validate_prompt_bundle(expected, root):
        raise ValueError("prompt-1 bundle does not match deterministic compilation")


def _validate_figurebench_chain(
    root: Path, reference_root: Path, context2: Mapping[str, Any], context3: Mapping[str, Any]
) -> dict[str, Any]:
    request = load_json_object(root / _FIGUREBENCH_REQUEST)
    stored_manifest = load_json_object(root / _FIGUREBENCH_MANIFEST)
    coverage = validate_reference_coverage(context2, request, request.get("basic_geometry", []))
    if coverage["coverage_matrix"] != context3["coverage_matrix"]:
        raise ValueError("Context 3 coverage_matrix does not match preserved FigureBench request")
    with tempfile.TemporaryDirectory() as temporary_directory:
        replay_root = Path(temporary_directory) / "run/references/figurebench/crops"
        replay_manifest = materialize_figurebench_crops(reference_root, request, replay_root)
        _assert_manifest(replay_manifest, stored_manifest, "FigureBench crop manifest")
        for record in replay_manifest["crops"]:
            name = PurePosixPath(record["crop_path"]).name
            _compare_png(
                replay_root / name,
                _safe_run_file(root, record["crop_path"], "FigureBench crop"),
                f"FigureBench crop {name}",
            )
    fields = ("crop_id", "reference_id", "crop_path", "target_component_id", "crop_contract")
    expected = {
        record["crop_id"]: {field: record[field] for field in fields}
        for record in stored_manifest["crops"]
    }
    actual = {
        record["crop_id"]: {field: record[field] for field in fields}
        for record in context3["selected_references"]
    }
    if actual != expected:
        raise ValueError("Context 3 selected references do not match materialized FigureBench crops")
    return {"crops": len(stored_manifest["crops"]), "coverage": coverage}


def validate_complete_run(
    run_root: str | Path, reference_pack_root: str | Path, palette_library_path: str | Path
) -> dict[str, Any]:
    """Validate every deterministic artifact through the single final PNG1."""

    root = _real_root(run_root, "run root")
    references = _real_root(reference_pack_root, "reference pack root")
    artifacts = run_artifact_paths()
    manifest = validate_run_manifest(load_json_object(root / "run-manifest.json"), root)
    if manifest["artifacts"] != artifacts:
        raise ValueError("run manifest must declare the exact canonical artifact structure")

    context1 = validate_context1(load_json_object(root / artifacts["context1"]))
    context2 = validate_context2(load_json_object(root / artifacts["context2"]))
    component_ids = [component["id"] for component in context2["components"]]
    context3 = validate_context3(load_json_object(root / artifacts["context3"]), component_ids)
    validate_palette(context3["palette"], load_palette_library(palette_library_path))
    validate_web_manifest(load_json_object(root / artifacts["web_manifest"]), root, context1)

    candidates = load_json_object(root / artifacts["figurebench_candidates"])
    expected_candidates = rank_candidates(context2, load_reference_index(references))
    if candidates != {"candidates": expected_candidates}:
        raise ValueError("FigureBench candidates do not match deterministic ranking")
    figurebench = _validate_figurebench_chain(root, references, context2, context3)

    methodology = (root / artifacts["methodology"]).read_text(encoding="utf-8")
    creative_prompt = (root / artifacts["creative_director_prompt"]).read_text(encoding="utf-8")
    expected_creative_prompt = build_creative_director_prompt(
        methodology, context1, context2, context3
    )["prompt"]
    if creative_prompt != expected_creative_prompt:
        raise ValueError("Creative Director prompt does not match deterministic compilation")
    creative = validate_creative_director(
        load_json_object(root / artifacts["creative_director_brief"]), root, component_ids
    )

    verify_png(root / artifacts["png1"], "PNG1")
    prompt1 = build_prompt1_bundle(
        methodology, context1, context2, context3, find_user_reference(root), root, creative
    )
    _validate_stored_bundle(root, prompt1)

    images = sorted(path.name for path in root.glob("*.png"))
    if images != ["png1.png"]:
        raise ValueError("run requires exactly PNG1 as its image artifact")
    prompt_roots = sorted(path.name for path in root.glob("prompt-*") if path.is_dir())
    if prompt_roots != ["prompt-1"]:
        raise ValueError("run requires exactly one prompt artifact root")
    creative_roots = sorted(path.name for path in root.glob("creative-director") if path.is_dir())
    if creative_roots != ["creative-director"]:
        raise ValueError("run requires the creative-director artifact root")
    return {
        "status": "valid",
        "artifacts": len(manifest["artifacts"]),
        "images": images,
        "figurebench_crops": figurebench["crops"],
        "creative_director": creative["svg_evidence_status"],
    }
