"""
Integration test: Module 3 defensive assignment -> Module 4 batting order.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module1.matchup_analyzer import analyze_matchup_performance
from module2.defensive_analyzer import analyze_defensive_performance
from module3.position_assignment import DEFAULT_POSITIONS, assign_defensive_positions
from module4.batting_order import optimize_batting_order


_TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "test_data"
_MATCHUP_JSON = _TEST_DATA_DIR / "matchup_stats.json"
_DEFENSIVE_JSON = _TEST_DATA_DIR / "defensive_stats.json"


def _load_position_eligibility(offensive_scores: dict, defensive_json: Path) -> dict:
    with open(defensive_json, "r", encoding="utf-8") as f:
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
        eligibility.setdefault(pname, ["P"])
        existing = set(eligibility[pname])
        for pos in normalized:
            if pos in DEFAULT_POSITIONS:
                existing.add(pos)
        eligibility[pname] = list(existing)

    return eligibility


def _batter_stats_from_matchup_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for b in data.get("batters", []):
        name = b.get("name")
        if not name:
            continue
        out[name] = {
            "obp": float(b["obp"]),
            "slg": float(b["slg"]),
            "hr": int(b["hr"]),
            "rbi": int(b["rbi"]),
        }
    return out


class TestModule3_4Integration(unittest.TestCase):
    def test_m3_assignment_to_m4_ordering(self):
        offensive_scores = analyze_matchup_performance(str(_MATCHUP_JSON))
        defensive_scores = analyze_defensive_performance(
            str(_DEFENSIVE_JSON), predict_all_positions=False
        )
        eligibility = _load_position_eligibility(offensive_scores, _DEFENSIVE_JSON)

        assignment = assign_defensive_positions(
            offensive_scores, defensive_scores, eligibility
        )
        selected = list(assignment.values())
        self.assertEqual(len(selected), 9)
        self.assertEqual(len(set(selected)), 9)

        batter_stats = _batter_stats_from_matchup_json(_MATCHUP_JSON)
        for p in selected:
            self.assertIn(p, batter_stats, msg=f"batter stats missing for {p!r}")

        offensive_subset = {p: offensive_scores[p] for p in selected}

        result = optimize_batting_order(
            selected,
            batter_stats,
            offensive_scores=offensive_subset,
            seed=42,
            generations=80,
            population_size=80,
        )
        order = result["optimized_order"]
        self.assertEqual(len(order), 9)
        self.assertEqual(len(set(order)), 9)
        self.assertEqual(set(order), set(selected))
        self.assertIn("best_fitness", result)
        self.assertIn("generations_run", result)
        self.assertEqual(result["seed"], 42)


if __name__ == "__main__":
    unittest.main()
"""
Integration test: Module 3 defensive assignment -> Module 4 batting order.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module1.matchup_analyzer import analyze_matchup_performance
from module2.defensive_analyzer import analyze_defensive_performance
from module3.position_assignment import DEFAULT_POSITIONS, assign_defensive_positions
from module4.batting_order import optimize_batting_order


_TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "test_data"
_MATCHUP_JSON = _TEST_DATA_DIR / "matchup_stats.json"
_DEFENSIVE_JSON = _TEST_DATA_DIR / "defensive_stats.json"


def _load_position_eligibility(offensive_scores: dict, defensive_json: Path) -> dict:
    with open(defensive_json, "r", encoding="utf-8") as f:
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
        eligibility.setdefault(pname, ["P"])
        existing = set(eligibility[pname])
        for pos in normalized:
            if pos in DEFAULT_POSITIONS:
                existing.add(pos)
        eligibility[pname] = list(existing)

    return eligibility


def _batter_stats_from_matchup_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for b in data.get("batters", []):
        name = b.get("name")
        if not name:
            continue
        out[name] = {
            "obp": float(b["obp"]),
            "slg": float(b["slg"]),
            "hr": int(b["hr"]),
            "rbi": int(b["rbi"]),
        }
    return out


class TestModule3_4Integration(unittest.TestCase):
    def test_m3_assignment_to_m4_ordering(self):
        offensive_scores = analyze_matchup_performance(str(_MATCHUP_JSON))
        defensive_scores = analyze_defensive_performance(
            str(_DEFENSIVE_JSON), predict_all_positions=False
        )
        eligibility = _load_position_eligibility(offensive_scores, _DEFENSIVE_JSON)

        assignment = assign_defensive_positions(
            offensive_scores, defensive_scores, eligibility
        )
        selected = list(assignment.values())
        self.assertEqual(len(selected), 9)
        self.assertEqual(len(set(selected)), 9)

        batter_stats = _batter_stats_from_matchup_json(_MATCHUP_JSON)
        for p in selected:
            self.assertIn(p, batter_stats, msg=f"batter stats missing for {p!r}")

        offensive_subset = {p: offensive_scores[p] for p in selected}

        result = optimize_batting_order(
            selected,
            batter_stats,
            offensive_scores=offensive_subset,
            seed=42,
            generations=80,
            population_size=80,
        )
        order = result["optimized_order"]
        self.assertEqual(len(order), 9)
        self.assertEqual(len(set(order)), 9)
        self.assertEqual(set(order), set(selected))
        self.assertIn("best_fitness", result)
        self.assertIn("generations_run", result)
        self.assertEqual(result["seed"], 42)


if __name__ == "__main__":
    unittest.main()
