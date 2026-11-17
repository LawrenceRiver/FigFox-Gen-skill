# Text and symbol economy for framework figures

Use this during the existing Creative Director pass and final pixel inspection. It adds no search, model call or automatic repair pass.

## Reference budget

The user supplied a five-panel architecture reference on 2026-11-17. Manual transcription gives approximately **99 English words**: panel totals **20 / 18 / 16 / 25 / 20**. Count headings, module/artifact names, diagram annotations and summaries at every visible occurrence. Hyphenated words count as one; “Stage” and its Roman numeral are included. Panel letters, ampersands, mathematical variables and symbolic placeholder tags are excluded. The count is approximate because the reference is a raster image; it is a density anchor, not scientific content for subsequent figures. Do not reuse its stage names, modules, model names or topology.

For a new framework/harness overview, **aim for about 100 English words or fewer; the absolute maximum is 160**. If 100 communicates the science, do not expand toward 160. The upper allowance is reserved for necessary scientific distinctions, not additional commentary, implementation categories or narration. Do not pad a shorter figure to 100. Before exceeding 100, first group supporting detail and move explanations to the paper/caption; record the scientific necessity as `text_budget_reason` in the Director brief. Keep essential mathematical notation in a separate visible-symbol inventory and inspect its occupied area too; symbols are not a way to evade the text budget. A different explicit user budget takes precedence. Do not exceed 160 or shrink fonts to fit.

## Subtraction pass

- Name each distinct visible object precisely, normally with a two- or three-word noun phrase. A stage heading summarizes its process and may be longer when needed.
- Beyond the heading, express each idea in one place: an artifact name, an essential relation caption, or one short process summary. Do not repeat the same description in all three.
- Remove captions that merely narrate a clear arrow or recognizable drawing. Do not print every internal relationship label supplied for planning.
- If a short summary explains the process, remove the supporting category lists and operation-by-operation prose. Fine detail belongs where it explains the framework innovation, not everywhere it is available in Methodology.
- Preserve scientifically essential distinctions, labels, direction and dependencies. Grouping visible details must not erase a genuine branch or imply an unsupported mechanism.
- Learn modular assembly, alignment, meaningful stacking and horizontal sequencing from inspected architecture figures. Use canonical model grammar only for models actually present in the current source, at its relevant level of detail. Do not turn every framework into a Transformer or stack repeated empty boxes for decoration.
- Delete checks, exclamation marks, warning triangles, status dots and decorative badges unless each retained mark communicates a necessary source-supported distinction. Repeated “success” marks often add no information. Neither model-written decoration nor its presence in a reference justifies keeping it.

## Director handoff and inspection

In `creative-director/brief.json`, record `visible_text` (the exact intended strings, including repeated occurrences), `visible_word_count`, and a separate `visible_symbols` inventory. Keep these as optional extra brief fields; they do not replace the canonical schema. Record why any nonsemantic-looking mark or budget exception is scientifically necessary. Every intended visible component caption must agree with `display_labels`.

The generator receives the approved text inventory as a whitelist: construction descriptions, source excerpts, route meanings, restrictions and review notes are instructions, not additional image lettering. Ask for no extra narrative. Keep the inventory short rather than shortening every word into cryptic abbreviations. Do not replace deleted prose with generic icons.

Inspect actual output for excess text, repeated descriptions, unneeded status symbols and leaked instructions. Compare the actual image against the approved inventory; planning counts do not prove pixel compliance. Report deviations honestly. Preserve the first output and follow the skill's single-pass stopping rule.
