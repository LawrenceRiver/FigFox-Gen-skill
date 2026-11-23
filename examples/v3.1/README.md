# V3 · SVG-reference examples

Current workflow demonstrations generated on 2026-11-23. Each case retains its **complete updated Methodology**, source SVGs and provenance, Director decisions, geometry, exact image prompt, generated PNG and known limitations. These are independent visualizations of the cited projects, not performance evaluations or claims of ownership of the underlying models.

| Example | Methodology | Image | Known deviations |
|---|---|---|---|
| [Qwen-Music](qwen-music/README.md) | [Full text](qwen-music/input/methodology.md) | [PNG](qwen-music/png1.png) | External connector prose; incomplete melody-to-semantic continuation |
| [AlphaGenome](alphagenome/README.md) | [Full text](alphagenome/input/methodology.md) | [PNG](alphagenome/png1.png) | Some external connector labels |
| [World Models · MDN-RNN](world-models/README.md) | [Full text](world-models/input/methodology.md) | [PNG](world-models/png1.png) | Mild shading/gradients |
| [Our V3 architecture](architecture/README.md) | [Full text](architecture/input/methodology.md) | [PNG](architecture/png1.png) | Mild shading; repeated compiler label |

All four run packages pass `python scripts/figure_workflow.py validate-run --run examples/v3.1/NAME`. This verifies stored artifacts and sources, not perfect rendered topology or visual quality. The packages preserve the original generations and disclose inspection results.

Earlier [preview examples](../v3-0-1/README.md) and the [V2 overview](../v2-architecture/README.md) remain historical evidence.
