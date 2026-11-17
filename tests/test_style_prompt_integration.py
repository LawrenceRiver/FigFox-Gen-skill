import json,tempfile,unittest
from pathlib import Path
from PIL import Image
from scientific_figure_workflow.prompts import build_prompt1_bundle,build_creative_director_prompt,validate_prompt_bundle
from scientific_figure_workflow.style_direction import load_style_brief,style_palette

class PromptIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'input').mkdir()
  self.c1={'domain':'test scientific pipeline','mainline':'input to output','dominant_colour_count':4,'conventions':[{'concept':'block','recurrence_evidence':'Fixture evidence only','visual_treatment':'rectangle','terminology':'block','methodology_relevance':'method'}]}
  self.c2={'mainline':'input to output','components':[{'id':i,'label':i.title(),'semantic_role':i,'visual_treatment':'simple rectangle','construction_provenance':'basic geometry','source_context':'methodology','special':'no'} for i in ['input','output']],'relationships':[{'source_id':'input','target_id':'output','label':'encodes'}]}
  selections=[]
  for i in [1,2]:
   p=f'references/figurebench/crops/ref{i}.png';(self.root/p).parent.mkdir(parents=True,exist_ok=True);Image.new('RGB',(10,10),'white').save(self.root/p)
   selections.append({'crop_id':f'c{i}','reference_id':f'r{i}','crop_path':p,'target_component_id':'input','crop_contract':{'borrow':['stroke geometry'],'must_change':['source content'],'human_editable_reason':'basic lines'}})
  library=json.loads((Path(__file__).resolve().parents[1]/'references/palette-library.json').read_text())['palettes']
  self.style={'format':'figfox-style-brief-v1','family':'handdrawn','reference_mode':'image','main_reference':{'path':'input/main.png','source':'Own synthetic fixture','ai_reference_permitted':True,'permission_evidence':'Test-generated image'},'borrow':['handwritten annotations','clear arrows'],'avoid':['decorative cards'],'palette_id':'workflow-role-01','dominant_roles':['primary','accent'],'palette_reason':'Cool base,warm emphasis','accent_target':'output','reading_path':'parallel_merge','mainline':['input','output'],'detail_references':[]}
  Image.new('RGB',(20,10),'white').save(self.root/'input/main.png')
  (self.root/'input/style-brief.json').write_text(json.dumps(self.style))
  self.c3={'selected_references':selections,'coverage_matrix':[{'component_id':'input','crop_ids':['c1','c2']},{'component_id':'output','basic_geometry_justification':'rectangle'}],'palette':style_palette(self.style,library),'taste_constraints':['clear and restrained']}
 def tearDown(self):self.tmp.cleanup()
 def bundle(self):return build_prompt1_bundle('Input is encoded to Output.',self.c1,self.c2,self.c3,None,self.root)
 def test_global_image_role_and_style_count_reach_prompt_and_validator(self):
  b=self.bundle();self.assertEqual(len([a for a in b['attachments'] if a['role']=='style_anchor']),1)
  self.assertIn('handwritten annotations',b['prompt']);self.assertNotIn('established 4 dominant',b['prompt']);self.assertNotIn('Hard first-pass prohibition: never draw an upper title-band',b['prompt'])
  validate_prompt_bundle(b,self.root)
 def test_both_stages_receive_same_main_style(self):
  style=load_style_brief(self.root,{'input','output'});b=build_creative_director_prompt('Input to Output.',self.c1,self.c2,self.c3,style)
  self.assertIn('Global style anchor',b['prompt']);self.assertEqual(b['attachments'][0]['role'],'style_anchor')
 def test_local_image_has_target_and_does_not_become_second_global_anchor(self):
  detail=dict(self.style['main_reference'],target_component_id='input',borrow=['node linework']);self.style['detail_references']=[detail]
  (self.root/'input/style-brief.json').write_text(json.dumps(self.style));b=self.bundle();validate_prompt_bundle(b,self.root)
  self.assertEqual([a['role'] for a in b['attachments']].count('style_anchor'),1);self.assertEqual([a for a in b['attachments'] if a['role']=='style_component'][0]['target_component_id'],'input')
 def test_legacy_run_without_brief_keeps_original_reference_contract(self):
  (self.root/'input/style-brief.json').unlink();b=build_prompt1_bundle('Input to Output.',self.c1,self.c2,self.c3,'input/main.png',self.root)
  self.assertIn('Reference-fidelity lock',b['prompt']);validate_prompt_bundle(b,self.root)
 def test_unnamed_scientific_edge_blocks_style_run(self):
  self.c2['relationships'][0].pop('label')
  with self.assertRaisesRegex(ValueError,'arrow labels'):self.bundle()
 def test_changed_source_invalidates_compiled_style_fingerprint(self):
  before=self.bundle();Image.new('RGB',(20,10),'blue').save(self.root/'input/main.png');after=self.bundle()
  self.assertNotEqual(before['prompt'],after['prompt'])

if __name__=='__main__':unittest.main()

class CreativeCLIIntegrationTests(unittest.TestCase):
 setUp=PromptIntegrationTests.setUp
 tearDown=PromptIntegrationTests.tearDown
 def test_creative_cli_persists_real_reference_attachments(self):
  import subprocess,sys
  (self.root/'context').mkdir();(self.root/'input/methodology.md').write_text('Input is encoded to Output.')
  for i,c in enumerate([self.c1,self.c2,self.c3],1):
   name=['domain-conventions','content-visual-plan','visual-kit'][i-1]
   (self.root/f'context/context-{i}-{name}.json').write_text(json.dumps(c))
  script=Path(__file__).resolve().parents[1]/'scripts/figure_workflow.py'
  result=subprocess.run([sys.executable,str(script),'build-creative-director-prompt','--run',str(self.root)],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stderr)
  attached=json.loads((self.root/'creative-director/attachments.json').read_text())
  self.assertEqual(attached[0]['path'],'input/main.png');self.assertIn('attachments',json.loads(result.stdout))

class PromptBudgetTests(unittest.TestCase):
 def test_compaction_preserves_context_values_and_scientific_edges(self):
  import re
  from scientific_figure_workflow.prompts import _fit_style_prompt
  context={'components':[{'id':str(i),'label':'Scientific label','visual_treatment':'Flat native geometry'} for i in range(170)],'relationships':[{'source_id':'0','target_id':'169','label':'feedback'}]}
  original=json.dumps(context,indent=2)
  redundant='\n'.join(['Duplicate component mapping']*800)
  prompt='BEGIN NORMALIZED CONTEXT 2 JSON\n'+original+'\nEND NORMALIZED CONTEXT 2 JSON\n## 2. Exact block and structure names\n'+redundant+'\n## 3. Semantic relationships and reading order\n0 -> 169: feedback\n## 4. Content-to-visual mapping for every element\nComplete mapping retained'
  self.assertGreater(len(prompt),32000)
  compact=_fit_style_prompt(prompt)
  self.assertLessEqual(len(compact),32000)
  evidence=re.search(r'BEGIN NORMALIZED CONTEXT 2 JSON\n(.*?)\nEND NORMALIZED CONTEXT 2 JSON',compact,re.S)[1]
  self.assertEqual(json.loads(evidence),context)
  self.assertIn('0 -> 169: feedback',compact)
  self.assertIn('Complete mapping retained',compact)
 def test_irreducible_overflow_stops_before_model_submission(self):
  from scientific_figure_workflow.prompts import _fit_style_prompt
  with self.assertRaisesRegex(ValueError,'exceeds 32000'):_fit_style_prompt('scientific content '*2000)
