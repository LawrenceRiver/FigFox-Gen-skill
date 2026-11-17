import copy,json,tempfile,unittest
from pathlib import Path
from PIL import Image

class StyleDirectionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'input').mkdir()
  Image.new('RGB',(100,50),'white').save(self.root/'input/main-style-reference.png')
  self.brief={'format':'figfox-style-brief-v1','family':'handdrawn','reference_mode':'traits_only','main_reference':{'path':'input/main-style-reference.png','source':'user-provided;original unresolved','ai_reference_permitted':False,'permission_evidence':''},'borrow':['handwritten annotation','clear hand-drawn arrows'],'avoid':['generic card grids'],'palette_id':'workflow-role-01','dominant_roles':['primary','accent'],'accent_target':'output','palette_reason':'Cool base and one warm emphasis','reading_path':'parallel_merge','mainline':['input','output'],'detail_references':[]}
 def tearDown(self):self.tmp.cleanup()
 def load(self,b=None):
  from scientific_figure_workflow.style_direction import load_style_brief
  (self.root/'input/style-brief.json').write_text(json.dumps(b or self.brief));return load_style_brief(self.root,{'input','output'})
 def test_traits_only_does_not_attach_unapproved_source(self):
  from scientific_figure_workflow.style_direction import style_attachments,style_lines
  brief=self.load();self.assertEqual(style_attachments(brief),[]);self.assertIn('handwritten annotation','\n'.join(style_lines(brief)))
 def test_full_reference_requires_recorded_permission(self):
  b=copy.deepcopy(self.brief);b['reference_mode']='image'
  with self.assertRaisesRegex(ValueError,'permission'):self.load(b)
  b['main_reference'].update(ai_reference_permitted=True,permission_evidence='Author permission for AI reference,2026-11-17')
  from scientific_figure_workflow.style_direction import style_attachments
  a=style_attachments(self.load(b));self.assertEqual(a[0]['role'],'style_anchor')
 def test_detail_reference_requires_target_and_cannot_become_global(self):
  b=copy.deepcopy(self.brief);b['detail_references']=[dict(b['main_reference'],target_component_id='missing',borrow=['linework'])]
  with self.assertRaisesRegex(ValueError,'component'):self.load(b)
 def test_palette_selection_follows_style_not_random_or_domain_count(self):
  from scientific_figure_workflow.style_direction import style_palette
  library=json.loads((Path(__file__).resolve().parents[1]/'references/palette-library.json').read_text())['palettes']
  p=style_palette(self.load(),library);self.assertEqual(p['base_palette_id'],'workflow-role-01');self.assertEqual(p['dominant_colour_roles'],['primary','accent'])
 def test_overcomplex_palette_and_unknown_mainline_block(self):
  b=copy.deepcopy(self.brief);b['dominant_roles']=['primary','accent','secondary','ink']
  with self.assertRaises(ValueError):self.load(b)
  b=copy.deepcopy(self.brief);b['mainline']=['invented']
  with self.assertRaisesRegex(ValueError,'component'):self.load(b)
 def test_safe_intake_never_overwrites_methodology(self):
  from scientific_figure_workflow.style_direction import init_style_run
  r=self.root/'fresh';init_style_run(r,'handdrawn')
  self.assertTrue((r/'input/methodology.md').exists());self.assertTrue((r/'input/style-brief.json').exists())
  with self.assertRaisesRegex(ValueError,'exists'):init_style_run(r,'manual')
 def test_plain_text_file_cannot_be_an_image_anchor(self):
  (self.root/'input/main-style-reference.png').write_text('not an image')
  with self.assertRaises(ValueError):self.load()

if __name__=='__main__':unittest.main()

class ExtendedStyleTests(unittest.TestCase):
 setUp=StyleDirectionTests.setUp
 tearDown=StyleDirectionTests.tearDown
 load=StyleDirectionTests.load
 def test_story_and_volumetric_families_and_routes(self):
  for family in ['volumetric_chromatic','story_schematic']:
   for route in ['horizontal','vertical','c_curve','reverse_c','clockwise_spiral','counterclockwise_spiral','main_side_chain','serpentine']:
    b=copy.deepcopy(self.brief);b.update(family=family,reading_path=route)
    self.assertEqual(self.load(b)['family'],family)
 def test_stage_labels_and_typography_policy(self):
  from scientific_figure_workflow.style_direction import style_lines
  b=copy.deepcopy(self.brief);b['stage_labels']='badge_numbers'
  with self.assertRaisesRegex(ValueError,'Stage'):self.load(b)
  b['stage_labels']='parenthesized_letters';lines='\n'.join(style_lines(self.load(b)))
  self.assertIn('Arial Italic',lines);self.assertIn('Times New Roman',lines);self.assertIn('gray microcopy',lines)
 def test_two_contrast_foci_must_be_distant_not_in_same_neighbor_group(self):
  b=copy.deepcopy(self.brief);b.update(contrast_foci=['input','output'])
  with self.assertRaisesRegex(ValueError,'distant'):self.load(b)
  b.update(distant_focus_reason='Opposite ends of the planned canvas',proximity_groups=[['input','output']])
  with self.assertRaisesRegex(ValueError,'adjacent'):self.load(b)
  b['proximity_groups']=[['input'],['output']];self.assertEqual(len(self.load(b)['contrast_foci']),2)

class AccentConsistencyTests(unittest.TestCase):
 setUp=StyleDirectionTests.setUp
 tearDown=StyleDirectionTests.tearDown
 load=StyleDirectionTests.load
 def test_accent_target_must_be_one_of_declared_foci(self):
  b=copy.deepcopy(self.brief);b['contrast_foci']=['input']
  with self.assertRaisesRegex(ValueError,'accent_target'):self.load(b)

class IntakeSourceTests(unittest.TestCase):
 def test_figfoxbench_reference_is_copied_locally_without_assuming_permission(self):
  from scientific_figure_workflow.style_direction import init_style_run
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);m=root/'m.md';m.write_text('True methodology.');image=root/'bench.png';Image.new('RGB',(20,10),'white').save(image)
   run=root/'run';init_style_run(run,'architecture_2d',methodology=m,reference=image,source_kind='figfoxbench',source='sample-0001;original rights unresolved')
   b=json.loads((run/'input/style-brief.json').read_text());self.assertEqual(b['main_reference']['source_kind'],'figfoxbench');self.assertFalse(b['main_reference']['ai_reference_permitted']);self.assertEqual((run/'input/methodology.md').read_text(),m.read_text())
