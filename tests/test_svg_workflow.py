import copy, hashlib, json, tempfile, unittest
from pathlib import Path
from PIL import Image
from scientific_figure_workflow.palette import validate_palette
from scientific_figure_workflow.style_direction import load_style_brief
from scientific_figure_workflow.routing_geometry import compile_routing_geometry
from scientific_figure_workflow.artifacts import validate_web_manifest

SVG='<svg xmlns="http://www.w3.org/2000/svg" width="300" height="160"><rect id="base" width="180" height="100" fill="#DDEEFF"/><circle id="focus" cx="230" cy="80" r="30" fill="#AA4455"/></svg>'
def palette():
 return dict(source_mode='svg-reference',base_palette_id='svg-paper-a',dominant_colour_roles=['primary','accent'],colours=[dict(role='primary',hex='#DDEEFF',rgb=[221,238,255]),dict(role='accent',hex='#AA4455',rgb=[170,68,85])],extensions=[],reference=dict(path='input/palette.svg',sha256=hashlib.sha256(SVG.encode()).hexdigest(),source_url='https://example.org/paper',evidence_url='https://example.org/figure.svg',source_track='protein design',target_track='world models',complete_figure=True),relationships=[dict(roles=['primary','accent'],relation='separate',observation='Strong accent is isolated from the other coloured region.')])
def style():
 return dict(format='figfox-style-brief-v1',workflow_policy='svg-reference-v1',family='architecture_2d',reference_mode='traits_only',main_reference=None,borrow=['rounded frames'],avoid=['steps'],palette_id='svg-paper-a',dominant_roles=['primary','accent'],accent_target='b',palette_reason='Director will decide using complete source SVG.',reading_path='horizontal',mainline=['a','b'],detail_references=[],palette=palette())
class SvgWorkflowTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'input').mkdir();(self.root/'input/palette.svg').write_text(SVG)
 def tearDown(self):self.tmp.cleanup()
 def load(self,s):
  (self.root/'input/style-brief.json').write_text(json.dumps(s));return load_style_brief(self.root,{'a','b'})
 def test_svg_palette_is_valid_without_a_library_group(self):
  self.assertEqual(validate_palette(palette(),[])['source_mode'],'svg-reference')
 def test_svg_palette_rejects_unexplained_colour_relation(self):
  p=palette();p['relationships'][0]['observation']=''
  with self.assertRaisesRegex(ValueError,'observation'):validate_palette(p,[])
 def test_svg_style_checks_real_source_and_sampled_colours(self):
  self.assertEqual(self.load(style())['palette']['reference']['path'],'input/palette.svg')
  (self.root/'input/palette.svg').write_text(SVG.replace('#AA4455','#AA4456'))
  with self.assertRaisesRegex(ValueError,'hash|sha256|source'):self.load(style())
 def test_raster_renamed_to_svg_is_not_a_valid_colour_reference(self):
  Image.new('RGB',(10,10)).save(self.root/'input/palette.svg',format='PNG')
  with self.assertRaisesRegex(ValueError,'SVG|svg'):self.load(style())
 def test_embedded_raster_and_same_track_palette_are_rejected(self):
  s=style();s['palette']['reference']['source_track']='world models'
  with self.assertRaisesRegex(ValueError,'track'):self.load(s)
  (self.root/'input/palette.svg').write_text(SVG.replace('</svg>','<image href="data:image/png;base64,AAAA"/></svg>'))
  with self.assertRaisesRegex(ValueError,'raster|image'):self.load(style())
 def test_svg_only_manifest_rejects_raster_reference_even_with_svg_metadata(self):
  folder=self.root/'references/web/crops';folder.mkdir(parents=True)
  records=[]
  for i in range(2):
   Image.new('RGB',(10,10)).save(folder/f'{i}.png')
   records.append(dict(id=str(i),title='paper',figure='figure',source_url=f'https://example.org/paper{i}',evidence_url=f'https://example.org/{i}.svg',crop_path=f'references/web/crops/{i}.png',inspection='view',source_format='svg'))
  c1=dict(domain='worlds',dominant_colour_count=2,mainline='a to b',reference_policy='svg-only',conventions=[dict(concept='frames',recurrence_evidence='two papers',visual_treatment='sequence',terminology='frames',methodology_relevance='live frames')])
  with self.assertRaisesRegex(ValueError,'SVG|svg'):validate_web_manifest(dict(format='scholarly-domain-figure-manifest-v1',sources=records),self.root,c1,minimum_sources=2)
 def geometry(self):return dict(canvas=[800,500],columns=[[40,240],[440,760]],rows=[[100,300]],slots={'a':[0,0,1,1],'b':[0,1,1,1]},routing_policy='simple')
 def route(self):return dict(source_id='a',target_id='b',source_port='east',target_port='west',route_kind='mainline',points=[[240,200],[440,200]])
 def test_simple_policy_accepts_one_smooth_return_arc(self):
  r=dict(source_id='b',target_id='a',source_port='south',target_port='south',route_kind='feedback',curve='cubic',points=[[600,300],[600,450],[140,450],[140,300]])
  g,routes=compile_routing_geometry(self.geometry(),[self.route(),r],['a','b']);self.assertEqual(routes[1]['curve'],'cubic')
 def test_simple_policy_rejects_staircase_instead_of_adding_a_detour(self):
  r=self.route();r.update(route_kind='branch',points=[[240,180],[340,180],[340,240],[440,240]])
  with self.assertRaisesRegex(ValueError,'stair|simple|curve'):compile_routing_geometry(self.geometry(),[r],['a','b'])
 def test_simple_policy_rejects_unexplained_double_entry(self):
  r=self.route();r['points']=[[240,240],[440,240]]
  with self.assertRaisesRegex(ValueError,'entry|incoming|one input'):compile_routing_geometry(self.geometry(),[self.route(),r],['a','b'])
 def test_svg_source_rejects_external_css_that_escapes_source_hash(self):
  from scientific_figure_workflow.svg_workflow import svg_source
  for css in ['@import url("https://example.org/colour.css");','rect {fill:url(https://example.org/paint.svg#colour)}']:
   p=self.root/'external.svg';p.write_text(SVG.replace('</svg>','<style>'+css+'</style></svg>'))
   with self.assertRaisesRegex(ValueError,'self-contained|external'):svg_source(p)
 def test_simple_routes_validate_caption_bounds_and_node_overlap(self):
  for box in [[100,100,200,200],[-10,200,30,20],'invalid']:
   r=self.route();r.update(caption='encodes',caption_box=box)
   with self.assertRaisesRegex(ValueError,'caption|Caption'):compile_routing_geometry(self.geometry(),[r],['a','b'])

class DirectorHandoffTests(unittest.TestCase):
 def test_final_image_compiler_requires_real_director_colour_decision(self):
  from tests.test_style_prompt_integration import PromptIntegrationTests
  from scientific_figure_workflow.prompts import build_prompt1_bundle, _default_creative_director
  fixture=PromptIntegrationTests();fixture.setUp()
  try:
   (fixture.root/'input/palette.svg').write_text(SVG)
   s=style();s.update(accent_target='output',mainline=['input','output']);(fixture.root/'input/style-brief.json').write_text(json.dumps(s))
   fixture.c3.update(reference_strategy='essential-only',selected_references=[],coverage_matrix=[dict(component_id=i,basic_geometry_justification='native') for i in ['input','output']],palette=palette())
   with self.assertRaisesRegex(ValueError,'Creative Director colour_decision'):
    build_prompt1_bundle('Input encodes Output.',fixture.c1,fixture.c2,fixture.c3,None,fixture.root)
   creative=_default_creative_director(fixture.c2)
   creative.update(colour_decision=dict(chosen_palette=palette(),rationale='Reference warm and cool balance.',region_colours={'input':['white'],'output':['accent']},adjacency_review='Strong focus isolated.',whitespace_plan='Leave support white.'),topology_review='Only one directed relationship is supported.',design_intents=dict(layout='我想两框左右排布',flow='我想主线直接向右',density='我想保留充分留白'))
   plan=dict(format='figfox-generation-plan-v2',scientific_summary='Input encodes output.',layout='Two frames aligned.',typography='Arial',invariants=['One directed scientific relation.'],placements=[dict(component_id=i,placement='aligned') for i in ['input','output']],routes=[dict(source_id='input',target_id='output',label='encodes',source_port='east',target_port='west',via='straight',route_kind='mainline',points=[[240,200],[440,200]])],routing_geometry=dict(canvas=[800,500],columns=[[40,240],[440,760]],rows=[[100,300]],slots={'input':[0,0,1,1],'output':[0,1,1,1]},routing_policy='simple'))
   (fixture.root/'input/generation-plan.json').write_text(json.dumps(plan))
   b=build_prompt1_bundle('Input encodes Output.',fixture.c1,fixture.c2,fixture.c3,None,fixture.root,creative)
   self.assertIn('Director colour rationale',b['prompt']);self.assertIn('Strong focus isolated.',b['prompt'])
   self.assertNotIn('Use only this palette group',b['prompt'])
   (fixture.root/'input/palette.svg').write_text(SVG.replace('#AA4455','#123456'))
   with self.assertRaisesRegex(ValueError,'sha256'):
    build_prompt1_bundle('Input encodes Output.',fixture.c1,fixture.c2,fixture.c3,None,fixture.root,creative)
  finally:fixture.tearDown()
