"""
Main analyzer for Module 2: Defensive Performance Analysis

Orchestrates the defensive performance analysis pipeline.
"""

from typing import Dict
from .input_parser import DefensiveStatsParser
from .knowledge_base import DefensiveKnowledgeBase
from .position_evaluator import PositionEvaluator
from .score_calculator import ScoreCalculator


def analyze_defensive_performance(
    input_file: str,
    predict_all_positions: bool = True,
) -> Dict[str, Dict[str, float]]:
    """
    Analyze defensive performance for all players.

    By default, predicts performance at all positions (including unplayed ones).
    Set predict_all_positions=False to only evaluate positions players have played.

    This is the main public API for Module 2.

    Args:
        input_file: Path to CSV or JSON file containing defensive statistics
        predict_all_positions: If True (default), predict scores for unplayed
            positions using similar positions. If False, only return scores for
            positions each player has actually played.

    Returns:
        Dictionary mapping player names to position scores
        Format: {player_name: {position: score}}
        Scores are in the range 0-100. Unplayed positions use predicted scores
        when predict_all_positions=True.

    Example:
        >>> scores = analyze_defensive_performance('defensive_stats.json')
        >>> print(scores['John Doe']['C'])
        85.5
        >>> # John may have scores for positions he hasn't played (predicted)
        >>> scores = analyze_defensive_performance('data.json', predict_all_positions=False)
    """
    parser = DefensiveStatsParser()
    players_data = parser.parse(input_file)

    kb = DefensiveKnowledgeBase()
    position_evaluator = PositionEvaluator(kb)
    score_calculator = ScoreCalculator(kb)

    facts_dict = position_evaluator.evaluate_all_players(
        players_data, predict_all_positions=predict_all_positions
    )
    scores = score_calculator.calculate_all_scores(facts_dict)

    return scores
