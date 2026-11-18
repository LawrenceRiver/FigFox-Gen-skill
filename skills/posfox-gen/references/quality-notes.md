# Cached poster-quality notes

This is a reusable planning checklist, not a live evaluator or a request to research these systems each run. User requirements and the actual paper take precedence over a generic layout.

| Concern | Practical planning question |
|---|---|
| Faithfulness | Are numbers, entities, method relations and qualifiers supported by the paper? |
| Coverage | Can a reader recover the problem, method, contribution, evidence and scope? |
| Density | Is there substantive explanation without empty panels or unreadable small text? |
| Visual evidence | Are the important source figures complete, readable and explained nearby? |
| Layout | Is the reading order coherent, with aligned groups and no clipping/overlap? |
| Readability | Are type hierarchy, source labels and line lengths usable at the chosen scale? |
| Aesthetics | Are typography, restrained colour roles and background treatment consistent? |

The AutoDesign fixed PosterBench rubric assigns these dimensions weights 10/10/15/10/20/25/10. Its aggregation applies severe-failure ceilings; this Skill does not execute that benchmark. There is no universal word-count, OCR-area or source-image-area requirement. Choose content/area budgets from the paper and supplied reference. Native text-box area is not OCR glyph coverage, and high-resolution extraction alone does not fix undersized displayed labels.

Primary references retained for traceability, not mandatory runtime downloads:

- [AutoDesign fixed poster rubric](https://github.com/Yaxin9Luo/AutoDesign/blob/bd635851ef8a2ae257e2bf4c8cd4e984ea3fff1e/autodesign/evaluator/poster_rubric.py) and [aggregation](https://github.com/Yaxin9Luo/AutoDesign/blob/bd635851ef8a2ae257e2bf4c8cd4e984ea3fff1e/autodesign/evaluator/quality_rubric.py).
- [Paper2Poster layout judge](https://github.com/Paper2Poster/Paper2Poster/blob/70fc6f7b778bc8c9bfecc22875eff66f4eb65f93/utils/prompt_templates/aesthetic_layout_judge.yaml): alignment, spacing and reading flow.
- [PosterGen spatial planner](https://github.com/Y-Research-SBU/PosterGen/blob/8a54325f871ee10fa6545de3b3a9b771aa12620c/config/prompts/spatial_content_planner.txt): content and visual hierarchy planned before generation.
- [FigFox-Gen-skill](https://github.com/LawrenceRiver/FigFox-Gen-skill): a related generation-first Skill and the repository-packaging reference. Its figure-specific palette/context machinery is not inherited here.

Do not copy upstream API runners, fixed layouts or evaluation scores into a claim that this generation-only Skill has run them.
