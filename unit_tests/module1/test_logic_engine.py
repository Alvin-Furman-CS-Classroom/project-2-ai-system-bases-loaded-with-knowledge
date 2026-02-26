"""
Unit tests for Module 1 logic engine (first-order logic quantifiers).
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.logic_engine import LogicEngine
from module1.models import Batter, Pitcher


class TestLogicEngine(unittest.TestCase):
    """Test cases for LogicEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = LogicEngine()
        
        # Create test batters
        self.batter1 = Batter(
            name="Player 1",
            ba=0.300,
            k=100,
            obp=0.400,
            slg=0.500,
            hr=30,
            rbi=80,
            handedness="R"
        )
        
        self.batter2 = Batter(
            name="Player 2",
            ba=0.280,
            k=120,
            obp=0.350,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="L"
        )
        
        self.batter3 = Batter(
            name="Player 3",
            ba=0.250,
            k=150,
            obp=0.300,
            slg=0.400,
            hr=15,
            rbi=50,
            handedness="R"
        )
    
    def test_apply_universal_rule_all_true(self):
        """Test universal quantifier when all elements satisfy the rule."""
        batters = [self.batter1, self.batter2]
        result = self.engine.apply_universal_rule(
            batters,
            lambda b: b.ba > 0.250
        )
        self.assertTrue(result)
    
    def test_apply_universal_rule_some_false(self):
        """Test universal quantifier when some elements don't satisfy the rule."""
        batters = [self.batter1, self.batter2, self.batter3]
        result = self.engine.apply_universal_rule(
            batters,
            lambda b: b.obp > 0.350
        )
        self.assertFalse(result)  # batter3 has OBP 0.300
    
    def test_apply_universal_rule_with_condition(self):
        """Test universal quantifier with a condition filter."""
        batters = [self.batter1, self.batter2, self.batter3]
        # Check if all left-handed batters have OBP > 0.340
        result = self.engine.apply_universal_rule(
            batters,
            lambda b: b.obp > 0.340,
            condition=lambda b: b.handedness == 'L'
        )
        self.assertTrue(result)  # Only batter2 is left-handed, OBP 0.350 > 0.340
    
    def test_apply_universal_rule_empty_collection(self):
        """Test universal quantifier with empty collection (vacuous truth)."""
        result = self.engine.apply_universal_rule(
            [],
            lambda b: False  # Even if rule is always False
        )
        self.assertTrue(result)  # Vacuous truth
    
    def test_apply_universal_rule_condition_filters_all(self):
        """Test universal quantifier when condition filters out all elements."""
        batters = [self.batter1, self.batter2]
        result = self.engine.apply_universal_rule(
            batters,
            lambda b: False,
            condition=lambda b: b.name == "NonExistent"
        )
        self.assertTrue(result)  # Vacuous truth when condition filters all
    
    def test_apply_universal_rule_error_handling(self):
        """Test universal quantifier handles rule errors gracefully."""
        batters = [self.batter1, self.batter2]
        # Rule that raises an exception
        def failing_rule(b):
            raise ValueError("Test error")
        
        result = self.engine.apply_universal_rule(batters, failing_rule)
        self.assertFalse(result)
    
    def test_check_existential_rule_exists(self):
        """Test existential quantifier when at least one element satisfies the rule."""
        batters = [self.batter1, self.batter2, self.batter3]
        result = self.engine.check_existential_rule(
            batters,
            lambda b: b.obp > 0.350
        )
        self.assertTrue(result)  # batter1 and batter2 have OBP > 0.350
    
    def test_check_existential_rule_none_exist(self):
        """Test existential quantifier when no elements satisfy the rule."""
        batters = [self.batter1, self.batter2, self.batter3]
        result = self.engine.check_existential_rule(
            batters,
            lambda b: b.obp > 0.500
        )
        self.assertFalse(result)  # No batter has OBP > 0.500
    
    def test_check_existential_rule_with_condition(self):
        """Test existential quantifier with a condition filter."""
        batters = [self.batter1, self.batter2, self.batter3]
        # Check if there exists a left-handed batter with OBP > 0.340
        result = self.engine.check_existential_rule(
            batters,
            lambda b: b.obp > 0.340,
            condition=lambda b: b.handedness == 'L'
        )
        self.assertTrue(result)  # batter2 is left-handed with OBP 0.350
    
    def test_check_existential_rule_empty_collection(self):
        """Test existential quantifier with empty collection."""
        result = self.engine.check_existential_rule(
            [],
            lambda b: True
        )
        self.assertFalse(result)  # False for empty collection
    
    def test_check_existential_rule_error_handling(self):
        """Test existential quantifier handles rule errors gracefully."""
        batters = [self.batter1, self.batter2]
        # Rule that raises an exception
        def failing_rule(b):
            raise ValueError("Test error")
        
        result = self.engine.check_existential_rule(batters, failing_rule)
        self.assertFalse(result)
    
    def test_apply_universal_rule_with_adjustment_sum(self):
        """Test universal quantifier with adjustments (sum aggregation)."""
        batters = [self.batter1, self.batter2]
        result = self.engine.apply_universal_rule_with_adjustment(
            batters,
            lambda b: 5.0 if b.obp > 0.350 else 0.0,
            aggregation="sum"
        )
        self.assertEqual(result, 5.0)  # Only batter1 has OBP > 0.350
    
    def test_apply_universal_rule_with_adjustment_average(self):
        """Test universal quantifier with adjustments (average aggregation)."""
        batters = [self.batter1, self.batter2]
        result = self.engine.apply_universal_rule_with_adjustment(
            batters,
            lambda b: 10.0,  # All get 10.0
            aggregation="average"
        )
        self.assertEqual(result, 10.0)
    
    def test_apply_universal_rule_with_adjustment_max(self):
        """Test universal quantifier with adjustments (max aggregation)."""
        batters = [self.batter1, self.batter2, self.batter3]
        result = self.engine.apply_universal_rule_with_adjustment(
            batters,
            lambda b: b.obp * 100,  # Different values
            aggregation="max"
        )
        self.assertEqual(result, 40.0)  # batter1 has highest OBP (0.400)
    
    def test_apply_universal_rule_with_adjustment_min(self):
        """Test universal quantifier with adjustments (min aggregation)."""
        batters = [self.batter1, self.batter2, self.batter3]
        result = self.engine.apply_universal_rule_with_adjustment(
            batters,
            lambda b: b.obp * 100,
            aggregation="min"
        )
        self.assertEqual(result, 30.0)  # batter3 has lowest OBP (0.300)
    
    def test_apply_universal_rule_with_adjustment_empty(self):
        """Test universal quantifier with adjustments on empty collection."""
        result = self.engine.apply_universal_rule_with_adjustment(
            [],
            lambda b: 5.0,
            aggregation="sum"
        )
        self.assertEqual(result, 0.0)
    
    def test_apply_universal_rule_with_adjustment_invalid_aggregation(self):
        """Test universal quantifier with invalid aggregation method."""
        with self.assertRaises(ValueError):
            self.engine.apply_universal_rule_with_adjustment(
                [self.batter1],
                lambda b: 5.0,
                aggregation="invalid"
            )
    
    def test_evaluate_rule_for_element(self):
        """Test evaluating a rule for a single element."""
        result = self.engine.evaluate_rule_for_element(
            self.batter1,
            lambda b: b.obp * 100
        )
        self.assertEqual(result, 40.0)
    
    def test_evaluate_rule_for_element_error(self):
        """Test evaluating a rule that raises an error."""
        result = self.engine.evaluate_rule_for_element(
            self.batter1,
            lambda b: 1 / 0  # Division by zero
        )
        self.assertIsNone(result)
    
    def test_universal_rule_none_collection(self):
        """Test universal quantifier with None collection."""
        with self.assertRaises(ValueError):
            self.engine.apply_universal_rule(None, lambda b: True)
    
    def test_universal_rule_none_rule(self):
        """Test universal quantifier with None rule."""
        with self.assertRaises(ValueError):
            self.engine.apply_universal_rule([self.batter1], None)
    
    def test_existential_rule_none_collection(self):
        """Test existential quantifier with None collection."""
        with self.assertRaises(ValueError):
            self.engine.check_existential_rule(None, lambda b: True)
    
    def test_existential_rule_none_rule(self):
        """Test existential quantifier with None rule."""
        with self.assertRaises(ValueError):
            self.engine.check_existential_rule([self.batter1], None)
    
    def test_evaluate_rule_none_element(self):
        """Test evaluating rule with None element."""
        with self.assertRaises(ValueError):
            self.engine.evaluate_rule_for_element(None, lambda b: True)
    
    def test_evaluate_rule_none_rule(self):
        """Test evaluating None rule."""
        with self.assertRaises(ValueError):
            self.engine.evaluate_rule_for_element(self.batter1, None)


if __name__ == '__main__':
    unittest.main()
