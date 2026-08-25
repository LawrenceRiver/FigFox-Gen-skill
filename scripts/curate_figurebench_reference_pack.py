#!/usr/bin/env python3
"""Maintainer tools for a reviewed, development-only FigureBench reference pack."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scientific_figure_workflow.reference_pack import INDEX_FIELDS, validate_reference_pack  # noqa: E402


FIGUREBENCH_REPOSITORY = "WestlakeNLP/FigureBench"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}
SELECTION_FIELDS = (INDEX_FIELDS - {"id", "file", "partition"}) | {
    "rights_reviewed",
    "human_editability_reviewed",
    "source_path",
}


def _load_json_object(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"missing JSON file: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}: {error.msg}") from error
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _required_string(record: Mapping[str, Any], field: str, location: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires non-empty {field}")
    return value.strip()


def _image_root(dataset: Path) -> Path:
    image_root = (dataset / "images").resolve()
    if not image_root.is_dir():
        raise ValueError(f"FigureBench development image root not found: {image_root}")
    return image_root


def _safe_source_path(dataset: Path, source_path: str, location: str) -> Path:
    requested = Path(source_path)
    if requested.is_absolute():
        raise ValueError(f"{location} source_path must be relative")
    image_root = _image_root(dataset)
    candidate = (dataset / requested).resolve()
    if not candidate.is_relative_to(image_root):
        raise ValueError(f"{location} source_path must remain under the development images root")
    if not candidate.is_file():
        raise ValueError(f"{location} source image does not exist: {source_path}")
    return candidate


def _thumbnail(image_path: Path, thumbnail_path: Path, max_edge: int) -> None:
    from PIL import Image

    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as image:
        normalized = image.convert("RGB")
        normalized.thumbnail((max_edge, max_edge))
        normalized.save(thumbnail_path, format="PNG", optimize=True)


def prepare(dataset: Path, output: Path, manifest: Path) -> dict[str, Any]:
    """Make 1200px review thumbnails from local FigureBench *development* images."""

    dataset = dataset.resolve()
    image_root = _image_root(dataset)
    candidates: list[dict[str, Any]] = []
    image_paths = sorted(
        path for path in image_root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    for position, source in enumerate(image_paths, start=1):
        relative = source.relative_to(dataset).as_posix()
        thumbnail = Path("thumbnails") / f"{position:04d}.png"
        _thumbnail(source, output / thumbnail, 1200)
        candidates.append(
            {
                "id": f"candidate-{position:04d}",
                "source_path": relative,
                "thumbnail": thumbnail.as_posix(),
                "source_id": source.parent.name,
            }
        )
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(
            {
                "format": "figurebench-development-review-v1",
                "dataset_root": str(dataset),
                "purpose": "Human visual review for reusable geometry and layout; not a tracing library.",
                "candidates": candidates,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"candidates": len(candidates), "output": str(output), "manifest": str(manifest)}


def download(destination: Path) -> dict[str, Any]:
    """Download only the FigureBench development source and image files."""

    try:
        from huggingface_hub import snapshot_download
    except ImportError as error:
        raise RuntimeError("Install requirements-maintainer.txt for FigureBench download support.") from error
    destination.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=FIGUREBENCH_REPOSITORY,
        repo_type="dataset",
        local_dir=str(destination),
        allow_patterns=["README.md", "data/dev.parquet", "images/*", "images/**/*"],
    )
    forbidden = [
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file() and ("test_images" in path.parts or path.relative_to(destination).as_posix() == "data/test.parquet")
    ]
    if forbidden:
        raise ValueError(f"download must not include FigureBench test inputs: {', '.join(forbidden)}")
    return {"destination": str(destination), "downloaded_development_only": True}


def _selection_records(selection_path: Path) -> list[Mapping[str, Any]]:
    value = _load_json_object(selection_path)
    selections = value.get("selections")
    if not isinstance(selections, list):
        raise ValueError("selection requires a selections list")
    if len(selections) != 30:
        raise ValueError("selection requires exactly 30 reviewed records")
    if not all(isinstance(item, Mapping) for item in selections):
        raise ValueError("selection records must be objects")
    return selections


def _index_record(selection: Mapping[str, Any], dataset: Path, position: int) -> tuple[dict[str, Any], Path]:
    location = f"selection selections[{position - 1}]"
    if set(selection) != SELECTION_FIELDS:
        raise ValueError(f"{location} must contain exactly the selection schema fields")
    if selection.get("rights_reviewed") is not True:
        raise ValueError(f"{location} requires rights_reviewed true")
    if selection.get("human_editability_reviewed") is not True:
        raise ValueError(f"{location} requires human_editability_reviewed true")
    source_path = _required_string(selection, "source_path", location)
    source = _safe_source_path(dataset, source_path, location)
    record = {field: selection[field] for field in INDEX_FIELDS - {"id", "file", "partition"}}
    record["id"] = f"reference-{position:03d}"
    record["file"] = f"reference-{position:03d}.png"
    record["partition"] = "dev"
    return record, source


def materialize(dataset: Path, selection_path: Path, output: Path) -> dict[str, Any]:
    """Normalize 30 reviewed source images into the distributable pack."""

    from PIL import Image

    dataset = dataset.resolve()
    selections = _selection_records(selection_path)
    records_and_sources = [_index_record(selection, dataset, position) for position, selection in enumerate(selections, start=1)]
    source_paths = [source.resolve() for _, source in records_and_sources]
    if len(source_paths) != len(set(source_paths)):
        raise ValueError("selection source_path values must be unique; duplicated images are not allowed")

    output.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for record, source in records_and_sources:
        destination = output / record["file"]
        with Image.open(source) as image:
            normalized = image.convert("RGB")
            normalized.thumbnail((1600, 1600))
            normalized.save(destination, format="PNG", optimize=True)
        records.append(record)
    (output / "index.json").write_text(
        json.dumps({"format": "figurebench-reference-pack-v1", "references": records}, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = validate_reference_pack(output)
    pack_bytes = sum(path.stat().st_size for path in output.glob("*.png")) + (output / "index.json").stat().st_size
    return {**summary, "bytes": pack_bytes, "output": str(output)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    download_parser = subcommands.add_parser("download", help="download development-only FigureBench files")
    download_parser.add_argument("--destination", required=True, type=Path)
    download_parser.add_argument("--accept-figurebench-license", action="store_true")

    prepare_parser = subcommands.add_parser("prepare", help="make review thumbnails from images/")
    prepare_parser.add_argument("--dataset", required=True, type=Path)
    prepare_parser.add_argument("--output", required=True, type=Path)
    prepare_parser.add_argument("--manifest", required=True, type=Path)

    materialize_parser = subcommands.add_parser("materialize", help="write the bundled reference pack")
    materialize_parser.add_argument("--dataset", required=True, type=Path)
    materialize_parser.add_argument("--selection", required=True, type=Path)
    materialize_parser.add_argument("--output", required=True, type=Path)

    arguments = parser.parse_args()
    try:
        if arguments.command == "download":
            if not arguments.accept_figurebench_license:
                parser.error("download requires --accept-figurebench-license after reviewing FigureBench terms")
            result = download(arguments.destination)
        elif arguments.command == "prepare":
            result = prepare(arguments.dataset, arguments.output, arguments.manifest)
        else:
            result = materialize(arguments.dataset, arguments.selection, arguments.output)
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
