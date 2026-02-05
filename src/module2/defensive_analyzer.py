"""
Main analyzer for Module 2: Defensive Performance Analysis

Orchestrates the defensive performance analysis pipeline.
"""

from typing import Dict
from .input_parser import DefensiveStatsParser
from .knowledge_base import DefensiveKnowledgeBase
from .position_evaluator import PositionEvaluator
from .score_calculator import ScoreCalculator


def analyze_defensive_performance(input_file: str) -> Dict[str, Dict[str, float]]:
    """
    Analyze defensive performance for all players at their eligible positions.
    
    This is the main public API for Module 2.
    
    Args:
        input_file: Path to CSV or JSON file containing defensive statistics
        
    Returns:
        Dictionary mapping player names to position scores
        Format: {player_name: {position: score}}
        Scores are in the range 0-100
        
    Example:
        >>> scores = analyze_defensive_performance('defensive_stats.json')
        >>> print(scores['John Doe']['C'])
        85.5
    """
    # 1. Parse input file
    parser = DefensiveStatsParser()
    players_data = parser.parse(input_file)
    
    # 2. Initialize knowledge base and evaluators
    kb = DefensiveKnowledgeBase()
    position_evaluator = PositionEvaluator(kb)
    score_calculator = ScoreCalculator(kb)
    
    # 3. Evaluate all positions for all players
    facts_dict = position_evaluator.evaluate_all_players(players_data)
    
    # 4. Calculate scores
    scores = score_calculator.calculate_all_scores(facts_dict)
    
    # 5. Return results
    return scores
