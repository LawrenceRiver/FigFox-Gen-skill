"""Validate and rank the bundled, development-only FigureBench reference pack."""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from PIL import Image


INDEX_FIELDS = {
    "id",
    "file",
    "partition",
    "source_id",
    "source_kind",
    "license",
    "attribution",
    "components",
    "layout_family",
    "human_editable_signals",
    "description",
}
_TAG_FIELDS = ("components", "human_editable_signals")
_REDISTRIBUTION_LICENSES = {"CC-BY-4.0", "CC-BY-SA-4.0", "CC0-1.0"}
_FIGUREBENCH_LICENSE_NOTICE = (
    "FigureBench dataset license (separate; does not determine original-figure rights): "
    "CC-BY-4.0; metadata: "
    "https://huggingface.co/datasets/WestlakeNLP/FigureBench/blob/main/README.md."
)


def _non_empty_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires a non-empty string")
    return value.strip()


def _non_empty_tags(value: Any, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location} requires at least one construction tag")
    tags = [_non_empty_string(item, location) for item in value]
    if len(tags) != len(set(tags)):
        raise ValueError(f"{location} tags must be unique")
    return tags


def _index_records(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, list):
        records = value
    elif isinstance(value, Mapping):
        records = value.get("references")
    else:
        records = None
    if not isinstance(records, list):
        raise ValueError("index.json requires a references list")
    if not all(isinstance(record, Mapping) for record in records):
        raise ValueError("index.json references must be objects")
    return records


def _validate_record(record: Mapping[str, Any], location: str) -> dict[str, Any]:
    if set(record) != INDEX_FIELDS:
        missing = sorted(INDEX_FIELDS - set(record))
        unexpected = sorted(set(record) - INDEX_FIELDS)
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected fields: {', '.join(unexpected)}")
        raise ValueError(f"{location} must contain exactly maintained fields ({'; '.join(details)})")

    normalized = copy.deepcopy(dict(record))
    for field in INDEX_FIELDS - set(_TAG_FIELDS):
        normalized[field] = _non_empty_string(record[field], f"{location} {field}")
    for field in _TAG_FIELDS:
        normalized[field] = _non_empty_tags(record[field], f"{location} {field}")
    if normalized["partition"] != "dev":
        raise ValueError(f"{location} partition must be dev")
    if Path(normalized["file"]).name != normalized["file"] or not normalized["file"].endswith(".png"):
        raise ValueError(f"{location} file must be a PNG filename")
    if normalized["license"] not in _REDISTRIBUTION_LICENSES:
        raise ValueError(f"{location} license must permit original-figure redistribution")
    attribution = normalized["attribution"]
    evidence_marker = f"original-figure license: {normalized['license']}; evidence: "
    evidence_start = attribution.find(evidence_marker)
    evidence_url = ""
    if evidence_start >= 0:
        evidence_url = attribution[evidence_start + len(evidence_marker):].split(maxsplit=1)[0].removesuffix(".")
    parsed_evidence = urlsplit(evidence_url)
    evidence_is_direct = (
        "Original figure source:" in attribution
        and parsed_evidence.scheme == "https"
        and bool(parsed_evidence.hostname)
        and parsed_evidence.hostname not in {"creativecommons.org", "huggingface.co"}
    )
    if parsed_evidence.hostname == "arxiv.org":
        evidence_is_direct = evidence_is_direct and parsed_evidence.path.rstrip("/") == (
            f"/abs/{normalized['source_id']}"
        )
    if not evidence_is_direct or _FIGUREBENCH_LICENSE_NOTICE not in attribution:
        raise ValueError(
            f"{location} requires original-figure license evidence separate from "
            "FigureBench dataset licensing"
        )
    return normalized


def load_reference_index(root: str | Path) -> list[dict[str, Any]]:
    """Load and validate maintained metadata without requiring image bytes."""

    index_path = Path(root) / "index.json"
    try:
        value = json.loads(index_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"reference pack is missing {index_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"reference pack has invalid index.json: {error.msg}") from error

    records = [_validate_record(record, f"index references[{index}]") for index, record in enumerate(_index_records(value))]
    ids = [record["id"] for record in records]
    files = [record["file"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("index reference ids must be unique")
    if len(files) != len(set(files)):
        raise ValueError("index reference files must be unique")
    return records


def validate_reference_pack(root: str | Path, expected_count: int = 30) -> dict[str, Any]:
    """Validate the distributable pack and report count, partitions, and missing files."""

    if not isinstance(expected_count, int) or isinstance(expected_count, bool) or expected_count < 1:
        raise ValueError("expected_count must be a positive integer")
    pack_root = Path(root)
    records = load_reference_index(pack_root)
    if len(records) != expected_count:
        raise ValueError(f"reference pack requires exactly {expected_count} index records")
    missing = [record["file"] for record in records if not (pack_root / record["file"]).is_file()]
    if missing:
        raise ValueError(f"reference pack is missing indexed files: {', '.join(missing)}")
    png_files = sorted(path.name for path in pack_root.glob("*.png"))
    indexed_files = sorted(record["file"] for record in records)
    if png_files != indexed_files:
        raise ValueError("reference pack PNG files must exactly match index files")
    return {
        "references": len(records),
        "missing": missing,
        "partitions": sorted({record["partition"] for record in records}),
    }


def _strings(value: Any) -> set[str]:
    if isinstance(value, str) and value.strip():
        return {value.strip()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return {item.strip() for item in value if isinstance(item, str) and item.strip()}
    return set()


def _context_component_tags(context2: Mapping[str, Any]) -> set[str]:
    tags = _strings(context2.get("components_needed")) | _strings(context2.get("geometry_tags"))
    components = context2.get("components", [])
    if not isinstance(components, Sequence) or isinstance(components, (str, bytes)):
        return tags
    for component in components:
        if not isinstance(component, Mapping):
            continue
        tags |= _strings(component.get("visual_treatment"))
        tags |= _strings(component.get("geometry_tags"))
        tags |= _strings(component.get("components"))
    return tags


def _context_layouts(context2: Mapping[str, Any]) -> set[str]:
    return (
        _strings(context2.get("layout_family"))
        | _strings(context2.get("layout_families"))
        | _strings(context2.get("layout"))
        | _strings(context2.get("layout_preferences"))
    )


def _context_editability(context2: Mapping[str, Any]) -> set[str]:
    tags = _strings(context2.get("human_editable_signals"))
    components = context2.get("components", [])
    if isinstance(components, Sequence) and not isinstance(components, (str, bytes)):
        for component in components:
            if isinstance(component, Mapping):
                tags |= _strings(component.get("human_editable_signals"))
    return tags


def rank_candidates(
    context2: Mapping[str, Any], references: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """Rank development references by compatible geometry, layout, and editability.

    Extra fields in either input are deliberately ignored so workflow artifacts can
    evolve without invalidating this deterministic selection aid.
    """

    needed_components = _context_component_tags(context2)
    needed_layouts = _context_layouts(context2)
    needed_editability = _context_editability(context2)
    scored: list[dict[str, Any]] = []
    for position, reference in enumerate(references):
        if not isinstance(reference, Mapping):
            raise ValueError(f"references[{position}] must be an object")
        normalized = copy.deepcopy(dict(reference))
        reference_id = _non_empty_string(normalized.get("id"), f"references[{position}] id")
        partition = _non_empty_string(normalized.get("partition"), f"references[{position}] partition")
        if partition != "dev":
            raise ValueError("rank_candidates accepts development references only")
        source_id = _non_empty_string(normalized.get("source_id"), f"references[{position}] source_id")
        components = _strings(normalized.get("components"))
        layout_family = _non_empty_string(normalized.get("layout_family"), f"references[{position}] layout_family")
        editability = _strings(normalized.get("human_editable_signals"))
        matched_components = sorted(needed_components & components)
        matched_layouts = sorted(needed_layouts & {layout_family})
        matched_editability = sorted(needed_editability & editability)
        normalized.update(
            {
                "id": reference_id,
                "partition": partition,
                "source_id": source_id,
                "matched_components": matched_components,
                "matched_layouts": matched_layouts,
                "matched_human_editable_signals": matched_editability,
                "score": 5 * len(matched_components)
                + 3 * len(matched_layouts)
                + 2 * len(matched_editability),
            }
        )
        scored.append(normalized)

    # Score dominates.  Within each score group, choose unseen layouts and sources
    # greedily, then the stable id; this makes ties diverse without randomness.
    ranked: list[dict[str, Any]] = []
    for score in sorted({item["score"] for item in scored}, reverse=True):
        pending = sorted((item for item in scored if item["score"] == score), key=lambda item: item["id"])
        seen_layouts = {item["layout_family"] for item in ranked}
        seen_sources = {item["source_id"] for item in ranked}
        while pending:
            selected = min(
                pending,
                key=lambda item: (
                    item["layout_family"] in seen_layouts,
                    item["source_id"] in seen_sources,
                    item["id"],
                ),
            )
            pending.remove(selected)
            ranked.append(selected)
            seen_layouts.add(selected["layout_family"])
            seen_sources.add(selected["source_id"])
    return ranked


def _crop_id(value: Any, location: str) -> str:
    crop_id = _non_empty_string(value, location)
    if Path(crop_id).name != crop_id or crop_id in {".", ".."}:
        raise ValueError(f"{location} must be a filename-safe crop id")
    return crop_id


def _crop_bounds(value: Any, location: str) -> list[float]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 4:
        raise ValueError(f"{location} bounds requires [left, top, right, bottom]")
    if any(not isinstance(coordinate, (int, float)) or isinstance(coordinate, bool) for coordinate in value):
        raise ValueError(f"{location} bounds requires numeric coordinates")
    bounds = [float(coordinate) for coordinate in value]
    left, top, right, bottom = bounds
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ValueError(f"{location} bounds must be normalized and increasing within [0, 1]")
    return bounds


def _contract_strings(value: Any, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location} requires a non-empty list")
    strings = [_non_empty_string(item, location) for item in value]
    if len(strings) != len(set(strings)):
        raise ValueError(f"{location} values must be unique")
    return strings


def _crop_contract(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{location} requires an object")
    required_fields = {"borrow", "must_change", "human_editable_reason"}
    if set(value) != required_fields:
        raise ValueError(f"{location} requires borrow, must_change, and human_editable_reason")
    return {
        "borrow": _contract_strings(value["borrow"], f"{location} borrow"),
        "must_change": _contract_strings(value["must_change"], f"{location} must_change"),
        "human_editable_reason": _non_empty_string(
            value["human_editable_reason"], f"{location} human_editable_reason"
        ),
    }


def _normalise_crops(crop_manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(crop_manifest, Mapping):
        raise ValueError("crop manifest requires an object")
    crops = crop_manifest.get("crops")
    if not isinstance(crops, Sequence) or isinstance(crops, (str, bytes)) or not crops:
        raise ValueError("crop manifest requires a non-empty crops list")

    normalized: list[dict[str, Any]] = []
    crop_ids: list[str] = []
    for index, crop in enumerate(crops):
        location = f"crop manifest crops[{index}]"
        if not isinstance(crop, Mapping):
            raise ValueError(f"{location} requires an object")
        required_fields = {"id", "reference_id", "bounds", "target_component_id", "crop_contract"}
        if set(crop) != required_fields:
            raise ValueError(
                f"{location} requires exactly id, reference_id, bounds, target_component_id, and crop_contract"
            )
        crop_id = _crop_id(crop["id"], f"{location} id")
        crop_ids.append(crop_id)
        normalized.append({
            "id": crop_id,
            "reference_id": _non_empty_string(crop["reference_id"], f"{location} reference_id"),
            "bounds": _crop_bounds(crop["bounds"], location),
            "target_component_id": _non_empty_string(
                crop["target_component_id"], f"{location} target_component_id"
            ),
            "crop_contract": _crop_contract(crop["crop_contract"], f"{location} crop_contract"),
        })
    if len(crop_ids) != len(set(crop_ids)):
        raise ValueError("crop manifest crop ids must be unique")
    return normalized


def apply_crop_manifest(
    reference_root: Path, manifest: Mapping[str, Any], output_dir: Path
) -> dict[str, Any]:
    """Write deterministic RGB crops from indexed complete FigureBench references."""

    records = load_reference_index(reference_root)
    files_by_id = {record["id"]: record["file"] for record in records}
    crops = _normalise_crops(manifest)
    normalized: list[dict[str, Any]] = []
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    for crop in crops:
        reference_id = crop["reference_id"]
        if reference_id not in files_by_id:
            raise ValueError(f"crop manifest reference_id is not indexed: {reference_id}")
        source_path = Path(reference_root) / files_by_id[reference_id]
        try:
            with Image.open(source_path) as source:
                image = source.convert("RGB")
        except OSError as error:
            raise ValueError(f"crop manifest cannot read complete reference image: {source_path}") from error
        left, top, right, bottom = crop["bounds"]
        coordinates = (
            int(left * image.width),
            int(top * image.height),
            int(right * image.width),
            int(bottom * image.height),
        )
        if coordinates[0] >= coordinates[2] or coordinates[1] >= coordinates[3]:
            raise ValueError(f"crop manifest bounds select no pixels for {crop['id']}")
        crop_path = f"{crop['id']}.png"
        image.crop(coordinates).save(destination / crop_path, format="PNG")
        normalized_crop = copy.deepcopy(crop)
        normalized_crop["crop_id"] = crop["id"]
        normalized_crop["crop_path"] = crop_path
        normalized.append(normalized_crop)
    return {"crops": normalized}


def _context_component_ids(context2: Mapping[str, Any]) -> set[str]:
    if not isinstance(context2, Mapping):
        raise ValueError("context2 requires an object")
    components = context2.get("components")
    if not isinstance(components, Sequence) or isinstance(components, (str, bytes)) or not components:
        raise ValueError("context2 requires a non-empty components list")
    component_ids = [
        _non_empty_string(component.get("id"), f"context2 components[{index}] id")
        if isinstance(component, Mapping)
        else None
        for index, component in enumerate(components)
    ]
    if any(component_id is None for component_id in component_ids):
        raise ValueError("context2 components must be objects")
    if len(component_ids) != len(set(component_ids)):
        raise ValueError("context2 component ids must be unique")
    return set(component_ids)


def _normalise_basic_geometry(
    basic_geometry: Sequence[Mapping[str, Any]], component_ids: set[str]
) -> list[dict[str, Any]]:
    if not isinstance(basic_geometry, Sequence) or isinstance(basic_geometry, (str, bytes)):
        raise ValueError("basic_geometry requires a list")
    normalized: list[dict[str, Any]] = []
    covered_ids: list[str] = []
    for index, record in enumerate(basic_geometry):
        location = f"basic_geometry[{index}]"
        if not isinstance(record, Mapping):
            raise ValueError(f"{location} requires an object")
        required_fields = {"component_id", "primitive", "construction_steps", "human_editable_reason"}
        if set(record) != required_fields:
            raise ValueError(
                f"{location} requires component_id, primitive, construction_steps, and human_editable_reason"
            )
        component_id = _non_empty_string(record["component_id"], f"{location} component_id")
        if component_id not in component_ids:
            raise ValueError(f"{location} component_id must name a Context 2 component")
        covered_ids.append(component_id)
        normalized.append({
            "component_id": component_id,
            "primitive": _non_empty_string(record["primitive"], f"{location} primitive"),
            "construction_steps": _contract_strings(record["construction_steps"], f"{location} construction_steps"),
            "human_editable_reason": _non_empty_string(
                record["human_editable_reason"], f"{location} human_editable_reason"
            ),
        })
    if len(covered_ids) != len(set(covered_ids)):
        raise ValueError("basic_geometry component ids must be unique")
    return normalized


def validate_reference_coverage(
    context2: Mapping[str, Any], crop_manifest: Mapping[str, Any], basic_geometry: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Require two complete references and coverage for every planned component."""

    component_ids = _context_component_ids(context2)
    crops = _normalise_crops(crop_manifest)
    crop_reference_ids = {crop["reference_id"] for crop in crops}
    if len(crop_reference_ids) < 2:
        raise ValueError("crop manifest requires two distinct reference_id values")
    crop_component_ids = {crop["target_component_id"] for crop in crops}
    unknown_crop_components = crop_component_ids - component_ids
    if unknown_crop_components:
        raise ValueError("crop manifest target_component_id must name a Context 2 component")
    geometry = _normalise_basic_geometry(basic_geometry, component_ids)
    geometry_component_ids = {record["component_id"] for record in geometry}
    covered_component_ids = crop_component_ids | geometry_component_ids
    if covered_component_ids != component_ids:
        raise ValueError("crop manifest and basic_geometry must cover every Context 2 component")
    crop_ids_by_component: dict[str, list[str]] = {}
    for crop in crops:
        crop_ids_by_component.setdefault(crop["target_component_id"], []).append(crop["id"])
    geometry_by_component = {record["component_id"]: record for record in geometry}
    coverage_matrix = []
    for component in context2["components"]:
        component_id = component["id"]
        if component_id in crop_ids_by_component:
            coverage_matrix.append({
                "component_id": component_id,
                "crop_ids": crop_ids_by_component[component_id],
            })
        else:
            record = geometry_by_component[component_id]
            coverage_matrix.append({
                "component_id": component_id,
                "basic_geometry_justification": (
                    f"Primitive: {record['primitive']}. "
                    f"Construction steps: {'; '.join(record['construction_steps'])}. "
                    f"Human-editable rationale: {record['human_editable_reason']}"
                ),
            })
    return {
        "crops": copy.deepcopy(crops),
        "basic_geometry": geometry,
        "covered_component_ids": sorted(covered_component_ids),
        "coverage_matrix": coverage_matrix,
    }
