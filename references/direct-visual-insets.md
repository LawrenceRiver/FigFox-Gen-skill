# Direct visual insets

## Decide from the role, not a list of objects

During the existing visual-needs retrieval pass, ask: **would a well-chosen existing visual asset communicate this content more clearly, naturally or faithfully than redrawing it?** If yes, collect and inspect the actual file for direct use or a crop. If only its drawing grammar is useful, classify it as construction/style evidence. If the content is an abstract mechanism, draw the native schematic. Do not make every component an image-search task and do not add a separate generic search round.

Examples can include a specimen, a screen, an object, an environment, a measured signal, a document region, a rendered view or another informative visual instance. These are examples only; apply the same reasoning to other domains and media. A meaningful existing illustration can also qualify. Audio/video itself requires selecting or deriving a truthful visual representation from the identified source, rather than inventing an unrelated signal.

## Collect once, keep roles explicit

For a selected direct-content asset, retain the original file under `input/raster/` and record its source URL or user/own-data origin, inspected dimensions/aspect, use-permission evidence, attribution and scientific role. A search thumbnail, publicly accessible page or arXiv presence does not by itself establish reuse permission. Prefer relevant user/source data, author-owned assets or material whose applicable terms permit the intended use. Keep unresolved candidates local as leads. Do not infer that one dataset license covers every constituent asset.

In the existing need-to-drawing correspondence, state **direct inset / crop / construction-only**, the target component and why that treatment communicates the Methodology. Reuse selected assets and source metadata across parallel work. Do not copy another method’s labels or evidence, imply an illustrative stock sample is a real generated result, or replace a scientific input with a semantically mismatched pretty picture.

## Design the inset before generation

Creative Director reserves a readable, axis-aligned area inside the complete rectangular framework. Match inset sizes for comparable views, preserve source aspect, choose a justified crop or contain fit, and align borders/baselines with adjacent native elements. Keep arrows, labels and frame strokes outside the inset. The asset supplies visual content; it does not impose the whole figure’s palette or style.

For pixel-preserving use, generate the layout with the declared inset regions left clean. Keep that image as `generated-layout.png`; do not ask the image model to redraw the selected asset. Then inspect the actual generated image and record the observed inset boxes in its pixel coordinates. Do not blindly scale planned coordinates when the model changes the canvas ratio or local placement.

## Optional deterministic placement

The calling Harness may use `scripts/place_raster_insets.py`; it does not search, select assets, evaluate licenses, identify blank slots or call a model. It validates a placement manifest, uses Pillow for aspect-preserving placement, and keeps a provenance receipt. This is a requested use of collected raster material, not another image-generation pass or a repair loop.

Example manifest `input/raster-inserts.json` (replace all example values with inspected actual records):

```json
{
  "canvas": [1600, 1000],
  "background": "generated-layout.png",
  "output": "png1.png",
  "insets": [
    {
      "path": "input/raster/selected-asset.png",
      "target_component_id": "actual-component-id",
      "box": [80, 200, 240, 160],
      "source": "actual source URL or own/user data origin",
      "permission_evidence": "actual applicable permission for use in this figure",
      "attribution": "actual required credit",
      "fit": "contain"
    }
  ]
}
```

`box` is `[x,y,width,height]` on the actual background, not guessed model coordinates. `contain` fits the full image without stretching and leaves the surrounding layout visible; `cover` fills the box by a centered aspect-preserving crop. If that crop removes scientifically important information, select a better source crop first or use contain. Every selected region must be clear of connector shafts and meaningful text; the helper cannot judge this visually.

```sh
python scripts/place_raster_insets.py --run RUN --manifest input/raster-inserts.json
```

Keep the background, source assets, manifest and provenance receipt. Required attribution must accompany the delivered figure in the manner required by the asset terms; a local receipt alone is not a public credit. Inspect the final composite for correct content, crop, resolution, visual alignment and unobscured arrows. Existing no-reference case trials remain the recorded runs they were; do not describe them as having used internet insets retroactively.
