"""One-group palette lineage validation for Context 3 visual kits."""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlparse


PALETTE_RELATIONSHIPS = frozenset(
    {
        "tint",
        "shade",
        "tone",
        "analogous_neighbour",
        "compatible_neutral",
        "controlled_contrast",
    }
)
_UPPERCASE_HEX = re.compile(r"#[0-9A-F]{6}\Z")
_ONE_GROUP_FIELDS = frozenset({"additional_palette_ids", "source_palette_ids"})
_USER_REFERENCE_FIELDS = frozenset({"user_reference_palette_id", "user_reference_colours"})
_FIGUREBENCH_FIELDS = frozenset({"figurebench_palette_id", "figurebench_colours"})
_FORBIDDEN_SOURCE_FIELDS = frozenset({"base_palette", "palette_source", "palette_sources", "source"})
_GRADIENT_FIELDS = frozenset({"gradient", "gradients", "gradient_stops"})
_PALETTE_FIELDS = frozenset({"base_palette_id", "colours", "extensions"})


def _mapping(value: Any, location: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{location} must be an object")
    return value


def _required_string(record: Mapping[str, Any], key: str, location: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires non-empty {key}")
    return value.strip()


def _validate_colour(record: Any, location: str) -> dict[str, Any]:
    source = _mapping(record, location)
    role = _required_string(source, "role", location)
    hex_value = _required_string(source, "hex", location)
    if source.get("hex") != hex_value or not _UPPERCASE_HEX.fullmatch(hex_value):
        raise ValueError(f"{location} requires exact uppercase HEX")
    rgb = source.get("rgb")
    if (
        not isinstance(rgb, list)
        or len(rgb) != 3
        or any(
            not isinstance(channel, int)
            or isinstance(channel, bool)
            or not 0 <= channel <= 255
            for channel in rgb
        )
    ):
        raise ValueError(f"{location} requires rgb with three integer channels")
    expected_rgb = [int(hex_value[index : index + 2], 16) for index in (1, 3, 5)]
    if rgb != expected_rgb:
        raise ValueError(f"{location} requires rgb matching hex")
    return {"role": role, "hex": hex_value, "rgb": copy.deepcopy(rgb)}


def _validate_colours(value: Any, location: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{location} requires at least one record")
    colours = [_validate_colour(record, f"{location}[{index}]") for index, record in enumerate(value)]
    hexes = [colour["hex"] for colour in colours]
    if len(hexes) != len(set(hexes)):
        raise ValueError("palette has duplicate hex values")
    return colours


def _reject_disallowed_fields(palette: Mapping[str, Any]) -> None:
    fields = set(palette)
    if forbidden := fields & _ONE_GROUP_FIELDS:
        raise ValueError(
            f"palette must not include {sorted(forbidden)[0]}: one base palette group is required"
        )
    if forbidden := fields & _USER_REFERENCE_FIELDS:
        raise ValueError(f"palette must not include {sorted(forbidden)[0]}: user-reference colours are forbidden")
    if forbidden := fields & _FIGUREBENCH_FIELDS:
        raise ValueError(f"palette must not include {sorted(forbidden)[0]}: FigureBench colours are forbidden")
    if forbidden := fields & _GRADIENT_FIELDS:
        raise ValueError(f"palette must not include {sorted(forbidden)[0]}: gradients are forbidden")
    if forbidden := fields & _FORBIDDEN_SOURCE_FIELDS:
        raise ValueError(f"palette must not include {sorted(forbidden)[0]}: secondary palette sources are forbidden")
    unexpected = fields - _PALETTE_FIELDS
    if unexpected:
        raise ValueError(f"palette must not include {sorted(unexpected)[0]}")


def _validate_extensions(value: Any, active_hexes: set[str]) -> list[dict[str, Any]]:
    if value is None:
        value = []
    if not isinstance(value, list):
        raise ValueError("palette extensions must be a list")
    extensions: list[dict[str, Any]] = []
    for index, extension in enumerate(value):
        location = f"palette extensions[{index}]"
        source = _mapping(extension, location)
        normalized = _validate_colour(source, location)
        relationship = _required_string(source, "relationship", location)
        if relationship not in PALETTE_RELATIONSHIPS:
            raise ValueError(f"{location} requires a supported relationship")
        evidence_url = _required_string(source, "evidence_url", location)
        parsed_url = urlparse(evidence_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise ValueError(f"{location} requires an HTTPS evidence_url")
        evidence_summary = _required_string(source, "evidence_summary", location)
        if normalized["hex"] in active_hexes:
            raise ValueError("palette has duplicate hex values")
        active_hexes.add(normalized["hex"])
        normalized.update(
            relationship=relationship,
            evidence_url=evidence_url,
            evidence_summary=evidence_summary,
        )
        extensions.append(normalized)
    return extensions


def _palette_shape(value: Mapping[str, Any]) -> dict[str, Any]:
    palette = _mapping(value, "palette")
    _reject_disallowed_fields(palette)
    base_palette_id = _required_string(palette, "base_palette_id", "palette")
    colours = _validate_colours(palette.get("colours"), "palette colours")
    extensions = _validate_extensions(palette.get("extensions", []), {colour["hex"] for colour in colours})
    return {
        "base_palette_id": base_palette_id,
        "colours": colours,
        "extensions": extensions,
    }


def _library_group(palette_library: Sequence[Mapping[str, Any]], palette_id: str) -> Mapping[str, Any]:
    if isinstance(palette_library, (str, bytes)) or not isinstance(palette_library, Sequence):
        raise ValueError("palette library must be a sequence of palette groups")
    for index, group in enumerate(palette_library):
        source = _mapping(group, f"palette library[{index}]")
        if _required_string(source, "id", f"palette library[{index}]") == palette_id:
            return source
    raise ValueError("base_palette_id must name an approved base palette group")


def _colour_identity(colour: Mapping[str, Any]) -> tuple[str, str, tuple[int, int, int]]:
    return colour["role"], colour["hex"], tuple(colour["rgb"])


def validate_palette(
    value: Mapping[str, Any], palette_library: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Return a Context 3-compatible palette from one library group and extensions."""

    normalized = _palette_shape(value)
    group = _library_group(palette_library, normalized["base_palette_id"])
    library_colours = _validate_colours(group.get("colours"), "selected base palette colours")
    if {
        _colour_identity(colour) for colour in normalized["colours"]
    } != {
        _colour_identity(colour) for colour in library_colours
    }:
        raise ValueError("palette colours must exactly match the selected base palette group")
    return normalized


def palette_hex_set(value: Mapping[str, Any]) -> frozenset[str]:
    """Return the exact active HEX values from a validated Context 3 palette."""

    palette = _palette_shape(value)
    return frozenset(
        colour["hex"] for colour in [*palette["colours"], *palette["extensions"]]
    )
