---
name: FigFox-Gen-skill
description: Generate a scientific figure PNG from Methodology and optional references. Only an explicit scientific or research poster request uses the bundled poster-generation branch.
metadata:
  short-description: Build evidence-guided single-pass scientific figures
---

# FigFox-Gen-skill

## Choose the requested artifact first

The default is a scientific paper figure: methodology diagrams, architecture figures and other research illustrations follow the V3 figure workflow below.

Use the bundled [poster-generation branch](skills/posfox-gen/SKILL.md) **only when the user positively and explicitly asks to make a scientific/research poster, academic conference poster, 科研海报 or 学术海报**. A paper PDF, page size, poster-shaped reference, quoted poster text, or a comparison with posters does not request that artifact. Negated requests such as “不要做海报” stay out of the poster branch. An explicit `$posfox-gen` invocation without clear poster intent needs clarification before entering that branch.

For a qualifying poster request, read that local Skill and follow only its generation-only workflow, ending with PNG delivery. Do not also run the scientific-figure planning pipeline below. For all other requests, keep the existing scientific-figure workflow; do not silently promote a figure request into a poster task.

Turn Methodology into one source-grounded PNG1 through the updated content-first workflow while preserving the original Creative Director's complete role. All new runs use `workflow_policy: "svg-reference-v1"` in `input/style-brief.json`. Old library-mode runs remain replayable archives, not new-run defaults. See [SVG workflow and schemas](references/svg-reference-workflow.md).

## 1. Identify the task track and inspect genuine SVG figures

Read Methodology first. Identify the task track and inspect complete original architecture figures from about two relevant scholarly papers when genuine SVGs are available. Every newly retrieved image reference—same-track, replacement, topology, global style, frame/arrow or dedicated colour reference—must have a genuine vector SVG source. Do not inspect a retrieved PNG/JPEG/WebP, PDF raster snapshot or an SVG wrapping an embedded bitmap as a substitute. Do not rename formats, trace a raster, or invent an SVG source. A local display rendering made from the retained SVG is a viewing/attachment derivative, never a retrieved raster reference. Retain the original SVG and provenance; preserve actual source CSS when needed to render it correctly. If a necessary SVG is unavailable, report the gap instead of silently relaxing the rule. Plain textual scientific sources such as a paper/model card are not image references.

Record observed transmission, input/output, intermediate artifacts, functional grouping, actual internal topology and repeated terms. Distinguish shared conventions from one paper's design. Inspect nesting, parallel/repeated units, node degree, split/merge semantics and meaningful symbols/operators—not just arrow directions. Add/multiply, concatenate, gates and state marks are included only when the current Methodology supports them. Never transplant a peer's internal network into an undisclosed model.

## 2. Filter useful constructions and collect SVG replacements

Classify the observations as essential, non-essential or a justified partial match for our Methodology. Preserve a stable visual-needs anchor. For each retained need, record need/location → actual observed SVG construction → our own source-grounded content. Native abstract geometry is allowed; no illustration quota and no image for every block. Context2 preserves exact scientific components, conditions, labels and dependencies independently of style references.

Reuse suitable inspected local SVGs first, otherwise find source SVGs in other tracks. Record whether a source is direct content, a crop or construction evidence. Never present another study's result as our evidence. Preserve complete useful style language: font character, linework, frames, arrowheads, spacing, density and meaningful local constructions. Do not reduce a good reference to disconnected shape adjectives. Keep valid caches and stop when actual needs are covered.

## 3. Set content and narrative before composition

Write our own exact visible strings and shortest accurate narrative. Count readable labels in peer figures with a stated scope; choose density for the current content. About 100 English words is a reference, not a quota; compiler maximum 160, with scientific justification above 100. Never pad or shrink text to fill a frame. Let content and meaningful grouping determine the major regions. Supporting internals remain coarse unless they explain the actual contribution.

## 4. Collect frame/style evidence and a separate complete palette SVG

Choose useful frame/text/arrow grammar from a neighboring track's genuine SVG. This supplies visual language, not foreign scientific topology or a fixed whole composition.

Separately select one COMPLETE SVG figure specifically for colour. Its paper may be very unrelated to our task. New runs do not select from a palette library. Keep the complete source, exact original paint values and any linked source CSS; a random swatch screenshot or a cropped colour patch is insufficient. Frame/style and palette references may be different figures.

Record not only colours but their observed spatial relationships: which neighbours are compatible, which strong colours are separated by white/neutral space, how pale support relates to deep marks, where emphasis sits and how much area remains white. These are source observations for the Creative Director, not an upstream colour lock. Derived tints, shades, lower-saturation tones, analogous neighbours and compatible neutrals retain the original mature colour rules and cite the source/base role.

## 5. Creative Director owns colour, whole composition and local ideas

Perform one real Creative Director pass using Methodology, visual needs/correspondences, COMPLETE useful references and the dedicated colour SVG. Preserve ALL original creative capabilities: whole-figure style integration, purposeful grouping and innovation emphasis, meaningful local visuals/canonical constructions, typography, colour, density, frames and routes. Add new evidence and constraints without removing those capabilities or turning the Director into a box-filling executor. Do not confuse creative capability with adding decoration.

**First colour.** Director chooses the palette from the source observations and justified derivatives. Retain the mature principles: usually 1–2 dominant families, harmonious analogous pale neighbours, deeper meaningful marks, separated strong contrast foci, readable dark/black lettering, restrained coloured area. More hues require lower saturation and area; no universal invented contrast threshold. Keep white wherever colouring is unnecessary. Pale base-frame fills are allowed when useful; emphasize actual mechanisms. Titles and unimportant objects receive no automatic colour fill, title strip or dark underlay. User recolouring triggers a Director review of the entire adjacency/separation and emphasis plan, not independent HEX swaps.

**Then frames and routes together.** Set base-frame positions BEFORE drawing routes. Let content size and narrative determine their proportions; regular alignment is useful, but equal cards and a filled rectangular silhouette are not mandatory. Use only basic straight lines or a single simple smooth curve where turning is needed. No staircase/zigzag, complicated perimeter pipes or maze-like detours. Complex routing is evidence of a layout problem: reposition or regroup instead of adding bends. Normally a frame has at most ONE input and ONE output, or only one input/output. A second port triggers layout/topology review; a third is a strong warning. Genuine source-supported multi-port exceptions require a reason and true internal landings; never delete dependencies or invent a merge to hide them. Preserve genuine loops with the simplest meaningful smooth path.

**Finally fill.** Use exact settled words, supported symbols and essential visual artifacts in the coherent whole style. Keep every title, word, symbol, image and local object fully inside its parent with padding. Only actual inter-frame connections travel outside. Trace each continuous shaft and attached arrowhead after placing contents.

Return three `design_intents`: layout, flow, density. Each starts 我想 and is at most 15 Chinese characters, or starts I want and is at most 15 English words; one line without commas. These are planning metadata, never image lettering. Also return `colour_decision` (chosen palette, rationale, region colours, adjacency review, whitespace plan), `topology_review`, exact visible-text/symbol inventory, notation aliases and concrete local ideas. Director creates the generation plan after making these choices; the caller must not pre-lock colour/geometry and then claim the Director chose them.

## 6. Compile, generate once and inspect pixels

Use [SVG workflow](references/svg-reference-workflow.md) and [compact generation](references/compact-generation.md) for artifacts and commands. Context3 uses `reference_strategy: "essential-only"`; an empty selected library-crop list is valid with complete native/construction coverage. Do not fabricate an unused raster FigureBench chain. The compiler retains exact graph relationships and requires the Director's source-verified colour decision before the image call.

New plans use `figfox-generation-plan-v2` with `routing_geometry.routing_policy: "simple"`. Straight lines have two points; a necessary smooth quadratic/cubic curve uses its explicit curve type and control handles, never orthogonal stair waypoints. Preflight rejects malformed paths, obvious obstructions, steps and unexplained multiple input/output ports. Curved-path clearance is sampled, so inspect actual pixels separately.

```sh
python scripts/figure_workflow.py init-style --run RUN --family architecture_2d --methodology /absolute/methodology.md
# Complete SVG references, Contexts1–3 and style brief; no pre-locked final geometry.
python scripts/figure_workflow.py build-creative-director-prompt --run RUN
# Actual Director writes creative-director/brief.json and input/generation-plan.json.
python scripts/figure_workflow.py build-prompt1 --run RUN
# One built-in image-generation call with actual manifest attachments → png1.png.
python scripts/figure_workflow.py validate-run --run RUN
```

The compact image packet contains scientific invariants, the Director's coherent visual language and colour relationships, exact components/routes, visible inventory, supported topology and scoped references. Keep full research and rejected alternatives local. Generate once; no automatic extra style-sheet image or repair loop. A user-requested rerun is a new recorded operation preserving the previous image and prompt. Inspect actual containment, topology/operators, true arrow landings, simple routes, text, colour adjacency, coloured area and whitespace. File tests are not evidence of visual quality. Deliver PNG as PNG; editable SVG reconstruction is a separate requested artifact. Briefly attribute essential constructions and the palette source, and report unresolved deviations honestly.
