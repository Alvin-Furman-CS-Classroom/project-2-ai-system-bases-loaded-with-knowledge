"""
Unit tests for src/module4/lineup_fitness.py (Partner B deliverables).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module4.lineup_fitness import (
    MissingBattingStatsError,
    evaluate_lineup_fitness,
    make_lineup_fitness_function,
)


def _nine_toy_stats() -> dict:
    return {
        "LeadA": {"obp": 0.440, "slg": 0.380, "hr": 12, "rbi": 55},
        "LeadB": {"obp": 0.420, "slg": 0.390, "hr": 14, "rbi": 52},
        "PowA": {"obp": 0.310, "slg": 0.540, "hr": 38, "rbi": 105},
        "PowB": {"obp": 0.300, "slg": 0.520, "hr": 35, "rbi": 98},
        "PowC": {"obp": 0.295, "slg": 0.510, "hr": 32, "rbi": 90},
        "TailA": {"obp": 0.320, "slg": 0.400, "hr": 10, "rbi": 40},
        "TailB": {"obp": 0.315, "slg": 0.395, "hr": 9, "rbi": 38},
        "TailC": {"obp": 0.305, "slg": 0.385, "hr": 8, "rbi": 36},
        "TailD": {"obp": 0.300, "slg": 0.380, "hr": 7, "rbi": 34},
    }


class TestLineupFitness(unittest.TestCase):
    def test_good_lineup_scores_higher_than_poor_lineup(self):
        stats = _nine_toy_stats()
        good = [
            "LeadA",
            "LeadB",
            "PowA",
            "PowB",
            "PowC",
            "TailA",
            "TailB",
            "TailC",
            "TailD",
        ]
        poor = [
            "TailD",
            "TailC",
            "TailB",
            "TailA",
            "PowC",
            "PowB",
            "PowA",
            "LeadB",
            "LeadA",
        ]
        self.assertGreater(evaluate_lineup_fitness(good, stats), evaluate_lineup_fitness(poor, stats))

    def test_missing_stats_raises(self):
        stats = {f"P{i}": {"obp": 0.3} for i in range(9)}
        order = [f"P{i}" for i in range(9)]
        with self.assertRaises(MissingBattingStatsError):
            evaluate_lineup_fitness(order, stats)

    def test_make_lineup_fitness_function_matches_evaluate(self):
        stats = _nine_toy_stats()
        order = list(stats.keys())
        fn = make_lineup_fitness_function(stats)
        self.assertAlmostEqual(fn(order), evaluate_lineup_fitness(order, stats))


if __name__ == "__main__":
    unittest.main()
"""
Unit tests for src/module4/lineup_fitness.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module4.lineup_fitness import (
    MissingBattingStatsError,
    evaluate_lineup_fitness,
    make_lineup_fitness_function,
)


def _nine_toy_stats() -> dict:
    """Nine players: two table-setters, three power bats, four tail bats."""
    return {
        "LeadA": {"obp": 0.440, "slg": 0.380, "hr": 12, "rbi": 55},
        "LeadB": {"obp": 0.420, "slg": 0.390, "hr": 14, "rbi": 52},
        "PowA": {"obp": 0.310, "slg": 0.540, "hr": 38, "rbi": 105},
        "PowB": {"obp": 0.300, "slg": 0.520, "hr": 35, "rbi": 98},
        "PowC": {"obp": 0.295, "slg": 0.510, "hr": 32, "rbi": 90},
        "TailA": {"obp": 0.320, "slg": 0.400, "hr": 10, "rbi": 40},
        "TailB": {"obp": 0.315, "slg": 0.395, "hr": 9, "rbi": 38},
        "TailC": {"obp": 0.305, "slg": 0.385, "hr": 8, "rbi": 36},
        "TailD": {"obp": 0.300, "slg": 0.380, "hr": 7, "rbi": 34},
    }


class TestLineupFitness(unittest.TestCase):
    def test_good_lineup_scores_higher_than_poor_lineup(self):
        stats = _nine_toy_stats()
        good = [
            "LeadA",
            "LeadB",
            "PowA",
            "PowB",
            "PowC",
            "TailA",
            "TailB",
            "TailC",
            "TailD",
        ]
        poor = [
            "TailD",
            "TailC",
            "TailB",
            "TailA",
            "PowC",
            "PowB",
            "PowA",
            "LeadB",
            "LeadA",
        ]
        self.assertGreater(evaluate_lineup_fitness(good, stats), evaluate_lineup_fitness(poor, stats))

    def test_missing_stats_raises(self):
        stats = {f"P{i}": {"obp": 0.3} for i in range(9)}  # missing slg, hr, rbi
        order = [f"P{i}" for i in range(9)]
        with self.assertRaises(MissingBattingStatsError):
            evaluate_lineup_fitness(order, stats)

    def test_make_lineup_fitness_function_matches_evaluate(self):
        stats = _nine_toy_stats()
        order = list(stats.keys())
        fn = make_lineup_fitness_function(stats)
        self.assertAlmostEqual(fn(order), evaluate_lineup_fitness(order, stats))


if __name__ == "__main__":
    unittest.main()
