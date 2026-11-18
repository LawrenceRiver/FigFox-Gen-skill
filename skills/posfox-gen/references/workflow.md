# Generation-only workflow

## 1. Read and prepare together

Work in an explicit RUN directory. The provided PDF is the content source; download nothing already supplied. Read full text and inspect relevant figure regions. Run independent operations concurrently rather than sequentially waiting for source text, reference pixels and extracted assets. Source completion remains a real step: correct truncated axes or missing context before freezing the shared packet. Avoid a new image-processing pipeline for each selection.

`extract_pdf.py` extracts page text with bounds, page previews, embedded images, hashes and captions. It does not detect complete vector figures automatically. Inspect actual pages first, then pass rectangular crops in PDF points:

```bash
python /path/to/posfox-gen/scripts/extract_pdf.py paper.pdf --out run/source
python /path/to/posfox-gen/scripts/extract_pdf.py paper.pdf --out run/source --crops crops.json --render-scale 6
```

Each inspected crop has `id`, `type` (`figure` or `table`), one-based `page`, `bbox` (`x0,y0,x1,y1`), `caption`, and `source_locator`. Use real source bounds, not guessed example coordinates. The asset table reports `geometry:{pdf_size_pt,pixel_size,aspect_ratio}`, source hash and rendering resolution; source DPI is not the eventual poster's printing DPI. High resolution does not make tiny displayed labels readable: provide enough layout area. Carry each measured pixel size/ratio and intended display frame into the image prompt. Allocate area using the true source aspect, not an arbitrary box that a later reconstruction must repair. The figure may be contained in a differently shaped envelope without distortion. Exact native-looking table reflow is allowed when all source values/headers/conditions are preserved.

## 2. Freeze one packet

Share the same version with all three roles: full paper; asset inventory; clear complete source images; actual user template/reference; initial content/layout plan. Preserve that version while reports are being authored. Initial plans map each claim/metric/figure to a page or asset ID, include evaluation settings and units, and explain input → model/method → output plus innovation and limitations.

Use one compact plan rather than mandatory duplicate JSON documents. Scientific content and the number of useful sections depend on the paper; no fixed word count, column count or figure count. The whole paper is available to every role, but record what each actually read/viewed. File access is not proof of inspection.

## 3. Parallel reports, one brief callback

Follow debate.md. Roles receive the packet simultaneously. They may produce one detailed initial report each. Main executor only calls back on disputed/high-impact issues, giving original passage, proposed edit and source evidence. Each callback is usually one to three sentences per issue, with a position and decisive reason. No callback is needed when there is no disagreement. Preserve original reports; record main-executor resolutions separately. Do not manufacture amended-plan reviewer approval or majority-vote away scientific uncertainty.

## 4. Prompt and generate

Use generation-rules.md. The primary user reference guides composition/style; paper assets supply scientific evidence. Never borrow the reference's research claims or author identity. Retain exact method relations and numerical settings. Make the generation prompt a usable design brief, not an appended dump of every report. Record each module's relative area/text budget, reading order, background/header colors, and visible dots/bullets/rules. Keep this roster in the saved handoff. Later reconstruction must inventory the actual generated result separately; it must not silently drop repeated modules or decorations merely because their words survive elsewhere. This edition does not execute that later stage.

Invoke the host's image-generation tool directly. No OpenAI SDK, upstream AutoDesign/FigFox runner or model transport is bundled. There is no separate image-review agent. A local observation while receiving the output can justify one regeneration for missing planned visuals or global scientific failure. Keep both attempts and the reason. No additional generation after the second call; disclose remaining faults and stop.

## 5. Deliver the image

Suggested lightweight run files (not compulsory database schemas):

```text
RUN/
  source/asset_table.json + pages/ + images/
  plan.md
  debate/content.md + science.md + visual.md
  debate/callback.md             # only when a callback occurred
  decisions.md
  prompt.txt
  poster.png                    # actual image-tool result
  generation.json               # actual inputs, roles, output, attempt, hash
  timing.json                   # actual stage start/end times
```

Record supplied PDF identity, original asset locations, reference roles and which images were actually attached. Do not silently turn this into a long report-writing stage. Time source preparation, initial plan, parallel reports, callback/resolution and generation separately. Separate tool waits from interpretation/output when measurable; do not attribute an entire wall-clock phase to a network request. Never claim a stable latency from one development run.

Show the image inline and link the saved artifact. Report a remaining issue plainly rather than inventing an acceptance score. Stop before reconstruction, paired crops, visual issue maps, SVG/HTML editing, repair, rewards or trajectory optimization. Those belong to a later separately invoked workflow.
