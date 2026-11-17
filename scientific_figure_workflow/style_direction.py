"""Opt-in style-first direction; no extra model call and no image-rights inference."""
import copy
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

STYLE_CONTRACT = ('Global style anchor: apply the explicitly liked reference traits, such as typography, linework, spacing, colour relationships or arrow treatment, coherently across the figure. State what is borrowed; do not claim to copy the whole reference or its composition. Layout and detail hierarchy come from this Methodology and its innovations. Do not copy source labels, characters or scientific claims. Component references affect only their named target. Active colours come from the selected compatible palette group. White or near-white space and black readable text dominate. Use very pale targeted content tints; leave supporting regions mostly unfilled. Stronger colour marks a mechanism or comparison, not every card. Preserve source-image colours and arrow contrast. Title treatment defaults to bold dark or deliberate theme-coloured text without filled header strips; important scientific content receives the fill. Arrow treatment includes shaft character, head/body proportion, weight, corners and palette role; bold hand-drawn or filled arrows are valid when coherent and clear. Semantic hand-drawn icons and purposeful dividers are allowed; no pasted stickers or meaningless ornaments.')
FAMILIES={'instruction_manual','architecture_2d','concept_led','handdrawn','volumetric_chromatic','story_schematic'}
PATHS={'linear','stages','parallel_merge','s_curve','reverse_s','arc','horizontal','vertical','c_curve','reverse_c','clockwise_spiral','counterclockwise_spiral','main_side_chain','serpentine'}

def _strings(value,label):
    if not isinstance(value,list) or not value or any(not isinstance(v,str) or not v.strip() for v in value):
        raise ValueError(label+' needs nonempty strings')
    return value


def _reference(record,root):
    if not isinstance(record,dict) or not isinstance(record.get('path'),str):raise ValueError('reference needs local input path')
    relative=Path(record['path']);path=(root/relative).resolve(strict=True)
    if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root/'input') or any((root/Path(*relative.parts[:i])).is_symlink() for i in range(1,len(relative.parts)+1)):
        raise ValueError('reference must stay inside input without symlinks')
    try:
        with Image.open(path) as image:image.verify()
    except (OSError,ValueError) as exc:raise ValueError('reference must be a real image') from exc
    if not isinstance(record.get('source'),str) or not record['source'].strip():raise ValueError('reference source required; unresolved is allowed but is not permission')
    normalized=copy.deepcopy(record);normalized['path']=path.relative_to(root).as_posix()
    normalized['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    return normalized


def load_style_brief(root,component_ids=None):
    root=Path(root).resolve();path=root/'input/style-brief.json'
    if not path.exists():return None
    if path.is_symlink() or (root/'input').is_symlink():raise ValueError('style brief/input must not be a symlink')
    d=json.loads(path.read_text());ids=set(component_ids) if component_ids is not None else None
    if not isinstance(d,dict) or d.get('format')!='figfox-style-brief-v1':raise ValueError('unsupported style brief')
    if d.get('family') not in FAMILIES or d.get('reference_mode') not in {'image','traits_only','model_composed'}:raise ValueError('choose a supported style family and reference mode')
    _strings(d.get('borrow'),'borrow');_strings(d.get('avoid'),'avoid')
    roles=_strings(d.get('dominant_roles'),'dominant roles')
    if len(roles)>3 or len(set(roles))!=len(roles):raise ValueError('use1-3 distinct dominant colour roles')
    if len(roles)==3 and not d.get('third_colour_reason'):raise ValueError('third dominant role needs scientific reason')
    for k in ('palette_id','palette_reason','accent_target'):
        if not isinstance(d.get(k),str) or not d[k].strip():raise ValueError(k+' is required')
    mainline=_strings(d.get('mainline'),'mainline component ids')
    if ids is not None and (not set(mainline)<=ids or d['accent_target'] not in ids):raise ValueError('mainline/accent must name real component ids')
    if d.get('reading_path') not in PATHS:raise ValueError('unknown reading path')
    if d.get('stage_labels','none') not in {'none','stage_numbers','parenthesized_letters'}:raise ValueError('Stage labels must be Stage1/2/3 or (a)/(b)/(c)')
    foci=d.get('contrast_foci',[d['accent_target']]);_strings(foci,'contrast foci')
    if len(foci)>2 or len(set(foci))!=len(foci) or (ids is not None and not set(foci)<=ids):raise ValueError('contrast foci require at most two distinct real components')
    if d['accent_target'] not in foci:raise ValueError('accent_target must belong to contrast_foci')
    groups=d.get('proximity_groups',[])
    if not isinstance(groups,list) or any(not isinstance(g,list) or not g or any(not isinstance(i,str) or (ids is not None and i not in ids) for i in g) for g in groups):raise ValueError('proximity groups require known components')
    if len(foci)==2:
        if not d.get('distant_focus_reason') or not groups or not set(foci)<={i for g in groups for i in g}:raise ValueError('two contrast foci require an explicit distant-layout reason and proximity groups')
        if any(set(foci)<=set(g) for g in groups):raise ValueError('two strong contrast foci cannot be adjacent')
    result=copy.deepcopy(d)
    result['contrast_foci']=foci
    ref=d.get('main_reference')
    result['main_reference']=_reference(ref,root) if ref is not None else None
    if d['reference_mode']=='image':
        r=result['main_reference']
        if r is None or r.get('ai_reference_permitted') is not True or not r.get('permission_evidence','').strip():raise ValueError('image reference requires recorded AI-reference permission')
    if d['reference_mode']=='model_composed' and ref is not None:raise ValueError('model-composed mode does not attach another global reference')
    details=d.get('detail_references',[])
    if not isinstance(details,list):raise ValueError('detail references must be a list')
    result['detail_references']=[]
    for item in details:
        if not isinstance(item,dict) or not item.get('target_component_id') or (ids is not None and item['target_component_id'] not in ids):raise ValueError('detail reference needs known target component')
        _strings(item.get('borrow'),'detail borrow');normalized=_reference(item,root)
        if item.get('ai_reference_permitted') is True and not item.get('permission_evidence','').strip():raise ValueError('detail image requires permission evidence')
        result['detail_references'].append(normalized)
    return result


def style_attachments(brief):
    if brief is None:return []
    out=[]
    if brief['reference_mode']=='image':out.append({'path':brief['main_reference']['path'],'role':'style_anchor','contract':STYLE_CONTRACT})
    for ref in brief['detail_references']:
        if ref.get('ai_reference_permitted') is True:
            out.append({'path':ref['path'],'role':'style_component','target_component_id':ref['target_component_id'],'borrow':ref['borrow'],'contract':'Local component style only; subordinate to global style anchor. Change all original content; no pasted source objects.'})
    return out


def style_palette(brief,library):
    group=next((g for g in library if g['id']==brief['palette_id']),None)
    if group is None:raise ValueError('style palette_id must name an approved library group')
    if not set(brief['dominant_roles'])<={c['role'] for c in group['colours']}:raise ValueError('style dominant roles not supplied by group')
    return {'base_palette_id':group['id'],'dominant_colour_roles':brief['dominant_roles'],'colours':copy.deepcopy(group['colours']),'extensions':[]}


def validate_style_palette(brief,palette):
    if brief and (palette['base_palette_id']!=brief['palette_id'] or palette['dominant_colour_roles']!=brief['dominant_roles']):raise ValueError('style palette differs from approved style brief; run select-palette')


def style_lines(brief):
    if brief is None:return []
    return ['## Global style direction (before domain-search aesthetics)',STYLE_CONTRACT,
            'Style brief SHA256: '+hashlib.sha256(json.dumps(brief,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            'Family: '+brief['family']+'; reference mode: '+brief['reference_mode'],
            'Stage labeling: '+{'none':'do not invent stages or panel letters','stage_numbers':'use Stage 1, Stage 2, Stage 3 according to actual stage count','parenthesized_letters':'use (a), (b), (c) according to actual panel count'}[brief.get('stage_labels','none')]+'. No generic numbered badges, emoji or decorative step labels.',
            'Typography follows the main reference consistently; do not default to Times New Roman. Formulas may retain appropriate mathematical notation. No gray microcopy or invented caution notes. Necessary short italic explanations use readable Arial Italic in black or a coherent dark ink. Black is welcome; do not make all text pastel.',
            'Frame and arrow grammar remain consistent. Neighboring base frames use analogous, similarly light fills; at most one local strong contrast focus in each proximity group. Separate far-away regions may carry a second emphasis only when the declared layout justifies their separation.',
            'Use pale support surfaces and deeper main marks, or a reference-supported inverse. Keep saturation and the chosen style coherent.',
            'Declared proximity groups: '+json.dumps(brief.get('proximity_groups',[]))+'; contrast foci: '+', '.join(brief['contrast_foci']),
            'User likes: '+'; '.join(brief['borrow']), 'Avoid: '+'; '.join(brief['avoid']),
            'Reading path: '+brief['reading_path']+'; scientific mainline: '+' -> '.join(brief['mainline']),
            'Keep every scientific edge. Simplify presentation, not scientific meaning. Every arrow has an unambiguous source and destination; add concise relation labels where needed. Arc/S layouts are geometry, not permission to invent cycles; distinguish crossings from junctions.',
            'Palette for this run: '+brief['palette_id']+'. '+brief['palette_reason']+' Example purple/blue/orange hues are illustrative, not a default theme. Select per reference; reuse is allowed. Lock hues only on explicit user request.',
            'Use adjacent/analogous shades for related modules; one contrast family at one semantic emphasis focus: '+brief['accent_target']+'. Distant extra focus, if any, follows the declared proximity plan; related legend marks may repeat that accent. Neutrals and subordinate tints are not additional dominant colours; no gratuitous gradients.',
            *['Local detail for '+r['target_component_id']+': '+'; '.join(r['borrow'])+' (does not change global style)' for r in brief['detail_references']],
            'Style may be imagined within this brief when no approved image exists, during the same Creative Director pass; do not generate an extra style-sheet image.']


def init_style_run(root,family,*,methodology=None,reference=None,source_kind="user_provided",source="user provided; original source unresolved"):
    root=Path(root)
    if root.exists():raise ValueError('run already exists; never overwrite methodology or references')
    family='instruction_manual' if family=='manual' else family
    if family not in FAMILIES:raise ValueError('unsupported style family')
    methodology_text=Path(methodology).read_text() if methodology else '# Methodology\n\nREPLACE_WITH_YOUR_METHODOLOGY\n'
    reference_path=Path(reference).resolve(strict=True) if reference else None
    if reference_path:
        with Image.open(reference_path) as image:image.verify()
    if source_kind not in {'user_provided','figurebench','figfoxbench','web'}:raise ValueError('unsupported reference source kind')
    (root/'input').mkdir(parents=True)
    (root/'input/methodology.md').write_text(methodology_text)
    d={'format':'figfox-style-brief-v1','family':family,'reference_mode':'model_composed','main_reference':None,'borrow':['coherent human-made linework','clear labels and compact spacing'],'avoid':['generic decorative cards'],'palette_id':'REPLACE_WITH_REFERENCE_MATCHED_PALETTE_ID','dominant_roles':['primary','accent'],'palette_reason':'Choose an approved palette group for this reference and explain its hue/saturation/contrast fit; prior demo hues are examples only','accent_target':'REPLACE_WITH_COMPONENT_ID','reading_path':'linear','mainline':['REPLACE_WITH_COMPONENT_ID'],'detail_references':[],'stage_labels':'none','proximity_groups':[]}
    if reference_path:
        target=root/'input'/('main-style-reference'+reference_path.suffix.lower())
        shutil.copyfile(reference_path,target)
        d.update(reference_mode='traits_only',main_reference={'path':target.relative_to(root).as_posix(),'source_kind':source_kind,'source':source,'ai_reference_permitted':False,'permission_evidence':''})
    (root/'input/style-brief.json').write_text(json.dumps(d,indent=2)+'\n')
    return {'run':str(root),'next':'Supply methodology, component ids and style preferences; optionally add a permitted main reference. No model called.'}


def validate_creative_style_attachments(root, expected):
    if load_style_brief(root) is None:return
    path=Path(root)/'creative-director/attachments.json'
    if not path.is_file() or path.is_symlink() or json.loads(path.read_text())!=expected:
        raise ValueError('Creative Director style attachments missing or differ from compiled brief')
