"""
Unit tests for src/module5/strategy_rules.py (Person B deliverables).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module5.strategy_rules import (
    StrategyRuleError,
    evaluate_strategy_recommendations,
    resolve_recommendation_conflicts,
)


def _state():
    return {
        "inning": 8,
        "half": "top",
        "outs": 1,
        "score_for": 2,
        "score_against": 3,
        "bases": [True, False, False],
        "substitutions_used": 1,
        "substitutions_limit": 5,
        "pitcher_fatigue": 0.4,
    }


def _lineup():
    names = [f"P{i}" for i in range(1, 10)]
    return {
        "batting_order": names,
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


def _offense_scores():
    scores = {f"P{i}": 50 + i for i in range(1, 10)}
    scores["BenchGoodPH"] = 88.0
    scores["BenchWeakPH"] = 60.0
    return scores


def _defense_scores():
    scores = {f"P{i}": 45 + i for i in range(1, 10)}
    scores["BenchDef"] = 84.0
    return scores


class TestStrategyRules(unittest.TestCase):
    def test_favorable_scenario_ranks_above_poor_choice(self):
        bench = [
            {"name": "BenchGoodPH", "roles": ["PH"]},
            {"name": "BenchWeakPH", "roles": ["PH"]},
            {"name": "BenchPR", "roles": ["PR"], "speed": 93},
            {"name": "BenchDef", "roles": ["DEF"]},
        ]
        recs = evaluate_strategy_recommendations(
            state=_state(),
            current_lineup=_lineup(),
            bench_players=bench,
            offensive_scores=_offense_scores(),
            defensive_scores=_defense_scores(),
            innings_ahead=3,
        )
        pinch_hitter = [r for r in recs if r["action_type"] == "pinch_hitter"][0]
        self.assertEqual(pinch_hitter["bench_player"], "BenchGoodPH")

    def test_missing_player_metrics_or_eligibility_raises(self):
        bad_offense = {f"P{i}": 50 + i for i in range(1, 9)}  # missing P9
        with self.assertRaises(StrategyRuleError):
            evaluate_strategy_recommendations(
                state=_state(),
                current_lineup=_lineup(),
                bench_players=[{"name": "BenchPH", "roles": ["PH"]}],
                offensive_scores=bad_offense,
                defensive_scores=_defense_scores(),
                innings_ahead=2,
            )

    def test_incompatible_actions_filtered(self):
        raw = [
            {
                "action_type": "pinch_hitter",
                "inning_window": [8, 9],
                "priority": 1,
                "confidence": 0.8,
                "score": 0.8,
                "bench_player": "BenchA",
            },
            {
                "action_type": "defensive_replacement",
                "inning_window": [8, 8],
                "priority": 1,
                "confidence": 0.7,
                "score": 0.4,
                "bench_player": "BenchA",
            },
            {
                "action_type": "lineup_matchup_adjustment",
                "inning_window": [9, 10],
                "priority": 2,
                "confidence": 0.6,
                "score": 0.3,
                "bench_player": "",
            },
        ]
        cleaned = resolve_recommendation_conflicts(raw)
        action_types = [r["action_type"] for r in cleaned]
        self.assertIn("pinch_hitter", action_types)
        self.assertNotIn("defensive_replacement", action_types)


if __name__ == "__main__":
    unittest.main()
