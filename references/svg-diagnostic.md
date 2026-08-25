# SVG1 diagnostics and review-only crops

## Purpose and boundaries

PNG1 is visual truth for the base Codex multimodal model's bare-model SVG1
transcription. Request one direct transcription of PNG1; do not locally rebuild,
beautify, redraw, repair, or substitute SVG from the Methodology, contexts, or
topology plan. If the transcription cannot be inspected or rendered faithfully,
report the failure and retain PNG1 rather than silently hand-authoring another
SVG.

Python only inspects SVG1 safely, deterministically renders PNG1.5, and crops
diagnosis-approved regions from PNG1.5. PNG1.5 is VLM-review-only: it is never
an image-generation attachment and never becomes an input to a PNG2-to-SVG loop.

## Inspection and rendering

`inspect_editable_svg()` uses defused XML parsing and requires the root and every
child element to be in the SVG namespace. Foreign-namespace and no-namespace
children, scripts, and `foreignObject` fail closed. Before CairoSVG can run, the
inspector rejects `xml:base`, file/relative/absolute/HTTP/protocol-relative
resources, unsafe `href` and `xlink:href` values on every element (including
`use`), CSS `@import`, and every `url(...)` except an internal `url(#fragment)`.
CSS is tokenized with `tinycss2`, so escaped function names, quoted URLs, and
URLs nested in other functions are checked after CSS escape decoding in style
attributes, presentation values, declaration lists, at-rules, and stylesheets.
Only an `image` `href` may carry base64 `data:image/png`, `data:image/jpeg`, or
`data:image/webp`. The decoded payload is limited to 5 MiB and 25 megapixels,
verified by Pillow as a real image, and required to match its declared MIME
format; malformed, mislabeled, XML/SVG, and oversized payloads fail before
CairoSVG.

Editable counts include only visible, positive-size SVG-namespace `text`,
`rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, and `path` nodes.
Definitions, display-none or visibility-hidden branches, zero-opacity content,
zero-size geometry, and zero-length geometry cannot satisfy editability. The
summary reports visible and total raster counts, meaningful editable-node count,
large/full-canvas raster counts, and dominant-raster status for VLM diagnosis.
A conservative structural check rejects a dominant raster paired only with
zero, microscopic, or trivial vector content. Candidate geometry must have
visible paint, intersect the viewport, and remain provably visible after
inherited inline visibility/opacity, transforms, clipping/filter uncertainty,
and later-raster paint-order occlusion. Stylesheets capable of changing
visibility, opacity, paint, clipping, filters, or transforms make vector
eligibility uncertain and therefore cannot prove editability beside a dominant
raster. Unhandled complex paths and fragment/variable paint are similarly not
used to satisfy that gate. A raster painted first followed by meaningful,
visible flat-colour labels and geometry remains eligible. Python reports these
structural facts; it does not infer whether an embedded raster depicts a genuine
photograph.

Structural editability and dominant-raster proof are separate. In a vector-only
SVG, painted nonzero text and geometry inside transforms or nested SVG viewports
still count as editable markup. When a dominant raster is present, those same
nodes cannot satisfy the two-meaningful-node proof unless their final visibility
and bounds are conservatively known. Hidden, non-rendering, zero-size, and
unpainted structural content never counts in either category.

`render_svg()` calls CairoSVG only after validation. It rejects symlink output
targets, renders to an exclusive temporary sibling, verifies a real nonempty
PNG, and atomically publishes `svg-diagnostic/png1.5.png`. Failure removes the
temporary and any stale regular canonical PNG1.5; SVG1 is never modified.

## VLM diagnosis

The diagnosis compares PNG1, SVG1, PNG1.5, and Contexts 1–3, with Context 2
components as the identity authority. It returns one of five verdicts for every
component:

- `keep`: preserve the faithful component.
- `accept_variation`: a reasonable complex simplification may pass when the
  semantic logic survives.
- `patch`: retain the component but correct the named local defect.
- `reject`: do not use the component as evidence.
- `replace`: use a provenance-safe replacement lookup for a semantically wrong
  component.

Semantic truth outranks surface polish. Fake, abstract, cartoon, or
semantically wrong objects are rejected or replaced; a visually plain but
scientifically faithful structure is not rejected merely for lacking decorative
detail. The VLM, not Python, approves a genuine photographic crop or determines
whether a simplification keeps the intended scientific logic.

## Approved crop request and materialized manifest

`apply_svg_crop_manifest(rendered_png, manifest, output_dir)` accepts only
`svg-diagnostic/png1.5.png` and only writes below the same run's
`svg-diagnostic/approved-crops/` root. The VLM coordinates are preserved in
`request.json`; deterministic cropping never overwrites them. At execution, the
caller supplies a Task 1-valid `diagnosis` and a mandatory non-empty complete
`component_ids` list copied from Context 2 alongside request crop records with
`crop_id`, `target_component_id`, `diagnosis_id`, and normalized `bounds`:

```json
{
  "component_ids": ["encoder"],
  "diagnosis": {"verdicts": [{"component_id": "encoder", "verdict": "keep", "reason": "faithful label and geometry"}]},
  "crops": [{
    "crop_id": "encoder-detail",
    "target_component_id": "encoder",
    "diagnosis_id": "encoder",
    "bounds": {"x": 0.0, "y": 0.0, "width": 0.5, "height": 0.5}
  }]
}
```

The separate materialized `manifest.json` explicitly identifies `request.json`
as its source and contains only the Task 5-compatible approved-crop attachment
records returned by deterministic cropping.

Every crop must cite a real diagnosis record for the same Context 2 component.
The diagnosis is validated against the supplied Context 2 identity anchor; the
expected IDs are never inferred from diagnosis claims. Crop IDs are unique safe
filenames, bounds must remain inside normalized PNG1.5 coordinates, and the
output directory, its in-run parents, and final destinations must not redirect
through symlinks. Each PNG is encoded to an exclusive temporary sibling and
atomically replaces its approved-crop directory entry.
Only `keep`, `accept_variation`, and `patch` records may be cropped;
`reject` and `replace` fail. The result is a Task 5-compatible `svg_crops`
object: each record has a run-relative approved-crop path, target component,
and diagnosis string. Only these approved SVG crops may enter Prompt 2; the
full PNG1.5 path is never returned as an attachment.
