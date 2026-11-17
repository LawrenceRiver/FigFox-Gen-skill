# Rectangular-layout comparison trial

Three cases use the recorded Methodology and previously inspected peer evidence. Initial generations are text-only; no style or content image is attached. These runs precede the new optional direct-raster-inset route and must not be described as using it. All three preserve their earlier palette choices.

| Case | Organizing rule | Selected preview | Initial request | Separate correction |
| --- | --- | --- | --- | --- |
| Latent Diffusion | Equal-width columns, matched-height lanes | [PNG](../../assets/generated-figures/regular-layout-trial/latent-diffusion.png) | 39.2 s | 76.3 s: continuous noising shaft and centered phase headings |
| MusiCoT | Complete 3×3 framework | [PNG](../../assets/generated-figures/regular-layout-trial/musicot.png) | 41.4 s | None |
| AlphaFold 3 | Complete 3×3 framework with two spanning modules | [PNG](../../assets/generated-figures/regular-layout-trial/alphafold3.png) | 114.4 s | 35.6 s: inference-loop landing and compartment separation |

Times measure built-in tool requests, including any queuing. Three requests ran together; summing request durations is not end-to-end elapsed time. Retrieval evidence was cached, so this is not a cold-search benchmark. Exact image prompts, source-grounded plans, Director briefs and correction prompts are retained beside this report; tool metadata is in [requests.json](requests.json). The corrections used the corresponding generated figure as an edit target, not a style reference. Original generations remain in the local run archive.

Visual comparison candidates, not publication acceptance: layout and major shafts are clearer, but the model does not reproduce every requested coordinate, equal width or canvas ratio exactly. Small RVQ/mathematical notation still needs author inspection. Geometry preflight validates planning, not the output pixels. No source reference bitmaps are included.

The branch also adds an optional direct-content-asset workflow: [direct visual insets](../../references/direct-visual-insets.md). It chooses from the role of a visual instance rather than a whitelist of media types.
