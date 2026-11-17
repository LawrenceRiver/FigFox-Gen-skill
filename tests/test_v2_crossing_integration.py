"""A valid V2 crossing reaches the image packet without changing its inputs."""
import copy
import json
import unittest

from scientific_figure_workflow.prompts import build_prompt1_bundle
from tests import test_generation_checklist as checklist_fixtures
from tests import test_style_prompt_integration as style_fixtures


class V2CrossingIntegrationTests(unittest.TestCase):
    setUp = style_fixtures.PromptIntegrationTests.setUp
    tearDown = style_fixtures.PromptIntegrationTests.tearDown

    def test_distinct_ink_crossing_reaches_bundle_without_input_mutation(self):
        for ident in ('middle', 'end'):
            component = copy.deepcopy(self.c2['components'][0])
            component.update(id=ident, label=ident.title())
            self.c2['components'].append(component)
            self.c3['coverage_matrix'].append({
                'component_id': ident,
                'basic_geometry_justification': 'rectangle',
            })
        self.c2['relationships'].append({
            'source_id': 'middle', 'target_id': 'end', 'label': 'supports',
        })
        plan = checklist_fixtures.GenerationChecklistTests.plan(self)
        plan.update(
            format='figfox-generation-plan-v2',
            placements=[{'component_id': ident, 'placement': 'grid'}
                        for ident in ('input', 'output', 'middle', 'end')],
            routing_geometry={
                'canvas': [600, 400],
                'columns': [[40, 140], [240, 340], [440, 540]],
                'rows': [[40, 120], [240, 320]],
                'slots': {'input': [0, 0, 1, 1], 'output': [0, 2, 1, 1],
                          'middle': [0, 1, 1, 1], 'end': [1, 1, 1, 1]},
                'crossings': [{
                    'routes': [0, 1], 'point': [290, 180],
                    'treatment': 'distinct_ink', 'reason': 'Separate flows',
                }],
            },
            routes=[{
                'source_id': 'input', 'target_id': 'output', 'label': 'encodes',
                'source_port': 'south', 'target_port': 'south',
                'via': 'separate arrow', 'route_kind': 'branch',
                'points': [[100, 120], [100, 180], [480, 180], [480, 120]],
            }, {
                'source_id': 'middle', 'target_id': 'end', 'label': 'supports',
                'source_port': 'south', 'target_port': 'north',
                'via': 'separate arrow', 'route_kind': 'mainline',
                'points': [[290, 120], [290, 240]],
            }],
        )
        path = self.root / 'input/generation-plan.json'
        path.write_text(json.dumps(plan))
        original_file = path.read_bytes()
        original_inputs = copy.deepcopy((plan, self.c1, self.c2, self.c3))

        bundle = build_prompt1_bundle(
            'Input encodes Output; Middle supports End.',
            self.c1, self.c2, self.c3, None, self.root,
        )

        self.assertIn(
            'Declared crossing of routes [0, 1] at [290, 180]: distinct ink; Separate flows',
            bundle['prompt'],
        )
        self.assertNotIn('distinct_ink', bundle['prompt'])
        self.assertIn('[[100, 120], [100, 180], [480, 180], [480, 120]]', bundle['prompt'])
        self.assertIn('[[290, 120], [290, 240]]', bundle['prompt'])
        self.assertEqual((plan, self.c1, self.c2, self.c3), original_inputs)
        self.assertEqual(path.read_bytes(), original_file)
