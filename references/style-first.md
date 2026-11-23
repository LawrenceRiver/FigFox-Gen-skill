# Active SVG-reference workflow

For new tasks follow [the active entrypoint](../SKILL.md) and [SVG workflow](svg-reference-workflow.md). Palette-library selection and raster-reference modes below describe archived runs only. Preserve full Director capability; new colour comes from a dedicated complete SVG and Director-owned adjacency/separation decisions.

# Style-anchor experiment

This branch adds an opt-in style-first circuit. The original workflow remains available when `input/style-brief.json` is absent. No production skill is reinstalled automatically; no merge into main is implied.

For the compact model handoff and cached retrieval circuit on `codex/style-anchor-fast`, use [compact-generation.md](compact-generation.md).

## Start a new task

```sh
python scripts/figure_workflow.py init-style --run local/my-run --family handdrawn \
  --methodology /absolute/methodology.md \
  --reference /absolute/reference.png --source-kind user_provided \
  --source 'author/source URL or unresolved source note'
```

Existing directories are never overwritten. Without supplied inputs the command creates an explicit starter, not fabricated methodology. Complete the real component IDs and preferences in `input/style-brief.json` before compiling. This is first-use task intake, not a package installer that searches for private user files.

`--source-kind figfoxbench` or `figurebench` identifies a dataset-derived reference. They are separate collections. Use original source images unless the user explicitly chooses a reconstructed example. Record sample ID, original source and reuse evidence. Dataset membership does not establish rights. No new aesthetic screening of the entire FigFoxBench has been claimed. When evaluating a benchmark, do not use the test target or its reconstruction as the style reference and report it as independent generalization.

## Six starting families

- `instruction_manual`: restrained instruction-sheet rhythm, simple explanatory glyphs and clear physical/semantic relationships. The user's IKEA analogy describes a preference, not permission to copy IKEA illustrations or branding.
- `architecture_2d`: precise geometry, modules, graphs/matrices and aligned parallel lanes.
- `concept_led`: one purposeful visual idea organizes the scientific story; creative grouping never changes its relationships.
- `handdrawn`: consistent hand-lettering/annotations, simple semantic icons and deliberate hand-drawn connector character.
- `volumetric_chromatic`: reference-supported layered volumes and colour depth, without gratuitous gloss, glow or unrelated 3D decoration.
- `story_schematic`: situations/actors/actions and a central story, used for suitable conceptual, design or social-science material rather than forced onto every architecture.

These are starting vocabularies, not fixed templates. The main reference and user preferences determine the actual grammar. Do not blend all six families together.

## Reference hierarchy

One **main reference** controls whole-image typography, linework, frames, arrows, density, spacing and colour relationships. It may come from the user, FigureBench, FigFoxBench or a source-checked web candidate. Inspect actual pixels; relevance ranking alone cannot select beauty. When no image is suitable, `model_composed` imagines one coherent construction during the existing Creative Director pass; do not add an image-model moodboard pass.

`detail_references` specify `target_component_id` and `borrow`. They may supply small glyphs/linework/visual construction only for that component. Redraw coherent new scientific content in the main style. Never paste source characters, logos or source scientific claims into new work. A detail reference cannot silently replace the global style.

Modes:

- `image`: a complete main reference actually accompanies both the Creative Director and PNG1 inputs; its `ai_reference_permitted:true` and `permission_evidence` must reflect a real permission/license basis, not a guess. The input image is hashed and must stay under `input/`.
- `traits_only`: use explicit observed/user-stated descriptors; the original reference stays local and is not attached to either model stage. This is not a blanket legal clearance for reproducing distinctive composition.
- `model_composed`: no external main image; hold the selected family/traits coherent while constructing a new composition from scientific relationships.

AI-reference permission and public redistribution are different scopes. This branch does not auto-publish user references. Keep the inbox under ignored `local/`; publish only original images whose actual applicable terms and constituent rights are verified. arXiv availability, a repository MIT label, or a dataset license alone do not prove rights for every figure/photo. Research leads/statuses are in [style-source-notes.md](style-source-notes.md) and [style-source-candidates.json](style-source-candidates.json). Later user submissions can enter the same local inbox/metadata format.

## Colour, typography and routing

Previous purple/blue/orange examples demonstrate relationships only, not a permanent theme. Match a palette independently per task; reuse is allowed when it fits. Exact hues require an explicit user constraint.

Select one approved palette group deliberately for the main style's cool/warm balance, saturation and contrast relationships; `select-palette` is deterministic with a style brief. `palette_reason` explains the match. Do not randomly pick a different group after the style is fixed. Domain-paper colour counts remain observations, not a style mandate.

Normally use one base colour family with a second accent family; retain1-3 `dominant_roles`, and justify a third. Neutrals/tints and nearby blue-violet shades are not independent decorative themes. Neighboring base frames use analogous light fills, with at most one strong local contrast focus. `contrast_foci` contains the `accent_target`; at most two foci are allowed, and two require a distant-layout reason plus `proximity_groups` showing they are not adjacent. This checks the declared plan, not eventual image pixels. Use deeper colour for meaningful main marks and lighter supporting views (or a deliberate reference-supported inverse). Keep dark/black type readable and coherent. Do not automatically paint all shapes or labels pastel.

The mainline may be horizontal, vertical, C/reverse-C, S/reverse-S/serpentine, arc, clockwise/counterclockwise spiral, stages, parallel merge, or a macro main-chain with side/detail chains. These are placement patterns, not scientific topology. Preserve every actual branch, merge, feedback and relationship; avoid fake loops and ambiguous crossings. Mainline IDs, accent targets and all detail targets must be real Context2 components. Every relationship needs an explicit label. Purposeful curved arrows are allowed when heads/endpoints remain clear.

Stage labels are `Stage 1/2/3` or panel letters `(a)/(b)/(c)` only; `stage_labels` is `none`, `stage_numbers` or `parenthesized_letters`. Never add decorative numbered badges or generic stage labels to a method that has none. Respect actual stage count.

Typography follows the main reference consistently. Do not default to Times New Roman for diagram text; formulas may use appropriate mathematical notation. No invented gray microcopy. Necessary short italic explanations use readable **Arial Italic**, in black or a compatible dark ink. Frames and arrows use the same planned visual grammar. A real template/table header divider may be appropriate; generic dashboard cards are not. Icons may be human-drawn semantic constructions, not pasted stickers.

## Current compact circuit

Follow the concise [SKILL entrypoint](../SKILL.md) and [compact-generation.md](compact-generation.md): one peer/Methodology needs anchor first, then concurrent need-driven construction lookup, liked-style traits and palette matching, one correspondence table, Creative Director, one drawing packet and PNG1. Do not run a separate search for every component or ordinary C/reverse-C layout. Keep valid caches and explicit source/permission records. No synthetic speedup claim.

## Compiling, replay and testing

Run existing commands after completing Contexts1-3. In style mode `build-creative-director-prompt` writes both `creative-director/prompt.md` and `attachments.json`; pass both to the actual Harness model. `build-prompt1` and `validate-run` check that attachment manifest against the same approved style brief. Prompt1's separate main/detail roles are permission-checked. Changing reference pixels or preferences changes the style fingerprint and invalidates deterministic prompt replay.

```sh
python scripts/figure_workflow.py select-palette --run local/my-run
python scripts/figure_workflow.py build-creative-director-prompt --run local/my-run
# Harness executes that single ideation pass, saving its real brief.
python scripts/figure_workflow.py build-prompt1 --run local/my-run
# Harness makes one image call with Prompt1 and its actual manifest attachments.
python scripts/figure_workflow.py validate-run --run local/my-run
python -m unittest discover -s tests -v
```

Use the same Methodology/reference for main-vs-branch trials, with one PNG per variant. Compare scientific topology/labels first, then overall style, local/global coherence, density, frames/arrows, typography and colour proximity. Synthetic compiler tests are not an aesthetic image trial. No new image generation has occurred merely because the tests pass.

Prompt1 tool budget: style-mode compilation removes JSON indentation and the duplicate component listing when needed to fit the image tool's 32,000-character limit. It retains every normalized Context value, scientific edge, and the full component mapping. If this lossless reduction is insufficient, compilation stops before submission; shorten repeated planning prose while preserving the science. A rejected request that produced no image is not a completed generation pass.
