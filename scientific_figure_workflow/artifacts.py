"""Validation helpers for model-produced two-pass workflow artifacts."""

from __future__ import annotations

import copy
import json
from collections.abc import Collection, Mapping
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

from .palette import validate_palette


VERDICTS = {"keep", "accept_variation", "patch", "reject", "replace"}
_UNRESOLVED_SVG_DEFECT_MARKERS = (
    "gradient",
    "missing badge",
    "badge is missing",
    "missing seal",
    "missing medal",
    "missing icon",
    "not replicated",
    "not reproduced",
    "absent",
    "occluded",
    "materially distorted",
)
WEB_MANIFEST_FORMAT = "scholarly-domain-figure-manifest-v1"
_WEB_CROP_ROOT = PurePosixPath("references/web/crops")
_WEB_REPLACEMENT_ROOT = PurePosixPath("references/web/crops/replacements")
CREATIVE_DIRECTOR_FORMAT = "creative-director-brief-v1"
_CREATIVE_DIRECTOR_CROP_ROOT = PurePosixPath("references/web/crops/creative-director")

_RUN_ARTIFACTS = {
    "methodology": "input/methodology.md",
    "context1": "context/context-1-domain-conventions.json",
    "context2": "context/context-2-content-visual-plan.json",
    "context3": "context/context-3-visual-kit.json",
    "web_manifest": "references/web/manifest.json",
    "figurebench_candidates": "references/figurebench/candidates.json",
    "figurebench_crop_request": "references/figurebench/crops/request.json",
    "figurebench_crops": "references/figurebench/crops/manifest.json",
    "prompt1": "prompt-1/prompt.md",
    "prompt1_attachments": "prompt-1/attachments.json",
    "png1": "png1.png",
    "svg1": "svg-diagnostic/svg1.svg",
    "png1_5": "svg-diagnostic/png1.5.png",
    "diagnosis": "svg-diagnostic/diagnosis.json",
    "approved_crop_request": "svg-diagnostic/approved-crops/request.json",
    "approved_crops": "svg-diagnostic/approved-crops/manifest.json",
    "prompt2": "prompt-2/prompt.md",
    "prompt2_attachments": "prompt-2/attachments.json",
    "png2": "png2-final.png",
}


def run_artifact_paths() -> dict[str, str]:
    """Return a copy of the exact canonical complete-run artifact mapping."""

    return dict(_RUN_ARTIFACTS)


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


def _required_string_list(record: Mapping[str, Any], key: str, location: str) -> list[str]:
    value = record.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location} requires non-empty {key} list")
    strings = [_required_string({key: item}, key, location) for item in value]
    if len(strings) != len(set(strings)):
        raise ValueError(f"{location} {key} values must be unique")
    return strings


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


def _https_url(record: Mapping[str, Any], key: str, location: str) -> str:
    value = _required_string(record, key, location)
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{location} requires HTTPS {key}")
    return value


def _safe_web_crop(value: Any, root: Path, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires non-empty crop_path")
    raw = value.strip()
    if "\\" in raw:
        raise ValueError(f"{location} crop_path must be a safe run-relative path")
    relative = PurePosixPath(raw)
    if (
        relative.is_absolute()
        or any(part in {"", ".", ".."} for part in raw.split("/"))
        or not relative.is_relative_to(_WEB_CROP_ROOT)
        or relative.is_relative_to(_WEB_REPLACEMENT_ROOT)
    ):
        raise ValueError(
            f"{location} crop_path must be under references/web/crops and outside replacements"
        )
    declared = root.joinpath(*relative.parts)
    if not declared.is_file():
        raise ValueError(f"{location} crop_path requires an existing file")
    resolved_root = root.resolve(strict=True)
    resolved = declared.resolve(strict=True)
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"{location} crop_path must stay under the run root")
    current = resolved_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{location} crop_path must not use a symlink alias")
    return relative.as_posix()


def _context1_mapped_crop_paths(context1: Mapping[str, Any]) -> set[str]:
    normalized = validate_context1(context1)
    paths: set[str] = set()
    for convention_index, convention in enumerate(normalized["conventions"]):
        for field in ("eligible_source_crops", "source_crops"):
            records = convention.get(field, [])
            if records is None:
                continue
            if not isinstance(records, list):
                raise ValueError(
                    f"context1 conventions[{convention_index}] {field} must be a list"
                )
            for crop_index, record in enumerate(records):
                if not isinstance(record, Mapping):
                    raise ValueError(
                        f"context1 conventions[{convention_index}] {field}[{crop_index}] must be an object"
                    )
                path = record.get("path", record.get("crop_path"))
                if not isinstance(path, str) or not path.strip():
                    raise ValueError(
                        f"context1 conventions[{convention_index}] {field}[{crop_index}] requires crop path"
                    )
                paths.add(PurePosixPath(path.strip()).as_posix())
    return paths


def validate_web_manifest(
    value: Mapping[str, Any], root: Path, context1: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate 3–4 scholarly paper sources and their retained visual evidence."""

    source = _mapping(value, "web manifest")
    if source.get("format") != WEB_MANIFEST_FORMAT:
        raise ValueError(f"web manifest format must be {WEB_MANIFEST_FORMAT}")
    records = source.get("sources")
    if not isinstance(records, list):
        raise ValueError("web manifest requires sources list")

    normalized: list[dict[str, Any]] = []
    ids: list[str] = []
    paper_urls: list[str] = []
    crop_paths: list[str] = []
    for index, item in enumerate(records):
        location = f"web manifest sources[{index}]"
        record = _mapping(item, location)
        source_id = _required_string(record, "id", location)
        ids.append(source_id)
        paper_url = _https_url(record, "source_url", location)
        paper_urls.append(paper_url)
        crop_path = _safe_web_crop(record.get("crop_path"), Path(root), location)
        crop_paths.append(crop_path)
        normalized.append(
            {
                "id": source_id,
                "title": _required_string(record, "title", location),
                "figure": _required_string(record, "figure", location),
                "source_url": paper_url,
                "evidence_url": _https_url(record, "evidence_url", location),
                "crop_path": crop_path,
                "inspection": _required_string(record, "inspection", location),
            }
        )
    if not 3 <= len(set(paper_urls)) <= 4:
        raise ValueError("web manifest requires 3 or 4 distinct scholarly papers")
    if len(ids) != len(set(ids)):
        raise ValueError("web manifest source ids must be unique")
    if len(crop_paths) != len(set(crop_paths)):
        raise ValueError("web manifest crop paths must be unique")

    mapped = _context1_mapped_crop_paths(context1)
    missing = sorted(mapped - set(crop_paths))
    if missing:
        raise ValueError(
            "web manifest must cover all Context 1 mapped domain crops: " + ", ".join(missing)
        )
    return {"format": WEB_MANIFEST_FORMAT, "sources": normalized}


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


def _validate_palette(value: Any) -> dict[str, Any]:
    """Validate Context 3's palette with the bundled approved library."""

    library_path = Path(__file__).resolve().parents[1] / "references" / "palette-library.json"
    library = json.loads(library_path.read_text(encoding="utf-8"))
    palettes = library.get("palettes") if isinstance(library, Mapping) else None
    if not isinstance(palettes, list):
        raise ValueError("bundled palette library requires palettes list")
    return validate_palette(value, palettes)


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
    for index, selection in enumerate(selections):
        location = f"context3 selected_references[{index}]"
        contract = _mapping(selection.get("crop_contract"), f"{location} crop_contract")
        for key in crop_fields:
            _required_string(selection, key, location)
        target_component_id = _required_string(selection, "target_component_id", location)
        if target_component_id not in known_component_ids:
            raise ValueError(f"{location} target_component_id must name a known component")
        crop_ids.append(_required_string(selection, "crop_id", location))
        reference_ids.append(_required_string(selection, "reference_id", location))
        normalized_selection = _normalized_record(selection, crop_fields)
        normalized_selection["crop_contract"] = {
            "borrow": _required_string_list(contract, "borrow", f"{location} crop_contract"),
            "must_change": _required_string_list(contract, "must_change", f"{location} crop_contract"),
            "human_editable_reason": _required_string(
                contract, "human_editable_reason", f"{location} crop_contract"
            ),
        }
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


def validate_creative_director(
    value: Mapping[str, Any], root: Path, component_ids: Collection[str]
) -> dict[str, Any]:
    """Validate the pre-PNG1 creative brief and paper-SVG crop provenance."""

    source = _mapping(value, "creative director brief")
    if source.get("format") != CREATIVE_DIRECTOR_FORMAT:
        raise ValueError(f"creative director brief format must be {CREATIVE_DIRECTOR_FORMAT}")
    normalized = copy.deepcopy(dict(source))
    normalized["brief"] = _required_string(source, "brief", "creative director brief")
    ideas = _records(source.get("ideas"), "creative director ideas")
    known_components = set(component_ids)
    if not known_components:
        raise ValueError("creative director brief requires Context 2 component ids")
    idea_ids: list[str] = []
    crop_paths: set[str] = set()
    normalized["ideas"] = []
    required_idea_fields = ("id", "target_component_id", "concept", "visual_intent", "construction_plan")
    for index, idea in enumerate(ideas):
        location = f"creative director ideas[{index}]"
        for field in required_idea_fields:
            _required_string(idea, field, location)
        idea_id = _required_string(idea, "id", location)
        target = _required_string(idea, "target_component_id", location)
        if target not in known_components:
            raise ValueError(f"{location} target_component_id must name a Context 2 component")
        requires_svg = idea.get("requires_svg_evidence")
        if not isinstance(requires_svg, bool):
            raise ValueError(f"{location} requires boolean requires_svg_evidence")
        raw_crops = idea.get("svg_crops", [])
        if not isinstance(raw_crops, list) or not all(isinstance(crop, Mapping) for crop in raw_crops):
            raise ValueError(f"{location} svg_crops must be a list of objects")
        if requires_svg and not raw_crops:
            raise ValueError(f"{location} requires at least one paper SVG crop")
        normalized_idea = copy.deepcopy(dict(idea))
        normalized_idea["svg_crops"] = []
        for crop_index, crop in enumerate(raw_crops):
            crop_location = f"{location} svg_crops[{crop_index}]"
            crop_target = _required_string(crop, "target_component_id", crop_location)
            if crop_target != target:
                raise ValueError(
                    f"{crop_location} target_component_id must match its idea target_component_id"
                )
            path = _required_string(crop, "path", crop_location)
            relative = PurePosixPath(path)
            if not relative.is_relative_to(_CREATIVE_DIRECTOR_CROP_ROOT):
                raise ValueError(
                    f"{crop_location} path must be under {_CREATIVE_DIRECTOR_CROP_ROOT.as_posix()}"
                )
            safe_path = _safe_web_crop(path, root, crop_location)
            if safe_path in crop_paths:
                raise ValueError("creative director SVG crop paths must be unique")
            crop_paths.add(safe_path)
            if _required_string(crop, "source_format", crop_location).casefold() != "svg":
                raise ValueError(f"{crop_location} source_format must be svg")
            normalized_crop = copy.deepcopy(dict(crop))
            normalized_crop.update(
                path=safe_path,
                target_component_id=crop_target,
                source_url=_https_url(crop, "source_url", crop_location),
                evidence_url=_https_url(crop, "evidence_url", crop_location),
                source_format="svg",
                borrow=_required_string_list(crop, "borrow", crop_location),
                must_change=_required_string_list(crop, "must_change", crop_location),
                human_editable_reason=_required_string(crop, "human_editable_reason", crop_location),
            )
            normalized_idea["svg_crops"].append(normalized_crop)
        idea_ids.append(idea_id)
        normalized["ideas"].append(normalized_idea)
    if len(idea_ids) != len(set(idea_ids)):
        raise ValueError("creative director idea ids must be unique")
    if not crop_paths:
        normalized["svg_evidence_status"] = "no_external_svg_needed"
    else:
        normalized["svg_evidence_status"] = "paper_svg_crops_verified"
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
        reason = _required_string(record, "reason", location)
        if verdict in {"keep", "accept_variation"}:
            lowered_reason = reason.casefold()
            if any(marker in lowered_reason for marker in _UNRESOLVED_SVG_DEFECT_MARKERS):
                raise ValueError(
                    f"{location} cannot mark an unresolved SVG defect as {verdict}; use patch, reject, or replace"
                )
        recorded_component_ids.append(component_id)
        normalized_record = _normalized_record(record, ("component_id", "verdict", "reason"))
        normalized["verdicts"].append(normalized_record)
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
    unexpected = set(artifacts) - set(_RUN_ARTIFACTS)
    if unexpected:
        raise ValueError(
            f"run manifest artifacts must not include {sorted(unexpected)[0]}"
        )
    normalized["artifacts"] = normalized_artifacts
    return normalized


def load_json_object(path: str | Path) -> dict[str, Any]:
    """Load a UTF-8 JSON object from *path*."""

    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON artifact must be an object")
    return value
