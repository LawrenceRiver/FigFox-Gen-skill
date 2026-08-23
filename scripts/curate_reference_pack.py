#!/usr/bin/env python3
"""Create a local, diverse FigureBench reference-pack preview for human review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scientific_figure_rag.curation import select_diverse_records  # noqa: E402


def _records(index_path: Path) -> list[dict]:
    with sqlite3.connect(index_path) as connection:
        rows = connection.execute(
            "SELECT record_id, source_path, source_group_id, source_id, metadata_json, visual_json FROM figures"
        ).fetchall()
    return [
        {
            "record_id": record_id,
            "source_path": source_path,
            "source_group_id": group_id,
            "source_id": source_id,
            "metadata": json.loads(metadata_json),
            "visual": json.loads(visual_json),
        }
        for record_id, source_path, group_id, source_id, metadata_json, visual_json in rows
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--max-edge", type=int, default=1024)
    arguments = parser.parse_args()

    try:
        from PIL import Image
    except ImportError as error:
        raise RuntimeError("Install Pillow from requirements-rag.txt to create thumbnails.") from error
    output = Path(arguments.output)
    image_dir = output / "thumbnails"
    image_dir.mkdir(parents=True, exist_ok=True)
    selected = select_diverse_records(_records(Path(arguments.index)), arguments.count)
    references = []
    for position, record in enumerate(selected, start=1):
        thumbnail_name = f"{position:02d}-{record['record_id']}.png"
        with Image.open(record["source_path"]) as image:
            thumbnail = image.convert("RGB")
            thumbnail.thumbnail((arguments.max_edge, arguments.max_edge))
            thumbnail.save(image_dir / thumbnail_name, format="PNG", optimize=True)
        metadata = record["metadata"]
        references.append(
            {
                "id": record["record_id"],
                "thumbnail": f"thumbnails/{thumbnail_name}",
                "source_id": record["source_id"],
                "source_group_id": record["source_group_id"],
                "attribution": "FigureBench / WestlakeNLP, CC-BY-4.0; verify original figure rights before public redistribution.",
                "structure_summary": {
                    key: metadata.get(key)
                    for key in ("figure_type", "layout", "grouping", "text_density", "visual_primitives")
                },
            }
        )
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "format": "genlike-scientific-svg-reference-pack-v1",
                "purpose": "Human-reviewed local geometry and style reference pack; not a tracing library.",
                "references": references,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"curated": len(references), "output": str(output)}))


if __name__ == "__main__":
    main()
