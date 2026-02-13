"""
Knowledge Base for Module 2: Defensive Performance Analysis

Contains facts and rules for evaluating defensive performance.
Uses propositional logic rules to evaluate defensive performance based on
position-specific heuristics (catcher vs. general positions).
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
        Rule for evaluating catcher defensive performance.
        
        Knowledge Base Rule:
        IF position == "C" THEN
            score = (fielding_pct * 0.4) + 
                    ((1 - normalized_passed_balls) * 0.3) + 
                    (caught_stealing_pct * 0.3)
        
        Args:
            fact: DefensiveFact for a catcher
            
        Returns:
            Raw score (0-1 range)
        """
        fp = self._normalize_percentage(fact.fielding_pct)
        total_chances = self._calculate_total_chances(fact.putouts, fact.errors)
        normalized_passed_balls = (fact.passed_balls / total_chances) if total_chances > 0 else 0.0
        cs_pct = self._normalize_percentage(fact.caught_stealing_pct)

        score = (
            (fp * 0.4) +
            ((1.0 - normalized_passed_balls) * 0.3) +
            (cs_pct * 0.3)
        )

        return max(0.0, min(1.0, score))
    
    def _general_position_rule(self, fact: DefensiveFact) -> float:
        """
        Rule for evaluating general position defensive performance.
        
        Knowledge Base Rule:
        IF position != "C" THEN
            score = (fielding_pct * 0.5) + 
                    ((1 - normalized_errors) * 0.3) + 
                    (normalized_putouts * 0.2)
        
        Args:
            fact: DefensiveFact for a non-catcher position
            
        Returns:
            Raw score (0-1 range)
        """
        fp = self._normalize_percentage(fact.fielding_pct)
        total_chances = self._calculate_total_chances(fact.putouts, fact.errors)
        normalized_errors = (fact.errors / total_chances) if total_chances > 0 else 0.0
        normalized_putouts = (fact.putouts / total_chances) if total_chances > 0 else 0.0

        score = (
            (fp * 0.5) +
            ((1.0 - normalized_errors) * 0.3) +
            (normalized_putouts * 0.2)
        )

        return max(0.0, min(1.0, score))
    
    def get_rule_description(self, position: str) -> str:
        """
        Get a human-readable description of the rule for a position.
        
        Args:
            position: Position to get rule description for
            
        Returns:
            String description of the rule
        """
        if position == 'C':
            return (
                'Catcher rule: 0.4*fielding_pct + 0.3*(1-normalized_passed_balls) '
                '+ 0.3*caught_stealing_pct'
            )

        return (
            'General rule: 0.5*fielding_pct + 0.3*(1-normalized_errors) '
            '+ 0.2*normalized_putouts'
        )
