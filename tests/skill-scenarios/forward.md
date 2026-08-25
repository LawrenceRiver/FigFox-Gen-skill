# Behavioral forward test: rewritten Skill

Recorded after the complete `SKILL.md` rewrite. The three scenarios repeated the
baseline requests in fresh agent contexts. Each agent could read only the rewritten
Skill and references explicitly routed by it, could not read these scenario records,
and could not make real web/model/image calls or edit the repository.

## Scenario A — Methodology only through first-generation input

Agent: `/root/task8_rewrite_skill/forward_a`

Observed behavior:

- Extracted the music-generation domain and the correct mainline:
  `Text Prompt → Prompt Encoder → Diffusion Model → Structured Piano Roll → Audio Decoder → Generated Audio`.
- Planned the canonical Context 1, Context 2, Context 3, web-manifest,
  FigureBench request/materialized-manifest, and Prompt 1 paths.
- Required 3–4 scholarly papers, at least three retained credible cropped panels,
  recurrence evidence, HTTPS sources, and component-mapped `borrow`/`must_change`
  contracts.
- Required inspection of at least two complete FigureBench references and adaptive
  continuation until geometry, containers, connectors, layout, and special visuals
  were completely covered.
- Used exactly one palette-library group and correctly planned no user-reference
  attachment.
- Shaped Prompt 1 attachments as every mapped domain crop plus every mapped
  FigureBench crop, never complete unexplained references or a palette image.
- Refused to fabricate Context 1 or compile a false Prompt 1 when web inspection was
  prohibited.

Representative output:

> Outcome: the first image-generation input cannot be validly compiled in this
> offline scenario. Context 1 requires inspecting and retaining at least three
> credible scholarly figure panels; no web calls are allowed, so recurrence
> evidence, source URLs, and crop attachments would be fabricated.

> After valid Contexts 1 and 2, Context 3 would inspect at least two complete
> FigureBench references and continue until every component’s geometry, containers,
> connectors, layout relationships, and special visuals are covered. Exactly one
> palette-library group would supply all colors.

Result: pass. The agent used the new artifacts and coverage rule and did not revert
to topology planning, aggregate top-k summaries, or a first-PNG-only workflow.

## Scenario B — PNG1 to editable SVG

Agent: `/root/task8_rewrite_skill/forward_b`

Observed behavior:

- Named SVG1 transcription as mandatory, not optional.
- Assigned the transcription to the base Codex multimodal model looking directly at
  PNG1.
- Required a one-pass editable SVG with independent text, shapes, paths, lines,
  arrows, and groups, and rejected a full-canvas raster wrapper.
- Kept deterministic local commands after SVG1: `inspect-svg`, then `render-svg` to
  PNG1.5.
- Refused to invent SVG1 or silently substitute a local reconstruction when the
  scenario's declared PNG path was absent from the accessible workspace.

Representative output:

> The next valid action, once the file exists, is for the base Codex multimodal model
> to inspect PNG1 directly and write: `run/svg-diagnostic/svg1.svg`.

> It must be a one-pass transcription—not a redesign—with independently editable
> `<text>`, shapes, paths, lines, arrows, and groups. A full-canvas embedded raster is
> not acceptable.

> I did not fabricate SVG1, substitute a locally handcrafted reconstruction, or
> claim validation success.

Result: pass. The legacy converter/verification-brief/`skip_svg_verification`
rationalization disappeared.

## Scenario C — diagnosis through final figure

Agent: `/root/task8_rewrite_skill/forward_c`

Observed behavior:

- Converted the supplied findings into `keep` for encoder, `accept_variation` for
  diffusion, and `replace` for the fake output, while requiring exactly one verdict
  for every Context 2 component.
- Approved crops only for the faithful encoder and semantically sound simplified
  diffusion regions; it did not approve the fake output icon.
- Required a mature component-mapped domain/FigureBench replacement crop for the
  output before Prompt 2.
- Shaped Prompt 2 image attachments as PNG1, approved SVG crops, and the replacement
  crop. It explicitly excluded PNG1.5, SVG1, rejected crops, and complete unexplained
  reference figures.
- Planned final `png2-final.png`, run-manifest validation, and termination without a
  PNG2-to-SVG loop.
- Correctly stopped before Prompt 2 because the real replacement crop was unavailable
  under the no-network/no-image scenario constraint.

Representative output:

> Prompt 2 image attachments must be exactly: `png1.png`; approved encoder crop;
> approved diffusion crop; mapped output replacement crop.

> Never attach `svg-diagnostic/png1.5.png`.

> After one image-generation call, save `png2-final.png`, write
> `run-manifest.json`, run final provenance validation, and stop. Do not transcribe
> PNG2 to SVG or begin another diagnostic loop.

Result: pass. The agent used the diagnosis to prepare a targeted second image pass
instead of rejecting the whole SVG stage or returning PNG1 as final.

## Conclusion

All three fresh-context scenarios converged on the canonical artifact recipe. No
scenario skipped scholarly domain evidence, stopped FigureBench selection at a fixed
count, attached complete unexplained references, hand-authored SVG through local
tools, included PNG1.5 in Prompt 2, or stopped the intended workflow at PNG1.
