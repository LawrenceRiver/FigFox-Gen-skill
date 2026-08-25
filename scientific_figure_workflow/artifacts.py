"""Validation helpers for model-produced two-pass workflow artifacts."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Collection, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


VERDICTS = {"keep", "accept_variation", "patch", "reject", "replace"}
PALETTE_RELATIONSHIPS = {
    "tint",
    "shade",
    "tone",
    "analogous_neighbour",
    "compatible_neutral",
    "controlled_contrast",
}
_UPPERCASE_HEX = re.compile(r"#[0-9A-F]{6}\Z")
_FORBIDDEN_PALETTE_FIELDS = {
    "additional_palette_ids",
    "base_palette",
    "palette_source",
    "palette_sources",
    "source_palette_ids",
    "user_reference_palette_id",
    "figurebench_palette_id",
}

_RUN_ARTIFACTS = {
    "methodology": "input/methodology.md",
    "context1": "context/context-1-domain-conventions.json",
    "context2": "context/context-2-content-visual-plan.json",
    "context3": "context/context-3-visual-kit.json",
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


def _mapping(value: Any, location: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{location} must be an object")
    return value


def _records(value: Any, location: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location} requires at least one record")
    return [_mapping(record, location) for record in value]


def _required_string(record: Mapping[str, Any], key: str, location: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires non-empty {key}")
    return value.strip()


def _required_value(record: Mapping[str, Any], key: str, location: str) -> Any:
    if key not in record or record[key] is None:
        raise ValueError(f"{location} requires {key}")
    return record[key]


def _unique_ids(records: list[Mapping[str, Any]], location: str) -> list[str]:
    ids = [_required_string(record, "id", location) for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{location} ids must be unique")
    return ids


def _normalized_record(record: Mapping[str, Any], string_keys: Collection[str]) -> dict[str, Any]:
    normalized = copy.deepcopy(dict(record))
    for key in string_keys:
        if key in normalized:
            normalized[key] = _required_string(record, key, "record")
    return normalized


def validate_context1(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate recurring, Methodology-relevant domain visual conventions."""

    source = _mapping(value, "context1")
    normalized = copy.deepcopy(dict(source))
    normalized["domain"] = _required_string(source, "domain", "context1")
    conventions = _records(source.get("conventions"), "context1 conventions")
    normalized["conventions"] = []
    required = (
        "concept",
        "recurrence_evidence",
        "visual_treatment",
        "terminology",
        "methodology_relevance",
    )
    for index, convention in enumerate(conventions):
        location = f"context1 conventions[{index}]"
        for key in required:
            _required_string(convention, key, location)
        normalized["conventions"].append(_normalized_record(convention, required))
    normalized["mainline"] = _required_string(source, "mainline", "context1")
    return normalized


def _relationship_endpoint(record: Mapping[str, Any], endpoint: str, location: str) -> str:
    aliases = {
        "source": ("source_id", "from_component_id", "source"),
        "target": ("target_id", "to_component_id", "target"),
    }
    for key in aliases[endpoint]:
        if key in record:
            return _required_string(record, key, location)
    raise ValueError(f"{location} requires {endpoint}_id")


def validate_context2(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the content-to-visual plan and its component relationships."""

    source = _mapping(value, "context2")
    normalized = copy.deepcopy(dict(source))
    normalized["mainline"] = _required_string(source, "mainline", "context2")
    components = _records(source.get("components"), "context2 components")
    component_ids = _unique_ids(components, "context2 components")
    component_fields = (
        "id",
        "label",
        "semantic_role",
        "construction_provenance",
        "visual_treatment",
        "source_context",
    )
    normalized["components"] = []
    for index, component in enumerate(components):
        location = f"context2 components[{index}]"
        for key in component_fields:
            _required_string(component, key, location)
        _required_value(component, "special", location)
        normalized["components"].append(_normalized_record(component, component_fields))

    relationships = source.get("relationships")
    if not isinstance(relationships, list):
        raise ValueError("context2 requires relationships list")
    normalized["relationships"] = copy.deepcopy(relationships)
    known_ids = set(component_ids)
    for index, relationship in enumerate(relationships):
        record = _mapping(relationship, f"context2 relationships[{index}]")
        source_id = _relationship_endpoint(record, "source", f"context2 relationships[{index}]")
        target_id = _relationship_endpoint(record, "target", f"context2 relationships[{index}]")
        if source_id not in known_ids or target_id not in known_ids:
            raise ValueError("context2 relationships must point to known component ids")
    return normalized


def _validate_colour(record: Mapping[str, Any], location: str) -> dict[str, Any]:
    role = _required_string(record, "role", location)
    hex_value = _required_string(record, "hex", location)
    if record.get("hex") != hex_value or not _UPPERCASE_HEX.fullmatch(hex_value):
        raise ValueError(f"{location} requires exact uppercase HEX")
    rgb = record.get("rgb")
    if (
        not isinstance(rgb, list)
        or len(rgb) != 3
        or any(not isinstance(channel, int) or isinstance(channel, bool) or not 0 <= channel <= 255 for channel in rgb)
    ):
        raise ValueError(f"{location} requires rgb with three integer channels")
    expected_rgb = [int(hex_value[index : index + 2], 16) for index in (1, 3, 5)]
    if rgb != expected_rgb:
        raise ValueError(f"{location} requires rgb matching hex")
    normalized = copy.deepcopy(dict(record))
    normalized["role"] = role
    normalized["hex"] = hex_value
    return normalized


def _validate_palette(value: Any) -> dict[str, Any]:
    """Validate Context 3's palette structure without consulting a library."""

    palette = _mapping(value, "context3 palette")
    for field in _FORBIDDEN_PALETTE_FIELDS:
        if field in palette:
            raise ValueError(f"context3 palette must not include {field}")
    normalized = copy.deepcopy(dict(palette))
    normalized["base_palette_id"] = _required_string(
        palette, "base_palette_id", "context3 palette"
    )
    colours = _records(palette.get("colours"), "context3 palette colours")
    normalized["colours"] = []
    active_hexes: set[str] = set()
    for index, colour in enumerate(colours):
        normalized_colour = _validate_colour(
            colour, f"context3 palette colours[{index}]"
        )
        if normalized_colour["hex"] in active_hexes:
            raise ValueError("context3 palette has duplicate hex values")
        active_hexes.add(normalized_colour["hex"])
        normalized["colours"].append(normalized_colour)

    extensions = palette.get("extensions", [])
    if not isinstance(extensions, list):
        raise ValueError("context3 palette extensions must be a list")
    normalized["extensions"] = []
    for index, extension in enumerate(extensions):
        location = f"context3 palette extensions[{index}]"
        record = _mapping(extension, location)
        normalized_extension = _validate_colour(record, location)
        relationship = _required_string(record, "relationship", location)
        if relationship not in PALETTE_RELATIONSHIPS:
            raise ValueError(f"{location} has unsupported relationship")
        evidence_url = _required_string(record, "evidence_url", location)
        parsed_url = urlparse(evidence_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise ValueError(f"{location} requires an HTTPS evidence_url")
        evidence_summary = _required_string(record, "evidence_summary", location)
        if normalized_extension["hex"] in active_hexes:
            raise ValueError("context3 palette has duplicate hex values")
        active_hexes.add(normalized_extension["hex"])
        normalized_extension["relationship"] = relationship
        normalized_extension["evidence_url"] = evidence_url
        normalized_extension["evidence_summary"] = evidence_summary
        normalized["extensions"].append(normalized_extension)
    return normalized


def validate_context3(
    value: Mapping[str, Any], component_ids: Collection[str]
) -> dict[str, Any]:
    """Validate reference crops, complete visual coverage, palette, and taste rules."""

    source = _mapping(value, "context3")
    normalized = copy.deepcopy(dict(source))
    known_component_ids = set(component_ids)
    if not known_component_ids:
        raise ValueError("context3 requires Context 2 component ids")

    selections = _records(source.get("selected_references"), "context3 selected_references")
    crop_ids: list[str] = []
    reference_ids: list[str] = []
    normalized["selected_references"] = []
    crop_fields = ("crop_id", "reference_id", "crop_path", "target_component_id")
    contract_fields = ("borrow", "must_change", "human_editable_reason")
    for index, selection in enumerate(selections):
        location = f"context3 selected_references[{index}]"
        contract = _mapping(selection.get("crop_contract"), f"{location} crop_contract")
        for key in contract_fields:
            _required_string(contract, key, f"{location} crop_contract")
        for key in crop_fields:
            _required_string(selection, key, location)
        target_component_id = _required_string(selection, "target_component_id", location)
        if target_component_id not in known_component_ids:
            raise ValueError(f"{location} target_component_id must name a known component")
        crop_ids.append(_required_string(selection, "crop_id", location))
        reference_ids.append(_required_string(selection, "reference_id", location))
        normalized_selection = _normalized_record(selection, crop_fields)
        normalized_selection["crop_contract"] = _normalized_record(contract, contract_fields)
        normalized["selected_references"].append(normalized_selection)
    if len(crop_ids) != len(set(crop_ids)):
        raise ValueError("context3 selected_references crop_ids must be unique")
    if len(set(reference_ids)) < 2:
        raise ValueError("context3 selected_references requires two distinct reference_id values")

    coverage = _records(source.get("coverage_matrix"), "context3 coverage_matrix")
    covered_components: list[str] = []
    normalized["coverage_matrix"] = copy.deepcopy(coverage)
    known_crop_ids = set(crop_ids)
    for index, record in enumerate(coverage):
        location = f"context3 coverage_matrix[{index}]"
        component_id = _required_string(record, "component_id", location)
        if component_id not in known_component_ids:
            raise ValueError(f"{location} component_id must name a known component")
        covered_components.append(component_id)
        crop_references = record.get("crop_ids")
        geometry_reason = record.get("basic_geometry_justification")
        if crop_references is None and geometry_reason is None:
            raise ValueError(f"{location} requires crop_ids or basic_geometry_justification")
        if crop_references is not None:
            if not isinstance(crop_references, list) or not crop_references:
                raise ValueError(f"{location} crop_ids requires one or more crop ids")
            for crop_id in crop_references:
                if not isinstance(crop_id, str) or not crop_id.strip() or crop_id.strip() not in known_crop_ids:
                    raise ValueError(f"{location} crop_ids must name selected crop ids")
        if geometry_reason is not None:
            _required_string(record, "basic_geometry_justification", location)
    if len(covered_components) != len(set(covered_components)):
        raise ValueError("context3 coverage_matrix component_id values must be unique")
    if set(covered_components) != known_component_ids:
        raise ValueError("context3 coverage_matrix must cover every Context 2 component")

    normalized["palette"] = _validate_palette(source.get("palette"))
    taste_constraints = source.get("taste_constraints")
    if not isinstance(taste_constraints, list) or not taste_constraints:
        raise ValueError("context3 requires a non-empty taste_constraints list")
    normalized["taste_constraints"] = []
    for index, constraint in enumerate(taste_constraints):
        if not isinstance(constraint, str) or not constraint.strip():
            raise ValueError(f"context3 taste_constraints[{index}] must be non-empty")
        normalized["taste_constraints"].append(constraint.strip())
    return normalized


def validate_diagnosis(
    value: Mapping[str, Any], component_ids: Collection[str]
) -> dict[str, Any]:
    """Validate one SVG-diagnostic verdict for every Context 2 component."""

    source = _mapping(value, "diagnosis")
    normalized = copy.deepcopy(dict(source))
    verdict_records = _records(source.get("verdicts"), "diagnosis verdicts")
    recorded_component_ids: list[str] = []
    normalized["verdicts"] = []
    for index, record in enumerate(verdict_records):
        location = f"diagnosis verdicts[{index}]"
        component_id = _required_string(record, "component_id", location)
        verdict = _required_string(record, "verdict", location)
        if verdict not in VERDICTS:
            raise ValueError(f"{location} has unsupported verdict")
        recorded_component_ids.append(component_id)
        normalized["verdicts"].append(
            _normalized_record(record, ("component_id", "verdict"))
        )
    if len(recorded_component_ids) != len(set(recorded_component_ids)) or set(recorded_component_ids) != set(component_ids):
        raise ValueError("diagnosis requires exactly one verdict per Context 2 component")
    return normalized


def validate_run_manifest(value: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Validate canonical run paths and ensure declared files stay under *root*."""

    source = _mapping(value, "run manifest")
    normalized = copy.deepcopy(dict(source))
    artifacts = _mapping(source.get("artifacts"), "run manifest artifacts")
    normalized_artifacts: dict[str, str] = {}
    root_path = Path(root).resolve()
    for key, expected_path in _RUN_ARTIFACTS.items():
        declared_path = _required_string(artifacts, key, "run manifest artifacts")
        path = Path(declared_path)
        if path.is_absolute():
            raise ValueError("run manifest artifact paths must be relative")
        if not (root_path / path).resolve().is_relative_to(root_path):
            raise ValueError("run manifest artifact paths must stay under root")
        if declared_path != expected_path:
            raise ValueError(f"run manifest artifacts {key} must be {expected_path}")
        normalized_artifacts[key] = declared_path
    for key, declared_path in artifacts.items():
        if not isinstance(key, str):
            raise ValueError("run manifest artifact names must be strings")
        normalized_path = _required_string(artifacts, key, "run manifest artifacts")
        path = Path(normalized_path)
        if path.is_absolute():
            raise ValueError("run manifest artifact paths must be relative")
        candidate = (root_path / path).resolve()
        if not candidate.is_relative_to(root_path):
            raise ValueError("run manifest artifact paths must stay under root")
        if not candidate.is_file():
            raise ValueError(f"run manifest artifact does not exist: {normalized_path}")
        normalized_artifacts[key] = normalized_path
    normalized["artifacts"] = normalized_artifacts
    return normalized


def load_json_object(path: str | Path) -> dict[str, Any]:
    """Load a UTF-8 JSON object from *path*."""

    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON artifact must be an object")
    return value
