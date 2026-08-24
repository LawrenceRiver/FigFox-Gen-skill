---
name: genlike-scientific-svg
description: Generate publication-ready research figures with the structured, editable finish of a professional scientific SVG from any paper-figure brief, using aesthetic web references and local FigureBench RAG.
metadata:
  short-description: Make professional paper figures with SVG-grade structure
---

# GenLikeScientificSVG

Create a final raster research figure with the structured finish of a professionally drawn scientific SVG. Start from a **Figure Brief**, not only a methodology: it may be an idea, paper section, method, result, hypothesis, sketch, PNG/SVG, reference image, or a plain-language request. The **Scientific Topology Plan** is the structural truth: it fixes module semantics, hierarchy, arrow relations, labels, and primary reading order. Do not first render a full SVG and use it as the image model's input. Instead, use exactly one **post-generation SVG correction** after the first image-model draft, then render that editable correction directly to the final PNG.

## Required workflow

Keep the reference work parallel. Do not expand it into a multi-agent serial chain.

1. Gather a Figure Brief, constraints, optional reference image, desired output size, and a local FigureBench index if available. Classify the request inline as **basic** (a familiar explanatory figure) or **custom** (a method-specific, result-specific, or novelty-bearing figure); do not make this classification a separate model call.
2. In parallel:
   - **Web domain figure search:** find candidate paper HTML/SVG figures relevant to the brief. Prefer a native SVG/HTML figure over a page screenshot; crop the relevant panel, legend, or structural region as a **temporary crop** for VLM inspection. For a basic brief, use the selected cases to establish a suitable professional SVG starting grammar; for a custom brief, also collect evidence of how the user's approach differs from common practice. It is an aesthetic search, not a recency search. Screen candidates against all of: clear composition, explicit hierarchy, sophisticated colour relationships, unified elements, purposeful whitespace, visible focal point, scientific credibility, and no ordinary-slide-deck appearance. Replace weak candidates; retain at least 3 and preferably 4+ strong references. Extract component conventions, layout cadence, emphasis treatments, and domain drawing conventions. The web work supplies novelty *evidence* only; it must not decide novelty emphasis or supply final colours. Do not publish temporary crops unless their licence explicitly permits it.
   - **FigureBench semantic–structural RAG:** for custom briefs or when stronger professional geometry is needed, query a prepared local cache with the brief + inline Figure Intent + requested topology/figure type as primary signals. Use it as a VLM-facing library of abstract professional drawing grammar: module/container geometry, arrow rhythm, grouping, physical/process depiction, density, and SVG-like finish. Visual style is secondary. Return only top-k compact structure summaries. If no cache exists, give the user the one-command local setup from [FigureBench RAG](references/figurebench-rag.md); do not silently download a multi-GB dataset. Read that reference before indexing, querying, exporting, or deploying it.
   - **Colour-source selection:** choose exactly one colour source for this render: either one approved image-free library group, or an ephemeral HEX/RGB group extracted from an aesthetically strong web SVG unrelated to the brief's domain. For the latter, explicitly reject any candidate whose declared source domain overlaps the Figure Brief or the selected domain references. A temporary crop may be made from that SVG to inspect its swatch/legend region, but retain only colour roles and exact HEX/RGB values; discard the crop and do not store its image, URL, thumbnail, or a persistent record. Do not mix sources, borrow colours from domain references, or ask the final model to invent or interpolate colours. Read [Palette RAG](references/palette-rag.md) before invoking the helper.
   - **User reference image:** when supplied, let the VLM learn composition and rendering style directly. Its colours do not expand the permitted colour set unless they independently satisfy the selected colour-source rule. Do not run a separate OpenCV palette-extraction stage.
3. Do one **Scientific Topology Planning** pass. Extract Figure Intent inline, not as an extra model call: purpose, core claim, novelty focus, scope, and domain drawing question. Simultaneously perform scientific compression: remove redundant methodological prose; replace text that position or arrows can express; merge repeated modules. Plan modules, levels, arrows, layout, labels, and the few novelty claims that deserve emphasis.
   - **Color Planning** is an inline output of this same pass and does not add a model call. Declare the selected source, its domain (when it is a cross-domain SVG), every exact allowed HEX value, and role assignments for canvas, ink/outline, surfaces, semantic modules, and at most one novelty accent. Compile it with `python scripts/figurebench_rag.py colour-contract --plan-json colour-plan.json`. The renderer may use only exact HEX values in the compiled contract: no new, shifted, blended, or activated colours. State restrictions before rendering: avoid rainbow treatment, do not encode a category with colour alone, reserve the accent for the intended claim, and keep text/arrow contrast readable.
4. Emit a compact **Image Generation Contract** from the plan: canvas/aspect; named modules; relative bounds and grouping; directional relations; primary reading order; exact label strings; allowed scientific assets; selected reference crops; FigureBench summaries; and the compiled colour contract. This is structured data/prompt context, not a rendered SVG.
5. Call the selected image-generation model to **directly generate the first scientific raster draft** from the Image Generation Contract and approved reference crops. It must not use a rendered SVG as its input. It must **generate every required label directly** inside its specified module, rather than dropping text or leaving blank boxes. The model may improve assets, icons, materials, and controlled geometry details, but it must preserve module meanings, arrow relations, principal structure, label content, and the compiled colour contract.
6. Inspect the generated raster once with a VLM using the FigureBench geometry lexicon and selected RAG summaries. Explicitly check for **missing, incorrect, or overflowing text**, collisions, arrow direction, hierarchy, density, whitespace, accidental gradients/glow/shadows on structural colour blocks, inconsistent geometry, and non-copying treatment. Compile the original Image Generation Contract, the geometry lexicon, and this inspection into one editable **post-generation SVG correction** with `python scripts/figurebench_rag.py svg-repair-brief --generation-contract-json image-generation-contract.json --lexicon-json geometry-lexicon.json --inspection-json inspection.json --output svg-repair-brief.json`. Use it to lock boxes, arrows, labels, flat exact-HEX fills, margins, and geometry. Preserve complex scientific assets as placed raster assets. Render the corrected SVG directly to the final PNG; **do not send it to a second image-generation call**. Do not redesign the figure or rerun topology planning.

## Image Generation Contract and typography

Represent the following explicitly before the image call: canvas/aspect; named module bounds; z-order; input/output ports; arrow endpoints and direction; group bounds; exact label strings and intended label bounds; wrapping rules; emphasis levels; and the Color Planning role-to-HEX assignments.

- Treat every labelled box as a text-fit constraint: specify the label string, font hierarchy, line breaks, and padding in the Image Generation Contract, and require the image model to render it inside the stated bounds.
- Keep arrow shafts and heads clear of labels and module interiors. Preserve a visible gap between unrelated modules and groups.
- Use geometric primitives deliberately: containers, nested enclosures, ribbons, brackets, nodes, directional channels, and restrained scientific texture. FigureBench geometry is a source of abstract grammar, not a tracing library.
- Complex scientific assets are expected to be raster/generated assets in the first draft. The SVG correction may place and crop them, but must not replace them with invented vector icons.
- The one SVG correction may alter only local geometry and presentation. It may not add/remove/reorder semantic modules, edit label meaning, invert or reroute relationships into a new topology, or change the primary reading order.
- Structural colour blocks in the SVG must use flat exact-HEX fills: no gradients, glow, texture, or decorative shadow. Use one consistent stroke family, corner family, arrowhead family, and declared grid/margin rhythm.
- Require every label, legend, panel letter, and annotation in the Image Generation Contract. The image model generates them as part of the scientific figure; do not pre-emptively remove text from its prompt.

## FigureBench iteration rule

The FigureBench retrieval may be computed earlier in parallel, but its effect is applied only at the single inspection/SVG-correction gate after the direct image-generation call.

Use RAG to derive an aggregate **geometry grammar** (container silhouettes, grouping/enclosure treatment, arrow rhythm, primitive vocabulary, visual density, and layout cadence). Use it to make the figure distinct, not similar to any retrieved example. Never trace a result, reproduce its distinctive arrangement, or pass the entire corpus to a model.

## Final-generation prompt boundary

Supply the Image Generation Contract and approved cropped references, then state these invariants plainly:

- Preserve all labelled modules, their semantic roles, their arrow relations, and the primary layout.
- Generate every required label directly and preserve it exactly unless the user has asked for a wording change. Do not omit text from the image-generation prompt or leave text boxes empty.
- Improve rendering only inside the Image Generation Contract: scientific polish, asset detail, material, colour relationships, and allowed local geometric treatment.
- Use only exact HEX values in the compiled Color Planning contract. Do not introduce, shift, blend, or activate any other colour, and do not repurpose the novelty accent.
- Do not make it look like a generic slide or mimic a retrieved FigureBench figure.

## Delivery

Return the final PNG, the editable SVG correction, and the Image Generation Contract. Report the chosen web-reference rationale, compact FigureBench structure summaries, the image model used, and the one SVG correction made. Do not publish raw FigureBench images or the local corpus. Only publish the safe embedding/metadata bundle after checking dataset and source licensing and receiving authority to deploy.
