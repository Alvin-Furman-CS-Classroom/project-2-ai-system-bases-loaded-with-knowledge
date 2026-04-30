"""
Genetic algorithm engine for batting-order optimization (Module 4, Partner A).
"""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Optional, Sequence, Tuple

DEFAULT_POPULATION_SIZE = 120
DEFAULT_GENERATIONS = 250
DEFAULT_MUTATION_RATE = 0.08
DEFAULT_ELITE_COUNT = 6
DEFAULT_STAGNATION_LIMIT = 60


class InvalidOptimizationInputError(ValueError):
    """Raised when optimizer inputs violate the Module 4 contract."""


def _validate_players(players: Sequence[str]) -> List[str]:
    if len(players) != 9:
        raise InvalidOptimizationInputError("Exactly 9 players are required.")
    if len(set(players)) != 9:
        raise InvalidOptimizationInputError("Players must be unique.")
    return list(players)


def _is_valid_lineup(lineup: Sequence[str], players: Sequence[str]) -> bool:
    return len(lineup) == len(players) and set(lineup) == set(players)


def _initialize_population(
    players: Sequence[str], population_size: int, rng: random.Random
) -> List[List[str]]:
    population: List[List[str]] = []
    seen = set()
    while len(population) < population_size:
        candidate = list(players)
        rng.shuffle(candidate)
        key = tuple(candidate)
        if key not in seen:
            seen.add(key)
            population.append(candidate)
    return population


def _tournament_select(
    population: Sequence[List[str]],
    fitness_map: Dict[Tuple[str, ...], float],
    rng: random.Random,
    tournament_size: int = 3,
) -> List[str]:
    contenders = rng.sample(population, k=min(tournament_size, len(population)))
    return max(contenders, key=lambda lineup: fitness_map[tuple(lineup)])


def _order_crossover(parent_a: Sequence[str], parent_b: Sequence[str], rng: random.Random) -> List[str]:
    size = len(parent_a)
    start, end = sorted(rng.sample(range(size), 2))
    child = [None] * size  # type: ignore[list-item]
    child[start : end + 1] = parent_a[start : end + 1]

    insert_idx = (end + 1) % size
    scan_idx = (end + 1) % size
    while None in child:
        candidate = parent_b[scan_idx]
        if candidate not in child:
            child[insert_idx] = candidate
            insert_idx = (insert_idx + 1) % size
        scan_idx = (scan_idx + 1) % size

    return child  # type: ignore[return-value]


def _mutate_lineup(lineup: List[str], mutation_rate: float, rng: random.Random) -> List[str]:
    if rng.random() >= mutation_rate:
        return lineup

    mutated = list(lineup)
    if rng.random() < 0.5:
        i, j = sorted(rng.sample(range(len(mutated)), 2))
        mutated[i], mutated[j] = mutated[j], mutated[i]
    else:
        i, j = sorted(rng.sample(range(len(mutated)), 2))
        mutated[i : j + 1] = reversed(mutated[i : j + 1])
    return mutated


def run_genetic_lineup_optimization(
    players: Sequence[str],
    fitness_fn: Callable[[Sequence[str]], float],
    *,
    population_size: int = DEFAULT_POPULATION_SIZE,
    generations: int = DEFAULT_GENERATIONS,
    mutation_rate: float = DEFAULT_MUTATION_RATE,
    elite_count: int = DEFAULT_ELITE_COUNT,
    seed: Optional[int] = None,
    stagnation_limit: int = DEFAULT_STAGNATION_LIMIT,
) -> Tuple[List[str], Dict[str, object]]:
    """
    Optimize batting order using a permutation-preserving genetic algorithm.

    Returns:
        (best_lineup, metadata)
    """
    validated_players = _validate_players(players)
    if population_size < 2:
        raise InvalidOptimizationInputError("population_size must be >= 2.")
    if generations < 1:
        raise InvalidOptimizationInputError("generations must be >= 1.")
    if not 0.0 <= mutation_rate <= 1.0:
        raise InvalidOptimizationInputError("mutation_rate must be in [0, 1].")
    if not 0 <= elite_count < population_size:
        raise InvalidOptimizationInputError(
            "elite_count must be >= 0 and less than population_size."
        )
    if stagnation_limit < 1:
        raise InvalidOptimizationInputError("stagnation_limit must be >= 1.")

    rng = random.Random(seed)
    population = _initialize_population(validated_players, population_size, rng)

    best_lineup: List[str] = []
    best_fitness = float("-inf")
    best_fitness_by_generation: List[float] = []
    generations_run = 0
    no_improvement_count = 0

    for generation_idx in range(generations):
        fitness_map = {tuple(lineup): float(fitness_fn(lineup)) for lineup in population}
        ranked_population = sorted(
            population, key=lambda lineup: fitness_map[tuple(lineup)], reverse=True
        )

        generation_best_lineup = ranked_population[0]
        generation_best_fitness = fitness_map[tuple(generation_best_lineup)]

        if generation_best_fitness > best_fitness:
            best_fitness = generation_best_fitness
            best_lineup = list(generation_best_lineup)
            no_improvement_count = 0
        else:
            no_improvement_count += 1

        best_fitness_by_generation.append(best_fitness)
        generations_run = generation_idx + 1

        if no_improvement_count >= stagnation_limit:
            break

        next_population: List[List[str]] = [list(lineup) for lineup in ranked_population[:elite_count]]
        while len(next_population) < population_size:
            parent_a = _tournament_select(ranked_population, fitness_map, rng)
            parent_b = _tournament_select(ranked_population, fitness_map, rng)
            child = _order_crossover(parent_a, parent_b, rng)
            child = _mutate_lineup(child, mutation_rate, rng)
            if _is_valid_lineup(child, validated_players):
                next_population.append(child)

        population = next_population

    metadata: Dict[str, object] = {
        "best_fitness": best_fitness,
        "generations_run": generations_run,
        "seed": seed,
        "population_size": population_size,
        "mutation_rate": mutation_rate,
        "elite_count": elite_count,
        "stagnation_limit": stagnation_limit,
        "best_fitness_by_generation": best_fitness_by_generation,
    }
    return best_lineup, metadata
