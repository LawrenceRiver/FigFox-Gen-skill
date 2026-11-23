Create one complete scientific figure from this locked generation checklist.
Evidence SHA256: 50c7a8441f89403f066afcdb7ff3f57d8d26d81c3e7c3da96ac7a8c6c1412feb
## Scientific meaning
Rewritten tags and lyrics condition a dense music LM and acoustic renderer. Optional generated melody or extracted cover melody conditions semantic-token continuation. A separate offline music tokenizer supplies LM targets.
- Text-only inference does not run the music tokenizer. Its dashed targets route lands only in the isolated LLM training footer.
- Music semantic tokens are single-codebook 25Hz; melody tokens are distinct 6.25Hz relative-pitch tokens.
- The LM is one dense 3B model. Melody-CoT is optional autoregressive planning, not mandatory external preprocessing.
- Cover reference melody tokens enter the shared LM prefix; text never enters RMVPE.
- Both text and semantic tokens must reach the DiT through their actual Text encoder and semantic inlet.
- Render: flow-matching DiT -> acoustic latents -> Spec-VAE decoder -> complex spectrogram -> Band-Mode Refiner -> inverse STFT -> 48kHz stereo.
- Training pretraining/SFT/DPO/GSPO is an isolated footer, not an inference loop.
## Innovation-led detail hierarchy
Peer depth observation: MusicGen illustrates its token interleaving at cell level; CosyVoice keeps its shared LM as one whole block and exposes token interfaces.
- Innovation: Melody-CoT and reference melody conditioning | Focus: llm | Finest visible unit: Optional melody-token planning and cover reference-prefix route into the same LM.
Shared non-innovation depth: Supporting tokenizer and acoustic stages remain compact named whole operations.
Keep whole (no invented model internals): condition, tokenizer, render
Allocate detail to the actual contributions; do not expand standard components just because they are familiar. Match supporting regions at the shared level.
## Locked overall framework
Main inference along one shared horizontal axis: compact text region upper left, larger dense LM centre, taller renderer right. Offline tokenizer lower left enters only LM lower training footer. One smooth short-height overhead text branch, no captions outside frames.
Content determines frame sizes; the Director planned frames and routes together. Unequal regions and useful white space are allowed. Keep every local title, symbol, text and picture inside its parent with padding; no filled title strips. Do not force a rectangular silhouette or equal-card template.
Canvas pixels: [2400, 1200]; preserve the exact boxes and path points below. Scale the entire composition uniformly.
Grid rows: [[220, 580], [740, 1100]]; columns: [[60, 580], [760, 1480], [1660, 2340]]
Clearance: 8 pixels. Captions must stay in their reserved boxes; never cut shafts.
## Connector construction (Creative Director and generator)
Only basic straight lines or one simple smooth curve. No staircase, zigzag, maze, crossings or complicated perimeter pipes. Ordinary frames have at most one input and one output; source-grounded exceptions must be explicit. The Director moved/regrouped boxes before choosing these paths. Bezier points are control handles, never polyline corners. Keep shafts continuous and arrows attached to actual source/target borders. Trace all lines after placing text. A simple curved human return is not an internal neural loop.
Draw every named component once. A container may be the component itself; do not add duplicate stand-ins. Repeated snapshots inside a component are insets, not extra pipeline nodes.
## Exact components and placement
- tokenizer = `Qwen-Music-Tokenizer` | box [60, 740, 520, 360] | Separate lower-left offline representation inset; plain encoder and VQ, token marks, offline training caption inside.
- condition = `Text Conditioning` | box [60, 220, 520, 360] | Compact white text conditioning region; plain dark request/rewriter/tags labels.
- llm = `Qwen-Music-LLM` | box [760, 220, 720, 880] | Main central generator; focus on optional Melody-CoT and cover melody prefix; shared dense 3B LM stays whole. Training landing isolated in bottom footer.
- render = `Qwen-Music-Render` | box [1660, 220, 680, 880] | White right renderer; semantic tokens and text enter real DiT inlets, then one compact acoustic synthesis sequence.
## Exact directed connections (one arrowhead per relationship)
These relationship labels specify meaning. Show only short relation captions where needed; not every arrow needs visible explanatory text. Preserve essential scientific notation and conditions.
- tokenizer.east -> llm.west | `offline training targets at 25 Hz` | reference line points [[580, 920], [760, 920]]
- condition.east -> llm.west | `music tags and lyrics` | mainline line points [[580, 420], [760, 420]]
- llm.east -> render.west | `generated Music Semantic Tokens at 25 Hz` | mainline line points [[1480, 420], [1660, 420]]
- condition.north -> render.north | `rewritten text via text encoder for DiT cross-attention` | branch cubic Bezier control points [[320, 220], [320, 40], [2000, 40], [2000, 220]]
Ports name the actual object/frame boundary. Never stop at an empty margin, nearby input, or unrelated enclosing stage. Independent evidence edges have distinct landing ports and arrowheads; crossings are not junctions. Do not merge unrelated evidence into one long bus.
## One-to-one drawing correspondence
| Need / location | Reference construction or source basis | Our adapted drawing |
| --- | --- | --- |
| semantic versus melody prefix interfaces / llm | Inspected MusicGen token-cell SVG and CosyVoice token/model SVG; exact sequence semantics follow Qwen. | Small native uniform token rows, no peer multi-codebook matrices; optional melody row locally green-tinted, full-mixture semantic row pale blue. |
For every visual need, choose direct use of a suitable collected asset, a source crop, or borrowed construction. Do not treat all existing imagery as style evidence: when a real visual instance communicates the content best, reserve an aligned inset for the actual file instead of inventing a drawn substitute. Only explicitly collected and approved direct-content insets get reserved slots; invent no blank panels when none are selected. Those insets are composited after generation; leave only those declared slots clean and preserve their aspect ratios. This choice is open-ended across domains, not limited to any media category. Source material used illustratively must not masquerade as this method’s measured result.
For standard models actually named in this Methodology, use a source-checked recognizable architectural silhouette at the scoped detail level. An unchanged model may remain a compact canonical inset; invent no arbitrary replacement geometry and do not expand supporting internals beyond the innovation-led hierarchy. Reuse already inspected construction evidence.
These are intentional visual content, not ornamental stickers. Keep them small, readable and coherent with the main reference. No invented observations, numerical results or unlabelled decorative particles.
## Typography reference
Reference-informed readable dark serif lettering, moderate bold headings. Preserve exact model names. No title background, gradients or underlines.
Use short Methodology-derived headings, no workflow aliases or added counters. Dark titles on white, no filled tabs. Align baselines, edges and spacing. No visible underscores, including code/IDs: typeset indices or use approved aliases. Keep raw IDs internal; reflow before shrinking fonts.
## Text and symbol economy
Emphasize framework innovation. Aim ≤100 English words; never pad. Only scientific necessity permits 101–160; maximum 160. Count repeats; hyphenated words count once. Prefer precise 2–3-word object names. Beyond headings, explain each idea once. Delete clear-arrow narration and fine lists covered by a summary. Remove generic ticks/warning/status badges unless scientifically needed. Borrow warranted architectural chains/stacks, not foreign topology or reference verbosity. Render only approved prose/symbol inventories, never instructions; inspect actual pixels.
## SVG-reference creative workflow
Preserve the full Creative Director role: coherent whole-figure style, creative grouping, colour, frames, arrows, meaningful symbols and local constructions. Add evidence and checks; do not reduce this to filling predetermined cards.
The Director owns the final colour decision. Source swatches below are observations, not an upstream colour lock. No palette-library selection for this run.
Dedicated COMPLETE palette SVG: input/palette.svg; source track: sentence scoring
Observed swatches: [{"role": "primary", "hex": "#5B9BD5", "rgb": [91, 155, 213]}, {"role": "accent", "hex": "#00B050", "rgb": [0, 176, 80]}, {"role": "pale", "hex": "#E5EBF7", "rgb": [229, 235, 247]}, {"role": "neighbour", "hex": "#DAE3F3", "rgb": [218, 227, 243]}, {"role": "ink", "hex": "#000000", "rgb": [0, 0, 0]}]
Observed adjacency/separation: [{"roles": ["primary", "pale"], "relation": "adjacent", "observation": "Fine blue square boundaries directly enclose very pale blue cells throughout the complete attention-mask SVG."}, {"roles": ["primary", "accent"], "relation": "separate", "observation": "Green query labels sit on white outside the blue cell array; stronger green and blue are spatially separated by white rather than adjacent solid areas."}, {"roles": ["pale", "neighbour"], "relation": "adjacent", "observation": "The forward/backward halves use two compatible low-saturation blue cell fills separated by thin lines."}]
Available source-derived tints/shades/tones: 
Retain mature colour rules: usually 1–2 dominant families; analogous light neighbours; deeper meaningful marks; isolate strong contrasting foci. White and readable black typography dominate. No invented universal contrast threshold.
Leave unnecessary surfaces white. A pale base frame may receive colour; important mechanism content may receive emphasis. Titles are ordinary text, never automatic colour strips. Do not recolour every object.
When user colours change, re-evaluate the whole relationship plan with the Director; do not do independent HEX substitutions.
Main style traits: CosyVoice2 LM SVG: thin black continuous arrows, modest round-corner white model enclosure, dark serif labels, sparse regular token marks and generous white separation; Transcormer complete mask SVG: pale blue neighbours with blue fine boundaries; green localized on white away from blue; do not copy matrix topology; MusicGen SVG: ordered native token cells; no imported multi-codebook layout
Avoid: colored title bands; colored full-panel surfaces; staircase routes; text outside parent frame; copied source model internals
Resolve content before the Director pass. Director locks colour, then places content-sized base frames and simple routes together, then fills content. Upstream draft geometry is revisable, not a fixed aesthetic.
No staircase or complex detour. Prefer a straight line; a necessary turn/return uses one smooth simple curve. If routing becomes complex, move or regroup frames first. Normally at most one input and one output per frame. Source-grounded multi-port exceptions require an explicit reason and actual internal landing.
Inspect topology beyond arrows: nested/parallel/repeated structures, node degree, merge/split semantics and operators such as addition, multiplication, concatenation or gates. Only include symbols actually supported by this method. Never invent internal modules to resemble a peer.
All text, titles, symbols and images stay inside their parent region with padding. No deep title backgrounds. Keep complete visual-reference language: typography, line character, frames, arrows, density and spacing.
Three design intentions (layout, flow, density): each starts 我想 and has at most 15 Chinese characters, or starts I want and has at most 15 English words. One line each, no commas.
Return a colour decision with chosen palette, rationale, region colours, adjacency review and whitespace plan. Retain the single source SVG and its observed relationships; choose source-derived extensions as needed. Return a topology review explaining supported structures/operators and omissions. These are planning metadata, never figure text.
## Scoped image references (attached in manifest order)
- input/palette-view.png [797x816] | style_anchor -> WHOLE FIGURE | borrow: Complete source SVG rendered locally for model transport. Borrow its coherent colour relationships, white separation, subdued source-derived fills, typography scale and purposeful frame/line treatment ONLY. This is NOT the scientific layout or model architecture to copy. Follow the Director exact new content, grouping, geometry and simple routes. No FiLM labels, network layers or source topology. Colour decisions come from the Director source-derived palette, never a fixed library. Keep all titles on white. | change: all source scientific content
Respect each crop aspect ratio when reading its construction; do not stretch a complete reference onto this new layout. Borrow only the declared grammar, never unrelated source nodes, labels or colours.
## Palette
Creative Director selected this source-derived palette; no fixed library.
Dedicated complete SVG: input/palette.svg
Dominant roles: primary, accent
primary: #5B9BD5
accent: #00B050
pale: #E5EBF7
neighbour: #DAE3F3
ink: #000000
melodytint: #E7F4EB
primary / pale: adjacent; Fine blue square boundaries directly enclose very pale blue cells throughout the complete attention-mask SVG.
primary / accent: separate; Green query labels sit on white outside the blue cell array; stronger green and blue are spatially separated by white rather than adjacent solid areas.
pale / neighbour: adjacent; The forward/backward halves use two compatible low-saturation blue cell fills separated by thin lines.
Use only selected roles where meaningful; white remains a deliberate surface. Black typography is allowed. Preserve the Director adjacency/separation and whitespace decisions.
## Final creative construction decisions
Creative Director brief:
- A white, type-led scholarly figure: main inference reads across the upper middle, offline representation sits lower left and lands in a separate training footer. The centre expands melody planning and reference conditioning; ordinary acoustic reconstruction stays a restrained vertical chain. Integrate observed thin native model frames and serif lettering with the dedicated pale-blue/green source relationships. No gradient, blanket panel wash or saturated model block.
Creative Director ideas:
Director colour rationale: Use the source pale blue for only compact semantic-token or model content, blue for fine mechanism boundaries, and a single source-green tint for optional Melody-CoT. Black text and dark arrows keep the page readable. Do not transplant attention masks.
Director adjacency review: The central blue semantic strip and small green melody planning inset stay separated by white. Supporting frames remain white, so pale blue and pale green never form adjacent full-panel colour fields. No green on renderer or input labels. Strong accents occupy only fine strokes or tiny token marks.
Director whitespace plan: All four major surfaces white; keep at least roughly three quarters of the figure uncoloured. No coloured title strips. Use white gutter around every group and between local colour foci.
condition region colours: white, black
tokenizer region colours: white, black, pale
llm region colours: white, black, primary, pale, melodytint
render region colours: white, black, pale
Topology review: Text tags/lyrics condition both dense autoregressive LM and renderer, so Text Conditioning has two real exits. The renderer has distinct semantic-token and text entrances; each must land at DiT or Text encoder. The LLM has inference conditioning and offline targets entering separate actual subregions. These are source-supported multi-port exceptions, not generic aesthetic branching. Music tokenizer is an offline support path, never upstream inference input. A single 3B LM generates optional Melody-CoT before music tokens or directly emits music tokens; do not draw Melody-CoT as mandatory preprocessing. Cover melody tokens condition that same LM prefix. No additive/multiplicative gates, MoE, codebook stacks or attention matrices are supported.
Design intent: 我想主线横排训练另置
Design intent: 我想文字经语义生成音乐
Design intent: 我想旋律局部紧凑其余留白
- `melody-prefix` -> `llm`: One LM with optional generated melody and cover reference prefix Intent: Explain the actual innovation at token interface level while keeping the familiar dense backbone whole. Construction: Shared 3B dense LM at mainline height. Show an optional small green-tint Melody-CoT sequence between autoregressive prefix planning and full-mixture semantic continuation, alongside direct generation. Cover-song reference melody passes through a compact named Melody Tokenizer (RMVPE, median pooling, relative pitch) to 6.25Hz melody tokens entering the same LM prefix. Do not feed music tags to RMVPE. Music Semantic Tokens at 25Hz are the only mainline output. Keep local lines short and simple; no invented network layers.
- `offline-support` -> `tokenizer`: Offline representation kept apart from inference Intent: Prevent the prior false mandatory audio-to-LLM chain. Construction: Small lower-left white region: tiny schematic audio mark, log-Mel, causal Conformer, single-codebook VQ and 25Hz token row. A dashed straight edge enters ONLY an isolated lower LLM training-target footer. No target-to-original-song inference arrow. Put Offline training targets label inside the tokenizer frame.
- `acoustic-render` -> `render`: Two real conditioning signals meet at DiT Intent: Use correct actual landings instead of border-only arrows. Construction: Top incoming text curve lands at Text encoder inside renderer; its local down arrow goes into DiT. Mainline semantic edge continues from the west boundary to a distinct DiT inlet. Chain: DiT, acoustic latents, Spec-VAE decoder, complex spectrogram, Band-Mode Refiner, inverse STFT, then 48kHz stereo schematic waveform. Supporting spectral intermediates use only simple native outlines, not invented data heatmaps.
Approved visible text inventory (only these prose strings may be drawn; repeats are intentional):
["Qwen-Music-Tokenizer", "Offline training targets", "Example audio", "Log-Mel", "Causal Conformer", "Single-codebook VQ", "25 Hz tokens", "Text Conditioning", "User request", "Prompt rewriter", "Music tags + Lyrics", "Qwen-Music-LLM", "3B dense LM", "Original song", "Direct generation", "Melody-CoT (optional)", "Cover song", "Reference melody", "Melody Tokenizer", "RMVPE", "Median pooling", "Relative pitch", "6.25 Hz melody tokens", "Music Semantic Tokens", "25 Hz", "Quality-graded pre-training", "SFT → DPO → GSPO", "Qwen-Music-Render", "Text encoder", "Flow-matching DiT", "Acoustic latents", "Spec-VAE decoder", "Complex spectrogram", "Band-Mode Refiner", "Inverse STFT", "48 kHz stereo"]
Reported English word count: 77
Approved mathematical symbol inventory:
[]
All remaining construction descriptions and route meanings are instructions, not additional lettering.
## Final drawing checks
White frames and black labels; no header bands or gradients.
Every label and local object inside parent; outside frames only actual inter-frame shafts.
Training targets land only at training footer; do not enter original-song inference.
Tokens enter DiT; rewritten text enters text encoder; no floating endpoints.
Verify every listed arrow endpoint, concise label and semantic inset before finishing. No gray microcopy, pseudo-text, gratuitous gradients, glow, pasted clip-art or decorative badge. Purposeful dividers and hand-drawn semantic icons are allowed. Keep exact repeated geometry regular.
Generate one PNG1. Do not copy planning prose or evidence hashes into the image.