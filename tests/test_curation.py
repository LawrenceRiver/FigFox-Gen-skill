import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from scientific_figure_rag.curation import select_diverse_records
from scientific_figure_rag.index import build_index


def record(record_id, group, layout, aspect, color):
    return {
        "record_id": record_id,
        "source_group_id": group,
        "metadata": {"layout": layout},
        "visual": {
            "aspect_ratio": aspect,
            "mean_rgb": color,
            "std_rgb": [0.1, 0.1, 0.1],
            "palette_size_capped": 12,
            "foreground_ratio": 0.2,
            "horizontal_edge_energy": 0.04,
            "vertical_edge_energy": 0.04,
            "occupied_grid_cells": 5,
        },
    }


class CurationTest(unittest.TestCase):
    def test_selects_distinct_source_groups_and_preserves_layout_coverage(self):
        records = [
            record("wide-a", "paper-a", "horizontal_flow", 2.4, [0.9, 0.2, 0.2]),
            record("wide-a-copy", "paper-a", "horizontal_flow", 2.4, [0.9, 0.2, 0.2]),
            record("vertical", "paper-b", "vertical_stack", 0.55, [0.2, 0.9, 0.2]),
            record("balanced", "paper-c", "balanced_canvas", 1.0, [0.2, 0.2, 0.9]),
            record("wide-b", "paper-d", "horizontal_flow", 3.1, [0.1, 0.1, 0.1]),
        ]

        selected = select_diverse_records(records, count=4)

        self.assertEqual(len(selected), 4)
        self.assertEqual(len({item["source_group_id"] for item in selected}), 4)
        self.assertEqual(
            {"horizontal_flow", "vertical_stack", "balanced_canvas"},
            {item["metadata"]["layout"] for item in selected},
        )

    def test_curation_cli_writes_twenty_style_pack_manifest_without_local_paths(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is required to create reference thumbnails")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            dataset = root / "dataset"
            dataset.mkdir()
            for index, color in enumerate(["red", "green", "blue"]):
                Image.new("RGB", (160 + index * 40, 100), color).save(dataset / f"figure-{index}.png")
            index_path = root / "index.sqlite"
            output = root / "pack"
            build_index(dataset, index_path)
            script = Path(__file__).resolve().parents[1] / "scripts/curate_reference_pack.py"

            subprocess.run(
                [sys.executable, str(script), "--index", str(index_path), "--output", str(output), "--count", "2"],
                check=True,
                capture_output=True,
                text=True,
            )
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(len(manifest["references"]), 2)
            self.assertFalse(any(str(dataset) in json.dumps(item) for item in manifest["references"]))
            self.assertTrue(all((output / item["thumbnail"]).exists() for item in manifest["references"]))


if __name__ == "__main__":
    unittest.main()
