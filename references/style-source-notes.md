# Style source lookup — 2026-11-17

This is a provenance shortlist, not an image pack or a blanket aesthetic endorsement. Actual source pixels were inspected for RNAsmol, UTCS, LENS project asset and NoWait; screenshot-only citations remain unresolved for the two Habitat International figures. All downloaded research files stayed under `/tmp/figfox-style-research`. No external bitmaps were added to the repository.

## Supplied examples

| Example | Result | Reuse status |
|---|---|---|
| RNAsmol | Exact visual match to [publisher Fig.1](https://www.nature.com/articles/s43588-025-00820-x/figures/1): panels a–c, augmentation axes, CNN/graph branches and curved evaluation path. | Publisher rights section states exclusive rights. Link and describe; do not bundle bitmap. |
| Rural platform framework | Screenshot cites [10.1016/j.habitatint.2026.103841](https://doi.org/10.1016/j.habitatint.2026.103841), reported Fig.1. | Source figure and license not independently verified; DOI reader was blocked. |
| PBF compensation framework | Screenshot cites [10.1016/j.habitatint.2026.103813](https://doi.org/10.1016/j.habitatint.2026.103813), reported Fig.1. | Source figure and license not independently verified. |
| Node-Leiden architecture | Exact match: [UTCS, arXiv:2506.02784](https://arxiv.org/abs/2506.02784), Fig.1 on PDF p2. | Explicit CC BY 4.0 on arXiv abstract. Inspected diagram contains graph primitives rather than third-party photos; attribute authors/source/license and modifications. |
| LENS top image | Exact match to official [project image](https://github.com/Lens4MLLMs/LENS/blob/main/assets/figs/Brief_illustrations_of_LENS.png). **It is not paper Fig.1**: both inspected v1 and latest PDF Fig.1 show a tree instead. | v1 arXiv license is nonexclusive distribution, not CC. Project image includes a photo and icons; exact rights unresolved. |
| NoWait | Exact match: [arXiv:2506.08343](https://arxiv.org/abs/2506.08343), Fig.1 on PDF p2. Supplied OpenReview download returned HTML; arXiv PDF supplied the matching figure. | Article explicitly CC BY 4.0, but QA photos/clipart scope unresolved. Do not treat entire bitmap as cleared. |
| DeepSeek handdrawn robot explainer | Source remains unknown. Fareed Khan repositories contain related handdrawn explainers, but the two inspected overview images do **not** match the supplied diagram. | No attribution or reuse claim for the supplied image. |

## Eight additional candidates

The JSON records exact URLs, existing local references, inspection status and rights status. Six existing FigureBench examples were inspected as a contact sheet of complete figures. Their local index says CC BY 4.0, but this pass did not re-audit those original licenses or constituent-photo rights; they are candidates, not newly cleared redistributable assets.

- `reference-001` — **Rapid Model Architecture Adaption for Meta-Learning**: useful three-phase page rhythm, repeated groups and deployment branches. Strong stage reference.
- `reference-006` — **Unsupervised Cross-Task Generalization via Retrieval Augmentation**: distinct chunky module identities; attractive retrieval instruction treatment, though text density needs reduction.
- `reference-007` — **PyramidCLIP**: paired modality columns and central correspondence zone. Strong parallel-architecture reference; photos should be replaced.
- `reference-013` — **Transcormer**: repeated attention lanes with aligned inputs; useful controlled parallelism.
- `reference-017` — **EfficientFormer**: stage sequence with enlarged internal-block callouts; useful overview/detail hierarchy.
- `reference-019` — **Neuro-Symbolic Procedural Planning with Commonsense Prompting**: task, knowledge and plan objects provide a concept-led story.
- [Fareed Khan: DeepSeek-R1-from-scratch](https://github.com/FareedKhan-dev/DeepSeek-R1-from-scratch): README-linked overview inspected. Rough rectangles, hand-lettered transitions and sparse branching; exact image rights unresolved despite repository MIT metadata.
- [Fareed Khan: train-deepseek-r1](https://github.com/FareedKhan-dev/train-deepseek-r1): README-linked training overview inspected. A more horizontal handdrawn stage-to-outcomes alternative; exact image rights unresolved.

## What to borrow

Stage numbering, bounded parallel lanes, repeated modules, overview-to-callout hierarchy, radial task grouping, semantic icons, hand-lettered emphasis and purposeful connector routing are separable design treatments. Redraw new content from simple editable geometry; do not copy logos, photos, decorative illustrations or source-specific text. Treat every unverified source as link-only until its exact image rights are established.

Research used the agent-reach Exa/Jina routing plus GitHub API and direct primary-source PDF/image reads. `agent-reach check-update` could not run because the executable is absent; `mcporter` is installed and Exa searches worked. Search failures were not treated as evidence that a source does not exist.
