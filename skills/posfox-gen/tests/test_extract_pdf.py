"""Synthetic local PDF checks; no scientific poster or model run."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import fitz

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('extract_pdf',ROOT/'scripts/extract_pdf.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ExtractPDFTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.paper=self.root/'paper.pdf';d=fitz.open();p=d.new_page(width=300,height=200)
        p.insert_text((20,30),'A source-backed result: 91.4 points')
        p.draw_rect(fitz.Rect(20,50,220,160),color=(0,0,1))
        d.save(self.paper);d.close()
    def tearDown(self):self.tmp.cleanup()
    def test_full_text_preview_and_inspected_vector_crop(self):
        table=module.extract_assets(self.paper,self.root/'source',[{'id':'method','type':'figure','page':1,'bbox':[20,50,220,160],'caption':'Complete synthetic diagram','source_locator':'Page 1 diagram'}],render_scale=4)
        self.assertEqual(table['source']['page_count'],1)
        self.assertTrue((self.root/'source/pages/page-001.png').is_file())
        self.assertTrue(any('91.4' in a.get('text','') for a in table['assets']))
        crop=next(a for a in table['assets'] if a['id']=='method')
        self.assertEqual((crop['width'],crop['height']),(800,440))
        self.assertEqual(crop['geometry'], {'pdf_size_pt':[200.0,110.0], 'pixel_size':[800,440], 'aspect_ratio':800/440})
        self.assertTrue(crop['source_bounds_verified'])
        self.assertEqual(crop['source']['paper_sha256'],table['source']['paper_sha256'])
        self.assertEqual(json.loads((self.root/'source/asset_table.json').read_text())['source'],table['source'])
    def test_out_of_bounds_crop_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'outside page'):
            module.extract_assets(self.paper,self.root/'bad',[{'id':'bad','page':1,'bbox':[0,0,400,100]}])
    def test_invalid_resolution_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'render_scale'):
            module.extract_assets(self.paper,self.root/'bad',render_scale=True)

if __name__=='__main__':unittest.main()
