"""
Unit tests for knowledge_base.py
"""

# Changes made to tests:
# - Added comprehensive unit tests covering `add_fact`, `evaluate` for
#   catchers and general positions, normalization/bounds, and
#   `get_rule_description`.
# - Tests include perfect/poor players and out-of-range inputs to ensure
#   normalization and clamping behavior.
# - Tests also run against test_data/defensive_stats.json.

import json
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module2.knowledge_base import DefensiveKnowledgeBase, DefensiveFact

_TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'test_data'
_JSON_PATH = _TEST_DATA_DIR / 'defensive_stats.json'


def _load_test_data_json():
    with open(_JSON_PATH, 'r') as f:
        return json.load(f)


class TestDefensiveKnowledgeBase(unittest.TestCase):
    """Test cases for DefensiveKnowledgeBase."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.kb = DefensiveKnowledgeBase()
    
    def test_add_fact_catcher_fields(self):
        pdata = {
            'player_name': 'Jane Doe',
            'fielding_pct': 0.995,
            'errors': 1,
            'putouts': 200,
            'passed_balls': 2,
            'caught_stealing_pct': 0.4,
        }

        fact = self.kb.add_fact(pdata, 'C')
        self.assertEqual(fact.player_name, 'Jane Doe')
        self.assertEqual(fact.position, 'C')
        self.assertAlmostEqual(fact.fielding_pct, 0.995)
        self.assertEqual(fact.errors, 1)
        self.assertEqual(fact.putouts, 200)
        self.assertEqual(fact.passed_balls, 2)
        self.assertAlmostEqual(fact.caught_stealing_pct, 0.4)
        self.assertTrue(fact.is_catcher)

    def test_evaluate_catcher_perfect_and_poor(self):
        perfect = {
            'player_name': 'Perfect C',
            'fielding_pct': 1.0,
            'errors': 0,
            'putouts': 100,
            'passed_balls': 0,
            'caught_stealing_pct': 1.0,
        }
        poor = {
            'player_name': 'Poor C',
            'fielding_pct': 0.0,
            'errors': 10,
            'putouts': 0,
            'passed_balls': 10,
            'caught_stealing_pct': 0.0,
        }

        pf = self.kb.add_fact(perfect, 'C')
        pp = self.kb.add_fact(poor, 'C')

        score_perfect = self.kb.evaluate(pf)
        score_poor = self.kb.evaluate(pp)

        self.assertAlmostEqual(score_perfect, 1.0, places=6)
        self.assertAlmostEqual(score_poor, 0.0, places=6)

    def test_evaluate_general_position_perfect_and_poor(self):
        perfect = {
            'player_name': 'Perfect 2B',
            'fielding_pct': 1.0,
            'errors': 0,
            'putouts': 100,
        }
        poor = {
            'player_name': 'Poor 2B',
            'fielding_pct': 0.0,
            'errors': 10,
            'putouts': 0,
        }

        pf = self.kb.add_fact(perfect, '2B')
        pp = self.kb.add_fact(poor, '2B')

        score_perfect = self.kb.evaluate(pf)
        score_poor = self.kb.evaluate(pp)

        self.assertAlmostEqual(score_perfect, 1.0, places=6)
        self.assertAlmostEqual(score_poor, 0.0, places=6)

    def test_evaluate_bounds_and_normalization(self):
        # Provide out-of-range inputs to ensure normalization and clamping
        weird = {
            'player_name': 'Weird',
            'fielding_pct': 150,   # should be treated as 1.5 -> 1.0 after normalization
            'errors': -5,
            'putouts': 0,
            'passed_balls': -1,
            'caught_stealing_pct': 200,
        }

        f = self.kb.add_fact(weird, 'C')
        score = self.kb.evaluate(f)

        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_get_rule_description(self):
        desc_c = self.kb.get_rule_description('C')
        desc_2b = self.kb.get_rule_description('2B')

        self.assertIn('Catcher rule', desc_c)
        self.assertIn('General rule', desc_2b)

    def test_add_fact_from_test_data_catcher(self):
        """Create fact for a catcher from test_data JSON (e.g. Drake Baldwin)."""
        players = _load_test_data_json()
        catcher = next(p for p in players if 'C' in p.get('positions', []) and p.get('name') == 'Drake Baldwin')
        fact = self.kb.add_fact(catcher, 'C')
        self.assertEqual(fact.player_name, 'Drake Baldwin')
        self.assertEqual(fact.position, 'C')
        self.assertTrue(fact.is_catcher)
        self.assertEqual(fact.passed_balls, 3)
        self.assertAlmostEqual(fact.caught_stealing_pct, 0.137)

    def test_add_fact_from_test_data_general_position(self):
        """Create fact for a general position from test_data JSON (e.g. Matt Olson 1B)."""
        players = _load_test_data_json()
        matt = next(p for p in players if p.get('name') == 'Matt Olson')
        fact = self.kb.add_fact(matt, '1B')
        self.assertEqual(fact.player_name, 'Matt Olson')
        self.assertEqual(fact.position, '1B')
        self.assertFalse(fact.is_catcher)
        self.assertEqual(fact.errors, 5)
        self.assertEqual(fact.putouts, 1147)

    def test_evaluate_all_from_test_data_bounds(self):
        """All players/positions in test_data JSON evaluate to score in 0-1."""
        players = _load_test_data_json()
        for player in players:
            positions = player.get('positions', [])
            for pos in positions:
                fact = self.kb.add_fact(player, pos)
                score = self.kb.evaluate(fact)
                self.assertGreaterEqual(score, 0.0, f"{player.get('name')} @ {pos}")
                self.assertLessEqual(score, 1.0, f"{player.get('name')} @ {pos}")


if __name__ == '__main__':
    unittest.main()
