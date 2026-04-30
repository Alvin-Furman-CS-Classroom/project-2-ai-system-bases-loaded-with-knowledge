"""
Unit tests for Module 1 score calculator.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.score_calculator import ScoreCalculator
from module1.models import Batter, Pitcher


class TestScoreCalculator(unittest.TestCase):
    """Test cases for score calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = ScoreCalculator()
    
    def test_calculate_base_score(self):
        """Test base score calculation from batter stats."""
        batter = Batter(
            name="Test Player",
            ba=0.300,
            k=100,
            obp=0.350,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="R"
        )
        
        base_score = self.calculator.calculate_base_score(batter)
        
        # Base score should be weighted average: 0.30*BA + 0.40*OBP + 0.30*SLG
        # Expected: 0.30*0.300 + 0.40*0.350 + 0.30*0.450 = 0.09 + 0.14 + 0.135 = 0.365
        # In 0-100 scale: 36.5
        expected = (0.30 * 0.300 + 0.40 * 0.350 + 0.30 * 0.450) * 100.0
        
        self.assertAlmostEqual(base_score, expected, places=1)
        self.assertGreaterEqual(base_score, 0.0)
        self.assertLessEqual(base_score, 100.0)
    
    def test_calculate_base_score_perfect_stats(self):
        """Test base score with perfect stats (1.000 for all)."""
        batter = Batter(
            name="Perfect Player",
            ba=1.000,
            k=0,
            obp=1.000,
            slg=1.000,
            hr=100,
            rbi=200,
            handedness="R"
        )
        
        base_score = self.calculator.calculate_base_score(batter)
        
        # Perfect stats should give 100.0
        self.assertAlmostEqual(base_score, 100.0, places=1)
    
    def test_calculate_base_score_zero_stats(self):
        """Test base score with zero stats."""
        batter = Batter(
            name="Zero Player",
            ba=0.000,
            k=500,
            obp=0.000,
            slg=0.000,
            hr=0,
            rbi=0,
            handedness="R"
        )
        
        base_score = self.calculator.calculate_base_score(batter)
        
        # Zero stats should give 0.0
        self.assertAlmostEqual(base_score, 0.0, places=1)
    
    def test_calculate_base_score_none_batter(self):
        """Test that None batter raises ValueError."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_base_score(None)
    
    def test_apply_adjustments_positive(self):
        """Test applying positive adjustment."""
        base_score = 50.0
        adjustment = 15.0
        
        result = self.calculator.apply_adjustments(base_score, adjustment)
        
        self.assertAlmostEqual(result, 65.0, places=1)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 100.0)
    
    def test_apply_adjustments_negative(self):
        """Test applying negative adjustment."""
        base_score = 50.0
        adjustment = -20.0
        
        result = self.calculator.apply_adjustments(base_score, adjustment)
        
        self.assertAlmostEqual(result, 30.0, places=1)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 100.0)
    
    def test_apply_adjustments_clamp_upper(self):
        """Test that scores are clamped to 100 maximum."""
        base_score = 95.0
        adjustment = 20.0  # Would exceed 100
        
        result = self.calculator.apply_adjustments(base_score, adjustment)
        
        self.assertAlmostEqual(result, 100.0, places=1)
    
    def test_apply_adjustments_clamp_lower(self):
        """Test that scores are clamped to 0 minimum."""
        base_score = 10.0
        adjustment = -25.0  # Would go below 0
        
        result = self.calculator.apply_adjustments(base_score, adjustment)
        
        self.assertAlmostEqual(result, 0.0, places=1)
    
    def test_apply_adjustments_none(self):
        """Test applying None adjustment (should default to 0)."""
        base_score = 50.0
        
        result = self.calculator.apply_adjustments(base_score, None)
        
        self.assertAlmostEqual(result, 50.0, places=1)
    
    def test_calculate_final_score(self):
        """Test final score calculation with adjustment."""
        batter = Batter(
            name="Test Player",
            ba=0.300,
            k=100,
            obp=0.350,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="R"
        )
        
        final_score = self.calculator.calculate_final_score(batter, adjustment=10.0)
        
        base_score = self.calculator.calculate_base_score(batter)
        expected = base_score + 10.0
        
        self.assertAlmostEqual(final_score, expected, places=1)
        self.assertGreaterEqual(final_score, 0.0)
        self.assertLessEqual(final_score, 100.0)
    
    def test_calculate_final_score_no_adjustment(self):
        """Test final score calculation without adjustment."""
        batter = Batter(
            name="Test Player",
            ba=0.300,
            k=100,
            obp=0.350,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="R"
        )
        
        final_score = self.calculator.calculate_final_score(batter)
        base_score = self.calculator.calculate_base_score(batter)
        
        self.assertAlmostEqual(final_score, base_score, places=1)
    
    def test_calculate_all_scores(self):
        """Test calculating scores for multiple batters."""
        batters = [
            Batter(name="Player 1", ba=0.300, k=100, obp=0.350, slg=0.450, hr=20, rbi=70, handedness="R"),
            Batter(name="Player 2", ba=0.280, k=120, obp=0.320, slg=0.420, hr=15, rbi=60, handedness="L"),
        ]
        
        adjustments = {
            "Player 1": 10.0,
            "Player 2": -5.0
        }
        
        results = self.calculator.calculate_all_scores(batters, adjustments)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 2)
        self.assertIn("Player 1", results)
        self.assertIn("Player 2", results)
        
        # Check that scores are in valid range
        for name, score in results.items():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)
    
    def test_calculate_all_scores_no_adjustments(self):
        """Test calculating scores without adjustments."""
        batters = [
            Batter(name="Player 1", ba=0.300, k=100, obp=0.350, slg=0.450, hr=20, rbi=70, handedness="R"),
        ]
        
        results = self.calculator.calculate_all_scores(batters)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 1)
        self.assertIn("Player 1", results)
        
        # Score should equal base score (no adjustments)
        base_score = self.calculator.calculate_base_score(batters[0])
        self.assertAlmostEqual(results["Player 1"], base_score, places=1)
    
    def test_calculate_all_scores_missing_adjustment(self):
        """Test that missing adjustments default to 0."""
        batters = [
            Batter(name="Player 1", ba=0.300, k=100, obp=0.350, slg=0.450, hr=20, rbi=70, handedness="R"),
        ]
        
        adjustments = {
            "Player 2": 10.0  # Adjustment for different player
        }
        
        results = self.calculator.calculate_all_scores(batters, adjustments)
        
        # Player 1 should get base score (no adjustment applied)
        base_score = self.calculator.calculate_base_score(batters[0])
        self.assertAlmostEqual(results["Player 1"], base_score, places=1)
    
    def test_normalize_score(self):
        """Test score normalization."""
        # Normal score should remain unchanged
        self.assertAlmostEqual(self.calculator.normalize_score(50.0), 50.0, places=1)
        
        # Score above 100 should be clamped
        self.assertAlmostEqual(self.calculator.normalize_score(150.0), 100.0, places=1)
        
        # Score below 0 should be clamped
        self.assertAlmostEqual(self.calculator.normalize_score(-10.0), 0.0, places=1)
    
    def test_normalize_score_custom_range(self):
        """Test normalization with custom range."""
        result = self.calculator.normalize_score(75.0, min_score=0.0, max_score=50.0)
        self.assertAlmostEqual(result, 50.0, places=1)
    
    def test_normalize_score_invalid_input(self):
        """Test normalization with invalid input."""
        result = self.calculator.normalize_score("invalid")
        self.assertAlmostEqual(result, 0.0, places=1)


if __name__ == '__main__':
    unittest.main()
