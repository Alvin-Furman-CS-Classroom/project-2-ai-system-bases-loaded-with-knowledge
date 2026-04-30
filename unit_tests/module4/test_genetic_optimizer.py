"""
Unit tests for src/module4/genetic_optimizer.py (Partner A deliverables).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module4.genetic_optimizer import (
    _initialize_population,
    _mutate_lineup,
    _order_crossover,
    run_genetic_lineup_optimization,
)


PLAYERS = [f"Player{i}" for i in range(1, 10)]


def simple_fitness(lineup):
    return sum((9 - idx) * int(player.replace("Player", "")) for idx, player in enumerate(lineup))


class TestPopulationAndOperators(unittest.TestCase):
    def test_initial_population_contains_valid_permutations(self):
        import random

        population = _initialize_population(PLAYERS, 30, random.Random(7))
        self.assertEqual(len(population), 30)
        for lineup in population:
            self.assertEqual(len(lineup), 9)
            self.assertEqual(set(lineup), set(PLAYERS))
            self.assertEqual(len(set(lineup)), 9)

    def test_crossover_preserves_uniqueness_and_length(self):
        import random

        parent_a = PLAYERS
        parent_b = list(reversed(PLAYERS))
        child = _order_crossover(parent_a, parent_b, random.Random(3))
        self.assertEqual(len(child), 9)
        self.assertEqual(len(set(child)), 9)
        self.assertEqual(set(child), set(PLAYERS))

    def test_mutation_preserves_uniqueness_and_length(self):
        import random

        mutated = _mutate_lineup(list(PLAYERS), mutation_rate=1.0, rng=random.Random(5))
        self.assertEqual(len(mutated), 9)
        self.assertEqual(len(set(mutated)), 9)
        self.assertEqual(set(mutated), set(PLAYERS))


class TestDeterminismAndElitism(unittest.TestCase):
    def test_seeded_runs_are_deterministic(self):
        lineup_1, meta_1 = run_genetic_lineup_optimization(
            PLAYERS,
            simple_fitness,
            population_size=40,
            generations=40,
            mutation_rate=0.1,
            elite_count=4,
            seed=42,
        )
        lineup_2, meta_2 = run_genetic_lineup_optimization(
            PLAYERS,
            simple_fitness,
            population_size=40,
            generations=40,
            mutation_rate=0.1,
            elite_count=4,
            seed=42,
        )
        self.assertEqual(lineup_1, lineup_2)
        self.assertEqual(meta_1["best_fitness"], meta_2["best_fitness"])
        self.assertEqual(meta_1["best_fitness_by_generation"], meta_2["best_fitness_by_generation"])

    def test_best_fitness_non_regression_with_elitism(self):
        _, metadata = run_genetic_lineup_optimization(
            PLAYERS,
            simple_fitness,
            population_size=60,
            generations=50,
            mutation_rate=0.12,
            elite_count=6,
            seed=11,
        )
        history = metadata["best_fitness_by_generation"]
        self.assertGreaterEqual(len(history), 1)
        for i in range(1, len(history)):
            self.assertGreaterEqual(history[i], history[i - 1])


if __name__ == "__main__":
    unittest.main()
