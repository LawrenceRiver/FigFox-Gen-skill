---
name: FigFox-Gen-skill
description: Use when turning a scientific Methodology, with an optional reference image, into one evidence-grounded, human-editable final PNG figure.
metadata:
  short-description: Build evidence-guided single-pass scientific figures
---

# FigFox-Gen-skill

Turn a scientific Methodology into one source-grounded PNG1. New experimental runs use `input/style-brief.json` and the compact route below. Existing runs without that file use [legacy-generation.md](references/legacy-generation.md); do not load both workflows. This branch does not replace the installed skill automatically.

## 1. One peer-and-Methodology pass: the visual-needs anchor

Read Methodology and inspect actual figures from about two similar scholarly examples. In ONE synthesis, list only visual conventions that the examples share AND this Methodology actually needs. Check input/output representation, real specimens or thumbnails, internal topology, intermediate artifacts, iteration/comparison views and meaningful visual symbols. A PDF may use source pages, HTML a rendered page thumbnail, a graph actual topology; never add one just because a peer has it.

Keep this anchor in Context1's conventions: concept, observed peer commonality, Methodology relevance and useful visual form. Give selected needs stable IDs in the generation plan's `visual_needs`. Do not produce a second long paper summary or run another generic visual survey. A method-specific scientific detail remains in Context2; do not invent a peer commonality for it.

## 2. Parallel work from that one list

After the list exists, run independent work together:

- Find effective icon/illustration constructions for the listed needs. Prioritize scientific input/output, difficult symbols and meaningful small views. Do not search separately for every component or make a generic PDF/robot/code icon the default answer.
- Inspect a main style reference. State exactly what is liked: typography, line character, frame grammar, spacing or colour relationships. It is not permission to copy the whole source composition. If two references complement each other, give each an explicit trait/role. Use user references or local FigureBench/FigFoxBench when suitable.
- Match the approved palette group using the existing restrained colour principles. This may proceed alongside stylistic/creative work once liked traits are clear. Keep approved colour direction stable.

Reuse source-checked caches. Keep full source/crop/license evidence local. Drop rejected candidates and repeated research prose from handoffs. Search again only for a named unresolved visual need. Do not create separate C/reverse-C routing research: Creative Director should understand those ordinary layout patterns.

## 3. A grounded drawing correspondence, not another search round

For each selected visual need write one row: **need ID / location → observed borrowed construction → how our own scientific content is drawn**. These are `local_visuals` with `need_id`, target component, meaning, construction and source basis. `visual_needs` must be covered; unknown/missing need IDs fail compilation. Need IDs are not a requirement to retrieve an image for every graph component.

Context2 independently preserves exact scientific components, labels and directed relationships. Context3 retains inspected construction evidence and the selected palette. Keep scientific assumptions, fixed/trainable status, input/output types, gate inequalities and data-isolation boundaries explicit. Full research is not sent to the image model.

## 4. Creative Director + palette: settle one coherent visual system

Run one Creative Director ideation pass with the needs anchor and correspondence table. Combine reference traits into one construction language, not a collage. Make useful visuals prominent; do not reduce the method to empty equal cards. A planner should visibly plan something, a candidate show its actual artifact type, and inspection display real paired views when the method requires them.

Plan placement and arrows together. Straight connectors first; move modules to remove crossings and pointless bends. A person must be able to reproduce each arrow as one continuous source-border → target-arrowhead path. No empty-space starts, detached arrowheads, suddenly disappearing shafts or text-erased gaps. Use short branches and one clear perimeter lane for an actual return loop. Only after layout alternatives fail may an unavoidable crossing use a continuous bridge, modest rerouting, or distinguishable approved ink colours. Preserve every scientific edge. Record exact ports/routes once the layout is coherent.

Use the existing palette rules: related pale base regions, deeper meaningful marks, usually 1–2 dominant families and one separated warm focus. Dark/black labels are welcome. Keep typography coherent with the liked reference traits; no gray microcopy or automatic Times New Roman. Necessary short italic notes use readable dark Arial Italic. Stage labels, if needed, are `Stage 1/2/3` or `(a)/(b)/(c)` only. Semantic hand-drawn/native objects are welcome; pasted mascots, badges and generic decorative AI symbols are not.

## 5. Compile one drawing packet, generate, inspect

Use [compact-generation.md](references/compact-generation.md) for exact artifacts/schema/commands. The packet contains: short scientific invariants; overall framework; exact components and arrows; the needs-to-drawing table; liked main/font/detail reference traits; actual selected reference images with dimensions and scoped contracts; palette; final Creative Director construction decisions. It does not contain full PDF text, search transcripts, rejected candidates or duplicate Context JSON.

```sh
python scripts/figure_workflow.py check-installation --root .
python scripts/figure_workflow.py build-creative-director-prompt --run RUN
# Calling Harness performs one real ideation pass, saving brief.json.
python scripts/figure_workflow.py build-prompt1 --run RUN
# One image-generation call with prompt.md and actual manifest attachments -> PNG1.
python scripts/figure_workflow.py validate-run --run RUN
```

The skill's normal run ends at PNG1; no automatic second image, conversion or repair loop. An explicit user request for another comparison or connector repair is a separate recorded operation; preserve the prior image and actual prompt. File/provenance validation is not proof of scientific or aesthetic correctness. Inspect the actual output before calling it accepted.

Load [style-first.md](references/style-first.md) only for family/reference permission/colour details, [artifact-schemas.md](references/artifact-schemas.md) for original artifact schemas. Source availability or dataset membership alone is not redistribution permission. Keep user images and unresolved assets local. Never copy a reference's labels, scientific claims, photos or mascots into a new method.
