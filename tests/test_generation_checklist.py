import json
import unittest
from tests import test_style_prompt_integration as fixtures
from scientific_figure_workflow.prompts import build_prompt1_bundle, build_creative_director_prompt
from scientific_figure_workflow.style_direction import load_style_brief

class GenerationChecklistTests(unittest.TestCase):
    setUp = fixtures.PromptIntegrationTests.setUp
    tearDown = fixtures.PromptIntegrationTests.tearDown

    def plan(self):
        return {'format':'figfox-generation-plan-v1',
                'scientific_summary':'Input is encoded to Output; no model-weight update.',
                'layout':'Landscape; Input left, Output right.',
                'typography':'Arial, consistent dark labels; no gray microcopy.',
                'invariants':['No model-weight update.'],
                'placements':[{'component_id':i,'placement':p} for i,p in [('input','left'),('output','right')]],
                'routes':[{'source_id':'input','target_id':'output','label':'encodes','source_port':'east','target_port':'west','via':'direct separate arrow'}],
                'local_visuals':[{'target_component_id':'input','meaning':'source document', 'construction':'Folded page icon with PDF text; no brand logo.', 'basis':'Native rectangle, polygon and text.'}]}

    def save(self,plan):
        (self.root/'input/generation-plan.json').write_text(json.dumps(plan))

    def bundle(self):
        return build_prompt1_bundle('Input encodes Output. INTERNAL_SEARCH_NOTE: lengthy retrieval notes.',self.c1,self.c2,self.c3,None,self.root)

    def test_compiles_one_checklist_and_discards_retrieval_prose(self):
        self.save(self.plan());self.c1['conventions'][0]['recurrence_evidence']='INTERNAL_SEARCH_NOTE: '+('irrelevant retrieval details '*2000)
        prompt=self.bundle()['prompt']
        self.assertNotIn('INTERNAL_SEARCH_NOTE',prompt)
        self.assertNotIn('BEGIN NORMALIZED',prompt)
        self.assertIn('input.east -> output.west',prompt)
        self.assertIn('Folded page icon',prompt)
        self.assertIn('No model-weight update.',prompt)
        self.assertLess(len(prompt),12000)
        for c in self.c2['components']:self.assertIn(c['label'],prompt)

    def test_missing_edge_route_is_rejected(self):
        plan=self.plan();plan['routes']=[];self.save(plan)
        with self.assertRaisesRegex(ValueError,'every scientific relationship'):self.bundle()

    def test_invented_edge_is_rejected(self):
        plan=self.plan();plan['routes'].append(dict(plan['routes'][0],source_id='output',target_id='input'));self.save(plan)
        with self.assertRaisesRegex(ValueError,'every scientific relationship'):self.bundle()

    def test_duplicate_component_placement_is_rejected(self):
        plan=self.plan();plan['placements'].append(plan['placements'][0]);self.save(plan)
        with self.assertRaisesRegex(ValueError,'placement'):self.bundle()

    def test_visual_for_nonexistent_component_is_rejected(self):
        plan=self.plan();plan['local_visuals'][0]['target_component_id']='absent';self.save(plan)
        with self.assertRaisesRegex(ValueError,'local visual'):self.bundle()

    def test_source_change_invalidates_compiled_checklist(self):
        self.save(self.plan());before=self.bundle()['prompt'];self.c1['conventions'][0]['recurrence_evidence']='New inspected evidence'
        self.assertNotEqual(before,self.bundle()['prompt'])

    def test_endpoint_changes_invalidate_routes(self):
        self.save(self.plan());self.c2['relationships'][0]['label']='different relation'
        with self.assertRaisesRegex(ValueError,'every scientific relationship'):self.bundle()

    def test_route_aliases_are_normalized_for_rendering(self):
        plan=self.plan();route=plan['routes'][0]
        route['source']=route.pop('source_id');route['target']=route.pop('target_id');self.save(plan)
        self.assertIn('input.east -> output.west',self.bundle()['prompt'])

    def test_director_receives_same_compact_routing_and_insets(self):
        from scientific_figure_workflow.generation_checklist import load_generation_plan
        self.save(self.plan());plan=load_generation_plan(self.root,self.c2)
        b=build_creative_director_prompt('INTERNAL_SEARCH_NOTE: source text',self.c1,self.c2,self.c3,load_style_brief(self.root),plan)
        self.assertIn('input.east -> output.west',b['prompt'])
        self.assertIn('Folded page icon',b['prompt'])
        self.assertNotIn('INTERNAL_SEARCH_NOTE',b['prompt'])
        self.assertEqual(b['attachments'][0]['role'],'style_anchor')

    def test_reference_instructions_follow_written_manifest_order(self):
        from scientific_figure_workflow.prompts import validate_prompt_bundle
        from PIL import Image
        crop='references/web/crops/domain.png';(self.root/crop).parent.mkdir(parents=True)
        Image.new('RGB',(10,10),'white').save(self.root/crop)
        self.c1['conventions'][0]['eligible_source_crops']=[{'path':crop,'target_component_id':'input','borrow':['geometry'],'must_change':['labels']}]
        self.save(self.plan())
        bundle=self.bundle();written=validate_prompt_bundle(bundle,self.root)['attachments']
        section=bundle['prompt'].split('## Scoped image references')[1].split('## Palette')[0]
        positions=[section.index(item['path']) for item in written]
        self.assertEqual(positions,sorted(positions))

    def test_explicit_reference_selection_keeps_only_needed_model_images(self):
        plan=self.plan();plan['attached_reference_paths']=['input/main.png'];self.save(plan)
        b=self.bundle();self.assertEqual([a['path'] for a in b['attachments']],['input/main.png'])

    def test_reference_selection_cannot_drop_main_or_invent_path(self):
        plan=self.plan();plan['attached_reference_paths']=['references/figurebench/crops/ref1.png'];self.save(plan)
        with self.assertRaisesRegex(ValueError,'style reference'):self.bundle()
        plan['attached_reference_paths']=['input/main.png','input/nonexistent.png'];self.save(plan)
        with self.assertRaisesRegex(ValueError,'unknown reference'):self.bundle()

    def test_declared_visual_need_cannot_be_silently_skipped(self):
        plan=self.plan();plan['visual_needs']=[{'id':'v-input','need':'document input','methodology_evidence':'Input is a document','peer_evidence':'Two inspected peer figures show source pages'}];self.save(plan)
        with self.assertRaisesRegex(ValueError,'visual need'):self.bundle()

    def test_correspondence_covers_declared_needs_and_carries_anchor(self):
        plan=self.plan();plan['visual_needs']=[{'id':'v-input','need':'document input','methodology_evidence':'Input is a document','peer_evidence':'Two inspected peer figures show source pages'}];plan['local_visuals'][0]['need_id']='v-input';self.save(plan)
        p=self.bundle()['prompt'];self.assertIn('v-input',p);self.assertIn('Two inspected peer figures',p)
        plan['local_visuals'][0]['need_id']='unknown';self.save(plan)
        with self.assertRaisesRegex(ValueError,'visual need'):self.bundle()

    def test_innovation_hierarchy_rejects_unknown_focus(self):
        plan=self.plan();plan['detail_hierarchy']={'innovation_focuses':[{'claim':'new operator','component_ids':['absent'],'draw_to':'operation'}],'common_depth':'input/output black boxes','keep_whole':['input']};self.save(plan)
        with self.assertRaisesRegex(ValueError,'innovation'):self.bundle()

    def test_hierarchy_reaches_drawing_packet(self):
        plan=self.plan();plan['detail_hierarchy']={'innovation_focuses':[{'claim':'new output operator','component_ids':['output'],'draw_to':'native operation and result'}],'common_depth':'ordinary input/output boundaries','keep_whole':['input']};self.save(plan)
        p=self.bundle()['prompt'];self.assertIn('native operation and result',p);self.assertIn('ordinary input/output boundaries',p)

    def test_compact_route_can_stop_after_two_inspected_peers(self):
        from PIL import Image
        from scientific_figure_workflow.artifacts import validate_web_manifest
        sources=[]
        for i in range(2):
            path=f'references/web/crops/peer{i}.png';(self.root/path).parent.mkdir(parents=True,exist_ok=True);Image.new('RGB',(10,10),'white').save(self.root/path)
            sources.append({'id':f'peer{i}','title':f'Peer {i}','figure':'Figure 1','source_url':f'https://example.org/paper{i}','evidence_url':f'https://example.org/paper{i}','crop_path':path,'inspection':'Synthetic source-contract fixture, not real research.'})
        manifest={'format':'scholarly-domain-figure-manifest-v1','sources':sources}
        with self.assertRaisesRegex(ValueError,'3 or 4'):validate_web_manifest(manifest,self.root,self.c1)
        self.assertEqual(len(validate_web_manifest(manifest,self.root,self.c1,minimum_sources=2)['sources']),2)

    def test_display_labels_shorten_internal_stage_names_without_changing_source(self):
        self.c2['components'][0]['label']='G1: internal paired inspection stage'
        plan=self.plan();plan['display_labels']={'input':'Visual Inspection'};self.save(plan)
        prompt=self.bundle()['prompt']
        self.assertIn('Visual Inspection',prompt)
        self.assertNotIn('G1: internal paired inspection stage',prompt)
        self.assertEqual(self.c2['components'][0]['label'],'G1: internal paired inspection stage')
        from scientific_figure_workflow.generation_checklist import load_generation_plan
        director=build_creative_director_prompt('Source method',self.c1,self.c2,self.c3,load_style_brief(self.root),load_generation_plan(self.root,self.c2))
        self.assertIn('Visual Inspection',director['prompt'])
        self.assertNotIn('G1: internal paired inspection stage',director['prompt'])

    def test_display_labels_reject_unknown_targets_and_empty_captions(self):
        plan=self.plan();plan['display_labels']={'absent':'Inspect'};self.save(plan)
        with self.assertRaisesRegex(ValueError,'display label'):self.bundle()
        plan['display_labels']={'input':'  '};self.save(plan)
        with self.assertRaisesRegex(ValueError,'display label'):self.bundle()
