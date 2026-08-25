import base64
import os
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from scientific_figure_workflow.prompts import build_prompt2_bundle
from scientific_figure_workflow.svg_diagnostics import (
    apply_svg_crop_manifest,
    inspect_editable_svg,
    render_svg,
)


FIXTURES = Path(__file__).parent / "fixtures"
PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"


def raster_uri(image_format: str = "png") -> str:
    output = BytesIO()
    Image.new("RGB", (1, 1), (255, 0, 0)).save(output, format=image_format.upper())
    payload = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/{image_format};base64,{payload}"


def diagnosis(verdict: str = "keep", component_id: str = "encoder"):
    return {
        "verdicts": [
            {
                "component_id": component_id,
                "verdict": verdict,
                "reason": "clear editable geometry",
            }
        ]
    }


def crop_manifest(*, verdict: str = "keep", component_ids=None, crops=None):
    return {
        "component_ids": ["encoder"] if component_ids is None else component_ids,
        "diagnosis": diagnosis(verdict),
        "crops": crops or [
            {
                "crop_id": "encoder-detail",
                "target_component_id": "encoder",
                "diagnosis_id": "encoder",
                "bounds": {"x": 0.0, "y": 0.0, "width": 0.5, "height": 0.5},
            }
        ],
    }


def write_svg(directory: Path, name: str, child: str, root_attributes: str = "") -> Path:
    path = directory / f"{name}.svg"
    path.write_text(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' {root_attributes}>"
        f"{child}</svg>",
        encoding="utf-8",
    )
    return path


class SvgInspectionTests(unittest.TestCase):
    def test_editable_svg_reports_text_and_vector_nodes(self):
        summary = inspect_editable_svg(FIXTURES / "editable.svg")

        self.assertGreater(summary["text_nodes"], 0)
        self.assertGreater(summary["vector_nodes"], 2)
        self.assertGreater(summary["editable_nodes"], 3)
        self.assertEqual(summary["raster_nodes"], 0)
        self.assertFalse(summary["raster_only"])

    def test_vector_only_transformed_and_nested_content_remains_structurally_editable(self):
        cases = {
            "transformed": (
                "<g transform='translate(10 10)'><rect width='40' height='30'/>"
                "<text x='5' y='20'>Moved label</text></g>"
            ),
            "nested": (
                "<svg x='10' y='10' width='80' height='80'><rect width='40' height='30'/>"
                "<text x='5' y='20'>Nested label</text></svg>"
            ),
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, child in cases.items():
                with self.subTest(name=name):
                    summary = inspect_editable_svg(write_svg(root, name, child))
                    self.assertEqual(summary["vector_nodes"], 1)
                    self.assertEqual(summary["text_nodes"], 1)
                    self.assertEqual(summary["editable_nodes"], 2)
                    self.assertEqual(summary["meaningful_editable_nodes"], 0)

    def test_raster_wrapper_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "raster wrapper"):
            inspect_editable_svg(FIXTURES / "raster-wrapper.svg")

    def test_rejects_html_malformed_missing_svg_and_zero_editable_content(self):
        cases = {
            "html": "<html><body>not an svg</body></html>",
            "malformed": "<svg xmlns='http://www.w3.org/2000/svg'><path></svg>",
            "missing-svg": "<svg><rect width='2' height='2'/></svg>",
            "zero-editable": "<svg xmlns='http://www.w3.org/2000/svg'><title>only metadata</title></svg>",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, source in cases.items():
                path = root / f"{name}.svg"
                path.write_text(source, encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(ValueError):
                    inspect_editable_svg(path)

    def test_rejects_unsafe_nodes_and_remote_images_but_reports_local_embedded_image(self):
        unsafe = {
            "script": "<script>alert(1)</script>",
            "foreign": "<foreignObject><div>bad</div></foreignObject>",
            "remote": "<image href='https://example.test/image.png' width='2' height='2'/>",
            "remote-style": "<rect width='2' height='2' style='fill: url(https://example.test/pattern.svg)'/>",
            "remote-style-block": "<style>@import url(https://example.test/style.css);</style>",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, child in unsafe.items():
                path = root / f"{name}.svg"
                path.write_text(
                    "<svg xmlns='http://www.w3.org/2000/svg'><rect width='2' height='2'/>"
                    f"{child}</svg>",
                    encoding="utf-8",
                )
                with self.subTest(name=name), self.assertRaises(ValueError):
                    inspect_editable_svg(path)

            mixed = root / "mixed.svg"
            mixed.write_text(
                "<svg xmlns='http://www.w3.org/2000/svg'><rect width='4' height='4'/>"
                f"<image href='{raster_uri()}' width='2' height='2'/></svg>",
                encoding="utf-8",
            )
            summary = inspect_editable_svg(mixed)
            self.assertEqual(summary["raster_nodes"], 1)
            self.assertFalse(summary["raster_only"])

    def test_rejects_every_non_fragment_resource_reference(self):
        references = {
            "relative": "image.png",
            "absolute": "/tmp/image.png",
            "file": "file:///tmp/image.png",
            "http": "https://example.test/image.png",
            "protocol-relative": "//example.test/image.png",
            "unc-ish": r"\\server\share\image.png",
            "windows": r"C:\image.png",
            "svg-data": "data:image/svg+xml;base64,PHN2Zy8+",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, reference in references.items():
                path = write_svg(
                    root,
                    name,
                    f"<rect width='20' height='20'/><image href='{reference}' width='50' height='50'/>",
                )
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "resource"):
                    inspect_editable_svg(path)

    def test_rejects_unsafe_use_xlink_xml_base_and_resource_attributes(self):
        cases = {
            "use-relative": "<rect width='20' height='20'/><use href='symbols.svg#shape'/>",
            "use-http": "<rect width='20' height='20'/><use href='https://example.test/a.svg#x'/>",
            "xlink": (
                "<rect width='20' height='20'/><image xmlns:xlink='http://www.w3.org/1999/xlink' "
                "xlink:href='local.png' width='20' height='20'/>"
            ),
            "xml-base": "<g xml:base='https://example.test/'><rect width='20' height='20'/></g>",
            "cursor": "<rect width='20' height='20' cursor='local.cur'/>",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, child in cases.items():
                with self.subTest(name=name), self.assertRaises(ValueError):
                    inspect_editable_svg(write_svg(root, name, child))

    def test_allows_fragments_and_only_explicit_base64_raster_image_data(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for image_format in ("png", "jpeg", "webp"):
                safe = (
                    "<defs><linearGradient id='g'/><path id='shape' d='M0 0 L10 10'/></defs>"
                    "<rect width='30' height='30' fill='url(#g)'/>"
                    f"<use href='#shape'/><image href='{raster_uri(image_format)}' "
                    "x='60' y='60' width='20' height='20'/>"
                )
                with self.subTest(image_format=image_format):
                    summary = inspect_editable_svg(write_svg(root, f"safe-{image_format}", safe))
                    self.assertEqual(summary["raster_nodes"], 1)

    def test_rejects_css_import_and_every_non_fragment_css_url(self):
        cases = {
            "import-string": "<style>@import 'local.css';</style><rect width='20' height='20'/>",
            "import-url": "<style>@import url(https://example.test/a.css);</style><rect width='20' height='20'/>",
            "style-relative": "<rect width='20' height='20' style=\"fill:url('paint.svg#g')\"/>",
            "style-data": "<rect width='20' height='20' style=\"fill:url(data:image/png;base64,AA==)\"/>",
            "presentation-url": "<rect width='20' height='20' filter='url(/tmp/filter.svg#f)'/>",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, child in cases.items():
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "resource|CSS"):
                    inspect_editable_svg(write_svg(root, name, child))

    def test_css_parser_rejects_escaped_quoted_and_nested_resource_urls(self):
        cases = {
            "escaped-url": r"<rect width='20' height='20' style='fill:u\72l(file:///tmp/paint.svg)'/>",
            "quoted-url": "<rect width='20' height='20' style='fill:url(\"file:///tmp/paint.svg\")'/>",
            "nested-url": "<rect width='20' height='20' style='fill:paint(url(file:///tmp/paint.svg))'/>",
            "stylesheet-escaped": r"<style>rect { fill: u\72l(https://example.test/paint.svg) }</style><rect width='20' height='20'/>",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, child in cases.items():
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "resource"):
                    inspect_editable_svg(write_svg(root, name, child))

            safe = write_svg(
                root,
                "decoded-safe-fragment",
                r"<defs><linearGradient id='gradient'/></defs><rect width='20' height='20' style='fill:u\72l(#gradient)'/>",
            )
            self.assertEqual(inspect_editable_svg(safe)["vector_nodes"], 1)

    def test_rejects_mislabeled_malformed_xml_and_oversized_raster_payloads(self):
        oversized = base64.b64encode(b"\0" * (5 * 1024 * 1024 + 1)).decode("ascii")
        unsafe = {
            "mislabeled": f"data:image/jpeg;base64,{PNG_BASE64}",
            "malformed": "data:image/png;base64,AA==",
            "xml": "data:image/png;base64,PHN2Zz48L3N2Zz4=",
            "oversized": f"data:image/png;base64,{oversized}",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, reference in unsafe.items():
                child = f"<rect width='20' height='20'/><image href='{reference}' width='20' height='20'/>"
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "resource"):
                    inspect_editable_svg(write_svg(root, name, child))

    def test_rejects_foreign_and_no_namespace_child_elements(self):
        cases = {
            "foreign": "<html:div xmlns:html='http://www.w3.org/1999/xhtml'/><rect width='20' height='20'/>",
            "no-namespace": "<g xmlns=''><rect width='20' height='20'/></g><rect width='20' height='20'/>",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, child in cases.items():
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "namespace"):
                    inspect_editable_svg(write_svg(root, name, child))

    def test_dominant_raster_rejects_hidden_zero_and_microscopic_vector_bypasses(self):
        bypasses = {
            "display": "<rect style='display:none' width='100' height='100'/>",
            "visibility": "<rect visibility='hidden' width='100' height='100'/>",
            "opacity": "<rect opacity='0' width='100' height='100'/>",
            "zero-size": "<rect width='0' height='100'/>",
            "zero-line": "<line x1='2' y1='2' x2='2' y2='2'/>",
            "microscopic": "<rect width='0.01' height='0.01'/>",
        }
        raster = f"<image href='{raster_uri('jpeg')}' width='100' height='100'/>"
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, vector in bypasses.items():
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "raster wrapper"):
                    inspect_editable_svg(write_svg(root, name, raster + vector))

    def test_dominant_raster_rejects_stylesheet_bounds_paint_transform_and_occlusion_bypasses(self):
        raster_first = f"<image href='{raster_uri()}' width='100' height='100'/>"
        raster_last = f"<image href='{raster_uri()}' width='100' height='100'/>"
        bypasses = {
            "class-hidden": (
                "<style>.hidden { display:none }</style>" + raster_first
                + "<rect class='hidden' width='80' height='30'/><text class='hidden' x='10' y='20'>Hidden label</text>"
            ),
            "element-hidden": (
                "<style>rect { opacity:0 }</style>" + raster_first
                + "<rect width='80' height='30'/><rect y='50' width='80' height='30'/>"
            ),
            "inherited-hidden": (
                raster_first + "<g visibility='hidden'><rect width='80' height='30'/>"
                "<text x='10' y='20'>Hidden label</text></g>"
            ),
            "off-canvas": (
                raster_first + "<rect x='200' y='200' width='80' height='30'/>"
                "<text x='200' y='250'>Outside label</text>"
            ),
            "microscopic-visible-intersection": (
                raster_first + "<rect x='99.999' width='1000' height='30'/>"
                "<rect x='99.999' y='50' width='1000' height='30'/>"
            ),
            "transformed-off-canvas": (
                raster_first + "<g transform='translate(500 0)'><rect width='80' height='30'/>"
                "<text x='10' y='20'>Moved label</text></g>"
            ),
            "text-displacement": (
                raster_first + "<text x='10' y='20' dx='500'>Moved label</text>"
                "<text x='10' y='60' dx='500'>Moved detail</text>"
            ),
            "nested-svg-viewport": (
                raster_first + "<svg x='500' width='100' height='100'>"
                "<rect width='80' height='30'/><text x='10' y='20'>Nested label</text></svg>"
            ),
            "transformed-raster": (
                f"<image href='{raster_uri()}' width='100' height='100' transform='translate(0 0)'/>"
                "<rect width='80' height='30'/><text x='10' y='20'>False proof</text>"
            ),
            "no-paint": (
                raster_first + "<rect width='80' height='30' fill='none' stroke='none'/>"
                "<line x1='10' y1='50' x2='90' y2='50'/>"
            ),
            "covered-by-later-raster": (
                "<rect width='80' height='30'/><text x='10' y='20'>Covered label</text>" + raster_last
            ),
            "unhandled-path-bounds": (
                raster_first + "<path d='M10 10 C20 20 60 20 80 30' fill='none' stroke='black'/>"
                "<path d='M10 50 C20 60 60 60 80 70' fill='none' stroke='black'/>"
            ),
            "empty-clip": (
                "<defs><clipPath id='empty'/></defs>" + raster_first
                + "<g clip-path='url(#empty)'><rect width='80' height='30'/>"
                "<text x='10' y='20'>Clipped label</text></g>"
            ),
            "uncertain-fragment-paint": (
                "<defs><linearGradient id='transparent'><stop stop-opacity='0'/></linearGradient></defs>"
                + raster_first + "<rect width='80' height='30' fill='url(#transparent)'/>"
                "<rect y='50' width='80' height='30' fill='url(#transparent)'/>"
            ),
            "transparent-modern-color": (
                raster_first + "<rect width='80' height='30' fill='rgb(0 0 0 / 0)'/>"
                "<rect y='50' width='80' height='30' fill='rgba(0 0 0 / 0)'/>"
            ),
            "unresolved-current-color": (
                raster_first + "<rect width='80' height='30' fill='currentColor'/>"
                "<rect y='50' width='80' height='30' fill='currentColor'/>"
            ),
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, child in bypasses.items():
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "raster wrapper"):
                    inspect_editable_svg(write_svg(root, name, child))

    def test_meaningful_mixed_vector_raster_passes_and_reports_dominance_facts(self):
        child = (
            f"<image href='{raster_uri('webp')}' width='80' height='100'/>"
            "<rect x='5' y='5' width='90' height='90' fill='none' stroke='black'/>"
            "<line x1='10' y1='50' x2='90' y2='50' stroke='black'/>"
            "<text x='10' y='20'>Measured sample</text>"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            summary = inspect_editable_svg(write_svg(Path(temporary_directory), "mixed-meaningful", child))
        self.assertTrue(summary["dominant_raster"])
        self.assertGreaterEqual(summary["meaningful_editable_nodes"], 2)
        self.assertEqual(summary["large_raster_nodes"], 1)

    def test_raster_wrapper_cannot_hide_vectors_only_in_defs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "defs-wrapper.svg"
            path.write_text(
                "<svg xmlns='http://www.w3.org/2000/svg'><defs><path d='M0 0'/></defs>"
                f"<image href='{raster_uri()}' width='2' height='2'/></svg>",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "raster wrapper"):
                inspect_editable_svg(path)


class SvgRenderAndCropTests(unittest.TestCase):
    def test_render_svg_materializes_png15_after_inspection(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "svg-diagnostic/png1.5.png"
            result = render_svg(FIXTURES / "editable.svg", target)

            self.assertEqual(result, target)
            self.assertTrue(result.is_file())
            self.assertGreater(result.stat().st_size, 0)

    def test_approved_crop_is_rendered_from_png15_with_prompt2_provenance(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            rendered = render_svg(FIXTURES / "editable.svg", root / "svg-diagnostic/png1.5.png")
            result = apply_svg_crop_manifest(
                rendered,
                crop_manifest(),
                root / "svg-diagnostic/approved-crops",
            )

            self.assertEqual(result["crops"], [{
                "path": "svg-diagnostic/approved-crops/encoder-detail.png",
                "target_component_id": "encoder",
                "diagnosis": "keep: clear editable geometry",
            }])
            self.assertTrue((root / result["crops"][0]["path"]).is_file())
            self.assertNotIn("png1.5.png", str(result["crops"]))

    def test_crop_rejects_nonapproved_verdict_mismatched_diagnosis_and_noncanonical_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            rendered = render_svg(FIXTURES / "editable.svg", root / "svg-diagnostic/png1.5.png")
            manifest = crop_manifest(verdict="replace")
            with self.assertRaisesRegex(ValueError, "approved diagnosis"):
                apply_svg_crop_manifest(rendered, manifest, root / "svg-diagnostic/approved-crops")

            manifest["diagnosis"] = diagnosis()
            manifest["crops"][0]["diagnosis_id"] = "other"
            with self.assertRaisesRegex(ValueError, "diagnosis"):
                apply_svg_crop_manifest(rendered, manifest, root / "svg-diagnostic/approved-crops")

            manifest["crops"][0]["diagnosis_id"] = "encoder"
            with self.assertRaisesRegex(ValueError, "approved-crops"):
                apply_svg_crop_manifest(rendered, manifest, root / "crops")

    def test_render_rejects_symlink_target_and_cleans_partial_or_stale_png15(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            target = root / "svg-diagnostic/png1.5.png"
            target.parent.mkdir(parents=True)
            outside = root / "outside.png"
            outside.write_bytes(b"do not overwrite")
            os.symlink(outside, target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                render_svg(FIXTURES / "editable.svg", target)
            self.assertEqual(outside.read_bytes(), b"do not overwrite")

            target.unlink()
            target.write_bytes(b"stale canonical output")

            def partial_then_fail(*, url, write_to):
                Path(write_to).write_bytes(b"partial")
                raise RuntimeError("simulated CairoSVG failure")

            with patch("cairosvg.svg2png", side_effect=partial_then_fail):
                with self.assertRaisesRegex(RuntimeError, "simulated"):
                    render_svg(FIXTURES / "editable.svg", target)
            self.assertFalse(target.exists())
            self.assertEqual(list(target.parent.glob(".*png1.5.png.*")), [])

    def test_render_rejects_symlink_parent_without_unlinking_redirected_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            outside = root / "outside"
            outside.mkdir()
            redirected = outside / "png1.5.png"
            redirected.write_bytes(b"preserve redirected file")
            os.symlink(outside, root / "svg-diagnostic")

            with self.assertRaisesRegex(ValueError, "symlink"):
                render_svg(FIXTURES / "editable.svg", root / "svg-diagnostic/png1.5.png")

            self.assertEqual(redirected.read_bytes(), b"preserve redirected file")

    def test_render_rejects_non_png_output_and_removes_stale_target(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "svg-diagnostic/png1.5.png"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"stale")

            def fake_success(*, url, write_to):
                Path(write_to).write_bytes(b"not a png")

            with patch("cairosvg.svg2png", side_effect=fake_success):
                with self.assertRaisesRegex(RuntimeError, "PNG1.5"):
                    render_svg(FIXTURES / "editable.svg", target)
            self.assertFalse(target.exists())

    def test_crop_rejects_symlink_output_and_destination(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            rendered = render_svg(FIXTURES / "editable.svg", root / "svg-diagnostic/png1.5.png")
            output = root / "svg-diagnostic/approved-crops"
            outside = root / "outside"
            outside.mkdir()
            os.symlink(outside, output)
            with self.assertRaisesRegex(ValueError, "symlink"):
                apply_svg_crop_manifest(rendered, crop_manifest(), output)

            output.unlink()
            output.mkdir()
            outside_file = root / "outside.png"
            outside_file.write_bytes(b"preserve")
            os.symlink(outside_file, output / "encoder-detail.png")
            with self.assertRaisesRegex(ValueError, "symlink"):
                apply_svg_crop_manifest(rendered, crop_manifest(), output)
            self.assertEqual(outside_file.read_bytes(), b"preserve")

    def test_crop_cleans_exclusive_temporary_file_when_encoding_fails(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            rendered = render_svg(FIXTURES / "editable.svg", root / "svg-diagnostic/png1.5.png")
            output = root / "svg-diagnostic/approved-crops"
            with patch("PIL.Image.Image.save", side_effect=OSError("simulated crop encoding failure")):
                with self.assertRaisesRegex(OSError, "simulated"):
                    apply_svg_crop_manifest(rendered, crop_manifest(), output)
            self.assertEqual(list(output.glob(".*.tmp")), [])

    def test_crop_rejects_invalid_bounds_duplicate_or_unsafe_ids_and_path_escape(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            rendered = render_svg(FIXTURES / "editable.svg", root / "svg-diagnostic/png1.5.png")
            valid = crop_manifest()["crops"][0]
            bad_crops = {
                "invalid-bounds": [{**valid, "bounds": {"x": 0.9, "y": 0, "width": 0.2, "height": 1}}],
                "duplicate": [valid, dict(valid)],
                "escape": [{**valid, "crop_id": "../escape"}],
                "absolute": [{**valid, "crop_id": "/tmp/escape"}],
            }
            for name, crops in bad_crops.items():
                with self.subTest(name=name), self.assertRaises(ValueError):
                    apply_svg_crop_manifest(rendered, crop_manifest(crops=crops), root / "svg-diagnostic/approved-crops")
            self.assertFalse((root / "escape.png").exists())

    def test_crop_requires_complete_context2_component_identity_anchor(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            rendered = render_svg(FIXTURES / "editable.svg", root / "svg-diagnostic/png1.5.png")
            missing = crop_manifest()
            del missing["component_ids"]
            with self.assertRaisesRegex(ValueError, "component_ids"):
                apply_svg_crop_manifest(rendered, missing, root / "svg-diagnostic/approved-crops")

            invented = crop_manifest(component_ids=["invented"])
            with self.assertRaisesRegex(ValueError, "exactly one verdict"):
                apply_svg_crop_manifest(rendered, invented, root / "svg-diagnostic/approved-crops")

            incomplete = crop_manifest(component_ids=["encoder", "audio"])
            with self.assertRaisesRegex(ValueError, "exactly one verdict"):
                apply_svg_crop_manifest(rendered, incomplete, root / "svg-diagnostic/approved-crops")

    def test_crop_result_is_an_actual_task5_prompt2_handoff(self):
        from tests.test_prompts import c1, c2, c3

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for relative in (
                "references/web/crops/piano-roll.png",
                "references/figurebench/crops/container.png",
                "references/figurebench/crops/arrow.png",
                "png1.png",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture")
            rendered = render_svg(FIXTURES / "editable.svg", root / "svg-diagnostic/png1.5.png")
            complete_diagnosis = {
                "verdicts": [
                    {"component_id": "encoder", "verdict": "keep", "reason": "faithful"},
                    {"component_id": "audio", "verdict": "patch", "reason": "repair label"},
                ]
            }
            result = apply_svg_crop_manifest(
                rendered,
                {
                    "component_ids": ["encoder", "audio"],
                    "diagnosis": complete_diagnosis,
                    "crops": crop_manifest()["crops"],
                },
                root / "svg-diagnostic/approved-crops",
            )
            bundle = build_prompt2_bundle(
                "method", c1(), c2(), c3(), "png1.png", complete_diagnosis, result, {}, root
            )
            approved = [item for item in bundle["attachments"] if item["role"] == "approved_svg_crop"]
            self.assertEqual(approved[0]["path"], result["crops"][0]["path"])
            self.assertNotIn("png1.5.png", {item["path"] for item in bundle["attachments"]})
