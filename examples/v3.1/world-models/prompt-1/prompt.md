Create one complete scientific figure from this locked generation checklist.
Evidence SHA256: 786acc926540dbf3b982f0d9b085f681db4de454773e0211bf1ad341bfafcd36
## Scientific meaning
Current latent zₜ, action aₜ and recurrent state hₜ condition an LSTM update. Updated hₜ₊₁ supports an MDN Gaussian-mixture distribution for zₜ₊₁ and also passes through separately. Temperature τ controls distribution sampling; sampled next latent and updated state are distinct outputs.
- World Models M component, Ha and Schmidhuber 2018; not a latest model or full V-M-C architecture.
- LSTM updated state supports the MDN head and is also retained as the separate recurrent-state output.
- The mixture head outputs π/μ/σ of the stochastic next-latent distribution; it is not a deterministic future prediction.
- Only the predictive distribution enters the temperature-controlled sampler; hidden state never passes through sampling.
- The dynamics-to-prediction boundary carries a distribution/state tuple, not a new arithmetic merge.
- No sampled-future-latent arrow to Controller C, no done/reward head, and no invented Transformer/diffusion block.
- Mixture curves and vector marks are schematic model representations without measured values.
## Innovation-led detail hierarchy
Peer depth observation: The author SVG exposes repeated recurrent cells, their MDN heads, state links, latent/action conditions and temperature rather than using a model-name card.
- Innovation: Recurrent stochastic latent dynamics predict a Gaussian mixture rather than one deterministic future. | Focus: dynamics, prediction | Finest visible unit: LSTM updated state, MDN weights/means/scales, conditional next-latent law, temperature sampling and independent state output.
Shared non-innovation depth: Current context and terminal outputs are typed latent/action/state objects; the actual novel mechanism is shown at LSTM, MDN mixture and sampling depth.
Keep whole (no invented model internals): context
Allocate detail to the actual contributions; do not expand standard components just because they are familiar. Match supporting regions at the shared level.
## Locked overall framework
Content-sized left input frame and detailed middle/right scientific regions share bottom y=650. Current context enters dynamics on a straight horizontal arrow at y=510. Dynamics sends the grouped distribution/state tuple to prediction on another straight horizontal arrow at y=420. No exterior feedback or staircase. True internal recurrence/density/sampling topology is explicitly drawn inside its parent regions.
Content determines frame sizes; the Director planned frames and routes together. Unequal regions and useful white space are allowed. Keep every local title, symbol, text and picture inside its parent with padding; no filled title strips. Do not force a rectangular silhouette or equal-card template.
Canvas pixels: [2200, 800]; preserve the exact boxes and path points below. Scale the entire composition uniformly.
Grid rows: [[180, 380], [450, 650]]; columns: [[50, 380], [490, 1390], [1500, 2150]]
Clearance: 16 pixels. Captions must stay in their reserved boxes; never cut shafts.
## Connector construction (Creative Director and generator)
Only basic straight lines or one simple smooth curve. No staircase, zigzag, maze, crossings or complicated perimeter pipes. Ordinary frames have at most one input and one output; source-grounded exceptions must be explicit. The Director moved/regrouped boxes before choosing these paths. Bezier points are control handles, never polyline corners. Keep shafts continuous and arrows attached to actual source/target borders. Trace all lines after placing text. A simple curved human return is not an internal neural loop.
Draw every named component once. A container may be the component itself; do not add duplicate stand-ins. Repeated snapshots inside a component are insets, not extra pipeline nodes.
## Exact components and placement
- context = `Current context` | box [50, 450, 330, 200] | Native latent-vector, action and recurrent-state representations, explicitly distinguished as z at t, a at t and h at t. No invented observed pixel sample or toy numeric values.
- dynamics = `MDN-RNN` | box [490, 180, 900, 470] | Show actual LSTM recurrence and mixture-density head at meaningful internal depth. The Director chooses single-cell state loop or a compact truthful shared-weight unrolled motif. Mixture parameters are weights, means and standard deviations, not invented tokens. Preserve updated state as a separate object from predictive distribution. Temperature sampling may be internal for honest single-port grouping.
- prediction = `Next-step prediction` | box [1500, 180, 650, 470] | Show stochastic next latent versus updated recurrent state distinctly. If sampling is here, use a source-grounded internal state passthrough rather than making h flow through the sampler. Temperature controls uncertainty. Gaussian visualization only illustrative. No fictitious quantitative results.
## Exact directed connections (one arrowhead per relationship)
These relationship labels specify meaning. Show only short relation captions where needed; not every arrow needs visible explanatory text. Preserve essential scientific notation and conditions.
- context.east -> dynamics.west | `current latent and action with recurrent state condition latent dynamics` | mainline line points [[380, 510], [490, 510]]
- dynamics.east -> prediction.west | `next latent predictive distribution and updated recurrent state` | mainline line points [[1390, 420], [1500, 420]]
Ports name the actual object/frame boundary. Never stop at an empty margin, nearby input, or unrelated enclosing stage. Independent evidence edges have distinct landing ports and arrowheads; crossings are not junctions. Do not merge unrelated evidence into one long bus.
## One-to-one drawing correspondence
| Need / location | Reference construction or source basis | Our adapted drawing |
| --- | --- | --- |
| One real recurrent update with its density head / dynamics | Author MDN-RNN source SVG and source method text; complete FiLM SVG supplies color relationships only. | Within dynamics [490,180,900,470], place LSTM around [600,450,240,120] and the MDN/Gaussian-mixture head above around [600,240,240,110]. The grouped context enters the LSTM via a short straight extension from the external input landing y=510. Updated hₜ₊₁ leaves LSTM right at y=510 as a straight lower state channel; it also branches upward from the top of LSTM to the MDN bottom on a single vertical source-supported state connector. Label that state branch hₜ₊₁ once. MDN outputs π/μ/σ to the right into a compact mixture-parameter representation, around [930,240,330,150]. Use small smooth Gaussian curves as an abstract distribution glyph, not a measured graph. Below it typeset P(zₜ₊₁ | aₜ, zₜ, hₜ). At the right edge collect the upper distribution channel and lower state channel with a thin tuple brace spanning y=280..550; it is not a processing node. The exterior output leaves the overall region at y=420. Put the recurrence equation low inside the region at y≈610. Local scientific branching is justified by the actual model, while the outer frame still has exactly one input and one output. |
| Temperature sampling with independent state passthrough / prediction | Author MDN-RNN source SVG and source method text; complete FiLM SVG supplies color relationships only. | Within prediction [1500,180,650,470], the tuple entering at y=420 is unpacked by a thin brace, not an arithmetic operator. The upper distribution channel continues directly to a modest Sample unit around [1770,285,150,80], with τ and Temperature above entering it by one short vertical control arrow. A short rightward arrow leaves Sample and lands on zₜ₊₁, with Sampled latent below, near x=2030/y=325. The separate lower channel runs at y≈520 straight to a recurrent-state vector mark hₜ₊₁ near x=2010, with Updated state. No connector from that lower channel may touch the sampler or sampled z. Keep generous white separation between these two scientifically distinct outputs. |
| Explicit latent action and recurrent context / context | Author MDN-RNN source SVG and source method text; complete FiLM SVG supplies color relationships only. | Compact white current-context frame [50,450,330,200]. Under the heading align three short rows: Latent zₜ with a small cool-pale vector glyph, Action aₜ with a compact native action mark, State hₜ with a recurrent-state glyph. No numeric toy vectors or photographs. Treat the one exterior arrow as carrying the typed context tuple, not as a fake plus operation. The vector/state marks are meaningful primitives, not decorative dots. |
For every visual need, choose direct use of a suitable collected asset, a source crop, or borrowed construction. Do not treat all existing imagery as style evidence: when a real visual instance communicates the content best, reserve an aligned inset for the actual file instead of inventing a drawn substitute. Only explicitly collected and approved direct-content insets get reserved slots; invent no blank panels when none are selected. Those insets are composited after generation; leave only those declared slots clean and preserve their aspect ratios. This choice is open-ended across domains, not limited to any media category. Source material used illustratively must not masquerade as this method’s measured result.
For standard models actually named in this Methodology, use a source-checked recognizable architectural silhouette at the scoped detail level. An unchanged model may remain a compact canonical inset; invent no arbitrary replacement geometry and do not expand supporting internals beyond the innovation-led hierarchy. Reuse already inspected construction evidence.
These are intentional visual content, not ornamental stickers. Keep them small, readable and coherent with the main reference. No invented observations, numerical results or unlabelled decorative particles.
## Typography reference
Arial; black scientific headings and labels, real Greek letters and true subscripts. Keep formulas readable and all text within regions. No gray microcopy or automatic colored title strip.
Use short Methodology-derived headings, no workflow aliases or added counters. Dark titles on white, no filled tabs. Align baselines, edges and spacing. No visible underscores, including code/IDs: typeset indices or use approved aliases. Keep raw IDs internal; reflow before shrinking fonts.
## Text and symbol economy
Emphasize framework innovation. Aim ≤100 English words; never pad. Only scientific necessity permits 101–160; maximum 160. Count repeats; hyphenated words count once. Prefer precise 2–3-word object names. Beyond headings, explain each idea once. Delete clear-arrow narration and fine lists covered by a summary. Remove generic ticks/warning/status badges unless scientifically needed. Borrow warranted architectural chains/stacks, not foreign topology or reference verbosity. Render only approved prose/symbol inventories, never instructions; inspect actual pixels.
## SVG-reference creative workflow
Preserve the full Creative Director role: coherent whole-figure style, creative grouping, colour, frames, arrows, meaningful symbols and local constructions. Add evidence and checks; do not reduce this to filling predetermined cards.
The Director owns the final colour decision. Source swatches below are observations, not an upstream colour lock. No palette-library selection for this run.
Dedicated COMPLETE palette SVG: input/palette-reference.svg; source track: feature-wise conditioning for visual reasoning
Observed swatches: [{"role": "cool", "hex": "#C0DFF2", "rgb": [192, 223, 242]}, {"role": "cool-edge", "hex": "#81BEE4", "rgb": [129, 190, 228]}, {"role": "warm", "hex": "#F2CBC2", "rgb": [242, 203, 194]}, {"role": "warm-edge", "hex": "#E49381", "rgb": [228, 147, 129]}, {"role": "neutral", "hex": "#F9F9F9", "rgb": [249, 249, 249]}, {"role": "ink", "hex": "#666666", "rgb": [102, 102, 102]}, {"role": "black", "hex": "#000000", "rgb": [0, 0, 0]}, {"role": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}]
Observed adjacency/separation: [{"roles": ["cool", "cool-edge"], "relation": "adjacent", "observation": "The cool generator fill and deeper blue border touch within one semantic region."}, {"roles": ["warm", "warm-edge"], "relation": "adjacent", "observation": "Warm FiLM layer fill and warmer border form one region."}, {"roles": ["cool", "warm"], "relation": "separate", "observation": "Cool generator and warm modulated network are separated by a generous white corridor, not pressed against each other."}, {"roles": ["warm", "neutral"], "relation": "adjacent", "observation": "Warm active layers sit beside much quieter support layers in the same vertical family."}]
Available source-derived tints/shades/tones: 
Retain mature colour rules: usually 1–2 dominant families; analogous light neighbours; deeper meaningful marks; isolate strong contrasting foci. White and readable black typography dominate. No invented universal contrast threshold.
Leave unnecessary surfaces white. A pale base frame may receive colour; important mechanism content may receive emphasis. Titles are ordinary text, never automatic colour strips. Do not recolour every object.
When user colours change, re-evaluate the whole relationship plan with the Director; do not do independent HEX substitutions.
Main style traits: Complete coherent diagram language with readable dark typography, purposeful internal topology, modest rounded regions, fine attached arrows, sparse scientifically meaningful vector/mixture marks and white corridors.; Author SVG establishes actual recurrent model grammar, not a generic neural-network icon.; Dedicated other-track FiLM SVG supplies colour relationships only; no borrowed FiLM topology.
Avoid: Staircase and maze routing; Multiple ordinary entries/exits; Bright blue outlines around everything; Invented network internals; Decorative symbols; Filled title bands
Resolve content before the Director pass. Director locks colour, then places content-sized base frames and simple routes together, then fills content. Upstream draft geometry is revisable, not a fixed aesthetic.
No staircase or complex detour. Prefer a straight line; a necessary turn/return uses one smooth simple curve. If routing becomes complex, move or regroup frames first. Normally at most one input and one output per frame. Source-grounded multi-port exceptions require an explicit reason and actual internal landing.
Inspect topology beyond arrows: nested/parallel/repeated structures, node degree, merge/split semantics and operators such as addition, multiplication, concatenation or gates. Only include symbols actually supported by this method. Never invent internal modules to resemble a peer.
All text, titles, symbols and images stay inside their parent region with padding. No deep title backgrounds. Keep complete visual-reference language: typography, line character, frames, arrows, density and spacing.
Three design intentions (layout, flow, density): each starts 我想 and has at most 15 Chinese characters, or starts I want and has at most 15 English words. One line each, no commas.
Return a colour decision with chosen palette, rationale, region colours, adjacency review and whitespace plan. Retain the single source SVG and its observed relationships; choose source-derived extensions as needed. Return a topology review explaining supported structures/operators and omissions. These are planning metadata, never figure text.
## Scoped image references (attached in manifest order)
- input/palette-reference-view.png [704x510] | style_anchor -> WHOLE FIGURE | borrow: Complete source SVG rendered locally for model transport. Borrow its coherent colour relationships, white separation, subdued source-derived fills, typography scale and purposeful frame/line treatment ONLY. This is NOT the scientific layout or model architecture to copy. Follow the Director exact new content, grouping, geometry and simple routes. No FiLM labels, network layers or source topology. Colour decisions come from the Director source-derived palette, never a fixed library. Keep all titles on white. | change: all source scientific content
Respect each crop aspect ratio when reading its construction; do not stretch a complete reference onto this new layout. Borrow only the declared grammar, never unrelated source nodes, labels or colours.
## Palette
Creative Director selected this source-derived palette; no fixed library.
Dedicated complete SVG: input/palette-reference.svg
Dominant roles: cool, warm
cool: #C0DFF2
cool-edge: #81BEE4
warm: #F2CBC2
warm-edge: #E49381
neutral: #F9F9F9
ink: #666666
black: #000000
white: #FFFFFF
cool-pale: #EFF7FC
warm-pale: #FCF2F0
cool / cool-edge: adjacent; The cool generator fill and deeper blue border touch within one semantic region.
warm / warm-edge: adjacent; Warm FiLM layer fill and warmer border form one region.
cool / warm: separate; Cool generator and warm modulated network are separated by a generous white corridor, not pressed against each other.
warm / neutral: adjacent; Warm active layers sit beside much quieter support layers in the same vertical family.
Use only selected roles where meaningful; white remains a deliberate surface. Black typography is allowed. Preserve the Director adjacency/separation and whitespace decisions.
## Final creative construction decisions
Creative Director brief:
- Director chooses cool for recurrent state and warm for mixture/sampling, separated by white; all outer frames and headings stay white. Use black Arial, fine dark arrows and modest consistent corners. This is an actual MDN-RNN mechanism: LSTM below MDN as in the author SVG. Updated state branches to the head and also passes directly to the output, distinct from the predicted distribution. A mathematical brace groups distribution/state, never an arithmetic node. Only the distribution enters the τ sampler; the lower hidden-state channel bypasses it. Two straight exterior arrows; no exterior loop, staircase, extra ports, title bands, gradients or decorative scenery. Use small schematic Gaussian curves with π/μ/σ, no empirical axes/values. Follow the exact inner constructions and positions in the drawing-correspondence table. All content inside parent frames with 24px padding. Render only the approved inventories; leave connector corridors blank.
Creative Director ideas:
Director colour rationale: Use the complete FiLM SVG relationship with a fresh scientific role assignment: cool recurrence/state and warm density/sampling. Director-derived white tints reduce covered area. No palette-library choice.
Director adjacency review: Cool fill/border and warm fill/border each form a local family. Keep the two families apart through white corridors; outer frames stay white and text stays black.
Director whitespace plan: Only actual LSTM/state and mixture/sampler marks carry restrained colour. Outer regions, headings, formula surroundings, tuple braces and connector corridors remain white.
context region colours: white, black, ink, cool-pale
dynamics region colours: white, black, ink, cool-pale, cool-edge, warm-pale, warm-edge, warm
prediction region colours: white, black, ink, warm-pale, warm-edge, cool-pale, cool-edge
Topology review: Single-cell recurrent update from current zₜ, aₜ and hₜ produces hₜ₊₁. The MDN head depends on the updated recurrent state and emits Gaussian-mixture weights, means and standard deviations, denoted π/μ/σ, describing P(zₜ₊₁ | aₜ,zₜ,hₜ). Updated state also continues as a separate state output. A semantic distribution/state tuple, not an arithmetic merge, carries both across the single exterior dynamics output. In prediction, only the distribution reaches the τ-controlled sampler; hₜ₊₁ follows the separate lower passthrough. Sampled zₜ₊₁ and updated hₜ₊₁ remain distinct terminal objects. The one-cell recurrence is made explicit by hₜ₊₁ = LSTM(zₜ,aₜ,hₜ), not a false self-loop for a single time step. This reflects the author SVG's recurrent/MDN relationship without needlessly replicating multiple cells. No future sample feeds Controller C; no done/reward/Transformer/diffusion head is present.
Design intent: 我想中间展开真实机制
Design intent: 我想主线直连内部分流
Design intent: 我想状态与采样分层留白
- `conditioned-recurrence` -> `dynamics`: One real recurrent update with its density head Intent: Expose the actual source topology and state semantics rather than reducing the model to a named rectangle. Construction: Follow the exact dynamics construction in the correspondence table: LSTM below MDN; updated-state branch to head plus separate state channel, mixture parameters/distribution above, semantic tuple brace at exit. Preserve all stated positions and index meanings.
- `state-is-not-sample` -> `prediction`: Temperature sampling with independent state passthrough Intent: Prevent the common false topology in which recurrent state passes through the stochastic sampler. Construction: Follow the exact prediction construction: upper distribution → τ sampler → next latent; lower updated-state channel bypasses sampler. Preserve distinct symbols, white separation and stated positions.
- `typed-current-context` -> `context`: Explicit latent action and recurrent context Intent: Show the conditioning objects and time indices faithfully without inventing a pixel-input stage. Construction: Follow the exact context construction: three typed current latent/action/state rows and a single grouped-context exit. No numeric toy values or fake arithmetic.
Approved visible text inventory (only these prose strings may be drawn; repeats are intentional):
["World Models", "MDN-RNN latent dynamics · 2018", "Current context", "Latent", "Action", "State", "MDN-RNN", "LSTM", "Gaussian mixture", "Mixture parameters", "Next-step prediction", "Temperature", "Sample", "Sampled latent", "Updated state"]
Reported English word count: 25
Approved mathematical symbol inventory:
["zₜ", "aₜ", "hₜ", "hₜ₊₁", "π, μ, σ", "P(zₜ₊₁ | aₜ, zₜ, hₜ)", "hₜ₊₁ = LSTM(zₜ, aₜ, hₜ)", "τ", "zₜ₊₁", "hₜ₊₁"]
All remaining construction descriptions and route meanings are instructions, not additional lettering.
## Final drawing checks
No staircase, zigzag, crossing maze or complicated detour. Plan base frames and simple paths together.
Ordinary external regions at most one input and one output; actual internal model ports retain source-supported meanings.
White support surfaces, black readable labels, deliberate source-derived pale fills; no title strips or gradients.
All text and scientific glyphs inside their parent frames. Exact visible inventory only; do not print long route meaning prose.
Leave every external connector corridor blank. Do not print any route-meaning prose; only exact Director visible-text and symbol inventories may appear. No callout frame around connector labels.
Verify every listed arrow endpoint, concise label and semantic inset before finishing. No gray microcopy, pseudo-text, gratuitous gradients, glow, pasted clip-art or decorative badge. Purposeful dividers and hand-drawn semantic icons are allowed. Keep exact repeated geometry regular.
Generate one PNG1. Do not copy planning prose or evidence hashes into the image.