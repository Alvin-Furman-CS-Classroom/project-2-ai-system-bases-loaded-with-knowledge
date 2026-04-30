"""
Integration test for Module 1 + Module 2 + Module 3.
"""

import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module1.matchup_analyzer import analyze_matchup_performance
from module2.defensive_analyzer import analyze_defensive_performance
from module3.position_assignment import assign_defensive_positions, DEFAULT_POSITIONS, FIELD_POSITIONS


_TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "test_data"
_MATCHUP_JSON = _TEST_DATA_DIR / "matchup_stats.json"
_DEFENSIVE_JSON = _TEST_DATA_DIR / "defensive_stats.json"


def _load_position_eligibility(offensive_scores: dict) -> dict:
    """
    Build {player_name: [positions...]} from defensive_stats.json, while allowing
    every offensive player to also be eligible for the pitcher slot 'P'.
    """
    with open(_DEFENSIVE_JSON, "r", encoding="utf-8") as f:
        defensive_players = json.load(f)

    eligibility = {player: ["P"] for player in offensive_scores.keys()}

    for pdata in defensive_players:
        pname = pdata.get("name") or pdata.get("player_name")
        if not pname:
            continue

        positions = pdata.get("positions", [])
        if not isinstance(positions, list):
            continue

        normalized = [str(p).strip().upper() for p in positions if str(p).strip()]

        # Preserve the already-added 'P' eligibility.
        eligibility.setdefault(pname, ["P"])
        existing = set(eligibility[pname])
        for pos in normalized:
            if pos in DEFAULT_POSITIONS:
                existing.add(pos)
        eligibility[pname] = list(existing)

    return eligibility


class TestModule1_2_3Integration(unittest.TestCase):
    def test_integration_outputs_valid_assignment(self):
        offensive_scores = analyze_matchup_performance(str(_MATCHUP_JSON))

        # Align defensive_scores with eligibility (both use "played" positions).
        defensive_scores = analyze_defensive_performance(str(_DEFENSIVE_JSON), predict_all_positions=False)

        eligibility = _load_position_eligibility(offensive_scores)

        result = assign_defensive_positions(offensive_scores, defensive_scores, eligibility)

        self.assertEqual(set(result.keys()), set(DEFAULT_POSITIONS))
        self.assertEqual(len(set(result.values())), 9, "Players must be unique across positions")

        # Verify assignments exist in sources and respect per-position score availability.
        for pos, player in result.items():
            self.assertIn(player, offensive_scores)
            self.assertIn(pos, DEFAULT_POSITIONS)

            if pos == "P":
                continue

            self.assertIn(player, defensive_scores)
            self.assertIn(pos, defensive_scores[player])
            self.assertIn(pos, eligibility[player])

        # Optional sanity: all field positions should have some defense component.
        for pos in FIELD_POSITIONS:
            player = result[pos]
            self.assertGreaterEqual(defensive_scores[player][pos], 0.0)
            self.assertLessEqual(defensive_scores[player][pos], 100.0)


if __name__ == "__main__":
    unittest.main()

