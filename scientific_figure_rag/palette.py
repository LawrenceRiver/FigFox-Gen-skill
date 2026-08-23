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
        if not isinstance(colour, dict) or set(colour) != {"role", "hex", "rgb"}:
            raise ValueError(f"Palette {palette_id} has an invalid colour record")
        if colour["role"] not in ROLE_NAMES or not isinstance(colour["hex"], str) or not HEX.fullmatch(colour["hex"]):
            raise ValueError(f"Palette {palette_id} has invalid colour role or hex")
        if not isinstance(colour["rgb"], list) or len(colour["rgb"]) != 3 or any(
            not isinstance(value, int) or not 0 <= value <= 255 for value in colour["rgb"]
        ):
            raise ValueError(f"Palette {palette_id} has invalid RGB")
    return palette


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
