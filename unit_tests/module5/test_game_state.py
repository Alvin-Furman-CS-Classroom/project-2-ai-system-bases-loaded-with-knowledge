"""
Unit tests for src/module5/game_state.py (Person A deliverables).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module5.game_state import GameStateValidationError, normalize_game_state


def _valid_state():
    return {
        "inning": 7,
        "half": "bottom",
        "outs": 1,
        "score_for": 4,
        "score_against": 3,
        "bases": [True, False, True],
        "substitutions_used": 2,
        "substitutions_limit": 5,
        "pitcher_fatigue": 0.4,
    }


class TestGameStateValidation(unittest.TestCase):
    def test_normalize_game_state_success(self):
        state = normalize_game_state(_valid_state())
        self.assertEqual(state.inning, 7)
        self.assertEqual(state.half, "bottom")
        self.assertEqual(state.outs, 1)
        self.assertEqual(state.substitutions_remaining, 3)
        self.assertEqual(state.score_diff, 1)

    def test_missing_required_key_raises(self):
        state = _valid_state()
        del state["outs"]
        with self.assertRaises(GameStateValidationError):
            normalize_game_state(state)

    def test_outs_must_be_0_to_2(self):
        state = _valid_state()
        state["outs"] = 3
        with self.assertRaises(GameStateValidationError):
            normalize_game_state(state)

    def test_substitution_invariant(self):
        state = _valid_state()
        state["substitutions_used"] = 6
        with self.assertRaises(GameStateValidationError):
            normalize_game_state(state)


if __name__ == "__main__":
    unittest.main()
