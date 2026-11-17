"""Direct raster insertion preserves inputs and validates the whole batch first."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/place_raster_insets.py'


def compose(root):
    spec = importlib.util.spec_from_file_location('raster_insets', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.place_raster_insets(root)


def fixture(tmp_path):
    (tmp_path / 'input/raster').mkdir(parents=True)
    Image.new('RGB', (40, 30), 'navy').save(tmp_path / 'generated-layout.png')
    Image.new('RGBA', (10, 4), 'red').save(tmp_path / 'input/raster/a.png')
    manifest = {
        'canvas': [40, 30], 'background': 'generated-layout.png', 'output': 'png1.png',
        'insets': [{'path': 'input/raster/a.png', 'target_component_id': 'photo',
                    'box': [10, 10, 10, 10], 'source': 'own photograph',
                    'permission_evidence': 'Photographed and owned by the author',
                    'attribution': 'Author'}],
    }
    return tmp_path, manifest


def save(run):
    root, manifest = run
    (root / 'input/raster-inserts.json').write_text(json.dumps(manifest))
    return root



class RasterInsetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.run = fixture(Path(self.directory.name))

    def test_contain_preserves_aspect_background_and_source_bytes(self):
        run = self.run
        root = save(run)
        before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
        receipt = compose(root)
        with Image.open(root / 'png1.png') as image:
            assert image.getpixel((10, 10)) == (0, 0, 128, 255)
            assert image.getpixel((10, 13)) == (255, 0, 0, 255)
            assert image.getpixel((10, 17)) == (0, 0, 128, 255)
        assert all(p.read_bytes() == data for p, data in before.items())
        inset = receipt['insets'][0]
        assert inset['original_size'] == [10, 4]
        assert inset['requested_box'] == [10, 10, 10, 10]
        assert inset['actual_box'] == [10, 13, 10, 4]
        assert inset['fit'] == 'contain'
        assert inset['sha256'] == hashlib.sha256((root / 'input/raster/a.png').read_bytes()).hexdigest()
        assert json.loads((root / 'png1.raster-receipt.json').read_text()) == receipt


    def test_cover_crops_center_instead_of_stretching(self):
        run = self.run
        root, manifest = run
        source = Image.new('RGB', (10, 4), 'red')
        for x in range(3, 7):
            for y in range(4): source.putpixel((x, y), (0, 255, 0))
        source.save(root / 'input/raster/a.png')
        manifest['insets'][0].update(fit='cover', box=[10, 10, 4, 4])
        save(run); receipt = compose(root)
        with Image.open(root / 'png1.png') as image:
            assert image.getpixel((10, 10)) == (0, 255, 0, 255)
            assert image.getpixel((13, 13)) == (0, 255, 0, 255)
        assert receipt['insets'][0]['actual_box'] == [10, 10, 4, 4]


    def test_transparent_source_pixels_reveal_existing_background(self):
        run = self.run
        root, _ = run
        source = Image.new('RGBA', (10, 4), (255, 0, 0, 0))
        source.putpixel((5, 2), (255, 0, 0, 255))
        source.save(root / 'input/raster/a.png')
        save(run); compose(root)
        with Image.open(root / 'png1.png') as image:
            assert image.getpixel((10, 13)) == (0, 0, 128, 255)
            assert image.getpixel((15, 15)) == (255, 0, 0, 255)


    def test_invalid_manifest_produces_no_output(self):
        root, original = self.run
        for change in [
            {'canvas': [41, 30]}, {'output': '../escaped.png'},
            {'output': 'generated-layout.png'}, {'background': '../outside.png'},
        ]:
            with self.subTest(change=change):
                manifest = json.loads(json.dumps(original)); manifest.update(change)
                save((root, manifest))
                with self.assertRaises(ValueError): compose(root)
                self.assertFalse((root / 'png1.png').exists())
                self.assertFalse((root / 'png1.raster-receipt.json').exists())

    def test_invalid_late_inset_prevents_partial_composition(self):
        root, original = self.run
        for change in [
            {'box': [-1, 10, 10, 10]}, {'box': [35, 10, 10, 10]},
            {'box': [1.5, 10, 10, 10]}, {'fit': 'stretch'},
            {'permission_evidence': ''}, {'source': ''}, {'target_component_id': ''},
        ]:
            with self.subTest(change=change):
                manifest = json.loads(json.dumps(original))
                second = dict(manifest['insets'][0], box=[25, 10, 10, 10])
                second.update(change); manifest['insets'].append(second)
                save((root, manifest))
                with self.assertRaises(ValueError): compose(root)
                self.assertFalse((root / 'png1.png').exists())

    def test_overlapping_boxes_and_bad_image_are_rejected(self):
        run = self.run
        root, manifest = run
        manifest['insets'].append(dict(manifest['insets'][0], box=[15, 10, 10, 10]))
        save(run)
        with self.assertRaisesRegex(ValueError, 'overlap'): compose(root)
        manifest['insets'].pop(); (root / 'input/raster/a.png').write_bytes(b'not an image'); save(run)
        with self.assertRaisesRegex(ValueError, 'decode'): compose(root)
        assert not (root / 'png1.png').exists()


    def test_symlink_input_output_and_parent_are_rejected(self):
        run = self.run
        root, manifest = run
        (root / 'linked.png').symlink_to(root / 'input/raster/a.png')
        manifest['insets'][0]['path'] = 'linked.png'; save(run)
        with self.assertRaisesRegex(ValueError, 'symlink'): compose(root)
        manifest['insets'][0]['path'] = 'input/raster/a.png'
        (root / 'png1.png').symlink_to(root / 'generated-layout.png')
        save(run)
        original = (root / 'generated-layout.png').read_bytes()
        with self.assertRaisesRegex(ValueError, 'symlink'): compose(root)
        assert (root / 'generated-layout.png').read_bytes() == original
        (root / 'png1.png').unlink()
        (root / 'alias').symlink_to(root / 'input', target_is_directory=True)
        manifest['output'] = 'alias/new.png'; save(run)
        with self.assertRaisesRegex(ValueError, 'symlink'): compose(root)
        assert not (root / 'input/new.png').exists()


    def test_cli_default_manifest_and_existing_output_is_preserved(self):
        run = self.run
        root = save(run)
        result = subprocess.run([sys.executable, str(SCRIPT), '--run', str(root)],
                                capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        before = (root / 'png1.png').read_bytes()
        with self.assertRaisesRegex(ValueError, 'exist'): compose(root)
        assert (root / 'png1.png').read_bytes() == before
