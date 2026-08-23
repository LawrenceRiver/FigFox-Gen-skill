#!/usr/bin/env python3
"""Prepare a portable local FigureBench RAG cache for GenLikeScientificSVG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scientific_figure_rag.index import build_index, derive_geometry_lexicon  # noqa: E402


def _is_figurebench_root(path: Path) -> bool:
    return (path / "images").exists() or (path / "raw/images").exists()


def _download_figurebench(destination: Path) -> Path:
    try:
        from huggingface_hub import snapshot_download  # type: ignore
    except ImportError as error:
        raise RuntimeError(
            "Install requirements-rag.txt before downloading FigureBench."
        ) from error
    snapshot_download(
        repo_id="WestlakeNLP/FigureBench",
        repo_type="dataset",
        local_dir=str(destination),
        allow_patterns=["README.md", "data/*", "images/*", "images/**/*"],
    )
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--dataset", help="Existing FigureBench root (local only)")
    source.add_argument("--download", action="store_true", help="Download the public FigureBench development files")
    parser.add_argument(
        "--cache-dir",
        default=str(Path.home() / ".cache" / "genlike-scientific-svg" / "figurebench-rag"),
        help="Directory for the local index and lexicon",
    )
    parser.add_argument("--accept-figurebench-license", action="store_true")
    arguments = parser.parse_args()

    cache_dir = Path(arguments.cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    if arguments.dataset:
        dataset_root = Path(arguments.dataset).expanduser().resolve()
        source_mode = "existing_local_dataset"
    else:
        if not arguments.accept_figurebench_license:
            parser.error("--download requires --accept-figurebench-license (CC-BY-4.0)")
        dataset_root = _download_figurebench(cache_dir / "figurebench-source")
        source_mode = "downloaded_public_development_dataset"
    if not _is_figurebench_root(dataset_root):
        parser.error(f"Not a FigureBench root: {dataset_root}")

    index_path = cache_dir / "figurebench.sqlite"
    lexicon_path = cache_dir / "geometry-lexicon.json"
    summary = build_index(dataset_root, index_path)
    lexicon_path.write_text(
        json.dumps(derive_geometry_lexicon(index_path), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "source_mode": source_mode,
                "dataset_root": str(dataset_root),
                "index": str(index_path),
                "geometry_lexicon": str(lexicon_path),
                **summary,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
