Create one complete scientific figure from this locked generation checklist.
Evidence SHA256: d3d4c6a2f1031232170b9928332ed86cdf26e502cc06a6650e4175d544503c7b
## Scientific meaning
MusiCoT trains a single text-conditioned semantic LM on coarse-first CLAP RVQ thought tokens followed by audio tokens. CLAP embeddings of 10-second clips yield analyzable intermediate musical thoughts.
- Thoughts are continuous CLAP embeddings represented by RVQ tokens, not natural-language reasoning.
- For M clips and L codebooks, flatten all M tokens of level 1, then level 2, through level L; do not flatten clip by clip.
- LM predicts thought tokens before audio tokens; training uses CE for both token domains.
- Dual temperatures T₁/T₂ and CFG scales λ₁/λ₂ belong to thought/audio domains, respectively.
- CLAP internals and fixed/trainable flags are not specified in the supplied excerpt; do not invent them. RVQ is trained by reconstruction quantization loss.
- Analysis reconstructs quantized CLAP vectors and compares cosine similarity to relevant text anchors; heatmap is schematic, not experiment data.
- Diagram output stops at audio tokens, as supplied Methodology; do not invent a direct CLAP audio decoder.
## Visual-needs anchor (Methodology intersected with inspected peer conventions)
- tokens: Aligned temporal/codebook grid with explicit flatten order | Methodology: L codebooks flattened coarse-to-fine, all M time positions at each level | Peers: MusicLM Fig2 uses semantic/acoustic token strips; MusicGen Fig1 shows codebook-time grids and explicit ordering.
- wave: Actual audio representation and readable model boundaries | Methodology: CLAP processes 10-second audio segments; one semantic LM | Peers: MusicLM Fig2 shows waveform specimens and whole encoding/decoding modules; MusicGen token grid abstracts the representation outside model internals.
## Innovation-led detail hierarchy
Peer depth observation: MusicGen Fig1 resolves tokens within codebook/time grid, while MusicLM Fig2 keeps encoders and generative stages as whole modules.
- Innovation: Analyzable coarse-to-fine musical thought sequence | Focus: rvq, thought, analysis | Finest visible unit: Individual cells, level-major ordering and cosine-similarity analysis branch.
- Innovation: Dual-domain sampling | Focus: sampling | Finest visible unit: Two parameter rows, paired temperature and CFG scale per domain.
Shared non-innovation depth: Supporting CLAP and LM stay whole-model; audio/text stay input strips.
Keep whole (no invented model internals): clap, lm
Allocate detail to the actual contributions; do not expand standard components just because they are familiar. Match supporting regions at the shared level.
## Locked overall framework
A complete rectangular equal-division 3×3 matrix within one landscape frame. All nine component panels are identical 440×260 rectangles. Top row left-to-right: Music Audio, CLAP Embeddings, Coarse-to-Fine RVQ. Middle row: Text Tokens, Dual Sampling, Semantic LM. Bottom row: Structural Analysis, Audio Tokens, Musical Thoughts. The semantic chain turns downward at the right edge; predicted thoughts feed audio tokens leftward. Analysis and control are fully reserved equal cells, never dangling footers. Read the actual arrow directions, without invented row-wide buses. Use one white outer frame x40–1640/y50–1120, title above. Two inter-row gutters and one bottom analysis lane contain only specified arrows and concise captions. Native scientific microviews differentiate content inside the shared rectangular framework.
Imagine the whole structural overview as one clean, complete rectangular silhouette before details. Choose an explicit organizing rule: equal-width stage columns, equal-height parallel bands, or a balanced bilateral arrangement, according to the scientific graph. State which rule is used. Equalize peer regions, margins and gutters; innovation may span integer cells without protruding. Visual balance never invents a second branch, reverses an edge, or turns unrelated edges into a bus. Fix the canvas and row/column grid first; reserve the final-output cell before drawing. Align sibling block edges/baselines; innovation panels may span cells. Keep every planned block and the final output inside that same footprint. If crowded, simplify or reflow upstream content rather than extending a dangling last block. Keep flow simple; no added step numbers.
Canvas pixels: [1680, 1160]; preserve the exact boxes and path points below. Scale the entire composition uniformly.
Grid rows: [[70, 330], [430, 690], [790, 1050]]; columns: [[60, 500], [620, 1060], [1180, 1620]]
Clearance: 10 pixels. Captions must stay in their reserved boxes; never cut shafts.
## Connector construction (Creative Director and generator)
Plan module placement and connector clearance together, before locking the composition. Prefer straight source-to-target arrows. Reposition nearby modules to eliminate crossings and unnecessary bends rather than drawing a detour around a poor layout. Use only a few consistent right-angle bends; geometry-locked routes follow their exact path points. Every arrow is one continuous, human-reproducible path from the actual source border to the target arrowhead: no disappearing shafts, isolated arrowheads, empty-space starts or unexplained gaps. Keep labels beside the shaft, never erase the shaft to fit text. Avoid intersections; if a crossing is scientifically unavoidable, use a clear continuous bridge and distinguish it from a junction. Align source and target ports on one shared horizontal or vertical axis wherever possible. Use a single consistent arrowhead size and stroke weight; local microview arrows follow the same grammar. Mainline arrows should read immediately; return loops use a separate perimeter lane. Reserve section-heading bands separately from connector corridors. Background fills and title bands never erase shafts. After placing labels and icons, trace each complete shaft again; revise crowded placement instead of extending routes.
Draw every named component once. A container may be the component itself; do not add duplicate stand-ins. Repeated snapshots inside a component are insets, not extra pipeline nodes.
## Exact components and placement
- audio = `Music Audio` | box [60, 70, 440, 260] | Segmented waveform, 0–10 s, 10–20 s, …
- clap = `CLAP Embeddings` | box [620, 70, 440, 260] | Whole CLAP encoder and aligned continuous embedding bars; 10 s per embedding
- rvq = `Coarse-to-Fine RVQ` | box [1180, 70, 440, 260] | L codebook rows by M time positions; first row c¹₁ … cᴹ₁, second c¹₂ … cᴹ₂, last c¹ᴸ … cᴹᴸ; flatten row by row
- text = `Text Tokens` | box [60, 430, 440, 260] | Compact token strip; illustrative prompt: piano and drums
- lm = `Semantic LM` | box [1180, 430, 440, 260] | Single whole semantic LM spanning aligned thought and audio prediction zones; CE targets in training
- thought = `Musical Thoughts` | box [1180, 790, 440, 260] | Predicted CLAP RVQ token strip, coarse before fine; start/end markers
- sound = `Audio Tokens` | box [620, 790, 440, 260] | Audio token strip follows thought end in same autoregressive sequence
- analysis = `Structural Analysis` | box [60, 790, 440, 260] | Quantized CLAP embeddings versus text anchors piano/drums; cosine similarity heatmap with time columns; schematic, no invented numerical results
- sampling = `Dual Sampling` | box [620, 430, 440, 260] | Two neat aligned rows: Thoughts: T₁, λ₁; Audio: T₂, λ₂; temperatures and CFG scales
## Exact directed connections (one arrowhead per relationship)
These relationship labels specify meaning. Show only short relation captions where needed; not every arrow needs visible explanatory text. Preserve essential scientific notation and conditions.
- audio.east -> clap.west | `10 s clips` | mainline points [[500, 200], [620, 200]]
- clap.east -> rvq.west | `quantize` | mainline points [[1060, 200], [1180, 200]]
- rvq.south -> lm.north | `training targets` | reference points [[1450, 330], [1450, 430]] | visible caption `Training` in box [1470, 361, 130, 28]
- text.north -> lm.north | `condition` | branch points [[280, 430], [280, 380], [1250, 380], [1250, 430]]
- lm.south -> thought.north | `predict first` | mainline points [[1400, 690], [1400, 790]]
- thought.west -> sound.east | `then predict` | mainline points [[1180, 920], [1060, 920]]
- thought.south -> analysis.south | `reconstruct embeddings` | branch points [[1400, 1050], [1400, 1100], [280, 1100], [280, 1050]] | visible caption `Reconstruct embeddings` in box [650, 1060, 340, 28]
- sampling.east -> lm.west | `sampling controls` | branch points [[1060, 560], [1180, 560]]
Ports name the actual object/frame boundary. Never stop at an empty margin, nearby input, or unrelated enclosing stage. Independent evidence edges have distinct landing ports and arrowheads; crossings are not junctions. Do not merge unrelated evidence into one long bus.
## One-to-one drawing correspondence
| Need / location | Reference construction or source basis | Our adapted drawing |
| --- | --- | --- |
| tokens / rvq | MusicGen Fig1 token lattice; own CLAP content and own layout. | Within the equal-size RVQ panel draw 3 symbolic rows labeled Codebook 1, Codebook 2, Codebook L with the same 4 symbolic time columns 1, 2, …, M. A flattened strip below contains the complete row 1 followed by the complete row 2 then … row L. Pale vermilion cells with stronger coarse-row emphasis; avoid clip-major order and do not fabricate data. |
| wave / audio | MusicLM Fig2 waveform specimens; own native schematic. | One waveform split into equal duration clip windows with 0,10,20 s ticks. |
These are intentional visual content, not ornamental stickers. Keep them small, readable and coherent with the main reference. No invented observations, numerical results or unlabelled decorative particles.
## Typography reference
Arial, dark near-black text; 28–30 px unnumbered panel headings, 21–24 px essential labels, consistent baselines. Real subscripts and superscripts. No tiny gray notes. Keep schematic marker readable and dark.
Use short unnumbered scientific headings derived only from this Methodology. Never copy stage titles from workflow instructions or other cases. Internal orchestration codes stay in planning, not reader-facing headings. Keep image text to labels, essential terms and equations. Typeset mathematical indices as real subscripts/superscripts. NO visible underscore anywhere, including identifiers and illustrative code. Use approved typeset aliases; raw IDs/source code stay in internal records. Optically align text baselines, object edges and centers with consistent spacing/padding. Shorten text or rearrange crowded groups before shrinking fonts.
## Global style direction (before domain-search aesthetics)
Global style anchor: apply the explicitly liked reference traits, such as typography, linework, spacing or colour relationships, coherently across the figure. State what is borrowed; do not claim to copy the whole reference or its composition. Layout and detail hierarchy come from this Methodology and its innovations. Do not copy source labels, characters or scientific claims. Component references affect only their named target. Active colours come from the selected compatible palette group. Semantic hand-drawn icons and purposeful dividers are allowed; no pasted stickers or meaningless ornaments.
Style brief SHA256: b60ffd494d29d02017e96a8e982bde9f7fe26843bf769b1ebfd6f6f9ba10ce62
Family: architecture_2d; reference mode: model_composed
Stage labeling: do not invent stages or panel letters. No generic numbered badges, emoji or decorative step labels.
Typography follows the main reference consistently; do not default to Times New Roman. Formulas may retain appropriate mathematical notation. No gray microcopy or invented caution notes. Necessary short italic explanations use readable Arial Italic in black or a coherent dark ink. Black is welcome; do not make all text pastel.
Frame and arrow grammar remain consistent. Neighboring base frames use analogous, similarly light fills; at most one local strong contrast focus in each proximity group. Separate far-away regions may carry a second emphasis only when the declared layout justifies their separation.
Use pale support surfaces and deeper main marks, or a reference-supported inverse. Keep saturation and the chosen style coherent.
Declared proximity groups: [["audio", "clap", "rvq"], ["text", "lm", "thought", "sound"], ["sampling", "analysis"]]; contrast foci: rvq
User likes: Aligned token lattices and clear whole-model boundaries observed in peers; Consistent thin paths, Arial typography and generous white gutters, composed originally
Avoid: Copied scholarly composition; Generic decorative AI icons; Numbered stages; Tiny gray prose
Reading path: main_side_chain; scientific mainline: audio -> clap -> rvq -> lm -> thought -> sound
Keep every scientific edge. Simplify presentation, not scientific meaning. Every arrow has an unambiguous source and destination; add concise relation labels where needed. Arc/S layouts are geometry, not permission to invent cycles; distinguish crossings from junctions.
Palette for this run: earth-data-01. Muted deep teal suits orderly continuous and discrete music representations; vermilion gives the new RVQ ordering a single contrast focus; warm pale surfaces provide restrained support. Example purple/blue/orange hues are illustrative, not a default theme. Select per reference; reuse is allowed. Lock hues only on explicit user request.
Use adjacent/analogous shades for related modules; one contrast family at one semantic emphasis focus: rvq. Distant extra focus, if any, follows the declared proximity plan; related legend marks may repeat that accent. Neutrals and subordinate tints are not additional dominant colours; no gratuitous gradients.
Style may be imagined within this brief when no approved image exists, during the same Creative Director pass; do not generate an extra style-sheet image.
## Scoped image references (attached in manifest order)
Respect each crop aspect ratio when reading its construction; do not stretch a complete reference onto this new layout. Borrow only the declared grammar, never unrelated source nodes, labels or colours.
## Palette
Style-selected palette group: earth-data-01
Dominant roles (style brief, not the first paper): primary, accent
muted: #B7B49F
primary: #44757B
ink: #452A3D
accent: #D34D3A
comparison: #DC6C4C
surface: #EFD5B7
Use only this palette group's active colours/evidenced extensions; borrow reference colour relationships, not source swatches.
## Final creative construction decisions
Creative Director brief:
- Original equal-division 3×3 MusiCoT diagram: nine matched rectangular panels establish one complete balanced silhouette, with one coherent teal and warm neutral palette and a single vermilion RVQ emphasis. Start with the bounded frame and exact validated boxes, construct native scientific microviews, route all eight continuous shafts at the exact points, then add short dark Arial labels. This is a fresh text-only ideation pass informed by the copied inspected research cache, with no repeated research, image attachment or borrowed composition. The right-column training and prediction cascade makes the dominant path clear; two modest two-bend branches carry text conditioning and reconstructed embeddings. Dual Sampling has a full central panel equal to its peers, so control detail no longer dangles beneath the figure. Plain supporting modules stay whole; the RVQ ordering, predicted thought structure, analyzability and two-domain controls carry meaningful detail. Only the two declared route captions print; no prose footer, numbered steps or tiny gray notes.
Creative Director ideas:
- `equal-matrix-rvq` -> `rvq`: Coarse-first lattice within a fixed peer panel Intent: Make the actual innovation legible without breaking the regular outer grid. Construction: Keep the exact 440×260 frame. Heading on the shared 30-pixel inset baseline. Below, draw a compact 3×4 symbolic token lattice: Codebook 1, Codebook 2, Codebook L; columns 1, 2, …, M. All M time positions from one codebook precede the next. A short level-major flattened strip at the bottom repeats full row 1, full row 2, …, full row L. Use row labels rather than difficult superscript token indices when space is tight; never portray the final codebook index as a superscript. Pale vermilion background and deeper vermilion token edges provide the only contrasting focus. This is a representation schematic, not measured token data.
- `paired-central-controls` -> `sampling`: Two-domain parameter table in the reserved central cell Intent: Give sampling controls the same deliberate rectangular footprint as every other scientific component. Construction: Use the common heading baseline and a compact native table with column labels Temperature and CFG, two aligned domain rows Thoughts and Audio, entries T₁ and λ₁ then T₂ and λ₂. Use dark readable 23-pixel Arial. Keep the rest of the panel calm; no knobs, sliders, oversized empty decorative cards or tiny explanatory paragraphs. The sole outgoing control arrow is the exact horizontal east-to-west shaft into the LM.
- `whole-lm-prediction` -> `lm`: Single LM with a two-domain prediction rhythm Intent: Keep a standard model whole while stating the training and generation contract. Construction: Inside the equal frame draw one plain teal whole-model rectangle with Semantic LM heading and a concise CE: thoughts + audio label. Do not draw transformer layers or invent fixed/trainable flags. Text conditioning and RVQ training enter distinct north ports; controls enter west; the sole south output predicts thoughts first. Maintain distinct continuous arrowheads at each exact landing.
- `thought-stream` -> `thought`: Readable coarse-to-fine intermediate stream Intent: Retain a meaningful thought representation and make its two uses explicit. Construction: Inside the bottom-right panel show thought start, a row-major symbolic CLAP RVQ strip divided into coarse and fine groups, then thought end. Use true T₁/λ₁ indices only in the control table; here short Coarse and Fine captions suffice. The west arrow leads to Audio Tokens; the south branch runs continuously along the reserved bottom lane then up into Structural Analysis. No natural-language reasoning bubbles. Keep a uniform 3-pixel line and 12-pixel arrowhead throughout.
- `schematic-analysis` -> `analysis`: Quantized-vector and text-anchor comparison Intent: Show what analyzability computes without inventing an experimental result. Construction: Within the equal panel, put short Quantized CLAP and Text anchors captions above a compact cosine-similarity tile map. Use two rows piano and drums, time columns 0–10 s and 10–20 s plus ellipsis. Native light/deep teal tiles remain schematic, without numerical scores, colorbar claims or results trend. Print Schematic in readable dark Arial on the shared lower baseline. Keep this component inside the common bottom edge.
## Final drawing checks
Airy publication diagram; dark Arial labels; no decorative icons; restrained teal with one vermilion RVQ focus.
Verify every listed arrow endpoint, concise label and semantic inset before finishing. No gray microcopy, pseudo-text, gratuitous gradients, glow, pasted clip-art or decorative badge. Purposeful dividers and hand-drawn semantic icons are allowed. Keep exact repeated geometry regular.
Generate one PNG1. Do not copy planning prose or evidence hashes into the image.