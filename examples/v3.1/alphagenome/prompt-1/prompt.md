Create one complete scientific figure from this locked generation checklist.
Evidence SHA256: aa94c041c08cebaf62961deccb2dd7eedce22ea7981e561adeb94424e440d713
## Scientific meaning
DNA and species identity feed the multi-scale U-Net/transformer backbone; 1D embeddings predict genomic tracks while pair embeddings predict contact maps.
- Original AlphaGenome only; 1 Mb one-hot DNA and species identity; no added cell-state conditioning.
- Encoder selected scales 1 bp then 4 bp then omitted levels terminate at a 128-bp Transformer Tower. Decoder mirrors this back to 1 bp; no further pooling below 128 bp.
- Preserve same-scale skips and the separate 128-bp transformer tap into the 1D output embedder.
- Transformer pair embeddings bypass the decoder and predict 2D contacts at 2,048 bp.
- All eleven output types are grouped correctly by 1-bp/128-bp/2,048-bp resolution.
- Splice junction head uses donor–acceptor interactions from 1D features.
- Miniature output profiles and matrices are schematic; no empirical values or results.
## Innovation-led detail hierarchy
Peer depth observation: HyenaDNA expands internal grouping; DNABERT input comparison remains a representation detail. Neither substitutes for the source AlphaGenome model.
- Innovation: Joint long-context and single-base readouts with a separate pair-representation branch | Focus: backbone, tracks, contacts | Finest visible unit: Scale-correct U path, matched skips and distinct 1D/2D branch landings
Shared non-innovation depth: Supporting input and assay heads remain coarse symbolic forms.
Keep whole (no invented model internals): dna
Allocate detail to the actual contributions; do not expand standard components just because they are familiar. Match supporting regions at the shared level.
## Locked overall framework
Compact left input, spacious central multi-scale U, tall genomic readout upper right, compact contact readout lower right. Fine white enclosures and plain serif labels. Title sits within canvas top margin.
Content determines frame sizes; the Director planned frames and routes together. Unequal regions and useful white space are allowed. Keep every local title, symbol, text and picture inside its parent with padding; no filled title strips. Do not force a rectangular silhouette or equal-card template.
Canvas pixels: [2400, 1500]; preserve the exact boxes and path points below. Scale the entire composition uniformly.
Grid rows: [[160, 920], [1040, 1400]]; columns: [[40, 360], [480, 1720], [1840, 2360]]
Clearance: 12 pixels. Captions must stay in their reserved boxes; never cut shafts.
## Connector construction (Creative Director and generator)
Only basic straight lines or one simple smooth curve. No staircase, zigzag, maze, crossings or complicated perimeter pipes. Ordinary frames have at most one input and one output; source-grounded exceptions must be explicit. The Director moved/regrouped boxes before choosing these paths. Bezier points are control handles, never polyline corners. Keep shafts continuous and arrows attached to actual source/target borders. Trace all lines after placing text. A simple curved human return is not an internal neural loop.
Draw every named component once. A container may be the component itself; do not add duplicate stand-ins. Repeated snapshots inside a component are insets, not extra pipeline nodes.
## Exact components and placement
- dna = `DNA Input` | box [40, 160, 320, 760] | Short symbolic DNA nucleotide row and compact one-hot cells with 1 Mb and human/mouse labels. No biological artwork.
- backbone = `Multi-scale Backbone` | box [480, 160, 1240, 1240] | U-shaped convolutional encoder/decoder at selected scales 1 bp and 4 bp, with skipped intermediate scales shown by ellipses. Bottleneck Transformer Tower is 128 bp; do not show any further pooling below 128 bp. Two matched encoder-to-decoder skips. Output embedder receives restored 1-bp decoder features plus a separate 128-bp transformer tap. Pair representation branch from transformer bypasses decoder to 2D contact output.
- tracks = `Genomic Tracks` | box [1840, 160, 520, 760] | All eight 1-bp readout types plus histone modification and TF binding at 128 bp; native schematic aligned profile lines with donor–acceptor splice arcs, no measured data.
- contacts = `DNA Contact Maps` | box [1840, 1040, 520, 360] | Native symmetric contact matrix with diagonal plus a few off-diagonal cells at 2,048 bp; no quantitative claims.
## Exact directed connections (one arrowhead per relationship)
These relationship labels specify meaning. Show only short relation captions where needed; not every arrow needs visible explanatory text. Preserve essential scientific notation and conditions.
- dna.east -> backbone.west | `sequence and species` | mainline line points [[360, 500], [480, 500]]
- backbone.east -> tracks.west | `1D embeddings` | mainline line points [[1720, 500], [1840, 500]]
- backbone.east -> contacts.west | `2D embeddings` | branch line points [[1720, 1150], [1840, 1150]]
Ports name the actual object/frame boundary. Never stop at an empty margin, nearby input, or unrelated enclosing stage. Independent evidence edges have distinct landing ports and arrowheads; crossings are not junctions. Do not merge unrelated evidence into one long bus.
## One-to-one drawing correspondence
| Need / location | Reference construction or source basis | Our adapted drawing |
| --- | --- | --- |
| DNA Input / dna | Own source-checked scientific geometry; SVG input/grouping/style observations recorded in Context1. No foreign topology. | Short symbolic DNA nucleotide row and compact one-hot cells with 1 Mb and human/mouse labels. No biological artwork. |
| Multi-scale Backbone / backbone | Own source-checked scientific geometry; SVG input/grouping/style observations recorded in Context1. No foreign topology. | U-shaped convolutional encoder/decoder at selected scales 1 bp and 4 bp, with skipped intermediate scales shown by ellipses. Bottleneck Transformer Tower is 128 bp; do not show any further pooling below 128 bp. Two matched encoder-to-decoder skips. Output embedder receives restored 1-bp decoder features plus a separate 128-bp transformer tap. Pair representation branch from transformer bypasses decoder to 2D contact output. |
| Genomic Tracks / tracks | Own source-checked scientific geometry; SVG input/grouping/style observations recorded in Context1. No foreign topology. | All eight 1-bp readout types plus histone modification and TF binding at 128 bp; native schematic aligned profile lines with donor–acceptor splice arcs, no measured data. |
| DNA Contact Maps / contacts | Own source-checked scientific geometry; SVG input/grouping/style observations recorded in Context1. No foreign topology. | Native symmetric contact matrix with diagonal plus a few off-diagonal cells at 2,048 bp; no quantitative claims. |
For every visual need, choose direct use of a suitable collected asset, a source crop, or borrowed construction. Do not treat all existing imagery as style evidence: when a real visual instance communicates the content best, reserve an aligned inset for the actual file instead of inventing a drawn substitute. Only explicitly collected and approved direct-content insets get reserved slots; invent no blank panels when none are selected. Those insets are composited after generation; leave only those declared slots clean and preserve their aspect ratios. This choice is open-ended across domains, not limited to any media category. Source material used illustratively must not masquerade as this method’s measured result.
For standard models actually named in this Methodology, use a source-checked recognizable architectural silhouette at the scoped detail level. An unchanged model may remain a compact canonical inset; invent no arbitrary replacement geometry and do not expand supporting internals beyond the innovation-led hierarchy. Reuse already inspected construction evidence.
These are intentional visual content, not ornamental stickers. Keep them small, readable and coherent with the main reference. No invented observations, numerical results or unlabelled decorative particles.
## Typography reference
Readable Times-like serif body 25–28 px; bold serif section headings 36 px; main title 48 px. Black text; no filled headings or tiny gray notes.
Use short Methodology-derived headings, no workflow aliases or added counters. Dark titles on white, no filled tabs. Align baselines, edges and spacing. No visible underscores, including code/IDs: typeset indices or use approved aliases. Keep raw IDs internal; reflow before shrinking fonts.
## Text and symbol economy
Emphasize framework innovation. Aim ≤100 English words; never pad. Only scientific necessity permits 101–160; maximum 160. Count repeats; hyphenated words count once. Prefer precise 2–3-word object names. Beyond headings, explain each idea once. Delete clear-arrow narration and fine lists covered by a summary. Remove generic ticks/warning/status badges unless scientifically needed. Borrow warranted architectural chains/stacks, not foreign topology or reference verbosity. Render only approved prose/symbol inventories, never instructions; inspect actual pixels.
## SVG-reference creative workflow
Preserve the full Creative Director role: coherent whole-figure style, creative grouping, colour, frames, arrows, meaningful symbols and local constructions. Add evidence and checks; do not reduce this to filling predetermined cards.
The Director owns the final colour decision. Source swatches below are observations, not an upstream colour lock. No palette-library selection for this run.
Dedicated COMPLETE palette SVG: input/palette.svg; source track: language-model attention masking
Observed swatches: [{"role": "primary", "hex": "#5B9BD5", "rgb": [91, 155, 213]}, {"role": "surface", "hex": "#E5EBF7", "rgb": [229, 235, 247]}, {"role": "companion", "hex": "#DAE3F3", "rgb": [218, 227, 243]}, {"role": "accent", "hex": "#92D050", "rgb": [146, 208, 80]}, {"role": "ink", "hex": "#000000", "rgb": [0, 0, 0]}, {"role": "neutral", "hex": "#7F7F7F", "rgb": [127, 127, 127]}]
Observed adjacency/separation: [{"roles": ["primary", "surface"], "relation": "adjacent", "observation": "Thin medium-blue rounded outlines directly enclose pale-blue mask cells."}, {"roles": ["surface", "companion"], "relation": "adjacent", "observation": "Two close low-saturation blue cell families occupy neighboring matrix regions without a harsh boundary."}, {"roles": ["primary", "accent"], "relation": "separate", "observation": "Blue bordered cells and the green query-stream label are separated by white margin; green occupies only small text/mark areas."}, {"roles": ["neutral", "surface"], "relation": "adjacent", "observation": "Neutral gray mask cells border pale-blue available cells; pale regions retain dark readable labels."}]
Available source-derived tints/shades/tones: 
Retain mature colour rules: usually 1–2 dominant families; analogous light neighbours; deeper meaningful marks; isolate strong contrasting foci. White and readable black typography dominate. No invented universal contrast threshold.
Leave unnecessary surfaces white. A pale base frame may receive colour; important mechanism content may receive emphasis. Titles are ordinary text, never automatic colour strips. Do not recolour every object.
When user colours change, re-evaluate the whole relationship plan with the Director; do not do independent HEX substitutions.
Main style traits: Complete CosyVoice 2 SVG frame language: fine black outlines, plain serif labels, restrained pale functional marks, broad white separation and sparse arrows; replace speech content with our genomic content; HyenaDNA SVG shows purposeful nested functional enclosures and aligned local modules; preserve only semantic grouping and readable typography hierarchy; Complete Transcormer SVG supplies the observed pale-blue adjacency, thin blue outlines, small separated green focus and large white spaces; source matrix semantics are excluded
Avoid: foreign Hyena gates or additions; DNABERT k-mer/BPE tokenization inside AlphaGenome; copied attention-mask topology; painted title strips; zigzag or staircase routes; duplicated skip labels and excess text
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
surface: #E5EBF7
companion: #DAE3F3
accent: #92D050
ink: #000000
neutral: #7F7F7F
deepblue: #315B80
softgreen: #EDF5E3
primary / surface: adjacent; Thin medium-blue rounded outlines directly enclose pale-blue mask cells.
surface / companion: adjacent; Two close low-saturation blue cell families occupy neighboring matrix regions without a harsh boundary.
primary / accent: separate; Blue bordered cells and the green query-stream label are separated by white margin; green occupies only small text/mark areas.
neutral / surface: adjacent; Neutral gray mask cells border pale-blue available cells; pale regions retain dark readable labels.
Use only selected roles where meaningful; white remains a deliberate surface. Black typography is allowed. Preserve the Director adjacency/separation and whitespace decisions.
## Final creative construction decisions
Creative Director brief:
- Create an airy publication diagram using the source whole-reference language: fine uniform outlined enclosures, plain readable typographic labels, small functional pale shapes, simple continuous arrows, large white space. Use a coherent Times-like serif for body labels inspired by the inspected CosyVoice SVG; use bold serif for headings and mathematical/native symbols consistently. Avoid enormous title branding. Set a compact 1 Mb DNA input left, largest central backbone, and two unequal output frames right. Preserve all source-grounded topology. Blue source cells/shades show representations, tiny near-white green focuses the Transformer Tower; black text and unfilled titles. No gradients or shadows. Native schematic genomic marks only. Correct the earlier ambiguous 128 bp label placement: ONLY mark 128 bp in the bottleneck and output-embedding/readout labels, never halfway down the encoder. Use 4 bp for the selected middle skip scale and ellipses to summarize intermediate scale stages. Within the backbone use two smooth skip curves rather than complex orthogonal pipes. The macro grid/ports in the resulting plan are exact; all local words and marks are contained.
Creative Director ideas:
Director colour rationale: Choose one primary blue family plus a restrained separated green mechanism focus from the complete Transcormer SVG. Deep blue is a shade of its actual outline colour; near-white green is a tint of its query-stream green. White stays dominant. Do not reproduce the source mask matrix layout or grey blocked-cell semantics.
Director adjacency review: Related encoder/decoder cells use neighboring pale source blues with deep blue linework. Strongest local colour is the small green-tinted transformer mechanism at the bottom; white around it separates it from blue feature columns. Same-scale skip shafts stay deep blue; green is not scattered across unrelated readouts. White regions and black text preserve figure hierarchy.
Director whitespace plan: Keep canvas and major frames white. Only feature cells, transformer interior and tiny readout marks receive pale colour. Leave broad clear gutters and the U interior white. Title and section headings never receive a band.
dna region colours: white, primary, ink
backbone region colours: white, surface, companion, deepblue, softgreen, ink
tracks region colours: white, primary, deepblue, ink
contacts region colours: white, surface, primary, deepblue, ink
Topology review: The original AlphaGenome science requires convolutional downsampling to a 128-bp transformer and upsampling to 1 bp with same-scale encoder/decoder skips. A 128-bp transformer tap and the restored 1-bp decoder stream feed output embeddings; pair features from the transformer independently feed contacts at 2,048 bp. Two macro outputs from backbone are therefore a necessary source-supported exception, with distinct internal landings at the 1D output embedder and 2D pair representation. No gate, multiply, arbitrary add or BPE operator from HyenaDNA/DNABERT is inserted. Repeated actual network levels are summarized; 1 bp and 4 bp are selected scale examples with ellipses down to the only 128-bp bottleneck. No pooling below this bottleneck.
Design intent: 我想主干展开而输入收紧
Design intent: 我想两路读出直接落位
Design intent: 我想机制紧凑且底框留白
- `scale-correct-u` -> `backbone`: Make the U-shaped scale transition and the two distinct output representations visible Intent: Prevent an incorrect extra downsampling stage while retaining real skip and pair dependencies Construction: Inside the model frame place encoder left x650–880 and decoder right x1160–1390. Top selected 1-bp features at y410, middle selected 4-bp features at y650. Encoder down arrows descend toward one Transformer Tower centered x1000 y1010 and decoder arrows ascend from it; use ellipses between 4-bp strips and bottleneck to summarize unshown levels. Mark 128 bp only within Transformer Tower. Two smooth single-curve skip arrows connect corresponding encoder/decoder feature strips; label Same-scale skips once inside their whitespace. Place Output embeddings as small right-side region x1450–1660 y400–630, receiving decoder-top 1-bp features by one straight arrow and the 128-bp tower tap by one unobstructed smooth curve in the empty right inner corridor. Output embeddings connects directly to the upper-right genomic frame at y500. Pair embeddings as a compact blue matrix at x1450–1660 y1080–1240 receives its own simple curve from transformer and connects directly to lower-right contacts at y1150. Keep the pair path below the decoder. No overlapping pipes, no shared arrowhead, no staircase.
- `scientific-readouts` -> `tracks`: Group all assay types by resolution and keep contacts separate Intent: Explain the biological readout families without presenting invented measurements Construction: In the tall upper-right region, align 1-bp headings, three short grouped modality lines and small schematic profiles; donor–acceptor arcs distinguish splicing. A simple divider separates 128-bp histone/TF readouts. Lower contact region contains a symmetric schematic diagonal matrix and 2,048-bp label. Curves and grids are symbolic without numerical axes or empirical scores. Schematic readouts appears once in ordinary dark italic text inside the lower contact frame.
Approved visible text inventory (only these prose strings may be drawn; repeats are intentional):
["AlphaGenome", "DNA sequence to molecular readouts", "DNA Input", "1 Mb", "A C G T", "One-hot encoding", "Human / mouse", "Multi-scale Backbone", "Encoder", "Conv + pooling", "1 bp", "4 bp", "Decoder", "Conv + upsampling", "1 bp", "4 bp", "Same-scale skips", "Transformer Tower", "128 bp", "Long-range interactions", "Output embeddings", "1 bp + 128 bp", "Pair embeddings", "2,048 bp", "Genomic Tracks", "1 bp", "RNA-seq · CAGE · PRO-cap", "DNase · ATAC", "Splice sites · Usage · Junctions", "Donor–acceptor pairs", "128 bp", "Histone modifications", "TF binding", "DNA Contact Maps", "2,048 bp", "Pairwise interactions", "Schematic readouts"]
Reported English word count: 85
Approved mathematical symbol inventory:
["…", "0", "1"]
All remaining construction descriptions and route meanings are instructions, not additional lettering.
## Final drawing checks
Mostly white; pale blue only in meaningful local modules; restrained green at matched skip emphasis; dark/black readable typography.
No invented quantitative results or benchmark plots. No gradients, shadows, decorated cards or title ribbons.
Every title, word and symbol stays inside its actual parent region. Only continuous real inter-region connections leave frames.
Verify every listed arrow endpoint, concise label and semantic inset before finishing. No gray microcopy, pseudo-text, gratuitous gradients, glow, pasted clip-art or decorative badge. Purposeful dividers and hand-drawn semantic icons are allowed. Keep exact repeated geometry regular.
Generate one PNG1. Do not copy planning prose or evidence hashes into the image.