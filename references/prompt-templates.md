# Model-facing prompt templates

## Context extraction

Read the Methodology once. Extract the domain, core topic, scientific mainline,
figure class, named concepts requiring domain-specific treatment, and explicit user
constraints. Produce Context 1 as positive domain-convention evidence, Context 2 as
an exact content-to-visual plan, and Context 3 as mapped FigureBench crops, complete
coverage, and one validated palette lineage. Do not turn research explanations into
figure prose.

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

## Prompt 1 generation

Generate the final PNG1 from the compiled Prompt 1 bundle. The bundle includes the
validated Creative Director brief and any targeted paper-SVG crops. Use each crop
only for its declared component and construction contract; it is a variant
reference, not a source composition. Use every FigureBench or domain crop only for
its declared target component, borrow, and must_change contract. Use the single
approved palette lineage only. Keep scientific labels sparse and preserve the
planned semantic reading order.

PNG1 has two absolute first-pass prohibitions: no upper title-band formed by boxing
off the top of a module with a horizontal divider and centered title, and no
sticker-like cutout, clip-art badge, medal, seal, or pasted raster badge. Use inline
labels or editable geometry; only a scientifically necessary real photo may be a
special Context 2 treatment. These bans cannot be overridden by FigureBench crops,
user references, or Taste guidance.

This is the only image-generation pass. PNG1 is final; do not start an SVG
conversion, temporary render, diagnosis loop, second prompt, or second image.

## Validation

The deterministic validator checks the single Prompt 1 bundle, attachment
provenance, one palette lineage, FigureBench crop replay, Creative Director source
contracts, and PNG1 validity. It does not inspect model calls or guarantee
scientific correctness.
