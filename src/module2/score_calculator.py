"""
Score Calculator for Module 2: Defensive Performance Analysis

Calculates final defensive scores (0-100) for each player-position combination.
Converts knowledge base evaluations (0-1 range) to final scores (0-100 range)
for use by downstream modules.
"""

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

        # If KB didn't provide a score, compute using fallback heuristics
        if raw_score is None:
            raw_score = self._fallback_score(fact)

        # Clamp raw_score to 0-1 and convert to 0-100
        try:
            raw = float(raw_score)
        except Exception:
            raw = 0.0

        raw = max(0.0, min(1.0, raw))
        return raw * 100.0
    
    def _normalize_percentage(self, value: float) -> float:
        """
        Normalize a percentage value to 0-1 range.
        
        Accepts values in either 0-1 or 0-100 format and normalizes to 0-1.
        
        Args:
            value: Percentage value (may be 0-1 or 0-100)
            
        Returns:
            Normalized percentage in 0-1 range
        """
        normalized = float(value) if value is not None else 0.0
        if normalized > 1.0:
            normalized = normalized / 100.0
        return max(0.0, min(1.0, normalized))
    
    def _calculate_total_chances(self, putouts: int, errors: int) -> int:
        """Calculate total defensive chances from putouts and errors."""
        return max(0, putouts + errors)
    
    def _fallback_score(self, fact: DefensiveFact) -> float:
        """
        Calculate fallback score when knowledge base evaluation fails.
        
        Uses the same boolean logic rules as the knowledge base as a safety net.
        
        Args:
            fact: DefensiveFact to evaluate
            
        Returns:
            Raw score (0-1 range) based on boolean rule evaluation
        """
        fp = self._normalize_percentage(fact.fielding_pct)
        total_chances = self._calculate_total_chances(fact.putouts, fact.errors)

        if fact.is_catcher or fact.position == 'C':
            # Catcher boolean rules
            normalized_passed_balls = (fact.passed_balls / total_chances) if total_chances > 0 else 0.0
            cs_pct = self._normalize_percentage(fact.caught_stealing_pct)
            
            true_count = sum([
                fp >= 0.95,                          # R1: excellent fielding
                normalized_passed_balls <= 0.01,     # R2: low passed balls
                cs_pct >= 0.25,                      # R3: good caught stealing
                fact.errors <= 5,                    # R4: few errors
                fact.putouts >= 100                   # R5: adequate putouts
            ])
            return true_count / 5.0
        else:
            # General position boolean rules
            normalized_errors = (fact.errors / total_chances) if total_chances > 0 else 0.0
            normalized_putouts = (fact.putouts / total_chances) if total_chances > 0 else 0.0
            
            true_count = sum([
                fp >= 0.95,                          # R1: excellent fielding
                normalized_errors <= 0.05,            # R2: low error rate
                normalized_putouts >= 0.80,          # R3: high putout rate
                fact.errors <= 10,                    # R4: few errors
                fact.putouts >= 50                    # R5: adequate putouts
            ])
            return true_count / 5.0
    
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
