# Versions and installation

`main` is the V3 default, released as `v3.0.1`. Release tags preserve reproducible versions without rewriting
the old published history.

| Ref | Skill name | Invocation | Purpose |
|---|---|---|---|
| `main` / `v3.0.1` | `FigFox-Gen-skill` | Implicit or explicit | Current V3 workflow; `main` can advance |
| `v3.0.0` | `FigFox-Gen-skill` | Implicit or explicit | Pinned first V3 release |
| `v2.0.1` | `figfox-gen-v2` | Explicit only | V2 compatibility identity, original V2 algorithm/assets |
| `v2.0.0` | `FigFox-Gen-skill` | Implicit or explicit | Pinned original V2 release |
| `v1.0.0` | `figfox-gen-v1` | Explicit only | Original algorithm and assets, with a distinct legacy skill identity |
| `v1-original` | Original identity | Historical metadata | Byte-original former `main`, retained for archival inspection |

The explicit-only V1 and V2 identities let all three versions coexist. General calls use V3; request `$figfox-gen-v1` or `$figfox-gen-v2` for the corresponding older workflow. `v2.0.0` retains its untouched original public identity; use `v2.0.1` for a coexisting V2 alias. Do not install `v1-original`
alongside V3 under its original name: it predates the distinct legacy identity.

## Install the default or pin a release

```bash
# Current default
npx skills@latest add LawrenceRiver/FigFox-Gen-skill --skill FigFox-Gen-skill

# Reproducible current V3 release
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v3.0.1 --skill FigFox-Gen-skill

# Pinned original V2 release
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v2.0.0 --skill FigFox-Gen-skill

# Explicit-only V2 alongside V3
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v2.0.1 --skill figfox-gen-v2

# Explicit-only V1 alongside V3
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v1.0.0 --skill figfox-gen-v1
```

Add `-a codex` to target Codex and `-g` for a user-wide installation. Without `-g`, the CLI
installs into the current project. The CLI requires Node.js 22.20 or later.

The [official CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#skills-add)
documents GitHub tree URLs, release-tag sources and `--skill` selection. The commands above
use those documented forms. Release-specific installs require the corresponding published
tags.

## Update an existing installation

```bash
npx skills@latest check
npx skills@latest update FigFox-Gen-skill
```

The [update command](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#skills-update)
updates an installed skill from its recorded source. Repository changes do not automatically
refresh local copies. A V1 or V2 pin stays on its selected source; to migrate, run the default V3 install
command instead. A manually copied skill may have no tracked source, so reinstall it through
the CLI or replace that copy deliberately. Save local customizations before replacing files.

The `v2.0.0` and `v3.0.0` pins each stay on their release. Use the unpinned default source when you want later
current-version changes through explicit updates. Do not interpret a restore from a lock file as an
update: the CLI can restore the recorded commit.

## What changed in V3

V3 keeps V2's Methodology-grounded visual-needs anchor from about two inspected peers,
parallel construction/style/palette work and compact drawing packet. It reuses inspected
caches and resolves only named missing needs. Innovation determines the drawing granularity;
standard models use source-checked canonical constructions at that scope.

The Creative Director fixes the entire rectangular layout, including the output, before
local details. Exact ports/path points feed deterministic grid/route preflight. Bold headings
normally sit on the ordinary background, while colour fill emphasizes scientific content.
Arrows share a coherent family and can be broad, rounded or hand-drawn when appropriate;
centerline geometry does not force thin black strokes. Each connector remains continuous
and reaches its intended process. The palette is selected per run from 14 groups. References
have scoped roles; no-reference runs use empty attachments and omit image-input arguments.

One layout image call yields the figure. Optional licensed direct-content assets are pasted
into reserved slots with a deterministic helper, retaining their actual pixels and provenance
without another model call. The generated image or composite is the single final raster
PNG1 for author inspection. There is no editable SVG deliverable or automatic repair loop.
Artifact and geometry checks do not certify generated pixels. The
[latest V3 previews and recorded checks](../examples/v3-0-1/README.md) document selected
examples, including the indigo/violet and amber MusiCoT revision, without guaranteeing pixel
acceptance. Original V1 images and full recorded Methodology inputs remain in the
[README](../README.md#examples).

The original V2 release stays pinned at `v2.0.0`; its tagged documentation and gallery remain
available without rewriting published history. `v1.0.0` remains the explicitly invoked legacy
skill, and `v1-original` remains the untouched archival source.

Detailed legacy instructions: [V1 README](https://github.com/LawrenceRiver/FigFox-Gen-skill/blob/v1.0.0/README.md)
and [V1 Skill](https://github.com/LawrenceRiver/FigFox-Gen-skill/blob/v1.0.0/SKILL.md).
For the untouched historical source, inspect
[`v1-original`](https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v1-original).

V3.0.1 makes the approved pale, predominantly white and black-text direction the default. Complete rectangular composition and regular partitions take precedence over forcing all arrows to share one compass direction. See the [V3.0.1 examples](../examples/v3-0-1/README.md). Earlier tags stay fixed.
