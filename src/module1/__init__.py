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
from .logic_engine import LogicEngine
from .matchup_rules import (
    handedness_penalty,
    obp_walk_advantage,
    power_vs_era_advantage,
    strikeout_matchup,
    obp_vs_whip_advantage,
    elite_batter_bonus,
    elite_pitcher_penalty,
    power_hitter_bonus,
    contact_hitter_advantage,
    get_all_rules,
    evaluate_single_matchup
)
from .rule_evaluator import RuleEvaluator

__all__ = [
    'Batter', 
    'Pitcher', 
    'analyze_matchup_performance',
    'analyze_batter_vs_pitchers',
    'analyze_batter_vs_pitchers_from_file',
    'analyze_matchups_matrix',
    'analyze_matchups_matrix_from_file',
    'ScoreCalculator', 
    'MatchupDataParser',
    'LogicEngine',
    'handedness_penalty',
    'obp_walk_advantage',
    'power_vs_era_advantage',
    'strikeout_matchup',
    'obp_vs_whip_advantage',
    'elite_batter_bonus',
    'elite_pitcher_penalty',
    'power_hitter_bonus',
    'contact_hitter_advantage',
    'get_all_rules',
    'evaluate_single_matchup',
    'RuleEvaluator'
]
