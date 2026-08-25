# Model-facing prompt templates

## Context extraction

Read the Methodology once. Extract the domain, core topic, scientific mainline,
figure class, named concepts requiring domain-specific treatment, and explicit user
constraints. Then produce Context 1 as positive domain-convention evidence, Context
2 as an exact content-to-visual plan, and Context 3 as mapped FigureBench crops,
complete coverage, and one validated palette lineage. Do not turn web-search
explanations into figure prose.

## Prompt 1 generation

Generate PNG1 from the compiled Prompt 1 bundle. Follow its ten sections in order.
Use every FigureBench or domain crop only for its declared target component, `borrow`,
and `must_change` contract. Use the single approved base palette lineage only. Keep
scientific labels sparse and preserve the planned semantic reading order. Do not add
unmapped decorations, inferred palette colours, slide-deck cards, or fake cartoons.
The workflow has exactly two image-generation passes: this creates PNG1, and Prompt 2
creates final PNG2.

## Direct editable SVG transcription

PNG1 is the only visual truth. Inspect PNG1 and output a complete, editable SVG source
in one direct transcription. Faithfully retain its labels, colours, placement, and
visual relationships with editable text, geometry, paths, groups, lines, and arrows.

No HTML or canvas wrapper. No embedded raster wrapper. No Python, local scripting, or draw.io. No fresh SVG design from the prompt or Methodology. Do not embed PNG1 as one `<image>` element. This is transcription, not planning or redesign.

## Prompt 2 revision

Modify PNG1 once into PNG2 using the compiled Prompt 2 bundle. Respect all five
diagnostic blocks: preserve, accept variation, patch, reject, and replace. Treat
approved SVG crops and replacement crops as component-specific evidence, never as a
reason to redesign the whole figure. `reject` deletes an element with no valid
scientific role; if the role must remain, use `replace`. Every `replace` verdict
requires at least one mapped replacement crop. PNG1.5 and SVG diagnostic renders are
forbidden attachments. Before generating, actively compare every PNG1 component to
SVG1/PNG1.5. A gradient or translucent effect covering a flat PNG1 box is a `patch`
back to the single palette fill. A missing badge, seal, medal, icon, marker, label,
or connector is a failed transcription and must be `reject`/`replace` and restored
in PNG2. Never leave such a defect unchanged or classify it as `keep`. This is the
second and final image-generation pass; do not start a PNG2-to-SVG loop.
