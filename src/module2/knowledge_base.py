"""
Knowledge Base for Module 2: Defensive Performance Analysis

Contains facts and rules for evaluating defensive performance.
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
        # TODO: Set up rules dictionary
        pass
    
    def add_fact(self, player_data: Dict, position: str) -> DefensiveFact:
        """
        Create a defensive fact from player data.
        
        Args:
            player_data: Dictionary containing player statistics
            position: Position to evaluate
            
        Returns:
            DefensiveFact object
        """
        # TODO: Implement fact creation
        pass
    
    def evaluate(self, fact: DefensiveFact) -> float:
        """
        Evaluate a defensive fact using knowledge base rules.
        
        Args:
            fact: DefensiveFact to evaluate
            
        Returns:
            Raw score (before normalization to 0-100)
        """
        # TODO: Implement rule evaluation
        pass
    
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
        # TODO: Implement catcher evaluation rule
        pass
    
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
        # TODO: Implement general position evaluation rule
        pass
    
    def get_rule_description(self, position: str) -> str:
        """
        Get a human-readable description of the rule for a position.
        
        Args:
            position: Position to get rule description for
            
        Returns:
            String description of the rule
        """
        # TODO: Return rule description
        pass
