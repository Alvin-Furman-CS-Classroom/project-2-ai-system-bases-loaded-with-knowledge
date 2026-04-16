"""
Strategy rule evaluation for Module 5 adaptive planning.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple


class StrategyRuleError(ValueError):
    """Raised when strategy-rule inputs are invalid."""


# Positions where defensive ability matters on the field (excludes DH; no pitcher module).
FIELD_POSITIONS_DEFENSIVE = frozenset({"C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"})

WEIGHTS: Dict[str, float] = {
    "impact": 0.5,
    "urgency": 0.2,
    "feasibility": 0.2,
    "risk_penalty": 0.1,
}


def _require_numeric(name: str, value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise StrategyRuleError(f"{name} must be numeric") from exc


def _window(start_inning: int, innings_ahead: int) -> List[int]:
    end = min(12, start_inning + max(1, innings_ahead) - 1)
    return [start_inning, end]


def _weighted_score(*, impact: float, urgency: float, feasibility: float, risk: float) -> float:
    return (
        WEIGHTS["impact"] * impact
        + WEIGHTS["urgency"] * urgency
        + WEIGHTS["feasibility"] * feasibility
        - WEIGHTS["risk_penalty"] * risk
    )


def _player_name(player: Mapping[str, Any], idx: int) -> str:
    if "name" not in player:
        raise StrategyRuleError(f"bench player #{idx} missing required key 'name'")
    name = player["name"]
    if not isinstance(name, str) or not name.strip():
        raise StrategyRuleError(f"bench player #{idx} has invalid name {name!r}")
    return name.strip()


def _player_roles(player: Mapping[str, Any], name: str) -> List[str]:
    roles = player.get("roles")
    if roles is None:
        raise StrategyRuleError(f"bench player {name!r} missing required key 'roles'")
    if isinstance(roles, str):
        raise StrategyRuleError(f"bench player {name!r} roles must be an iterable of strings")
    role_list = [str(r).strip().upper() for r in roles if str(r).strip()]
    if not role_list:
        raise StrategyRuleError(f"bench player {name!r} must include at least one role")
    return role_list


def _validate_lineup_players(current_lineup: Mapping[str, Any]) -> List[str]:
    order = current_lineup.get("batting_order")
    if not isinstance(order, list) or len(order) != 9:
        raise StrategyRuleError("current_lineup['batting_order'] must be a list of 9 players")
    normalized = []
    for idx, player in enumerate(order):
        if not isinstance(player, str) or not player.strip():
            raise StrategyRuleError(f"batting_order index {idx} must be a non-empty string")
        normalized.append(player.strip())
    return normalized


def _validate_field_positions(current_lineup: Mapping[str, Any]) -> Mapping[str, str]:
    positions = current_lineup.get("field_positions")
    if not isinstance(positions, Mapping) or not positions:
        raise StrategyRuleError("current_lineup['field_positions'] must be a non-empty mapping")
    out: Dict[str, str] = {}
    for pos, player in positions.items():
        pos_norm = str(pos).strip().upper()
        if not pos_norm:
            continue
        if not isinstance(player, str) or not player.strip():
            raise StrategyRuleError(f"field position {pos!r} must map to a non-empty player")
        out[pos_norm] = player.strip()
    if not out:
        raise StrategyRuleError("current_lineup['field_positions'] must include at least one player")
    return out


def _bench_index(bench_players: Iterable[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    indexed: Dict[str, Dict[str, Any]] = {}
    for idx, player in enumerate(bench_players):
        name = _player_name(player, idx)
        roles = _player_roles(player, name)
        if name in indexed:
            raise StrategyRuleError(f"duplicate bench player {name!r}")
        indexed[name] = {"name": name, "roles": roles, **dict(player)}
    return indexed


def _intervals_overlap(a: Sequence[int], b: Sequence[int]) -> bool:
    return int(a[0]) <= int(b[1]) and int(b[0]) <= int(a[1])


def resolve_recommendation_conflicts(
    recommendations: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Keep highest-scoring recommendation for overlapping actions that use same bench player.
    """
    ranked = sorted(
        (dict(r) for r in recommendations),
        key=lambda rec: (-float(rec["score"]), int(rec["priority"]), rec["action_type"]),
    )
    accepted: List[Dict[str, Any]] = []
    for rec in ranked:
        rec_bench = str(rec.get("bench_player", "")).strip()
        rec_window = rec.get("inning_window", [1, 1])
        is_conflict = False
        for kept in accepted:
            kept_bench = str(kept.get("bench_player", "")).strip()
            if not rec_bench or rec_bench != kept_bench:
                continue
            if _intervals_overlap(rec_window, kept.get("inning_window", [1, 1])):
                is_conflict = True
                break
        if not is_conflict:
            accepted.append(rec)
    return sorted(
        accepted,
        key=lambda rec: (int(rec["priority"]), -float(rec["confidence"]), rec["action_type"]),
    )


def evaluate_strategy_recommendations(
    *,
    state: Mapping[str, Any],
    current_lineup: Mapping[str, Any],
    bench_players: Sequence[Mapping[str, Any]],
    offensive_scores: Mapping[str, float],
    defensive_scores: Mapping[str, float],
    innings_ahead: int = 3,
) -> List[Dict[str, Any]]:
    """
    Produce scored tactical recommendations for adaptive planning.
    """
    inning = int(state["inning"])
    outs = int(state["outs"])
    score_diff = int(state["score_for"]) - int(state["score_against"])
    substitutions_remaining = int(state["substitutions_limit"]) - int(state["substitutions_used"])
    bases = tuple(bool(x) for x in state.get("bases", [False, False, False]))

    lineup_players = _validate_lineup_players(current_lineup)
    field_positions = _validate_field_positions(current_lineup)
    bench = _bench_index(bench_players)
    window = _window(inning, innings_ahead)

    # Require metrics for all active lineup players to support deterministic comparisons.
    missing_offense = [p for p in lineup_players if p not in offensive_scores]
    if missing_offense:
        raise StrategyRuleError(
            f"offensive_scores missing required lineup players: {', '.join(sorted(missing_offense))}"
        )
    missing_defense = [p for p in field_positions.values() if p not in defensive_scores]
    if missing_defense:
        raise StrategyRuleError(
            f"defensive_scores missing required field players: {', '.join(sorted(set(missing_defense)))}"
        )

    recs: List[Dict[str, Any]] = []
    if substitutions_remaining <= 0 or not bench:
        return recs

    # Rule 1: pinch hitter opportunity when trailing in middle/late game.
    if inning >= 6 and score_diff < 0:
        ph_candidates = [
            b for b in bench.values() if "PH" in b["roles"] and b["name"] in offensive_scores
        ]
        if ph_candidates:
            bench_pick = max(
                ph_candidates,
                key=lambda b: (float(offensive_scores[b["name"]]), b["name"]),
            )
            replace_target = min(
                lineup_players, key=lambda name: (float(offensive_scores[name]), name)
            )
            impact = min(
                1.0,
                max(
                    0.0,
                    (float(offensive_scores[bench_pick["name"]]) - float(offensive_scores[replace_target]))
                    / 30.0,
                ),
            )
            urgency = min(1.0, 0.35 + (inning - 5) * 0.12)
            feasibility = min(1.0, substitutions_remaining / 3.0)
            risk = 0.3 + max(0, outs - 1) * 0.1
            score = _weighted_score(
                impact=impact, urgency=urgency, feasibility=feasibility, risk=risk
            )
            recs.append(
                {
                    "action_type": "pinch_hitter",
                    "inning_window": window,
                    "priority": 1,
                    "confidence": 0.66 + 0.2 * impact,
                    "score": score,
                    "bench_player": bench_pick["name"],
                    "target_player": replace_target,
                    "reason": (
                        f"Trailing in inning {inning}: {bench_pick['name']} projects stronger offense "
                        f"than {replace_target} for immediate run production."
                    ),
                }
            )

    # Rule 2: pinch runner when speed leverage is high.
    if inning >= 7 and any(bases) and score_diff <= 0:
        pr_candidates: List[Tuple[Dict[str, Any], float]] = []
        for bench_player in bench.values():
            if "PR" not in bench_player["roles"]:
                continue
            speed = bench_player.get("speed")
            if speed is None:
                continue
            pr_candidates.append((bench_player, _require_numeric("bench speed", speed)))
        if pr_candidates:
            bench_pick, speed_value = max(pr_candidates, key=lambda pair: (pair[1], pair[0]["name"]))
            impact = min(1.0, max(0.0, (speed_value - 60.0) / 40.0))
            urgency = min(1.0, 0.5 + (inning - 7) * 0.15)
            feasibility = min(1.0, substitutions_remaining / 2.0)
            risk = 0.2
            score = _weighted_score(
                impact=impact, urgency=urgency, feasibility=feasibility, risk=risk
            )
            recs.append(
                {
                    "action_type": "pinch_runner",
                    "inning_window": window,
                    "priority": 1,
                    "confidence": 0.62 + 0.2 * impact,
                    "score": score,
                    "bench_player": bench_pick["name"],
                    "target_player": "slowest_current_runner",
                    "reason": (
                        f"Base occupied in late leverage spot; {bench_pick['name']} adds speed "
                        "to improve scoring probability."
                    ),
                }
            )

    # Rule 3: defensive replacement to protect a lead (field positions only — not DH).
    if inning >= 7 and score_diff > 0:
        def_candidates = [
            b for b in bench.values() if ("DEF" in b["roles"] or "CF" in b["roles"] or "SS" in b["roles"])
        ]
        field_assignments = {
            str(pos).strip().upper(): player.strip()
            for pos, player in field_positions.items()
            if str(pos).strip().upper() in FIELD_POSITIONS_DEFENSIVE
            and isinstance(player, str)
            and player.strip()
        }
        if def_candidates and field_assignments:
            best_bench = max(
                def_candidates,
                key=lambda b: (
                    float(defensive_scores.get(b["name"], b.get("defense_score", 0.0))),
                    b["name"],
                ),
            )
            weakest_position, weakest_player = min(
                field_assignments.items(),
                key=lambda pair: (float(defensive_scores[pair[1]]), pair[0], pair[1]),
            )
            bench_score = float(defensive_scores.get(best_bench["name"], best_bench.get("defense_score", 0.0)))
            impact = min(
                1.0,
                max(0.0, (bench_score - float(defensive_scores[weakest_player])) / 25.0),
            )
            urgency = min(1.0, 0.5 + (inning - 7) * 0.1)
            feasibility = min(1.0, substitutions_remaining / 3.0)
            risk = 0.15
            score = _weighted_score(
                impact=impact, urgency=urgency, feasibility=feasibility, risk=risk
            )
            recs.append(
                {
                    "action_type": "defensive_replacement",
                    "inning_window": window,
                    "priority": 1,
                    "confidence": 0.64 + 0.2 * impact,
                    "score": score,
                    "bench_player": best_bench["name"],
                    "target_player": weakest_player,
                    "position": weakest_position,
                    "reason": (
                        f"Protecting a lead: strengthen {weakest_position} by bringing in "
                        f"{best_bench['name']} for {weakest_player}."
                    ),
                }
            )

    # Rule 4: lineup/matchup adjustment watch recommendation.
    if inning <= 8 and substitutions_remaining > 0:
        strongest_bat = max(lineup_players, key=lambda p: (float(offensive_scores[p]), p))
        score = _weighted_score(impact=0.45, urgency=0.4, feasibility=0.9, risk=0.05)
        recs.append(
            {
                "action_type": "lineup_matchup_adjustment",
                "inning_window": window,
                "priority": 2,
                "confidence": 0.6,
                "score": score,
                "bench_player": "",
                "target_player": strongest_bat,
                "reason": (
                    f"Center next high-leverage plate appearance around {strongest_bat} "
                    "based on projected matchup edge."
                ),
            }
        )

    return resolve_recommendation_conflicts(recs)
