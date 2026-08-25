# Canonical artifact schemas

These are complete valid examples for model-authored JSON and for both preserved
crop-request/materialized-manifest pairs. Paths are run-relative. Keep
`request.json` coordinates separate from deterministic `manifest.json` output.

## Context 1 — `context/context-1-domain-conventions.json`

```json
{
  "domain": "music generation",
  "mainline": "text prompt to diffusion piano roll to generated audio",
  "conventions": [
    {
      "concept": "piano-roll intermediate",
      "recurrence_evidence": "A time-pitch grid appears in three retained scholarly method figures.",
      "visual_treatment": "rectangular grid with horizontal note bars and labelled time and pitch axes",
      "terminology": "piano roll",
      "methodology_relevance": "shows the structured representation predicted before audio decoding",
      "eligible_source_crops": [
        {
          "path": "references/web/crops/piano-roll-panel.png",
          "target_component_id": "piano_roll",
          "borrow": ["time-pitch grid grammar", "horizontal note-bar treatment"],
          "must_change": ["source note pattern", "source labels", "source layout"]
        }
      ]
    }
  ]
}
```
## Scholarly web manifest — `references/web/manifest.json`

Retain cropped visual evidence from three or four distinct scholarly papers. More
than one crop may come from the same paper, but `source_url` must identify exactly
three or four distinct HTTPS paper pages. Every mapped Context 1 domain crop must
be declared here, and every crop path must be a real run-local file under
`references/web/crops/` (not the later `replacements/` area).

```json
{
  "format": "scholarly-domain-figure-manifest-v1",
  "sources": [
    {
      "id": "paper-1-piano-roll",
      "title": "Paper title",
      "figure": "Figure 2",
      "source_url": "https://arxiv.org/html/2402.14285",
      "evidence_url": "https://arxiv.org/html/2402.14285v4/VAE_new.png",
      "crop_path": "references/web/crops/piano-roll-panel.png",
      "inspection": "Visible time-pitch grid, sparse note bars, encoder, and latent tiles."
    }
  ]
}
```

`id` and `crop_path` values are unique. Both URLs must use HTTPS. `inspection`
records visible pixel evidence rather than a title/abstract inference.

## Context 2 — `context/context-2-content-visual-plan.json`

```json
{
  "mainline": "prompt to encoded conditioning to diffusion piano roll to audio",
  "components": [
    {
      "id": "prompt",
      "label": "Text Prompt",
      "semantic_role": "input",
      "visual_treatment": "plain labelled rectangle",
      "construction_provenance": "basic editable geometry",
      "special": "no",
      "source_context": "methodology"
    },
    {
      "id": "encoder",
      "label": "Prompt Encoder",
      "semantic_role": "transformation",
      "visual_treatment": "rounded process container",
      "construction_provenance": "basic editable geometry",
      "special": "no",
      "source_context": "methodology"
    },
    {
      "id": "diffusion",
      "label": "Diffusion Model",
      "semantic_role": "structured prediction",
      "visual_treatment": "nested enclosure containing a restrained noisy-to-structured sequence",
      "construction_provenance": "recurring domain convention rendered as draw.io-like geometry",
      "special": "yes: a human would construct three small grids with progressively ordered cells",
      "source_context": "context-1-domain-conventions.json"
    },
    {
      "id": "piano_roll",
      "label": "Structured Piano Roll",
      "semantic_role": "intermediate representation",
      "visual_treatment": "time-pitch grid with horizontal note bars",
      "construction_provenance": "recurring domain-paper construction",
      "special": "no",
      "source_context": "context-1-domain-conventions.json"
    },
    {
      "id": "audio",
      "label": "Generated Audio",
      "semantic_role": "output",
      "visual_treatment": "simple editable waveform path inside a labelled frame",
      "construction_provenance": "human-editable path geometry",
      "special": "no",
      "source_context": "methodology"
    }
  ],
  "relationships": [
    {"source_id": "prompt", "target_id": "encoder", "label": "encodes"},
    {"source_id": "encoder", "target_id": "diffusion", "label": "conditions"},
    {"source_id": "diffusion", "target_id": "piano_roll", "label": "predicts"},
    {"source_id": "piano_roll", "target_id": "audio", "label": "decodes to"}
  ]
}
```

## FigureBench crop request — `references/figurebench/crops/request.json`

`bounds` is normalized `[left, top, right, bottom]`.

```json
{
  "crops": [
    {
      "id": "frame-style",
      "reference_id": "reference-001",
      "bounds": [0.05, 0.08, 0.48, 0.44],
      "target_component_id": "encoder",
      "crop_contract": {
        "borrow": ["corner radius", "stroke weight", "inner padding"],
        "must_change": ["source label", "source proportions", "source arrangement"],
        "human_editable_reason": "the frame is flat rectangle and stroke geometry"
      }
    },
    {
      "id": "process-sequence",
      "reference_id": "reference-002",
      "bounds": [0.24, 0.18, 0.86, 0.72],
      "target_component_id": "diffusion",
      "crop_contract": {
        "borrow": ["nested grouping", "connector rhythm", "small-multiple spacing"],
        "must_change": ["scientific content", "number of internal states", "all source colours"],
        "human_editable_reason": "the construction uses grouped boxes, paths, and arrows"
      }
    }
  ],
  "basic_geometry": [
    {
      "component_id": "prompt",
      "primitive": "rectangle with centred text",
      "construction_steps": ["draw one rectangle", "apply one flat fill and outline", "centre the exact label"],
      "human_editable_reason": "every part is a basic editable primitive"
    },
    {
      "component_id": "piano_roll",
      "primitive": "rectangular grid with horizontal note bars",
      "construction_steps": ["draw evenly spaced grid lines", "add horizontal note rectangles", "label time and pitch axes"],
      "human_editable_reason": "the grid, bars, and labels are basic editable primitives"
    },
    {
      "component_id": "audio",
      "primitive": "framed waveform polyline",
      "construction_steps": ["draw one rectangular frame", "draw one centred polyline", "place the exact output label"],
      "human_editable_reason": "the frame, polyline, and text remain independently editable"
    }
  ]
}
```

## Materialized FigureBench manifest — `references/figurebench/crops/manifest.json`

```json
{
  "format": "figurebench-materialized-crops-v1",
  "request": "references/figurebench/crops/request.json",
  "crops": [
    {
      "id": "frame-style",
      "reference_id": "reference-001",
      "bounds": [0.05, 0.08, 0.48, 0.44],
      "target_component_id": "encoder",
      "crop_contract": {
        "borrow": ["corner radius", "stroke weight", "inner padding"],
        "must_change": ["source label", "source proportions", "source arrangement"],
        "human_editable_reason": "the frame is flat rectangle and stroke geometry"
      },
      "crop_id": "frame-style",
      "crop_path": "references/figurebench/crops/frame-style.png"
    },
    {
      "id": "process-sequence",
      "reference_id": "reference-002",
      "bounds": [0.24, 0.18, 0.86, 0.72],
      "target_component_id": "diffusion",
      "crop_contract": {
        "borrow": ["nested grouping", "connector rhythm", "small-multiple spacing"],
        "must_change": ["scientific content", "number of internal states", "all source colours"],
        "human_editable_reason": "the construction uses grouped boxes, paths, and arrows"
      },
      "crop_id": "process-sequence",
      "crop_path": "references/figurebench/crops/process-sequence.png"
    }
  ]
}
```

## Context 3 — `context/context-3-visual-kit.json`

```json
{
  "selected_references": [
    {
      "crop_id": "frame-style",
      "reference_id": "reference-001",
      "crop_path": "references/figurebench/crops/frame-style.png",
      "target_component_id": "encoder",
      "crop_contract": {
        "borrow": ["corner radius", "stroke weight", "inner padding"],
        "must_change": ["source label", "source proportions", "source arrangement"],
        "human_editable_reason": "the frame is flat rectangle and stroke geometry"
      }
    },
    {
      "crop_id": "process-sequence",
      "reference_id": "reference-002",
      "crop_path": "references/figurebench/crops/process-sequence.png",
      "target_component_id": "diffusion",
      "crop_contract": {
        "borrow": ["nested grouping", "connector rhythm", "small-multiple spacing"],
        "must_change": ["scientific content", "number of internal states", "all source colours"],
        "human_editable_reason": "the construction uses grouped boxes, paths, and arrows"
      }
    }
  ],
  "coverage_matrix": [
    {
      "component_id": "prompt",
      "basic_geometry_justification": "Primitive: rectangle with centred text. Construction steps: draw one rectangle; apply one flat fill and outline; centre the exact label. Human-editable rationale: every part is a basic editable primitive"
    },
    {"component_id": "encoder", "crop_ids": ["frame-style"]},
    {"component_id": "diffusion", "crop_ids": ["process-sequence"]},
    {
      "component_id": "piano_roll",
      "basic_geometry_justification": "Primitive: rectangular grid with horizontal note bars. Construction steps: draw evenly spaced grid lines; add horizontal note rectangles; label time and pitch axes. Human-editable rationale: the grid, bars, and labels are basic editable primitives"
    },
    {
      "component_id": "audio",
      "basic_geometry_justification": "Primitive: framed waveform polyline. Construction steps: draw one rectangular frame; draw one centred polyline; place the exact output label. Human-editable rationale: the frame, polyline, and text remain independently editable"
    }
  ],
  "palette": {
    "base_palette_id": "workflow-role-01",
    "colours": [
      {"role": "primary", "hex": "#2E5BFF", "rgb": [46, 91, 255]},
      {"role": "accent", "hex": "#F59E0B", "rgb": [245, 158, 11]},
      {"role": "secondary", "hex": "#14B8A6", "rgb": [20, 184, 166]},
      {"role": "ink", "hex": "#475569", "rgb": [71, 85, 105]}
    ],
    "extensions": []
  },
  "taste_constraints": [
    "use a quiet hierarchy and deliberate whitespace",
    "keep one coherent stroke, corner, and arrowhead family",
    "reserve the accent for one scientifically meaningful emphasis"
  ]
}
```

When an extension is necessary, each `extensions` record has exactly `role`,
`hex`, `rgb`, `relationship`, `evidence_url`, and `evidence_summary`.

## Diagnosis — `svg-diagnostic/diagnosis.json`

One record is required for every Context 2 component. Allowed verdicts are `keep`,
`accept_variation`, `patch`, `reject`, and `replace`.

```json
{
  "verdicts": [
    {"id": "prompt", "component_id": "prompt", "verdict": "keep", "reason": "PNG1 label and simple geometry are faithful after the SVG1/PNG1.5 comparison; preserve them"},
    {"id": "encoder", "component_id": "encoder", "verdict": "patch", "reason": "PNG1 is flat but SVG1/PNG1.5 covers the box with a gradient; patch PNG2 back to the single palette fill"},
    {"id": "diffusion", "component_id": "diffusion", "verdict": "accept_variation", "reason": "the simplified three-state sequence preserves denoising semantics"},
    {"id": "piano_roll", "component_id": "piano_roll", "verdict": "reject", "reason": "the note grid reverses time and pitch and is logically wrong"},
    {"id": "audio", "component_id": "audio", "verdict": "replace", "reason": "the badge/marker is absent in SVG1/PNG1.5, so replace the failed transcription with a mature editable treatment"}
  ]
}
```

Every reason must state the observed PNG1 versus SVG1/PNG1.5 result and the action
that Prompt 2 must apply. A gradient-over-solid defect or a missing badge/seal/medal/
icon cannot be described as faithful and cannot receive `keep` or
`accept_variation`.

## Approved SVG crop request — `svg-diagnostic/approved-crops/request.json`

Only `keep`, `accept_variation`, and `patch` diagnoses may be referenced. Bounds use
normalized `x`, `y`, `width`, and `height` in PNG1.5.

```json
{
  "crops": [
    {
      "crop_id": "encoder-treatment",
      "target_component_id": "encoder",
      "diagnosis_id": "encoder",
      "bounds": {"x": 0.16, "y": 0.28, "width": 0.18, "height": 0.36}
    },
    {
      "crop_id": "diffusion-treatment",
      "target_component_id": "diffusion",
      "diagnosis_id": "diffusion",
      "bounds": {"x": 0.34, "y": 0.18, "width": 0.27, "height": 0.58}
    }
  ]
}
```

## Approved SVG materialized manifest — `svg-diagnostic/approved-crops/manifest.json`

```json
{
  "format": "approved-svg-materialized-crops-v1",
  "request": "svg-diagnostic/approved-crops/request.json",
  "crops": [
    {
      "path": "svg-diagnostic/approved-crops/encoder-treatment.png",
      "target_component_id": "encoder",
      "diagnosis": "patch: reduce width while preserving the corner and stroke treatment"
    },
    {
      "path": "svg-diagnostic/approved-crops/diffusion-treatment.png",
      "target_component_id": "diffusion",
      "diagnosis": "accept_variation: the simplified three-state sequence preserves denoising semantics"
    }
  ]
}
```

## Optional replacement-crop manifest

When a `reject` or `replace` verdict needs new visual evidence, use this exact
optional shape at `references/web/crops/replacements/manifest.json`:

```json
{
  "crops": [
    {
      "path": "references/web/crops/replacements/audio-waveform.png",
      "target_component_id": "audio",
      "reason": "replace the fake cartoon speaker with a mature editable waveform treatment"
    }
  ]
}
```

## Complete run manifest — `run-manifest.json`

```json
{
  "artifacts": {
    "methodology": "input/methodology.md",
    "context1": "context/context-1-domain-conventions.json",
    "context2": "context/context-2-content-visual-plan.json",
    "context3": "context/context-3-visual-kit.json",
    "web_manifest": "references/web/manifest.json",
    "figurebench_candidates": "references/figurebench/candidates.json",
    "figurebench_crop_request": "references/figurebench/crops/request.json",
    "figurebench_crops": "references/figurebench/crops/manifest.json",
    "prompt1": "prompt-1/prompt.md",
    "prompt1_attachments": "prompt-1/attachments.json",
    "png1": "png1.png",
    "svg1": "svg-diagnostic/svg1.svg",
    "png1_5": "svg-diagnostic/png1.5.png",
    "diagnosis": "svg-diagnostic/diagnosis.json",
    "approved_crop_request": "svg-diagnostic/approved-crops/request.json",
    "approved_crops": "svg-diagnostic/approved-crops/manifest.json",
    "prompt2": "prompt-2/prompt.md",
    "prompt2_attachments": "prompt-2/attachments.json",
    "png2": "png2-final.png"
  }
}
```
