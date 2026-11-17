# Versions and installation

`main` is the V2 default. Release tags preserve reproducible versions without rewriting
the old published history.

| Ref | Skill name | Invocation | Purpose |
|---|---|---|---|
| `main` / `v2.0.0` | `FigFox-Gen-skill` | Implicit or explicit | Current V2 workflow; `main` can advance |
| `v1.0.0` | `figfox-gen-v1` | Explicit only | Original algorithm and assets, with a distinct legacy skill identity |
| `v1-original` | Original identity | Historical metadata | Byte-original former `main`, retained for archival inspection |

The `v1.0.0` identity and explicit-only policy allow V1 and V2 to coexist. General calls
prefer V2; request `$figfox-gen-v1` to use the legacy workflow. Do not install `v1-original`
alongside V2 under its original name: it predates the distinct legacy identity.

## Install the default or pin a release

```bash
# Current default
npx skills@latest add LawrenceRiver/FigFox-Gen-skill --skill FigFox-Gen-skill

# Reproducible V2 release
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v2.0.0 --skill FigFox-Gen-skill

# Explicit-only legacy skill, alongside V2
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
refresh local copies. A V1 pin remains a V1 source; to migrate, run the default V2 install
command instead. A manually copied skill may have no tracked source, so reinstall it through
the CLI or replace that copy deliberately. Save local customizations before replacing files.

The `v2.0.0` pin stays on that release. Use the unpinned default source when you want later
V2 changes through explicit updates. Do not interpret a restore from a lock file as an
update: the CLI can restore the recorded commit.

## What changed in V2

V2 replaces the fixed 3–4-paper/full-crop handoff with one visual-needs anchor from about
two inspected peers, parallel need-driven construction/style/palette work and a compact
packet. Innovation-focused detail, notation aliases, a complete regular frame and exact
ports/path points feed deterministic grid/route preflight. The palette is selected per run
from 14 groups, without a fixed demo hue theme. Optional references have scoped traits;
no-reference runs have an empty attachment list and omit image-input arguments.

The final deliverable remains one PNG1 for author inspection. Artifact and geometry checks
do not certify the generated pixels. The V2 gallery is labelled as previews because small
symbol/connector issues remain. Original V1 images and full recorded Methodology inputs
are retained in the [README](../README.md#examples).

Detailed legacy instructions: [V1 README](https://github.com/LawrenceRiver/FigFox-Gen-skill/blob/v1.0.0/README.md)
and [V1 Skill](https://github.com/LawrenceRiver/FigFox-Gen-skill/blob/v1.0.0/SKILL.md).
For the untouched historical source, inspect
[`v1-original`](https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v1-original).
