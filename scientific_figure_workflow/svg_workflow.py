"""Source SVGs, reference-derived colour, and Director-owned new-run decisions.

Legacy palette-library artifacts remain replayable; this contract is opt-in on
old artifacts and mandatory in the active skill's new-run intake.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import colorsys

POLICY = 'svg-reference-v1'


def svg_source(path):
    path = Path(path)
    if path.suffix.lower() != '.svg':
        raise ValueError('Reference must have a genuine SVG source, not raster')
    data = path.read_bytes()
    clean = re.sub(r'/\*.*?\*/|<!--.*?-->', '', data.decode('utf-8-sig', errors='replace'), flags=re.S)
    if re.search(r'@import\b|<\?xml-stylesheet\b', clean, re.I):
        raise ValueError('SVG must be self-contained; inline and retain external styles first')
    for match in re.findall(r'url\(\s*([^)]*)\)', clean, re.I):
        if not match.strip().strip('\"\'').startswith('#'):
            raise ValueError('SVG must be self-contained; external CSS/paint URLs are not retained')
    try:
        root = ET.fromstring(data)
    except (ET.ParseError, UnicodeError) as error:
        raise ValueError('Reference is not a genuine SVG document') from error
    if root.tag.split('}')[-1] != 'svg':
        raise ValueError('Reference root must be SVG')
    for node in root.iter():
        if node.tag.split('}')[-1] in {'image', 'foreignObject'}:
            raise ValueError('SVG reference must not embed raster images or foreignObject')
        for key, value in node.attrib.items():
            if key.split('}')[-1] == 'href' and not value.startswith('#'):
                raise ValueError('SVG reference must be self-contained')
    text = re.sub(r'/\*.*?\*/|<!--.*?-->', '', data.decode('utf-8-sig'), flags=re.S)
    text = '\n'.join(re.findall(r'(?:fill|stroke|stop-color|color)\s*[:=]\s*["\']?([^;"\'<>}\n]+)', text))
    colours = {c.upper() for c in re.findall(r'#[0-9a-fA-F]{6}\b', text)}
    for c in re.findall(r'(?<![\w-])#[0-9a-fA-F]{3}(?![0-9a-fA-F])', text):
        colours.add('#' + ''.join(v * 2 for v in c[1:]).upper())
    for rgb in re.findall(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', text):
        if all(0 <= int(v) <= 255 for v in rgb):
            colours.add('#' + ''.join(f'{int(v):02X}' for v in rgb))
    for h,s,l in re.findall(r'hsl\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%\s*\)', text):
        rgb = colorsys.hls_to_rgb(float(h)/360, float(l)/100, float(s)/100)
        colours.add('#' + ''.join(f'{round(v*255):02X}' for v in rgb))
    for name, colour in [('white','#FFFFFF'),('black','#000000')]:
        if re.search(r'\b'+name+r'\b',text):colours.add(colour)
    return dict(sha256=hashlib.sha256(data).hexdigest(), colours=colours)


def svg_preview(path, destination):
    """Rendering is only a viewing/attachment derivative of the retained SVG."""
    svg_source(path)
    import cairosvg
    cairosvg.svg2png(url=str(path), write_to=str(destination), background_color='white')


def local_file(root, relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError('SVG source needs a local path')
    p = Path(relative)
    root = Path(root).resolve()
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('SVG source path must stay inside run')
    current = root
    for part in p.parts:
        current /= part
        if current.is_symlink():
            raise ValueError('SVG source path must not use symlinks')
    if not current.is_file() or not current.resolve().is_relative_to(root):
        raise ValueError('SVG source must be an existing file inside run')
    return current


def _text(record, key):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError('SVG palette requires ' + key)
    return value.strip()


def validate_svg_palette(value):
    from .palette import _palette_shape, _validate_extensions
    if not isinstance(value, dict):
        raise ValueError('SVG palette must be an object')
    expected = {'source_mode', 'base_palette_id', 'dominant_colour_roles', 'colours',
                'extensions', 'reference', 'relationships'}
    if set(value) - expected:
        raise ValueError('Unknown SVG palette fields: ' + ', '.join(sorted(set(value) - expected)))
    base = {k: deepcopy(value[k]) for k in ('base_palette_id', 'dominant_colour_roles', 'colours')}
    base['extensions'] = []
    result = _palette_shape(base)
    roles = [c['role'] for c in result['colours']]
    if len(roles) != len(set(roles)):
        raise ValueError('SVG palette roles must be unique')
    reference = value.get('reference')
    if not isinstance(reference, dict):
        raise ValueError('SVG palette requires a reference')
    for key in ('path', 'sha256', 'source_url', 'evidence_url', 'source_track', 'target_track'):
        _text(reference, key)
    from urllib.parse import urlparse
    for key in ('source_url', 'evidence_url'):
        url = urlparse(reference[key])
        if url.scheme != 'https' or not url.netloc:
            raise ValueError('SVG reference requires HTTPS ' + key)
    if reference.get('complete_figure') is not True:
        raise ValueError('Palette reference must be a complete SVG figure')
    if reference['source_track'].strip().casefold() == reference['target_track'].strip().casefold():
        raise ValueError('Palette reference must come from another track')
    if not re.fullmatch(r'[0-9a-f]{64}', reference['sha256']):
        raise ValueError('SVG reference needs sha256')
    relationships = value.get('relationships')
    if not isinstance(relationships, list) or not relationships:
        raise ValueError('Record observed SVG colour relationships, not just swatches')
    seen = {}
    for rel in relationships:
        if not isinstance(rel, dict):
            raise ValueError('Colour relationship must be an object')
        pair = rel.get('roles')
        if not isinstance(pair, list) or len(pair) != 2 or len(set(pair)) != 2 or not set(pair) <= set(roles):
            raise ValueError('Colour relationship must name two known source roles')
        if rel.get('relation') not in {'adjacent', 'separate'}:
            raise ValueError('Colour relationship must say adjacent or separate')
        _text(rel, 'observation')
        key = tuple(sorted(pair))
        if key in seen:
            raise ValueError('Duplicate or contradictory colour relationship')
        seen[key] = rel['relation']
    extensions = value.get('extensions', [])
    base_roles = set(roles)
    cleaned = []
    for ext in extensions:
        if not isinstance(ext, dict) or ext.get('base_role') not in base_roles:
            raise ValueError('Derived colour needs a known base_role')
        if ext.get('relationship') not in {'tint', 'shade', 'tone', 'analogous_neighbour', 'compatible_neutral', 'controlled_contrast'}:
            raise ValueError('Derived colour needs a supported relationship')
        cleaned.append({k: v for k, v in ext.items() if k != 'base_role'})
    checked = _validate_extensions(cleaned, {c['hex'] for c in result['colours']})
    for ext, original in zip(checked, extensions):
        if ext['role'] in base_roles:
            raise ValueError('Derived colour roles must be distinct')
        base_roles.add(ext['role'])
        ext['base_role'] = original['base_role']
    result.update(source_mode='svg-reference', reference=deepcopy(reference),
                  relationships=deepcopy(relationships), extensions=checked)
    return result


def verify_palette_source(palette, root):
    palette = validate_svg_palette(palette)
    actual = svg_source(local_file(root, palette['reference']['path']))
    if actual['sha256'] != palette['reference']['sha256']:
        raise ValueError('Palette SVG source sha256 changed; repeat Director colour review')
    if not {c['hex'] for c in palette['colours']} <= actual['colours']:
        raise ValueError('Palette source swatches do not occur in the actual SVG')
    return palette


def svg_style_lines(style):
    p = style['palette']
    return [
        '## SVG-reference creative workflow',
        'Preserve the full Creative Director role: coherent whole-figure style, creative grouping, colour, frames, arrows, meaningful symbols and local constructions. Add evidence and checks; do not reduce this to filling predetermined cards.',
        'The Director owns the final colour decision. Source swatches below are observations, not an upstream colour lock. No palette-library selection for this run.',
        'Dedicated COMPLETE palette SVG: ' + p['reference']['path'] + '; source track: ' + p['reference']['source_track'],
        'Observed swatches: ' + json.dumps(p['colours']),
        'Observed adjacency/separation: ' + json.dumps(p['relationships']),
        'Available source-derived tints/shades/tones: ' + '; '.join(c['role'] + ' ' + c['hex'] + ' from ' + c['base_role'] + ' as ' + c['relationship'].replace('_',' ') for c in p['extensions']),
        'Retain mature colour rules: usually 1–2 dominant families; analogous light neighbours; deeper meaningful marks; isolate strong contrasting foci. White and readable black typography dominate. No invented universal contrast threshold.',
        'Leave unnecessary surfaces white. A pale base frame may receive colour; important mechanism content may receive emphasis. Titles are ordinary text, never automatic colour strips. Do not recolour every object.',
        'When user colours change, re-evaluate the whole relationship plan with the Director; do not do independent HEX substitutions.',
        'Main style traits: ' + '; '.join(style['borrow']),
        'Avoid: ' + '; '.join(style['avoid']),
        'Resolve content before the Director pass. Director locks colour, then places content-sized base frames and simple routes together, then fills content. Upstream draft geometry is revisable, not a fixed aesthetic.',
        'No staircase or complex detour. Prefer a straight line; a necessary turn/return uses one smooth simple curve. If routing becomes complex, move or regroup frames first. Normally at most one input and one output per frame. Source-grounded multi-port exceptions require an explicit reason and actual internal landing.',
        'Inspect topology beyond arrows: nested/parallel/repeated structures, node degree, merge/split semantics and operators such as addition, multiplication, concatenation or gates. Only include symbols actually supported by this method. Never invent internal modules to resemble a peer.',
        'All text, titles, symbols and images stay inside their parent region with padding. No deep title backgrounds. Keep complete visual-reference language: typography, line character, frames, arrows, density and spacing.',
        'Three design intentions (layout, flow, density): each starts 我想 and has at most 15 Chinese characters, or starts I want and has at most 15 English words. One line each, no commas.',
        'Return a colour decision with chosen palette, rationale, region colours, adjacency review and whitespace plan. Retain the single source SVG and its observed relationships; choose source-derived extensions as needed. Return a topology review explaining supported structures/operators and omissions. These are planning metadata, never figure text.',
    ]


def director_palette(creative, style, root, component_ids):
    decision = creative.get('colour_decision')
    if not isinstance(decision, dict):
        raise ValueError('SVG workflow requires the Creative Director colour_decision')
    chosen = verify_palette_source(decision.get('chosen_palette'), root)
    if chosen['reference'] != style['palette']['reference'] or chosen['colours'] != style['palette']['colours'] or chosen['relationships'] != style['palette']['relationships']:
        raise ValueError('Director palette must retain the inspected source and colour relationships')
    for key in ('rationale', 'adjacency_review', 'whitespace_plan'):
        _text(decision, key)
    regions = decision.get('region_colours')
    if not isinstance(regions, dict) or set(regions) != set(component_ids):
        raise ValueError('Director region_colours must cover every component')
    roles = {c['role'] for c in chosen['colours'] + chosen['extensions']} | {'white', 'black'}
    for region in regions.values():
        if not isinstance(region, list) or not region or not set(region) <= roles:
            raise ValueError('Director region colour roles must belong to the chosen palette')
    _text(creative, 'topology_review')
    intents = creative.get('design_intents')
    if not isinstance(intents, dict) or set(intents) != {'layout', 'flow', 'density'}:
        raise ValueError('Director must retain three design_intents')
    for intent in intents.values():
        if not isinstance(intent, str) or re.search(r'[,，;；。.!！?？\n]', intent) or not ((intent.startswith('我想') and len(intent) <= 15) or (intent.startswith('I want ') and len(intent.split()) <= 15)):
            raise ValueError('Director design_intents must be short first-person single lines')
    return chosen


def simple_degree_check(geometry, routes):
    exceptions = geometry.get('multi_port_exceptions', {})
    for endpoint, description in [('target_id', 'incoming entry'), ('source_id', 'outgoing exit')]:
        for ident, count in Counter(r[endpoint] for r in routes).items():
            if count > 1:
                reason = exceptions.get(ident)
                if not isinstance(reason, str) or not reason.strip():
                    raise ValueError(f'Ordinary frame {ident} has more than one {description}; redesign positions/grouping or document source-grounded exception')
