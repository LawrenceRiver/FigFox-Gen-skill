"""Validate and rank the bundled, development-only FigureBench reference pack."""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


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
