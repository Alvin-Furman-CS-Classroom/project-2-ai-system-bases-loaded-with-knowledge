"""
Unit tests for score_calculator.py
"""

# Changes made to tests:
# - Added tests for `calculate_score` covering catcher and general
#   position perfect scores, normalization and bounds, and batch scoring
#   via `calculate_all_scores` for multiple players and positions.

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module2.score_calculator import ScoreCalculator
from module2.knowledge_base import DefensiveKnowledgeBase, DefensiveFact


class TestScoreCalculator(unittest.TestCase):
    """Test cases for ScoreCalculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.kb = DefensiveKnowledgeBase()
        self.calculator = ScoreCalculator(self.kb)
    
    def test_calculate_score_catcher_and_general(self):
        catcher = self.kb.add_fact({
            'player_name': 'Catchy',
            'fielding_pct': 1.0,
            'errors': 0,
            'putouts': 50,
            'passed_balls': 0,
            'caught_stealing_pct': 1.0,
        }, 'C')

        infielder = self.kb.add_fact({
            'player_name': 'Infy',
            'fielding_pct': 1.0,
            'errors': 0,
            'putouts': 100,
        }, '2B')

        score_c = self.calculator.calculate_score(catcher)
        score_i = self.calculator.calculate_score(infielder)

        self.assertAlmostEqual(score_c, 100.0, places=6)
        self.assertAlmostEqual(score_i, 100.0, places=6)

    def test_score_bounds_and_normalization(self):
        weird = self.kb.add_fact({
            'player_name': 'Weird',
            'fielding_pct': 150,  # should normalize
            'errors': -3,
            'putouts': 0,
            'passed_balls': -1,
            'caught_stealing_pct': 200,
        }, 'C')

        score = self.calculator.calculate_score(weird)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_calculate_all_scores_multiple_players(self):
        facts_dict = {
            'Alpha': {
                'RF': self.kb.add_fact({'player_name': 'Alpha', 'fielding_pct': 0.9, 'errors': 2, 'putouts': 80}, 'RF')
            },
            'Beta': {
                'C': self.kb.add_fact({'player_name': 'Beta', 'fielding_pct': 0.95, 'errors': 1, 'putouts': 100, 'passed_balls': 0, 'caught_stealing_pct': 0.5}, 'C'),
                'SS': self.kb.add_fact({'player_name': 'Beta', 'fielding_pct': 0.92, 'errors': 3, 'putouts': 120}, 'SS')
            }
        }

        scores = self.calculator.calculate_all_scores(facts_dict)
        self.assertIn('Alpha', scores)
        self.assertIn('Beta', scores)
        self.assertIn('RF', scores['Alpha'])
        self.assertIn('C', scores['Beta'])
        self.assertIn('SS', scores['Beta'])

        # Ensure numeric scores and in range
        for pname, pmap in scores.items():
            for pos, val in pmap.items():
                self.assertIsInstance(val, float)
                self.assertGreaterEqual(val, 0.0)
                self.assertLessEqual(val, 100.0)

    def test_kb_value_used_when_available(self):
        # Fake KB that returns a fixed raw score (0-1)
        class FakeKB:
            def evaluate(self, fact):
                return 0.42

        fake_kb = FakeKB()
        calc = ScoreCalculator(fake_kb)
        fact = DefensiveFact(player_name='X', position='RF', fielding_pct=0.9, errors=1, putouts=10)
        score = calc.calculate_score(fact)
        self.assertAlmostEqual(score, 42.0, places=6)

    def test_kb_exception_triggers_local_fallback(self):
        class BrokenKB:
            def evaluate(self, fact):
                raise RuntimeError('kb failure')

        calc = ScoreCalculator(BrokenKB())
        # non-catcher perfect stats should yield 100 via fallback
        fact = DefensiveFact(player_name='Y', position='2B', fielding_pct=1.0, errors=0, putouts=100)
        score = calc.calculate_score(fact)
        self.assertAlmostEqual(score, 100.0, places=6)

    def test_calculate_score_none_raises(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_score(None)

    def test_calculate_all_scores_with_empty_facts(self):
        facts_dict = {'Empty': {}}
        scores = self.calculator.calculate_all_scores(facts_dict)
        self.assertIn('Empty', scores)
        self.assertEqual(scores['Empty'], {})


if __name__ == '__main__':
    unittest.main()
