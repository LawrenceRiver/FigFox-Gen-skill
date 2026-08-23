"""Image-free retrieval for curated scientific figure colour groups."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
from typing import Any, Mapping


ROLE_NAMES = {"ink", "canvas", "surface", "primary", "secondary", "comparison", "accent", "muted"}
HEX = re.compile(r"#[0-9A-F]{6}$")
FORBIDDEN_KEYS = {"image", "screenshot", "thumbnail", "path", "url", "embedding"}
DEFAULT_LIBRARY = Path(__file__).resolve().parents[1] / "references/palette-library.json"


def _string_set(value: object) -> set[str]:
    if isinstance(value, str):
        return {value.lower()}
    if isinstance(value, list):
        return {item.lower() for item in value if isinstance(item, str)}
    return set()


def _validate_palette(palette: object) -> dict[str, Any]:
    if not isinstance(palette, dict):
        raise ValueError("Each palette must be an object")
    if FORBIDDEN_KEYS & {key.lower() for key in palette}:
        raise ValueError("Palette records must not include image-like fields")
    palette_id = palette.get("id")
    name = palette.get("name")
    tags = palette.get("tags")
    colours = palette.get("colours")
    if not isinstance(palette_id, str) or not palette_id:
        raise ValueError("Palette requires an id")
    if not isinstance(name, str) or not name:
        raise ValueError(f"Palette {palette_id} requires a name")
    if not isinstance(tags, list) or not all(isinstance(tag, str) and tag for tag in tags):
        raise ValueError(f"Palette {palette_id} has invalid tags")
    if not isinstance(colours, list) or not colours:
        raise ValueError(f"Palette {palette_id} requires colours")
    for colour in colours:
        _validate_colour_record(colour, f"Palette {palette_id}")
    return palette


def _validate_colour_record(colour: object, source_name: str) -> None:
    if not isinstance(colour, dict) or set(colour) != {"role", "hex", "rgb"}:
        raise ValueError(f"{source_name} has an invalid colour record")
    if colour["role"] not in ROLE_NAMES or not isinstance(colour["hex"], str) or not HEX.fullmatch(colour["hex"]):
        raise ValueError(f"{source_name} has invalid colour role or hex")
    if not isinstance(colour["rgb"], list) or len(colour["rgb"]) != 3 or any(
        not isinstance(value, int) or not 0 <= value <= 255 for value in colour["rgb"]
    ):
        raise ValueError(f"{source_name} has invalid RGB")


def load_palette_library(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load validated colour-only groups without retaining a visual source."""
    source = Path(path) if path else DEFAULT_LIBRARY
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("format") != "genlike-scientific-svg-palette-library-v1":
        raise ValueError("Unsupported palette library format")
    palettes = payload.get("palettes")
    if not isinstance(palettes, list):
        raise ValueError("Palette library requires a palettes list")
    validated = [_validate_palette(palette) for palette in palettes]
    if len({palette["id"] for palette in validated}) != len(validated):
        raise ValueError("Palette ids must be unique")
    return copy.deepcopy(validated)


def select_palettes(
    query: Mapping[str, object], top_k: int = 3, path: str | Path | None = None
) -> dict[str, object]:
    """Select compact palette groups from tags and required colour roles."""
    requested_tags = _string_set(query.get("tags")) | _string_set(query.get("figure_type"))
    required_roles = _string_set(query.get("required_roles"))
    limit = max(1, min(int(top_k), 5))

    scored: list[tuple[int, str, dict[str, Any]]] = []
    for palette in load_palette_library(path):
        tags = _string_set(palette["tags"])
        roles = {colour["role"] for colour in palette["colours"]}
        score = 4 * len(requested_tags & tags) + 3 * len(required_roles & roles)
        scored.append((score, palette["id"], palette))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return {
        "selection_basis": {
            "tags": sorted(requested_tags),
            "required_roles": sorted(required_roles),
            "top_k": limit,
        },
        "palettes": [copy.deepcopy(palette) for _, _, palette in scored[:limit]],
    }


def compile_colour_contract(
    plan: Mapping[str, object], path: str | Path | None = None
) -> dict[str, object]:
    """Freeze a render plan to exact colours from one permitted source.

    A source is either an approved local palette group or a per-run palette
    extracted from a web SVG whose declared domain is unrelated to the brief.
    The latter is deliberately not persisted in the local palette library.
    """
    brief_domains = _string_set(plan.get("brief_domains"))
    source = plan.get("source")
    assignments = plan.get("assignments")
    if not brief_domains:
        raise ValueError("Colour contract requires at least one brief domain")
    if not isinstance(source, Mapping) or not isinstance(assignments, Mapping) or not assignments:
        raise ValueError("Colour contract requires source and non-empty assignments")

    source_kind = source.get("kind")
    if source_kind == "approved_library":
        palette_id = source.get("palette_id")
        if not isinstance(palette_id, str) or not palette_id:
            raise ValueError("Approved-library source requires palette_id")
        palette = next((item for item in load_palette_library(path) if item["id"] == palette_id), None)
        if palette is None:
            raise ValueError(f"Unknown approved palette: {palette_id}")
        colours = palette["colours"]
        source_summary: dict[str, object] = {"kind": source_kind, "palette_id": palette_id}
    elif source_kind == "cross_domain_svg":
        source_domains = _string_set(source.get("source_domains"))
        colours = source.get("colours")
        if not source_domains:
            raise ValueError("Cross-domain SVG source requires source_domains")
        if brief_domains & source_domains:
            raise ValueError("Cross-domain SVG palette must come from a domain unrelated to the brief")
        if not isinstance(colours, list) or not colours:
            raise ValueError("Cross-domain SVG source requires extracted colours")
        source_summary = {
            "kind": source_kind,
            "source_domains": sorted(source_domains),
            "ephemeral": True,
        }
    else:
        raise ValueError("Colour source kind must be approved_library or cross_domain_svg")

    for colour in colours:
        _validate_colour_record(colour, "Colour source")
    allowed_hex = [colour["hex"] for colour in colours]
    if len(set(allowed_hex)) != len(allowed_hex):
        raise ValueError("Colour source cannot contain duplicate HEX values")

    frozen_assignments: dict[str, str] = {}
    for role, colour in assignments.items():
        if not isinstance(role, str) or not role or not isinstance(colour, str):
            raise ValueError("Colour assignments must map named roles to HEX values")
        if colour not in allowed_hex:
            raise ValueError(f"Assigned colour {colour} is not in the selected source")
        frozen_assignments[role] = colour

    return {
        "brief_domains": sorted(brief_domains),
        "source": source_summary,
        "allowed_hex": allowed_hex,
        "assignments": frozen_assignments,
        "render_rules": [
            "Use only allowed_hex values for all authored colour fills and strokes.",
            "Do not add, shift, blend, or activate colours outside allowed_hex.",
            "Retain SVG text as a separately composited, immutable final layer.",
        ],
    }
