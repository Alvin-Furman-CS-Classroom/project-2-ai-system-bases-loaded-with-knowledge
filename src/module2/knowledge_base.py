"""
Knowledge Base for Module 2: Defensive Performance Analysis

Contains facts and rules for evaluating defensive performance.
Uses boolean propositional logic rules (True/False conditions) to evaluate
defensive performance based on position-specific heuristics (catcher vs. general positions).
Each rule evaluates to True or False, and the final score is the proportion of True rules.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class DefensiveFact:
    """Represents a fact about a player's defensive statistics."""
    player_name: str
    position: str
    fielding_pct: float
    errors: int
    putouts: int
    passed_balls: int = 0
    caught_stealing_pct: float = 0.0
    is_catcher: bool = False


class DefensiveKnowledgeBase:
    """
    Knowledge base containing rules for defensive evaluation.
    
    Uses propositional logic rules to evaluate defensive performance
    based on position-specific heuristics.
    """
    
    def __init__(self):
        """Initialize the knowledge base."""
        # Map positions to rule callables; default to general rule
        self.rules = {
            'C': self._catcher_rule,
            'DEFAULT': self._general_position_rule,
        }
    
    def add_fact(self, player_data: Dict, position: str) -> DefensiveFact:
        """
        Create a defensive fact from player data.
        
        Args:
            player_data: Dictionary containing player statistics
            position: Position to evaluate
            
        Returns:
            DefensiveFact object
        """
        # Safely extract fields with defaults
        name = player_data.get('player_name') or player_data.get('name') or 'Unknown'

        # Accept fielding pct as 0-1 or 0-100; normalize later in rules
        fielding_pct = player_data.get('fielding_pct', 0.0)

        try:
            fielding_pct = float(fielding_pct)
        except Exception:
            fielding_pct = 0.0

        errors = int(player_data.get('errors', 0) or 0)
        putouts = int(player_data.get('putouts', 0) or 0)
        passed_balls = int(player_data.get('passed_balls', 0) or 0)

        caught_stealing_pct = player_data.get('caught_stealing_pct', 0.0) or 0.0
        try:
            caught_stealing_pct = float(caught_stealing_pct)
        except Exception:
            caught_stealing_pct = 0.0

        is_catcher = (position == 'C')

        fact = DefensiveFact(
            player_name=name,
            position=position,
            fielding_pct=fielding_pct,
            errors=errors,
            putouts=putouts,
            passed_balls=passed_balls,
            caught_stealing_pct=caught_stealing_pct,
            is_catcher=is_catcher,
        )

        return fact
    
    def evaluate(self, fact: DefensiveFact) -> float:
        """
        Evaluate a defensive fact using knowledge base rules.
        
        Args:
            fact: DefensiveFact to evaluate
            
        Returns:
            Raw score (before normalization to 0-100)
        """
        if fact is None:
            return 0.0

        # Choose rule based on position
        rule = self.rules.get(fact.position, self.rules.get('DEFAULT'))

        try:
            score = rule(fact)
        except Exception:
            score = 0.0

        # Clamp to 0-1
        try:
            s = float(score)
        except Exception:
            s = 0.0

        s = max(0.0, min(1.0, s))
        return s
    
    def _normalize_percentage(self, value: float) -> float:
        """
        Normalize a percentage value to 0-1 range.
        
        Accepts values in either 0-1 or 0-100 format and normalizes to 0-1.
        
        Args:
            value: Percentage value (may be 0-1 or 0-100)
            
        Returns:
            Normalized percentage in 0-1 range
        """
        normalized = float(value or 0.0)
        if normalized > 1.0:
            normalized = normalized / 100.0
        return max(0.0, min(1.0, normalized))
    
    def _calculate_total_chances(self, putouts: int, errors: int) -> int:
        """Calculate total defensive chances from putouts and errors."""
        return max(0, putouts + errors)
    
    def _catcher_rule(self, fact: DefensiveFact) -> float:
        """
        Rule for evaluating catcher defensive performance using boolean logic.
        
        Knowledge Base Rules (all must be evaluated as True/False):
        IF position == "C" THEN
            R1: fielding_pct >= 0.95
            R2: normalized_passed_balls <= 0.01
            R3: caught_stealing_pct >= 0.25
            R4: errors <= 5
            R5: putouts >= 100
        
        Score = (number of True rules) / (total rules)
        
        Args:
            fact: DefensiveFact for a catcher
            
        Returns:
            Raw score (0-1 range) based on boolean rule evaluation
        """
        fp = self._normalize_percentage(fact.fielding_pct)
        total_chances = self._calculate_total_chances(fact.putouts, fact.errors)
        normalized_passed_balls = (fact.passed_balls / total_chances) if total_chances > 0 else 0.0
        cs_pct = self._normalize_percentage(fact.caught_stealing_pct)

        # Boolean rules - each evaluates to True or False
        r1_excellent_fielding = fp >= 0.95
        r2_low_passed_balls = normalized_passed_balls <= 0.01
        r3_good_caught_stealing = cs_pct >= 0.25
        r4_few_errors = fact.errors <= 5
        r5_adequate_putouts = fact.putouts >= 100

        # Count how many rules are True
        true_count = sum([
            r1_excellent_fielding,
            r2_low_passed_balls,
            r3_good_caught_stealing,
            r4_few_errors,
            r5_adequate_putouts
        ])

        # Score = proportion of rules that are True
        total_rules = 5
        score = true_count / total_rules

        return max(0.0, min(1.0, score))
    
    def _general_position_rule(self, fact: DefensiveFact) -> float:
        """
        Rule for evaluating general position defensive performance using boolean logic.
        
        Knowledge Base Rules (all must be evaluated as True/False):
        IF position != "C" THEN
            R1: fielding_pct >= 0.95
            R2: normalized_errors <= 0.05
            R3: normalized_putouts >= 0.80
            R4: errors <= 10
            R5: putouts >= 50
        
        Score = (number of True rules) / (total rules)
        
        Args:
            fact: DefensiveFact for a non-catcher position
            
        Returns:
            Raw score (0-1 range) based on boolean rule evaluation
        """
        fp = self._normalize_percentage(fact.fielding_pct)
        total_chances = self._calculate_total_chances(fact.putouts, fact.errors)
        normalized_errors = (fact.errors / total_chances) if total_chances > 0 else 0.0
        normalized_putouts = (fact.putouts / total_chances) if total_chances > 0 else 0.0

        # Boolean rules - each evaluates to True or False
        r1_excellent_fielding = fp >= 0.95
        r2_low_error_rate = normalized_errors <= 0.05
        r3_high_putout_rate = normalized_putouts >= 0.80
        r4_few_errors = fact.errors <= 10
        r5_adequate_putouts = fact.putouts >= 50

        # Count how many rules are True
        true_count = sum([
            r1_excellent_fielding,
            r2_low_error_rate,
            r3_high_putout_rate,
            r4_few_errors,
            r5_adequate_putouts
        ])

        # Score = proportion of rules that are True
        total_rules = 5
        score = true_count / total_rules

        return max(0.0, min(1.0, score))
    
    def get_rule_description(self, position: str) -> str:
        """
        Get a human-readable description of the boolean rules for a position.
        
        Args:
            position: Position to get rule description for
            
        Returns:
            String description of the boolean rules
        """
        if position == 'C':
            return (
                'Catcher boolean rules: '
                'R1: fielding_pct >= 0.95 AND '
                'R2: normalized_passed_balls <= 0.01 AND '
                'R3: caught_stealing_pct >= 0.25 AND '
                'R4: errors <= 5 AND '
                'R5: putouts >= 100. '
                'Score = (True rules) / 5'
            )

        return (
            'General position boolean rules: '
            'R1: fielding_pct >= 0.95 AND '
            'R2: normalized_errors <= 0.05 AND '
            'R3: normalized_putouts >= 0.80 AND '
            'R4: errors <= 10 AND '
            'R5: putouts >= 50. '
            'Score = (True rules) / 5'
        )
