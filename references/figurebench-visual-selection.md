# FigureBench visual selection for Prompt 1

FigureBench is a development-only source of construction and style geometry. It
does not supply a palette: choose all colours from the approved palette workflow.

1. Read Context 2 and list every planned visual need: components, frames,
   connectors, layout, and any special visualization. Give each need its Context
   2 component id.
2. Rank the complete FigureBench references, then inspect at least two distinct
   complete references before selecting any regions. Use complete figures only
   for inspection; never attach a complete figure to Prompt 1.
3. Select the relevant region from each inspected figure, and update the coverage
   matrix after each selection. Continue inspecting ranked complete references as
   needed. There is no fixed maximum or target number of images: stop only when
   every planned geometry, frame, connector, layout, and special visualization is
   covered.
4. A component can be covered without a crop only as a basic-geometry exception.
   The exception must name its primitive, explicit construction steps, and a
   human-editable rationale. Do not use this exception for an unexplained or
   complex visual treatment.
5. Emit the preserved crop request at
   `references/figurebench/crops/request.json` with normalized
   `[left, top, right, bottom]` coordinates. The deterministic crop command never
   overwrites this request; it writes crop files and the separate materialized
   `references/figurebench/crops/manifest.json`.
   Every crop must map to a `target_component_id` and carry a contract with:
   `borrow` (the construction/style geometry to reuse), `must_change` (the
   figure-specific content or proportions to alter), and
   `human_editable_reason` (why the result remains editable).
6. Apply `request.json` through the deterministic crop helper, validate coverage
   against that preserved request, and write `manifest.json` as the explicit
   materialized output. Attach only the resulting mapped crop images and their
   contracts to Prompt 1.

Prompt-facing output must contain only mapped crops with explicit `borrow`,
`must_change`, and `human_editable_reason` contracts. Never attach unexplained
complete figures, and never borrow or infer palette values from FigureBench.
