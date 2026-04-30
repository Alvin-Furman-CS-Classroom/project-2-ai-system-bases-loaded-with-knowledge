"""
Unit tests for src/module5/planner.py (Person A deliverables).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module5.planner import PlanningInputError, generate_adaptive_plan


def _game_state():
    return {
        "inning": 8,
        "half": "top",
        "outs": 1,
        "score_for": 2,
        "score_against": 3,
        "bases": [False, True, False],
        "substitutions_used": 1,
        "substitutions_limit": 5,
        "pitcher_fatigue": 0.82,
    }


def _lineup():
    players = [f"P{i}" for i in range(1, 10)]
    return {
        "batting_order": players,
        "field_positions": {
            "P": "P1",
            "C": "P2",
            "1B": "P3",
            "2B": "P4",
            "3B": "P5",
            "SS": "P6",
            "LF": "P7",
            "CF": "P8",
            "RF": "P9",
        },
    }


def _bench():
    return [
        {"name": "BenchA", "roles": ["PH", "LF"]},
        {"name": "BenchB", "roles": ["PR", "CF"]},
    ]


def _off_scores():
    return {f"P{i}": 50 + i for i in range(1, 10)}


def _def_scores():
    return {f"P{i}": 40 + i for i in range(1, 10)}


class TestPlanner(unittest.TestCase):
    def test_output_shape_and_inning_window(self):
        plan = generate_adaptive_plan(
            _game_state(),
            _lineup(),
            _bench(),
            _off_scores(),
            _def_scores(),
            innings_ahead=3,
        )
        self.assertIn("recommendations", plan)
        self.assertIn("multi_inning_plan", plan)
        self.assertIn("summary", plan)
        self.assertEqual(len(plan["multi_inning_plan"]), 3)
        self.assertEqual(plan["multi_inning_plan"][0]["inning"], 8)
        self.assertEqual(plan["multi_inning_plan"][-1]["inning"], 10)

    def test_deterministic_same_inputs(self):
        p1 = generate_adaptive_plan(
            _game_state(),
            _lineup(),
            _bench(),
            _off_scores(),
            _def_scores(),
            innings_ahead=2,
        )
        p2 = generate_adaptive_plan(
            _game_state(),
            _lineup(),
            _bench(),
            _off_scores(),
            _def_scores(),
            innings_ahead=2,
        )
        self.assertEqual(p1, p2)

    def test_empty_bench_yields_no_substitution_recommendations(self):
        plan = generate_adaptive_plan(
            _game_state(),
            _lineup(),
            [],
            _off_scores(),
            _def_scores(),
        )
        action_types = [r["action_type"] for r in plan["recommendations"]]
        self.assertNotIn("pinch_hitter_watch", action_types)
        self.assertNotIn("defensive_replacement_watch", action_types)

    def test_invalid_lineup_raises(self):
        lineup = _lineup()
        lineup["batting_order"] = lineup["batting_order"][:-1]
        with self.assertRaises(PlanningInputError):
            generate_adaptive_plan(
                _game_state(),
                lineup,
                _bench(),
                _off_scores(),
                _def_scores(),
            )


if __name__ == "__main__":
    unittest.main()
