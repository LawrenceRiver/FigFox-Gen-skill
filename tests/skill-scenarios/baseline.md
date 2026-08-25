# Behavioral baseline: legacy Skill

Recorded before rewriting `SKILL.md` at commit `da7c765`. Each scenario ran in a
fresh agent context that could read only the legacy Skill and the scenario request.
Agents were forbidden from editing the repository or making real web, model, or
image calls. The observations below are actual outputs, not predicted failures.

## Scenario A — Methodology only through first-generation input

Agent: `/root/task8_rewrite_skill/baseline_a`

Request: plan the evidence/context work and first image-generation input for a
text-conditioned music system with a diffusion piano-roll intermediate and no user
reference.

Observed behavior:

- Classified the figure as `custom`, then produced a `Scientific topology plan` and
  a legacy `first-image-generation-input.json`.
- Proposed 3–4 web crops, but treated them as aesthetic inputs and never produced
  `context-1-domain-conventions.json` with recurrence records.
- Proposed one `top_k: 5` FigureBench RAG query and aggregate geometry summaries,
  rather than inspecting complete bundled images adaptively, preserving crop
  coordinates, or proving component coverage.
- Produced no Context 2 or Context 3 artifact, no mapped FigureBench crop files, and
  no Prompt 1 attachment manifest.
- Kept palette work unresolved behind the legacy Palette RAG/colour-contract flow.
- Described the first PNG as the only planned generation and final deliverable.

Verbatim rationalizations:

> No user reference image exists. Therefore `user_reference_crops` must be an empty
> array. This does not remove the separate requirement to gather domain references:
> before a real generation call, I would retain at least three strong web figure
> crops and aggregate local FigureBench structure summaries.

> Because this scenario prohibits real web, model, image, and local-cache calls—and
> permits reading only `SKILL.md`—I cannot truthfully claim that references were
> screened, FigureBench was queried, Palette RAG was consulted, or the colour
> contract was compiled. The generation input below is consequently a concrete
> preflight artifact with deliberately unresolved evidence and colour fields.

Failure: the old Skill shaped the wrong artifacts and stopping rule. It did not
create Contexts 1–3 or a Prompt 1 bundle containing every mapped domain/FigureBench
crop.

## Scenario B — PNG1 to editable SVG

Agent: `/root/task8_rewrite_skill/baseline_b`

Request: continue from `run/png1.png`; the SVG output must be editable.

Observed behavior:

- Treated SVG as an optional verification operation.
- Required a prior VLM inspection, generation contract, geometry lexicon, frozen
  palette, and a capable external converter.
- Proposed the obsolete `scripts/figurebench_rag.py svg-verification-brief` command.
- Declined to produce SVG1 and returned `skip_svg_verification`.

Verbatim rationalizations:

> “Editable” does not authorize reconstructing the architecture as a fresh vector
> design. The skill explicitly treats PNG1 as the creative source of truth and
> permits SVG only as a faithful transcription. Therefore I would inspect PNG1 once,
> compile the verification brief from the frozen generation artifacts, and attempt
> conversion only with a converter capable of preserving semantic layers and
> editable text.

> If the inspection fails, required generation artifacts are unavailable, or
> conversion fidelity cannot be established, I would not fabricate an SVG; I would
> return `skip_svg_verification` with the original PNG.

Concrete result:

```text
skip_svg_verification
reason: faithful conversion has not yet been validated against PNG1 and its frozen generation contract
```

Failure: the old Skill did not make direct one-pass base-model PNG1-to-editable-SVG1
transcription mandatory.

## Scenario C — diagnosis through final figure

Agent: `/root/task8_rewrite_skill/baseline_c`

Request: continue after PNG1, editable SVG, and diagnostic render; keep the faithful
encoder, accept the simplified diffusion view, and replace a fake output icon.

Observed behavior:

- Rejected the whole SVG verification because one component failed.
- Did not create five-way per-component diagnosis data, approved SVG crops, or a
  targeted replacement crop.
- Did not compile Prompt 2.
- Explicitly refused a second image-generation call and returned PNG1 as final.

Verbatim rationalizations:

> The SVG is not a faithful verification artifact because its output icon is
> invented rather than transcribed from the first PNG.

> Because an SVG verification check failed, the workflow requires
> `skip_svg_verification` and return of the original PNG.

> Replacing the icon through another image-generation call would violate the
> one-direct-generation boundary; the original first PNG therefore remains the final
> figure by default.

Failure: the old Skill had no diagnosis-to-Prompt2 path and stopped at PNG1 instead
of producing final PNG2 from PNG1 plus approved SVG crops and replacements while
excluding PNG1.5.
