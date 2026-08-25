"""Safe inspection, deterministic rendering, and diagnosis-gated SVG crops.

This module intentionally does not generate or modify SVG markup.  SVG1 is the
base multimodal model's direct transcription of PNG1; this code only validates
that submitted transcription, renders it to review-only PNG1.5, and crops
regions that an already-produced diagnosis explicitly approves.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from defusedxml import ElementTree as DefusedElementTree

from .artifacts import validate_diagnosis


_SVG_NAMESPACE = "http://www.w3.org/2000/svg"
_SVG_ROOT = f"{{{_SVG_NAMESPACE}}}svg"
_VECTOR_TAGS = frozenset({"rect", "circle", "ellipse", "line", "polyline", "polygon", "path"})
_BANNED_TAGS = frozenset({"script", "foreignobject"})
_NON_RENDERING_TAGS = frozenset({"defs", "clippath", "mask", "marker", "pattern", "symbol"})
_APPROVED_VERDICTS = frozenset({"keep", "accept_variation", "patch"})
_CANONICAL_CROP_SUFFIX = ("svg-diagnostic", "approved-crops")
_CROP_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_URL_FUNCTION = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
_CSS_IMPORT = re.compile(r"@import\s+(?:url\(\s*)?(['\"])(.*?)\1", re.IGNORECASE)


def _local_name(tag: object) -> str:
    """Return an XML local name without trusting an arbitrary namespace."""

    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def _is_remote_reference(value: str) -> bool:
    """Identify URLs that could make parsing or rendering network-dependent."""

    candidate = value.strip()
    if not candidate or candidate.startswith("#") or candidate.startswith("data:"):
        return False
    parsed = urlsplit(candidate)
    return bool(parsed.scheme) or candidate.startswith("//")


def _has_remote_reference(element: Any) -> bool:
    def has_remote_url(value: str) -> bool:
        return any(_is_remote_reference(match.group(2)) for match in _URL_FUNCTION.finditer(value)) or any(
            _is_remote_reference(match.group(2)) for match in _CSS_IMPORT.finditer(value)
        )

    for attribute, value in element.attrib.items():
        name = _local_name(attribute).casefold()
        if not isinstance(value, str):
            continue
        if name in {"href", "src"} and _is_remote_reference(value):
            return True
        if has_remote_url(value):
            return True
    if isinstance(element.text, str) and has_remote_url(element.text):
        return True
    return False


def inspect_editable_svg(path: str | Path) -> dict[str, int | bool]:
    """Safely inspect SVG1 and reject unsafe or raster-only submissions.

    A non-sole local or ``data:`` image is reported as ``raster_nodes`` rather
    than treated as semantic approval.  Whether it is a legitimate photographic
    crop is deliberately left to the VLM diagnosis and crop manifest gate.
    """

    source = Path(path)
    if not source.is_file():
        raise ValueError("SVG1 requires an existing file")
    try:
        root = DefusedElementTree.parse(source).getroot()
    except Exception as error:
        raise ValueError("SVG1 must be well-formed safe XML") from error
    if root.tag != _SVG_ROOT:
        raise ValueError("SVG1 root must be an SVG element in the SVG namespace")

    text_nodes = 0
    vector_nodes = 0
    raster_nodes = 0
    visible_editable_nodes = 0

    def visit(element: Any, hidden_definition: bool = False) -> None:
        nonlocal text_nodes, vector_nodes, raster_nodes, visible_editable_nodes
        tag = _local_name(element.tag).casefold()
        if tag in _BANNED_TAGS:
            raise ValueError(f"SVG1 must not contain {tag}")
        if _has_remote_reference(element):
            raise ValueError("SVG1 must not contain remote references")
        hidden_definition = hidden_definition or tag in _NON_RENDERING_TAGS
        if tag == "text":
            text_nodes += 1
            if not hidden_definition:
                visible_editable_nodes += 1
        elif tag in _VECTOR_TAGS:
            vector_nodes += 1
            if not hidden_definition:
                visible_editable_nodes += 1
        elif tag == "image":
            raster_nodes += 1
        for child in element:
            visit(child, hidden_definition)

    visit(root)

    editable_nodes = text_nodes + vector_nodes
    raster_only = raster_nodes > 0 and visible_editable_nodes == 0
    if raster_only:
        raise ValueError("SVG1 raster wrapper is not an editable SVG")
    if editable_nodes == 0 or visible_editable_nodes == 0:
        raise ValueError("SVG1 requires one or more editable text or vector nodes")
    return {
        "editable_nodes": editable_nodes,
        "text_nodes": text_nodes,
        "vector_nodes": vector_nodes,
        "raster_nodes": raster_nodes,
        "raster_only": False,
    }


def render_svg(svg_path: str | Path, png_path: str | Path) -> Path:
    """Render a validated SVG1 deterministically to review-only PNG1.5."""

    import cairosvg

    inspect_editable_svg(svg_path)
    target = Path(png_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(url=str(Path(svg_path)), write_to=str(target))
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError("SVG rendering did not produce PNG1.5")
    return target


def _string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires a non-empty string")
    return value.strip()


def _normalized_bounds(value: Any, location: str) -> tuple[float, float, float, float]:
    if not isinstance(value, Mapping) or set(value) != {"x", "y", "width", "height"}:
        raise ValueError(f"{location} requires normalized x, y, width, and height")
    numbers: dict[str, float] = {}
    for key in ("x", "y", "width", "height"):
        raw = value[key]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(raw):
            raise ValueError(f"{location} {key} must be a finite number")
        numbers[key] = float(raw)
    x, y, width, height = (numbers[key] for key in ("x", "y", "width", "height"))
    if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 1 or y + height > 1:
        raise ValueError(f"{location} must stay within normalized PNG1.5 bounds")
    return x, y, width, height


def _run_root_for_crop_directory(output_dir: Path) -> Path:
    resolved = output_dir.resolve()
    if tuple(resolved.parts[-2:]) != _CANONICAL_CROP_SUFFIX:
        raise ValueError("approved SVG crop output_dir must end with svg-diagnostic/approved-crops")
    return resolved.parents[1]


def _diagnosis_records(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw_diagnosis = manifest.get("diagnosis")
    if not isinstance(raw_diagnosis, Mapping):
        raise ValueError("crop manifest requires a diagnosis object")
    raw_records = raw_diagnosis.get("verdicts")
    if not isinstance(raw_records, list) or not raw_records:
        raise ValueError("crop manifest diagnosis requires verdict records")
    expected_ids = manifest.get("component_ids")
    if expected_ids is None:
        expected_ids = [record.get("component_id") for record in raw_records if isinstance(record, Mapping)]
    if not isinstance(expected_ids, list) or not all(isinstance(item, str) and item.strip() for item in expected_ids):
        raise ValueError("crop manifest component_ids must be non-empty component ids")
    normalized = validate_diagnosis(raw_diagnosis, expected_ids)
    records: dict[str, Mapping[str, Any]] = {}
    for record in normalized["verdicts"]:
        diagnosis_id = record.get("id", record["component_id"])
        if not isinstance(diagnosis_id, str) or not diagnosis_id.strip() or diagnosis_id in records:
            raise ValueError("diagnosis records require unique non-empty ids")
        records[diagnosis_id] = record
    return records


def _crop_records(manifest: Mapping[str, Any], diagnosis_records: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    raw_crops = manifest.get("crops")
    if not isinstance(raw_crops, list) or not raw_crops:
        raise ValueError("crop manifest requires one or more crops")
    normalized: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for index, crop in enumerate(raw_crops):
        location = f"crop manifest crops[{index}]"
        if not isinstance(crop, Mapping):
            raise ValueError(f"{location} must be an object")
        crop_id = _string(crop.get("crop_id"), f"{location} crop_id")
        if not _CROP_ID.fullmatch(crop_id):
            raise ValueError(f"{location} crop_id is not a safe filename")
        target_component_id = _string(crop.get("target_component_id"), f"{location} target_component_id")
        diagnosis_id = _string(crop.get("diagnosis_id"), f"{location} diagnosis_id")
        diagnosis = diagnosis_records.get(diagnosis_id)
        if diagnosis is None:
            raise ValueError(f"{location} must cite a real diagnosis record")
        if diagnosis["component_id"] != target_component_id:
            raise ValueError(f"{location} diagnosis must target the same Context 2 component")
        if diagnosis["verdict"] not in _APPROVED_VERDICTS:
            raise ValueError(f"{location} requires an approved diagnosis verdict")
        output_name = f"{crop_id}.png"
        if output_name in seen_paths:
            raise ValueError("crop manifest crop_id values must be unique")
        seen_paths.add(output_name)
        normalized.append({
            "output_name": output_name,
            "target_component_id": target_component_id,
            "diagnosis": diagnosis,
            "bounds": _normalized_bounds(crop.get("bounds"), f"{location} bounds"),
        })
    return normalized


def apply_svg_crop_manifest(rendered_png: Path, manifest: Mapping[str, Any], output_dir: Path) -> dict[str, Any]:
    """Materialize diagnosis-approved component crops from PNG1.5 only.

    ``output_dir`` must be a run's ``svg-diagnostic/approved-crops`` directory.
    Returned records are directly consumable as Task 5 ``svg_crops`` and never
    expose PNG1.5 as a Prompt 2 attachment.
    """

    from PIL import Image

    if not isinstance(manifest, Mapping):
        raise ValueError("crop manifest must be an object")
    rendered = Path(rendered_png).resolve(strict=True)
    if rendered.name.casefold() != "png1.5.png" or tuple(rendered.parts[-2:-1]) != ("svg-diagnostic",):
        raise ValueError("approved SVG crops must be made from svg-diagnostic/png1.5.png")
    run_root = _run_root_for_crop_directory(Path(output_dir))
    if rendered.parents[1] != run_root:
        raise ValueError("PNG1.5 and approved SVG crops must share a run root")
    diagnosis_records = _diagnosis_records(manifest)
    crops = _crop_records(manifest, diagnosis_records)
    destination = run_root / "svg-diagnostic" / "approved-crops"
    destination.mkdir(parents=True, exist_ok=True)

    attachments: list[dict[str, Any]] = []
    with Image.open(rendered) as image:
        width, height = image.size
        if width <= 0 or height <= 0:
            raise ValueError("PNG1.5 must have positive dimensions")
        for crop in crops:
            x, y, crop_width, crop_height = crop["bounds"]
            left, top = math.floor(x * width), math.floor(y * height)
            right, bottom = math.ceil((x + crop_width) * width), math.ceil((y + crop_height) * height)
            if right <= left or bottom <= top:
                raise ValueError("normalized crop bounds produced an empty PNG1.5 crop")
            target = destination / crop["output_name"]
            image.crop((left, top, right, bottom)).save(target, format="PNG")
            diagnosis = crop["diagnosis"]
            reason = diagnosis.get("reason", "diagnosis-approved SVG component")
            attachments.append({
                "path": f"svg-diagnostic/approved-crops/{crop['output_name']}",
                "target_component_id": crop["target_component_id"],
                "diagnosis": f"{diagnosis['verdict']}: {_string(reason, 'diagnosis reason')}",
            })
    return {"crops": attachments}
