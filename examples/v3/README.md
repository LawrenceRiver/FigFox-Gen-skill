# V3 selected examples · 2026-11-17

These three selected previews use the recorded Methodology and inspected peer evidence, with original content images placed after generation. Headings use dark bold text without painted title strips. Colour emphasizes scientific regions; connectors follow a coherent heavier arrow family. These remain author-review previews rather than proof of publication readiness or exact pixel reproduction.

| Case | Selected PNG | Content inset | Layout request |
| --- | --- | --- | --- |
| Latent Diffusion | [PNG](../../assets/generated-figures/v3/latent-diffusion.png) | Original NASA Apollo 17 photo crop; outputs marked schematic | 39.1 s |
| MusiCoT | [PNG](../../assets/generated-figures/v3/musicot.png) | Actual piano recording waveform, recoloured indigo/violet with amber RVQ emphasis | 39.6 s + 32.2 s connector correction |
| AlphaFold 3 | [PNG](../../assets/generated-figures/v3/alphafold3.png) | Public-domain myoglobin image as a contextual protein example | 80.7 s |

The first three comparison requests ran concurrently and took 123.5 s of image-tool wall time. The user then requested a separate MusiCoT colour scheme; its original teal preview remains archived locally. The selected recolour initially contained a second, backward arrowhead on the condition edge; one scoped edit removed it. This edit is explicitly recorded and is not described as a one-pass success. Content placement took roughly 0.2–0.4 s per selected case. These durations include tool queuing, exclude cached prior scientific research, and are not cold end-to-end benchmarks.

Each case retains its exact image request, scientific plan, Creative Director brief, final content placement manifest and source/output hash receipt. Full original source assets and intermediate images remain in the local run archive. All three selected cases passed deterministic artifact validation with their current-generation inputs; actual scientific pixels still require author inspection. New colour/source changes did not alter the original scientific edge lists.

## Source roles

- NASA / Apollo 17 crew, [AS17-148-22727 source](https://images.nasa.gov/details/ARC-1972-AS17-148-22727), [specific public-domain notice](https://commons.wikimedia.org/wiki/File:The_Earth_seen_from_Apollo_17.jpg). The collected scan is cropped to remove film/empty borders and is only an illustrative RGB input. Reconstructed/generated views are schematic, not measured LDM results. The conditional example now reads Earth from space. The compact U-shaped drawing grammar was checked against [Ronneberger et al., Fig. 1](https://arxiv.org/pdf/1505.04597); only contraction/expansion/skip-link construction is borrowed, not exact segmentation layers or scientific content.
- Aya Higuchi, Chopin Waltz in A minor B.150, [performance source and CC0 notice](https://commons.wikimedia.org/wiki/File:Chopin_-_Waltz_in_A_minor,_B_150.ogg). Waveform uses actual first-20-second samples; recolouring changes the plot palette, not the signal. Text conditioning and similarity views are illustrative independent branches, not measured examples from this recording.
- AzaToth, [Myoglobin.png and PD-self dedication](https://commons.wikimedia.org/wiki/File:Myoglobin.png), PDB 1MBO. The image is contextual input illustration; it is neither a literal required known structure nor a claimed AF3 prediction. The final atomic drawing is schematic.

Pixel limitations remain: the generator approximates exact box dimensions, some small glyphs/token captions and micro-connectors need specialist inspection, and the U-Net is a compact explanatory silhouette rather than a layer inventory. Generated layouts are not editable SVGs. Earlier trials and historical releases remain available rather than being overwritten.
