"""
Score Calculator for Module 2: Defensive Performance Analysis

Calculates final defensive scores (0-100) for each player-position combination.
"""

# Changes made:
# - Stored the provided `DefensiveKnowledgeBase` instance on init.
# - Implemented `calculate_score` to prefer `knowledge_base.evaluate(fact)`;
#   if the knowledge base does not return a value, a local heuristic is
#   used as a fallback. The method normalizes/clamps intermediate values
#   and returns a value in the 0-100 range.
# - Implemented `calculate_all_scores` to process a nested facts mapping
#   and return numeric scores for each player-position.
# These changes enable conversion from `DefensiveFact` objects to final
# numeric scores used by the public analysis API.

from typing import Dict
from .knowledge_base import DefensiveKnowledgeBase, DefensiveFact


class ScoreCalculator:
    """Calculates position-specific defensive scores."""
    
    def __init__(self, knowledge_base: DefensiveKnowledgeBase):
        """
        Initialize score calculator.
        
        Args:
            knowledge_base: Knowledge base containing evaluation rules
        """
        # Store reference to the knowledge base for evaluation
        self.knowledge_base = knowledge_base
    
    def calculate_score(self, fact: DefensiveFact) -> float:
        """
        Calculate defensive score for a fact.
        
        Args:
            fact: DefensiveFact to evaluate
            
        Returns:
            Score from 0-100
        """
        if fact is None:
            raise ValueError("fact must be a DefensiveFact")

        # Try to use knowledge base evaluation first
        raw_score = None
        try:
            raw_score = self.knowledge_base.evaluate(fact)
        except Exception:
            raw_score = None

        # If KB didn't provide a score, compute using local heuristics
        if raw_score is None:
            # Ensure fielding_pct is in 0-1 range
            fp = float(fact.fielding_pct) if fact.fielding_pct is not None else 0.0
            fp = max(0.0, min(1.0, fp))

            total_chances = max(0, fact.putouts + fact.errors)

            if fact.is_catcher or fact.position == 'C':
                # normalize passed balls by total chances (fallback)
                normalized_passed_balls = (fact.passed_balls / total_chances) if total_chances > 0 else 0.0
                cs_pct = float(fact.caught_stealing_pct) if fact.caught_stealing_pct is not None else 0.0
                cs_pct = max(0.0, min(1.0, cs_pct))

                raw_score = (
                    (fp * 0.4) +
                    ((1.0 - normalized_passed_balls) * 0.3) +
                    (cs_pct * 0.3)
                )
            else:
                normalized_errors = (fact.errors / total_chances) if total_chances > 0 else 0.0
                normalized_putouts = (fact.putouts / total_chances) if total_chances > 0 else 0.0

                raw_score = (
                    (fp * 0.5) +
                    ((1.0 - normalized_errors) * 0.3) +
                    (normalized_putouts * 0.2)
                )

        # Clamp raw_score to 0-1 and convert to 0-100
        try:
            raw = float(raw_score)
        except Exception:
            raw = 0.0

        raw = max(0.0, min(1.0, raw))
        return raw * 100.0
    
    def calculate_all_scores(self, facts_dict: Dict[str, Dict[str, DefensiveFact]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate scores for all player-position combinations.
        
        Args:
            facts_dict: Dictionary mapping player_name to position facts
                       Format: {player_name: {position: DefensiveFact}}
            
        Returns:
            Dictionary mapping player_name to position scores
            Format: {player_name: {position: score}}
        """
        results: Dict[str, Dict[str, float]] = {}

        for player_name, pos_facts in facts_dict.items():
            player_scores: Dict[str, float] = {}
            for pos, fact in (pos_facts or {}).items():
                try:
                    score = self.calculate_score(fact)
                except Exception:
                    score = 0.0
                player_scores[pos] = score

            results[player_name] = player_scores

        return results
