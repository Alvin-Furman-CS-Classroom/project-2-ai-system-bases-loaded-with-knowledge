"""
Batting-order fitness for Module 4 (Partner B).

Heuristics:
- slots 1-2 reward OBP (table setters)
- slots 3-5 reward power/run production
- slots 6-9 reward balanced production
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

REQUIRED_STAT_KEYS: Tuple[str, ...] = ("obp", "slg", "hr", "rbi")


class LineupFitnessError(ValueError):
    """Base error for invalid Module 4 fitness inputs."""


class MissingBattingStatsError(LineupFitnessError):
    """Raised when a selected player is missing required batting stats."""


@dataclass(frozen=True)
class LineupFitnessWeights:
    """Tunable weights and thresholds for lineup slot scoring."""

    top_obp: float = 2.2
    top_secondary: float = 0.35

    middle_power: float = 2.0
    middle_obp_floor_penalty: float = 0.4

    tail_balanced: float = 1.1

    penalty_low_obp_leadoff: float = 0.45
    penalty_low_power_middle: float = 0.35
    leadoff_obp_threshold: float = 0.28
    middle_power_threshold: float = 0.42

    offensive_score_blend: float = 0.12


def _normalize_hr(hr: float) -> float:
    return max(0.0, min(float(hr) / 50.0, 1.0))


def _normalize_rbi(rbi: float) -> float:
    return max(0.0, min(float(rbi) / 120.0, 1.0))


def power_index(stats: Mapping[str, Any]) -> float:
    """Power-focused index in approximately [0, 1]."""
    return (
        0.45 * float(stats["slg"])
        + 0.30 * _normalize_hr(float(stats["hr"]))
        + 0.25 * _normalize_rbi(float(stats["rbi"]))
    )


def balanced_index(stats: Mapping[str, Any]) -> float:
    """Balanced production index in approximately [0, 1]."""
    return (
        float(stats["obp"])
        + float(stats["slg"])
        + _normalize_hr(float(stats["hr"]))
        + _normalize_rbi(float(stats["rbi"]))
    ) / 4.0


def _ensure_stats(player: str, stats: Mapping[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED_STAT_KEYS if k not in stats]
    if missing:
        raise MissingBattingStatsError(
            f"Player {player!r} missing required keys {missing}; "
            f"required {list(REQUIRED_STAT_KEYS)}"
        )
    return {k: stats[k] for k in REQUIRED_STAT_KEYS}


def evaluate_lineup_fitness(
    order: Sequence[str],
    batter_stats: Mapping[str, Mapping[str, Any]],
    *,
    offensive_scores: Optional[Mapping[str, float]] = None,
    weights: Optional[LineupFitnessWeights] = None,
) -> float:
    """Evaluate one lineup; higher score means a better batting order."""
    if len(order) != 9 or len(set(order)) != 9:
        raise LineupFitnessError("order must contain exactly 9 unique players")

    w = weights or LineupFitnessWeights()
    total = 0.0

    for slot, player in enumerate(order):
        if player not in batter_stats:
            raise MissingBattingStatsError(f"No batting stats found for player {player!r}")
        st = _ensure_stats(player, batter_stats[player])
        obp = float(st["obp"])
        pwr = power_index(st)
        bal = balanced_index(st)

        if slot <= 1:
            total += w.top_obp * obp + w.top_secondary * bal
            if slot == 0 and obp < w.leadoff_obp_threshold:
                total -= w.penalty_low_obp_leadoff * (w.leadoff_obp_threshold - obp)
        elif slot <= 4:
            total += w.middle_power * pwr
            if pwr < w.middle_power_threshold:
                total -= w.middle_obp_floor_penalty * (w.middle_power_threshold - pwr)
            if obp < 0.26:
                total -= w.penalty_low_power_middle * (0.26 - obp)
        else:
            total += w.tail_balanced * bal

        if offensive_scores is not None:
            if player not in offensive_scores:
                raise LineupFitnessError(
                    f"offensive_scores provided but missing entry for {player!r}"
                )
            total += w.offensive_score_blend * (float(offensive_scores[player]) / 100.0)

    return total


def make_lineup_fitness_function(
    batter_stats: Mapping[str, Mapping[str, Any]],
    *,
    offensive_scores: Optional[Mapping[str, float]] = None,
    weights: Optional[LineupFitnessWeights] = None,
) -> Callable[[Sequence[str]], float]:
    """Build a fitness closure compatible with Partner A optimizer."""

    def fitness(order: Sequence[str]) -> float:
        return evaluate_lineup_fitness(
            order,
            batter_stats,
            offensive_scores=offensive_scores,
            weights=weights,
        )

    return fitness
