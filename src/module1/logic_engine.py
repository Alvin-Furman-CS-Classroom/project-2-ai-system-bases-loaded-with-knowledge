"""
First-Order Logic Engine for Module 1: Matchup Analysis

Implements universal (∀) and existential (∃) quantifiers for evaluating
first-order logic rules over collections of batters and pitchers.
"""

from typing import Callable, List, Any, Optional
from .models import Batter, Pitcher


class LogicEngine:
    """
    First-order logic engine for evaluating quantified rules.
    
    Supports universal quantification (∀) and existential quantification (∃)
    for applying rules to collections of batters and pitchers.
    """
    
    def __init__(self):
        """Initialize the logic engine."""
        pass
    
    def apply_universal_rule(
        self,
        collection: List[Any],
        rule: Callable[[Any], bool],
        condition: Optional[Callable[[Any], bool]] = None
    ) -> bool:
        """
        Apply a universal quantifier (∀) rule to a collection.
        
        Universal quantifier: "For all x in collection, if condition(x) then rule(x)"
        Returns True if the rule holds for ALL elements that satisfy the condition.
        If no condition is provided, applies to all elements.
        
        Args:
            collection: List of objects to evaluate (e.g., List[Batter])
            rule: Function that takes an element and returns True/False
                  Signature: rule(element) -> bool
            condition: Optional filter function that selects which elements to evaluate
                      Signature: condition(element) -> bool
                      If None, all elements are evaluated
        
        Returns:
            True if rule holds for all elements (that satisfy condition), False otherwise
            Returns True for empty collections (vacuous truth)
        
        Example:
            >>> engine = LogicEngine()
            >>> batters = [Batter(...), Batter(...)]
            >>> # Check if all left-handed batters have OBP > 0.350
            >>> result = engine.apply_universal_rule(
            ...     batters,
            ...     lambda b: b.obp > 0.350,
            ...     condition=lambda b: b.handedness == 'L'
            ... )
        """
        if collection is None:
            raise ValueError("collection cannot be None")
        
        if rule is None:
            raise ValueError("rule cannot be None")
        
        # Empty collection: universal quantifier is vacuously true
        if not collection:
            return True
        
        # Filter by condition if provided
        elements_to_evaluate = collection
        if condition is not None:
            elements_to_evaluate = [elem for elem in collection if condition(elem)]
            # If condition filters out all elements, return True (vacuous truth)
            if not elements_to_evaluate:
                return True
        
        # Check if rule holds for all elements
        for element in elements_to_evaluate:
            try:
                if not rule(element):
                    return False
            except Exception:
                # If rule evaluation fails, consider it False
                return False
        
        return True
    
    def check_existential_rule(
        self,
        collection: List[Any],
        rule: Callable[[Any], bool],
        condition: Optional[Callable[[Any], bool]] = None
    ) -> bool:
        """
        Check an existential quantifier (∃) rule on a collection.
        
        Existential quantifier: "There exists x in collection such that condition(x) and rule(x)"
        Returns True if the rule holds for AT LEAST ONE element that satisfies the condition.
        If no condition is provided, checks all elements.
        
        Args:
            collection: List of objects to evaluate (e.g., List[Batter])
            rule: Function that takes an element and returns True/False
                  Signature: rule(element) -> bool
            condition: Optional filter function that selects which elements to evaluate
                      Signature: condition(element) -> bool
                      If None, all elements are evaluated
        
        Returns:
            True if rule holds for at least one element (that satisfies condition), False otherwise
            Returns False for empty collections
        
        Example:
            >>> engine = LogicEngine()
            >>> batters = [Batter(...), Batter(...)]
            >>> # Check if there exists a batter with SLG > 0.500
            >>> result = engine.check_existential_rule(
            ...     batters,
            ...     lambda b: b.slg > 0.500
            ... )
        """
        if collection is None:
            raise ValueError("collection cannot be None")
        
        if rule is None:
            raise ValueError("rule cannot be None")
        
        # Empty collection: existential quantifier is false
        if not collection:
            return False
        
        # Filter by condition if provided
        elements_to_evaluate = collection
        if condition is not None:
            elements_to_evaluate = [elem for elem in collection if condition(elem)]
            # If condition filters out all elements, return False
            if not elements_to_evaluate:
                return False
        
        # Check if rule holds for at least one element
        for element in elements_to_evaluate:
            try:
                if rule(element):
                    return True
            except Exception:
                # If rule evaluation fails, continue checking other elements
                continue
        
        return False
    
    def apply_universal_rule_with_adjustment(
        self,
        collection: List[Any],
        rule: Callable[[Any], float],
        condition: Optional[Callable[[Any], bool]] = None,
        aggregation: str = "sum"
    ) -> float:
        """
        Apply a universal quantifier rule that returns adjustments for each element.
        
        Similar to apply_universal_rule, but the rule function returns a numeric
        adjustment value instead of a boolean. Aggregates adjustments across all
        elements that satisfy the condition.
        
        Args:
            collection: List of objects to evaluate (e.g., List[Batter])
            rule: Function that takes an element and returns a numeric adjustment
                  Signature: rule(element) -> float
            condition: Optional filter function that selects which elements to evaluate
                      Signature: condition(element) -> bool
            aggregation: How to aggregate adjustments: "sum", "average", "max", "min"
        
        Returns:
            Aggregated adjustment value
            Returns 0.0 for empty collections
        
        Example:
            >>> engine = LogicEngine()
            >>> batters = [Batter(...), Batter(...)]
            >>> # Sum adjustments for all left-handed batters
            >>> total = engine.apply_universal_rule_with_adjustment(
            ...     batters,
            ...     lambda b: -5.0 if b.obp < 0.300 else 0.0,
            ...     condition=lambda b: b.handedness == 'L'
            ... )
        """
        if collection is None:
            raise ValueError("collection cannot be None")
        
        if rule is None:
            raise ValueError("rule cannot be None")
        
        if aggregation not in ["sum", "average", "max", "min"]:
            raise ValueError(f"Invalid aggregation: {aggregation}. Must be 'sum', 'average', 'max', or 'min'")
        
        # Empty collection: return 0.0
        if not collection:
            return 0.0
        
        # Filter by condition if provided
        elements_to_evaluate = collection
        if condition is not None:
            elements_to_evaluate = [elem for elem in collection if condition(elem)]
            if not elements_to_evaluate:
                return 0.0
        
        # Collect adjustments
        adjustments = []
        for element in elements_to_evaluate:
            try:
                adjustment = rule(element)
                adjustments.append(float(adjustment))
            except Exception:
                # If rule evaluation fails, skip this element
                continue
        
        if not adjustments:
            return 0.0
        
        # Aggregate based on method
        if aggregation == "sum":
            return sum(adjustments)
        elif aggregation == "average":
            return sum(adjustments) / len(adjustments)
        elif aggregation == "max":
            return max(adjustments)
        elif aggregation == "min":
            return min(adjustments)
        else:
            return 0.0
    
    def evaluate_rule_for_element(
        self,
        element: Any,
        rule: Callable[[Any], Any]
    ) -> Any:
        """
        Evaluate a rule for a single element.
        
        This is a helper method for applying rules to individual elements
        (e.g., a single batter-pitcher matchup).
        
        Args:
            element: Single object to evaluate (e.g., Batter or tuple of (Batter, Pitcher))
            rule: Function that takes an element and returns a result
                  Signature: rule(element) -> Any
        
        Returns:
            Result of applying the rule to the element
            Returns None if rule evaluation fails
        
        Example:
            >>> engine = LogicEngine()
            >>> batter = Batter(...)
            >>> pitcher = Pitcher(...)
            >>> # Evaluate a rule for this specific matchup
            >>> adjustment = engine.evaluate_rule_for_element(
            ...     (batter, pitcher),
            ...     lambda pair: -10.0 if pair[0].handedness == pair[1].handedness[0] else 0.0
            ... )
        """
        if element is None:
            raise ValueError("element cannot be None")
        
        if rule is None:
            raise ValueError("rule cannot be None")
        
        try:
            return rule(element)
        except Exception:
            return None
