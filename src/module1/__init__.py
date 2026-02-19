"""
Module 1: Matchup Analysis

This module uses first-order logic to analyze batter-pitcher matchups
and calculate performance scores for each batter.
"""

from .models import Batter, Pitcher
from .matchup_analyzer import (
    analyze_matchup_performance,
    analyze_batter_vs_pitchers,
    analyze_batter_vs_pitchers_from_file,
    analyze_matchups_matrix,
    analyze_matchups_matrix_from_file
)
from .score_calculator import ScoreCalculator
from .input_parser import MatchupDataParser

__all__ = [
    'Batter', 
    'Pitcher', 
    'analyze_matchup_performance',
    'analyze_batter_vs_pitchers',
    'analyze_batter_vs_pitchers_from_file',
    'analyze_matchups_matrix',
    'analyze_matchups_matrix_from_file',
    'ScoreCalculator', 
    'MatchupDataParser'
]
