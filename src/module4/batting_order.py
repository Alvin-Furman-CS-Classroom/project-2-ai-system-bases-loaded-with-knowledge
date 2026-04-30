"""
Public Module 4 API (Partner B): optimize batting order from selected players.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from module4.genetic_optimizer import run_genetic_lineup_optimization
from module4.lineup_fitness import (
    LineupFitnessError,
    LineupFitnessWeights,
    MissingBattingStatsError,
    REQUIRED_STAT_KEYS,
    make_lineup_fitness_function,
)


def _validate_selected_players(selected_players: Sequence[str]) -> List[str]:
    names = list(selected_players)
    if len(names) != 9:
        raise LineupFitnessError(
            f"selected_players must contain exactly 9 players, got {len(names)}"
        )
    if len(set(names)) != 9:
        raise LineupFitnessError("selected_players must contain unique player names")
    return names


def _validate_batter_stats(
    players: Sequence[str], batter_stats: Mapping[str, Mapping[str, Any]]
) -> None:
    for player in players:
        if player not in batter_stats:
            raise MissingBattingStatsError(f"batter_stats missing player {player!r}")
        missing = [k for k in REQUIRED_STAT_KEYS if k not in batter_stats[player]]
        if missing:
            raise MissingBattingStatsError(
                f"Player {player!r} missing keys {missing}; "
                f"required {list(REQUIRED_STAT_KEYS)}"
            )


def optimize_batting_order(
    selected_players: Sequence[str],
    batter_stats: Mapping[str, Mapping[str, Any]],
    *,
    offensive_scores: Optional[Mapping[str, float]] = None,
    fitness_weights: Optional[LineupFitnessWeights] = None,
    seed: Optional[int] = None,
    population_size: int = 120,
    generations: int = 250,
    mutation_rate: float = 0.08,
    elite_count: int = 6,
) -> Dict[str, Any]:
    """
    Optimize lineup order for nine selected players.

    Returns standardized output:
    {
      "optimized_order": [...9 players...],
      "best_fitness": float,
      "generations_run": int,
      "seed": int|None
    }
    """
    players = _validate_selected_players(selected_players)
    _validate_batter_stats(players, batter_stats)

    fitness_fn = make_lineup_fitness_function(
        batter_stats,
        offensive_scores=offensive_scores,
        weights=fitness_weights,
    )
    best_order, metadata = run_genetic_lineup_optimization(
        players,
        fitness_fn,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        elite_count=elite_count,
        seed=seed,
    )

    return {
        "optimized_order": best_order,
        "best_fitness": metadata["best_fitness"],
        "generations_run": metadata["generations_run"],
        "seed": metadata["seed"],
    }
