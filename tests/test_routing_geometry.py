"""Deterministic geometry contracts, independent of rendering."""
import copy
import unittest


class RoutingGeometryTests(unittest.TestCase):
    def compile(self, geometry, routes):
        from scientific_figure_workflow.routing_geometry import compile_routing_geometry
        return compile_routing_geometry(geometry, routes, list(geometry['slots']))

    def grid(self):
        return dict(canvas=[600, 400], columns=[[40, 140], [240, 340], [440, 540]],
                    rows=[[40, 120], [240, 320]], slots={'a': [0, 0, 1, 1], 'b': [0, 2, 1, 1]})

    def route(self, source='a', target='b', points=None, **kwargs):
        return dict(source_id=source, target_id=target, label='', source_port='east',
                    target_port='west', via=[], route_kind='mainline',
                    points=points or [[140, 80], [440, 80]], **kwargs)

    def test_straight_normalizes_without_mutation(self):
        g = self.grid(); r = [self.route(points=[[140,80],[200,80],[440,80]])]
        before = copy.deepcopy((g,r)); ng,nr = self.compile(g,r)
        self.assertEqual(ng['node_boxes']['a'], [40,40,100,80])
        self.assertEqual(nr[0]['points'], [[140,80],[440,80]])
        self.assertEqual((g,r), before)

    def test_branch_with_shared_source_stem(self):
        g=self.grid();g['slots']['c']=[1,2,1,1]
        r=[self.route(),self.route(target='c',points=[[140,80],[380,80],[380,280],[440,280]])]
        r[1]['route_kind']='branch';self.compile(g,r)

    def test_invalid_endpoints_and_segments(self):
        for changes in [dict(points=[[150,80],[440,80]]), dict(source_port='north'),
                        dict(points=[[140,80],[440,90]]),dict(points=[[140,80],[140,80]])]:
            r=self.route();r.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):self.compile(self.grid(),[r])

    def test_port_departure_and_arrival_must_be_normal(self):
        for side in ('source','target'):
            route=self.route(points=[[140,120],[440,120]])
            route[side+'_port']='south'
            with self.subTest(side=side),self.assertRaisesRegex(ValueError,'direction'):
                self.compile(self.grid(),[route])

    def test_obstacle_and_clearance(self):
        g=self.grid();g['slots']['c']=[0,1,1,1]
        with self.assertRaisesRegex(ValueError,'interior|clearance'):self.compile(g,[self.route()])
        r=self.route(points=[[140,80],[200,80],[200,125],[380,125],[380,80],[440,80]])
        r['route_kind']='feedback'
        with self.assertRaisesRegex(ValueError,'clearance'):self.compile(g,[r])

    def test_needless_and_excessive_bends(self):
        r=self.route(points=[[140,80],[180,80],[180,180],[400,180],[400,80],[440,80]])
        with self.assertRaises(ValueError):self.compile(self.grid(),[r])
        r['route_kind']='feedback'
        with self.assertRaisesRegex(ValueError,'detour'):self.compile(self.grid(),[r])

    def test_bad_grid_and_slot_bounds(self):
        for key,value in [('canvas',[0,400]),('rows',[[40,120],[110,200]]),
                          ('columns',[[40,140],[240,340],[450,550]]),
                          ('slots',{'a':[0,0,1,1],'b':[0,0,1,1]}),
                          ('slots',{'a':[0,0,1,1],'b':[0,2,1,2]})]:
            g=self.grid();g[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.compile(g,[])

    def crossing(self):
        g=self.grid();g['slots']={'a':[0,0,1,1],'b':[0,2,1,1], 'c':[0,1,1,1], 'd':[1,1,1,1]}
        # a and b use their lower borders so the horizontal route clears c.
        r=[self.route(points=[[100,120],[100,180],[480,180],[480,120]]),
           self.route('c','d',[[290,120],[290,240]])]
        r[0].update(source_port='south',target_port='south',route_kind='branch')
        r[1].update(source_port='south',target_port='north')
        return g,r

    def test_crossing_requires_valid_explicit_record(self):
        g,r=self.crossing()
        with self.assertRaisesRegex(ValueError,'crossing'):self.compile(g,r)
        g['crossings']=[dict(routes=[0,1],point=[290,180],treatment='bridge',reason='Separate flows')]
        self.compile(g,r)
        for change in [dict(point=[300,180]),dict(reason=''),dict(treatment='none')]:
            bad=copy.deepcopy(g);bad['crossings'][0].update(change)
            with self.assertRaises(ValueError):self.compile(bad,r)

    def test_more_than_one_crossing_per_route_is_rejected(self):
        g,r=self.crossing()
        r.append(self.route('c','d',[[320,120],[320,240]]))
        r[-1].update(source_port='south',target_port='north')
        g['crossings']=[dict(routes=[0,i],point=[x,180],treatment='distinct_ink',reason='Distinct flows')
                        for i,x in [(1,290),(2,320)]]
        with self.assertRaisesRegex(ValueError,'one crossing'):self.compile(g,r)

    def test_unrelated_routes_cannot_merge(self):
        g=self.grid();g['slots']['c']=[1,0,1,1]
        r=[self.route(),self.route('c','b',[[140,280],[380,280],[380,80],[440,80]])]
        r[1]['route_kind']='branch'
        with self.assertRaisesRegex(ValueError,'overlap|merge'):self.compile(g,r)

    def test_captions_cannot_hide_shafts_or_nodes(self):
        for box in [[200,70,80,20],[50,50,40,20],[590,350,50,20]]:
            with self.subTest(box=box),self.assertRaises(ValueError):
                self.compile(self.grid(),[self.route(caption='flow',caption_box=box)])
        self.compile(self.grid(),[self.route(caption='flow',caption_box=[200,130,80,20])])

    def test_identical_routes_cannot_merge_at_same_target(self):
        with self.assertRaisesRegex(ValueError,'merge|overlap'):
            self.compile(self.grid(),[self.route(),self.route()])

    def test_nonfinite_points_and_stale_crossings(self):
        for value in [float('nan'),float('inf'),True]:
            r=self.route();r['points'][0][0]=value
            with self.assertRaisesRegex(ValueError,'finite'):self.compile(self.grid(),[r])
        g=self.grid();g['crossings']=[dict(routes=[0,1],point=[200,80],treatment='bridge',reason='unused')]
        r=[self.route(),self.route(points=[[140,90],[440,90]])]
        with self.assertRaisesRegex(ValueError,'stale|unused'):self.compile(g,r)

    def test_caption_boxes_cannot_overlap(self):
        r=[self.route(caption='first',caption_box=[200,160,80,20]),
           self.route(points=[[140,90],[440,90]],caption='second',caption_box=[210,165,80,20])]
        with self.assertRaisesRegex(ValueError,'caption'):self.compile(self.grid(),r)

    def test_every_component_and_span_is_accounted_for(self):
        from scientific_figure_workflow.routing_geometry import compile_routing_geometry
        g=self.grid()
        with self.assertRaises(ValueError):compile_routing_geometry(g,[],['a','b','missing'])
        g['slots']['a']=[0,0,2,2]
        ng,_=self.compile(g,[]);self.assertEqual(ng['node_boxes']['a'],[40,40,300,280])

if __name__ == '__main__': unittest.main()
