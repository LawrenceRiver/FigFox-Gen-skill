# Evidence-Guided Two-Pass Figure Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Skill around three evidence contexts, a bundled 30-image FigureBench reference pack, PNG1-to-SVG1 diagnosis, and a diagnosis-guided final PNG2.

**Architecture:** Model judgment stays in `SKILL.md`: scholarly search, VLM comparison, planning, image generation, direct base-model SVG transcription, and diagnosis. A new `scientific_figure_workflow` Python package deterministically validates artifacts, ranks the bundled references, executes model-provided crops, enforces one palette, compiles Prompt 1 and Prompt 2 bundles, validates/renders SVG1, and verifies the complete run. The old aggregate-only RAG and optional-SVG workflow are removed after the replacement passes tests.

**Tech Stack:** Python 3.11+, standard-library JSON/XML/path handling, Pillow, defusedxml, CairoSVG, unittest, Markdown Skill instructions, JSON manifests, PNG assets.

## Global Constraints

- Bundle exactly 30 complete, attributed FigureBench development images under `assets/figurebench-references/`; never bundle official test images.
- Ordinary users never download FigureBench; the full dataset is a maintainer-only curation input.
- Inspect at least two complete bundled references per run and continue until every planned geometry, frame, connector, layout relationship, and special visualization is covered; attach only mapped crops to Prompt 1.
- Context 1 records recurring domain visual conventions; Context 2 maps scientific content to human-producible visuals; Context 3 records adaptively selected crops, a complete visual-coverage matrix, one base-palette lineage, and taste soft constraints.
- Prompt 1 must include the mapped FigureBench crop images and their textual crop contracts.
- Use exactly one approved palette-library base group; optional added colours require explicit web evidence of their relationship to that group and must never come from another library group.
- Python must not call scholarly search, VLM, image-generation, or SVG-generation models.
- PNG1 is directly transcribed to editable SVG1 by the base Codex multimodal model; no HTML, Python, draw.io, local redraw, or raster-wrapper substitution is allowed.
- PNG1.5 exists only as a deterministic rendering of SVG1 for VLM diagnosis and must never appear in Prompt 2 attachments.
- Prompt 2 receives PNG1, approved SVG crops, the diagnosis, replacement crops, and Contexts 1–3; it produces final PNG2.
- Perform exactly two image-generation calls and exactly one SVG-diagnostic loop.
- Do not run PNG2 through another SVG conversion.
- Use TDD for code and baseline/forward behavioral scenarios for Skill instructions.

---

## Target file map

### Create

- `scientific_figure_workflow/__init__.py` — supported public interfaces.
- `scientific_figure_workflow/artifacts.py` — Context 1–3, diagnosis, and run-manifest validation.
- `scientific_figure_workflow/reference_pack.py` — bundled reference index validation, ranking, and crop execution.
- `scientific_figure_workflow/palette.py` — one-palette contract validation.
- `scientific_figure_workflow/prompts.py` — Prompt 1 and Prompt 2 bundle compilation.
- `scientific_figure_workflow/svg_diagnostics.py` — editable-SVG checks, rendering, diagnosis validation, and approved crop execution.
- `scripts/figure_workflow.py` — unified deterministic CLI.
- `scripts/curate_figurebench_reference_pack.py` — maintainer-only candidate preparation and 30-image materialization.
- `scripts/check_installation.py` — validates required instructions, manifests, dependencies, and all 30 bundled references.
- `assets/figurebench-references/index.json` — index and attribution for the 30 complete images.
- `assets/figurebench-references/reference-001.png` through `reference-030.png` — curated full-image references.
- `references/artifact-schemas.md` — model-facing Context and diagnosis schemas.
- `references/figurebench-visual-selection.md` — candidate selection and crop-contract instructions.
- `references/prompt-templates.md` — exact Prompt 1, SVG transcription, diagnosis, and Prompt 2 templates.
- `references/taste-rules.md` — low-priority palette/layout/human-editability guidance.
- `references/svg-diagnostic.md` — SVG1/PNG1.5 diagnostic decisions and crop rules.
- `requirements.txt` — runtime deterministic dependencies.
- `requirements-maintainer.txt` — FigureBench curation dependencies.
- `tests/test_artifacts.py`
- `tests/test_reference_pack.py`
- `tests/test_palette.py`
- `tests/test_prompts.py`
- `tests/test_svg_diagnostics.py`
- `tests/test_cli.py`
- `tests/test_installation.py`
- `tests/fixtures/editable.svg`
- `tests/fixtures/raster-wrapper.svg`
- `tests/skill-scenarios/baseline.md`
- `tests/skill-scenarios/forward.md`

### Rewrite

- `SKILL.md`
- `agents/openai.yaml`
- `README.md`
- `README_ZH.md`

### Remove after replacement passes

- `scientific_figure_rag/`
- `scripts/figurebench_rag.py`
- `scripts/setup_figurebench_rag.py`
- `scripts/curate_reference_pack.py`
- `references/figurebench-rag.md`
- `references/palette-rag.md`
- `requirements-rag.txt`
- `tests/test_retrieval.py`
- `tests/test_curation.py`

---

### Task 1: Artifact contracts for Contexts 1–3 and run state

**Files:**
- Create: `scientific_figure_workflow/__init__.py`
- Create: `scientific_figure_workflow/artifacts.py`
- Create: `tests/test_artifacts.py`

**Interfaces:**
- Produces: `validate_context1(value: Mapping[str, Any]) -> dict[str, Any]`
- Produces: `validate_context2(value: Mapping[str, Any]) -> dict[str, Any]`
- Produces: `validate_context3(value: Mapping[str, Any], component_ids: Collection[str]) -> dict[str, Any]`
- Produces: `validate_diagnosis(value: Mapping[str, Any], component_ids: Collection[str]) -> dict[str, Any]`
- Produces: `validate_run_manifest(value: Mapping[str, Any], root: Path) -> dict[str, Any]`
- Produces: `load_json_object(path: str | Path) -> dict[str, Any]`

- [ ] **Step 1: Write failing Context validation tests**

Create tests that use concrete valid fixtures and one failure per invariant:

```python
class ContextArtifactTests(unittest.TestCase):
    def test_context1_requires_recurrence_evidence(self):
        with self.assertRaisesRegex(ValueError, "recurrence_evidence"):
            validate_context1({"domain": "music generation", "conventions": [{"concept": "piano roll"}]})

    def test_context2_requires_visual_provenance_for_each_component(self):
        with self.assertRaisesRegex(ValueError, "construction_provenance"):
            validate_context2({
                "mainline": "prompt to audio",
                "components": [{"id": "audio", "label": "Audio", "semantic_role": "output"}],
                "relationships": [],
            })

    def test_context3_requires_crop_image_and_crop_contract(self):
        with self.assertRaisesRegex(ValueError, "crop_contract"):
            validate_context3({
                "selected_references": [{"reference_id": "reference-001", "crop_path": "crops/a.png"}],
                "palette": valid_palette(),
                "taste_constraints": ["quiet hierarchy"],
            }, {"encoder"})
```

- [ ] **Step 2: Run the tests and confirm RED**

Run: `python -m unittest tests.test_artifacts -v`

Expected: import failure because `scientific_figure_workflow.artifacts` does not exist.

- [ ] **Step 3: Implement focused validators**

Use explicit field checks instead of a new schema dependency. Normalize copies rather than mutating inputs. Define:

```python
VERDICTS = {"keep", "accept_variation", "patch", "reject", "replace"}
PALETTE_RELATIONSHIPS = {
    "tint", "shade", "tone", "analogous_neighbour", "compatible_neutral", "controlled_contrast"
}

def _required_string(record: Mapping[str, Any], key: str, location: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires non-empty {key}")
    return value.strip()

def _unique_ids(records: list[Mapping[str, Any]], location: str) -> list[str]:
    ids = [_required_string(record, "id", location) for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{location} ids must be unique")
    return ids
```

`validate_context1` requires `domain`, `mainline`, and at least one convention with `concept`, non-empty `recurrence_evidence`, `visual_treatment`, `terminology`, and `methodology_relevance`.

`validate_context2` requires `mainline`, unique components with `id`, `label`, `semantic_role`, `visual_treatment`, `construction_provenance`, `special`, and `source_context`; every relationship must point to known component ids.

`validate_context3` requires at least two distinct selected `reference_id` values; selected crops with `reference_id`, `crop_path`, `target_component_id`, and a `crop_contract` containing non-empty `borrow`, `must_change`, and `human_editable_reason`; a coverage-matrix record for every Context 2 visual need; one base-palette lineage with validated extensions; and a taste list. Every coverage record names either one or more crop ids or an explicit basic-geometry justification.

`validate_diagnosis` requires exactly one verdict record per Context 2 component id and accepts only the five declared verdicts.

`validate_run_manifest` checks required relative paths through `png2-final.png`, rejects absolute paths, and verifies every declared file under the supplied root.

- [ ] **Step 4: Export only stable public functions**

```python
from .artifacts import (
    load_json_object,
    validate_context1,
    validate_context2,
    validate_context3,
    validate_diagnosis,
    validate_run_manifest,
)

__all__ = [
    "load_json_object",
    "validate_context1",
    "validate_context2",
    "validate_context3",
    "validate_diagnosis",
    "validate_run_manifest",
]
```

- [ ] **Step 5: Run tests and commit**

Run: `python -m unittest tests.test_artifacts -v`

Expected: all Context and manifest tests pass.

Commit:

```bash
git add scientific_figure_workflow tests/test_artifacts.py
git commit -m "feat: define two pass workflow artifacts"
```

---

### Task 2: Bundled 30-image FigureBench reference pack

**Files:**
- Create: `scientific_figure_workflow/reference_pack.py`
- Create: `scripts/curate_figurebench_reference_pack.py`
- Create: `assets/figurebench-references/index.json`
- Create: `assets/figurebench-references/reference-001.png` through `reference-030.png`
- Create: `tests/test_reference_pack.py`
- Create: `requirements-maintainer.txt`

**Interfaces:**
- Produces: `load_reference_index(root: str | Path) -> list[dict[str, Any]]`
- Produces: `validate_reference_pack(root: str | Path, expected_count: int = 30) -> dict[str, Any]`
- Produces: `rank_candidates(context2: Mapping[str, Any], references: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]`
- Maintainer CLI: `prepare` creates a review manifest from FigureBench development images.
- Maintainer CLI: `materialize` copies and normalizes exactly 30 reviewed images into the bundled pack.

- [ ] **Step 1: Write failing pack completeness and selection tests**

```python
class ReferencePackTests(unittest.TestCase):
    def test_distributed_pack_has_exactly_thirty_indexed_images(self):
        summary = validate_reference_pack(ROOT / "assets/figurebench-references")
        self.assertEqual(summary["references"], 30)
        self.assertEqual(summary["missing"], [])
        self.assertEqual(summary["partitions"], ["dev"])

    def test_candidate_ranking_prioritizes_needed_geometry_and_layout(self):
        ranked = rank_candidates(context2_fixture(), references_fixture(30))
        self.assertEqual(len(ranked), 30)
        self.assertIn("rounded_container", ranked[0]["matched_components"])
        self.assertTrue(all(item["partition"] == "dev" for item in ranked))
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_reference_pack -v`

Expected: import failure and missing asset pack.

- [ ] **Step 3: Implement index validation and deterministic ranking**

Each index record must contain exactly these maintained fields:

```json
{
  "id": "reference-001",
  "file": "reference-001.png",
  "partition": "dev",
  "source_id": "fixture-paper-001",
  "source_kind": "paper",
  "license": "CC-BY-4.0",
  "attribution": "FigureBench / original source attribution",
  "components": ["rounded_container", "branching_arrow"],
  "layout_family": "horizontal_flow",
  "human_editable_signals": ["flat fill", "consistent stroke"],
  "description": "Grouped three-stage flow with restrained annotations"
}
```

Reject duplicate ids/files, absent files, non-`dev` partitions, missing attribution, empty construction tags, and an index count other than 30.

Candidate scoring is `5 * component_overlap + 3 * layout_overlap + 2 * human_editability_overlap`. Return all 30 in stable rank order while preferring unseen `layout_family` and unseen `source_id` at equal scores. The VLM, not Python, decides how many ranked images to inspect. Ties sort by stable `id`.

- [ ] **Step 4: Implement the maintainer curation CLI**

`prepare` accepts a local FigureBench root, scans only `images/`, excludes `test_images/`, creates max-edge-1200 review thumbnails under `work/figurebench-review/`, and writes `work/figurebench-candidates.json`. A maintainer-only `download` subcommand uses `huggingface_hub.snapshot_download` with `allow_patterns=["README.md", "data/dev.parquet", "images/*", "images/**/*"]`, requires `--accept-figurebench-license`, and writes to the explicitly supplied development cache without downloading `test_images/` or `data/test.parquet`.

`materialize` consumes `work/figurebench-selection.json`, requires exactly 30 reviewed records, verifies each `source_path` remains under the development image root, normalizes each image to RGB PNG with max edge 1600, and writes sequential `reference-001.png` through `reference-030.png` plus `index.json`.

Use this selection schema:

```json
{
  "selections": [
    {
      "source_path": "images/fixture-paper-001/figure-01.png",
      "source_id": "fixture-paper-001",
      "source_kind": "paper",
      "license": "CC-BY-4.0",
      "attribution": "FigureBench / verify original source",
      "components": ["rounded_container"],
      "layout_family": "horizontal_flow",
      "human_editable_signals": ["flat fill", "consistent stroke"],
      "description": "Reusable container and connector treatment",
      "rights_reviewed": true,
      "human_editability_reviewed": true
    }
  ]
}
```

Require `rights_reviewed` and `human_editability_reviewed` to be true. Refuse materialization otherwise.

- [ ] **Step 5: Curate the actual 30-image pack**

Download the maintainer-only development inputs and prepare the review set:

```bash
python scripts/curate_figurebench_reference_pack.py download \
  --destination work/figurebench-source \
  --accept-figurebench-license
python scripts/curate_figurebench_reference_pack.py prepare \
  --dataset work/figurebench-source \
  --output work/figurebench-review \
  --manifest work/figurebench-candidates.json
```

Use the FigureBench development set only. Produce at least 60 review candidates covering the component/layout families in the design spec. Inspect the candidates with a VLM, exclude image-model-looking figures, unverifiable redistributions, test images, decorative slide cards, and redundant layouts. Record the final 30 in `work/figurebench-selection.json`, then run:

```bash
python scripts/curate_figurebench_reference_pack.py materialize \
  --dataset work/figurebench-source \
  --selection work/figurebench-selection.json \
  --output assets/figurebench-references
```

Expected: exactly 30 PNG files and an index with exactly 30 records; total pack size is reported.

- [ ] **Step 6: Run tests and commit**

Run: `python -m unittest tests.test_reference_pack -v`

Expected: all pack and selection tests pass.

Commit:

```bash
git add scientific_figure_workflow/reference_pack.py scripts/curate_figurebench_reference_pack.py assets/figurebench-references tests/test_reference_pack.py requirements-maintainer.txt
git commit -m "feat: bundle curated figurebench reference pack"
```

---

### Task 3: Per-run FigureBench crop contracts

**Files:**
- Modify: `scientific_figure_workflow/reference_pack.py`
- Modify: `tests/test_reference_pack.py`
- Create: `references/figurebench-visual-selection.md`

**Interfaces:**
- Produces: `apply_crop_manifest(reference_root: Path, manifest: Mapping[str, Any], output_dir: Path) -> dict[str, Any]`
- Produces: `validate_reference_coverage(context2: Mapping[str, Any], crop_manifest: Mapping[str, Any], basic_geometry: Sequence[Mapping[str, Any]]) -> dict[str, Any]`
- Consumes crop records with normalized `[left, top, right, bottom]` bounds.

- [ ] **Step 1: Write failing crop tests**

```python
def test_crop_manifest_writes_mapped_crop_and_contract(self):
    manifest = {
        "crops": [{
            "id": "crop-container",
            "reference_id": "reference-001",
            "bounds": [0.1, 0.2, 0.6, 0.8],
            "target_component_id": "encoder",
            "crop_contract": {
                "borrow": ["corner family", "stroke rhythm"],
                "must_change": ["label", "proportions"],
                "human_editable_reason": "flat primitives with a consistent outline"
            }
        }]
    }
    result = apply_crop_manifest(pack_root, manifest, output)
    self.assertTrue((output / result["crops"][0]["crop_path"]).is_file())
```

Also test unknown reference ids, out-of-range bounds, empty contracts, and duplicate crop ids.

Add coverage tests requiring at least two distinct `reference_id` values and requiring every non-basic Context 2 component to be mapped to a crop. A component may instead be covered by a basic-geometry record only when that record names its primitive, construction steps, and human-editable rationale.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_reference_pack.ReferenceCropTests -v`

Expected: `apply_crop_manifest` import failure.

- [ ] **Step 3: Implement deterministic cropping**

Convert normalized bounds to integer pixel coordinates using the complete bundled image. Preserve RGB, do not recolour or decorate crops, and write `{crop-id}.png`. Return a manifest that keeps the crop contract next to its image path.

- [ ] **Step 4: Write the model-facing selection reference**

Document the required sequence: derive needed components from Context 2, inspect at least two ranked complete references, choose relevant regions, update the coverage matrix, and continue inspecting references until every planned visual need is covered. Then emit normalized coordinates plus crop contracts, execute the crop helper, and attach the resulting crops to Prompt 1. Explicitly forbid stopping at an arbitrary image count or attaching unexplained complete figures.

- [ ] **Step 5: Run tests and commit**

Run: `python -m unittest tests.test_reference_pack -v`

Commit:

```bash
git add scientific_figure_workflow/reference_pack.py tests/test_reference_pack.py references/figurebench-visual-selection.md
git commit -m "feat: map figurebench crops to planned components"
```

---

### Task 4: One base-palette lineage, related-colour enrichment, and taste priority

**Files:**
- Create: `scientific_figure_workflow/palette.py`
- Rewrite: `tests/test_palette.py`
- Create: `references/taste-rules.md`

**Interfaces:**
- Produces: `validate_palette(value: Mapping[str, Any], palette_library: Sequence[Mapping[str, Any]]) -> dict[str, Any]`
- Produces: `palette_hex_set(value: Mapping[str, Any]) -> frozenset[str]`

- [ ] **Step 1: Replace old palette tests with new source-identity tests**

Test one approved base group, optional web-evidenced related colours, and these failures:

```python
def test_rejects_a_second_palette_library_group(self):
    with self.assertRaisesRegex(ValueError, "one base palette group"):
        validate_palette({
            "base_palette_id": "group-a",
            "additional_palette_ids": ["group-b"],
            "colours": [{"role": "ink", "hex": "#203040", "rgb": [32, 48, 64]}],
            "extensions": []
        }, palette_library_fixture())

def test_related_colour_requires_web_evidence_and_relationship(self):
    palette = validate_palette({
        "base_palette_id": "group-a",
        "colours": base_colours(),
        "extensions": [{
            "role": "quiet_accent",
            "hex": "#6E8FA3",
            "rgb": [110, 143, 163],
            "relationship": "analogous_neighbour",
            "evidence_url": "https://color.adobe.com/create/color-wheel",
            "evidence_summary": "Blue-grey adjacent tone compatible with the base blue family"
        }]
    }, palette_library_fixture())
    self.assertEqual(palette["base_palette_id"], "group-a")
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_palette -v`

Expected: failures because the old API accepts unrelated web SVG sources.

- [ ] **Step 3: Implement the new validator**

Require one `base_palette_id` that exists in the approved library. The active base colours must match that group. Every extension requires exact uppercase HEX, matching integer RGB, a non-empty semantic role, a relationship from `tint`, `shade`, `tone`, `analogous_neighbour`, `compatible_neutral`, or `controlled_contrast`, an HTTPS evidence URL, and a short evidence summary. Reject `additional_palette_ids`, user-reference or FigureBench palette sources, duplicate HEX values, gradients, unexplained extensions, and any active colour outside the base-plus-extension contract.

- [ ] **Step 4: Write taste soft constraints with explicit priority**

`references/taste-rules.md` must contain short, actionable language for restraint, coherent spacing, hierarchy, balanced contrast, controlled accent use, and draw.io-like editability. It must state that taste cannot override scientific correctness, explicit user constraints, domain conventions, construction provenance, or the one-base-palette lineage. It cannot invent extension colours without the required web relationship evidence.

- [ ] **Step 5: Run tests and commit**

Run: `python -m unittest tests.test_palette -v`

Commit:

```bash
git add scientific_figure_workflow/palette.py tests/test_palette.py references/taste-rules.md
git commit -m "feat: enforce one extensible palette lineage"
```

---

### Task 5: Prompt 1 and Prompt 2 bundle compilers

**Files:**
- Create: `scientific_figure_workflow/prompts.py`
- Create: `tests/test_prompts.py`
- Create: `references/prompt-templates.md`

**Interfaces:**
- Produces: `build_prompt1_bundle(methodology: str, context1: Mapping[str, Any], context2: Mapping[str, Any], context3: Mapping[str, Any], user_reference: str | None, root: Path) -> dict[str, Any]`
- Produces: `build_prompt2_bundle(methodology: str, context1: Mapping[str, Any], context2: Mapping[str, Any], context3: Mapping[str, Any], png1: str, diagnosis: Mapping[str, Any], svg_crops: Mapping[str, Any], replacement_crops: Mapping[str, Any], root: Path) -> dict[str, Any]`
- Produces: `write_bundle(bundle: Mapping[str, Any], output_dir: Path) -> None`

- [ ] **Step 1: Write failing Prompt 1 tests**

```python
def test_prompt1_contains_every_mapped_figurebench_crop(self):
    bundle = build_prompt1_bundle("method", c1(), c2(), c3(), None, run_root)
    self.assertEqual(
        {item["path"] for item in bundle["attachments"] if item["role"] == "figurebench_component"},
        {"references/figurebench/crops/container.png", "references/figurebench/crops/arrow.png"},
    )
    self.assertIn("Do not add decoration without a named scientific role", bundle["prompt"])
```

Test failure when a crop lacks a component mapping, when a planned component lacks a visual treatment, or when palette assignments use disallowed colours.

- [ ] **Step 2: Write failing Prompt 2 exclusion tests**

```python
def test_prompt2_uses_png1_and_svg_crops_but_never_png15(self):
    bundle = build_prompt2_bundle("method", c1(), c2(), c3(), "png1.png", diagnosis(), svg_crops(), {}, run_root)
    paths = {item["path"] for item in bundle["attachments"]}
    self.assertIn("png1.png", paths)
    self.assertIn("svg-diagnostic/approved-crops/encoder.png", paths)
    self.assertNotIn("svg-diagnostic/png1.5.png", paths)
```

- [ ] **Step 3: Run tests and confirm RED**

Run: `python -m unittest tests.test_prompts -v`

Expected: import failure because `prompts.py` does not exist.

- [ ] **Step 4: Implement ordered prompt compilation**

Prompt 1 must emit the ten ordered sections from the design spec. Include exact component labels and relationships from Context 2, mapped crop instructions and complete coverage matrix from Context 3, the one base-palette lineage with any evidenced extensions, and the anti-AI prohibitions. Search explanations remain in Context 1 evidence and do not become figure prose.

Prompt 2 must convert diagnosis verdicts into five explicit instruction blocks: preserve, accept variation, patch, reject, replace. Reject any attachment whose normalized basename is `png1.5.png`, any attachment role `svg_diagnostic_render`, and any diagnosis missing a Context 2 component.

Return bundles in this stable shape:

```json
{
  "format": "scientific-figure-prompt-bundle-v1",
  "phase": "prompt1",
  "prompt": "...",
  "attachments": [
    {"path": "...", "role": "figurebench_component", "target_component_id": "encoder"}
  ]
}
```

- [ ] **Step 5: Write the exact model-facing templates**

`references/prompt-templates.md` contains four templates: Context extraction, Prompt 1 generation, direct editable SVG transcription, and Prompt 2 revision. The direct SVG template must say that PNG1 is the only visual truth and forbid HTML, embedded raster wrappers, local scripting, and fresh SVG design.

- [ ] **Step 6: Run tests and commit**

Run: `python -m unittest tests.test_prompts -v`

Commit:

```bash
git add scientific_figure_workflow/prompts.py tests/test_prompts.py references/prompt-templates.md
git commit -m "feat: compile two pass image prompts"
```

---

### Task 6: SVG1 editability, PNG1.5 rendering, and diagnosis crops

**Files:**
- Create: `scientific_figure_workflow/svg_diagnostics.py`
- Create: `tests/test_svg_diagnostics.py`
- Create: `tests/fixtures/editable.svg`
- Create: `tests/fixtures/raster-wrapper.svg`
- Create: `references/svg-diagnostic.md`
- Create: `requirements.txt`

**Interfaces:**
- Produces: `inspect_editable_svg(path: str | Path) -> dict[str, int | bool]`
- Produces: `render_svg(svg_path: str | Path, png_path: str | Path) -> Path`
- Produces: `apply_svg_crop_manifest(rendered_png: Path, manifest: Mapping[str, Any], output_dir: Path) -> dict[str, Any]`
- Consumes: `validate_diagnosis` from Task 1.

- [ ] **Step 1: Write failing editability tests**

```python
def test_editable_svg_reports_text_and_vector_nodes(self):
    summary = inspect_editable_svg(FIXTURES / "editable.svg")
    self.assertGreater(summary["text_nodes"], 0)
    self.assertGreater(summary["vector_nodes"], 2)
    self.assertFalse(summary["raster_only"])

def test_raster_wrapper_is_rejected(self):
    with self.assertRaisesRegex(ValueError, "raster wrapper"):
        inspect_editable_svg(FIXTURES / "raster-wrapper.svg")
```

Add failures for HTML roots, malformed XML, missing SVG namespace/root, zero editable nodes, and remote image URLs.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_svg_diagnostics -v`

Expected: import failure.

- [ ] **Step 3: Implement safe SVG inspection**

Parse with `defusedxml.ElementTree`. Count `text`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, and `path` nodes. Reject non-SVG roots, script/foreignObject nodes, external URLs, and any SVG whose only visible content is `image`. Permit an embedded image only when it is not the sole visual content and the diagnosis marks it as an eligible photographic crop.

- [ ] **Step 4: Implement deterministic CairoSVG rendering**

```python
def render_svg(svg_path: str | Path, png_path: str | Path) -> Path:
    import cairosvg
    inspect_editable_svg(svg_path)
    target = Path(png_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(url=str(svg_path), write_to=str(target))
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError("SVG rendering did not produce PNG1.5")
    return target
```

- [ ] **Step 5: Implement approved SVG crop execution**

Use normalized bounds over PNG1.5 only to materialize the specifically approved SVG crops. Each crop record must name a target component and cite a `keep`, `accept_variation`, or `patch` diagnosis id. Reject crops for `reject` or `replace` verdicts. The full PNG1.5 path is never returned as a Prompt 2 attachment.

- [ ] **Step 6: Write SVG diagnostic guidance**

Document comparison inputs, the five verdicts, semantic-over-aesthetic priority, acceptable diffusion simplification, unacceptable fake objects, replacement lookup, and the rule that PNG1.5 is review-only while approved SVG crops may enter Prompt 2.

- [ ] **Step 7: Run tests and commit**

Run: `python -m unittest tests.test_svg_diagnostics -v`

Commit:

```bash
git add scientific_figure_workflow/svg_diagnostics.py tests/test_svg_diagnostics.py tests/fixtures references/svg-diagnostic.md requirements.txt
git commit -m "feat: diagnose png drafts through editable svg"
```

---

### Task 7: Unified CLI and complete-run validation

**Files:**
- Create: `scripts/figure_workflow.py`
- Create: `scripts/check_installation.py`
- Create: `tests/test_cli.py`
- Create: `tests/test_installation.py`
- Modify: `scientific_figure_workflow/__init__.py`

**Interfaces:**
- CLI commands: `check-installation`, `validate-context`, `rank-references`, `crop-references`, `validate-reference-coverage`, `validate-palette`, `build-prompt1`, `inspect-svg`, `render-svg`, `validate-diagnosis`, `crop-svg`, `build-prompt2`, `validate-run`.

- [ ] **Step 1: Write failing CLI integration tests**

Use temporary run directories and subprocess calls. Verify JSON stdout, non-zero exit on invalid artifacts, output file creation, and no network/model imports.

```python
def test_build_prompt2_cli_rejects_png15_attachment(self):
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "build-prompt2", "--run", str(run_fixture)],
        text=True,
        capture_output=True,
    )
    self.assertNotEqual(completed.returncode, 0)
    self.assertIn("PNG1.5", completed.stderr)
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_cli tests.test_installation -v`

Expected: missing scripts.

- [ ] **Step 3: Implement the unified CLI**

Use `argparse` subcommands and thin dispatch only. All JSON file loading, validation, ranking, crop execution, bundle compilation, SVG inspection/rendering, and run validation must call package functions. Print one JSON object to stdout on success and a concise error to stderr with exit code 2 on validation failure.

- [ ] **Step 4: Implement installation validation**

Require `SKILL.md`, five new references, the unified CLI, package modules, runtime requirements, `index.json`, and exactly `reference-001.png` through `reference-030.png`. Run `validate_reference_pack` and report total bytes.

- [ ] **Step 5: Export public interfaces and run tests**

Update `__init__.py` with stable functions from all modules. Run:

```bash
python -m unittest tests.test_cli tests.test_installation -v
```

- [ ] **Step 6: Commit**

```bash
git add scripts/figure_workflow.py scripts/check_installation.py scientific_figure_workflow/__init__.py tests/test_cli.py tests/test_installation.py
git commit -m "feat: add deterministic figure workflow cli"
```

---

### Task 8: Rewrite the Skill using behavioral RED-GREEN scenarios

**Files:**
- Rewrite: `SKILL.md`
- Create: `references/artifact-schemas.md`
- Create: `tests/skill-scenarios/baseline.md`
- Create: `tests/skill-scenarios/forward.md`

**Interfaces:**
- Consumes all deterministic commands from Task 7.
- Produces the exact model workflow and progressive links to the five new references.

- [ ] **Step 1: Record three baseline failures before rewriting**

Run fresh-context agent scenarios against the current Skill:

1. Methodology only: observe whether it creates Contexts 1–3 and attaches mapped FigureBench crops to PNG1.
2. PNG1 available: observe whether it directly transcribes PNG1 to editable SVG1 or treats SVG as optional/local reconstruction.
3. SVG diagnosis available: observe whether it generates Prompt 2 from PNG1 plus approved SVG crops while excluding PNG1.5.

Record exact omissions and rationalizations in `tests/skill-scenarios/baseline.md`.

- [ ] **Step 2: Rewrite `SKILL.md` around the canonical artifact recipe**

Keep the entrypoint concise and route detail to references. The body must define:

- accepted input and domain extraction;
- 3–4 scholarly paper search and Context 1;
- Context 2 human-producible content-to-visual mapping;
- adaptive selection from the 30-image FigureBench pack with a two-image minimum, complete visual coverage, mapped crops, one base-palette lineage, targeted web colour-relationship enrichment when needed, and Context 3;
- Prompt 1 anti-AI recipe and first image generation;
- direct base-model editable SVG transcription from PNG1;
- PNG1.5 diagnostic-only rule and five diagnosis verdicts;
- Prompt 2 inputs and strict PNG1.5 exclusion; and
- final PNG2 termination.

State positive output shapes rather than relying only on prohibitions. Include exact commands at the point each deterministic helper is required.

- [ ] **Step 3: Write artifact schemas for model-produced JSON**

`references/artifact-schemas.md` must give one complete valid JSON example for Context 1, Context 2, Context 3, diagnosis, crop manifests, and the run manifest. Field names must match Task 1 exactly.

- [ ] **Step 4: Run forward scenarios with the rewritten Skill**

Repeat the same three fresh-context scenarios. Record whether the agent produced the required artifacts and attachments in `tests/skill-scenarios/forward.md`. Tighten wording if any scenario skips domain search, attaches complete unexplained references, hand-authors SVG, treats PNG1.5 as a Prompt 2 input, or stops at PNG1.

- [ ] **Step 5: Validate and commit**

Run:

```bash
python /Users/lawrenceriver/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
python scripts/check_installation.py
```

Expected: `Skill is valid!` and a complete 30-reference installation.

Commit:

```bash
git add SKILL.md references/artifact-schemas.md tests/skill-scenarios
git commit -m "feat: teach evidence guided two pass figure generation"
```

---

### Task 9: UI metadata, public documentation, and legacy removal

**Files:**
- Rewrite: `agents/openai.yaml`
- Rewrite: `README.md`
- Rewrite: `README_ZH.md`
- Remove: `scientific_figure_rag/`
- Remove: `scripts/figurebench_rag.py`
- Remove: `scripts/setup_figurebench_rag.py`
- Remove: `scripts/curate_reference_pack.py`
- Remove: `references/figurebench-rag.md`
- Remove: `references/palette-rag.md`
- Remove: `requirements-rag.txt`
- Remove: `tests/test_retrieval.py`
- Remove: `tests/test_curation.py`

**Interfaces:**
- `agents/openai.yaml` default prompt invokes `$genlike-scientific-svg` and starts the complete two-pass workflow.
- READMEs explain installation, required evidence stages, 30 bundled references, and final PNG2 without contradicting `SKILL.md`.

- [ ] **Step 1: Write failing public-surface tests**

Add to `tests/test_installation.py`:

```python
def test_public_files_describe_png1_svg_diagnosis_and_png2(self):
    for path in (ROOT / "SKILL.md", ROOT / "README.md", ROOT / "README_ZH.md"):
        text = path.read_text(encoding="utf-8")
        self.assertIn("PNG1", text)
        self.assertIn("SVG1", text)
        self.assertIn("PNG2", text)
        self.assertNotIn("optional faithful PNG-to-SVG verification", text)

def test_legacy_package_is_absent(self):
    self.assertFalse((ROOT / "scientific_figure_rag").exists())
    self.assertFalse((ROOT / "scripts/figurebench_rag.py").exists())
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_installation -v`

Expected: current UI/README wording and legacy paths fail.

- [ ] **Step 3: Rewrite public surfaces**

Keep `agents/openai.yaml` strings quoted and preserve implicit invocation. Its default prompt must request a Methodology, optional reference, three contexts, mapped FigureBench crops, PNG1, direct SVG diagnosis, and final PNG2 in one sentence.

Update READMEs only from implemented behavior. Explain that the 30 complete references ship with the Skill and ordinary users do not download FigureBench. Do not advertise SVG1 as a final deliverable.

- [ ] **Step 4: Remove legacy code and obsolete tests**

Delete only the listed files after all replacement tests are green. Confirm no imports or links remain:

```bash
rg -n "scientific_figure_rag|figurebench_rag|optional faithful PNG-to-SVG|skip_svg_verification" .
```

Expected: no runtime/public references; historical design documents may still contain the old phrase.

- [ ] **Step 5: Run tests and commit**

Run: `python -m unittest discover -s tests -v`

Commit:

```bash
git add agents/openai.yaml README.md README_ZH.md tests/test_installation.py
git add -u scientific_figure_rag scripts references requirements-rag.txt tests
git commit -m "refactor: replace legacy figure rag workflow"
```

---

### Task 10: End-to-end verification and release readiness

**Files:**
- Modify only files required to fix verification failures.

**Interfaces:**
- Verifies the complete repository and a synthetic run through Prompt 2.

- [ ] **Step 1: Run the complete automated test suite**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: all tests pass with no skipped core tests.

- [ ] **Step 2: Validate Skill installation and metadata**

Run:

```bash
python scripts/check_installation.py
python /Users/lawrenceriver/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

Expected: exactly 30 installed references and `Skill is valid!`.

- [ ] **Step 3: Run a deterministic synthetic workflow smoke test**

Create a temporary run from test fixtures, validate Contexts 1–3, rank all 30 references, inspect and map the minimum two references needed to cover the fixture's visual requirements, execute two mapped reference crops, build Prompt 1, validate/render `editable.svg` to PNG1.5, validate a five-verdict diagnosis, crop one approved SVG region, build Prompt 2, and validate a run manifest containing a fixture PNG2.

Run through CLI commands only. Expected: every command returns exit code 0; Prompt 1 attachments include mapped FigureBench crops; Prompt 2 attachments include PNG1 and approved SVG crops but not PNG1.5.

- [ ] **Step 4: Audit the reference pack**

Run:

```bash
find assets/figurebench-references -name 'reference-*.png' | wc -l
du -sh assets/figurebench-references
python scripts/figure_workflow.py check-installation
```

Expected: count `30`, a reported pack size, and an installation PASS. Manually inspect the contact sheet for duplicate compositions, obvious generated-image artifacts, unreadable source figures, and missing attribution.

- [ ] **Step 5: Run repository hygiene checks**

Run:

```bash
git diff --check
git status --short
rg -n "TBD|TODO|PLACEHOLDER" SKILL.md references scientific_figure_workflow scripts tests
```

Expected: no whitespace errors, only intended changes, and no unfinished placeholders.

- [ ] **Step 6: Commit final verification fixes**

```bash
git add SKILL.md agents assets references scientific_figure_workflow scripts tests README.md README_ZH.md requirements.txt requirements-maintainer.txt
git commit -m "test: verify two pass figure workflow"
```
