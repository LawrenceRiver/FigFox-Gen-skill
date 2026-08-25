"""Deterministic, provenance-safe compilers for two scientific-figure prompts."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import unquote

from .artifacts import validate_context1, validate_context2, validate_context3, validate_diagnosis


_FORMAT = "scientific-figure-prompt-bundle-v1"
_PNG15_BASENAME = "png1.5.png"
_DIAGNOSTIC_RENDER_ROLE = "svg_diagnostic_render"
_FIGUREBENCH_CROP_ROOT = PurePosixPath("references/figurebench/crops")
_DOMAIN_CROP_ROOT = PurePosixPath("references/web/crops")
_REPLACEMENT_CROP_ROOT = PurePosixPath("references/web/crops/replacements")
_USER_REFERENCE_ROOT = PurePosixPath("input")
_APPROVED_SVG_CROP_ROOT = PurePosixPath("svg-diagnostic/approved-crops")
_USER_REFERENCE_CONTRACT = (
    "Use as strong guidance for structure, emphasis, layout, and visibly human-made "
    "basic visualization. Ignore generated-looking, fake, or decorative parts. Never "
    "source palette colours from the user reference."
)
_VERDICT_BLOCKS = (("keep", "Preserve"), ("accept_variation", "Accept variation"), ("patch", "Patch"), ("reject", "Reject"), ("replace", "Replace"))


def _string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires a non-empty string")
    return value.strip()


def _string_list(value: Any, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location} requires a non-empty list")
    return [_string(item, location) for item in value]


def _run_root(root: Path) -> Path:
    candidate = Path(root)
    if not candidate.is_dir():
        raise ValueError("run root must be an existing directory")
    return candidate.resolve(strict=True)


def _decoded_relative(value: Any, location: str) -> PurePosixPath:
    decoded = _string(value, location)
    for _ in range(32):
        next_value = unquote(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    else:
        raise ValueError(f"{location} has excessive percent encoding")
    normalized = decoded.replace("\\", "/")
    windows = PureWindowsPath(normalized)
    if windows.drive or windows.root or normalized.startswith("//"):
        raise ValueError(f"{location} must not be a Windows drive or UNC path")
    if normalized.startswith("/"):
        raise ValueError(f"{location} must be relative")
    if any(part in {"", ".", ".."} for part in normalized.split("/")):
        raise ValueError(f"{location} must not contain traversal or empty path segments")
    return PurePosixPath(normalized)


def _is_under(path: PurePosixPath, root: PurePosixPath) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _reject_prompt2_exclusion(path: Path | PurePosixPath, role: Any = None) -> None:
    if path.name.casefold() == _PNG15_BASENAME:
        raise ValueError("Prompt 2 must never attach PNG1.5")
    if isinstance(role, str) and role.strip().casefold() == _DIAGNOSTIC_RENDER_ROLE:
        raise ValueError("Prompt 2 must never attach svg_diagnostic_render")


def _has_symlink_alias(root: Path, declared: Path) -> bool:
    current = root
    for part in declared.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _resolve_attachment(value: Any, *, root: Path, expected_root: PurePosixPath | None, location: str, role: Any = None, prompt2: bool = False, exact_path: PurePosixPath | None = None) -> str:
    """Resolve a declared run-relative file and enforce its canonical provenance."""

    relative = _decoded_relative(value, location)
    if prompt2:
        _reject_prompt2_exclusion(relative, role)
    if exact_path is not None and relative != exact_path:
        raise ValueError(f"{location} must be {exact_path.as_posix()}")
    if expected_root is not None and not _is_under(relative, expected_root):
        names = {
            _FIGUREBENCH_CROP_ROOT: "FigureBench crop root",
            _DOMAIN_CROP_ROOT: "domain-paper crop root",
            _REPLACEMENT_CROP_ROOT: "replacement crop root",
            _USER_REFERENCE_ROOT: "run input area",
            _APPROVED_SVG_CROP_ROOT: "approved SVG crop root",
        }
        raise ValueError(f"{location} must be under the {names[expected_root]}")
    declared = root.joinpath(*relative.parts)
    if not declared.is_file():
        raise ValueError(f"{location} requires an existing file")
    resolved = declared.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError(f"{location} resolves outside the run root")
    if prompt2:
        _reject_prompt2_exclusion(resolved, role)
    if _has_symlink_alias(root, declared):
        raise ValueError(f"{location} must not use a symlink alias")
    if expected_root is not None:
        expected_absolute = root.joinpath(*expected_root.parts).resolve(strict=False)
        if not resolved.is_relative_to(expected_absolute):
            raise ValueError(f"{location} resolves outside its canonical provenance root")
    return relative.as_posix()


def _attachment(path: str, role: str, **details: Any) -> dict[str, Any]:
    return {"path": path, "role": role, **details}


def _validated_contexts(context1: Mapping[str, Any], context2: Mapping[str, Any], context3: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    normalized1 = validate_context1(context1)
    normalized2 = validate_context2(context2)
    normalized3 = validate_context3(context3, {component["id"] for component in normalized2["components"]})
    return normalized1, normalized2, normalized3


def _json_evidence(title: str, value: Any) -> list[str]:
    return [f"BEGIN {title}", json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False), f"END {title}"]


def _evidence_blocks(methodology: str, context1: Mapping[str, Any], context2: Mapping[str, Any], context3: Mapping[str, Any]) -> list[str]:
    return [
        "Use the following evidence for scientific meaning and explicit user requirements. Never copy explanatory prose into the figure; only concise block/structure names, labels, terms, and relationships belong in-image.",
        *_json_evidence("METHODOLOGY SOURCE OF TRUTH", methodology),
        *_json_evidence("NORMALIZED CONTEXT 1 JSON", context1),
        *_json_evidence("NORMALIZED CONTEXT 2 JSON", context2),
        *_json_evidence("NORMALIZED CONTEXT 3 JSON", context3),
    ]


def _relationship_lines(context2: Mapping[str, Any]) -> list[str]:
    lines = []
    for index, relationship in enumerate(context2["relationships"]):
        if not isinstance(relationship, Mapping):
            raise ValueError(f"context2 relationships[{index}] must be an object")
        source = _relationship_endpoint(relationship, ("source_id", "from_component_id", "source"), f"context2 relationships[{index}] source")
        target = _relationship_endpoint(relationship, ("target_id", "to_component_id", "target"), f"context2 relationships[{index}] target")
        label = _string(relationship.get("label", relationship.get("relationship", "flows to")), f"context2 relationships[{index}] label")
        lines.append(f"- {source} -> {target}: {label}.")
    return lines or ["- Read the listed components as the scientific mainline."]


def _relationship_endpoint(record: Mapping[str, Any], aliases: tuple[str, ...], location: str) -> str:
    for alias in aliases:
        if alias in record:
            return _string(record[alias], location)
    raise ValueError(f"{location} requires an endpoint")


def _component_lines(context2: Mapping[str, Any]) -> list[str]:
    return [
        "- {id}: label `{label}`; role `{semantic_role}`; treatment `{visual_treatment}`; provenance `{construction_provenance}`; special `{special}`.".format(**component)
        for component in context2["components"]
    ]


def _palette_lines(context3: Mapping[str, Any]) -> list[str]:
    palette = context3["palette"]
    lines = [
        f"Use only base palette group `{palette['base_palette_id']}` and its evidenced extensions.",
        "Base palette colours:",
        *(f"- {colour['role']}: {colour['hex']} ({colour['rgb']})" for colour in palette["colours"]),
        "Evidenced related-colour extensions:",
    ]
    if palette["extensions"]:
        lines.extend(
            f"- {colour['role']}: {colour['hex']} ({colour['rgb']}); relationship "
            f"`{colour['relationship']}`; evidence {colour['evidence_url']}; "
            f"{colour['evidence_summary']}"
            for colour in palette["extensions"]
        )
    else:
        lines.append("- None; do not invent an extension.")
    lines.append(
        "Do not sample, infer, or add colours from the user reference, FigureBench, or another palette group."
    )
    return lines


def _coverage_lines(context3: Mapping[str, Any]) -> list[str]:
    return [f"- {record['component_id']}: mapped crop ids {', '.join(record['crop_ids'])}." if "crop_ids" in record else f"- {record['component_id']}: basic geometry only — {record['basic_geometry_justification']}" for record in context3["coverage_matrix"]]


def _domain_crops(context1: Mapping[str, Any], component_ids: set[str], root: Path) -> list[dict[str, Any]]:
    attachments = []
    paths: set[str] = set()
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
                if "role" in record and _string(record["role"], f"{location} role") != "domain_paper_component":
                    raise ValueError(f"{location} role disagrees with domain-paper crop provenance")
                target = _string(record.get("target_component_id"), location)
                if target not in component_ids:
                    raise ValueError(f"{location} target_component_id must name a Context 2 component")
                contract = record.get("crop_contract", record)
                if not isinstance(contract, Mapping):
                    raise ValueError(f"{location} crop_contract must be an object")
                path = _resolve_attachment(record.get("path", record.get("crop_path")), root=root, expected_root=_DOMAIN_CROP_ROOT, location=location)
                if _is_under(PurePosixPath(path), _REPLACEMENT_CROP_ROOT):
                    raise ValueError(f"{location} role disagrees with replacement crop provenance")
                if path in paths:
                    raise ValueError("Context 1 domain-paper crop paths must be unique")
                paths.add(path)
                attachments.append(_attachment(path, "domain_paper_component", target_component_id=target, borrow=_string_list(contract.get("borrow"), f"{location} borrow"), must_change=_string_list(contract.get("must_change"), f"{location} must_change"), concept=convention["concept"]))
    return attachments


def _figurebench_attachments(context3: Mapping[str, Any], root: Path) -> list[dict[str, Any]]:
    attachments = []
    for index, selection in enumerate(context3["selected_references"]):
        location = f"context3 selected_references[{index}]"
        if "role" in selection and _string(selection["role"], f"{location} role") != "figurebench_component":
            raise ValueError(f"{location} role disagrees with FigureBench crop provenance")
        path = _resolve_attachment(selection["crop_path"], root=root, expected_root=_FIGUREBENCH_CROP_ROOT, location=location)
        contract = selection["crop_contract"]
        attachments.append(_attachment(path, "figurebench_component", crop_id=selection["crop_id"], reference_id=selection["reference_id"], target_component_id=selection["target_component_id"], borrow=contract["borrow"], must_change=contract["must_change"], human_editable_reason=contract["human_editable_reason"]))
    return attachments


def build_prompt1_bundle(methodology: str, context1: Mapping[str, Any], context2: Mapping[str, Any], context3: Mapping[str, Any], user_reference: str | None, root: Path) -> dict[str, Any]:
    """Compile Prompt 1 with full evidence and run-root-provenance attachments."""

    methodology = _string(methodology, "methodology")
    run_root = _run_root(root)
    normalized1, normalized2, normalized3 = _validated_contexts(context1, context2, context3)
    component_ids = {component["id"] for component in normalized2["components"]}
    attachments: list[dict[str, Any]] = []
    if user_reference is not None:
        path = _resolve_attachment(user_reference, root=run_root, expected_root=_USER_REFERENCE_ROOT, location="user_reference")
        attachments.append(_attachment(path, "user_reference", contract=_USER_REFERENCE_CONTRACT))
    domain_crops = _domain_crops(normalized1, component_ids, run_root)
    figurebench_crops = _figurebench_attachments(normalized3, run_root)
    attachments.extend(domain_crops)
    attachments.extend(figurebench_crops)
    crop_lines = [f"- `{item['path']}` -> Target: {item['target_component_id']}. Borrow: {'; '.join(item['borrow'])}. Must change: {'; '.join(item['must_change'])}." for item in [*domain_crops, *figurebench_crops]]
    user_contract = ["User-reference attachment contract:", f"- {_USER_REFERENCE_CONTRACT}"] if user_reference is not None else []
    prompt = "\n".join([
        "Create one publication-quality scientific architecture figure.", *_evidence_blocks(methodology, normalized1, normalized2, normalized3), *user_contract,
        "", "## 1. Figure purpose and scientific mainline", f"Purpose: communicate the `{normalized1['domain']}` method as `{normalized2['mainline']}`.",
        "", "## 2. Exact block and structure names", *_component_lines(normalized2),
        "", "## 3. Semantic relationships and reading order", *_relationship_lines(normalized2), "Read in the stated relationship order; preserve directionality and scientific logic.",
        "", "## 4. Content-to-visual mapping for every element", *_component_lines(normalized2), "Context 1 research explanations are evidence only; never copy explanatory prose into the figure.",
        "", "## 5. Crop-to-component mapping", *crop_lines, "Coverage matrix (complete):", *_coverage_lines(normalized3),
        "", "## 6. Single-palette contract", *_palette_lines(normalized3),
        "", "## 7. Layout and taste constraints", *(f"- {constraint}" for constraint in normalized3["taste_constraints"]), "Keep hierarchy, spacing, rhythm, restraint, and a human-edited finish subordinate to scientific meaning.",
        "", "## 8. Exact labels and text-density limits", "Use only concise block/structure names, necessary labels, terms, and relationship labels in-image. Never copy explanatory prose, research findings, or planning captions.",
        "", "## 9. Anti-AI visual constraints", "Do not add decoration without a named scientific role. Do not use decorative visuals unrelated to text, unexplained dots, floating symbols, or purposeless boxes.", "Do not use arbitrary high-contrast colours between adjacent modules, shapes with no human construction provenance, numbered 1/2/3/4 planning labels, the generic blue-title-strip-inside-every-box pattern, repeated card grids that make the figure look like a slide deck, or fake cartoon objects when a real crop or editable scientific geometry is expected.", "Only an explicit user requirement in the supplied Methodology or normalized Context may override the default prohibition on numbered 1/2/3/4 planning labels or the generic blue-title-strip-inside-every-box pattern. This narrow override does not permit any other anti-AI constraint to be overridden.",
        "", "## 10. Direct PNG generation instruction", "Generate PNG1 directly from this complete bundle. Every mapped crop uses its declared target and contract; the user reference is governed by its global structural contract and has no target component. This workflow has exactly two image-generation passes; this is the first. Produce one coherent scientific figure, not a slide deck or an illustration collage.",
    ])
    return {"format": _FORMAT, "phase": "prompt1", "prompt": prompt, "component_ids": sorted(component_ids), "attachments": attachments}


def _crop_records(value: Mapping[str, Any], location: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{location} requires an object")
    records = value.get("crops", [])
    if not isinstance(records, list) or not all(isinstance(record, Mapping) for record in records):
        raise ValueError(f"{location} crops must be a list of objects")
    return records


def _prompt2_crops(value: Mapping[str, Any], role: str, location: str, component_ids: set[str], verdicts: Mapping[str, Mapping[str, Any]], root: Path) -> list[dict[str, Any]]:
    expected_root = _APPROVED_SVG_CROP_ROOT if role == "approved_svg_crop" else _REPLACEMENT_CROP_ROOT
    attachments = []
    for index, record in enumerate(_crop_records(value, location)):
        crop_location = f"{location} crops[{index}]"
        _reject_prompt2_exclusion(_decoded_relative(record.get("path", record.get("crop_path")), f"{crop_location} path"), record.get("role"))
        if "role" in record and _string(record["role"], f"{crop_location} role") != role:
            raise ValueError(f"{crop_location} role disagrees with {role} provenance")
        target = _string(record.get("target_component_id"), crop_location)
        if target not in component_ids:
            raise ValueError(f"{crop_location} target_component_id must name a Context 2 component")
        path = _resolve_attachment(record.get("path", record.get("crop_path")), root=root, expected_root=expected_root, location=crop_location, role=record.get("role"), prompt2=True)
        verdict = verdicts[target]["verdict"]
        if role == "approved_svg_crop" and verdict in {"reject", "replace"}:
            raise ValueError(f"{crop_location} cannot approve a rejected or replacement component")
        if role == "replacement_crop" and verdict not in {"reject", "replace"}:
            raise ValueError(f"{crop_location} requires a reject or replace diagnosis")
        details: dict[str, Any] = {"target_component_id": target}
        if role == "approved_svg_crop":
            details["diagnosis"] = _string(record.get("diagnosis"), f"{crop_location} diagnosis")
        else:
            details["reason"] = _string(record.get("reason"), f"{crop_location} reason")
        attachments.append(_attachment(path, role, **details))
    return attachments


def _diagnostic_repair_lines(
    components: list[Mapping[str, Any]], verdicts: Mapping[str, Mapping[str, Any]]
) -> list[str]:
    """Turn SVG1/PNG1.5 findings into explicit, component-scoped PNG1 edits."""

    lines = [
        "## Mandatory SVG1/PNG1.5 correction gate",
        "Actively modify PNG1 to make PNG2; do not merely copy PNG1 or treat PNG1.5 as a passive proof image.",
        "Compare every planned component in PNG1 against the direct SVG1 transcription and its PNG1.5 render before deciding that it is faithful.",
        "If a box that is flat or solid in PNG1 is covered by a gradient, translucent overlay, glow, filter, or other unrequested effect in SVG1/PNG1.5, treat that as a transcription defect: patch PNG2 back to the single approved palette fill and preserve the editable boundary.",
        "If a badge, seal, medal, icon, marker, or other semantically meaningful object visible in PNG1 is absent, merged into a box, or materially distorted in SVG1/PNG1.5, it has failed transcription: reject or replace it and restore a human-editable version in PNG2.",
        "Do not mark a component keep or accept_variation when this comparison finds a gradient-over-solid defect, a missing badge/icon, an occluded label, or a broken scientific relationship. Upgrade the verdict and execute the repair.",
        "The diagnosis is actionable only when the stated verdict changes the PNG1 edit: preserve faithful parts, patch bounded defects, delete unsupported decoration, and use replacement crops for semantically wrong or missing objects.",
    ]
    for component in components:
        component_id = component["id"]
        record = verdicts[component_id]
        verdict = record["verdict"]
        reason = record.get("reason", "re-run the direct comparison and state the evidence")
        detail = reason.strip() if isinstance(reason, str) and reason.strip() else "re-run the direct comparison and state the evidence"
        if verdict in {"patch", "reject", "replace"}:
            lines.append(
                f"- REQUIRED PNG1 edit for `{component_id}`: verdict `{verdict}` — {detail} Modify this component in PNG2; do not leave the diagnosed defect unchanged."
            )
        else:
            lines.append(
                f"- Verification for `{component_id}`: verdict `{verdict}` — {detail} If the pixel comparison contradicts this verdict, change it to `patch`, `reject`, or `replace` and repair PNG1 in PNG2."
            )
    return lines


def build_prompt2_bundle(methodology: str, context1: Mapping[str, Any], context2: Mapping[str, Any], context3: Mapping[str, Any], png1: str, diagnosis: Mapping[str, Any], svg_crops: Mapping[str, Any], replacement_crops: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Compile the final PNG revision prompt while rejecting diagnostic-render inputs."""

    methodology = _string(methodology, "methodology")
    run_root = _run_root(root)
    normalized1, normalized2, normalized3 = _validated_contexts(context1, context2, context3)
    component_ids = {component["id"] for component in normalized2["components"]}
    normalized_diagnosis = validate_diagnosis(diagnosis, component_ids)
    verdicts = {record["component_id"]: record for record in normalized_diagnosis["verdicts"]}
    png1_path = _resolve_attachment(png1, root=run_root, expected_root=None, exact_path=PurePosixPath("png1.png"), location="png1", prompt2=True)
    attachments = [_attachment(png1_path, "png1_visual_truth")]
    attachments.extend(_prompt2_crops(svg_crops, "approved_svg_crop", "svg_crops", component_ids, verdicts, run_root))
    replacement_attachments = _prompt2_crops(
        replacement_crops,
        "replacement_crop",
        "replacement_crops",
        component_ids,
        verdicts,
        run_root,
    )
    required_replacements = {
        component_id
        for component_id, record in verdicts.items()
        if record["verdict"] == "replace"
    }
    supplied_replacements = {
        item["target_component_id"] for item in replacement_attachments
    }
    missing_replacements = sorted(required_replacements - supplied_replacements)
    if missing_replacements:
        raise ValueError(
            "replace verdicts require mapped replacement crops: "
            + ", ".join(missing_replacements)
        )
    attachments.extend(replacement_attachments)
    blocks: dict[str, list[str]] = {verdict: [] for verdict, _ in _VERDICT_BLOCKS}
    for component in normalized2["components"]:
        record = verdicts[component["id"]]
        detail = record.get("reason", "No additional diagnostic explanation supplied")
        if not isinstance(detail, str) or not detail.strip():
            raise ValueError(f"diagnosis verdict for {component['id']} requires a non-empty reason when supplied")
        blocks[record["verdict"]].append(f"- `{component['id']}` / `{component['label']}`: {detail.strip()}")
    verdict_sections: list[str] = []
    for verdict, heading in _VERDICT_BLOCKS:
        verdict_sections.extend([f"## {heading}", *(blocks[verdict] or ["- No components have this verdict."]), ""])
    prompt = "\n".join([
        "Revise PNG1 into the final PNG2. PNG1 is the image to modify and remains the only raster visual truth; use approved SVG and replacement crops only as targeted evidence.", *_evidence_blocks(methodology, normalized1, normalized2, normalized3), "Context 2 semantic relationships:", *_relationship_lines(normalized2), "Context 3 one-base-palette lineage:", *_palette_lines(normalized3), *_diagnostic_repair_lines(normalized2["components"], verdicts), *verdict_sections,
        "Use approved SVG crops only for their declared component and diagnosis. Use replacement crops only for explicitly rejected or replacement components.", "Do not attach, inspect as an image-generation reference, or derive a design from PNG1.5 / any SVG diagnostic render. This is the second and final image-generation pass. No PNG2-to-SVG loop.",
    ])
    return {"format": _FORMAT, "phase": "prompt2", "prompt": prompt, "component_ids": sorted(component_ids), "attachments": attachments}


def _validated_bundle(bundle: Mapping[str, Any], root: Path) -> tuple[str, str, list[dict[str, Any]]]:
    if not isinstance(bundle, Mapping) or bundle.get("format") != _FORMAT:
        raise ValueError("bundle has unsupported format")
    if set(bundle) != {"format", "phase", "prompt", "component_ids", "attachments"}:
        raise ValueError("bundle must contain the exact stable contract")
    phase = bundle.get("phase")
    if phase not in {"prompt1", "prompt2"}:
        raise ValueError("bundle has unsupported phase")
    prompt = _string(bundle.get("prompt"), "bundle prompt")
    component_ids = _string_list(bundle.get("component_ids"), "bundle component_ids")
    if component_ids != sorted(set(component_ids)):
        raise ValueError("bundle component_ids must be sorted and unique")
    component_id_set = set(component_ids)
    raw_attachments = bundle.get("attachments")
    if not isinstance(raw_attachments, list) or not all(isinstance(item, Mapping) for item in raw_attachments):
        raise ValueError("bundle attachments must be a list of objects")
    expected = {
        "user_reference": (_USER_REFERENCE_ROOT, {"path", "role", "contract"}),
        "domain_paper_component": (_DOMAIN_CROP_ROOT, {"path", "role", "target_component_id", "borrow", "must_change", "concept"}),
        "figurebench_component": (_FIGUREBENCH_CROP_ROOT, {"path", "role", "crop_id", "reference_id", "target_component_id", "borrow", "must_change", "human_editable_reason"}),
        "png1_visual_truth": (None, {"path", "role"}),
        "approved_svg_crop": (_APPROVED_SVG_CROP_ROOT, {"path", "role", "target_component_id", "diagnosis"}),
        "replacement_crop": (_REPLACEMENT_CROP_ROOT, {"path", "role", "target_component_id", "reason"}),
    }
    allowed = {"prompt1": {"user_reference", "domain_paper_component", "figurebench_component"}, "prompt2": {"png1_visual_truth", "approved_svg_crop", "replacement_crop"}}[phase]
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(raw_attachments):
        location = f"bundle attachments[{index}]"
        role = _string(item.get("role"), f"{location} role")
        if role not in allowed:
            raise ValueError(f"{location} role is invalid for {phase}")
        expected_root, exact_keys = expected[role]
        if set(item) != exact_keys:
            raise ValueError(f"{location} must contain the exact {role} contract")
        path = _resolve_attachment(item.get("path"), root=root, expected_root=expected_root, exact_path=PurePosixPath("png1.png") if role == "png1_visual_truth" else None, location=location, role=role, prompt2=phase == "prompt2")
        if role == "user_reference" and _string(item["contract"], f"{location} contract") != _USER_REFERENCE_CONTRACT:
            raise ValueError(f"{location} has an invalid user-reference contract")
        if role in {"domain_paper_component", "figurebench_component"}:
            target_component_id = _string(item["target_component_id"], f"{location} target_component_id")
            if target_component_id not in component_id_set:
                raise ValueError(f"{location} target_component_id must be in bundle component_ids")
            _string_list(item["borrow"], f"{location} borrow")
            _string_list(item["must_change"], f"{location} must_change")
        if role == "domain_paper_component":
            _string(item["concept"], f"{location} concept")
            if _is_under(PurePosixPath(path), _REPLACEMENT_CROP_ROOT):
                raise ValueError(f"{location} role disagrees with replacement crop provenance")
        if role == "figurebench_component":
            _string(item["crop_id"], f"{location} crop_id")
            _string(item["reference_id"], f"{location} reference_id")
            _string(item["human_editable_reason"], f"{location} human_editable_reason")
        if role == "approved_svg_crop":
            target_component_id = _string(item["target_component_id"], f"{location} target_component_id")
            if target_component_id not in component_id_set:
                raise ValueError(f"{location} target_component_id must be in bundle component_ids")
            _string(item["diagnosis"], f"{location} diagnosis")
        if role == "replacement_crop":
            target_component_id = _string(item["target_component_id"], f"{location} target_component_id")
            if target_component_id not in component_id_set:
                raise ValueError(f"{location} target_component_id must be in bundle component_ids")
            _string(item["reason"], f"{location} reason")
        if (path, role) in seen:
            raise ValueError("bundle attachments must not contain contradictory duplicates")
        seen.add((path, role))
        normalized.append(_canonical_attachment(item, path, role))
    if phase == "prompt2" and sum(item["role"] == "png1_visual_truth" for item in normalized) != 1:
        raise ValueError("prompt2 bundle requires exactly one PNG1 attachment")
    return phase, prompt, sorted(normalized, key=lambda item: (item["path"], item["role"]))


def _canonical_attachment(item: Mapping[str, Any], path: str, role: str) -> dict[str, Any]:
    """Return the exact role schema with normalized scalar and list metadata."""

    canonical: dict[str, Any] = {"path": path, "role": role}
    if role == "user_reference":
        canonical["contract"] = _USER_REFERENCE_CONTRACT
    elif role == "domain_paper_component":
        canonical.update(target_component_id=_string(item["target_component_id"], "attachment target_component_id"), borrow=_string_list(item["borrow"], "attachment borrow"), must_change=_string_list(item["must_change"], "attachment must_change"), concept=_string(item["concept"], "attachment concept"))
    elif role == "figurebench_component":
        canonical.update(crop_id=_string(item["crop_id"], "attachment crop_id"), reference_id=_string(item["reference_id"], "attachment reference_id"), target_component_id=_string(item["target_component_id"], "attachment target_component_id"), borrow=_string_list(item["borrow"], "attachment borrow"), must_change=_string_list(item["must_change"], "attachment must_change"), human_editable_reason=_string(item["human_editable_reason"], "attachment human_editable_reason"))
    elif role == "approved_svg_crop":
        canonical.update(target_component_id=_string(item["target_component_id"], "attachment target_component_id"), diagnosis=_string(item["diagnosis"], "attachment diagnosis"))
    elif role == "replacement_crop":
        canonical.update(target_component_id=_string(item["target_component_id"], "attachment target_component_id"), reason=_string(item["reason"], "attachment reason"))
    return canonical


def validate_prompt_bundle(bundle: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Validate and normalize one complete Prompt 1 or Prompt 2 bundle."""

    run_root = _run_root(root)
    phase, prompt, attachments = _validated_bundle(bundle, run_root)
    component_ids = sorted(_string_list(bundle.get("component_ids"), "bundle component_ids"))
    return {
        "format": _FORMAT,
        "phase": phase,
        "prompt": prompt,
        "component_ids": component_ids,
        "attachments": attachments,
    }


def write_bundle(bundle: Mapping[str, Any], output_dir: Path) -> None:
    """Atomically write a bundle; ``output_dir.parent`` is the canonical run root.

    The output directory must be ``run_root/prompt-1`` or ``run_root/prompt-2`` for
    its phase. Attachments are resolved and revalidated against that run root. Both
    files are staged before publication. A handled replacement failure restores the
    prior pair (or removes a newly published half); POSIX cannot make two replacements
    process-crash atomic.
    """

    destination = Path(output_dir)
    root = _run_root(destination.parent)
    phase, prompt, attachments = _validated_bundle(bundle, root)
    expected_name = "prompt-1" if phase == "prompt1" else "prompt-2"
    if destination.name != expected_name or destination.resolve(strict=False).parent != root:
        raise ValueError(f"output_dir must be run_root/{expected_name}")
    try:
        prompt_bytes = prompt.encode("utf-8")
        attachment_bytes = (json.dumps(attachments, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ValueError("bundle cannot be serialized") from error
    destination.mkdir(parents=False, exist_ok=True)
    if destination.is_symlink() or not destination.is_dir():
        raise ValueError("output_dir must be a real directory")
    temporary_paths: list[Path] = []
    published: list[str] = []
    originals: dict[str, bytes | None] = {}
    for name in ("prompt.md", "attachments.json"):
        existing = destination / name
        originals[name] = existing.read_bytes() if existing.exists() else None

    def stage(name: str, payload: bytes) -> Path:
        with tempfile.NamedTemporaryFile(dir=destination, prefix=f".{name}.", delete=False) as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            return Path(temporary.name)

    try:
        for name, payload in (("prompt.md", prompt_bytes), ("attachments.json", attachment_bytes)):
            temporary_paths.append(stage(name, payload))
        for name, temporary_path in zip(("prompt.md", "attachments.json"), temporary_paths, strict=True):
            os.replace(temporary_path, destination / name)
            published.append(name)
    except Exception:
        for name in reversed(published):
            original = originals[name]
            try:
                if original is None:
                    (destination / name).unlink(missing_ok=True)
                else:
                    os.replace(stage(f"restore-{name}", original), destination / name)
            except OSError:
                pass
        raise
    finally:
        for temporary_path in temporary_paths:
            if temporary_path.exists():
                temporary_path.unlink()
