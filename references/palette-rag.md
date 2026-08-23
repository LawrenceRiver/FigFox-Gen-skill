# Palette RAG

`palette-library.json` is an image-free library of curated scientific-figure colour groups. Each record has only a stable id, tags, colour roles, HEX values, and RGB values. It must not store screenshots, thumbnails, source image paths, image URLs, image embeddings, or copied figure content.

## Use

Provide a tiny planning query, rather than an image. Tags describe the domain or figure purpose; required roles describe what the figure needs.

```json
{
  "tags": ["biomedical", "contrast", "mechanism"],
  "required_roles": ["ink", "primary", "accent"]
}
```

```bash
python scripts/figurebench_rag.py palettes --planning-json colour-plan.json --top-k 3
```

The result contains a few independent palette groups. It is a candidate set, not an instruction to use every returned colour.

## Color Planning contract

During the existing Scientific Topology Planning pass, choose at most three groups and emit a compact plan:

```json
{
  "canvas": "#EDF7F8",
  "ink": "#14517C",
  "surface": "#E7EFFA",
  "semantic_modules": {"input": "#2F7FC1", "comparison": "#96C37D"},
  "novelty_accent": "#D8383A",
  "restrictions": ["accent only for the core claim", "text and arrows retain high contrast"]
}
```

This is a planning field, not a separate model call. Render the plan into the SVG contract and preserve it during the final raster pass. Do not use colour as the only encoding of a category; retain labels, geometry, or patterns where distinction matters.

## Maintaining the library

Add a new group only after extracting explicit colour values from an approved example. Keep the source example out of the repository. Assign each value a role relative to that group; do not infer a universal semantic meaning from a hue. Retain distinct groups even when they share a colour.
