"""
Rule Evaluator for Module 1: Matchup Analysis

Combines the first-order logic engine with matchup rules to evaluate
all batters against a pitcher and return score adjustments.
"""

from typing import Dict, List, Optional
from .models import Batter, Pitcher
from .logic_engine import LogicEngine
from .matchup_rules import get_all_rules, evaluate_single_matchup


class RuleEvaluator:
    """
    Evaluates first-order logic rules for all batter-pitcher matchups.
    
    Uses the logic engine to apply universal and existential quantifiers
    across collections of batters, then applies individual matchup rules
    to calculate score adjustments for each batter.
    """
    
    def __init__(self, use_quantifiers: bool = True):
        """
        Initialize the rule evaluator.
        
        Args:
            use_quantifiers: If True, applies first-order logic quantifiers
                           (universal and existential) before individual rules.
                           If False, only applies individual matchup rules.
        """
        self.logic_engine = LogicEngine()
        self.use_quantifiers = use_quantifiers
        self.rules = get_all_rules()
    
    def evaluate(self, batters: List[Batter], pitcher: Pitcher) -> Dict[str, float]:
        """
        Evaluate all rules for all batters against a pitcher.
        
        This is the main method that:
        1. Applies first-order logic quantifiers (if enabled)
        2. Applies individual matchup rules for each batter
        3. Returns total adjustments for each batter
        
        Args:
            batters: List of Batter objects to evaluate
            pitcher: Pitcher object to compare against
        
        Returns:
            Dictionary mapping batter names to total score adjustments
            Format: {batter_name: total_adjustment}
            Adjustments can be positive (bonus) or negative (penalty)
        
        Example:
            >>> evaluator = RuleEvaluator()
            >>> batters = [Batter(...), Batter(...)]
            >>> pitcher = Pitcher(...)
            >>> adjustments = evaluator.evaluate(batters, pitcher)
            >>> print(adjustments)
            {'Mike Trout': 12.5, 'Freddie Freeman': -8.0}
        """
        if batters is None:
            raise ValueError("batters cannot be None")
        
        if pitcher is None:
            raise ValueError("pitcher cannot be None")
        
        if not batters:
            return {}
        
        adjustments: Dict[str, float] = {}
        
        # Apply first-order logic quantifiers if enabled
        if self.use_quantifiers:
            quantifier_adjustments = self._apply_quantifiers(batters, pitcher)
        else:
            quantifier_adjustments = {}
        
        # Apply individual matchup rules for each batter
        for batter in batters:
            try:
                # Get quantifier-based adjustment (if any)
                quantifier_adj = quantifier_adjustments.get(batter.name, 0.0)
                
                # Get individual rule adjustments
                individual_adj = evaluate_single_matchup(batter, pitcher)
                
                # Total adjustment
                total_adjustment = quantifier_adj + individual_adj
                adjustments[batter.name] = total_adjustment
                
            except Exception:
                # If evaluation fails for a batter, assign 0.0 adjustment
                adjustments[batter.name] = 0.0
        
        return adjustments
    
    def evaluate_single(self, batter: Batter, pitcher: Pitcher) -> float:
        """
        Evaluate rules for a single batter-pitcher matchup.
        
        This method is useful when evaluating one batter at a time,
        such as in the matrix analysis functions.
        
        Args:
            batter: Single Batter object
            pitcher: Pitcher object
        
        Returns:
            Total score adjustment for this matchup
        """
        if batter is None:
            raise ValueError("batter cannot be None")
        
        if pitcher is None:
            raise ValueError("pitcher cannot be None")
        
        # Apply individual matchup rules
        adjustment = evaluate_single_matchup(batter, pitcher)
        
        # Apply quantifier-based adjustments if enabled
        if self.use_quantifiers:
            quantifier_adj = self._apply_quantifiers_for_single(batter, pitcher)
            adjustment += quantifier_adj
        
        return adjustment
    
    def _apply_quantifiers(self, batters: List[Batter], pitcher: Pitcher) -> Dict[str, float]:
        """
        Apply first-order logic quantifiers to generate adjustments.
        
        Uses universal (∀) and existential (∃) quantifiers to evaluate
        rules across the collection of batters.
        
        Args:
            batters: List of Batter objects
            pitcher: Pitcher object
        
        Returns:
            Dictionary mapping batter names to quantifier-based adjustments
        """
        adjustments: Dict[str, float] = {}
        
        # Example: Universal quantifier rule
        # "For all batters, if batter OBP > 0.350 and pitcher walk rate > 0.10, then increase score"
        universal_rule_holds = self.logic_engine.apply_universal_rule(
            batters,
            lambda b: b.obp > 0.350,
            condition=lambda b: pitcher.walk_rate > 0.10
        )
        
        if universal_rule_holds:
            # Apply bonus to all batters that satisfy the condition
            for batter in batters:
                if pitcher.walk_rate > 0.10 and batter.obp > 0.350:
                    adjustments[batter.name] = adjustments.get(batter.name, 0.0) + 3.0
        
        # Example: Universal quantifier with condition
        # "For all left-handed batters, if the pitcher is left-handed, then reduce performance score"
        left_handed_batters = [b for b in batters if b.is_left_handed()]
        if left_handed_batters and pitcher.is_left_handed():
            universal_penalty_holds = self.logic_engine.apply_universal_rule(
                left_handed_batters,
                lambda b: True  # All left-handed batters are affected
            )
            if universal_penalty_holds:
                for batter in left_handed_batters:
                    adjustments[batter.name] = adjustments.get(batter.name, 0.0) - 5.0
        
        # Example: Existential quantifier rule
        # "There exists a batter such that their slugging percentage > 0.500 and pitcher ERA > 4.00"
        existential_rule_holds = self.logic_engine.check_existential_rule(
            batters,
            lambda b: b.slg > 0.500,
            condition=lambda b: pitcher.era > 4.00
        )
        
        if existential_rule_holds:
            # Apply bonus to all power hitters when facing weak pitcher
            for batter in batters:
                if batter.slg > 0.500 and pitcher.era > 4.00:
                    adjustments[batter.name] = adjustments.get(batter.name, 0.0) + 4.0
        
        # Example: Universal quantifier for elite batters
        # "For all elite batters (BA > 0.300, OBP > 0.400, SLG > 0.500), apply bonus"
        elite_batters = [b for b in batters if b.ba > 0.300 and b.obp > 0.400 and b.slg > 0.500]
        if elite_batters:
            elite_rule_holds = self.logic_engine.apply_universal_rule(
                elite_batters,
                lambda b: True
            )
            if elite_rule_holds:
                for batter in elite_batters:
                    adjustments[batter.name] = adjustments.get(batter.name, 0.0) + 2.0
        
        return adjustments
    
    def _apply_quantifiers_for_single(self, batter: Batter, pitcher: Pitcher) -> float:
        """
        Apply quantifier-based adjustments for a single batter.
        
        This is a simplified version for single batter evaluation.
        Some quantifier rules require multiple batters to evaluate,
        so this method applies only the rules that make sense for a single batter.
        
        Args:
            batter: Single Batter object
            pitcher: Pitcher object
        
        Returns:
            Quantifier-based adjustment (usually 0.0 for single batter)
        """
        # Most quantifier rules require multiple batters to evaluate
        # For single batter evaluation, we primarily rely on individual rules
        # But we can still apply some logic
        
        adjustment = 0.0
        
        # Example: Check if this batter satisfies universal conditions
        if batter.obp > 0.350 and pitcher.walk_rate > 0.10:
            # This batter would contribute to a universal rule
            adjustment += 1.0
        
        if batter.slg > 0.500 and pitcher.era > 4.00:
            # This batter would satisfy an existential rule
            adjustment += 2.0
        
        return adjustment
    
    def get_rule_count(self) -> int:
        """
        Get the number of rules being used.
        
        Returns:
            Number of matchup rules
        """
        return len(self.rules)
    
    def set_use_quantifiers(self, use: bool):
        """
        Enable or disable first-order logic quantifiers.
        
        Args:
            use: If True, quantifiers are applied; if False, only individual rules
        """
        self.use_quantifiers = use
