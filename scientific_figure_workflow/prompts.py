"""Deterministic, provenance-safe compilers for the PNG1 prompt."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import unquote, urlparse

from .artifacts import (
    CREATIVE_DIRECTOR_FORMAT,
    validate_context1,
    validate_context2,
    validate_context3,
    validate_creative_director,
)


_FORMAT = "scientific-figure-prompt-bundle-v1"
_FIGUREBENCH_CROP_ROOT = PurePosixPath("references/figurebench/crops")
_DOMAIN_CROP_ROOT = PurePosixPath("references/web/crops")
_CREATIVE_DIRECTOR_CROP_ROOT = PurePosixPath("references/web/crops/creative-director")
_REPLACEMENT_CROP_ROOT = PurePosixPath("references/web/crops/replacements")
_USER_REFERENCE_ROOT = PurePosixPath("input")
_USER_REFERENCE_CONTRACT = (
    "Reference-fidelity lock: treat the supplied user reference as the canonical visual "
    "specification. Match its composition, spacing, hierarchy, and visual grammar; "
    "preserve its line weight, corner-radius, fill, typography scale, arrow, and sample "
    "treatment wherever the Methodology permits. Change only labels, scientific content, "
    "and geometry required by the Methodology. Do not beautify, complicate, stylize, "
    "recompose, or switch to a different visual language. Ignore only generated-looking, "
    "fake, or decorative parts. Use the selected palette group for active colours; never "
    "source palette colours from the user reference."
)

_HUMAN_CONSTRUCTION_ORDER = [
    "Human construction order is mandatory: choose the base canvas and simple editable geometry first; build the meaningful structures on it; add plain readable arrows; place concise exact text; then place the explanatory visual below or beside the text.",
    "Use real or explicitly documented input samples instead of repeated filler lines. For topology, grids, model blocks, and other known constructions, prefer a targeted crop from a real scholarly SVG/HTML figure over an invented pseudo-structure.",
    "Keep arrows visually subordinate and semantically directional. Keep repeated geometry regular and exact; keep each geometric block flat or one controlled fill; use deliberate repeated points or a real noise image only when noise is scientifically required; use real photographs only when scientifically necessary.",
]



def _string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires a non-empty string")
    return value.strip()


def _string_list(value: Any, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location} requires a non-empty list")
    return [_string(item, location) for item in value]


def _https_attachment_url(value: Any, location: str) -> str:
    candidate = _string(value, location)
    parsed = urlparse(candidate)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{location} requires HTTPS URL")
    return candidate


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


def _has_symlink_alias(root: Path, declared: Path) -> bool:
    current = root
    for part in declared.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _resolve_attachment(value: Any, *, root: Path, expected_root: PurePosixPath | None, location: str, exact_path: PurePosixPath | None = None) -> str:
    """Resolve a declared run-relative file and enforce canonical provenance."""

    relative = _decoded_relative(value, location)
    if exact_path is not None and relative != exact_path:
        raise ValueError(f"{location} must be {exact_path.as_posix()}")
    if expected_root is not None and not _is_under(relative, expected_root):
        names = {
            _FIGUREBENCH_CROP_ROOT: "FigureBench crop root",
            _DOMAIN_CROP_ROOT: "domain-paper crop root",
            _CREATIVE_DIRECTOR_CROP_ROOT: "Creative Director crop root",
            _REPLACEMENT_CROP_ROOT: "replacement crop root",
            _USER_REFERENCE_ROOT: "run input area",
        }
        raise ValueError(f"{location} must be under the {names[expected_root]}")
    declared = root.joinpath(*relative.parts)
    if not declared.is_file():
        raise ValueError(f"{location} requires an existing file")
    resolved = declared.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError(f"{location} resolves outside the run root")
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


def _palette_lines(
    context3: Mapping[str, Any], dominant_colour_count: int
) -> list[str]:
    palette = context3["palette"]
    lines = [
        f"Use the selected multi-colour palette group `{palette['base_palette_id']}` and its evidenced extensions.",
        "Use multiple colours from that group; this is not a monochrome or single-colour constraint.",
        "Limit the figure to at most three dominant colours from this group.",
        f"The first representative scholarly figure selected during Context 1 established {dominant_colour_count} dominant colour(s); use exactly that many dominant colours from this group. Later domain figures may corroborate the count but must not replace this evidence with a subjective guess.",
        "Dominant colour roles (maximum three): " + ", ".join(palette["dominant_colour_roles"]) + ".",
        "Other swatches may appear only as subordinate neutral, tint, shade, or support roles and must not become a fourth dominant hue.",
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


def _default_creative_director(context2: Mapping[str, Any]) -> dict[str, Any]:
    first_component = context2["components"][0]["id"]
    return {
        "format": CREATIVE_DIRECTOR_FORMAT,
        "brief": "No additional creative direction was requested; use the validated Context 1–3 construction plan.",
        "ideas": [
            {
                "id": "context-baseline",
                "target_component_id": first_component,
                "concept": "Use the existing Context 1–3 visual plan without adding a new special visual.",
                "visual_intent": "Keep the figure human-editable and semantically direct.",
                "construction_plan": "Follow the mapped domain and FigureBench evidence already present in Contexts 1–3.",
                "requires_svg_evidence": False,
                "svg_crops": [],
            }
        ],
    }


def build_creative_director_prompt(
    methodology: str,
    context1: Mapping[str, Any],
    context2: Mapping[str, Any],
    context3: Mapping[str, Any],
) -> dict[str, Any]:
    """Compile the pre-PNG1 creative-director instruction."""

    methodology = _string(methodology, "methodology")
    normalized1, normalized2, normalized3 = _validated_contexts(context1, context2, context3)
    prompt = "\n".join([
        "Act as the Creative Director before PNG1 generation.",
        "Propose concrete, scientifically relevant visual ideas for the planned figure; do not generate PNG1.",
        "For every idea that needs a mature visual construction not already covered by Contexts 1–3, locate a real scholarly paper figure available as SVG or extractable SVG/HTML, inspect its pixels, and provide a targeted crop request.",
        "A paper SVG crop must name its target component, source and evidence HTTPS URLs, source_format `svg`, what to borrow, what must change, and why the crop remains human-editable. Never attach a complete paper figure, invent a source, or use a sticker-like cutout.",
        "Before proposing a visual treatment, simulate human editor construction in this order:",
        *[f"- {line}" for line in _HUMAN_CONSTRUCTION_ORDER],
        "Respect the selected multi-colour palette-group lineage and the absolute PNG1 bans on upper title-bands and pasted raster stickers. The creative brief is evidence for Prompt 1, not a licence to override those constraints.",
        *_evidence_blocks(methodology, normalized1, normalized2, normalized3),
        "Return a `creative-director-brief-v1` JSON with `brief` and an `ideas` list. Each idea must include `id`, `target_component_id`, `concept`, `visual_intent`, `construction_plan`, `requires_svg_evidence`, and `svg_crops`.",
    ])
    return {
        "format": "creative-director-prompt-bundle-v1",
        "phase": "creative_director",
        "prompt": prompt,
        "component_ids": sorted(component["id"] for component in normalized2["components"]),
        "attachments": [],
    }


def _creative_director_attachments(
    creative_director: Mapping[str, Any], component_ids: set[str], root: Path
) -> list[dict[str, Any]]:
    attachments: list[dict[str, Any]] = []
    for idea in creative_director["ideas"]:
        for crop in idea["svg_crops"]:
            target = crop["target_component_id"] if "target_component_id" in crop else idea["target_component_id"]
            if target not in component_ids:
                raise ValueError("creative director SVG crop target_component_id must name a Context 2 component")
            path = _resolve_attachment(
                crop["path"],
                root=root,
                expected_root=_CREATIVE_DIRECTOR_CROP_ROOT,
                location=f"creative director idea {idea['id']} SVG crop",
            )
            attachments.append(_attachment(
                path,
                "creative_director_svg",
                idea_id=idea["id"],
                target_component_id=target,
                source_url=crop["source_url"],
                evidence_url=crop["evidence_url"],
                source_format="svg",
                borrow=crop["borrow"],
                must_change=crop["must_change"],
                human_editable_reason=crop["human_editable_reason"],
            ))
    return attachments


def _creative_director_lines(creative_director: Mapping[str, Any]) -> list[str]:
    lines = ["Creative Director brief:", f"- {creative_director['brief']}", "Creative Director ideas:"]
    for idea in creative_director["ideas"]:
        lines.append(
            f"- `{idea['id']}` -> `{idea['target_component_id']}`: {idea['concept']} "
            f"Intent: {idea['visual_intent']} Construction: {idea['construction_plan']}"
        )
        for crop in idea["svg_crops"]:
            lines.append(
                f"  - Paper SVG crop `{crop['path']}` from {crop['evidence_url']} "
                f"(paper {crop['source_url']}). Borrow: {'; '.join(crop['borrow'])}. "
                f"Must change: {'; '.join(crop['must_change'])}. {crop['human_editable_reason']}"
            )
    return lines


def build_prompt1_bundle(methodology: str, context1: Mapping[str, Any], context2: Mapping[str, Any], context3: Mapping[str, Any], user_reference: str | None, root: Path, creative_director: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Compile Prompt 1 with full evidence and run-root-provenance attachments."""

    methodology = _string(methodology, "methodology")
    run_root = _run_root(root)
    normalized1, normalized2, normalized3 = _validated_contexts(context1, context2, context3)
    component_ids = {component["id"] for component in normalized2["components"]}
    normalized_creative = validate_creative_director(
        creative_director or _default_creative_director(normalized2), run_root, component_ids
    )
    attachments: list[dict[str, Any]] = []
    if user_reference is not None:
        path = _resolve_attachment(user_reference, root=run_root, expected_root=_USER_REFERENCE_ROOT, location="user_reference")
        attachments.append(_attachment(path, "user_reference", contract=_USER_REFERENCE_CONTRACT))
    domain_crops = _domain_crops(normalized1, component_ids, run_root)
    figurebench_crops = _figurebench_attachments(normalized3, run_root)
    creative_crops = _creative_director_attachments(normalized_creative, component_ids, run_root)
    attachments.extend(domain_crops)
    attachments.extend(figurebench_crops)
    attachments.extend(creative_crops)
    crop_lines = [f"- `{item['path']}` -> Target: {item['target_component_id']}. Borrow: {'; '.join(item['borrow'])}. Must change: {'; '.join(item['must_change'])}." for item in [*domain_crops, *figurebench_crops, *creative_crops]]
    user_contract = ["User-reference attachment contract:", f"- {_USER_REFERENCE_CONTRACT}"] if user_reference is not None else []
    prompt = "\n".join([
        "Create one publication-quality scientific architecture figure.", *_evidence_blocks(methodology, normalized1, normalized2, normalized3), *user_contract,
        "", "## 1. Figure purpose and scientific mainline", f"Purpose: communicate the `{normalized1['domain']}` method as `{normalized2['mainline']}`.",
        "", "## 2. Exact block and structure names", *_component_lines(normalized2),
        "", "## 3. Semantic relationships and reading order", *_relationship_lines(normalized2), "Read in the stated relationship order; preserve directionality and scientific logic.",
        "", "## 4. Content-to-visual mapping for every element", *_component_lines(normalized2), "Context 1 research explanations are evidence only; never copy explanatory prose into the figure.",
        "", "## 5. Creative Director brief and paper-SVG evidence", *_creative_director_lines(normalized_creative), "Treat every paper-SVG crop as targeted construction evidence only; do not copy its labels, palette, proportions, or complete composition.",
        "", "## 6. Crop-to-component mapping", *crop_lines, "Coverage matrix (complete):", *_coverage_lines(normalized3),
        "", "## 7. Palette-group contract", *_palette_lines(normalized3, normalized1["dominant_colour_count"]),
        "", "## 8. Layout and taste constraints", *(f"- {constraint}" for constraint in normalized3["taste_constraints"]), "Keep hierarchy, spacing, rhythm, restraint, and a human-edited finish subordinate to scientific meaning.",
        "", "## 9. Exact labels and text-density limits", "Use only concise block/structure names, necessary labels, terms, and relationship labels in-image. Never copy explanatory prose, research findings, or planning captions.",
        "", "## 10. Anti-AI visual constraints", "Do not add decoration without a named scientific role. Do not use decorative visuals unrelated to text, unexplained dots, floating symbols, or purposeless boxes.", "Do not use arbitrary high-contrast colours between adjacent modules, shapes with no human construction provenance, numbered 1/2/3/4 planning labels, the generic blue-title-strip-inside-every-box pattern, repeated card grids that make the figure look like a slide deck, or fake cartoon objects when a real crop or editable scientific geometry is expected.", "A subtle, intentional fill transition is allowed only on a planned base/container shape. Do not use decorative gradients, gradients inside a geometric block, glow, or shading to hide an unplanned structure.", "Hard first-pass prohibition: never draw an upper title-band inside a module by boxing off its top portion with a horizontal divider and centered title. Do not use the screenshot-like title-bar/content-box treatment shown in the supplied counterexample. Labels must sit inline, outside the frame, or in the planned geometry without a dedicated header strip.", "Hard first-pass prohibition: never paste a sticker-like cutout, clip-art badge, medal, seal, or pasted raster badge directly into PNG1. If a scientific object is genuinely required, construct it as editable geometry or mark it as a Context 2 special real-photo treatment; a decorative sticker is never acceptable.", "These two prohibitions cannot be overridden by FigureBench crops, user references, taste guidance, or an inferred aesthetic preference. Only the explicit scientific Methodology can require a real scientific special visual, and it still cannot justify a title band or pasted sticker.", "Only an explicit user requirement in the supplied Methodology or normalized Context may override the default prohibition on numbered 1/2/3/4 planning labels or the generic blue-title-strip-inside-every-box pattern. This narrow override does not permit any other anti-AI constraint to be overridden.",
        "Human construction order is a hard gate: base geometry first; meaningful content second; plain arrows third; concise exact labels fourth; explanatory visual next to or below its label last. Do not turn this into a stack of decorative cards.",
        "Use a real sample or a targeted scholarly-paper crop for an input, topology, grid, or known model whenever one exists. Never draw a fake topology or pseudo-sample merely to fill space. A repeated grid must be regular, a geometric block must use a flat or single controlled fill (with only a planned subtle base transition allowed), and arrows must remain plain and readable.",
        "", "## 11. Direct PNG generation instruction", "Generate PNG1 directly from this complete bundle. Every mapped crop uses its declared target and contract; every Creative Director paper-SVG crop is targeted evidence, not a complete reference; the user reference is governed by its global structural contract and has no target component. This is the only image-generation pass. Produce one coherent scientific figure, not a slide deck or an illustration collage.",
    ])
    return {"format": _FORMAT, "phase": "prompt1", "prompt": prompt, "component_ids": sorted(component_ids), "attachments": attachments}



def _validated_bundle(bundle: Mapping[str, Any], root: Path) -> tuple[str, str, list[dict[str, Any]]]:
    if not isinstance(bundle, Mapping) or bundle.get("format") != _FORMAT:
        raise ValueError("bundle has unsupported format")
    if set(bundle) != {"format", "phase", "prompt", "component_ids", "attachments"}:
        raise ValueError("bundle must contain the exact stable contract")
    if bundle.get("phase") != "prompt1":
        raise ValueError("bundle phase must be prompt1")
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
        "creative_director_svg": (_CREATIVE_DIRECTOR_CROP_ROOT, {"path", "role", "idea_id", "target_component_id", "source_url", "evidence_url", "source_format", "borrow", "must_change", "human_editable_reason"}),
    }
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(raw_attachments):
        location = f"bundle attachments[{index}]"
        role = _string(item.get("role"), f"{location} role")
        if role not in expected:
            raise ValueError(f"{location} role is invalid for prompt1")
        expected_root, exact_keys = expected[role]
        if set(item) != exact_keys:
            raise ValueError(f"{location} must contain the exact {role} contract")
        path = _resolve_attachment(item.get("path"), root=root, expected_root=expected_root, location=location)
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
        if role == "creative_director_svg":
            _string(item["idea_id"], f"{location} idea_id")
            target_component_id = _string(item["target_component_id"], f"{location} target_component_id")
            if target_component_id not in component_id_set:
                raise ValueError(f"{location} target_component_id must be in bundle component_ids")
            if _string(item["source_format"], f"{location} source_format").casefold() != "svg":
                raise ValueError(f"{location} source_format must be svg")
            _https_attachment_url(item["source_url"], f"{location} source_url")
            _https_attachment_url(item["evidence_url"], f"{location} evidence_url")
            _string_list(item["borrow"], f"{location} borrow")
            _string_list(item["must_change"], f"{location} must_change")
            _string(item["human_editable_reason"], f"{location} human_editable_reason")
        if (path, role) in seen:
            raise ValueError("bundle attachments must not contain contradictory duplicates")
        seen.add((path, role))
        normalized.append(_canonical_attachment(item, path, role))
    return "prompt1", prompt, sorted(normalized, key=lambda item: (item["path"], item["role"]))


def _canonical_attachment(item: Mapping[str, Any], path: str, role: str) -> dict[str, Any]:
    canonical: dict[str, Any] = {"path": path, "role": role}
    if role == "user_reference":
        canonical["contract"] = _USER_REFERENCE_CONTRACT
    elif role == "domain_paper_component":
        canonical.update(target_component_id=_string(item["target_component_id"], "attachment target_component_id"), borrow=_string_list(item["borrow"], "attachment borrow"), must_change=_string_list(item["must_change"], "attachment must_change"), concept=_string(item["concept"], "attachment concept"))
    elif role == "figurebench_component":
        canonical.update(crop_id=_string(item["crop_id"], "attachment crop_id"), reference_id=_string(item["reference_id"], "attachment reference_id"), target_component_id=_string(item["target_component_id"], "attachment target_component_id"), borrow=_string_list(item["borrow"], "attachment borrow"), must_change=_string_list(item["must_change"], "attachment must_change"), human_editable_reason=_string(item["human_editable_reason"], "attachment human_editable_reason"))
    elif role == "creative_director_svg":
        canonical.update(idea_id=_string(item["idea_id"], "attachment idea_id"), target_component_id=_string(item["target_component_id"], "attachment target_component_id"), source_url=_https_attachment_url(item["source_url"], "attachment source_url"), evidence_url=_https_attachment_url(item["evidence_url"], "attachment evidence_url"), source_format="svg", borrow=_string_list(item["borrow"], "attachment borrow"), must_change=_string_list(item["must_change"], "attachment must_change"), human_editable_reason=_string(item["human_editable_reason"], "attachment human_editable_reason"))
    return canonical


def validate_prompt_bundle(bundle: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Validate and normalize the single Prompt 1 bundle."""

    run_root = _run_root(root)
    phase, prompt, attachments = _validated_bundle(bundle, run_root)
    return {
        "format": _FORMAT,
        "phase": phase,
        "prompt": prompt,
        "component_ids": sorted(_string_list(bundle.get("component_ids"), "bundle component_ids")),
        "attachments": attachments,
    }


def write_bundle(bundle: Mapping[str, Any], output_dir: Path) -> None:
    """Atomically write the Prompt 1 prompt and attachment manifest."""

    destination = Path(output_dir)
    root = _run_root(destination.parent)
    phase, prompt, attachments = _validated_bundle(bundle, root)
    if destination.name != "prompt-1" or destination.resolve(strict=False).parent != root:
        raise ValueError("output_dir must be run_root/prompt-1")
    prompt_bytes = prompt.encode("utf-8")
    attachment_bytes = (json.dumps(attachments, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    destination.mkdir(parents=False, exist_ok=True)
    if destination.is_symlink() or not destination.is_dir():
        raise ValueError("output_dir must be a real directory")
    temporary_paths: list[Path] = []
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
    except Exception:
        for name, original in originals.items():
            try:
                if original is None:
                    (destination / name).unlink(missing_ok=True)
                else:
                    (destination / name).write_bytes(original)
            except OSError:
                pass
        raise
    finally:
        for temporary_path in temporary_paths:
            if temporary_path.exists():
                temporary_path.unlink()
