import tempfile
import unittest
from pathlib import Path

from scientific_figure_workflow.svg_diagnostics import (
    apply_svg_crop_manifest,
    inspect_editable_svg,
    render_svg,
)


FIXTURES = Path(__file__).parent / "fixtures"


def diagnosis(verdict: str = "keep"):
    return {
        "verdicts": [
            {
                "component_id": "encoder",
                "verdict": verdict,
                "reason": "clear editable geometry",
            }
        ]
    }


class SvgInspectionTests(unittest.TestCase):
    def test_editable_svg_reports_text_and_vector_nodes(self):
        summary = inspect_editable_svg(FIXTURES / "editable.svg")

        self.assertGreater(summary["text_nodes"], 0)
        self.assertGreater(summary["vector_nodes"], 2)
        self.assertGreater(summary["editable_nodes"], 3)
        self.assertEqual(summary["raster_nodes"], 0)
        self.assertFalse(summary["raster_only"])

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
                "<image href='data:image/png;base64,AA==' width='2' height='2'/></svg>",
                encoding="utf-8",
            )
            summary = inspect_editable_svg(mixed)
            self.assertEqual(summary["raster_nodes"], 1)
            self.assertFalse(summary["raster_only"])

    def test_raster_wrapper_cannot_hide_vectors_only_in_defs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "defs-wrapper.svg"
            path.write_text(
                "<svg xmlns='http://www.w3.org/2000/svg'><defs><path d='M0 0'/></defs>"
                "<image href='data:image/png;base64,AA==' width='2' height='2'/></svg>",
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
                {
                    "diagnosis": diagnosis(),
                    "crops": [
                        {
                            "crop_id": "encoder-detail",
                            "target_component_id": "encoder",
                            "diagnosis_id": "encoder",
                            "bounds": {"x": 0.0, "y": 0.0, "width": 0.5, "height": 0.5},
                        }
                    ],
                },
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
            manifest = {
                "diagnosis": diagnosis("replace"),
                "crops": [{
                    "crop_id": "encoder-detail",
                    "target_component_id": "encoder",
                    "diagnosis_id": "encoder",
                    "bounds": {"x": 0.0, "y": 0.0, "width": 0.5, "height": 0.5},
                }],
            }
            with self.assertRaisesRegex(ValueError, "approved diagnosis"):
                apply_svg_crop_manifest(rendered, manifest, root / "svg-diagnostic/approved-crops")

            manifest["diagnosis"] = diagnosis()
            manifest["crops"][0]["diagnosis_id"] = "other"
            with self.assertRaisesRegex(ValueError, "diagnosis"):
                apply_svg_crop_manifest(rendered, manifest, root / "svg-diagnostic/approved-crops")

            manifest["crops"][0]["diagnosis_id"] = "encoder"
            with self.assertRaisesRegex(ValueError, "approved-crops"):
                apply_svg_crop_manifest(rendered, manifest, root / "crops")
