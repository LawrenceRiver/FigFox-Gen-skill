---
name: FigFox-Gen-skill
description: Use when turning a scientific Methodology, with an optional reference image, into an evidence-grounded architecture figure that needs human-edited geometry and a final revised PNG.
metadata:
  short-description: Build evidence-guided two-pass scientific figures
---

# FigFox-Gen-skill

## Core workflow

Turn a Methodology and optional user reference into this exact artifact chain:

```text
Methodology + optional reference
  -> Context 1 domain visual conventions
  -> Context 2 content-to-visual plan
  -> Context 3 mapped FigureBench crops + one palette lineage + taste
  -> Creative Director prompt -> brief + targeted paper-SVG crops
  -> Prompt 1 bundle -> image generation -> PNG1
  -> direct base-model PNG1 transcription -> editable SVG1
  -> deterministic render PNG1.5 -> VLM diagnosis -> approved SVG crops
  -> Prompt 2 bundle (PNG1, approved/replacement crops; never PNG1.5)
  -> image generation -> final PNG2 -> stop
```

This is structurally two image-generation stages and one SVG diagnostic loop. The
local commands validate artifacts and provenance; they do not observe or prove model
call counts.

Start a run with `input/methodology.md` and, when supplied,
`input/user-reference.<ext>`. Use the canonical layout and exact JSON fields in
[artifact schemas](references/artifact-schemas.md). Before work begins, run:

```bash
python scripts/figure_workflow.py check-installation --root .
```

## 1. Context 1: domain visual conventions

Read the Methodology with the language model and extract the scientific domain,
core topic, mainline, likely figure class, named domain concepts, and exact user
constraints. This domain classification supplies Context 1's search scope.

Search the web for 3–4 scholarly papers in that domain. Prefer arXiv and native
SVG/HTML figures; otherwise use credible papers with clearly extractable panels.
Inspect cropped figure regions, not titles or abstracts alone. Record source URLs
and crop paths in `references/web/manifest.json` and `references/web/crops/`.

Compare the retained panels and list Methodology-relevant recurrence: repeated
objects, intermediate models, structural relations, drawing treatments, grouping,
and professional terminology. Distinguish conventions from one-off treatments.
Write `context/context-1-domain-conventions.json`; each convention states what
recurs, where it recurs, how humans depict it, the term used, its Methodology
relevance, and any mapped domain crop with `target_component_id`, `borrow`, and
`must_change`.

If fewer than three credible figures remain, continue searching or report
insufficient evidence. Do not invent recurrence. Validate:

```bash
python scripts/figure_workflow.py validate-context --run RUN --context 1
```

## 2. Context 2: content-to-visual plan

Combine the Methodology, Context 1, and optional user reference. The user reference
has strong authority for structure, layout, emphasis, and visibly human-made basic
visual treatment. Ignore its generated-looking decoration, and never take palette
colours from it.

First express the scientific mainline in text. Then map every block, structure,
relationship, and required label to a visual treatment in
`context/context-2-content-visual-plan.json`. In-image text is limited to block
names, structure names, necessary scientific labels, terms, and relationships;
explanatory research prose stays in planning.

Normal treatments are human-producible basic geometry, recurring domain-paper
constructions, deliberate manual/stylus drawings, draw.io-like editable structures,
or real photographic crops when scientifically necessary. Mark any other treatment
as special and explain whether a human would construct it geometrically, draw it by
hand, or obtain it as a real photo. Every visual must have a semantic role and
construction provenance.

```bash
python scripts/figure_workflow.py validate-context --run RUN --context 2
```

## 3. Context 3: visual evidence, palette, and taste

Read [FigureBench visual selection](references/figurebench-visual-selection.md) and
[taste rules](references/taste-rules.md) at this stage.

The installed FigureBench pack contains exactly 30 complete development images.
Rank candidates, then inspect their actual pixels:

```bash
python scripts/figure_workflow.py rank-references --run RUN
```

Inspect at least two distinct complete references. Continue adaptively until every
Context 2 need has credible evidence: shapes, frame/container families, connectors,
layout relationships, and special visualizations. There is no fixed target or
maximum image count. Stop only at complete coverage.

Complete references are inspection sources, never unexplained Prompt 1 attachments.
For every useful region, write normalized coordinates and a component-specific
contract to `references/figurebench/crops/request.json`. The contract names what to
`borrow`, what `must_change` so the output remains a variant, and why the treatment
is human-editable. A basic-geometry exception must instead give its primitive,
construction steps, and human-editable reason; it cannot excuse a complex visual.
Materialize and check the preserved request:

```bash
python scripts/figure_workflow.py crop-references --run RUN
python scripts/figure_workflow.py validate-reference-coverage --run RUN
```

The crop command writes images plus the separate
`references/figurebench/crops/manifest.json`; it never replaces `request.json`.
FigureBench supplies geometry, layout, spacing, connectors, and human-edited finish.
It is never a palette authority.

Choose exactly one complete group from `references/palette-library.json`. If it
lacks a required functional role, make a targeted web search only for a related
tint, shade, tone, analogous neighbour, compatible neutral, or controlled contrast.
Each extension requires exact uppercase HEX, matching RGB, relationship, intended
role, HTTPS evidence URL, and evidence summary. Never use a second library group or
take colours from the user reference, FigureBench, or domain papers.

Taste is a low-priority soft constraint for spacing, hierarchy, rhythm, balance,
restraint, and human-edited finish. It cannot override scientific meaning, user
constraints, domain evidence, construction provenance, or palette lineage.

Write `context/context-3-visual-kit.json` from the materialized mapped crops,
coverage matrix, one palette lineage, and taste constraints, then validate:

```bash
python scripts/figure_workflow.py validate-palette --run RUN
python scripts/figure_workflow.py validate-context --run RUN --context 3
```

## 4. Creative Director: pre-PNG1 visual ideation

The Creative Director runs after Contexts 1–3 and before any PNG1 generation. It is
a bounded ideation pass, not an image-generation pass: it may propose a concrete
visual treatment for a planned component, but it must not redraw the whole figure or
invent decorative assets.

Compile its model-facing prompt:

```bash
python scripts/figure_workflow.py build-creative-director-prompt --run RUN
```

The model returns `creative-director/brief.json` using the schema in
[artifact schemas](references/artifact-schemas.md). Validate it before Prompt 1:

```bash
python scripts/figure_workflow.py validate-creative-director --run RUN
```

When a new idea needs a visual construction not already covered by Contexts 1–3,
the Creative Director must locate a real scholarly paper figure available as SVG or
extractable SVG/HTML, inspect its pixels, and request a targeted crop under
`references/web/crops/creative-director/`. The crop record must include the target
component, HTTPS `source_url` and `evidence_url`, `source_format: "svg"`, a nonempty
`borrow` list, a nonempty `must_change` list, and a human-editability reason. The
crop is evidence for one component, not a complete paper figure to copy. Never
invent a paper source, attach a whole figure, or use a sticker-like cutout. If no
new external treatment is needed, return an explicit `no_external_svg_needed` brief
instead of fabricating a crop. Palette lineage and both absolute PNG1 prohibitions
remain in force.

## 5. Prompt 1 and PNG1

Read [prompt templates](references/prompt-templates.md). Compile the bundle only
after Contexts 1–3, the Creative Director brief, and all mapped crop files exist:

```bash
python scripts/figure_workflow.py build-prompt1 --run RUN
```

Inspect `prompt-1/attachments.json`. It must attach every mapped domain-paper crop,
every mapped FigureBench crop, every validated Creative Director paper-SVG crop, and
the optional user reference. Attach targeted crop images, not complete unexplained
papers or FigureBench figures. Each crop guides only its declared component and
`borrow`/`must_change` contract. A Creative Director crop can suggest construction
quality and geometry, but cannot donate its source labels, palette, proportions, or
complete composition.

Prompt 1 gives, in order: purpose/mainline; exact block and structure names;
relationships/reading order; content-to-visual mapping; crop mapping; one-palette
contract; layout/taste; exact text and readable bounds; anti-AI invariants; and a
direct PNG instruction. Its visual recipe is flat, deliberate, human-producible,
semantically tied geometry with coherent strokes, corners, arrows, spacing, and
clear labels.

Enforce these defaults: no arbitrary decorative dots, tiles, floating symbols,
purposeless boxes, irrelevant ornament, unjustified extreme contrast, gradients,
glow, decorative shadow, fake cartoons, or shapes without human construction
provenance. Do not default to numbered `1/2/3/4` steps or blue-title-bar/content-box
cards unless an explicit user structure requires that special case. Every requested
label must be exact and fit its declared bounds.

Two first-pass prohibitions are absolute. Never draw a module whose upper portion is
boxed off by a horizontal divider and used as a centered title band; the screenshot-
like “title bar over content box” treatment is forbidden in PNG1. Put labels inline,
outside the frame, or in the planned geometry. Never paste a sticker-like cutout,
clip-art badge, medal, seal, or raster badge into PNG1. A scientifically necessary
object must be editable geometry or an explicitly documented Context 2 special real
photo; decorative sticker imagery is never a valid shortcut. FigureBench crops,
user references, Taste, and aesthetic preference cannot override either rule.

Pass `prompt-1/prompt.md` and every manifest attachment to the image-generation
model once and save its complete labelled result as `png1.png`.

## 5. Mandatory direct editable SVG1 transcription

Read [SVG diagnostics](references/svg-diagnostic.md). Give `png1.png` directly to
the current base Codex multimodal model and ask it to visually parse the pixels and
immediately write one complete `svg-diagnostic/svg1.svg`.

The instruction is: PNG1 is the sole visual source of truth; transcribe its labels,
colours, geometry, paths, groups, lines, arrows, placement, and relationships into
editable SVG source in one pass. This is transcription, not redesign, cleanup, or a
fresh plan. Text and vector elements remain independently editable.

The transcription must be adversarially faithful, not cosmetically approximate. Make
an inventory of every visible PNG1 object before writing SVG1, including small badges,
seals, medals, icons, markers, labels, and nested objects inside boxes. A badge or
icon that is present in PNG1 but absent, merged into a container, or materially
distorted in SVG1 is a failed transcription, not an acceptable simplification.
Likewise, if PNG1 uses a flat/solid box and SVG1 paints that box with a gradient,
translucent overlay, glow, or filter, record the mismatch for repair. Do not let a
visually smoother SVG1 conceal a lost object or changed visual grammar.

Do not use HTML/canvas, Python, draw.io, tracing/conversion utilities, local
programmatic reconstruction, hand-redrawing from the Methodology, or a single
embedded raster wrapper. Deterministic local tools begin only after SVG1 exists. If
the base model cannot perform the direct transcription, or the result fails
editability, stop and report failure at the SVG1 stage. Never silently substitute a
locally handcrafted SVG.

```bash
python scripts/figure_workflow.py inspect-svg --run RUN
python scripts/figure_workflow.py render-svg --run RUN
```

The render command creates `svg-diagnostic/png1.5.png`. PNG1.5 exists only so a VLM
can see what the editable transcription preserved or destabilized.

## 7. Diagnosis and approved SVG crops

Compare PNG1, SVG1, PNG1.5, Contexts 1–3, and original evidence. Give exactly one
verdict per Context 2 component in `svg-diagnostic/diagnosis.json`:

- `keep`: faithfully preserved and reusable;
- `accept_variation`: changed or simplified but scientifically sound;
- `patch`: correct a bounded defect in size, position, colour, label, or geometry;
- `reject`: remove an element that is fake, decorative, unstable, or has no valid
  scientific role; if a scientific role must remain, use `replace` instead;
- `replace`: retrieve a mature human-authored treatment and supply at least one
  mapped replacement crop for that component.

Scientific logic outranks polish. Slight position/angle variation in clear simple
geometry may pass. A complex diffusion view may simplify when its meaning survives.
A fake bulb, cartoon substitute, wrong photo/object, meaningless abstraction, or
directional/logical error must be rejected or replaced. For `replace` (and for any
`reject` that will be substituted rather than deleted), return to domain-paper
SVG/figure crops or FigureBench and save a mapped replacement under
`references/web/crops/replacements/` with its manifest. Prompt 2 compilation must
fail when a `replace` component has no mapped replacement crop.

The comparison is an active correction gate. For every component, state what PNG1
shows, what SVG1/PNG1.5 preserved or changed, and what PNG2 must do. A gradient that
covers a formerly flat box, a missing badge/seal/medal/icon, an occluded label, or a
broken relationship cannot receive `keep` or `accept_variation`; it must become
`patch`, `reject`, or `replace` with an explicit repair instruction. Do not crop a
known-defective gradient or missing-object region as approved SVG evidence. Either
crop only a qualified neighbouring treatment or provide a provenance-safe replacement
crop. Prompt 2 must actively modify PNG1 according to this audit; PNG1.5 is not a
passive proof image whose findings can be ignored.

Only visually useful `keep`, `accept_variation`, or `patch` regions may enter the
approved SVG crop request. Save VLM coordinates in
`svg-diagnostic/approved-crops/request.json`, then run:

```bash
python scripts/figure_workflow.py validate-diagnosis --run RUN
python scripts/figure_workflow.py crop-svg --run RUN
```

The crop command writes the separate
`svg-diagnostic/approved-crops/manifest.json`. PNG1.5 itself is diagnostic-only: do
not attach it, quote it as an image input, or otherwise expose it to Prompt 2.

## 8. Prompt 2 and final PNG2

Compile Prompt 2:

```bash
python scripts/figure_workflow.py build-prompt2 --run RUN
```

Its image attachments are exactly the original `png1.png`, diagnosis-approved SVG
crops, and any mapped replacement crops. Contexts 1–3 and the Methodology remain
textual evidence. `prompt-2/attachments.json` must never contain PNG1.5 or an SVG
diagnostic-render role.

Prompt 2 tells the image model component by component what to preserve, accept,
patch, reject, and replace. Modify PNG1 rather than recreating an unrelated figure;
use approved SVG crops only for their declared human-edited visual treatment and
use replacement crops only for rejected/replaced targets. Pass this bundle to the
image-generation model and save the result as `png2-final.png`.

PNG2 is final. Do not transcribe PNG2 to SVG or begin another diagnostic loop. Write
the canonical `run-manifest.json`, then verify deterministic provenance:

```bash
python scripts/figure_workflow.py validate-run --run RUN
```
