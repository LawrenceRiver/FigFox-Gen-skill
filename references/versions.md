# Versions and installation

`main` now provides **V3 (`v3.1.0`)**, the SVG-reference workflow. This supersedes V2 (`v2.1.0`). Earlier `v3.0.0` and `v3.0.1` tags remain historical snapshots; their commits and tags are unchanged.

```bash
# Current default V3
npx skills@latest add LawrenceRiver/FigFox-Gen-skill --skill FigFox-Gen-skill

# Pin this V3 revision
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v3.1.0 --skill FigFox-Gen-skill
```

V3 requires genuine SVG image references, a dedicated complete source SVG for palette relationships, full Creative Director decisions, and simple straight or single-curve routes. Scientific topology comes from Methodology. One image generation produces PNG1; actual image inspection is required. Validation cannot prove pixel fidelity. Legacy raster-library runs remain replayable.

Existing local installations require an explicit update. See [the active skill](../SKILL.md) and [SVG schemas](svg-reference-workflow.md).

The following notes describe the prior V2 release and are retained as historical installation guidance, not current defaults.

# Historical versions and installation

`main` provides the current **V2**, released as `v2.1.0`. The workflow previously presented as V3 is now consolidated under V2. The old standalone `figfox-gen-v2` entry and its `v2.0.0` / `v2.0.1` installation tags are retired and removed; use the default skill instead.

| Ref | Skill name | Invocation | Purpose |
|---|---|---|---|
| `main` / `v2.1.0` | `FigFox-Gen-skill` | Implicit or explicit | Current default V2 |
| `v1.0.0` | `figfox-gen-v1` | Explicit only | Preserved V1 workflow |
| `v1-original` | Original identity | Historical metadata | Untouched original snapshot |
| `v3.0.0`, `v3.0.1` | Historical release names | Historical only | Published snapshots before naming consolidation |

Existing published commits and V1/V3 snapshots are not rewritten. The current release is explicitly marked latest even though its major number is lower than the historical V3 tags. Earlier preview assets keep their original paths and provenance; they are not relabeled as newly generated V2 outputs.

## Install the default or pin a release

```bash
# Current default V2
npx skills@latest add LawrenceRiver/FigFox-Gen-skill --skill FigFox-Gen-skill

# Reproducible current V2 release
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v2.1.0 --skill FigFox-Gen-skill

# Explicit-only V1
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v1.0.0 --skill figfox-gen-v1
```

Add `-a codex` to select Codex and `-g` for a user-wide installation. Without `-g`, installation targets the current project. The [skills CLI documentation](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#skills-add) describes source URLs and skill selection.

## Update an existing installation

```bash
npx skills@latest check
npx skills@latest update FigFox-Gen-skill
```

Repository changes do not automatically replace installed copies. If using the retired standalone `figfox-gen-v2` or a historical pinned release, save local customizations, remove that retired installation, and install the default source above. V1 remains a separate explicit-only skill. Do not install `v1-original` alongside the default under its old shared identity.

## Current V2 scope

The default includes the Methodology-grounded needs anchor, inspected peer construction evidence, scoped visual references, parallel preparation, complete rectangular layouts, continuous checked routes, proximity-aware color, concise text and symbol inventories, and optional direct-content image placement. Use peer contribution-level granularity to guide detail depth, while deriving the scientific content from the current Methodology.

One image-generation call produces PNG1, optionally followed by deterministic insertion of approved content assets. Authors inspect the actual image; schema and geometry checks do not certify its scientific or visual correctness. The five user-facing highlights are in the [English README](../README.md#what-is-new-in-v2) and [Chinese README](../README_ZH.md#v2-更新亮点). The original workflow overview images remain unchanged.
