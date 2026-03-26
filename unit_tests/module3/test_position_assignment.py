"""
Unit tests for src/module3/position_assignment.py
"""

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module3.position_assignment import (
    DEFAULT_LEVERAGE_LINEAR_SCALE,
    DEFAULT_POSITIONS,
    DEFENSIVE_LEVERAGE_UP_THE_MIDDLE,
    FGRAPHS_POSITIONAL_ADJUSTMENT_RUNS,
    FIELD_POSITIONS,
    InfeasibleLineupError,
    InvalidLineupInputError,
    assign_defensive_positions,
    defense_multipliers_from_positional_adjustment_runs,
)


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

        with self.assertRaises(InvalidLineupInputError):
            assign_defensive_positions(offense, defense, eligibility)

    def test_bad_inputs_missing_offense_score(self):
        offense = {"PlayerC": 40.0}
        defense = {"PlayerC": {pos: 0.0 for pos in FIELD_POSITIONS}}

        eligibility = {
            "PlayerC": list(DEFAULT_POSITIONS),
            "UnknownPlayer": list(DEFAULT_POSITIONS),
        }

        with self.assertRaises(InvalidLineupInputError):
            assign_defensive_positions(offense, defense, eligibility)

    def test_infeasible_raises_infeasible_lineup_error(self):
        """One player cannot fill two positions with all-different constraint."""
        offense = {"A": 50.0}
        defense = {"A": {"2B": 80.0, "LF": 70.0}}
        eligibility = {"A": ["2B", "LF"]}
        with self.assertRaises(InfeasibleLineupError):
            assign_defensive_positions(
                offense,
                defense,
                eligibility,
                positions=["2B", "LF"],
            )


class TestDefensiveStressProfile(unittest.TestCase):
    """Optional 'up_the_middle' weighting — spice / course narrative hook."""

    def test_unknown_profile_raises(self):
        offense = {"A": 50.0, "B": 50.0}
        defense = {"A": {"2B": 80.0, "LF": 70.0}, "B": {"2B": 75.0, "LF": 85.0}}
        eligibility = {"A": ["2B", "LF"], "B": ["2B", "LF"]}
        with self.assertRaises(InvalidLineupInputError):
            assign_defensive_positions(
                offense,
                defense,
                eligibility,
                positions=["2B", "LF"],
                defensive_stress_profile="corner_specialist",  # type: ignore[arg-type]
            )

    def test_bruteforce_matches_solver_flat_and_up_the_middle(self):
        """Tiny CSP: enumerate both bijections and compare to solver."""
        offense = {"A": 48.0, "B": 52.0}
        defense = {
            "A": {"2B": 92.0, "LF": 55.0},
            "B": {"2B": 78.0, "LF": 91.0},
        }
        eligibility = {"A": ["2B", "LF"], "B": ["2B", "LF"]}
        pos_list = ["2B", "LF"]
        w_def, w_off = 0.65, 0.35

        def brute_best(profile):
            mult = {p: 1.0 for p in pos_list}
            if profile == "up_the_middle":
                mult = {p: DEFENSIVE_LEVERAGE_UP_THE_MIDDLE[p] for p in pos_list}

            def pair_score(pos, player):
                d = defense[player][pos]
                o = offense[player]
                return w_def * d * mult[pos] + w_off * o

            opt = None
            best = float("-inf")
            for a2b in ("A", "B"):
                lf = "B" if a2b == "A" else "A"
                assign = {"2B": a2b, "LF": lf}
                total = pair_score("2B", a2b) + pair_score("LF", lf)
                if total > best:
                    best = total
                    opt = assign
            return opt

        for profile in (None, "flat", "up_the_middle"):
            want = brute_best(profile)
            got = assign_defensive_positions(
                offense,
                defense,
                eligibility,
                positions=pos_list,
                weights=(w_def, w_off),
                defensive_stress_profile=profile,
            )
            self.assertEqual(got, want, msg=f"profile={profile!r}")

    def test_leverage_table_covers_all_default_positions(self):
        for pos in DEFAULT_POSITIONS:
            self.assertIn(pos, DEFENSIVE_LEVERAGE_UP_THE_MIDDLE)

    def test_leverage_matches_fangraphs_formula(self):
        """Multipliers = 1 + DEFAULT_LEVERAGE_LINEAR_SCALE * FanGraphs runs; P neutral."""
        self.assertEqual(
            DEFENSIVE_LEVERAGE_UP_THE_MIDDLE,
            defense_multipliers_from_positional_adjustment_runs(),
        )
        self.assertEqual(DEFENSIVE_LEVERAGE_UP_THE_MIDDLE["P"], 1.0)
        s = DEFAULT_LEVERAGE_LINEAR_SCALE
        self.assertAlmostEqual(
            DEFENSIVE_LEVERAGE_UP_THE_MIDDLE["C"],
            1.0 + s * FGRAPHS_POSITIONAL_ADJUSTMENT_RUNS["C"],
        )
        self.assertAlmostEqual(
            DEFENSIVE_LEVERAGE_UP_THE_MIDDLE["1B"],
            1.0 + s * FGRAPHS_POSITIONAL_ADJUSTMENT_RUNS["1B"],
        )


if __name__ == "__main__":
    unittest.main()

