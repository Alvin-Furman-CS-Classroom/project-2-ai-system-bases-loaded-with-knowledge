"""
Helpers to compute real Module 4 UI data from module pipelines.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from module1.matchup_analyzer import analyze_matchup_performance
from module2.defensive_analyzer import analyze_defensive_performance
from module3.position_assignment import DEFAULT_POSITIONS, assign_defensive_positions
from module4.batting_order import optimize_batting_order

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DATA_DIR = REPO_ROOT / "test_data"
MATCHUP_JSON = TEST_DATA_DIR / "matchup_stats.json"
DEFENSIVE_JSON = TEST_DATA_DIR / "defensive_stats.json"


def _load_position_eligibility(offensive_scores: Dict[str, float]) -> Dict[str, List[str]]:
    with open(DEFENSIVE_JSON, "r", encoding="utf-8") as f:
        defensive_players = json.load(f)

    eligibility: Dict[str, List[str]] = {player: ["P"] for player in offensive_scores.keys()}
    for pdata in defensive_players:
        pname = pdata.get("name") or pdata.get("player_name")
        if not pname:
            continue
        positions = pdata.get("positions", [])
        if not isinstance(positions, list):
            continue
        existing = set(eligibility.setdefault(pname, ["P"]))
        for pos in positions:
            pos_name = str(pos).strip().upper()
            if pos_name in DEFAULT_POSITIONS:
                existing.add(pos_name)
        eligibility[pname] = list(existing)
    return eligibility


def _batter_stats_from_matchup_json() -> Dict[str, Dict[str, float]]:
    with open(MATCHUP_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    out: Dict[str, Dict[str, float]] = {}
    for b in data.get("batters", []):
        name = b.get("name")
        if not name:
            continue
        out[name] = {
            "obp": float(b["obp"]),
            "slg": float(b["slg"]),
            "hr": float(b["hr"]),
            "rbi": float(b["rbi"]),
        }
    return out


def compute_module4_ui_inputs(seed: int = 42) -> Tuple[List[str], Dict[str, str]]:
    """
    Return (batting_order, position_assignment) from real module data/files.
    """
    offensive_scores = analyze_matchup_performance(str(MATCHUP_JSON))
    defensive_scores = analyze_defensive_performance(
        str(DEFENSIVE_JSON), predict_all_positions=False
    )
    eligibility = _load_position_eligibility(offensive_scores)
    assignment = assign_defensive_positions(offensive_scores, defensive_scores, eligibility)

    selected = list(assignment.values())
    batter_stats = _batter_stats_from_matchup_json()
    offensive_subset = {p: offensive_scores[p] for p in selected}
    optimized = optimize_batting_order(
        selected,
        batter_stats,
        offensive_scores=offensive_subset,
        seed=seed,
        generations=80,
        population_size=80,
    )
    return optimized["optimized_order"], assignment
