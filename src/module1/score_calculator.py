"""
Score Calculator for Module 1: Matchup Analysis

Calculates performance scores (0-100) for each batter based on their statistics
and rule-based adjustments from the first-order logic engine.
"""

from typing import Dict, List, Optional
from .models import Batter


class ScoreCalculator:
    """Calculates matchup performance scores for batters."""
    
    # Weighting factors for base score calculation
    BA_WEIGHT = 0.30   # Batting average weight
    OBP_WEIGHT = 0.40  # On-base percentage weight (most important)
    SLG_WEIGHT = 0.30  # Slugging percentage weight
    
    def __init__(self):
        """Initialize the score calculator."""
        pass
    
    def calculate_base_score(self, batter: Batter) -> float:
        """
        Calculate base performance score from batter statistics.
        
        Base score is calculated using a weighted combination of:
        - Batting average (BA): 30%
        - On-base percentage (OBP): 40%
        - Slugging percentage (SLG): 30%
        
        The base score is normalized to 0-100 range, where:
        - 0.000 BA/OBP/SLG = 0 points
        - 1.000 BA/OBP/SLG = 100 points
        
        Args:
            batter: Batter object with statistics
            
        Returns:
            Base score from 0-100 (before rule adjustments)
        """
        if batter is None:
            raise ValueError("batter must be a Batter object")
        
        # Calculate weighted average of key offensive stats
        # Each stat is already in 0-1 range, so we can directly weight them
        weighted_score = (
            batter.ba * self.BA_WEIGHT +
            batter.obp * self.OBP_WEIGHT +
            batter.slg * self.SLG_WEIGHT
        )
        
        # Convert to 0-100 scale
        base_score = weighted_score * 100.0
        
        # Ensure score is in valid range (should already be, but clamp for safety)
        return max(0.0, min(100.0, base_score))
    
    def apply_adjustments(self, base_score: float, adjustment: float) -> float:
        """
        Apply rule-based adjustments to base score.
        
        Adjustments can be positive (bonus) or negative (penalty).
        The adjusted score is clamped to 0-100 range.
        
        Args:
            base_score: Base score from calculate_base_score (0-100)
            adjustment: Score adjustment from rule evaluator (can be negative)
            
        Returns:
            Adjusted score from 0-100
        """
        if base_score is None:
            raise ValueError("base_score must be a number")
        
        # Convert adjustment to float, defaulting to 0 if invalid
        try:
            adj = float(adjustment) if adjustment is not None else 0.0
        except (TypeError, ValueError):
            adj = 0.0
        
        # Apply adjustment
        adjusted_score = base_score + adj
        
        # Clamp to 0-100 range
        return max(0.0, min(100.0, adjusted_score))
    
    def calculate_final_score(
        self,
        batter: Batter,
        adjustment: Optional[float] = None
    ) -> float:
        """
        Calculate final performance score for a batter.
        
        This is a convenience method that combines base score calculation
        and adjustment application in one step.
        
        Args:
            batter: Batter object with statistics
            adjustment: Optional score adjustment from rule evaluator
            
        Returns:
            Final score from 0-100
        """
        base_score = self.calculate_base_score(batter)
        return self.apply_adjustments(base_score, adjustment)
    
    def calculate_all_scores(
        self,
        batters: List[Batter],
        adjustments: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Calculate final scores for all batters.
        
        Args:
            batters: List of Batter objects
            adjustments: Optional dictionary mapping batter names to adjustments
                        Format: {batter_name: adjustment_value}
                        If None, no adjustments are applied
                        
        Returns:
            Dictionary mapping batter names to final scores (0-100)
            Format: {batter_name: score}
        """
        if batters is None:
            raise ValueError("batters must be a list")
        
        if adjustments is None:
            adjustments = {}
        
        results: Dict[str, float] = {}
        
        for batter in batters:
            try:
                # Get adjustment for this batter (default to 0 if not found)
                adjustment = adjustments.get(batter.name, 0.0)
                
                # Calculate final score
                final_score = self.calculate_final_score(batter, adjustment)
                
                results[batter.name] = final_score
            except Exception as e:
                # If calculation fails for a batter, assign score of 0
                # This ensures the function always returns a complete result
                results[batter.name] = 0.0
        
        return results
    
    def normalize_score(self, score: float, min_score: float = 0.0, max_score: float = 100.0) -> float:
        """
        Normalize a score to 0-100 range.
        
        This is a utility method for handling edge cases where scores
        might be outside the expected range.
        
        Args:
            score: Score to normalize
            min_score: Minimum allowed score (default: 0.0)
            max_score: Maximum allowed score (default: 100.0)
            
        Returns:
            Normalized score clamped to [min_score, max_score]
        """
        try:
            normalized = float(score)
        except (TypeError, ValueError):
            return 0.0
        
        return max(min_score, min(max_score, normalized))
