---
name: posfox-gen
description: Use only when the user explicitly requests a scientific or research poster image. Accept a paper PDF and optional poster reference; stop at PNG generation. Ordinary scientific figures and methodology diagrams do not use this Skill.
---

# PosFox Gen

## Explicit poster requests only

Use this optional branch only when the user explicitly asks for a scientific/research poster, academic conference poster, 科研海报 or 学术海报. A paper PDF, a large canvas, a poster-like reference, quoted/negated poster text, or a request for a scientific figure is not enough. The user must positively request the poster artifact. Ordinary paper figures and methodology/architecture diagrams stay in the default figure workflow. If intent is ambiguous, do not enter the poster workflow; clarify the intended artifact. Explicit `$posfox-gen` invocation without a clear poster request does not waive this gate.

This package runs independently of the full PosFox pipeline. It delivers a PNG and stops; it does not start editable reconstruction or require another repository. Resolve helpers relative to this Skill's own folder.

Turn the supplied paper into a complete scientific poster **image** using the calling Harness. Stop after delivery: this edition does not reconstruct HTML/SVG, run SAM, build a visual issue map, or repair editable artifacts. Read [the workflow](references/workflow.md) and [generation rules](references/generation-rules.md). Consult the [cached quality notes](references/quality-notes.md) when forming the brief, not a new literature survey every run.

## Inputs and parallel preparation

Use the user's PDF directly. A user-designated main reference/template is primary and goes to the generator; a sole supplied reference defaults to primary. A paper PDF supplies scientific content; a PDF explicitly supplied as a template supplies design guidance. Do not replace the user's reference with another poster. Without a reference, choose a relevant accessible example using available tools; record its source and role.

Read the whole paper, inventory useful figures/tables and extract complete high-resolution scientific regions with captions/source locations. Preserve axes, legends, labels and units. Measure each selected crop's PDF point size, actual pixel size and aspect ratio; retain its source hash. Use these measurements to allocate figure space and carry them, with the intended display frame, into the generation prompt. DPI alone does not establish a usable display size. Reuse normal PDF parsing/cropping; supplement incomplete assets when necessary. Batch independent text reading, asset extraction and reference reading concurrently. Do not invent boxes or slice arbitrary subfigures to fill space. The bundled deterministic helper is `python scripts/extract_pdf.py PAPER.pdf --out RUN/source`; use `--help` for inspected crops. Resolve scripts relative to this skill, and use an explicit persistent output directory in the user's workspace.

## Three perspectives, bounded debate

Write one source-backed initial content/layout plan: problem, input/output, model, innovation, metrics, useful figures and limitations. Freeze the PDF/assets/reference/plan packet. Dispatch **three parallel sub-agents**: content advocate, science reviewer and visual planner. Each may return one substantial initial report. Then permit **one short callback round** only for disputed or consequential points; no second long report or broad reread. See [roles and callback format](references/debate.md).

Every role applies rigor, protects what already works, and asks “why not?” about both changing and retaining the original. Main executor merges duplicates, resolves disagreements, applies justified edits once, and checks changed claims against sources. Reuse science findings; do not launch another logic reviewer. Keep actual review scopes and original opinions. Unresolved scientific blockers stop generation. If sub-agents are unavailable, disclose same-executor role passes rather than claim three independent agents.

## Generate and stop

Assemble exact approved copy, complete visual instructions, measured source dimensions/aspects, planned display sizes and reference roles into one prompt. Enumerate the planned modules and their relative area/text balance, section-band/background colors, and dots/bullets/rules. Source images keep their actual ratio; an envelope with a different ratio must explicitly contain the whole image rather than stretch it. Save this visual roster with the handoff so a separately invoked downstream reconstruction can preserve the generated modules/features. Use the available Harness image tool; no upstream API runner, new model service or API key setup. Every planned figure/table must actually be drawn, not reserved as a blank slot. Respect the tool's current attachment limit and supply complete instructions for remaining evidence.

Generate once. At most **one regeneration** is allowed: two image calls total. No separate image-review agent/round. During saving, observe whether required content/visuals are missing or globally wrong; only that kind of failure warrants the single retry. Do not reroll for minor polish. Persist and show the real image, final prompt, source/attachment manifest, brief debate decisions and stage timing. Record incomplete work honestly. A raster image is not an editable SVG or a scientifically certified result. **End here.**
