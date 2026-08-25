<div align="center">

# GenLikeScientificSVG

### Evidence-guided scientific figures, refined through an editable-vector diagnosis.

**Domain conventions · human-producible planning · mapped FigureBench crops · one palette lineage · final PNG2**

<!-- FILL IN: approved example figures can be added after the next end-to-end run. -->

[中文说明](./README_ZH.md) · [Workflow](#workflow) · [Reference pack](#bundled-reference-pack) · [Installation](#installation)

</div>

GenLikeScientificSVG turns a scientific Methodology and an optional reference image
into a revised, labelled architecture figure. It uses two image-generation passes
with one mandatory editable-SVG diagnostic between them. The final output is PNG2;
SVG1 is an intermediate diagnostic artifact, not the final deliverable.

## Installation

```bash
npx skills@latest add LawrenceRiver/genlike-scientific-svg-skill
```

Then provide a Methodology and, if useful, one reference image. The reference may
guide structure, layout, emphasis, and visibly human-made treatments, but it is not
a colour source.

## Workflow

```text
Methodology + optional reference
  -> Context 1: domain visual conventions
  -> Context 2: content-to-visual plan
  -> Context 3: mapped FigureBench crops + one palette lineage + taste
  -> Prompt 1 with all mapped crops -> PNG1
  -> direct base-Codex visual transcription -> editable SVG1
  -> temporary PNG1.5 -> diagnosis + approved/replacement crops
  -> Prompt 2 with PNG1 and crops, never PNG1.5
  -> final PNG2 -> stop
```

### Context 1: recurring domain visual language

The model identifies the field and screens figure panels from 3–4 scholarly papers,
preferably accessible arXiv SVG/HTML sources and otherwise credible extractable
figures. It compares actual panels and records only recurring, Methodology-relevant
objects, intermediate representations, relationships, drawing treatments,
grouping, and professional terminology. One-off treatments remain marked as such.

### Context 2: content-to-visual planning

The Methodology, Context 1, and optional reference are compressed into exact blocks,
labels, relationships, reading order, and a visual treatment for every component.
Treatments must be human-producible: basic geometry, a recurring domain convention,
a deliberate manual drawing, a draw.io-like construction, or a scientifically
necessary real photo crop. Any special visual explains why it is needed and how a
human would make it. Decorative generated-looking elements are rejected.

### Context 3: inspected construction evidence and one palette

The model inspects the pixels of at least two distinct bundled FigureBench images,
then continues adaptively until every required geometry, frame, connector, layout
relationship, and special visualization is covered. Useful regions become mapped
crops with a target component, what to borrow, what must change, and why the result
remains human-editable. Complete reference images are not dumped into Prompt 1.

Each run uses exactly one complete group from the local palette library. If that
group lacks a functional colour, only an evidenced tint, shade, tone, analogous
neighbour, compatible neutral, or controlled contrast may extend it. FigureBench,
domain figures, and the user reference never supply active palette colours. Taste
guidance is subordinate to scientific meaning, user constraints, domain evidence,
human editability, and palette lineage.

### PNG1, editable SVG1, and diagnosis

Prompt 1 contains the Methodology, Contexts 1–3, the optional reference, domain
crops, and every mapped FigureBench crop. The first image-generation pass creates
PNG1.

The base Codex multimodal model must then inspect PNG1 itself and directly transcribe
its visible labels, colours, geometry, paths, groups, lines, arrows, placement, and
relationships into editable SVG1 in one pass. This is not a redesign or a local
redraw: HTML, Python, draw.io, tracing utilities, and a single embedded-raster
wrapper are invalid substitutes. If direct editable transcription fails, the Skill
reports that failure instead of fabricating a fallback.

SVG1 is deterministically rendered to PNG1.5 solely for visual diagnosis. Each
planned component receives one verdict: `keep`, `accept_variation`, `patch`,
`reject`, or `replace`. Only qualified SVG regions and targeted replacement regions
become crops for the second prompt. PNG1.5 is never a Prompt 2 attachment.

### Final PNG2

Prompt 2 modifies PNG1 using the diagnosis, approved SVG crops, replacement crops,
and the earlier contexts. The second image-generation pass produces final PNG2 and
the workflow stops; PNG2 is not sent through another SVG loop. The deterministic
helpers validate files and provenance, but do not claim to observe model calls or
guarantee scientific correctness. Authors must verify the result before publication.

## Recorded methodology cases

These examples preserve the original Methodology inputs rather than replacing them
with keyword-only summaries. They are recorded source inputs for the workflow, not
reconstructions of the cited papers' figures. The generated figure remains an
original interpretation and must not copy the source figure. The generated images
are intentionally left as `FILL IN` until a new end-to-end run is approved.

### Latent Diffusion · visual generation

**Source:** Rombach et al., [*High-Resolution Image Synthesis with Latent Diffusion Models*](https://arxiv.org/abs/2112.10752), §3. The following is the recorded Methodology input; the source paper remains authoritative.

<details>
<summary>Methodology input (verbatim)</summary>

> We propose to circumvent this drawback by introducing an explicit separation of the compressive from the generative learning phase. To achieve this, we utilize an autoencoding model which learns a space that is perceptually equivalent to the image space, but offers significantly reduced computational complexity. By leaving the high-dimensional image space, we obtain DMs which are computationally much more efficient because sampling is performed on a low-dimensional space. We exploit the inductive bias of DMs inherited from their UNet architecture, which makes them particularly effective for data with spatial structure.
>
> Given an image x in RGB space, the encoder E encodes x into a latent representation z = E(x), and the decoder D reconstructs the image from the latent, giving x-tilde = D(z) = D(E(x)). Our subsequent DM is designed to work with the two-dimensional structure of our learned latent space z = E(x). The neural backbone of our model is realized as a time-conditional UNet. Samples from p(z) can be decoded to image space with a single pass through D. We turn DMs into more flexible conditional image generators by augmenting their underlying UNet backbone with the cross-attention mechanism.

</details>

**Labels derived from the original Methodology:** `Image x`, `Encoder E`, `Latent z`, `Denoising U-Net`, `Cross-Attention`, `Condition y`, `Decoder D`, and `Generated image`.

### MusiCoT · music generation

**Source:** [*MusiCoT: Analyzable Chain-of-Musical-Thought Prompting*](https://arxiv.org/abs/2503.19611), §4.1–§4.3. The following is the recorded Methodology input; the source paper remains authoritative.

<details>
<summary>Methodology input (verbatim)</summary>

> This paper proposes a novel approach to representing intermediate musical thoughts using the contrastively trained cross-domain embedding model, known as the CLAP model, rather than relying on natural language descriptions. Specifically, the CLAP model encodes segments of music audio into continuous-valued embeddings every 10 seconds. For a typical 3-minute song, this results in a sequence of audio embeddings. Each embedding, corresponding to a 10-second clip, is analyzable that allows for cosine similarity calculations against any relevant text.
>
> To tackle this issue, we introduce a residual vector quantization (RVQ) based coarse-to-fine tokenization method. This RVQ model consists of L codebooks. In MusiCoT, we arrange the RVQ tokens in a flattened coarse-to-fine sequence for LM prediction, ensuring that coarser tokens are predicted before finer ones. During training, the semantic LM utilizes the flattened CLAP RVQ tokens as additional prediction targets. We integrate tokens from three domains: text tokens, flattened CLAP RVQ tokens, and audio tokens, into a single LM. We introduce a dual-temperature sampling method and a dual-scale CFG sampling strategy for MusiCoT.

</details>

**Labels derived from the original Methodology:** `Text prompt`, `Audio clips`, `CLAP embeddings`, `RVQ codebooks`, `Coarse-to-fine thought tokens`, `Semantic LM`, `Audio tokens`, and `Music sample`.

### AlphaFold 3 · biomolecular structure

**Source:** Abramson et al., [*Accurate structure prediction of biomolecular interactions with AlphaFold 3*](https://www.nature.com/articles/s41586-024-07487-w), “Network architecture and training.” The following is the recorded Methodology input; the source article remains authoritative.

<details>
<summary>Methodology input (verbatim)</summary>

> The overall structure of AF3 echoes that of AlphaFold 2 with a large trunk evolving a pairwise representation of the chemical complex followed by a Structure Module that uses the pairwise representation to generate explicit atomic positions, but there are large differences in each major component. Within the trunk, MSA processing is substantially de-emphasized with a much smaller and simpler MSA embedding block. The “Pairformer” replaces the “Evoformer” of AlphaFold 2 as the dominant processing block. It operates only on the pair representation and the single representation; the MSA representation is not retained and all information passes via the pair representation.
>
> The resulting pair and single representation together with the input representation are passed to the new Diffusion Module that replaces Structure Module of AlphaFold 2. The Diffusion Module operates directly on raw atom coordinates, and on a coarse abstract token representation. The diffusion model is trained to receive “noised” atomic coordinates then predict the true coordinates. At inference time, random noise is sampled and then recurrently denoised to produce a final structure.

</details>

**Labels derived from the original Methodology:** `Chemical complex`, `MSA embedding`, `Pair representation`, `Single representation`, `Pairformer`, `Noised atom coordinates`, `Diffusion Module`, and `Final structure`.

## Bundled reference pack

The installed Skill includes exactly 30 complete, indexed, attributed FigureBench
development images. They are a compact construction library for geometry, layout,
spacing, connectors, and human-edited finish. Ordinary users do not download
FigureBench: the larger dataset is only a maintainer input when curating a future
revision of the bundled pack. The Skill never uses official FigureBench test images.

## Maintainers

Use `scripts/curate_figurebench_reference_pack.py` only for pack curation. Runtime
artifact validation and crop execution are exposed through
`scripts/figure_workflow.py`; installation integrity can be checked with:

```bash
python scripts/check_installation.py
```

Attributions and source metadata for all 30 bundled images are in
[`assets/figurebench-references/index.json`](assets/figurebench-references/index.json).
