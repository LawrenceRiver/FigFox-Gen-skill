"""Select a small, diverse visual grammar pack from a local FigureBench index."""

from __future__ import annotations

import math
from typing import Any, Iterable


def _vector(record: dict[str, Any]) -> list[float]:
    visual = record.get("visual", {})
    return [
        float(visual.get("aspect_ratio", 1.0)) / 3.0,
        *(float(value) for value in visual.get("mean_rgb", [0.5, 0.5, 0.5])),
        *(float(value) for value in visual.get("std_rgb", [0.0, 0.0, 0.0])),
        float(visual.get("palette_size_capped", 0)) / 96.0,
        float(visual.get("foreground_ratio", 0)),
        float(visual.get("horizontal_edge_energy", 0)),
        float(visual.get("vertical_edge_energy", 0)),
        float(visual.get("occupied_grid_cells", 0)) / 9.0,
    ]


def _distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    style_distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(_vector(left), _vector(right))))
    left_layout = left.get("metadata", {}).get("layout")
    right_layout = right.get("metadata", {}).get("layout")
    return style_distance + (0.75 if left_layout != right_layout else 0.0)


def select_diverse_records(records: Iterable[dict[str, Any]], count: int = 20) -> list[dict[str, Any]]:
    """Cover layout families first, then greedily maximise geometry/style distance."""
    candidates = sorted(records, key=lambda item: str(item["record_id"]))
    selected: list[dict[str, Any]] = []
    used_groups: set[str] = set()
    group_key = lambda item: item.get("source_group_id") or item["record_id"]
    for layout in sorted({item.get("metadata", {}).get("layout", "unknown") for item in candidates}):
        choice = next(
            (
                item
                for item in candidates
                if item.get("metadata", {}).get("layout") == layout
                and group_key(item) not in used_groups
            ),
            None,
        )
        if choice is not None and len(selected) < count:
            selected.append(choice)
            used_groups.add(group_key(choice))
    while len(selected) < count:
        remaining = [
            item
            for item in candidates
            if group_key(item) not in used_groups
        ]
        if not remaining:
            break
        choice = max(
            remaining,
            key=lambda item: (min(_distance(item, chosen) for chosen in selected), str(item["record_id"])),
        )
        selected.append(choice)
        used_groups.add(group_key(choice))
    return selected
