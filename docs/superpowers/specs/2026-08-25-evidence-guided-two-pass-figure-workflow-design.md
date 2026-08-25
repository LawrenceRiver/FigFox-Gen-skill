# Evidence-Guided Two-Pass Scientific Figure Workflow

## Status

Approved workflow design for a full repository rewrite. This specification replaces the current topology-first, one-PNG, optional-SVG design.

## Goal

Turn a Methodology and an optional user reference image into a final scientific architecture figure through two image-generation passes. The first pass tests a detailed, evidence-grounded visual design. A direct editable-SVG transcription then exposes which parts of that design are structurally stable, semantically valid, and human-editable. The second image-generation pass modifies the original PNG using that diagnosis and selected SVG crops.

The workflow must look as though a human could have assembled its components in draw.io, drawn them deliberately by hand, or supplied a real photographic crop. It must not rely on decorative imagery that merely looks plausible to an image model.

## Non-goals

- SVG1 is not the final deliverable.
- PNG1.5 is not an input to the second image-generation pass.
- Codex must not hand-author SVG1 from the Methodology, prompt, HTML, Python, draw.io, or a fresh vector plan.
- FigureBench is not reduced to aggregate metadata; the workflow must inspect concrete candidate images and component crops.
- Taste guidance must not override scientific meaning, explicit user constraints, domain conventions, or the chosen single-palette rule.
- PNG2 does not enter another SVG-diagnostic loop.

## Canonical artifact flow

```text
Methodology + optional user reference image
  -> Context 1: domain visual conventions
  -> Context 2: content-to-visual plan
  -> Context 3: FigureBench crops + one palette + taste constraints
  -> Prompt 1 bundle, including mapped crops
  -> PNG1
  -> direct one-pass editable SVG transcription by the base Codex model
  -> SVG1
  -> deterministic temporary render PNG1.5
  -> SVG diagnosis + approved SVG crops
  -> Prompt 2 bundle: PNG1 + approved SVG crops + diagnosis; never PNG1.5
  -> final PNG2
```

## Responsibility boundary

`SKILL.md` controls every judgment that requires a language or vision model:

- domain and mainline extraction;
- scholarly web search and figure screening;
- VLM comparison of domain figures;
- Methodology compression and content-to-visual planning;
- FigureBench candidate and crop selection;
- palette and taste judgment;
- Prompt 1 and Prompt 2 authoring;
- PNG1 and PNG2 image-generation calls;
- direct PNG1-to-SVG1 transcription by the base Codex model; and
- VLM diagnosis of PNG1, SVG1, PNG1.5, and the original evidence.

Python helpers provide deterministic support only:

- artifact schemas and validation;
- run-directory and manifest management;
- FigureBench candidate preparation and crop-coordinate execution;
- one-palette validation;
- Prompt 1 and Prompt 2 bundle compilation;
- SVG editability checks and deterministic SVG rendering;
- SVG crop-coordinate execution; and
- end-to-end completeness checks.

Python must not call a search provider, VLM, image-generation model, or SVG-generation model. This keeps the Skill portable and preserves direct base-model SVG transcription.

## Stage 0: input and field extraction

The required input is a Methodology. A user reference image is optional.

The language model reads the Methodology once and records:

- scientific domain;
- core topic;
- method mainline;
- likely figure class;
- named concepts that require domain-specific visual treatment; and
- exact user constraints.

This stage is semantic classification, not a visual planning pass.

When a user reference image is present, it has strong influence over structure and basic visualization choices. It may express a colour preference, but it is not a palette source. VLM inspection must distinguish human-editable or photographic evidence from obviously model-generated decoration. Only the former is eligible for reuse.

## Stage 1: scholarly visual search and Context 1

Search for three or four papers from the detected domain. Prefer arXiv when it exposes useful source material, and prefer accessible SVG/HTML figures. When those are unavailable, use other credible paper sources and clean figure crops.

The search is for visual conventions, not recency. Each retained paper figure must be screened for scientific relevance and visible construction quality.

The VLM compares the retained figures and records all recurring, Methodology-relevant similarities:

- repeated domain objects and how they are depicted;
- common intermediate models or representations;
- recurring structural relationships and flow patterns;
- shared professional terminology and label conventions;
- repeated human-authored shapes, sketches, diagram idioms, or photographic crops;
- typical grouping, hierarchy, and emphasis; and
- disagreements or one-off treatments that must not be mistaken for a convention.

The output is `context-1-domain-conventions.json`. It is a positive evidence list, not a prose literature review.

Every convention record contains its concept, recurrence evidence, visual treatment, terminology, eligible source crops, and relevance to the current Methodology.

## Stage 2: content-to-visual planning and Context 2

The model combines the Methodology, Context 1, and optional user reference image to rewrite the method as a concise architecture-figure mainline.

It first designs the scientific relationships in text:

- blocks and named structures;
- input, transformation, intermediate representation, and output;
- hierarchy, grouping, and direction;
- exact labels; and
- the role of every proposed visual element.

It then assigns each content unit a visual treatment. A normal treatment is eligible only when it is:

- basic geometry;
- a recurring human-authored convention found in the domain papers;
- a deliberate hand-drawn treatment;
- a draw.io-like editable construction; or
- a real photographic crop when the scientific meaning requires it.

Any other treatment is marked `special`. A special treatment must explain why it is necessary and how a human would make it: geometric construction, stylus drawing, or a real-world photograph. Unsupported generated decoration is rejected before Prompt 1.

The output is `context-2-content-visual-plan.json`. Each item maps exact scientific content to a visual treatment, construction provenance, semantic purpose, planned label, relationship, and special-case rationale when applicable.

## Stage 3: FigureBench visual kit, palette, taste, and Context 3

Context 2 determines which concrete components are needed, such as rectangles, containers, arrows, nodes, grouped regions, scientific objects, and structural illustrations.

The Skill bundles exactly 30 complete FigureBench development images in `assets/figurebench-references/`. They form the normal-user reference library and are installed with the Skill; users are not asked to download FigureBench. Each image must have verified redistribution terms and attribution, a stable id, source id, component tags, layout tags, human-editability signals, and a short human-authored index description. The complete multi-gigabyte FigureBench dataset is used only by maintainers when curating a future revision of these 30 references.

The 30-image library must cover a deliberately diverse set of human-editable scientific-figure treatments: basic and angled containers, arrows and branching flows, nested groups, staged architectures, nodes and matrices, simplified scientific processes, hand-drawn treatments, eligible photographic crops, layout families, spacing rhythms, and stroke families. Selection favors reusable construction grammar and scientific clarity rather than popularity, visual complexity, or source colour. Official test images are never used.

For each run, the helper ranks the bundled library against Context 2. The VLM must inspect at least two complete reference images, then continue selecting references until the planned visual vocabulary is covered. Coverage, not a fixed image count, is the stopping condition: every required geometry, frame/container family, connector treatment, layout relationship, and special visualization in Context 2 must have a credible human-editable reference or an explicit basic-geometry justification. The VLM inspects the actual complete images rather than only metadata. It selects and crops useful component regions, observing:

- shape and silhouette;
- angle and perspective;
- border, corner, and stroke treatment;
- grouping and enclosure;
- connection and arrow construction;
- spacing and human-editable finish; and
- how the component can be varied without copying a source arrangement.

Each selected FigureBench reference must retain both:

1. a crop image; and
2. a textual crop contract describing which target component it guides, what may be borrowed, what must change, and why the result remains a variant.

The complete bundled image is a selection source; the per-run crop is the Prompt 1 attachment. Prompt 1 does not receive unexplained complete figures. Context 3 records a coverage matrix that maps every planned visual need to at least one crop or basic-geometry justification and explains why reference collection is complete.

### Single-palette rule

Each run starts from exactly one approved palette-library group. Neither the user reference image nor FigureBench supplies the active palette.

When the base group is too narrow for the planned semantic roles, perform a targeted web colour-relationship search around that group. Added colours must have an explicit relationship to the base group, such as a tint, shade, tone, analogous neighbour, compatible neutral, or controlled contrast. Record the exact HEX/RGB value, relationship type, intended role, and web evidence. Do not select or borrow a second palette-library group.

The run therefore retains one palette lineage: one approved base group plus optional, evidenced related-colour extensions. The user reference may guide colour emphasis or restraint, but its pixels do not expand the allowed set. The contract records all exact allowed HEX/RGB values and their intended roles.

### Taste guidance

The rewrite retains only the useful core language of a visual taste skill. Taste is a soft constraint for palette balance, spacing, hierarchy, rhythm, restraint, and human-edited finish.

Priority is:

1. scientific and semantic correctness;
2. explicit user constraints and eligible user-reference evidence;
3. recurring domain visual conventions;
4. human editability and construction provenance;
5. the one base-palette lineage and its evidenced related-colour extensions; and
6. taste guidance.

Taste cannot authorize a new colour source, decorative element, or scientifically misleading composition.

The output is `context-3-visual-kit.json`, accompanied by a crop manifest and crop files. It contains FigureBench selections, crop contracts, the one palette, layout advice, and taste soft constraints.

## Stage 4: Prompt 1 bundle

Prompt 1 combines the Methodology, Context 1, Context 2, Context 3, the optional user reference image, domain-paper crops, and mapped FigureBench crops.

Every crop must have an explicit target. The model must be told which component it guides, which properties to borrow, and which source-specific properties to vary. Unmapped crop dumping is invalid.

Prompt 1 follows this order:

1. figure purpose and scientific mainline;
2. exact block and structure names;
3. semantic relationships and reading order;
4. content-to-visual mapping for every element;
5. crop-to-component mapping;
6. single-palette contract;
7. layout and taste constraints;
8. exact labels and text-density limits;
9. anti-AI visual constraints; and
10. direct PNG generation instruction.

Methodology prose is compressed aggressively. Explanatory material learned during web research helps the model understand the method but is not copied into the figure. Figure text is limited to block names, structure names, necessary labels, and relationships.

Prompt 1 prohibits by default:

- decorative visuals unrelated to text;
- unexplained dots, floating symbols, or purposeless boxes;
- arbitrary high-contrast colours between adjacent modules;
- shapes with no human construction provenance;
- numbered `1/2/3/4` planning labels;
- the generic blue-title-strip-inside-every-box pattern;
- repeated card grids that make the figure look like a slide deck; and
- fake cartoon objects when a real crop or editable scientific geometry is expected.

An explicit user requirement may override the numbering or title-strip prohibition for a genuine special case.

The output is a validated Prompt 1 bundle plus its attachment manifest. The first image-generation call consumes this complete bundle and generates `PNG1`.

## Stage 5: direct editable SVG transcription

The original `PNG1` is passed directly to the base Codex multimodal model with one task: inspect the image and immediately output a complete editable SVG transcription.

This is not a planning or redesign stage. The instruction must require:

- the original PNG as the visual source of truth;
- complete SVG source in one direct transcription;
- editable text, geometry, paths, groups, lines, and arrows;
- faithful labels, colours, placement, and visual relationships;
- no HTML or canvas wrapper;
- no Python, draw.io, or local programmatic reconstruction;
- no fresh SVG designed from the prompt or Methodology; and
- no SVG that merely embeds PNG1 as one raster `<image>`.

The output is `SVG1`.

The deterministic helper validates that the file is SVG, is parseable, contains editable vector/text structure, and is not only a raster wrapper. It then renders `SVG1` to `PNG1.5` for VLM diagnosis.

If direct transcription fails or produces a non-editable raster wrapper, the run reports SVG transcription failure. The workflow must not silently substitute a locally hand-authored SVG.

## Stage 6: editable-SVG diagnostic pass

`SVG1` and `PNG1.5` are diagnostic artifacts. They are not the final design and are not automatically cleaned up into a deliverable.

The VLM reviews PNG1, SVG1, PNG1.5, all three contexts, and the original reference evidence. It asks what the vector decomposition reveals about PNG1:

- Which colours, layouts, and geometries survived cleanly?
- Which visual ideas are semantically correct and human-editable?
- Which changes are harmless simplifications?
- Which elements became unstable because PNG1 was visually overcomplicated?
- Which elements are fake, decorative, semantically wrong, or logically wrong?

Every reviewed element receives one verdict:

- `keep`: faithfully preserved and ready to carry into PNG2;
- `accept_variation`: changed, but still meaningful and visually valid;
- `patch`: concept is correct but size, position, colour, label, or geometry needs a bounded correction;
- `reject`: visual concept is invalid or has unacceptable AI-generated character; or
- `replace`: retrieve a mature human-authored treatment from domain figures or FigureBench.

Decision rules include:

- A simple geometric element may keep a difficult angle when it remains clear and semantically correct.
- A complex process such as diffusion may be simplified when the simplified version still makes scientific sense.
- A real photographic crop must not be replaced by an invented cartoon or false geometry.
- A fake bulb, decorative icon, unstable abstract object, or meaningless shape is rejected.
- Any semantic, directional, or basic logical error overrides visual appeal.

Rejected and replacement elements trigger targeted return to domain-paper SVGs or FigureBench before Prompt 2.

The output is `svg-diagnosis.json` plus a small manifest of approved SVG crops. Only regions whose SVG treatment is visually correct and useful for PNG2 are cropped. Each crop records the target component and the diagnosis that justifies its use.

`PNG1.5` is never attached to Prompt 2.

## Stage 7: Prompt 2 and final PNG2

Prompt 2 treats PNG1 as the image to modify. Its evidence includes:

- the original Methodology and Contexts 1–3;
- the original user reference image when present;
- PNG1;
- the diagnosis list;
- approved SVG crops; and
- newly retrieved replacement crops for rejected elements.

Prompt 2 tells the image-generation model exactly what to preserve, accept, patch, reject, and replace. Approved SVG crops communicate a more human-editable visual feel, including useful small colour and geometry differences, without making PNG1.5 an input.

The second and final image-generation call modifies PNG1 according to this evidence and produces `PNG2`.

PNG2 is the final figure. There is no second SVG transcription or SVG-diagnostic loop.

## Run artifact layout

```text
run/
  input/
    methodology.md
    user-reference.*                 # optional
  context/
    context-1-domain-conventions.json
    context-2-content-visual-plan.json
    context-3-visual-kit.json
  references/
    web/manifest.json
    web/crops/
    figurebench/candidates.json
    figurebench/crops/request.json        # preserved VLM coordinates/contracts
    figurebench/crops/manifest.json
    figurebench/crops/
  prompt-1/
    prompt.md
    attachments.json
  png1.png
  svg-diagnostic/
    svg1.svg
    png1.5.png
    diagnosis.json
    approved-crops/request.json           # preserved VLM crop request
    approved-crops/manifest.json
    approved-crops/
  prompt-2/
    prompt.md
    attachments.json
  png2-final.png
  run-manifest.json
```

## Repository rewrite

The existing repository is rewritten around this artifact chain.

### Skill and references

- Replace `SKILL.md` with the canonical two-pass workflow and hard invariants.
- Rewrite `agents/openai.yaml` so the default prompt starts the complete workflow.
- Replace old FigureBench and palette references with focused references for artifact schemas, FigureBench visual selection, prompt templates, taste rules, and SVG diagnostics.
- Add exactly 30 curated complete images under `assets/figurebench-references/` plus an attribution and visual-index manifest.
- Rewrite both public READMEs only after behavior, helpers, and tests agree.

### Python package

Split deterministic responsibilities into focused modules:

- `artifacts.py`: schemas, run manifests, and completeness validation;
- `figurebench.py`: candidate preparation and crop-manifest execution;
- `palette.py`: single-palette selection and validation;
- `prompts.py`: Prompt 1 and Prompt 2 bundle compilation;
- `svg_diagnostics.py`: SVG editability checks, temporary rendering, diagnosis validation, and SVG crop manifests.

Legacy retrieval code may be retained only where it supports candidate preparation. Aggregate-only outputs and the optional-SVG brief are removed or replaced.

### CLI

Expose deterministic commands for:

- validating Contexts 1–3;
- ranking FigureBench candidates and validating adaptive visual-reference coverage;
- applying VLM-provided crop coordinates;
- compiling and validating the one palette;
- building Prompt 1 and Prompt 2 bundles;
- validating and rendering SVG1;
- validating the SVG diagnosis and approved crops; and
- checking the complete run manifest.

No CLI command performs model reasoning that belongs to the Skill.

## Failure handling

- Fewer than three strong domain figures: continue searching or report insufficient evidence; do not invent a convention list.
- No native SVG paper figure: use credible HTML/PDF figure crops while recording the source format.
- Bundled FigureBench reference pack is missing any of its 30 indexed images: fail installation validation before starting a run.
- Fewer than two inspected bundled references: fail Context 3 validation.
- Any Context 2 visual need lacks a reference crop or explicit basic-geometry justification: continue reference collection and block Prompt 1.
- Crop without a target contract: reject it from the prompt bundle.
- Missing base palette-library group, a second palette-library group, or a related colour without web evidence: fail validation.
- Direct SVG transcription failure: report failure and do not hand-author a substitute.
- SVG1 is only an embedded raster: fail editability validation.
- PNG1.5 appears in Prompt 2 attachments: fail bundle validation.
- Diagnosis lacks a verdict for a planned component: fail Prompt 2 compilation.

## Verification strategy

Tests must verify observable behavior and artifact invariants, not merely search documentation for phrases.

Required coverage:

- schema tests for all three contexts and manifests;
- adaptive candidate selection with a two-image minimum and complete visual-coverage stopping rule;
- installation validation for exactly 30 indexed, attributed bundled images;
- crop-coordinate execution and crop-to-component mapping;
- one base-palette-group enforcement and validation of web-evidenced related-colour extensions;
- Prompt 1 attachment inclusion, including FigureBench crops;
- anti-AI constraints and Methodology text compression fields in Prompt 1;
- rejection of HTML, malformed SVG, and raster-only SVG wrappers;
- deterministic SVG1-to-PNG1.5 render smoke test;
- diagnosis verdict validation;
- Prompt 2 inclusion of PNG1 and approved SVG crops;
- strict exclusion of PNG1.5 from Prompt 2;
- final run-manifest completeness through PNG2; and
- behavioral Skill scenarios confirming that an agent searches domain figures, inspects real FigureBench crops, directly transcribes PNG1, and performs exactly one diagnostic loop.

## Acceptance criteria

The rewrite is complete when:

1. The Skill executes the canonical artifact flow without reverting to topology-first planning.
2. Contexts 1–3 are concrete validated artifacts.
3. Prompt 1 includes mapped FigureBench crop images and their contracts.
4. The installed Skill contains exactly 30 complete, indexed, attributed FigureBench development references; each run inspects at least two and stops only after every planned visual need is covered.
5. Each run uses exactly one palette-library base group, optionally enriched only by web-evidenced related colours rather than another library group.
6. PNG1 is generated from the full Prompt 1 bundle.
7. SVG1 is directly transcribed from PNG1 by the base model and cannot be substituted with a local redraw.
8. PNG1.5 is used only for diagnosis and is structurally excluded from Prompt 2.
9. The diagnosis produces keep, accept-variation, patch, reject, and replace decisions where applicable.
10. Prompt 2 modifies PNG1 using approved SVG crops and the diagnosis.
11. PNG2 is the final output and no second SVG loop occurs.
12. Tests, quick skill validation, and repository checks pass.
