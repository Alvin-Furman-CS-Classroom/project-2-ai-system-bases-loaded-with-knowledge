"""
Public planning API for Module 5.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from module5.game_state import (
    GameStateValidationError,
    NormalizedGameState,
    normalize_game_state,
    validate_bench_players,
    validate_current_lineup,
)


class PlanningInputError(ValueError):
    """Raised when planner inputs are invalid."""


def _validate_score_map(name: str, score_map: Mapping[str, Any]) -> Dict[str, float]:
    if not isinstance(score_map, Mapping):
        raise PlanningInputError(f"{name} must be a mapping of player -> numeric score")
    validated: Dict[str, float] = {}
    for player, score in score_map.items():
        if not isinstance(player, str) or not player.strip():
            raise PlanningInputError(f"{name} has invalid player key {player!r}")
        try:
            score_value = float(score)
        except (TypeError, ValueError) as exc:
            raise PlanningInputError(f"{name} score for {player!r} must be numeric") from exc
        validated[player.strip()] = score_value
    return validated


def _make_default_recommendations(
    state: NormalizedGameState,
    offensive_scores: Mapping[str, float],
    defensive_scores: Mapping[str, float],
    bench_players: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Deterministic fallback recommendations for Person A baseline planner.
    """
    recommendations: List[Dict[str, Any]] = []
    if state.substitutions_remaining <= 0 or not bench_players:
        return recommendations

    lead_protection = state.score_diff > 0 and state.inning >= 7
    chasing_offense = state.score_diff < 0 and state.inning >= 6

    if lead_protection:
        best_def_player, best_def_score = max(
            defensive_scores.items(), key=lambda item: (item[1], item[0])
        )
        recommendations.append(
            {
                "action_type": "defensive_replacement_watch",
                "inning_window": [state.inning, min(state.inning + 1, 9)],
                "priority": 1,
                "confidence": 0.65,
                "reason": (
                    "Protecting a late lead: monitor defensive substitution opportunities "
                    f"around top defender {best_def_player} ({best_def_score:.1f})."
                ),
            }
        )

    if chasing_offense:
        best_off_player, best_off_score = max(
            offensive_scores.items(), key=lambda item: (item[1], item[0])
        )
        recommendations.append(
            {
                "action_type": "pinch_hitter_watch",
                "inning_window": [state.inning, min(state.inning + 1, 9)],
                "priority": 1 if not recommendations else 2,
                "confidence": 0.62,
                "reason": (
                    "Trailing in middle/late innings: prepare offense-focused substitutions "
                    f"near strongest bat profile {best_off_player} ({best_off_score:.1f})."
                ),
            }
        )

    if state.pitcher_fatigue >= 0.75:
        recommendations.append(
            {
                "action_type": "bullpen_alert",
                "inning_window": [state.inning, state.inning],
                "priority": 1 if not recommendations else 2,
                "confidence": 0.7,
                "reason": "Pitcher fatigue is elevated; prepare contingency pitching plan.",
            }
        )

    return recommendations


def _build_multi_inning_plan(
    state: NormalizedGameState, innings_ahead: int, recommendations: Sequence[Mapping[str, Any]]
) -> List[Dict[str, Any]]:
    horizon_end = state.inning + max(1, innings_ahead) - 1
    plan = []
    for inning in range(state.inning, horizon_end + 1):
        inning_recs = [
            rec
            for rec in recommendations
            if int(rec["inning_window"][0]) <= inning <= int(rec["inning_window"][1])
        ]
        plan.append(
            {
                "inning": inning,
                "half": state.half if inning == state.inning else "tbd",
                "objective": "protect_lead"
                if state.score_diff > 0
                else "recover_runs"
                if state.score_diff < 0
                else "maintain_pressure",
                "recommended_actions": inning_recs,
            }
        )
    return plan


def generate_adaptive_plan(
    game_state: Mapping[str, Any],
    current_lineup: Mapping[str, Any],
    bench_players: Sequence[Mapping[str, Any]],
    offensive_scores: Mapping[str, Any],
    defensive_scores: Mapping[str, Any],
    *,
    innings_ahead: int = 3,
) -> Dict[str, Any]:
    """
    Generate adaptive recommendations and a multi-inning plan.
    """
    try:
        normalized_state = normalize_game_state(game_state)
        normalized_batting_order = validate_current_lineup(current_lineup)
        validate_bench_players(bench_players)
    except GameStateValidationError as exc:
        raise PlanningInputError(str(exc)) from exc

    if innings_ahead < 1:
        raise PlanningInputError("innings_ahead must be >= 1")

    normalized_offense = _validate_score_map("offensive_scores", offensive_scores)
    normalized_defense = _validate_score_map("defensive_scores", defensive_scores)
    if not normalized_offense:
        raise PlanningInputError("offensive_scores must not be empty")
    if not normalized_defense:
        raise PlanningInputError("defensive_scores must not be empty")

    recommendations = _make_default_recommendations(
        normalized_state,
        normalized_offense,
        normalized_defense,
        bench_players,
    )
    recommendations = sorted(
        recommendations,
        key=lambda r: (int(r["priority"]), -float(r["confidence"]), r["action_type"]),
    )

    return {
        "recommendations": recommendations,
        "multi_inning_plan": _build_multi_inning_plan(
            normalized_state, innings_ahead, recommendations
        ),
        "summary": {
            "start_inning": normalized_state.inning,
            "horizon_innings": innings_ahead,
            "score_diff": normalized_state.score_diff,
            "substitutions_remaining": normalized_state.substitutions_remaining,
            "lineup_snapshot": normalized_batting_order,
        },
    }
