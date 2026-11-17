Create one complete scientific figure from this locked generation checklist.
Evidence SHA256: a6dcc4a89abc5bf70e614abe75efa4d6704494dffdd33c085747b2a68c04d8f8
## Scientific meaning
Perceptual autoencoding learns a spatial latent space separately from generative diffusion. A time-conditional U-Net denoises in that lower-dimensional space; cross-attention supplies conditional control; decoding is one pass.
- Compression is learned before diffusion; latent space is fixed during generative learning.
- Condition encoder and denoiser are jointly optimized; do not mark the condition encoder frozen.
- Forward noising is fixed and training-only; synthesis begins from Gaussian latent noise.
- Keep actual latent spatial grids, not a one-dimensional token vector.
- A shared decoder reconstructs encoded inputs and decodes generated latent samples in one pass.
- Schematic landscape miniatures are illustrative, not measured samples.
- Q derives from U-Net spatial features; K,V derive from encoded condition. No full attention formula needed.
## Visual-needs anchor (Methodology intersected with inspected peer conventions)
- v-images: image-valued source/reconstruction/output views | Methodology: x RGB and D(z) image reconstruction / generation | Peers: Both DDPM Fig2 and Imagen FigA4 use image miniatures at image-valued stages.
- v-spatial: spatial reduced latent and noisy state | Methodology: DM retains two-dimensional structure in latent space | Peers: DDPM Fig2 shows noisy image-valued intermediate views; Imagen FigA4 retains square spatial image views between models.
- v-direction: generation chain with conditional input | Methodology: Time-conditional U-Net augmented with cross-attention | Peers: DDPM Fig2 uses directed reverse transitions; Imagen FigA4 uses connected generative blocks and a conditioning branch.
## Innovation-led detail hierarchy
Peer depth observation: DDPM Fig2 expands timestep states and Imagen FigA4 stays at whole-model cascade units. Our innovation warrants spatial-latent views and a scoped cross-attention insertion, not generic convolution internals.
- Innovation: Separation of perceptual compression from lower-dimensional spatial diffusion | Focus: latent, noise, denoise, sample | Finest visible unit: Spatial grid and iterative denoising states in a dedicated latent lane.
- Innovation: Flexible conditional generation via U-Net cross-attention | Focus: condencoder, denoise | Finest visible unit: Q versus K,V input distinction, with a small attention inset embedded in denoiser.
Shared non-innovation depth: All support models remain single named encoder/decoder blocks; image and latent representations are meaningful thumbnails.
Keep whole (no invented model internals): encoder, decoder, condencoder
Allocate detail to the actual contributions; do not expand standard components just because they are familiar. Match supporting regions at the shared level.
## Locked overall framework
Title Latent Diffusion. One complete 1700×1000 rectangular overview organized by six equal-width columns and two equal-height aligned scientific lanes, with a shallow middle conditioning strip. Top: Perceptual Compression. Bottom: Latent Generation. Upper and lower image thumbnails share left/right edges, labels share baselines, pale lane backgrounds share the exact left and right bounds. The shared decoder occupies one vertical column with separate aligned reconstruction and generation ports. The wider innovative denoising group spans two integer columns. These are invisible placement bounds, not a grid of empty cards. Preserve all scientific miniature views. Do not add phase labels from any other workflow.
Imagine the whole structural overview as one clean, complete rectangular silhouette before details. Choose an explicit organizing rule: equal-width stage columns, equal-height parallel bands, or a balanced bilateral arrangement, according to the scientific graph. State which rule is used. Equalize peer regions, margins and gutters; innovation may span integer cells without protruding. Visual balance never invents a second branch, reverses an edge, or turns unrelated edges into a bus. Fix the canvas and row/column grid first; reserve the final-output cell before drawing. Align sibling block edges/baselines; innovation panels may span cells. Keep every planned block and the final output inside that same footprint. If crowded, simplify or reflow upstream content rather than extending a dangling last block. Keep flow simple; no added step numbers.
Canvas pixels: [1700, 1000]; preserve the exact boxes and path points below. Scale the entire composition uniformly.
Grid rows: [[140, 320], [430, 570], [680, 860]]; columns: [[50, 250], [330, 530], [610, 810], [890, 1090], [1170, 1370], [1450, 1650]]
Clearance: 8 pixels. Captions must stay in their reserved boxes; never cut shafts.
## Connector construction (Creative Director and generator)
Plan module placement and connector clearance together, before locking the composition. Prefer straight source-to-target arrows. Reposition nearby modules to eliminate crossings and unnecessary bends rather than drawing a detour around a poor layout. Use only a few consistent right-angle bends; geometry-locked routes follow their exact path points. Every arrow is one continuous, human-reproducible path from the actual source border to the target arrowhead: no disappearing shafts, isolated arrowheads, empty-space starts or unexplained gaps. Keep labels beside the shaft, never erase the shaft to fit text. Avoid intersections; if a crossing is scientifically unavoidable, use a clear continuous bridge and distinguish it from a junction. Align source and target ports on one shared horizontal or vertical axis wherever possible. Use a single consistent arrowhead size and stroke weight; local microview arrows follow the same grammar. Mainline arrows should read immediately; return loops use a separate perimeter lane. After placing labels and icons, trace each complete shaft again; revise crowded placement instead of extending routes.
Draw every named component once. A container may be the component itself; do not add duplicate stand-ins. Repeated snapshots inside a component are insets, not extra pipeline nodes.
## Exact components and placement
- image = `RGB Image x` | box [50, 140, 200, 180] | Framed original schematic landscape thumbnail.
- encoder = `Encoder E` | box [330, 140, 200, 180] | Simple tapering block, whole model.
- latent = `Spatial Latent z` | box [610, 140, 200, 180] | Stack of three small aligned two-dimensional grid planes.
- reconstruct = `Reconstruction x̃` | box [1450, 140, 200, 180] | Framed matching landscape thumbnail.
- noise = `Latent Noise zₜ` | box [50, 680, 200, 180] | Square fine noise grid, visibly smaller spatial representation than RGB thumbnail.
- condition = `Condition y` | box [610, 430, 200, 140] | Short text token strip, e.g. a mountain lake.
- condencoder = `Condition Encoder τθ` | box [890, 430, 200, 140] | Small whole-model rectangle, trainable with denoiser.
- denoise = `Latent Denoising` | box [330, 680, 480, 180] | Large bounded U-Net glyph with down/up levels and a cross-attention inset, no layer inventory.
- sample = `Sample z₀` | box [890, 680, 200, 180] | Small spatial grid with emerging landscape structure.
- decoder = `Decoder D` | box [1170, 140, 200, 720] | Whole decoder block shared by reconstruction and generation.
- output = `Generated Image x̂` | box [1450, 680, 200, 180] | Original illustrative landscape thumbnail, schematic sample, not an empirical result.
## Exact directed connections (one arrowhead per relationship)
These relationship labels specify meaning. Show only short relation captions where needed; not every arrow needs visible explanatory text. Preserve essential scientific notation and conditions.
- image.east -> encoder.west | `encode` | mainline points [[250, 230], [330, 230]]
- encoder.east -> latent.west | `z = E(x)` | mainline points [[530, 230], [610, 230]]
- latent.east -> decoder.west | `reconstruct` | mainline points [[810, 230], [1170, 230]]
- decoder.east -> reconstruct.west | `x̃ = D(z)` | mainline points [[1370, 230], [1450, 230]]
- latent.south -> noise.north | `add noise · training` | reference points [[710, 320], [710, 375], [150, 375], [150, 680]]
- noise.east -> denoise.west | `zₜ, t` | mainline points [[250, 770], [330, 770]]
- condition.east -> condencoder.west | `encode condition` | mainline points [[810, 500], [890, 500]]
- condencoder.south -> denoise.north | `K, V` | branch points [[990, 570], [990, 625], [700, 625], [700, 680]]
- denoise.east -> sample.west | `iterative denoising` | mainline points [[810, 770], [890, 770]]
- sample.east -> decoder.west | `single decode` | mainline points [[1090, 770], [1170, 770]]
- decoder.east -> output.west | `x̂ = D(z₀)` | mainline points [[1370, 770], [1450, 770]]
Ports name the actual object/frame boundary. Never stop at an empty margin, nearby input, or unrelated enclosing stage. Independent evidence edges have distinct landing ports and arrowheads; crossings are not junctions. Do not merge unrelated evidence into one long bus.
## One-to-one drawing correspondence
| Need / location | Reference construction or source basis | Our adapted drawing |
| --- | --- | --- |
| v-images / image | DDPM Fig2 and Imagen FigA4 show specimen thumbnails; own schematic anatomy replaces source examples. | Matching simple mountain-lake landscape miniatures for x and reconstruction; original plausible different landscape for generated sample. |
| v-spatial / latent | Peer spatial-state images plus inspected reference002 stacked feature planes. | Draw compact stack of square grid planes; same footprint for noisy and generated latent. |
| v-direction / denoise | Peer directed chain and conditioning branch; reference005 input-port construction, redrawn with our cross-attention semantics. | Coarse U silhouette with simple spatial feature layers; inset cross-attention shows Q from feature path and K,V entering from condition above. |
These are intentional visual content, not ornamental stickers. Keep them small, readable and coherent with the main reference. No invented observations, numerical results or unlabelled decorative particles.
## Typography reference
Arial dark labels, 30 px stage headings, 23 px component names, 20 px mathematics; short notes dark Arial Italic.
Use short unnumbered scientific headings derived only from this Methodology. Never copy stage titles from workflow instructions or other cases. Internal orchestration codes stay in planning, not reader-facing headings. Keep image text to labels, essential terms and equations. Typeset mathematical indices as real subscripts/superscripts. NO visible underscore anywhere, including identifiers and illustrative code. Use approved typeset aliases; raw IDs/source code stay in internal records. Optically align text baselines, object edges and centers with consistent spacing/padding. Shorten text or rearrange crowded groups before shrinking fonts.
## Global style direction (before domain-search aesthetics)
Global style anchor: apply the explicitly liked reference traits, such as typography, linework, spacing or colour relationships, coherently across the figure. State what is borrowed; do not claim to copy the whole reference or its composition. Layout and detail hierarchy come from this Methodology and its innovations. Do not copy source labels, characters or scientific claims. Component references affect only their named target. Active colours come from the selected compatible palette group. Semantic hand-drawn icons and purposeful dividers are allowed; no pasted stickers or meaningless ornaments.
Style brief SHA256: 8b7c40e22fb84ded86d006fc2d39a86801109f59f4d01834392078dfa2ade78a
Family: architecture_2d; reference mode: model_composed
Stage labeling: do not invent stages or panel letters. No generic numbered badges, emoji or decorative step labels.
Typography follows the main reference consistently; do not default to Times New Roman. Formulas may retain appropriate mathematical notation. No gray microcopy or invented caution notes. Necessary short italic explanations use readable Arial Italic in black or a coherent dark ink. Black is welcome; do not make all text pastel.
Frame and arrow grammar remain consistent. Neighboring base frames use analogous, similarly light fills; at most one local strong contrast focus in each proximity group. Separate far-away regions may carry a second emphasis only when the declared layout justifies their separation.
Use pale support surfaces and deeper main marks, or a reference-supported inverse. Keep saturation and the chosen style coherent.
Declared proximity groups: [["image", "encoder", "latent", "reconstruct"], ["noise", "denoise", "sample", "decoder", "output"]]; contrast foci: denoise
User likes: Precise spatial grids and parallel aligned scientific lanes.; Consistent dark line weight, clean Arial typography, sparse pale related enclosures.
Avoid: Numbered stage badges; Generic empty equal cards; All source composition copying; Visible underscores
Reading path: main_side_chain; scientific mainline: noise -> denoise -> sample -> decoder -> output
Keep every scientific edge. Simplify presentation, not scientific meaning. Every arrow has an unambiguous source and destination; add concise relation labels where needed. Arc/S layouts are geometry, not permission to invent cycles; distinguish crossings from junctions.
Palette for this run: biomedical-contrast-01. Blue gives a coherent cool latent/compression architecture; restrained separated red identifies the cross-attention mechanism. Pale blue surfaces remain subordinate; yellow and green library swatches are not promoted. Example purple/blue/orange hues are illustrative, not a default theme. Select per reference; reuse is allowed. Lock hues only on explicit user request.
Use adjacent/analogous shades for related modules; one contrast family at one semantic emphasis focus: denoise. Distant extra focus, if any, follows the declared proximity plan; related legend marks may repeat that accent. Neutrals and subordinate tints are not additional dominant colours; no gratuitous gradients.
Style may be imagined within this brief when no approved image exists, during the same Creative Director pass; do not generate an extra style-sheet image.
## Scoped image references (attached in manifest order)
Respect each crop aspect ratio when reading its construction; do not stretch a complete reference onto this new layout. Borrow only the declared grammar, never unrelated source nodes, labels or colours.
## Palette
Style-selected palette group: biomedical-contrast-01
Dominant roles (style brief, not the first paper): primary, accent
ink: #14517C
primary: #2F7FC1
surface: #E7EFFA
secondary: #96C37D
comparison: #F3D266
accent: #D8383A
muted: #A9B8C6
Use only this palette group's active colours/evidenced extensions; borrow reference colour relationships, not source swatches.
## Final creative construction decisions
Creative Director brief:
- Organizing rule: equal-width columns, two matched-height horizontal scientific lanes, common left/right image bounds, and one short centered conditioning strip. The whole silhouette is rectangular and balanced; denoising spans two cells and the single shared decoder spans the lane height. Keep the blue architectural palette and red cross-attention focus. Every main route is a straight axis-aligned source-border to target-border arrow. Training-only noising uses the empty left inter-lane corridor; the condition branch uses the short central corridor. Draw bounding boxes as invisible layout bounds except where a scientific model/group needs a frame. No extra stages, empty cards, ornament or invented scientific symmetry. Place all text clear of the actual continuous shafts.
Creative Director ideas:
- `matched-lanes` -> `latent`: Separate perceptual compression and latent generation in equal-height aligned lanes. Intent: Preserve image-valued thumbnails and two-dimensional spatial latent states while making their two roles immediately comparable. Construction: Match input/reconstruction/generated thumbnail sizes; use aligned native plane grids for latents. The fixed forward-noising training branch uses exact reserved points and a short nearby dark caption. Caption never erases a shaft. Decoder appears once as a shared vertical whole-model block with two independent port pairs, not repeated stand-ins.
- `bounded-attention` -> `denoise`: Give the innovative denoising and conditional attention mechanism an integer two-column span. Intent: Show what condition controls and retain meaningful small scientific visuals without losing the regular silhouette. Construction: Draw one flat U-shaped multiscale feature icon with one red cross-attention insert. Q originates at a spatial feature, K,V enter from the condition encoder at the declared top port. A small internal sequence of spatial grids conveys iteration rather than decorative particle dots. Use readable short labels, true subscript t and zero, identical arrowheads and consistent stroke. Re-trace every shaft after text placement.
## Final drawing checks
Precise architecture geometry with white space and dark labels.
Pale blue related regions; red limited to cross-attention emphasis.
Verify every listed arrow endpoint, concise label and semantic inset before finishing. No gray microcopy, pseudo-text, gratuitous gradients, glow, pasted clip-art or decorative badge. Purposeful dividers and hand-drawn semantic icons are allowed. Keep exact repeated geometry regular.
Generate one PNG1. Do not copy planning prose or evidence hashes into the image.