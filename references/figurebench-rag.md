# FigureBench Semantic–Structural RAG

## Local source and permitted partition

FigureBench is maintainer-local CC-BY-4.0 tooling and is never bundled with this Skill. Ordinary users must not be asked to download the multi-GB corpus. A maintainer who already has a lawful local copy may use it to maintain an approved lightweight geometry reference pack or to evaluate the retrieval pipeline.

When an existing `manifests/splits/geometry_source_v1/` is present, use only `extraction_library_source`; this project's stricter split contains 2,400 development images and excludes validation, holdout, and official test sources. A plain upstream Hugging Face download has no such manifest: index only its `images/` development directory, never `test_images/`, and deduplicate results by paper source ID.

## Index design

The local SQLite index retains only what retrieval needs:

- semantic text descriptor from FigureBench text plus any available caption/domain;
- structured metadata: figure type, topology, layout, grouping, text density, and visual primitives;
- small visual style descriptor (aspect ratio, colour moments, palette-size estimate) as a low-weight tie-breaker; and
- local source/group identifiers for diversity and attribution.

It is not a Pixel RAG. Ranking weights are semantic 0.58, structure 0.34, visual style 0.08. A local deterministic text embedding is the portability fallback; replace it with a local CLIP/SigLIP/text embedding backend only if it preserves the same query priority and keeps all corpus images local.

When FigureBench has no explicit structural label, the helper derives conservative minimal metadata from verified sidecars and image geometry. Treat inferred labels as hints, not facts. The geometry lexicon aggregates distributions; it does not retain image pixels or invite copying.

## Commands

Install the optional local RAG dependencies:

```bash
python -m pip install -r requirements-rag.txt
```

For maintainers with an existing local FigureBench root only:

```bash
python scripts/setup_figurebench_rag.py --dataset /path/to/FigureBench
```

The command writes the SQLite index and geometry lexicon to a maintainer-local cache. It does not upload images or text. Do not publish or document a full-dataset download as an installation step for this Skill.

For manual paths, set these values to your own cache paths:

```bash
ROOT="/path/to/GenLikeScientificSVG"
INDEX="$HOME/.cache/genlike-scientific-svg/figurebench-rag/figurebench.sqlite"

python "$ROOT/scripts/figurebench_rag.py" lexicon --index "$INDEX" --output "$ROOT/geometry-lexicon.json"
```

Create a small JSON file for the planned structure, then query top-k references:

```bash
python "$ROOT/scripts/figurebench_rag.py" query \
  --index "$INDEX" \
  --methodology "..." \
  --intent "Explain the method's causal pipeline and central contribution." \
  --structure-json "$ROOT/local/requested-structure.json" \
  --top-k 4 \
  --output "$ROOT/local/references.json"
```

Use the Image Generation Contract and geometry lexicon to make the single constrained refinement brief after direct image generation:

```bash
python "$ROOT/scripts/figurebench_rag.py" refinement-brief \
  --generation-contract-json "$ROOT/local/image-generation-contract.json" \
  --lexicon-json "$ROOT/local/geometry-lexicon.json" \
  --output "$ROOT/local/refinement-brief.json"
```

## Deployment boundary

Do not upload `raw/`, the SQLite index containing local paths/text, or FigureBench images. A future deployment may serve only the output of:

```bash
python "$ROOT/scripts/figurebench_rag.py" export-public \
  --index "$INDEX" --output "$ROOT/local/figurebench-public.jsonl"
```

That JSONL omits images, paths, and corpus text. It contains embeddings, compact structure summaries, IDs, and CC-BY-4.0 notice. Confirm FigureBench and individual source terms plus deployment authority before hosting it.
