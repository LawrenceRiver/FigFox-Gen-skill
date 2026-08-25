"""Deterministic compilers for the two model-facing scientific-figure prompts."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .artifacts import validate_context1, validate_context2, validate_context3, validate_diagnosis


_FORMAT = "scientific-figure-prompt-bundle-v1"
_PNG15_BASENAME = "png1.5.png"
_DIAGNOSTIC_RENDER_ROLE = "svg_diagnostic_render"
_VERDICT_BLOCKS = (
    ("keep", "Preserve"),
    ("accept_variation", "Accept variation"),
    ("patch", "Patch"),
    ("reject", "Reject"),
    ("replace", "Replace"),
)


def _string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires a non-empty string")
    return value.strip()


def _string_list(value: Any, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location} requires a non-empty list")
    return [_string(item, location) for item in value]


def _normalised_path(value: Any, location: str) -> str:
    """Return a relative, slash-normalised artifact path without traversal."""

    raw = _string(value, location).replace("\\", "/")
    decoded = raw
    # Decode repeatedly so percent-encoded spellings cannot evade attachment rules.
    while True:
        next_value = unquote(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    candidate = Path(decoded)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"{location} must be a relative artifact path")
    if len(candidate.parts) == 1 and ":" in candidate.parts[0]:
        raise ValueError(f"{location} must be a relative artifact path")
    return decoded.replace("\\", "/")


def _reject_prompt2_excluded_attachment(path: str, role: Any = None) -> None:
    basename = Path(path.replace("\\", "/")).name.casefold()
    if basename == _PNG15_BASENAME:
        raise ValueError("Prompt 2 must never attach PNG1.5")
    if isinstance(role, str) and role.strip().casefold() == _DIAGNOSTIC_RENDER_ROLE:
        raise ValueError("Prompt 2 must never attach svg_diagnostic_render")


def _attachment(path: Any, role: str, *, location: str, **details: Any) -> dict[str, Any]:
    normalized_path = _normalised_path(path, f"{location} path")
    return {"path": normalized_path, "role": role, **details}


def _validated_contexts(
    context1: Mapping[str, Any], context2: Mapping[str, Any], context3: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    normalized1 = validate_context1(context1)
    normalized2 = validate_context2(context2)
    component_ids = {component["id"] for component in normalized2["components"]}
    normalized3 = validate_context3(context3, component_ids)
    return normalized1, normalized2, normalized3


def _relationship_endpoint(record: Mapping[str, Any], names: tuple[str, ...], location: str) -> str:
    for name in names:
        if name in record:
            return _string(record[name], location)
    raise ValueError(f"{location} requires relationship endpoint")


def _domain_crops(context1: Mapping[str, Any], component_ids: set[str]) -> list[dict[str, Any]]:
    """Extract only explicitly mapped source crops from Context 1 convention evidence."""

    crops: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for convention_index, convention in enumerate(context1["conventions"]):
        for field in ("eligible_source_crops", "source_crops"):
            records = convention.get(field, [])
            if records is None:
                continue
            if not isinstance(records, list):
                raise ValueError(f"context1 conventions[{convention_index}] {field} must be a list")
            for crop_index, record in enumerate(records):
                location = f"context1 conventions[{convention_index}] {field}[{crop_index}]"
                if not isinstance(record, Mapping):
                    raise ValueError(f"{location} must be an object")
                target = _string(record.get("target_component_id"), location)
                if target not in component_ids:
                    raise ValueError(f"{location} target_component_id must name a Context 2 component")
                contract = record.get("crop_contract", record)
                if not isinstance(contract, Mapping):
                    raise ValueError(f"{location} crop_contract must be an object")
                borrow = _string_list(contract.get("borrow"), f"{location} borrow")
                must_change = _string_list(contract.get("must_change"), f"{location} must_change")
                attachment = _attachment(
                    record.get("path", record.get("crop_path")),
                    "domain_paper_component",
                    location=location,
                    target_component_id=target,
                    borrow=borrow,
                    must_change=must_change,
                    concept=convention["concept"],
                )
                if attachment["path"] in seen_paths:
                    raise ValueError("Context 1 domain-paper crop paths must be unique")
                seen_paths.add(attachment["path"])
                crops.append(attachment)
    return crops


def _figurebench_attachments(context3: Mapping[str, Any]) -> list[dict[str, Any]]:
    attachments = []
    for index, selection in enumerate(context3["selected_references"]):
        crop_path = _normalised_path(
            selection["crop_path"], f"context3 selected_references[{index}] crop_path"
        )
        if (
            Path(crop_path).name.casefold() == f"{selection['reference_id']}.png".casefold()
            or "figurebench-references" in {part.casefold() for part in Path(crop_path).parts}
        ):
            raise ValueError("Prompt 1 must not attach a complete FigureBench reference; attach a mapped crop")
        contract = selection["crop_contract"]
        attachments.append(
            _attachment(
                crop_path,
                "figurebench_component",
                location=f"context3 selected_references[{index}]",
                crop_id=selection["crop_id"],
                reference_id=selection["reference_id"],
                target_component_id=selection["target_component_id"],
                borrow=contract["borrow"],
                must_change=contract["must_change"],
                human_editable_reason=contract["human_editable_reason"],
            )
        )
    return attachments


def _component_lines(context2: Mapping[str, Any]) -> list[str]:
    return [
        "- {id}: label `{label}`; role `{semantic_role}`; treatment `{visual_treatment}`; "
        "provenance `{construction_provenance}`; special `{special}`.".format(**component)
        for component in context2["components"]
    ]


def _relationship_lines(context2: Mapping[str, Any]) -> list[str]:
    lines = []
    for index, relationship in enumerate(context2["relationships"]):
        if not isinstance(relationship, Mapping):
            raise ValueError(f"context2 relationships[{index}] must be an object")
        source = _relationship_endpoint(relationship, ("source_id", "from_component_id", "source"), f"context2 relationships[{index}]")
        target = _relationship_endpoint(relationship, ("target_id", "to_component_id", "target"), f"context2 relationships[{index}]")
        label = relationship.get("label", relationship.get("relationship", "flows to"))
        lines.append(f"- {source} -> {target}: {_string(label, f'context2 relationships[{index}] label')}.")
    return lines or ["- Read the listed components as the scientific mainline."]


def _palette_lines(context3: Mapping[str, Any]) -> list[str]:
    palette = context3["palette"]
    lines = [f"Use only base palette group `{palette['base_palette_id']}` and its evidenced extensions."]
    lines.extend(f"- {colour['role']}: {colour['hex']} ({colour['rgb']})" for colour in palette["colours"])
    for colour in palette["extensions"]:
        lines.append(
            f"- extension {colour['role']}: {colour['hex']} ({colour['relationship']}; {colour['evidence_url']})"
        )
    lines.append("Do not sample, infer, or add colours from the user reference, FigureBench, or another palette group.")
    return lines


def _coverage_lines(context3: Mapping[str, Any]) -> list[str]:
    lines = []
    for record in context3["coverage_matrix"]:
        if "crop_ids" in record:
            lines.append(f"- {record['component_id']}: mapped crop ids {', '.join(record['crop_ids'])}.")
        else:
            lines.append(f"- {record['component_id']}: basic geometry only — {record['basic_geometry_justification']}")
    return lines


def _convention_lines(context1: Mapping[str, Any]) -> list[str]:
    return [
        f"- `{record['concept']}`: treatment `{record['visual_treatment']}`; terminology `{record['terminology']}`."
        for record in context1["conventions"]
    ]


def build_prompt1_bundle(
    methodology: str,
    context1: Mapping[str, Any],
    context2: Mapping[str, Any],
    context3: Mapping[str, Any],
    user_reference: str | None,
    root: Path,
) -> dict[str, Any]:
    """Compile the complete first-pass prompt and its mapped reference attachments."""

    _string(methodology, "methodology")
    _ = Path(root)  # The caller owns the run root; attachment paths remain run-relative.
    normalized1, normalized2, normalized3 = _validated_contexts(context1, context2, context3)
    component_ids = {component["id"] for component in normalized2["components"]}
    figurebench = _figurebench_attachments(normalized3)
    domain_crops = _domain_crops(normalized1, component_ids)
    attachments: list[dict[str, Any]] = []
    if user_reference is not None:
        attachments.append(_attachment(user_reference, "user_reference", location="user_reference"))
    attachments.extend(domain_crops)
    attachments.extend(figurebench)

    coverage_lines = _coverage_lines(normalized3)
    crop_lines = []
    for attachment in [*domain_crops, *figurebench]:
        crop_lines.append(
            f"- `{attachment['path']}` -> Target: {attachment['target_component_id']}. "
            f"Borrow: {'; '.join(attachment['borrow'])}. "
            f"Must change: {'; '.join(attachment['must_change'])}."
        )
    if not crop_lines:
        crop_lines.append("- No crop attachment is permitted unless it is explicitly mapped to a target component.")

    prompt = "\n".join(
        [
            "Create one publication-quality scientific architecture figure. The supplied Methodology is authoritative for scope, but compress it into the structured scientific plan below; do not turn search explanations into figure prose.",
            "",
            "## 1. Figure purpose and scientific mainline",
            f"Purpose: communicate the `{normalized1['domain']}` method as `{normalized2['mainline']}`.",
            "",
            "## 2. Exact block and structure names",
            *_component_lines(normalized2),
            "",
            "## 3. Semantic relationships and reading order",
            *_relationship_lines(normalized2),
            "Read in the stated relationship order; preserve directionality and scientific logic.",
            "",
            "## 4. Content-to-visual mapping for every element",
            *_component_lines(normalized2),
            "Use Context 1 only as contextual convention evidence: do not copy recurrence/search explanations into the figure.",
            "",
            "## 5. Crop-to-component mapping",
            *crop_lines,
            "Coverage matrix (complete):",
            *coverage_lines,
            "",
            "## 6. Single-palette contract",
            *_palette_lines(normalized3),
            "",
            "## 7. Layout and taste constraints",
            *(f"- {constraint}" for constraint in normalized3["taste_constraints"]),
            "Keep hierarchy, spacing, rhythm, restraint, and a human-edited finish subordinate to scientific meaning.",
            "",
            "## 8. Exact labels and text-density limits",
            "Use only the exact block/structure labels above plus necessary relationship labels. Keep text sparse; do not add explanatory paragraphs, search findings, or planning captions.",
            "",
            "## 9. Anti-AI visual constraints",
            "Do not add decoration without a named scientific role. Do not use decorative visuals unrelated to text, unexplained dots, floating symbols, or purposeless boxes.",
            "Do not use arbitrary high-contrast colours between adjacent modules, shapes with no human construction provenance, numbered 1/2/3/4 planning labels, the generic blue-title-strip-inside-every-box pattern, repeated card grids that make the figure look like a slide deck, or fake cartoon objects when a real crop or editable scientific geometry is expected.",
            "",
            "## 10. Direct PNG generation instruction",
            "Generate PNG1 directly from this complete bundle. Use every attachment only for its declared target and contract. This workflow has exactly two image-generation passes; this is the first. Produce one coherent scientific figure, not a slide deck or an illustration collage.",
        ]
    )
    return {"format": _FORMAT, "phase": "prompt1", "prompt": prompt, "attachments": attachments}


def _crop_records(value: Mapping[str, Any], location: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{location} requires an object")
    records = value.get("crops", [])
    if not isinstance(records, list):
        raise ValueError(f"{location} crops must be a list")
    if not all(isinstance(record, Mapping) for record in records):
        raise ValueError(f"{location} crops must contain objects")
    return records


def _prompt2_crops(
    value: Mapping[str, Any], role: str, location: str, component_ids: set[str], verdicts: Mapping[str, Mapping[str, Any]]
) -> list[dict[str, Any]]:
    attachments = []
    for index, record in enumerate(_crop_records(value, location)):
        crop_location = f"{location} crops[{index}]"
        target = _string(record.get("target_component_id"), crop_location)
        if target not in component_ids:
            raise ValueError(f"{crop_location} target_component_id must name a Context 2 component")
        path = _normalised_path(record.get("path", record.get("crop_path")), f"{crop_location} path")
        _reject_prompt2_excluded_attachment(path, record.get("role"))
        if role == "approved_svg_crop" and verdicts[target]["verdict"] in {"reject", "replace"}:
            raise ValueError(f"{crop_location} cannot approve a rejected or replacement component")
        if role == "replacement_crop" and verdicts[target]["verdict"] not in {"reject", "replace"}:
            raise ValueError(f"{crop_location} requires a reject or replace diagnosis")
        details = {"target_component_id": target}
        if "diagnosis" in record:
            details["diagnosis"] = _string(record["diagnosis"], f"{crop_location} diagnosis")
        if "reason" in record:
            details["reason"] = _string(record["reason"], f"{crop_location} reason")
        attachments.append(_attachment(path, role, location=crop_location, **details))
    return attachments


def build_prompt2_bundle(
    methodology: str,
    context1: Mapping[str, Any],
    context2: Mapping[str, Any],
    context3: Mapping[str, Any],
    png1: str,
    diagnosis: Mapping[str, Any],
    svg_crops: Mapping[str, Any],
    replacement_crops: Mapping[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Compile the final PNG revision prompt while structurally excluding PNG1.5."""

    _string(methodology, "methodology")
    _ = Path(root)
    normalized1, normalized2, normalized3 = _validated_contexts(context1, context2, context3)
    component_ids = {component["id"] for component in normalized2["components"]}
    normalized_diagnosis = validate_diagnosis(diagnosis, component_ids)
    verdicts = {record["component_id"]: record for record in normalized_diagnosis["verdicts"]}
    png1_path = _normalised_path(png1, "png1")
    _reject_prompt2_excluded_attachment(png1_path)
    attachments = [_attachment(png1_path, "png1_visual_truth", location="png1")]
    attachments.extend(_prompt2_crops(svg_crops, "approved_svg_crop", "svg_crops", component_ids, verdicts))
    attachments.extend(_prompt2_crops(replacement_crops, "replacement_crop", "replacement_crops", component_ids, verdicts))

    block_lines: dict[str, list[str]] = {verdict: [] for verdict, _ in _VERDICT_BLOCKS}
    for component in normalized2["components"]:
        verdict_record = verdicts[component["id"]]
        detail = verdict_record.get("reason", "No additional diagnostic explanation supplied")
        if not isinstance(detail, str) or not detail.strip():
            raise ValueError(f"diagnosis verdict for {component['id']} requires a non-empty reason when supplied")
        block_lines[verdict_record["verdict"]].append(
            f"- `{component['id']}` / `{component['label']}`: {detail.strip()}"
        )
    verdict_sections = []
    for verdict, heading in _VERDICT_BLOCKS:
        verdict_sections.extend([f"## {heading}", *(block_lines[verdict] or ["- No components have this verdict."]), ""])

    prompt = "\n".join(
        [
            "Revise PNG1 into the final PNG2. PNG1 is the image to modify and remains the only raster visual truth; use approved SVG and replacement crops only as targeted evidence.",
            f"Scientific scope: `{normalized1['domain']}` — `{normalized2['mainline']}`.",
            "Context 1 convention anchors (context only; do not turn evidence explanations into figure prose):",
            *_convention_lines(normalized1),
            "Context 2 exact planned structures:",
            *_component_lines(normalized2),
            "Context 2 semantic relationships:",
            *_relationship_lines(normalized2),
            "Context 3 complete coverage:",
            *_coverage_lines(normalized3),
            "Context 3 one-base-palette lineage:",
            *_palette_lines(normalized3),
            *verdict_sections,
            "Use approved SVG crops only for their declared component and diagnosis. Use replacement crops only for explicitly rejected or replacement components.",
            "Do not attach, inspect as an image-generation reference, or derive a design from PNG1.5 / any SVG diagnostic render. This is the second and final image-generation pass. No PNG2-to-SVG loop.",
        ]
    )
    return {"format": _FORMAT, "phase": "prompt2", "prompt": prompt, "attachments": attachments}


def write_bundle(bundle: Mapping[str, Any], output_dir: Path) -> None:
    """Write the stable prompt and attachment manifest consumed by the image pass."""

    if not isinstance(bundle, Mapping):
        raise ValueError("bundle must be an object")
    if bundle.get("format") != _FORMAT:
        raise ValueError("bundle has unsupported format")
    if bundle.get("phase") not in {"prompt1", "prompt2"}:
        raise ValueError("bundle has unsupported phase")
    prompt = _string(bundle.get("prompt"), "bundle prompt")
    attachments = bundle.get("attachments")
    if not isinstance(attachments, list) or not all(isinstance(item, Mapping) for item in attachments):
        raise ValueError("bundle attachments must be a list of objects")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "prompt.md").write_text(prompt, encoding="utf-8")
    (destination / "attachments.json").write_text(
        json.dumps(attachments, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
