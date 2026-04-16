"""
Helpers to compute real Module 4 UI data from module pipelines.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from module1.matchup_analyzer import analyze_matchup_performance
from module2.defensive_analyzer import analyze_defensive_performance
from module3.position_assignment import DEFAULT_POSITIONS, assign_defensive_positions
from module4.batting_order import optimize_batting_order
from module5.planner import generate_adaptive_plan

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DATA_DIR = REPO_ROOT / "test_data"
MATCHUP_JSON = TEST_DATA_DIR / "matchup_stats.json"
DEFENSIVE_JSON = TEST_DATA_DIR / "defensive_stats.json"
UI_POSITIONS = [pos for pos in DEFAULT_POSITIONS if pos != "P"] + ["DH"]
DEFENSIVE_FIELD_POSITIONS = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]


def _load_position_eligibility(offensive_scores: Dict[str, float]) -> Dict[str, List[str]]:
    with open(DEFENSIVE_JSON, "r", encoding="utf-8") as f:
        defensive_players = json.load(f)

    eligibility: Dict[str, List[str]] = {player: ["DH"] for player in offensive_scores.keys()}
    for pdata in defensive_players:
        pname = pdata.get("name") or pdata.get("player_name")
        if not pname:
            continue
        positions = pdata.get("positions", [])
        if not isinstance(positions, list):
            continue
        existing = set(eligibility.setdefault(pname, ["DH"]))
        for pos in positions:
            pos_name = str(pos).strip().upper()
            if pos_name in UI_POSITIONS:
                existing.add(pos_name)
        existing.add("DH")
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
    # DH has no fielding component; set neutral defensive score for CSP compatibility.
    for player in offensive_scores:
        defensive_scores.setdefault(player, {})["DH"] = 0.0
    eligibility = _load_position_eligibility(offensive_scores)
    assignment = assign_defensive_positions(
        offensive_scores,
        defensive_scores,
        eligibility,
        positions=UI_POSITIONS,
    )

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


def compute_outfield_profiles(position_assignment: Dict[str, str]) -> Dict[str, Dict[str, float]]:
    """
    Return per-player outfield defensive scores for LF/CF/RF confidence calculations.
    """
    defensive_scores = analyze_defensive_performance(str(DEFENSIVE_JSON), predict_all_positions=False)
    outfield_positions = ("LF", "CF", "RF")
    profiles: Dict[str, Dict[str, float]] = {}
    for player in set(position_assignment.values()):
        per_pos = defensive_scores.get(player, {})
        profiles[player] = {
            of_pos: float(per_pos.get(of_pos, 0.0)) for of_pos in outfield_positions
        }
    return profiles


def compute_outfield_profiles_predicted(
    position_assignment: Dict[str, str],
) -> Dict[str, Dict[str, float]]:
    """
    Return projected outfield scores (includes unplayed positions).
    """
    defensive_scores = analyze_defensive_performance(str(DEFENSIVE_JSON), predict_all_positions=True)
    outfield_positions = ("LF", "CF", "RF")
    profiles: Dict[str, Dict[str, float]] = {}
    for player in set(position_assignment.values()):
        per_pos = defensive_scores.get(player, {})
        profiles[player] = {
            of_pos: float(per_pos.get(of_pos, 0.0)) for of_pos in outfield_positions
        }
    return profiles


def compute_defensive_profiles(position_assignment: Dict[str, str]) -> Dict[str, Dict[str, float]]:
    """
    Return per-player defensive scores across all fielding positions.
    """
    defensive_scores = analyze_defensive_performance(str(DEFENSIVE_JSON), predict_all_positions=False)
    profiles: Dict[str, Dict[str, float]] = {}
    for player in set(position_assignment.values()):
        per_pos = defensive_scores.get(player, {})
        profiles[player] = {
            pos: float(per_pos.get(pos, 0.0)) for pos in DEFENSIVE_FIELD_POSITIONS
        }
    return profiles


def compute_eligibility_profiles(position_assignment: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Return allowed positions for selected players (plus universal DH).
    """
    selected_players = set(position_assignment.values())
    with open(DEFENSIVE_JSON, "r", encoding="utf-8") as f:
        defensive_players = json.load(f)

    eligibility: Dict[str, List[str]] = {player: ["DH"] for player in selected_players}
    for pdata in defensive_players:
        pname = pdata.get("name") or pdata.get("player_name")
        if pname not in selected_players:
            continue
        positions = pdata.get("positions", [])
        if not isinstance(positions, list):
            continue
        valid = {"DH"}
        for pos in positions:
            pos_name = str(pos).strip().upper()
            if pos_name in DEFENSIVE_FIELD_POSITIONS:
                valid.add(pos_name)
        # UI interaction rule: outfielders are swappable across OF spots.
        # If a player can play any OF position, allow LF/CF/RF for manual drag demos.
        if {"LF", "CF", "RF"} & valid:
            valid.update({"LF", "CF", "RF"})
        eligibility[pname] = sorted(valid)
    return eligibility


def compute_offensive_profiles(position_assignment: Dict[str, str]) -> Dict[str, float]:
    """
    Return per-player offensive scores used for DH optimization.
    """
    offensive_scores = analyze_matchup_performance(str(MATCHUP_JSON))
    return {
        player: float(offensive_scores.get(player, 0.0))
        for player in set(position_assignment.values())
    }


def compute_module5_ui_plan(seed: int = 42) -> Dict[str, object]:
    """
    Return Module 5 plan using Module 1-4 pipeline outputs.
    """
    batting_order, assignment = compute_module4_ui_inputs(seed=seed)
    selected = list(assignment.values())
    offensive_scores = analyze_matchup_performance(str(MATCHUP_JSON))
    defensive_full = analyze_defensive_performance(
        str(DEFENSIVE_JSON), predict_all_positions=False
    )

    offensive_subset = {player: float(offensive_scores[player]) for player in selected}
    defensive_subset = {}
    for player in selected:
        positions = defensive_full.get(player, {})
        pos = next((k for k, v in assignment.items() if v == player), None)
        defensive_subset[player] = float(positions.get(pos, 0.0)) if pos else 0.0

    game_state = {
        "inning": 7,
        "half": "bottom",
        "outs": 1,
        "score_for": 4,
        "score_against": 3,
        "bases": [True, False, True],
        "substitutions_used": 2,
        "substitutions_limit": 5,
        "pitcher_fatigue": 0.0,
    }
    bench_players = [
        {"name": "Bench Speed", "roles": ["PR", "CF", "LF"]},
        {"name": "Bench Power", "roles": ["PH", "1B", "RF"]},
    ]
    current_lineup = {
        "batting_order": batting_order,
        "field_positions": assignment,
    }

    return generate_adaptive_plan(
        game_state,
        current_lineup,
        bench_players,
        offensive_subset,
        defensive_subset,
        innings_ahead=3,
    )


def compute_ui_bundle(seed: int = 42) -> Dict[str, Any]:
    """
    Build one end-to-end data bundle for Module 4/5 dashboard.

    This ensures the UI is sourced from a single consistent pipeline run:
    Module 1 -> Module 2 -> Module 3 -> Module 4 -> Module 5.
    """
    offensive_scores = analyze_matchup_performance(str(MATCHUP_JSON))
    defensive_scores = analyze_defensive_performance(
        str(DEFENSIVE_JSON), predict_all_positions=False
    )
    for player in offensive_scores:
        defensive_scores.setdefault(player, {})["DH"] = 0.0

    eligibility = _load_position_eligibility(offensive_scores)
    assignment = assign_defensive_positions(
        offensive_scores,
        defensive_scores,
        eligibility,
        positions=UI_POSITIONS,
    )

    selected_players = list(assignment.values())
    batter_stats = _batter_stats_from_matchup_json()
    offensive_subset = {p: float(offensive_scores[p]) for p in selected_players}
    optimized = optimize_batting_order(
        selected_players,
        batter_stats,
        offensive_scores=offensive_subset,
        seed=seed,
        generations=80,
        population_size=80,
    )
    batting_order = optimized["optimized_order"]

    flat_defense: Dict[str, float] = {}
    for pos, player in assignment.items():
        flat_defense[player] = float(defensive_scores.get(player, {}).get(pos, 0.0))

    game_state = {
        "inning": 7,
        "half": "bottom",
        "outs": 1,
        "score_for": 4,
        "score_against": 3,
        "bases": [True, False, True],
        "substitutions_used": 2,
        "substitutions_limit": 5,
        "pitcher_fatigue": 0.0,
    }
    bench_players = [
        {"name": "Bench Speed", "roles": ["PR", "CF", "LF"]},
        {"name": "Bench Power", "roles": ["PH", "1B", "RF"]},
    ]
    current_lineup = {"batting_order": batting_order, "field_positions": assignment}
    module5_plan = generate_adaptive_plan(
        game_state,
        current_lineup,
        bench_players,
        offensive_subset,
        flat_defense,
        innings_ahead=3,
    )

    planning_offense = dict(offensive_subset)
    planning_defense = dict(flat_defense)
    for b in bench_players:
        bname = b["name"]
        planning_offense[bname] = float(offensive_scores.get(bname, 58.0))
        nest = defensive_scores.get(bname) or {}
        planning_defense[bname] = float(max(nest.values()) if nest else 50.0)

    return {
        "batting_order": batting_order,
        "assignment": assignment,
        "module5_plan": module5_plan,
        "replan_context": {
            "game_state": game_state,
            "bench_players": bench_players,
            "offensive_scores": planning_offense,
            "defensive_scores": planning_defense,
            "innings_ahead": 3,
        },
        "outfield_profiles": compute_outfield_profiles(assignment),
        "outfield_profiles_predicted": compute_outfield_profiles_predicted(assignment),
        "defensive_profiles": compute_defensive_profiles(assignment),
        "offensive_profiles": compute_offensive_profiles(assignment),
        "eligibility_profiles": compute_eligibility_profiles(assignment),
        "pipeline_context": {
            "module1_players_scored": len(offensive_scores),
            "module2_players_scored": len(defensive_scores),
            "module3_positions_assigned": len(assignment),
            "module4_best_fitness": float(optimized["best_fitness"]),
            "module4_generations_run": int(optimized["generations_run"]),
            "module5_recommendations": len(module5_plan.get("recommendations", [])),
            "data_sources": {
                "matchup_stats": str(MATCHUP_JSON),
                "defensive_stats": str(DEFENSIVE_JSON),
            },
            "seed": seed,
        },
    }
