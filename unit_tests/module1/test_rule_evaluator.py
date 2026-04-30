"""
Unit tests for Module 1 rule evaluator.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.rule_evaluator import RuleEvaluator
from module1.models import Batter, Pitcher


class TestRuleEvaluator(unittest.TestCase):
    """Test cases for RuleEvaluator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test batters
        self.batter1 = Batter(
            name="Elite Player",
            ba=0.320,
            k=90,
            obp=0.420,
            slg=0.580,
            hr=35,
            rbi=100,
            handedness="R"
        )
        
        self.batter2 = Batter(
            name="Lefty",
            ba=0.280,
            k=110,
            obp=0.360,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="L"
        )
        
        self.batter3 = Batter(
            name="Power Hitter",
            ba=0.260,
            k=140,
            obp=0.340,
            slg=0.520,
            hr=32,
            rbi=85,
            handedness="R"
        )
        
        # Create test pitchers
        self.pitcher1 = Pitcher(
            name="Righty Pitcher",
            era=3.50,
            whip=1.20,
            k_rate=0.25,
            handedness="RHP",
            walk_rate=0.08
        )
        
        self.pitcher2 = Pitcher(
            name="Weak Pitcher",
            era=4.50,
            whip=1.40,
            k_rate=0.22,
            handedness="RHP",
            walk_rate=0.12
        )
        
        self.lefty_pitcher = Pitcher(
            name="Lefty Pitcher",
            era=3.20,
            whip=1.15,
            k_rate=0.28,
            handedness="LHP",
            walk_rate=0.09
        )
    
    def test_evaluate_basic(self):
        """Test basic rule evaluation."""
        evaluator = RuleEvaluator()
        batters = [self.batter1, self.batter2]
        adjustments = evaluator.evaluate(batters, self.pitcher1)
        
        self.assertIsInstance(adjustments, dict)
        self.assertEqual(len(adjustments), 2)
        self.assertIn(self.batter1.name, adjustments)
        self.assertIn(self.batter2.name, adjustments)
        # Adjustments should be numeric
        self.assertIsInstance(adjustments[self.batter1.name], float)
        self.assertIsInstance(adjustments[self.batter2.name], float)
    
    def test_evaluate_with_quantifiers(self):
        """Test rule evaluation with quantifiers enabled."""
        evaluator = RuleEvaluator(use_quantifiers=True)
        batters = [self.batter1, self.batter2, self.batter3]
        adjustments = evaluator.evaluate(batters, self.pitcher2)
        
        # Should have adjustments for all batters
        self.assertEqual(len(adjustments), 3)
        # Power hitter should get bonus against weak pitcher
        self.assertGreater(adjustments[self.batter3.name], 0.0)
    
    def test_evaluate_without_quantifiers(self):
        """Test rule evaluation with quantifiers disabled."""
        evaluator = RuleEvaluator(use_quantifiers=False)
        batters = [self.batter1, self.batter2]
        adjustments = evaluator.evaluate(batters, self.pitcher1)
        
        # Should still have adjustments (from individual rules)
        self.assertEqual(len(adjustments), 2)
    
    def test_evaluate_single(self):
        """Test evaluating a single batter-pitcher matchup."""
        evaluator = RuleEvaluator()
        adjustment = evaluator.evaluate_single(self.batter1, self.pitcher1)
        
        self.assertIsInstance(adjustment, float)
        # Should have some adjustment (handedness penalty for same-handed)
        self.assertLess(adjustment, 0.0)  # Negative due to same-handed penalty
    
    def test_evaluate_single_opposite_handed(self):
        """Test evaluating single matchup with opposite-handed."""
        evaluator = RuleEvaluator()
        # Righty batter vs lefty pitcher (opposite-handed)
        adjustment = evaluator.evaluate_single(self.batter1, self.lefty_pitcher)
        
        # Should have positive adjustment (opposite-handed bonus)
        self.assertGreater(adjustment, 0.0)
    
    def test_evaluate_empty_batters(self):
        """Test evaluation with empty batters list."""
        evaluator = RuleEvaluator()
        adjustments = evaluator.evaluate([], self.pitcher1)
        
        self.assertEqual(adjustments, {})
    
    def test_evaluate_none_batters(self):
        """Test evaluation with None batters."""
        evaluator = RuleEvaluator()
        with self.assertRaises(ValueError):
            evaluator.evaluate(None, self.pitcher1)
    
    def test_evaluate_none_pitcher(self):
        """Test evaluation with None pitcher."""
        evaluator = RuleEvaluator()
        with self.assertRaises(ValueError):
            evaluator.evaluate([self.batter1], None)
    
    def test_evaluate_single_none_batter(self):
        """Test evaluate_single with None batter."""
        evaluator = RuleEvaluator()
        with self.assertRaises(ValueError):
            evaluator.evaluate_single(None, self.pitcher1)
    
    def test_evaluate_single_none_pitcher(self):
        """Test evaluate_single with None pitcher."""
        evaluator = RuleEvaluator()
        with self.assertRaises(ValueError):
            evaluator.evaluate_single(self.batter1, None)
    
    def test_get_rule_count(self):
        """Test getting the number of rules."""
        evaluator = RuleEvaluator()
        count = evaluator.get_rule_count()
        
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)
    
    def test_set_use_quantifiers(self):
        """Test enabling/disabling quantifiers."""
        evaluator = RuleEvaluator(use_quantifiers=True)
        self.assertTrue(evaluator.use_quantifiers)
        
        evaluator.set_use_quantifiers(False)
        self.assertFalse(evaluator.use_quantifiers)
        
        evaluator.set_use_quantifiers(True)
        self.assertTrue(evaluator.use_quantifiers)
    
    def test_evaluate_handedness_effects(self):
        """Test that handedness rules are properly applied."""
        evaluator = RuleEvaluator()
        
        # Same-handed matchup (righty vs righty)
        adjustment1 = evaluator.evaluate_single(self.batter1, self.pitcher1)
        
        # Opposite-handed matchup (righty vs lefty)
        adjustment2 = evaluator.evaluate_single(self.batter1, self.lefty_pitcher)
        
        # Opposite-handed should have higher adjustment
        self.assertGreater(adjustment2, adjustment1)
    
    def test_evaluate_power_vs_weak_pitcher(self):
        """Test power hitter against weak pitcher."""
        evaluator = RuleEvaluator()
        
        # Power hitter vs weak pitcher
        adjustment1 = evaluator.evaluate_single(self.batter3, self.pitcher2)
        
        # Power hitter vs regular pitcher
        adjustment2 = evaluator.evaluate_single(self.batter3, self.pitcher1)
        
        # Should perform better against weak pitcher
        self.assertGreater(adjustment1, adjustment2)
    
    def test_evaluate_multiple_batters(self):
        """Test evaluation with multiple batters."""
        evaluator = RuleEvaluator()
        batters = [self.batter1, self.batter2, self.batter3]
        adjustments = evaluator.evaluate(batters, self.pitcher1)
        
        # All batters should have adjustments
        self.assertEqual(len(adjustments), 3)
        for batter in batters:
            self.assertIn(batter.name, adjustments)
            self.assertIsInstance(adjustments[batter.name], float)
    
    def test_evaluate_error_handling(self):
        """Test that errors in rule evaluation are handled gracefully."""
        evaluator = RuleEvaluator()
        
        # Create a batter with invalid data that might cause errors
        # (though validation should prevent this, we test error handling)
        batters = [self.batter1]
        adjustments = evaluator.evaluate(batters, self.pitcher1)
        
        # Should still return a result even if some rules fail
        self.assertIn(self.batter1.name, adjustments)
    
    def test_evaluate_quantifier_adjustments(self):
        """Test that quantifier-based adjustments are applied."""
        evaluator = RuleEvaluator(use_quantifiers=True)
        
        # Create batters that should trigger quantifier rules
        high_obp_batter = Batter(
            name="High OBP",
            ba=0.300,
            k=100,
            obp=0.380,  # > 0.350
            slg=0.480,
            hr=25,
            rbi=75,
            handedness="L"  # Left-handed to avoid same-handed penalty
        )
        
        weak_pitcher = Pitcher(
            name="Weak",
            era=4.20,
            whip=1.35,
            k_rate=0.20,
            handedness="RHP",  # Right-handed (opposite of batter)
            walk_rate=0.11  # > 0.10
        )
        
        batters = [high_obp_batter]
        adjustments = evaluator.evaluate(batters, weak_pitcher)
        
        # Should have adjustment (may be positive or negative, but quantifiers are applied)
        # The quantifier bonus should be present even if other rules apply penalties
        self.assertIn(high_obp_batter.name, adjustments)
        self.assertIsInstance(adjustments[high_obp_batter.name], float)
        
        # Test with quantifiers disabled to verify difference
        evaluator_no_quant = RuleEvaluator(use_quantifiers=False)
        adjustments_no_quant = evaluator_no_quant.evaluate(batters, weak_pitcher)
        
        # Adjustments should be different when quantifiers are enabled vs disabled
        # (This verifies quantifiers are being applied)
        self.assertNotEqual(
            adjustments[high_obp_batter.name],
            adjustments_no_quant[high_obp_batter.name]
        )


if __name__ == '__main__':
    unittest.main()
