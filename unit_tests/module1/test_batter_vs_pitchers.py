"""
Unit tests for batter vs multiple pitchers functionality.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.matchup_analyzer import (
    analyze_batter_vs_pitchers,
    analyze_batter_vs_pitchers_from_file
)
from module1.models import Batter, Pitcher


class TestBatterVsPitchers(unittest.TestCase):
    """Test cases for batter vs multiple pitchers analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.batter = Batter(
            name="Test Batter",
            ba=0.300,
            k=100,
            obp=0.350,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="R"
        )
        
        self.pitchers = [
            Pitcher(name="Pitcher 1", era=3.00, whip=1.00, k_rate=0.25,
                   handedness="RHP", walk_rate=0.08),
            Pitcher(name="Pitcher 2", era=2.50, whip=0.95, k_rate=0.30,
                   handedness="LHP", walk_rate=0.06),
            Pitcher(name="Pitcher 3", era=4.00, whip=1.20, k_rate=0.20,
                   handedness="RHP", walk_rate=0.10),
        ]
    
    def test_analyze_batter_vs_pitchers(self):
        """Test analyzing one batter against multiple pitchers."""
        scores = analyze_batter_vs_pitchers(self.batter, self.pitchers)
        
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(scores), 3)
        
        # Check all pitchers are present
        self.assertIn("Pitcher 1", scores)
        self.assertIn("Pitcher 2", scores)
        self.assertIn("Pitcher 3", scores)
        
        # Check scores are in valid range
        for pitcher_name, score in scores.items():
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)
    
    def test_analyze_batter_vs_pitchers_single_pitcher(self):
        """Test with single pitcher."""
        single_pitcher = [self.pitchers[0]]
        scores = analyze_batter_vs_pitchers(self.batter, single_pitcher)
        
        self.assertEqual(len(scores), 1)
        self.assertIn("Pitcher 1", scores)
    
    def test_analyze_batter_vs_pitchers_no_name(self):
        """Test with pitchers without names."""
        pitcher_no_name = Pitcher(
            era=3.00, whip=1.00, k_rate=0.25,
            handedness="RHP", walk_rate=0.08
        )
        
        scores = analyze_batter_vs_pitchers(self.batter, [pitcher_no_name])
        
        self.assertEqual(len(scores), 1)
        # Should use default name "Pitcher_1"
        self.assertIn("Pitcher_1", scores)
    
    def test_analyze_batter_vs_pitchers_empty_list(self):
        """Test with empty pitchers list."""
        with self.assertRaises(ValueError):
            analyze_batter_vs_pitchers(self.batter, [])
    
    def test_analyze_batter_vs_pitchers_none_batter(self):
        """Test with None batter."""
        with self.assertRaises(ValueError):
            analyze_batter_vs_pitchers(None, self.pitchers)
    
    def test_analyze_batter_vs_pitchers_from_file_json(self):
        """Test analyzing from JSON file."""
        json_file = Path(__file__).parent.parent.parent / 'test_data' / 'batter_vs_pitchers.json'
        if json_file.exists():
            scores = analyze_batter_vs_pitchers_from_file(str(json_file))
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
            
            # Check scores are in valid range
            for pitcher_name, score in scores.items():
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)
    
    def test_analyze_batter_vs_pitchers_from_file_csv(self):
        """Test analyzing from CSV file."""
        csv_file = Path(__file__).parent.parent.parent / 'test_data' / 'batter_vs_pitchers.csv'
        if csv_file.exists():
            scores = analyze_batter_vs_pitchers_from_file(str(csv_file))
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
    
    def test_analyze_batter_vs_pitchers_from_file_specific_batter(self):
        """Test selecting specific batter from file."""
        json_file = Path(__file__).parent.parent.parent / 'test_data' / 'batter_vs_pitchers.json'
        if json_file.exists():
            scores = analyze_batter_vs_pitchers_from_file(
                str(json_file),
                batter_name="Jonathan Ornelas"
            )
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
    
    def test_analyze_batter_vs_pitchers_from_file_invalid_batter(self):
        """Test with invalid batter name."""
        json_file = Path(__file__).parent.parent.parent / 'test_data' / 'batter_vs_pitchers.json'
        if json_file.exists():
            with self.assertRaises(ValueError):
                analyze_batter_vs_pitchers_from_file(
                    str(json_file),
                    batter_name="Nonexistent Batter"
                )
    
    def test_analyze_batter_vs_pitchers_with_rule_evaluator(self):
        """Test with mock rule evaluator."""
        class MockEvaluator:
            def evaluate_single(self, batter, pitcher):
                # Give different adjustments based on pitcher ERA
                if pitcher.era < 3.0:
                    return -5.0  # Penalty for good pitcher
                elif pitcher.era > 3.5:
                    return 5.0   # Bonus for weaker pitcher
                return 0.0
        
        evaluator = MockEvaluator()
        scores = analyze_batter_vs_pitchers(self.batter, self.pitchers, evaluator)
        
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(scores), 3)
        
        # Scores should differ based on pitcher ERA
        # Pitcher 2 has ERA 2.50 (< 3.0) - should have penalty
        # Pitcher 3 has ERA 4.00 (> 3.5) - should have bonus
        self.assertNotEqual(scores["Pitcher 2"], scores["Pitcher 3"])


if __name__ == '__main__':
    unittest.main()
