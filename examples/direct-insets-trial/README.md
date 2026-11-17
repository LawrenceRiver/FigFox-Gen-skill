# Direct-content inset trial · 2026-11-17

Three fresh layout generations, no style-reference image attachments, followed by deterministic placement of one actual collected content asset per figure. No image-edit calls. Source assets and generated layouts remain in the local trial archive; exact prompts, plans, placement manifests and receipts are saved here. The final PNGs contain the selected original content, with only documented cropping/aspect-preserving resizing.

| Case | Preview | Direct content | Generation request |
| --- | --- | --- | --- |
| LDM | [PNG](../../assets/generated-figures/direct-insets-trial/latent-diffusion.png) | NASA Apollo 17 source photo crop | 35.9 s |
| MusiCoT | [PNG](../../assets/generated-figures/direct-insets-trial/musicot.png) | Waveform derived from the first 20 s of actual CC0 piano-performance samples | 42.2 s |
| AlphaFold 3 | [PNG](../../assets/generated-figures/direct-insets-trial/alphafold3.png) | Existing public-domain myoglobin raster, PDB 1MBO, as contextual protein example | 83.5 s |

Requests for MusiCoT and AF3 ran concurrently. Request durations include queuing and are not an end-to-end benchmark. Scientific peer evidence was reused from the prior inspected cases; only named content assets were newly retrieved. Compositing replay took about 0.25 s for MusiCoT and AF3. Original source/receipt hashes and actual pixel boxes are in each case folder. Moving retained layout artifacts under input/ keeps the run root restricted to final PNG1; decoded final pixels were verified unchanged.

## Asset sources and roles

- **LDM**: NASA / Apollo 17 crew, AS17-148-22727. [NASA source](https://images.nasa.gov/details/ARC-1972-AS17-148-22727), [file-specific PD-NASA notice](https://commons.wikimedia.org/wiki/File:The_Earth_seen_from_Apollo_17.jpg), [NASA media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/). Crop removes scan borders and empty background; no generative alteration/recolouring. Actual downloaded scan is the NASA ARC asset, not the processed Commons JPEG. Only the RGB input is photographic; output views are labelled schematic.
- **MusiCoT**: Chopin, Waltz in A minor B.150, performed by Aya Higuchi (2014). The [file page](https://commons.wikimedia.org/wiki/File:Chopin_-_Waltz_in_A_minor,_B_150.ogg) explicitly dedicates the performance under CC0 1.0. The waveform uses actual sample extrema, not invented audio graphics. It is an input example, not a generated MusiCoT result.
- **AF3**: AzaToth, [Myoglobin.png](https://commons.wikimedia.org/wiki/File:Myoglobin.png), PD-self worldwide dedication. The protein image is contextual input illustration, not a literal required structure input or a claimed AF3 prediction. Final atomic structure remains schematic.

## Inspection and limitations

The direct-content placement succeeded in all three: actual assets occupy the inspected slots, preserve aspect and do not cover adjacent labels/arrows. Geometry preflight passed, and content hashes/placement receipts are retained. These remain previews rather than publication acceptance.

- **LDM**: the generated K,V branch still has a gap through the denoiser heading. The condition text still says a mountain lake while schematic outputs show Earth, so it is not a matched conditional example. Its full artifact check passes; these pixel/semantic presentation faults prevent acceptance.
- **MusiCoT**: actual piano waveform is embedded, but the separate text-conditioning example and schematic similarity panels refer to piano and drums; they are illustrative independent branches, not measured similarity results. Full artifact check passes.
- **AF3**: the new input-asset note in Context3 coverage does not match the preserved canonical FigureBench request. Full run validation therefore reports a coverage-record inconsistency. Actual request and Context3 are preserved unchanged rather than rewriting history to claim a pass. Geometry and raster composition checks pass; full-run acceptance remains pending this provenance correction.

No automatic pixel repair or hidden rerun was used to turn these issues into a success claim.
