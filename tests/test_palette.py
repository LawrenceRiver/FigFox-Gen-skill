import copy
from pathlib import Path
import unittest

import scientific_figure_workflow
from scientific_figure_workflow.palette import palette_hex_set, validate_palette


ROOT = Path(__file__).resolve().parents[1]


def palette_library_fixture():
    return [
        {
            "id": "group-a",
            "colours": [
                {"role": "ink", "hex": "#203040", "rgb": [32, 48, 64]},
                {"role": "primary", "hex": "#406080", "rgb": [64, 96, 128]},
            ],
        },
        {
            "id": "group-b",
            "colours": [
                {"role": "accent", "hex": "#A04040", "rgb": [160, 64, 64]},
            ],
        },
    ]


def base_colours():
    return copy.deepcopy(palette_library_fixture()[0]["colours"])


def valid_palette():
    return {
        "base_palette_id": "group-a",
        "dominant_colour_roles": ["ink", "primary"],
        "colours": base_colours(),
        "extensions": [
            {
                "role": "quiet_accent",
                "hex": "#6E8FA3",
                "rgb": [110, 143, 163],
                "relationship": "analogous_neighbour",
                "evidence_url": "https://color.adobe.com/create/color-wheel",
                "evidence_summary": "Blue-grey adjacent tone compatible with the base blue family.",
            }
        ],
    }


class PaletteLineageTests(unittest.TestCase):
    def test_validator_is_exported_from_the_workflow_package(self):
        self.assertIs(scientific_figure_workflow.validate_palette, validate_palette)

    def test_accepts_one_approved_base_group_and_evidenced_related_colour(self):
        palette = validate_palette(valid_palette(), palette_library_fixture())

        self.assertEqual(palette, valid_palette())

    def test_rejects_a_second_palette_library_group(self):
        with self.assertRaisesRegex(ValueError, "one base palette group"):
            validate_palette(
                {
                    "base_palette_id": "group-a",
                    "additional_palette_ids": ["group-b"],
                    "colours": [{"role": "ink", "hex": "#203040", "rgb": [32, 48, 64]}],
                    "extensions": [],
                },
                palette_library_fixture(),
            )

    def test_rejects_more_than_three_dominant_colour_roles(self):
        palette = valid_palette()
        palette["dominant_colour_roles"] = ["ink", "primary", "accent", "secondary"]
        with self.assertRaisesRegex(ValueError, "at most three dominant"):
            validate_palette(palette, palette_library_fixture())

    def test_related_colour_requires_web_evidence_and_relationship(self):
        palette = validate_palette(valid_palette(), palette_library_fixture())

        self.assertEqual(palette["base_palette_id"], "group-a")

    def test_requires_every_base_colour_to_match_the_selected_group_exactly(self):
        for mutation, reason in (
            (lambda palette: palette["colours"].pop(), "base palette"),
            (lambda palette: palette["colours"].__setitem__(0, {"role": "ink", "hex": "#203041", "rgb": [32, 48, 65]}), "base palette"),
            (lambda palette: palette["colours"].__setitem__(0, {"role": "label", "hex": "#203040", "rgb": [32, 48, 64]}), "base palette"),
        ):
            with self.subTest(reason=reason):
                palette = valid_palette()
                mutation(palette)
                with self.assertRaisesRegex(ValueError, reason):
                    validate_palette(palette, palette_library_fixture())

    def test_rejects_invalid_exact_colour_and_rgb_values(self):
        for location, field, value, reason in (
            ("colours", "hex", "#203040 ", "uppercase HEX"),
            ("colours", "hex", "#203040", "rgb matching hex"),
            ("extensions", "hex", "#6e8fa3", "uppercase HEX"),
            ("extensions", "rgb", [110, 143, 162], "rgb matching hex"),
        ):
            with self.subTest(location=location, field=field, value=value):
                palette = valid_palette()
                palette[location][0][field] = value
                if location == "colours" and field == "hex" and value == "#203040":
                    palette[location][0]["rgb"] = [32, 48, 63]
                with self.assertRaisesRegex(ValueError, reason):
                    validate_palette(palette, palette_library_fixture())

    def test_rejects_unexplained_or_invalid_extension(self):
        for field, value, reason in (
            ("role", "", "non-empty role"),
            ("relationship", "unrelated", "relationship"),
            ("evidence_url", "http://example.test/evidence", "HTTPS evidence_url"),
            ("evidence_summary", "", "evidence_summary"),
        ):
            with self.subTest(field=field):
                palette = valid_palette()
                palette["extensions"][0][field] = value
                with self.assertRaisesRegex(ValueError, reason):
                    validate_palette(palette, palette_library_fixture())

    def test_rejects_source_mixing_gradients_and_duplicate_colours(self):
        for field, value, reason in (
            ("user_reference_palette_id", "user-palette", "user-reference"),
            ("figurebench_palette_id", "figurebench-palette", "FigureBench"),
            ("gradients", [{"from": "#203040", "to": "#406080"}], "gradients"),
            ("additional_palette_ids", ["group-b"], "one base palette group"),
        ):
            with self.subTest(field=field):
                palette = valid_palette()
                palette[field] = value
                with self.assertRaisesRegex(ValueError, reason):
                    validate_palette(palette, palette_library_fixture())

        palette = valid_palette()
        palette["extensions"][0]["hex"] = "#203040"
        palette["extensions"][0]["rgb"] = [32, 48, 64]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_palette(palette, palette_library_fixture())

    def test_rejects_undeclared_base_colour_fields(self):
        palette = valid_palette()
        palette["colours"][0]["source"] = "user-reference"

        with self.assertRaisesRegex(ValueError, r"palette colours\[0\].*source"):
            validate_palette(palette, palette_library_fixture())

    def test_rejects_undeclared_nested_extension_fields(self):
        for field, value in (
            ("source", {"kind": "figurebench"}),
            ("source_kind", "user-reference"),
            ("figurebench_palette_id", "figurebench-palette"),
            ("user_reference", "uploaded-colours"),
            ("additional_palette_ids", ["group-b"]),
            ("gradient", {"from": "#203040", "to": "#6E8FA3"}),
            ("unrelated_note", "discard me"),
        ):
            with self.subTest(field=field):
                palette = valid_palette()
                palette["extensions"][0][field] = value
                with self.assertRaisesRegex(ValueError, rf"palette extensions\[0\].*{field}"):
                    validate_palette(palette, palette_library_fixture())

    def test_palette_hex_set_returns_every_active_colour_as_a_frozenset(self):
        palette = validate_palette(valid_palette(), palette_library_fixture())

        self.assertEqual(
            palette_hex_set(palette),
            frozenset({"#203040", "#406080", "#6E8FA3"}),
        )


class TasteGuidanceTests(unittest.TestCase):
    def test_taste_guidance_keeps_palette_lineage_subordinate_to_scientific_constraints(self):
        rules = (ROOT / "references/taste-rules.md").read_text(encoding="utf-8")

        for phrase in (
            "scientific correctness",
            "explicit user constraints",
            "domain conventions",
            "construction provenance",
            "selected multi-colour palette-group lineage",
            "multi-colour palette-group",
            "three dominant colours",
            "fourth dominant hue",
            "web colour-relationship research",
            "exact evidence",
            "second library group",
            "user-reference colours",
            "FigureBench colours",
            "draw.io-like editability",
        ):
            self.assertIn(phrase, rules)
