"""
Unit tests for score_calculator.py

Tests cover score calculation for catchers and general positions, normalization
and bounds checking, batch scoring, and fallback behavior when knowledge base
evaluation fails.
"""

import json
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module2.score_calculator import ScoreCalculator
from module2.knowledge_base import DefensiveKnowledgeBase, DefensiveFact

_TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'test_data'
_JSON_PATH = _TEST_DATA_DIR / 'defensive_stats.json'


def _load_test_data_json():
    with open(_JSON_PATH, 'r') as f:
        return json.load(f)


def _build_facts_dict_from_test_data(kb):
    """Build {player_name: {position: DefensiveFact}} from test_data JSON."""
    players = _load_test_data_json()
    result = {}
    for p in players:
        name = p.get('name') or p.get('player_name', '')
        positions = p.get('positions', [])
        result[name] = {}
        for pos in positions:
            result[name][pos] = kb.add_fact(p, pos)
    return result


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
            'putouts': 100,
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

    def test_calculate_score_from_test_data_catcher(self):
        """Score for a catcher from test_data JSON is in 0-100."""
        players = _load_test_data_json()
        drake = next(p for p in players if p.get('name') == 'Drake Baldwin')
        fact = self.kb.add_fact(drake, 'C')
        score = self.calculator.calculate_score(fact)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_calculate_score_from_test_data_general(self):
        """Score for a general position from test_data JSON is in 0-100."""
        players = _load_test_data_json()
        matt = next(p for p in players if p.get('name') == 'Matt Olson')
        fact = self.kb.add_fact(matt, '1B')
        score = self.calculator.calculate_score(fact)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_calculate_all_scores_from_test_data(self):
        """calculate_all_scores with test_data JSON returns expected structure and players."""
        facts_dict = _build_facts_dict_from_test_data(self.kb)
        scores = self.calculator.calculate_all_scores(facts_dict)
        self.assertIn('Matt Olson', scores)
        self.assertIn('Drake Baldwin', scores)
        self.assertIn('Sean Murphy', scores)
        for player_name, position_scores in scores.items():
            for pos, score in position_scores.items():
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)


if __name__ == '__main__':
    unittest.main()
