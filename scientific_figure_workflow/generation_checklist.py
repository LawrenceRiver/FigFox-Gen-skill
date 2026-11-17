"""Small generation handoff; full research stays in the replayable run artifacts."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

ROUTING_GRAMMAR = (
    'Plan module placement and connector clearance together, before locking the composition. '
    'Prefer straight source-to-target arrows. Reposition nearby modules to eliminate crossings '
    'and unnecessary bends rather than drawing a detour around a poor layout. '
    'Use only a few consistent right-angle bends or one deliberate smooth feedback arc when needed. '
    'Every arrow is one continuous, human-reproducible path from the actual source border to the '
    'target arrowhead: no disappearing shafts, isolated arrowheads, empty-space starts or unexplained gaps. '
    'Keep labels beside the shaft, never erase the shaft to fit text. Avoid intersections; if a crossing '
    'is scientifically unavoidable, use a clear continuous bridge and distinguish it from a junction. '
    'Mainline arrows should read immediately; return loops use a separate perimeter lane.'
)

LABEL_GRAMMAR = (
    'Use short scientific headings: SVG Reconstruction, Visual Inspection, Native Editing. '
    'Internal phase codes such as G1/G2 stay in planning, not reader-facing headings. '
    'Keep image text to labels, essential terms and equations. Typeset mathematical indices '
    'as real subscripts/superscripts, not literal underscores or raw TeX; preserve literal code '
    'and SVG IDs in monospace. Optically align text baselines, object edges and centers with '
    'consistent spacing/padding. Shorten text or rearrange crowded groups before shrinking fonts.'
)


def _text(record, key, location):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{location} needs {key}')
    return value.strip()


def _edge(record):
    def endpoint(keys):
        return next((record[k] for k in keys if k in record), None)
    return (endpoint(('source_id', 'from_component_id', 'source')),
            endpoint(('target_id', 'to_component_id', 'target')), record.get('label'))


def load_generation_plan(root, context2):
    root = Path(root).resolve()
    path = root / 'input/generation-plan.json'
    if not path.exists():
        return None
    if path.is_symlink() or (root / 'input').is_symlink():
        raise ValueError('generation plan/input must not be a symlink')
    return validate_generation_plan(json.loads(path.read_text()), context2)


def validate_generation_plan(plan, context2):
    if not isinstance(plan, dict) or plan.get('format') != 'figfox-generation-plan-v1':
        raise ValueError('unsupported generation plan')
    plan = copy.deepcopy(plan)
    for key in ('scientific_summary', 'layout', 'typography'):
        _text(plan, key, 'generation plan')
    invariants = plan.get('invariants')
    if not isinstance(invariants, list) or not invariants or any(not isinstance(v, str) or not v.strip() for v in invariants):
        raise ValueError('generation plan needs explicit scientific invariants')
    ids = {c['id'] for c in context2['components']}
    display_labels = plan.get('display_labels', {})
    if not isinstance(display_labels, dict) or any(
        key not in ids or not isinstance(value, str) or not value.strip()
        for key, value in display_labels.items()
    ):
        raise ValueError('display labels must map existing components to nonempty scientific captions')
    placements = plan.get('placements')
    if not isinstance(placements, list) or any(not isinstance(p, dict) for p in placements):
        raise ValueError('generation plan needs component placements')
    placed = [p.get('component_id') for p in placements]
    if len(placed) != len(set(placed)) or set(placed) != ids:
        raise ValueError('one placement required for every component; no duplicate or invented components')
    for placement in placements:
        _text(placement, 'placement', 'component placement')
    routes = plan.get('routes')
    if not isinstance(routes, list) or any(not isinstance(r, dict) for r in routes):
        raise ValueError('routes must cover every scientific relationship')
    for route in routes:
        source, target, label = _edge(route)
        if any(not isinstance(v, str) or not v.strip() for v in (source, target, label)):
            raise ValueError('routes must cover every scientific relationship with named endpoints and label')
        route['source_id'], route['target_id'] = source, target
    if Counter(_edge(r) for r in routes) != Counter(_edge(r) for r in context2['relationships']):
        raise ValueError('routes must cover every scientific relationship exactly once, with unchanged endpoints and label')
    for route in routes:
        for key in ('source_port', 'target_port', 'via'):
            _text(route, key, 'scientific route')
    visuals = plan.get('local_visuals', [])
    if not isinstance(visuals, list):
        raise ValueError('local visuals must be a list')
    for visual in visuals:
        if not isinstance(visual, dict) or visual.get('target_component_id') not in ids:
            raise ValueError('local visual needs an existing component')
        for key in ('meaning', 'construction', 'basis'):
            _text(visual, key, 'local visual')
    if 'visual_needs' in plan:
        needs = plan['visual_needs']
        if not isinstance(needs, list) or not needs or any(not isinstance(n, dict) for n in needs):
            raise ValueError('visual needs require a nonempty anchored list')
        for need in needs:
            for key in ('id', 'need', 'methodology_evidence', 'peer_evidence'):
                _text(need, key, 'visual need')
        need_ids = [n['id'] for n in needs]
        if len(need_ids) != len(set(need_ids)):
            raise ValueError('visual need ids must be unique')
        covered = [v.get('need_id') for v in visuals]
        if any(n not in need_ids for n in covered) or set(covered) != set(need_ids):
            raise ValueError('each visual need needs a grounded drawing correspondence; unknown or missing visual need')
    if 'detail_hierarchy' in plan:
        hierarchy = plan['detail_hierarchy']
        if not isinstance(hierarchy, dict):
            raise ValueError('innovation hierarchy must be a mapping')
        _text(hierarchy, 'common_depth', 'innovation hierarchy')
        if 'peer_depth_observation' in hierarchy:
            _text(hierarchy, 'peer_depth_observation', 'innovation hierarchy')
        focuses = hierarchy.get('innovation_focuses')
        if not isinstance(focuses, list) or not focuses:
            raise ValueError('innovation hierarchy requires source-grounded focuses')
        for focus in focuses:
            if not isinstance(focus, dict):
                raise ValueError('innovation focus must be a mapping')
            for key in ('claim', 'draw_to'):
                _text(focus, key, 'innovation focus')
            targets = focus.get('component_ids')
            if not isinstance(targets, list) or not targets or any(not isinstance(t, str) or t not in ids for t in targets):
                raise ValueError('innovation focus must name existing components')
        whole = hierarchy.get('keep_whole', [])
        if not isinstance(whole, list) or any(not isinstance(t, str) or t not in ids for t in whole):
            raise ValueError('innovation hierarchy keep_whole must name existing components')
    return plan


def checklist_lines(plan, methodology, context1, context2, context3):
    # A digest binds omitted research to replay without putting search transcripts into the image prompt.
    digest = hashlib.sha256(json.dumps([methodology, context1, context2, context3, plan],
        sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    placements = {p['component_id']: p['placement'] for p in plan['placements']}
    display_labels = plan.get('display_labels', {})
    return [
        'Create one complete scientific figure from this locked generation checklist.',
        'Evidence SHA256: ' + digest,
        '## Scientific meaning', plan['scientific_summary'],
        *['- ' + invariant for invariant in plan['invariants']],
        *(['## Visual-needs anchor (Methodology intersected with inspected peer conventions)',
           *[f"- {n['id']}: {n['need']} | Methodology: {n['methodology_evidence']} | Peers: {n['peer_evidence']}" for n in plan['visual_needs']]] if 'visual_needs' in plan else []),
        *(['## Innovation-led detail hierarchy',
           'Peer depth observation: ' + plan['detail_hierarchy'].get('peer_depth_observation', 'Use the inspected peer granularity, not invented model internals.'),
           *[f"- Innovation: {f['claim']} | Focus: {', '.join(f['component_ids'])} | Finest visible unit: {f['draw_to']}" for f in plan['detail_hierarchy']['innovation_focuses']],
           'Shared non-innovation depth: ' + plan['detail_hierarchy']['common_depth'],
           'Keep whole (no invented model internals): ' + ', '.join(plan['detail_hierarchy'].get('keep_whole', [])),
           'Allocate detail to the actual contributions; do not expand standard components just because they are familiar. Match supporting regions at the shared level.'] if 'detail_hierarchy' in plan else []),
        '## Locked overall framework', plan['layout'],
        '## Connector construction (Creative Director and generator)', ROUTING_GRAMMAR,
        'Draw every named component once. A container may be the component itself; do not add duplicate stand-ins. Repeated snapshots inside a component are insets, not extra pipeline nodes.',
        '## Exact components and placement',
        *[f"- {c['id']} = `{display_labels.get(c['id'], c['label'])}` | {placements[c['id']]} | {c['visual_treatment']}" for c in context2['components']],
        '## Exact directed connections (one arrowhead per relationship)',
        'These relationship labels specify meaning. Show only short relation captions where needed; not every arrow needs visible explanatory text. Preserve essential scientific notation and conditions.',
        *[f"- {r['source_id']}.{r['source_port']} -> {r['target_id']}.{r['target_port']} | `{r['label']}` | {r['via']}" for r in plan['routes']],
        'Ports name the actual object/frame boundary. Never stop at an empty margin, nearby input, or unrelated enclosing stage. Independent evidence edges have distinct landing ports and arrowheads; crossings are not junctions. Do not merge unrelated evidence into one long bus.',
        '## One-to-one drawing correspondence',
        '| Need / location | Reference construction or source basis | Our adapted drawing |',
        '| --- | --- | --- |',
        *[f"| {v.get('need_id', v['meaning'])} / {v['target_component_id']} | {v['basis']} | {v['construction']} |" for v in plan.get('local_visuals', [])],
        'These are intentional visual content, not ornamental stickers. Keep them small, readable and coherent with the main reference. No invented observations, numerical results or unlabelled decorative particles.',
        '## Typography reference', plan['typography'], LABEL_GRAMMAR,
    ]
