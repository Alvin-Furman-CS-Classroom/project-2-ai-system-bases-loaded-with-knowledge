"""
Unit tests for Module 1 matchup analyzer.
"""

import unittest
import sys
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.matchup_analyzer import analyze_matchup_performance
from module1.models import Batter, Pitcher


class MockRuleEvaluator:
    """Mock rule evaluator for testing."""
    
    def __init__(self, adjustments: Dict[str, float]):
        """
        Initialize with predefined adjustments.
        
        Args:
            adjustments: Dictionary mapping batter names to adjustments
        """
        self.adjustments = adjustments
    
    def evaluate(self, batters: List[Batter], pitcher: Pitcher) -> Dict[str, float]:
        """Return predefined adjustments."""
        return self.adjustments


class TestMatchupAnalyzer(unittest.TestCase):
    """Test cases for matchup analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent.parent.parent / 'test_data'
    
    def test_analyze_matchup_performance_json(self):
        """Test analyzing matchup performance from JSON file."""
        json_file = self.test_data_dir / 'matchup_stats.json'
        if json_file.exists():
            scores = analyze_matchup_performance(str(json_file))
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
            
            # Check that all scores are in valid range
            for batter_name, score in scores.items():
                self.assertIsInstance(batter_name, str)
                self.assertIsInstance(score, float)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)
            
            # Check that expected batters are present
            self.assertIn("Mike Trout", scores)
            self.assertIn("Freddie Freeman", scores)
    
    def test_analyze_matchup_performance_csv(self):
        """Test analyzing matchup performance from CSV file."""
        csv_file = self.test_data_dir / 'matchup_stats.csv'
        if csv_file.exists():
            scores = analyze_matchup_performance(str(csv_file))
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
            
            # Check that all scores are in valid range
            for batter_name, score in scores.items():
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)
    
    def test_analyze_matchup_performance_with_rule_evaluator(self):
        """Test analyzing with a rule evaluator."""
        json_file = self.test_data_dir / 'matchup_stats.json'
        if json_file.exists():
            # Create mock rule evaluator with adjustments
            adjustments = {
                "Mike Trout": 10.0,
                "Freddie Freeman": -5.0,
                "Mookie Betts": 8.0
            }
            evaluator = MockRuleEvaluator(adjustments)
            
            scores = analyze_matchup_performance(str(json_file), rule_evaluator=evaluator)
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
            
            # Scores should reflect adjustments
            # (We can't check exact values since base scores depend on stats,
            # but we can verify scores are in valid range)
            for batter_name, score in scores.items():
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)
    
    def test_analyze_matchup_performance_without_rule_evaluator(self):
        """Test analyzing without rule evaluator (base scores only)."""
        json_file = self.test_data_dir / 'matchup_stats.json'
        if json_file.exists():
            scores_no_evaluator = analyze_matchup_performance(str(json_file))
            scores_with_none = analyze_matchup_performance(str(json_file), rule_evaluator=None)
            
            # Both should produce same results (base scores only)
            self.assertEqual(scores_no_evaluator, scores_with_none)
            
            # Scores should be in valid range
            for score in scores_no_evaluator.values():
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)
    
    def test_analyze_matchup_performance_invalid_file(self):
        """Test analyzing with invalid file path."""
        with self.assertRaises(FileNotFoundError):
            analyze_matchup_performance('nonexistent_file.json')
    
    def test_analyze_matchup_performance_callable_evaluator(self):
        """Test that callable evaluators work (not just objects with evaluate method)."""
        json_file = self.test_data_dir / 'matchup_stats.json'
        if json_file.exists():
            # Create a callable function as evaluator
            def evaluator_func(batters, pitcher):
                return {"Mike Trout": 5.0}
            
            scores = analyze_matchup_performance(str(json_file), rule_evaluator=evaluator_func)
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
    
    def test_analyze_matchup_performance_evaluator_error_handling(self):
        """Test that evaluator errors don't crash the function."""
        json_file = self.test_data_dir / 'matchup_stats.json'
        if json_file.exists():
            # Create evaluator that raises an error
            class ErrorEvaluator:
                def evaluate(self, batters, pitcher):
                    raise ValueError("Test error")
            
            # Should still work, just without adjustments
            scores = analyze_matchup_performance(str(json_file), rule_evaluator=ErrorEvaluator())
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
            
            # Should have base scores (no adjustments applied)
            for score in scores.values():
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)
    
    def test_analyze_matchup_performance_evaluator_missing_method(self):
        """Test evaluator without evaluate method."""
        json_file = self.test_data_dir / 'matchup_stats.json'
        if json_file.exists():
            # Create object without evaluate method
            class NoMethodEvaluator:
                pass
            
            # Should still work, just without adjustments
            scores = analyze_matchup_performance(str(json_file), rule_evaluator=NoMethodEvaluator())
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)


if __name__ == '__main__':
    unittest.main()
