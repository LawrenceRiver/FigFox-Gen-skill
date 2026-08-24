# First PNG, Optional SVG Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the first directly generated, fully labelled PNG the only creative figure; use SVG only for an optional faithful PNG-to-SVG verification/editability pass.

**Architecture:** The skill detects the field, gathers 3–4 high-aesthetic same-domain examples, and derives a compact original topology without numbered parts. Domain references teach professional terminology and conventional visual encodings; FigureBench supplies compatible reusable geometry and layout grammar. The model generates the complete PNG directly. A later SVG operation is valid only when a capable converter can faithfully transcribe the first PNG with editable layers; otherwise it is explicitly skipped, never replaced by a newly authored SVG or a second image generation call.

**Tech Stack:** Markdown Skill instructions, Python 3 local RAG brief compiler, unittest, JSON CLI.

## Global Constraints

- Search and FigureBench references teach conventions, terminology, component treatment, and aggregate geometry; they must not be copied as one paper figure.
- Do not render SVG before first image generation, do not number planned parts, and do not run a second image-generation call.
- The first PNG contains every required label and is the semantic source of truth.
- SVG verification is optional, must be a faithful conversion of that PNG, and must preserve editable text/layers plus the frozen one-group palette; a failed conversion reports `skip_svg_verification`.
- Do not create a fresh SVG from the topology contract and label it a conversion.

---

### Task 1: Compile an optional SVG-verification brief

**Files:** `scientific_figure_rag/index.py`, `scripts/figurebench_rag.py`, `tests/test_retrieval.py`

**Interfaces:** `build_svg_verification_brief(first_draft_png: str, generation_contract: Mapping[str, Any], geometry_lexicon: Mapping[str, Any], inspection: Mapping[str, Any]) -> dict[str, Any]`; CLI command `svg-verification-brief`.

- [ ] Write a failing test asserting the phase is `optional faithful PNG-to-SVG verification`, the failure outcome is `skip_svg_verification`, and conversion rules include `do not create a new SVG`.
- [ ] Run `python -m unittest tests.test_retrieval -v`; expect failure because the function and command do not yet exist.
- [ ] Implement a brief that names the actual raster source, preserves only its generated-image contract as verification truth, requires editable text/layers and frozen palette fidelity, and prohibits new SVG authoring.
- [ ] Add `svg-verification-brief` using existing JSON CLI helpers.
- [ ] Re-run `python -m unittest tests.test_retrieval -v`; expect pass.
- [ ] Commit: `git add scientific_figure_rag/index.py scripts/figurebench_rag.py tests/test_retrieval.py && git commit -m "feat: add optional PNG to SVG verification brief"`.

### Task 2: Replace the skill workflow and public explanation

**Files:** `SKILL.md`, `README.md`, `README_ZH.md`, `agents/openai.yaml`, `references/figurebench-rag.md`, `tests/test_palette.py`.

- [ ] Write failing documentation assertions for: 3–4+ references, no numbered planning parts, one direct image-generation call, optional faithful PNG-to-SVG verification, skip behavior, and no second image-generation call.
- [ ] Run `python -m unittest tests.test_palette.SkillDocumentationTests -v`; expect failure because current documents specify a second image call.
- [ ] Replace the post-PNG stage with: first PNG is the only creative output and includes all labels; optional SVG verification accepts only a faithful converter of that exact PNG; loss of semantic structure, editable text, or palette fidelity returns the original PNG with an explicit skipped-verification result.
- [ ] State that same-domain references supply terminology and visual conventions, while FigureBench supplies compatible abstract building blocks and layout grammar; neither source authorizes copying a retrieved paper figure.
- [ ] Re-run `python -m unittest tests.test_palette.SkillDocumentationTests -v`; expect pass.
- [ ] Commit: `git add SKILL.md README.md README_ZH.md agents/openai.yaml references/figurebench-rag.md tests/test_palette.py && git commit -m "docs: make SVG verification optional after first PNG"`.

### Task 3: Validate and publish

- [ ] Run `python -m unittest discover -s tests -v`; expect all tests to pass.
- [ ] Run `python /Users/lawrenceriver/.codex/skills/.system/skill-creator/scripts/quick_validate.py . && git diff --check`; expect `Skill is valid!` and no diff errors.
- [ ] Push the verified commits with `git push origin main`.
