"""Small generation handoff; full research stays in the replayable run artifacts."""
from collections import Counter
import copy
import hashlib
import json
import re
from pathlib import Path
from .routing_geometry import compile_routing_geometry

ROUTING_GRAMMAR = (
    'Plan placement and connector clearance together. Prefer straight, axis-aligned ports; move modules '
    'to remove crossings and detours before locking exact route points. Use few consistent right-angle bends. '
    'Every arrow is one continuous human-reproducible source-border to target-arrowhead path: '
    'no empty-space starts, isolated heads, disappearing shafts or unexplained gaps. '
    'Keep text and heading areas clear of shafts; fills never erase lines. '
    'An unavoidable crossing needs a continuous bridge or declared distinguishing ink; it is not a junction. '
    'Return loops use a perimeter lane and land in their actual process subregion, not an adjacent training/evaluation inset. '
    'Choose a coherent reference-matched arrow family, including bold hand-drawn shafts or filled/rounded bodies when appropriate. '
    'Keep head/body proportions and weight consistent within each role and scale. Points specify centerlines, '
    'not mandatory thin-black ink; reserve clearance for the chosen width. After text/icons, trace every shaft again.'
)

LABEL_GRAMMAR = (
    'Use concise unnumbered scientific headings from this Methodology only; no stage titles from other cases '
    'or orchestration codes. Default to bold dark or deliberate theme-coloured text on the normal background, '
    'not automatic coloured title strips or white-on-colour tabs. Fill emphasizes scientific content/mechanisms. '
    'Text is labels, essential terms and equations. Typeset true subscripts/superscripts; NO visible underscore '
    'in identifiers or illustrative code. Use approved aliases; raw IDs stay internal. '
    'Optically align baselines, edges and centers with consistent padding; shorten/reflow before shrinking fonts.'
)

GRID_GRAMMAR = (
    'Imagine a complete rectangular overview first. State its organizing rule: equal-width columns, '
    'equal-height parallel bands or balanced bilateral groups, according to the scientific graph. '
    'Equalize peer regions, margins and gutters; innovations may span integer cells. '
    'Reserve output inside the fixed canvas/grid; align sibling edges/baselines. '
    'Reflow upstream content instead of appending a dangling final block. Visual symmetry never invents '
    'branches, reverses edges or merges unrelated paths into a bus. Keep flow simple; no added step numbers.'
)


def validate_notation_map(value):
    if not isinstance(value, dict) or any(
        not isinstance(source, str) or not source.strip() or
        not isinstance(display, str) or not display.strip() or '_' in display
        for source, display in value.items()
    ):
        raise ValueError('notation map needs nonempty source/display strings; no underscore in display')
    return dict(value)


def typeset_notation(text, mapping):
    if not mapping:
        return text
    # Preserve actual paths and avoid partial-ID replacements. Change image-facing text only.
    pattern = r'(?<![\w/])(' + '|'.join(re.escape(k) for k in sorted(mapping, key=len, reverse=True)) + r')(?![\w/])'
    return re.sub(pattern, lambda match: mapping[match[0]], text)


def check_image_notation(prompt, metadata_prefixes=(), attachment_paths=()):
    text = prompt
    for path in attachment_paths:
        text = text.replace(path, '')
    for prefix in metadata_prefixes:
        # Exclude only the actual structured occurrence, never that token elsewhere in prose/code.
        for path in attachment_paths:
            prefix = prefix.replace(path, '')
        text = re.sub(r'(?m)^' + re.escape(prefix), '', text)
    tokens = set(re.findall(r'\b\w+_(?:\{[^}\s]+\}|\([^\)\s]+\)|\w+)|\b\w*_\w*\b', text))
    missing = tokens
    if missing:
        raise ValueError('unmapped underscore notation in image packet: ' + ', '.join(sorted(missing)) + '; add Creative Director notation_map aliases')


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
    if not isinstance(plan, dict) or plan.get('format') not in {'figfox-generation-plan-v1', 'figfox-generation-plan-v2'}:
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
    if any('_' in label for label in display_labels.values()):
        raise ValueError('visible display labels cannot contain an underscore; use typeset notation')
    if 'notation_map' in plan:
        validate_notation_map(plan['notation_map'])
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
    if plan['format'] == 'figfox-generation-plan-v2' or 'routing_geometry' in plan:
        if 'routing_geometry' not in plan:
            raise ValueError('V2 generation plan requires routing geometry')
        plan['routing_geometry'], plan['routes'] = compile_routing_geometry(
            plan['routing_geometry'], plan['routes'], ids)
    return plan


def checklist_lines(plan, methodology, context1, context2, context3, *, for_image=False):
    # A digest binds omitted research to replay without putting search transcripts into the image prompt.
    digest = hashlib.sha256(json.dumps([methodology, context1, context2, context3, plan],
        sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    placements = {p['component_id']: p['placement'] for p in plan['placements']}
    geometry = plan.get('routing_geometry')
    if geometry:
        placements = {key: 'box ' + json.dumps(box) for key, box in geometry['node_boxes'].items()}
    display_labels = plan.get('display_labels', {})
    notation = plan.get('notation_map', {})
    labels = {c['id']: typeset_notation(display_labels.get(c['id'], c['label']), notation) for c in context2['components']}
    if for_image and any('_' in label for label in labels.values()):
        raise ValueError('visible label has an unmapped underscore; add display_labels or notation_map')
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
        GRID_GRAMMAR,
        *(['Canvas pixels: ' + json.dumps(geometry['canvas']) + '; preserve the exact boxes and path points below. Scale the entire composition uniformly.',
           'Grid rows: ' + json.dumps(geometry['rows']) + '; columns: ' + json.dumps(geometry['columns']),
           'Clearance: ' + str(geometry['clearance']) + ' pixels. Captions must stay in their reserved boxes; never cut shafts.',
           *[f"Declared crossing of routes {c['routes']} at {c['point']}: {c['treatment'].replace('_', ' ')}; {c['reason']}" for c in geometry.get('crossings', [])]] if geometry else []),
        '## Connector construction (Creative Director and generator)', ROUTING_GRAMMAR,
        'Draw every named component once. A container may be the component itself; do not add duplicate stand-ins. Repeated snapshots inside a component are insets, not extra pipeline nodes.',
        '## Exact components and placement',
        *[f"- {c['id']} = `{labels[c['id']]}` | {placements[c['id']]} | {c['visual_treatment']}" for c in context2['components']],
        '## Exact directed connections (one arrowhead per relationship)',
        'These relationship labels specify meaning. Show only short relation captions where needed; not every arrow needs visible explanatory text. Preserve essential scientific notation and conditions.',
        *[f"- {r['source_id']}.{r['source_port']} -> {r['target_id']}.{r['target_port']} | `{r['label']}` | {_route_construction(r, geometry)}" for r in plan['routes']],
        'Ports name the actual object/frame boundary. Never stop at an empty margin, nearby input, or unrelated enclosing stage. Independent evidence edges have distinct landing ports and arrowheads; crossings are not junctions. Do not merge unrelated evidence into one long bus.',
        '## One-to-one drawing correspondence',
        '| Need / location | Reference construction or source basis | Our adapted drawing |',
        '| --- | --- | --- |',
        *[f"| {v.get('need_id', v['meaning'])} / {v['target_component_id']} | {v['basis']} | {v['construction']} |" for v in plan.get('local_visuals', [])],
        'For every visual need, choose direct use of a suitable collected asset, a source crop, or borrowed construction. '
        'Do not treat all existing imagery as style evidence: when a real visual instance communicates the content best, '
        'reserve an aligned inset for the actual file instead of inventing a drawn substitute. '
        'Only explicitly collected and approved direct-content insets get reserved slots; invent no blank panels when none are selected. '
        'Those insets are composited after generation; leave only those declared slots clean and preserve their aspect ratios. '
        'This choice is open-ended across domains, not limited to any media category. '
        'Source material used illustratively must not masquerade as this method’s measured result.',
        'For standard models actually named in this Methodology, use a source-checked recognizable architectural silhouette '
        'at the scoped detail level. An unchanged model may remain a compact canonical inset; invent no arbitrary replacement geometry '
        'and do not expand supporting internals beyond the innovation-led hierarchy. Reuse already inspected construction evidence.',
        'These are intentional visual content, not ornamental stickers. Keep them small, readable and coherent with the main reference. No invented observations, numerical results or unlabelled decorative particles.',
        '## Typography reference', plan['typography'], LABEL_GRAMMAR,
    ]


def _route_construction(route, geometry):
    if not geometry:
        return route['via']
    result = route['route_kind'] + ' points ' + json.dumps(route['points'])
    if route.get('caption'):
        result += ' | visible caption `' + route['caption'] + '` in box ' + json.dumps(route['caption_box'])
    return result
