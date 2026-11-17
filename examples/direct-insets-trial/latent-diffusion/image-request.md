Create one complete scientific figure from this locked generation checklist.
Evidence SHA256: f43adbb24af1af286cf57a1b32a1e70c6e6135aa89053b563bb1115f4b97db1a
## Scientific meaning
Perceptual autoencoding learns a spatial latent space separately from generative diffusion. A time-conditional U-Net denoises in that lower-dimensional space; cross-attention supplies conditional control; decoding is one pass.
- Compression is learned before diffusion; latent space is fixed during generative learning.
- Condition encoder and denoiser are jointly optimized; do not mark the condition encoder frozen.
- Forward noising is fixed and training-only; synthesis begins from Gaussian latent noise.
- Keep actual latent spatial grids, not a one-dimensional token vector.
- A shared decoder reconstructs encoded inputs and decodes generated latent samples in one pass.
- Q derives from U-Net spatial features; K,V derive from encoded condition. No full attention formula needed.
- The input photograph is a real NASA image used only as an illustrative input. All reconstructed/generated outputs and latent imagery are schematic illustrations, not actual model results.
- Do not redraw the selected photo; its declared square slot remains clean for deterministic embedding.
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
Latent Diffusion, one bounded rectangular 1700×1150 overview. Six equal-width columns. Two matched-height scientific lanes titled Perceptual Compression and Latent Generation, both centered horizontally in dedicated header bands clear of all shafts. Short middle conditioning strip. Shared decoder one spanning column, denoising two columns. Reserve a clean 150×150 white photo slot inside input image frame at [75,195,150,150], below RGB Image x and above the short NASA / Apollo 17 credit. The actual selected Earth photo is pasted after generation; DO NOT draw anything in that one slot, not even placeholder words. Upper/lower output images are schematic Earth disks, explicitly labelled Schematic, not real model results. No other empty inset. Local model geometry remains native; every source-border to target arrow is continuous and aligned.
Imagine the whole structural overview as one clean, complete rectangular silhouette before details. Choose an explicit organizing rule: equal-width stage columns, equal-height parallel bands, or a balanced bilateral arrangement, according to the scientific graph. State which rule is used. Equalize peer regions, margins and gutters; innovation may span integer cells without protruding. Visual balance never invents a second branch, reverses an edge, or turns unrelated edges into a bus. Fix the canvas and row/column grid first; reserve the final-output cell before drawing. Align sibling block edges/baselines; innovation panels may span cells. Keep every planned block and the final output inside that same footprint. If crowded, simplify or reflow upstream content rather than extending a dangling last block. Keep flow simple; no added step numbers.
Canvas pixels: [1700, 1150]; preserve the exact boxes and path points below. Scale the entire composition uniformly.
Grid rows: [[150, 390], [500, 660], [770, 1010]]; columns: [[50, 250], [330, 530], [610, 810], [890, 1090], [1170, 1370], [1450, 1650]]
Clearance: 8 pixels. Captions must stay in their reserved boxes; never cut shafts.
## Connector construction (Creative Director and generator)
Plan module placement and connector clearance together, before locking the composition. Prefer straight source-to-target arrows. Reposition nearby modules to eliminate crossings and unnecessary bends rather than drawing a detour around a poor layout. Use only a few consistent right-angle bends; geometry-locked routes follow their exact path points. Every arrow is one continuous, human-reproducible path from the actual source border to the target arrowhead: no disappearing shafts, isolated arrowheads, empty-space starts or unexplained gaps. Keep labels beside the shaft, never erase the shaft to fit text. Avoid intersections; if a crossing is scientifically unavoidable, use a clear continuous bridge and distinguish it from a junction. Align source and target ports on one shared horizontal or vertical axis wherever possible. Use a single consistent arrowhead size and stroke weight; local microview arrows follow the same grammar. Mainline arrows should read immediately; return loops use a separate perimeter lane. When a frame contains different processes, a loop lands in its actual process subregion, never in a nearby training/evaluation inset merely because it shares the outer frame. Reserve section-heading bands separately from connector corridors. Background fills and title bands never erase shafts. After placing labels and icons, trace each complete shaft again; revise crowded placement instead of extending routes.
Draw every named component once. A container may be the component itself; do not add duplicate stand-ins. Repeated snapshots inside a component are insets, not extra pipeline nodes.
## Exact components and placement
- image = `RGB Image x` | box [50, 150, 200, 240] | Framed RGB source image with actual collected NASA Earth photo inserted later; leave a clean square slot, no generated photo imitation.
- encoder = `Encoder E` | box [330, 150, 200, 240] | Simple tapering block, whole model.
- latent = `Spatial Latent z` | box [610, 150, 200, 240] | Stack of three small aligned two-dimensional grid planes.
- reconstruct = `Reconstruction x̃` | box [1450, 150, 200, 240] | Framed original flat schematic Earth-disk miniature; short visible Schematic caption; not an empirical model output.
- noise = `Latent Noise zₜ` | box [50, 770, 200, 240] | Square fine noise grid, visibly smaller spatial representation than RGB thumbnail.
- condition = `Condition y` | box [610, 500, 200, 160] | Short text token strip, e.g. a mountain lake.
- condencoder = `Condition Encoder τθ` | box [890, 500, 200, 160] | Small whole-model rectangle, trainable with denoiser.
- denoise = `Latent Denoising` | box [330, 770, 480, 240] | Large bounded U-Net glyph with down/up levels and a cross-attention inset, no layer inventory.
- sample = `Sample z₀` | box [890, 770, 200, 240] | Small spatial grid with emerging Earth structure.
- decoder = `Decoder D` | box [1170, 150, 200, 860] | Whole decoder block shared by reconstruction and generation.
- output = `Generated Image x̂` | box [1450, 770, 200, 240] | Framed original flat schematic Earth-disk miniature; short visible Schematic caption; not an empirical model output.
## Exact directed connections (one arrowhead per relationship)
These relationship labels specify meaning. Show only short relation captions where needed; not every arrow needs visible explanatory text. Preserve essential scientific notation and conditions.
- image.east -> encoder.west | `encode` | mainline points [[250, 270], [330, 270]]
- encoder.east -> latent.west | `z = E(x)` | mainline points [[530, 270], [610, 270]]
- latent.east -> decoder.west | `reconstruct` | mainline points [[810, 270], [1170, 270]]
- decoder.east -> reconstruct.west | `x̃ = D(z)` | mainline points [[1370, 270], [1450, 270]]
- latent.south -> noise.north | `add noise · training` | reference points [[710, 390], [710, 445], [150, 445], [150, 770]]
- noise.east -> denoise.west | `zₜ, t` | mainline points [[250, 890], [330, 890]]
- condition.east -> condencoder.west | `encode condition` | mainline points [[810, 580], [890, 580]]
- condencoder.south -> denoise.north | `K, V` | branch points [[990, 660], [990, 715], [700, 715], [700, 770]]
- denoise.east -> sample.west | `iterative denoising` | mainline points [[810, 890], [890, 890]]
- sample.east -> decoder.west | `single decode` | mainline points [[1090, 890], [1170, 890]]
- decoder.east -> output.west | `x̂ = D(z₀)` | mainline points [[1370, 890], [1450, 890]]
Ports name the actual object/frame boundary. Never stop at an empty margin, nearby input, or unrelated enclosing stage. Independent evidence edges have distinct landing ports and arrowheads; crossings are not junctions. Do not merge unrelated evidence into one long bus.
## One-to-one drawing correspondence
| Need / location | Reference construction or source basis | Our adapted drawing |
| --- | --- | --- |
| v-images / image | NASA AS17-148-22727 source photo; PD-NASA file-specific notice checked. | Direct crop of collected NASA Earth raster, not borrowed style: leave the declared 150×150 input slot clean for deterministic paste; short dark NASA / Apollo 17 credit below it. |
| v-spatial / latent | Peer spatial-state images plus inspected reference002 stacked feature planes. | Draw compact stack of square grid planes; same footprint for noisy and generated latent. |
| v-direction / denoise | Peer directed chain and conditioning branch; reference005 input-port construction, redrawn with our cross-attention semantics. | Coarse U silhouette with simple spatial feature layers; inset cross-attention shows Q from feature path and K,V entering from condition above. |
For every visual need, choose direct use of a suitable collected asset, a source crop, or borrowed construction. Do not treat all existing imagery as style evidence: when a real visual instance communicates the content best, reserve an aligned inset for the actual file instead of inventing a drawn substitute. Only explicitly collected and approved direct-content insets get reserved slots; invent no blank panels when none are selected. Those insets are composited after generation; leave only those declared slots clean and preserve their aspect ratios. This choice is open-ended across domains, not limited to any media category. Source material used illustratively must not masquerade as this method’s measured result.
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
- Equal-width columns and matched-height scientific lanes form a complete rectangle. Center both phase headings, with explicit separate heading bands and connector corridors. Source photo stays actual: reserve only the one declared input square as clean white, paste the collected NASA crop later without redrawing. Keep small dark NASA / Apollo 17 source credit outside that square. Reconstructed and generated images are native schematic Earth disks labelled Schematic. Blue scientific architecture with red cross-attention focus, unchanged palette. All macro arrows follow exact preflight points and all labels remain beside shafts.
Creative Director ideas:
- `direct-input` -> `image`: Use an actual informative RGB instance instead of an invented input picture. Intent: Separate actual source data from schematic model explanations without changing the scientific method. Construction: One source thumbnail frame at the same aligned left boundary as the lower noise frame. Leave the planned square area blank white and do not draw Earth, noise, any marker, text or any symbol inside it. The real NASA crop is composited after this single generation pass. Put concise attribution outside the slot and keep the input arrow at the frame east border.
- `aligned-latent-mechanism` -> `denoise`: Keep the meaningful spatial-latent and conditioning miniatures inside the regular framework. Intent: Expose iterative denoising and Q versus K,V without decorative filler or unrelated structure. Construction: Two-dimensional grids and a readable flat U-Net icon with a single red cross-attention insert. Schematic Earth representations are illustrations, not actual outputs. Keep whole encoder, condition encoder and shared decoder. The training-only noising path stays continuous through the empty left corridor; centered phase headings never hide it.
## Final drawing checks
Precise architecture geometry with white space and dark labels.
Pale blue related regions; red limited to cross-attention emphasis.
Verify every listed arrow endpoint, concise label and semantic inset before finishing. No gray microcopy, pseudo-text, gratuitous gradients, glow, pasted clip-art or decorative badge. Purposeful dividers and hand-drawn semantic icons are allowed. Keep exact repeated geometry regular.
Generate one PNG1. Do not copy planning prose or evidence hashes into the image.