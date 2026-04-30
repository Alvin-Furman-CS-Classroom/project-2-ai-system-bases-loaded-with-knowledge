"""
Unit tests for src/module4/field_ui.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module4.field_ui import render_field_positions


class TestFieldUI(unittest.TestCase):
    def setUp(self):
        self.assignment = {
            "P": "Pitcher",
            "C": "Catcher",
            "1B": "First Base",
            "2B": "Second Base",
            "3B": "Third Base",
            "SS": "Shortstop",
            "LF": "Left Field",
            "CF": "Center Field",
            "RF": "Right Field",
        }

    def test_render_contains_all_positions(self):
        output = render_field_positions(self.assignment)
        for token in ("LF [", "CF [", "RF [", "3B [", "SS [", "2B [", "1B [", "P [", "C ["):
            self.assertIn(token, output)

    def test_missing_position_raises(self):
        bad = dict(self.assignment)
        del bad["SS"]
        with self.assertRaises(ValueError):
            render_field_positions(bad)


if __name__ == "__main__":
    unittest.main()
