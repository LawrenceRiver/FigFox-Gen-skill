#!/usr/bin/env python3
"""Local-only FigureBench RAG commands for the scientific figure Skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scientific_figure_rag.index import (  # noqa: E402
    build_index,
    build_iteration_brief,
    derive_geometry_lexicon,
    export_public_bundle,
    query_index,
)
from scientific_figure_rag.palette import compile_colour_contract, select_palettes  # noqa: E402


def _write_json(path: str | None, value: object) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path:
        Path(path).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


def _json_file(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    index = commands.add_parser("index", help="Index local FigureBench library sources only")
    index.add_argument("--dataset", required=True)
    index.add_argument("--index", required=True)

    lexicon = commands.add_parser("lexicon", help="Extract aggregate geometry grammar")
    lexicon.add_argument("--index", required=True)
    lexicon.add_argument("--output")

    query = commands.add_parser("query", help="Return compact semantic–structural references")
    query.add_argument("--index", required=True)
    query.add_argument("--methodology", required=True)
    query.add_argument("--intent", required=True)
    query.add_argument("--structure-json", required=True)
    query.add_argument("--top-k", type=int, default=4)
    query.add_argument("--user-reference-image")
    query.add_argument("--output")

    refine = commands.add_parser("refinement-brief", help="Make a one-pass non-drifting refinement brief")
    refine.add_argument("--generation-contract-json", required=True)
    refine.add_argument("--lexicon-json", required=True)
    refine.add_argument("--output")

    public = commands.add_parser("export-public", help="Export a safe, image-free deployment bundle")
    public.add_argument("--index", required=True)
    public.add_argument("--output", required=True)

    palettes = commands.add_parser("palettes", help="Select image-free scientific palette groups")
    palettes.add_argument("--planning-json", required=True)
    palettes.add_argument("--top-k", type=int, default=3)

    colour_contract = commands.add_parser(
        "colour-contract", help="Freeze one approved or cross-domain SVG palette for a render"
    )
    colour_contract.add_argument("--plan-json", required=True)
    colour_contract.add_argument("--output")

    arguments = parser.parse_args()
    if arguments.command == "index":
        _write_json(None, build_index(arguments.dataset, arguments.index))
    elif arguments.command == "lexicon":
        _write_json(arguments.output, derive_geometry_lexicon(arguments.index))
    elif arguments.command == "query":
        _write_json(
            arguments.output,
            query_index(
                arguments.index,
                arguments.methodology,
                arguments.intent,
                _json_file(arguments.structure_json),
                arguments.top_k,
                arguments.user_reference_image,
            ),
        )
    elif arguments.command == "refinement-brief":
        _write_json(
            arguments.output,
            build_iteration_brief(
                _json_file(arguments.generation_contract_json),
                _json_file(arguments.lexicon_json),
            ),
        )
    elif arguments.command == "export-public":
        _write_json(None, export_public_bundle(arguments.index, arguments.output))
    elif arguments.command == "palettes":
        _write_json(None, select_palettes(_json_file(arguments.planning_json), arguments.top_k))
    elif arguments.command == "colour-contract":
        _write_json(arguments.output, compile_colour_contract(_json_file(arguments.plan_json)))


if __name__ == "__main__":
    main()
