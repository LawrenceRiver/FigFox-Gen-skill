# Canonical artifact schemas

All paths are run-relative. The workflow stops after one final PNG1.

## Context 1 — context/context-1-domain-conventions.json

```json
{
  "domain": "music generation",
  "dominant_colour_count": 2,
  "mainline": "text prompt to structured representation to audio",
  "conventions": [
    {
      "concept": "piano roll",
      "recurrence_evidence": "A time-pitch grid recurs in three retained method figures.",
      "visual_treatment": "rectangular grid with horizontal note bars",
      "terminology": "piano roll",
      "methodology_relevance": "shows the structured representation before decoding",
      "eligible_source_crops": [
        {
          "path": "references/web/crops/piano-roll-panel.png",
          "target_component_id": "piano_roll",
          "borrow": ["time-pitch grid grammar"],
          "must_change": ["source labels", "source arrangement"]
        }
      ]
    }
  ]
}
```

The scholarly manifest at references/web/manifest.json records 3–4 distinct HTTPS
paper pages, exact evidence URLs, crop paths, and visible pixel inspection notes.
Every mapped Context 1 crop must exist under references/web/crops and be declared in
the manifest.

## Context 2 — context/context-2-content-visual-plan.json

```json
{
  "mainline": "prompt to encoded conditioning to structured representation to audio",
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
      "id": "audio",
      "label": "Generated Audio",
      "semantic_role": "output",
      "visual_treatment": "framed waveform path",
      "construction_provenance": "human-editable path geometry",
      "special": "no",
      "source_context": "methodology"
    }
  ],
  "relationships": [
    {"source_id": "prompt", "target_id": "audio", "label": "decodes to"}
  ]
}
```

Every component has a semantic role, an exact label, a visual treatment,
construction provenance, and a special-treatment explanation when needed.

## FigureBench crop request — references/figurebench/crops/request.json

Bounds are normalized [left, top, right, bottom]. The request is preserved as
model-authored evidence and is never overwritten by materialization.

```json
{
  "crops": [
    {
      "id": "frame-style",
      "reference_id": "reference-001",
      "bounds": [0.05, 0.08, 0.48, 0.44],
      "target_component_id": "prompt",
      "crop_contract": {
        "borrow": ["corner radius", "stroke weight", "inner padding"],
        "must_change": ["source label", "source proportions", "source arrangement"],
        "human_editable_reason": "the frame is flat rectangle and stroke geometry"
      }
    }
  ],
  "basic_geometry": []
}
```

The materialized manifest at references/figurebench/crops/manifest.json has format
figurebench-materialized-crops-v1 and records the deterministic crop paths.
Context 3 must reproduce its selected references and coverage matrix exactly.

## Context 3 — context/context-3-visual-kit.json

```json
{
  "selected_references": [
    {
      "crop_id": "frame-style",
      "reference_id": "reference-001",
      "crop_path": "references/figurebench/crops/frame-style.png",
      "target_component_id": "prompt",
      "crop_contract": {
        "borrow": ["corner radius", "stroke weight", "inner padding"],
        "must_change": ["source label", "source proportions", "source arrangement"],
        "human_editable_reason": "the frame is flat rectangle and stroke geometry"
      }
    }
  ],
  "coverage_matrix": [
    {"component_id": "prompt", "crop_ids": ["frame-style"]},
    {"component_id": "audio", "basic_geometry_justification": "Draw a framed waveform polyline with an exact label."}
  ],
  "palette": {
    "base_palette_id": "workflow-role-01",
    "dominant_colour_roles": ["primary", "accent"],
    "colours": [
      {"role": "primary", "hex": "#2E5BFF", "rgb": [46, 91, 255]},
      {"role": "accent", "hex": "#F59E0B", "rgb": [245, 158, 11]},
      {"role": "secondary", "hex": "#14B8A6", "rgb": [20, 184, 166]},
      {"role": "ink", "hex": "#475569", "rgb": [71, 85, 105]}
    ],
    "extensions": []
  },
  "taste_constraints": ["use deliberate whitespace", "keep one coherent stroke family"]
}
```

Use exactly one named multi-colour palette group; use multiple colours from that group.
Declare exactly the dominant-colour count anchored by Context 1 for the final figure;
the remaining swatches are subordinate support roles and must not be promoted beyond
that anchored count.
Extensions, if needed, have role, exact
uppercase HEX, matching RGB, relationship, HTTPS evidence_url, and an evidence
summary. FigureBench, scholarly figures, and the user reference are never active
palette sources.

## Creative Director brief — creative-director/brief.json

This brief is produced after Context 3 and before Prompt 1. It records bounded visual
ideas rather than an image result. A paper-SVG crop is a run-local targeted raster
crop of a real scholarly SVG/HTML figure; URLs preserve its source and evidence page.

```json
{
  "format": "creative-director-brief-v1",
  "brief": "Use a restrained editable enclosure for the intermediate representation.",
  "ideas": [
    {
      "id": "intermediate-shape-language",
      "target_component_id": "audio",
      "concept": "A compact enclosure with clear connector rhythm",
      "visual_intent": "Make the intermediate representation read as human-editable.",
      "construction_plan": "Use grouped rectangles and paths, then change labels and proportions.",
      "requires_svg_evidence": true,
      "svg_crops": [
        {
          "path": "references/web/crops/creative-director/intermediate-shape-language.png",
          "target_component_id": "audio",
          "source_url": "https://arxiv.org/html/2402.14285",
          "evidence_url": "https://arxiv.org/html/2402.14285v4/figure.svg",
          "source_format": "svg",
          "borrow": ["editable enclosure", "connector rhythm"],
          "must_change": ["source labels", "source proportions", "source colours"],
          "human_editable_reason": "The crop uses editable rectangles and paths rather than a pasted object."
        }
      ]
    }
  ]
}
```

Every crop must be unique, under references/web/crops/creative-director, and point
to an existing run-local file. The target component must match its idea. Both URLs
must be HTTPS and source_format must be exactly svg. If no idea needs new external
evidence, return an empty svg_crops list and the validator reports
no_external_svg_needed.

## Prompt 1 bundle — prompt-1/prompt.md and attachments.json

The bundle format is scientific-figure-prompt-bundle-v1 with phase prompt1. Allowed
attachment roles are user_reference, domain_paper_component,
figurebench_component, and creative_director_svg. Each attachment contains only its
role contract and a safe run-relative path. PNG1 is the only generated image path.

## Complete run manifest — run-manifest.json

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
    "creative_director_prompt": "creative-director/prompt.md",
    "creative_director_brief": "creative-director/brief.json",
    "prompt1": "prompt-1/prompt.md",
    "prompt1_attachments": "prompt-1/attachments.json",
    "png1": "png1.png"
  }
}
```

A valid run contains exactly one image artifact, png1.png, and stops there.
