"""
Unit tests for src/module3/position_assignment.py
"""

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module3.position_assignment import assign_defensive_positions, DEFAULT_POSITIONS, FIELD_POSITIONS


class TestPositionAssignment(unittest.TestCase):
    def test_happy_path_unique_best_assignment(self):
        offense = {
            "Extra": 90.0,  # best offense -> should be pitcher P
            "PlayerC": 40.0,
            "Player1B": 41.0,
            "Player2B": 42.0,
            "Player3B": 43.0,
            "PlayerSS": 44.0,
            "PlayerLF": 45.0,
            "PlayerCF": 46.0,
            "PlayerRF": 47.0,
        }

        # Defense dominates for field positions.
        defense = {
            "Extra": {pos: 0.0 for pos in FIELD_POSITIONS},
            "PlayerC": {pos: (100.0 if pos == "C" else 0.0) for pos in FIELD_POSITIONS},
            "Player1B": {pos: (100.0 if pos == "1B" else 0.0) for pos in FIELD_POSITIONS},
            "Player2B": {pos: (100.0 if pos == "2B" else 0.0) for pos in FIELD_POSITIONS},
            "Player3B": {pos: (100.0 if pos == "3B" else 0.0) for pos in FIELD_POSITIONS},
            "PlayerSS": {pos: (100.0 if pos == "SS" else 0.0) for pos in FIELD_POSITIONS},
            "PlayerLF": {pos: (100.0 if pos == "LF" else 0.0) for pos in FIELD_POSITIONS},
            "PlayerCF": {pos: (100.0 if pos == "CF" else 0.0) for pos in FIELD_POSITIONS},
            "PlayerRF": {pos: (100.0 if pos == "RF" else 0.0) for pos in FIELD_POSITIONS},
        }

        eligibility = {player: list(DEFAULT_POSITIONS) for player in offense.keys()}

        result = assign_defensive_positions(
            offense,
            defense,
            eligibility,
            weights=(0.65, 0.35),
        )

        self.assertEqual(set(result.keys()), set(DEFAULT_POSITIONS))
        self.assertEqual(len(set(result.values())), 9, "Players must be unique across positions")

        self.assertEqual(result["P"], "Extra")
        self.assertEqual(result["C"], "PlayerC")
        self.assertEqual(result["1B"], "Player1B")
        self.assertEqual(result["2B"], "Player2B")
        self.assertEqual(result["3B"], "Player3B")
        self.assertEqual(result["SS"], "PlayerSS")
        self.assertEqual(result["LF"], "PlayerLF")
        self.assertEqual(result["CF"], "PlayerCF")
        self.assertEqual(result["RF"], "PlayerRF")

    def test_lock_constraint_respected(self):
        offense = {
            "Extra": 90.0,
            "PlayerC": 40.0,
            "Player1B": 41.0,
            "Player2B": 42.0,
            "Player3B": 43.0,
            "PlayerSS": 44.0,
            "PlayerLF": 45.0,
            "PlayerCF": 46.0,
            "PlayerRF": 47.0,
        }

        defense = {
            "Extra": {pos: 0.0 for pos in FIELD_POSITIONS},
            "PlayerC": {pos: (100.0 if pos == "C" else 0.0) for pos in FIELD_POSITIONS},
            "Player1B": {pos: (100.0 if pos == "1B" else 0.0) for pos in FIELD_POSITIONS},
            "Player2B": {pos: (100.0 if pos == "2B" else 0.0) for pos in FIELD_POSITIONS},
            "Player3B": {pos: (100.0 if pos == "3B" else 0.0) for pos in FIELD_POSITIONS},
            "PlayerSS": {pos: (100.0 if pos == "SS" else 0.0) for pos in FIELD_POSITIONS},
            "PlayerLF": {pos: (100.0 if pos == "LF" else 0.0) for pos in FIELD_POSITIONS},
            "PlayerCF": {pos: (100.0 if pos == "CF" else 0.0) for pos in FIELD_POSITIONS},
            "PlayerRF": {pos: (100.0 if pos == "RF" else 0.0) for pos in FIELD_POSITIONS},
        }

        eligibility = {player: list(DEFAULT_POSITIONS) for player in offense.keys()}

        result = assign_defensive_positions(
            offense,
            defense,
            eligibility,
            weights=(0.65, 0.35),
            lock_positions={"SS": "Extra"},
        )

        self.assertEqual(result["SS"], "Extra")
        self.assertEqual(len(set(result.values())), 9)

    def test_bad_inputs_missing_eligibility_domain(self):
        offense = {"A": 10.0, "B": 20.0, "C": 30.0}
        defense = {"A": {}, "B": {}, "C": {}}

        # Only eligible for P; everything else should cause a clear error.
        eligibility = {"A": ["P"], "B": ["P"], "C": ["P"]}

        with self.assertRaises(ValueError):
            assign_defensive_positions(offense, defense, eligibility)

    def test_bad_inputs_missing_offense_score(self):
        offense = {"PlayerC": 40.0}
        defense = {"PlayerC": {pos: 0.0 for pos in FIELD_POSITIONS}}

        eligibility = {
            "PlayerC": list(DEFAULT_POSITIONS),
            "UnknownPlayer": list(DEFAULT_POSITIONS),
        }

        with self.assertRaises(ValueError):
            assign_defensive_positions(offense, defense, eligibility)


if __name__ == "__main__":
    unittest.main()

