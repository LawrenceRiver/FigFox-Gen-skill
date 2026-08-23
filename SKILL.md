---
name: genlike-scientific-svg
description: Generate publication-ready research figures with the structured, editable finish of a professional scientific SVG from any paper-figure brief, using aesthetic web references and local FigureBench RAG.
metadata:
  short-description: Make professional paper figures with SVG-grade structure
---

# GenLikeScientificSVG

Create a final raster research figure with the structured finish of a professionally drawn scientific SVG. Start from a **Figure Brief**, not only a methodology: it may be an idea, paper section, method, result, hypothesis, sketch, PNG/SVG, reference image, or a plain-language request. The editable SVG is the structural truth: it fixes scientific topology, module semantics, labels, hierarchy, and the primary reading order. The final image may improve rendering quality but may not alter that contract.

## Required workflow

Keep the reference work parallel. Do not expand it into a multi-agent serial chain.

1. Gather a Figure Brief, constraints, optional reference image, desired output size, and a local FigureBench index if available. Classify the request inline as **basic** (a familiar explanatory figure) or **custom** (a method-specific, result-specific, or novelty-bearing figure); do not make this classification a separate model call.
2. In parallel:
   - **Web domain figure search:** find candidate paper HTML/SVG figures relevant to the brief. For a basic brief, use the selected cases to establish a suitable professional SVG starting grammar; for a custom brief, also collect evidence of how the user's approach differs from common practice. It is an aesthetic search, not a recency search. Screen candidates against all of: clear composition, explicit hierarchy, sophisticated colour relationships, unified elements, purposeful whitespace, visible focal point, scientific credibility, and no ordinary-slide-deck appearance. Replace weak candidates; retain at least 3 and preferably 4+ strong references. Extract component conventions, layout cadence, emphasis treatments, palette relationships, and domain drawing conventions. The web work supplies novelty *evidence* only; it must not decide novelty emphasis.
   - **FigureBench semantic–structural RAG:** for custom briefs or when stronger professional geometry is needed, query a prepared local cache with the brief + inline Figure Intent + requested topology/figure type as primary signals. Use it as a VLM-facing library of abstract professional drawing grammar: module/container geometry, arrow rhythm, grouping, physical/process depiction, density, and SVG-like finish. Visual style is secondary. Return only top-k compact structure summaries. If no cache exists, give the user the one-command local setup from [FigureBench RAG](references/figurebench-rag.md); do not silently download a multi-GB dataset. Read that reference before indexing, querying, exporting, or deploying it.
   - **Colour palette RAG:** query the image-free grouped colour library with the brief's domain, figure type, comparison needs, and intended roles. It returns only 1--3 compatible groups of HEX/RGB values and colour-role labels; never retrieve, store, or pass palette screenshots. Read [Palette RAG](references/palette-rag.md) before editing the library or invoking the helper.
   - **User reference image:** when supplied, let the VLM learn its colour relationships and style directly. Do not run a separate OpenCV palette-extraction stage.
3. Do one **Scientific Topology Planning** pass. Extract Figure Intent inline, not as an extra model call: purpose, core claim, novelty focus, scope, and domain drawing question. Simultaneously perform scientific compression: remove redundant methodological prose; replace text that position or arrows can express; merge repeated modules. Plan modules, levels, arrows, layout, labels, and the few novelty claims that deserve emphasis.
   - **Color Planning** is an inline output of this same pass and does not add a model call. Select at most 1--3 palette groups; assign a canvas, ink/outline, surfaces, semantic module colours, and at most one novelty accent. State restrictions before rendering: avoid rainbow treatment, do not encode a category with colour alone, reserve the accent for the intended claim, and keep text/arrow contrast readable.
4. Render the plan to an SVG contract. Rasterise it to make **V0**, the first-version preview. SVG is allowed to combine vector elements with raster scientific assets, but it must preserve the logical skeleton.
5. Inspect V0 once with a VLM using the FigureBench geometry lexicon and selected RAG summaries. Apply exactly one **local SVG patch** for collisions, arrow direction, hierarchy, text density, label fit, whitespace, or non-copying geometry treatment. Do not redesign the figure or rerun topology planning.
6. Generate the final raster figure once. It may improve visual quality, scientific assets, icons, materials, and controlled geometry details, but it must retain the patched SVG's topology, module meanings, arrow relations, labels, and principal structure.

## SVG contract and typography

Represent the following explicitly before rasterisation: canvas/viewBox; element IDs; module bounds; z-order; input/output ports; arrow endpoints and direction; group bounds; label text bounds; wrapping rules; emphasis levels; and the Color Planning role-to-HEX assignments.

- Treat every labelled box as a text-fit constraint: measure the actual font, wrap with `tspan` where necessary, keep padding on all four sides, and ensure the label remains inside its own bounds at final raster dimensions.
- Keep arrow shafts and heads clear of labels and module interiors. Preserve a visible gap between unrelated modules and groups.
- Use geometric primitives deliberately: containers, nested enclosures, ribbons, brackets, nodes, directional channels, and restrained scientific texture. FigureBench geometry is a source of abstract grammar, not a tracing library.
- Complex scientific assets may remain raster or be generated as assets; do not force them into brittle SVG. The logic skeleton remains SVG.
- The one patch may alter only local geometry and presentation. It may not add/remove/reorder semantic modules, edit label meaning, invert or reroute relationships into a new topology, or change the primary reading order.

## FigureBench iteration rule

V0 is produced first from the SVG. The FigureBench retrieval may have been computed earlier in parallel, but its effect is applied only at the single inspection/patch gate.

Use RAG to derive an aggregate **geometry grammar** (container silhouettes, grouping/enclosure treatment, arrow rhythm, primitive vocabulary, visual density, and layout cadence). Use it to make the figure distinct, not similar to any retrieved example. Never trace a result, reproduce its distinctive arrangement, or pass the entire corpus to a model.

## Final-generation prompt boundary

Supply the patched SVG/render and state these invariants plainly:

- Preserve all labelled modules, their semantic roles, their arrow relations, and the primary layout.
- Preserve text exactly unless the user has asked for a wording change.
- Improve rendering only inside the SVG contract: scientific polish, asset detail, material, colour relationships, and allowed local geometric treatment.
- Preserve the Color Planning role assignments. Do not introduce new dominant colours or repurpose the novelty accent.
- Do not make it look like a generic slide or mimic a retrieved FigureBench figure.

## Delivery

Return the high-quality raster figure and retain the patched SVG as the editable skeleton. Report the chosen web-reference rationale, compact FigureBench structure summaries, and the one patch made. Do not publish raw FigureBench images or the local corpus. Only publish the safe embedding/metadata bundle after checking dataset and source licensing and receiving authority to deploy.
