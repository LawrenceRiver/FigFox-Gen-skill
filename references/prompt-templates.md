# Model-facing prompt templates

## Context extraction

Read the Methodology once. Extract the domain, core topic, scientific mainline,
figure class, named concepts requiring domain-specific treatment, and explicit user
constraints. Produce Context 1 as positive domain-convention evidence, Context 2 as
an exact content-to-visual plan, and Context 3 as mapped FigureBench crops, complete
coverage, and one selected validated multi-colour palette group. Do not turn research explanations into
figure prose.
Context 1 must record the observed dominant-colour count from the retained scholarly
figures as an integer from 1 to 3; record the count, not the source colours.

At the start of each run, randomly select exactly one approved palette-library group
for Context 3. Record its id and all of its role-labelled colours; use `--seed` only
when reproducibility is required. Never silently reuse a previous run's group or
write a hard-coded palette into the image-generation prompt.

## Creative Director prompt

Run this bounded ideation pass after Contexts 1–3 and before PNG1. The Creative
Director proposes a concrete, scientifically relevant treatment for a planned
component; it does not generate PNG1 or redesign the whole figure. If the idea is
not already covered by the contexts, find a real scholarly paper figure available
as SVG or extractable SVG/HTML, inspect its pixels, and request only a targeted crop.
Return creative-director-brief-v1 with a brief and ideas containing the target
component, concept, visual intent, construction plan, and whether SVG evidence is
required. Every requested crop carries target_component_id, source_format: "svg",
HTTPS source and evidence URLs, nonempty borrow and must_change lists, and a
human-editability reason. Never invent a source, attach a complete paper figure,
copy its labels or palette, or use a sticker-like cutout. If no new evidence is
needed, state no_external_svg_needed and return no crop.

Before proposing a treatment, explicitly simulate a human editor's sequence: choose
the base canvas and simple geometry; build the meaningful structures; add plain
arrows; place concise exact text; then place a nearby explanatory visual. Prefer
real input samples and targeted scholarly crops for known topologies, grids, and
model diagrams. Reject fake topologies, repeated filler lines, irregular copied
grids, multi-colour fills inside one geometric block, decorative arrows, and
sticker-like objects. A subtle fill transition is allowed only on a planned base
shape; gradients inside blocks or used as decorative polish are rejected.

## Prompt 1 generation

Generate the final PNG1 from the compiled Prompt 1 bundle. The bundle includes the
validated Creative Director brief and any targeted paper-SVG crops. Use each crop
only for its declared component and construction contract; it is a variant
reference, not a source composition. Use every FigureBench or domain crop only for
its declared target component, borrow, and must_change contract. Use multiple colours
from the selected approved palette group; do not mix a second group. Keep scientific
labels sparse and preserve the
planned semantic reading order.

### Reference-fidelity lock

When a user reference is attached or explicitly cited, treat it as the canonical visual
specification. Match its composition, spacing, hierarchy, and visual grammar; preserve
its line weight, corner-radius, fill treatment, typography scale, arrow grammar, and
sample treatment wherever the Methodology permits. Change only labels, scientific
content, and geometry required by the Methodology. Do not beautify, complicate, stylize,
recompose, or switch to a different visual language because the model prefers it. Ignore
only generated-looking, fake, or decorative parts. Active colours still come only from
the selected palette group.

Use exactly the dominant-colour count observed in Context 1, never exceeding three.
Other swatches may appear
only as subordinate neutral, tint, shade, or support roles; they must not become a
fourth dominant hue.

PNG1 has two absolute first-pass prohibitions: no upper title-band formed by boxing
off the top of a module with a horizontal divider and centered title, and no
sticker-like cutout, clip-art badge, medal, seal, or pasted raster badge. Use inline
labels or editable geometry; only a scientifically necessary real photo may be a
special Context 2 treatment. These bans cannot be overridden by FigureBench crops,
user references, or Taste guidance.

This is the only image-generation pass. PNG1 is final; do not start an SVG
conversion, temporary render, diagnosis loop, second prompt, or second image.

The generated figure must follow the same human construction sequence: base first,
content second, plain connectors third, labels fourth, explanatory visuals last.
Use a real sample or an evidenced paper construction when one exists rather than a
generic placeholder. Regular grids and repeated geometry must be exact and each
geometric block must use a flat or single controlled fill; only a planned base shape
may use one subtle fill transition.

## Validation

The deterministic validator checks the single Prompt 1 bundle, attachment
provenance, the selected palette-group lineage, FigureBench crop replay, Creative Director source
contracts, and PNG1 validity. It does not inspect model calls or guarantee
scientific correctness.
