"""Persistent, local-only semantic–structural retrieval for scientific figures.

This module deliberately does not perform pixel-nearest-neighbour retrieval.
Method/intent text and explicit structural metadata dominate ranking; optional
image descriptors only provide a low-weight style tie-breaker.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
from typing import Any, Iterable, Mapping


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
TOKEN = re.compile(r"[a-zA-Z][a-zA-Z0-9_+-]{1,}")
VECTOR_DIMENSIONS = 256
DEFAULT_WEIGHTS = {"semantic": 0.58, "structure": 0.34, "visual": 0.08}


@dataclass(frozen=True)
class FigureRecord:
    record_id: str
    source_path: str
    source_group_id: str | None
    source_id: str | None
    text: str
    metadata: dict[str, Any]
    text_vector: list[float]
    visual_descriptor: dict[str, Any]


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN.findall(text)]


def _normalise(values: list[float]) -> list[float]:
    length = math.sqrt(sum(value * value for value in values))
    return values if length == 0 else [value / length for value in values]


def text_embedding(text: str) -> list[float]:
    """A deterministic local lexical embedding used when a neural encoder is absent."""
    values = [0.0] * VECTOR_DIMENSIONS
    for token in _tokens(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % VECTOR_DIMENSIONS
        values[index] += -1.0 if digest[4] & 1 else 1.0
    return _normalise(values)


def _cosine(left: Iterable[float], right: Iterable[float]) -> float:
    return max(0.0, sum(a * b for a, b in zip(left, right)))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sidecar_metadata(image_path: Path) -> dict[str, Any]:
    for candidate in (image_path.with_suffix(".json"), image_path.with_suffix(".metadata.json")):
        if candidate.exists():
            return _read_json(candidate)
    return {}


def _visual_descriptor(image_path: Path) -> dict[str, Any]:
    """Return small, interpretable style statistics; never preserve image pixels."""
    try:
        from PIL import Image, ImageStat  # type: ignore
    except ImportError:
        return {"available": False}
    try:
        with Image.open(image_path) as image:
            thumbnail = image.convert("RGB")
            width, height = thumbnail.size
            thumbnail.thumbnail((96, 96))
            stat = ImageStat.Stat(thumbnail)
            mean = [round(value / 255, 4) for value in stat.mean]
            deviation = [round(value / 255, 4) for value in stat.stddev]
            colors = thumbnail.getcolors(maxcolors=96 * 96) or []
            pixels = list(thumbnail.getdata())
            sample_width, sample_height = thumbnail.size
            luminance = [sum(pixel) / 3 for pixel in pixels]
            foreground = [value < 235 for value in luminance]
            foreground_ratio = sum(foreground) / len(foreground)
            horizontal_energy = sum(
                abs(luminance[row * sample_width + column] - luminance[row * sample_width + column - 1])
                for row in range(sample_height)
                for column in range(1, sample_width)
            ) / max(255 * sample_height * max(sample_width - 1, 1), 1)
            vertical_energy = sum(
                abs(luminance[row * sample_width + column] - luminance[(row - 1) * sample_width + column])
                for row in range(1, sample_height)
                for column in range(sample_width)
            ) / max(255 * max(sample_height - 1, 1) * sample_width, 1)
            occupied_cells = 0
            for grid_row in range(3):
                for grid_column in range(3):
                    start_y, end_y = grid_row * sample_height // 3, (grid_row + 1) * sample_height // 3
                    start_x, end_x = grid_column * sample_width // 3, (grid_column + 1) * sample_width // 3
                    cell = [
                        foreground[row * sample_width + column]
                        for row in range(start_y, end_y)
                        for column in range(start_x, end_x)
                    ]
                    if cell and sum(cell) / len(cell) >= 0.015:
                        occupied_cells += 1
            inferred_primitives = []
            if occupied_cells >= 2 and horizontal_energy >= 0.01 and vertical_energy >= 0.01:
                inferred_primitives.append("inferred_geometric_modules")
            if width / max(height, 1) >= 1.35 and occupied_cells >= 2:
                inferred_primitives.append("inferred_directional_flow")
            if occupied_cells >= 4:
                inferred_primitives.append("inferred_multi_region_grouping")
            return {
                "available": True,
                "aspect_ratio": round(width / max(height, 1), 4),
                "mean_rgb": mean,
                "std_rgb": deviation,
                "palette_size_capped": min(len(colors), 96),
                "foreground_ratio": round(foreground_ratio, 4),
                "horizontal_edge_energy": round(horizontal_energy, 4),
                "vertical_edge_energy": round(vertical_energy, 4),
                "occupied_grid_cells": occupied_cells,
                "inferred_primitives": inferred_primitives,
            }
    except (OSError, ValueError):
        return {"available": False}


def _minimal_structure(
    image_path: Path,
    metadata: Mapping[str, Any],
    descriptor: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    structure = {
        "figure_type": metadata.get("figure_type", "unknown"),
        "layout": metadata.get("layout", "unknown"),
        "topology": metadata.get("topology", []),
        "grouping": metadata.get("grouping", "unknown"),
        "text_density": metadata.get("text_density", "unknown"),
        "visual_primitives": metadata.get("visual_primitives", []),
    }
    descriptor = descriptor or _visual_descriptor(image_path)
    if structure["layout"] == "unknown" and descriptor.get("available"):
        ratio = descriptor["aspect_ratio"]
        structure["layout"] = "horizontal_flow" if ratio >= 1.45 else "vertical_stack" if ratio <= 0.72 else "balanced_canvas"
    for key in ("topology", "visual_primitives"):
        if isinstance(structure[key], str):
            structure[key] = [structure[key]]
        if not isinstance(structure[key], list):
            structure[key] = []
    for primitive in descriptor.get("inferred_primitives", []):
        if primitive not in structure["visual_primitives"]:
            structure["visual_primitives"].append(primitive)
    if structure["grouping"] == "unknown" and descriptor.get("available"):
        structure["grouping"] = "inferred_multi_region" if descriptor.get("occupied_grid_cells", 0) >= 4 else "inferred_sparse_region"
    if structure["text_density"] == "unknown" and descriptor.get("available"):
        ratio = descriptor.get("foreground_ratio", 0)
        structure["text_density"] = "inferred_dense" if ratio >= 0.26 else "inferred_light" if ratio <= 0.09 else "inferred_medium"
    return structure


def _manifest_records(dataset_root: Path) -> dict[str, dict[str, Any]]:
    manifest = dataset_root / "manifests/splits/geometry_source_v1/sources.jsonl"
    if not manifest.exists():
        return {}
    records: dict[str, dict[str, Any]] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        records[value["relative_path"]] = value
    return records


def _figurebench_texts(raw_root: Path) -> dict[str, str]:
    """Load development text when PyArrow is available; absence is a safe fallback."""
    parquet_path = raw_root / "data/dev.parquet"
    if not parquet_path.exists():
        return {}
    try:
        import pyarrow.parquet as pq  # type: ignore
    except ImportError:
        return {}
    texts: dict[str, str] = {}
    table = pq.read_table(parquet_path, columns=["messages", "images"])
    for row in table.to_pylist():
        pieces: list[str] = []
        for message in row.get("messages") or []:
            content = message.get("content", "") if isinstance(message, dict) else ""
            if isinstance(content, str) and message.get("role") == "user":
                pieces.append(content)
        text = "\n".join(pieces)[:24000]
        for relative_path in row.get("images") or []:
            texts[str(relative_path)] = text
    return texts


def _raw_root(dataset_root: Path) -> Path:
    """Accept either this project's `raw/` layout or a Hugging Face snapshot."""
    return dataset_root / "raw" if (dataset_root / "raw/images").exists() else dataset_root


def _upstream_development_manifest(relative_path: str) -> dict[str, str] | None:
    """Create a safe minimal partition for a plain upstream FigureBench snapshot."""
    parts = Path(relative_path).parts
    if len(parts) < 3 or parts[0] != "images":
        return None
    source_id = parts[1]
    return {
        "partition": "upstream_development_only",
        "source_id": source_id,
        "source_group_id": f"upstream_{source_id}",
    }


def _iter_records(dataset_root: Path) -> Iterable[FigureRecord]:
    raw_root = _raw_root(dataset_root)
    manifests = _manifest_records(dataset_root)
    figurebench_texts = _figurebench_texts(raw_root)
    for image_path in sorted(raw_root.rglob("*")):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        relative_path = image_path.relative_to(raw_root).as_posix()
        manifest = manifests.get(relative_path, {})
        if manifests and manifest.get("partition") != "extraction_library_source":
            continue
        if not manifests:
            manifest = _upstream_development_manifest(relative_path)
            if manifest is None:
                continue
        metadata = _sidecar_metadata(image_path)
        visual_descriptor = _visual_descriptor(image_path)
        structure = _minimal_structure(image_path, metadata, visual_descriptor)
        metadata = {**metadata, **structure, "partition": manifest.get("partition", "unpartitioned")}
        text = " ".join(
            value
            for value in (
                str(metadata.get("caption", "")),
                str(metadata.get("domain", "")),
                figurebench_texts.get(relative_path, ""),
                image_path.stem.replace("_", " "),
            )
            if value
        )
        record_id = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:20]
        yield FigureRecord(
            record_id=record_id,
            source_path=str(image_path),
            source_group_id=manifest.get("source_group_id"),
            source_id=manifest.get("source_id"),
            text=text,
            metadata=metadata,
            text_vector=text_embedding(text),
            visual_descriptor=visual_descriptor,
        )


def build_index(dataset_root: str | Path, index_path: str | Path) -> dict[str, int]:
    """Build an SQLite index from a FigureBench root or a sidecar-labelled fixture."""
    dataset_root, index_path = Path(dataset_root), Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(index_path)
    with connection:
        connection.execute("DROP TABLE IF EXISTS figures")
        connection.execute(
            "CREATE TABLE figures (record_id TEXT PRIMARY KEY, source_path TEXT NOT NULL, source_group_id TEXT, source_id TEXT, text TEXT NOT NULL, metadata_json TEXT NOT NULL, text_vector_json TEXT NOT NULL, visual_json TEXT NOT NULL)"
        )
        count = 0
        is_figurebench = (dataset_root / "raw/images").exists() or (dataset_root / "images").exists()
        records = _iter_records(dataset_root) if is_figurebench else _iter_fixture_records(dataset_root)
        for record in records:
            connection.execute(
                "INSERT INTO figures VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record.record_id,
                    record.source_path,
                    record.source_group_id,
                    record.source_id,
                    record.text,
                    json.dumps(record.metadata, ensure_ascii=False, sort_keys=True),
                    json.dumps(record.text_vector),
                    json.dumps(record.visual_descriptor, sort_keys=True),
                ),
            )
            count += 1
    connection.close()
    return {"indexed": count}


def _iter_fixture_records(dataset_root: Path) -> Iterable[FigureRecord]:
    for image_path in sorted(dataset_root.rglob("*")):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        metadata = _sidecar_metadata(image_path)
        visual_descriptor = _visual_descriptor(image_path)
        metadata = {**metadata, **_minimal_structure(image_path, metadata, visual_descriptor), "partition": "fixture"}
        text = " ".join(str(metadata.get(key, "")) for key in ("caption", "domain"))
        yield FigureRecord(
            record_id=hashlib.sha256(str(image_path).encode()).hexdigest()[:20],
            source_path=str(image_path),
            source_group_id=None,
            source_id=None,
            text=text,
            metadata=metadata,
            text_vector=text_embedding(text),
            visual_descriptor=visual_descriptor,
        )


def _structure_score(query: Mapping[str, Any], candidate: Mapping[str, Any]) -> float:
    parts: list[float] = []
    for key in ("figure_type", "layout", "grouping", "text_density"):
        expected = query.get(key)
        if expected and expected != "unknown":
            parts.append(1.0 if expected == candidate.get(key) else 0.0)
    for key in ("topology", "visual_primitives"):
        expected = {str(value).lower() for value in query.get(key, [])}
        observed = {str(value).lower() for value in candidate.get(key, [])}
        if expected:
            parts.append(len(expected & observed) / len(expected))
    return sum(parts) / len(parts) if parts else 0.0


def _visual_score(query: Mapping[str, Any] | None, candidate: Mapping[str, Any]) -> float:
    if not query or not query.get("available") or not candidate.get("available"):
        return 0.0
    left, right = query.get("mean_rgb", []), candidate.get("mean_rgb", [])
    if len(left) != 3 or len(right) != 3:
        return 0.0
    distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right))) / math.sqrt(3)
    return max(0.0, 1.0 - distance)


def query_index(
    index_path: str | Path,
    methodology: str,
    figure_intent: str,
    requested_structure: Mapping[str, Any],
    top_k: int = 4,
    user_reference_image: str | Path | None = None,
    exclude_source_groups: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Return compact local references, diversified by source group."""
    query_vector = text_embedding(methodology + "\n" + figure_intent)
    query_visual = _visual_descriptor(Path(user_reference_image)) if user_reference_image else None
    connection = sqlite3.connect(index_path)
    rows = connection.execute("SELECT * FROM figures").fetchall()
    connection.close()
    ranked = []
    excluded = exclude_source_groups or set()
    for row in rows:
        record_id, source_path, group_id, source_id, text, metadata_json, vector_json, visual_json = row
        if group_id and group_id in excluded:
            continue
        metadata = json.loads(metadata_json)
        scores = {
            "semantic": _cosine(query_vector, json.loads(vector_json)),
            "structure": _structure_score(requested_structure, metadata),
            "visual": _visual_score(query_visual, json.loads(visual_json)),
        }
        total = sum(DEFAULT_WEIGHTS[key] * scores[key] for key in DEFAULT_WEIGHTS)
        ranked.append((total, record_id, source_path, group_id, source_id, metadata, scores))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    seen_groups: set[str] = set()
    results = []
    for total, record_id, source_path, group_id, source_id, metadata, scores in ranked:
        dedupe_key = group_id or record_id
        if dedupe_key in seen_groups:
            continue
        seen_groups.add(dedupe_key)
        results.append(
            {
                "record_id": record_id,
                "source_path": source_path,
                "source_group_id": group_id,
                "source_id": source_id,
                "structure_summary": {key: metadata.get(key) for key in ("figure_type", "layout", "topology", "grouping", "text_density", "visual_primitives")},
                "scores": {key: round(value, 4) for key, value in scores.items()},
                "score": round(total, 4),
            }
        )
        if len(results) >= top_k:
            break
    return results


def derive_geometry_lexicon(index_path: str | Path) -> dict[str, Any]:
    """Aggregate reusable *geometry grammar*, never image content or pixels.

    The output is intentionally a compact set of proportions and primitive
    families that can guide a fresh rendition without supplying a reference
    image to copy.
    """
    connection = sqlite3.connect(index_path)
    rows = connection.execute("SELECT metadata_json, visual_json FROM figures").fetchall()
    connection.close()
    layouts: Counter[str] = Counter()
    figure_types: Counter[str] = Counter()
    primitives: Counter[str] = Counter()
    aspect_ratios: list[float] = []
    visual_ready = 0
    for metadata_json, visual_json in rows:
        metadata, visual = json.loads(metadata_json), json.loads(visual_json)
        layouts[str(metadata.get("layout", "unknown"))] += 1
        figure_types[str(metadata.get("figure_type", "unknown"))] += 1
        primitives.update(str(item) for item in metadata.get("visual_primitives", []))
        if visual.get("available"):
            visual_ready += 1
            aspect_ratios.append(float(visual.get("aspect_ratio", 1.0)))
    family_by_layout = {
        "horizontal_flow": "sequential-band composition",
        "vertical_stack": "hierarchical-stack composition",
        "balanced_canvas": "balanced multi-region composition",
        "grid": "panel-grid composition",
    }
    return {
        "indexed_figures": len(rows),
        "layout_distribution": dict(layouts.most_common()),
        "figure_type_distribution": dict(figure_types.most_common()),
        "primitive_distribution": dict(primitives.most_common()),
        "composition_families": [
            family_by_layout.get(layout, "unclassified composition")
            for layout, _ in layouts.most_common()
        ],
        "mean_aspect_ratio": round(sum(aspect_ratios) / len(aspect_ratios), 4) if aspect_ratios else None,
        "visual_descriptor_coverage": round(visual_ready / len(rows), 4) if rows else 0.0,
        "interpretation": "Aggregate geometry/style statistics only; not a library of images to reproduce.",
    }


def build_iteration_brief(
    generation_contract: Mapping[str, Any],
    geometry_lexicon: Mapping[str, Any],
) -> dict[str, Any]:
    """Create a one-pass refinement brief with explicit anti-drift boundaries."""
    protected = {
        key: generation_contract.get(key)
        for key in ("modules", "arrows", "labels", "primary_layout")
        if key in generation_contract
    }
    return {
        "phase": "single FigureBench-informed refinement after first raster draft",
        "protected_generation_contract": protected,
        "forbidden_changes": [
            "module semantics",
            "arrow relations",
            "main reading order",
            "label content",
            "primary layout contract",
        ],
        "allowed_changes": [
            "container geometry",
            "corner and silhouette family",
            "grouping enclosure treatment",
            "arrow stroke and endpoint styling",
            "palette relationships",
            "scientific asset rendering",
        ],
        "geometry_grammar": {
            "composition_families": geometry_lexicon.get("composition_families", []),
            "primitive_distribution": geometry_lexicon.get("primitive_distribution", {}),
            "mean_aspect_ratio": geometry_lexicon.get("mean_aspect_ratio"),
        },
        "anti_copy_rule": "Use aggregate geometry grammar to make a new composition; do not trace, imitate, or preserve any retrieved figure's distinctive arrangement.",
    }


def build_svg_verification_brief(
    first_draft_png: str,
    generation_contract: Mapping[str, Any],
    geometry_lexicon: Mapping[str, Any],
    inspection: Mapping[str, Any],
) -> dict[str, Any]:
    """Brief an optional faithful editable-SVG verification of a first PNG.

    The first generated PNG remains the only creative figure. This brief may be
    used only by a converter able to transcribe that actual PNG into editable
    SVG layers. It must never synthesize a new SVG from the original contract.
    """
    issues = inspection.get("issues", [])
    if not isinstance(issues, list):
        issues = []
    repair_targets = [
        str(issue["kind"])
        for issue in issues
        if isinstance(issue, Mapping) and isinstance(issue.get("kind"), str)
    ]
    verification_truth = {
        key: generation_contract.get(key)
        for key in ("canvas", "title", "modules", "arrows", "labels", "primary_layout")
        if key in generation_contract
    }
    colour_contract = generation_contract.get("colour_contract", {})
    if not isinstance(colour_contract, Mapping):
        colour_contract = {}
    source = colour_contract.get("source", {})
    if not isinstance(source, Mapping):
        source = {}
    allowed_hex = colour_contract.get("allowed_hex", [])
    if not isinstance(allowed_hex, list):
        allowed_hex = []
    source_kind = source.get("kind")
    palette_id = source.get("palette_id")
    if source_kind == "approved_library":
        source_is_identified = isinstance(palette_id, str) and bool(palette_id)
    elif source_kind == "cross_domain_svg":
        source_is_identified = bool(source.get("source_domains"))
    else:
        source_is_identified = False
    if not source_is_identified or not allowed_hex:
        raise ValueError("A semantic SVG reconstruction requires one identified frozen palette source and its allowed HEX group.")
    return {
        "phase": "optional faithful PNG-to-SVG verification",
        "raster_source": first_draft_png,
        "verification_truth": verification_truth,
        "inspection_targets": list(dict.fromkeys(repair_targets)),
        "palette_policy": {
            "palette_id": palette_id,
            "source_kind": source_kind,
            "allowed_hex": allowed_hex,
            "rule": "Use exactly this one frozen group. Do not mix groups, infer missing role colours, or invent fallback HEX values.",
        },
        "conversion_rules": [
            "faithfully transcribe the actual first PNG, including all meaningful modules, connections, assets, and spatial relations.",
            "preserve every required label as editable text and preserve its placement relative to the PNG.",
            "preserve editable layers and the frozen one-group palette without introducing colours or moving semantic content.",
            "do not create a new SVG",
            "do not use the topology contract as a substitute for observing the first PNG.",
        ],
        "preservation_rules": [
            "module semantics",
            "arrow relations",
            "main reading order",
            "label content",
            "primary layout contract",
            "palette-group mixing or fallback colours",
            "newly authored geometry presented as a conversion",
        ],
        "geometry_grammar": {
            "composition_families": geometry_lexicon.get("composition_families", []),
            "primitive_distribution": geometry_lexicon.get("primitive_distribution", {}),
        },
        "on_conversion_failure": "skip_svg_verification",
        "delivery_rule": "Return the original first PNG when a converter cannot preserve semantic structure, editable text, layer editability, or palette fidelity.",
        "anti_copy_rule": "FigureBench is aggregate grammar only; this verification transcribes the generated first PNG, never a retrieved paper figure.",
    }


def export_public_bundle(index_path: str | Path, bundle_path: str | Path) -> dict[str, int]:
    """Export a deployable retrieval payload without raw images, paths, or corpus text."""
    connection = sqlite3.connect(index_path)
    rows = connection.execute(
        "SELECT record_id, source_group_id, source_id, metadata_json, text_vector_json, visual_json FROM figures"
    ).fetchall()
    connection.close()
    bundle_path = Path(bundle_path)
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    entries = [
        {
            "bundle_format": "scientific-figure-rag-public-v1",
            "license": "CC-BY-4.0",
            "notice": "No raw FigureBench images, local paths, or corpus text are included.",
        }
    ]
    for record_id, group_id, source_id, metadata_json, vector_json, visual_json in rows:
        metadata = json.loads(metadata_json)
        entries.append(
            {
                "record_id": record_id,
                "source_group_id": group_id,
                "source_id": source_id,
                "structure_summary": {
                    key: metadata.get(key)
                    for key in ("figure_type", "layout", "topology", "grouping", "text_density", "visual_primitives")
                },
                "text_embedding": json.loads(vector_json),
                "visual_style_descriptor": json.loads(visual_json),
            }
        )
    bundle_path.write_text(
        "\n".join(json.dumps(entry, ensure_ascii=False, sort_keys=True) for entry in entries) + "\n",
        encoding="utf-8",
    )
    return {"exported": len(rows)}
