"""
Unit tests for position_evaluator.py
"""

# Changes made to tests:
# - Added tests for parsing eligible positions from list and string inputs.
# - Added filtering tests for invalid positions.
# - Added tests verifying `evaluate_player_positions` builds `DefensiveFact`
#   objects and that `evaluate_all_players` aggregates results for multiple
#   players. Also added handling test for players with no positions.

import json
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module2.position_evaluator import PositionEvaluator
from module2.knowledge_base import DefensiveKnowledgeBase, DefensiveFact

_TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'test_data'
_JSON_PATH = _TEST_DATA_DIR / 'defensive_stats.json'


def _load_test_data_json():
    with open(_JSON_PATH, 'r') as f:
        return json.load(f)


class TestPositionEvaluator(unittest.TestCase):
    """Test cases for PositionEvaluator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.kb = DefensiveKnowledgeBase()
        self.evaluator = PositionEvaluator(self.kb)
    
    def test_get_eligible_positions_list_and_string(self):
        pdata_list = {'player_name': 'Alice', 'positions': ['C', '3B', 'P']}
        eligible_list = self.evaluator.get_eligible_positions(pdata_list)
        self.assertIn('C', eligible_list)
        self.assertIn('3B', eligible_list)
        self.assertNotIn('P', eligible_list)

        pdata_str = {'player_name': 'Bob', 'positions': '1B, RF/CF'}
        eligible_str = self.evaluator.get_eligible_positions(pdata_str)
        # order preserved and normalized
        self.assertEqual(eligible_str, ['1B', 'RF', 'CF'])

    def test_filter_invalid_positions(self):
        pdata = {'player_name': 'Charlie', 'positions': ['DH', 'LF', 'SS', 'Coach']}
        eligible = self.evaluator.get_eligible_positions(pdata)
        self.assertEqual(eligible, ['LF', 'SS'])

    def test_evaluate_player_positions(self):
        pdata = {
            'player_name': 'Diana',
            'positions': 'C,2B',
            'fielding_pct': 0.98,
            'errors': 2,
            'putouts': 120,
            'passed_balls': 1,
            'caught_stealing_pct': 0.35,
        }

        facts = self.evaluator.evaluate_player_positions(pdata)
        self.assertIn('C', facts)
        self.assertIn('2B', facts)
        self.assertIsInstance(facts['C'], DefensiveFact)
        self.assertEqual(facts['C'].player_name, 'Diana')
        self.assertEqual(facts['C'].position, 'C')

    def test_evaluate_all_players(self):
        players = [
            {'player_name': 'Eve', 'positions': 'RF', 'fielding_pct': 0.9, 'errors': 5, 'putouts': 80},
            {'player_name': 'Frank', 'positions': ['SS', '2B'], 'fielding_pct': 0.95, 'errors': 2, 'putouts': 150},
        ]

        all_facts = self.evaluator.evaluate_all_players(players)
        self.assertIn('Eve', all_facts)
        self.assertIn('Frank', all_facts)
        self.assertIn('RF', all_facts['Eve'])
        self.assertIn('SS', all_facts['Frank'])
        self.assertIn('2B', all_facts['Frank'])

    def test_handling_players_with_no_positions(self):
        players = [
            {'player_name': 'Gina', 'fielding_pct': 0.8, 'errors': 3, 'putouts': 50},
        ]

        all_facts = self.evaluator.evaluate_all_players(players)
        # Gina should be present but with empty position facts
        self.assertIn('Gina', all_facts)
        self.assertEqual(all_facts['Gina'], {})

    def test_lowercase_and_spaced_positions(self):
        pdata = {'player_name': 'Helen', 'positions': ' c , ss '}
        eligible = self.evaluator.get_eligible_positions(pdata)
        self.assertEqual(eligible, ['C', 'SS'])

    def test_duplicate_positions_preserved(self):
        pdata = {'player_name': 'Ivan', 'positions': ['RF', 'rf', 'RF']}
        eligible = self.evaluator.get_eligible_positions(pdata)
        # duplicates are preserved and normalized
        self.assertEqual(eligible, ['RF', 'RF', 'RF'])

    def test_unknown_positions_type_returns_empty(self):
        pdata = {'player_name': 'Judy', 'positions': 123}
        eligible = self.evaluator.get_eligible_positions(pdata)
        self.assertEqual(eligible, [])

    def test_large_mixed_list_filters_and_preserves_order(self):
        pdata = {'player_name': 'Kyle', 'positions': ['P', 'lf', '2B', 'coach', 'SS']}
        eligible = self.evaluator.get_eligible_positions(pdata)
        self.assertEqual(eligible, ['LF', '2B', 'SS'])

    def test_missing_name_fallback_key(self):
        players = [
            {'positions': 'RF', 'fielding_pct': 0.9, 'errors': 2, 'putouts': 80},
        ]

        all_facts = self.evaluator.evaluate_all_players(players)
        # fallback key should be present (uses 'unknown' when no name/id)
        self.assertIn('unknown', all_facts)

    def test_get_eligible_positions_from_test_data(self):
        """Eligible positions for a player from test_data JSON."""
        players = _load_test_data_json()
        matt = next(p for p in players if p.get('name') == 'Matt Olson')
        positions = self.evaluator.get_eligible_positions(matt)
        self.assertIn('1B', positions)
        self.assertEqual(len(positions), 1)

    def test_evaluate_player_positions_from_test_data(self):
        """evaluate_player_positions for a player from test_data JSON."""
        players = _load_test_data_json()
        nick = next(p for p in players if p.get('name') == 'Nick Allen')
        facts = self.evaluator.evaluate_player_positions(nick)
        self.assertIn('SS', facts)
        self.assertIn('2B', facts)
        self.assertEqual(facts['SS'].player_name, 'Nick Allen')
        self.assertEqual(facts['SS'].position, 'SS')

    def test_evaluate_all_players_from_test_data(self):
        """evaluate_all_players with test_data JSON returns expected players and positions."""
        players = _load_test_data_json()
        result = self.evaluator.evaluate_all_players(players)
        self.assertIn('Matt Olson', result)
        self.assertIn('Drake Baldwin', result)
        self.assertIn('1B', result['Matt Olson'])
        self.assertIn('C', result['Drake Baldwin'])


if __name__ == '__main__':
    unittest.main()
