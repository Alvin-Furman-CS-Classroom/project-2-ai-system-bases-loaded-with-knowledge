"""
Unit tests for multiple batters vs multiple pitchers (matrix) functionality.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.matchup_analyzer import (
    analyze_matchups_matrix,
    analyze_matchups_matrix_from_file
)
from module1.models import Batter, Pitcher


class TestMatchupsMatrix(unittest.TestCase):
    """Test cases for matrix matchup analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.batters = [
            Batter(name="Batter 1", ba=0.300, k=100, obp=0.350, slg=0.450,
                   hr=20, rbi=70, handedness="R"),
            Batter(name="Batter 2", ba=0.280, k=120, obp=0.320, slg=0.420,
                   hr=15, rbi=60, handedness="L"),
        ]
        
        self.pitchers = [
            Pitcher(name="Pitcher 1", era=3.00, whip=1.00, k_rate=0.25,
                   handedness="RHP", walk_rate=0.08),
            Pitcher(name="Pitcher 2", era=2.50, whip=0.95, k_rate=0.30,
                   handedness="LHP", walk_rate=0.06),
        ]
    
    def test_analyze_matchups_matrix(self):
        """Test analyzing multiple batters against multiple pitchers."""
        scores = analyze_matchups_matrix(self.batters, self.pitchers)
        
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(scores), 2)  # 2 batters
        
        # Check all batters are present
        self.assertIn("Batter 1", scores)
        self.assertIn("Batter 2", scores)
        
        # Check nested structure
        for batter_name, pitcher_scores in scores.items():
            self.assertIsInstance(pitcher_scores, dict)
            self.assertEqual(len(pitcher_scores), 2)  # 2 pitchers
            
            # Check all pitchers are present for each batter
            self.assertIn("Pitcher 1", pitcher_scores)
            self.assertIn("Pitcher 2", pitcher_scores)
            
            # Check scores are in valid range
            for pitcher_name, score in pitcher_scores.items():
                self.assertIsInstance(score, float)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)
    
    def test_analyze_matchups_matrix_single_batter(self):
        """Test with single batter."""
        single_batter = [self.batters[0]]
        scores = analyze_matchups_matrix(single_batter, self.pitchers)
        
        self.assertEqual(len(scores), 1)
        self.assertIn("Batter 1", scores)
        self.assertEqual(len(scores["Batter 1"]), 2)
    
    def test_analyze_matchups_matrix_single_pitcher(self):
        """Test with single pitcher."""
        single_pitcher = [self.pitchers[0]]
        scores = analyze_matchups_matrix(self.batters, single_pitcher)
        
        self.assertEqual(len(scores), 2)
        for batter_name in scores:
            self.assertEqual(len(scores[batter_name]), 1)
            self.assertIn("Pitcher 1", scores[batter_name])
    
    def test_analyze_matchups_matrix_empty_batters(self):
        """Test with empty batters list."""
        with self.assertRaises(ValueError):
            analyze_matchups_matrix([], self.pitchers)
    
    def test_analyze_matchups_matrix_empty_pitchers(self):
        """Test with empty pitchers list."""
        with self.assertRaises(ValueError):
            analyze_matchups_matrix(self.batters, [])
    
    def test_analyze_matchups_matrix_pitcher_no_name(self):
        """Test with pitchers without names."""
        pitcher_no_name = Pitcher(
            era=3.00, whip=1.00, k_rate=0.25,
            handedness="RHP", walk_rate=0.08
        )
        
        scores = analyze_matchups_matrix(self.batters, [pitcher_no_name])
        
        self.assertEqual(len(scores), 2)
        # Should use default name "Pitcher_1"
        self.assertIn("Pitcher_1", scores["Batter 1"])
    
    def test_analyze_matchups_matrix_from_file_json(self):
        """Test analyzing from JSON file."""
        json_file = Path(__file__).parent.parent.parent / 'test_data' / 'matchups_matrix.json'
        if json_file.exists():
            scores = analyze_matchups_matrix_from_file(str(json_file))
            
            self.assertIsInstance(scores, dict)
            self.assertGreater(len(scores), 0)
            
            # Check nested structure
            for batter_name, pitcher_scores in scores.items():
                self.assertIsInstance(pitcher_scores, dict)
                self.assertGreater(len(pitcher_scores), 0)
                
                # Check scores are in valid range
                for pitcher_name, score in pitcher_scores.items():
                    self.assertGreaterEqual(score, 0.0)
                    self.assertLessEqual(score, 100.0)
    
    def test_analyze_matchups_matrix_from_file_csv(self):
        """Test analyzing from CSV file."""
        # Create a CSV file with multiple batters and pitchers
        csv_file = Path(__file__).parent.parent.parent / 'test_data' / 'matchups_matrix.csv'
        
        # We'll use the existing batter_vs_pitchers.csv which has multiple pitchers
        # but we need multiple batters - let's check if we can use a modified version
        # For now, just test that the function can handle CSV format
        if csv_file.exists():
            scores = analyze_matchups_matrix_from_file(str(csv_file))
            self.assertIsInstance(scores, dict)
    
    def test_analyze_matchups_matrix_with_rule_evaluator(self):
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
        scores = analyze_matchups_matrix(self.batters, self.pitchers, evaluator)
        
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(scores), 2)
        
        # Scores should differ based on pitcher ERA
        # Pitcher 2 has ERA 2.50 (< 3.0) - should have penalty
        # Pitcher 1 has ERA 3.00 - should have no adjustment
        self.assertNotEqual(
            scores["Batter 1"]["Pitcher 1"],
            scores["Batter 1"]["Pitcher 2"]
        )
    
    def test_analyze_matchups_matrix_access_pattern(self):
        """Test accessing scores in the matrix."""
        scores = analyze_matchups_matrix(self.batters, self.pitchers)
        
        # Test accessing specific matchup
        score = scores["Batter 1"]["Pitcher 1"]
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        
        # Test accessing all matchups for a batter
        batter1_scores = scores["Batter 1"]
        self.assertIsInstance(batter1_scores, dict)
        self.assertEqual(len(batter1_scores), 2)
        
        # Test accessing all matchups for a pitcher (across all batters)
        pitcher1_scores = {batter: scores[batter]["Pitcher 1"] for batter in scores}
        self.assertEqual(len(pitcher1_scores), 2)


if __name__ == '__main__':
    unittest.main()
