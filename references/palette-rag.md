# Palette RAG

`palette-library.json` is an image-free library of curated scientific-figure colour groups. Each record has only a stable id, tags, colour roles, HEX values, and RGB values. It must not store screenshots, thumbnails, source image paths, image URLs, image embeddings, or copied figure content.

## Allowed colour sources

Each render chooses exactly one source:

1. one group from this approved library; or
2. one ephemeral group extracted from an aesthetically strong web SVG that is unrelated to the brief's domain.

The high-aesthetic **domain** references are never a colour source. Their job is topology, component conventions, and novelty evidence. A user reference image can guide style, but cannot add colours unless it separately passes the same unrelated-SVG rule.

For a web-SVG group, record only its declared source domains plus role-labelled HEX/RGB values in the current run's planning JSON. Reject it when any source-domain label overlaps a brief-domain label. Do not retain its image, URL, thumbnail, embedding, or a reusable palette record. Its purpose is colour transfer without copying the visual identity of a semantically related figure.

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

The result contains a few approved candidates. Choose one group, not a mix of groups.

## Color Planning contract

During the existing Scientific Topology Planning pass, emit a compact plan with exactly one source:

```json
{
  "brief_domains": ["biomedical"],
  "source": {"kind": "approved_library", "palette_id": "biomedical-contrast-01"},
  "assignments": {
    "canvas": "#E7EFFA",
    "ink": "#14517C",
    "primary_module": "#2F7FC1",
    "novelty_accent": "#D8383A"
  }
}
```

Compile before rendering:

```bash
python scripts/figurebench_rag.py colour-contract --plan-json colour-plan.json
```

The compiler freezes the source and returns `allowed_hex`. Every authored SVG fill and stroke must use only exact HEX values from `allowed_hex`; the raster pass cannot add, shift, blend, or activate any other colour. This is a planning field, not a separate model call. Render the plan into the SVG contract and preserve it during the final raster pass. Do not use colour as the only encoding of a category; retain labels, geometry, or patterns where distinction matters.

## Maintaining the library

Add a new group only after extracting explicit colour values from an approved example. Keep the source example out of the repository. Assign each value a role relative to that group; do not infer a universal semantic meaning from a hue. Retain distinct groups even when they share a colour.
