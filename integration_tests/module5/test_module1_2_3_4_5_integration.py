"""
Integration test: Modules 1-4 outputs feeding Module 5 planning.
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
from module5.planner import generate_adaptive_plan


_ROOT = Path(__file__).resolve().parent.parent.parent
_MATCHUP_JSON = _ROOT / "test_data" / "matchup_stats.json"
_DEFENSIVE_JSON = _ROOT / "test_data" / "defensive_stats.json"


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
        existing = set(eligibility.setdefault(pname, ["P"]))
        for pos in normalized:
            if pos in DEFAULT_POSITIONS:
                existing.add(pos)
        eligibility[pname] = list(existing)
    return eligibility


def _batter_stats_from_matchup_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for batter in data.get("batters", []):
        name = batter.get("name")
        if not name:
            continue
        out[name] = {
            "obp": float(batter["obp"]),
            "slg": float(batter["slg"]),
            "hr": int(batter["hr"]),
            "rbi": int(batter["rbi"]),
        }
    return out


class TestModule1To5Integration(unittest.TestCase):
    def test_end_to_end_pipeline_produces_valid_explainable_recommendations(self):
        offensive_scores = analyze_matchup_performance(str(_MATCHUP_JSON))
        defensive_scores_nested = analyze_defensive_performance(
            str(_DEFENSIVE_JSON), predict_all_positions=False
        )
        eligibility = _load_position_eligibility(offensive_scores, _DEFENSIVE_JSON)

        assignment = assign_defensive_positions(
            offensive_scores, defensive_scores_nested, eligibility
        )
        selected_players = list(assignment.values())
        self.assertEqual(len(selected_players), 9)
        self.assertEqual(len(set(selected_players)), 9)

        batter_stats = _batter_stats_from_matchup_json(_MATCHUP_JSON)
        offensive_subset = {p: float(offensive_scores[p]) for p in selected_players}
        batting_order_result = optimize_batting_order(
            selected_players,
            batter_stats,
            offensive_scores=offensive_subset,
            seed=42,
            generations=60,
            population_size=60,
        )
        batting_order = batting_order_result["optimized_order"]

        flat_defense = {}
        for pos, player in assignment.items():
            player_pos_scores = defensive_scores_nested.get(player, {})
            # Module 2 does not grade pitchers at "P"; use neutral fallback.
            flat_defense[player] = float(player_pos_scores.get(pos, 0.0))

        game_state = {
            "inning": 8,
            "half": "top",
            "outs": 1,
            "score_for": 2,
            "score_against": 3,
            "bases": [True, False, False],
            "substitutions_used": 1,
            "substitutions_limit": 5,
            "pitcher_fatigue": 0.65,
        }
        current_lineup = {"batting_order": batting_order, "field_positions": assignment}
        bench_players = [
            {"name": "BenchPH", "roles": ["PH"], "offense_score": 84},
            {"name": "BenchPR", "roles": ["PR"], "speed": 92},
            {"name": "BenchDEF", "roles": ["DEF"], "defense_score": 86},
        ]
        offensive_with_bench = {
            **offensive_subset,
            "BenchPH": 84.0,
            "BenchPR": 52.0,
            "BenchDEF": 48.0,
        }
        defensive_with_bench = {**flat_defense, "BenchDEF": 86.0}

        plan = generate_adaptive_plan(
            game_state,
            current_lineup,
            bench_players,
            offensive_with_bench,
            defensive_with_bench,
            innings_ahead=3,
        )

        self.assertIn("recommendations", plan)
        self.assertIn("multi_inning_plan", plan)
        self.assertTrue(plan["recommendations"], "expected at least one recommendation")

        for rec in plan["recommendations"]:
            self.assertIn("action_type", rec)
            self.assertIn("inning_window", rec)
            self.assertIn("reason", rec)
            self.assertTrue(str(rec["reason"]).strip())

        # Assert no bench player is used by conflicting simultaneous recommendations.
        used_by_bench = {}
        for rec in plan["recommendations"]:
            bench_name = str(rec.get("bench_player", "")).strip()
            if not bench_name:
                continue
            win = rec["inning_window"]
            for prev in used_by_bench.get(bench_name, []):
                overlaps = int(win[0]) <= int(prev[1]) and int(prev[0]) <= int(win[1])
                self.assertFalse(
                    overlaps,
                    msg=f"bench player {bench_name} used in overlapping windows {win} and {prev}",
                )
            used_by_bench.setdefault(bench_name, []).append(win)


if __name__ == "__main__":
    unittest.main()
