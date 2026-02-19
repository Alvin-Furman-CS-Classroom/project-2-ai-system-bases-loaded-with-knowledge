"""
Main analyzer for Module 1: Matchup Analysis

Orchestrates the matchup analysis pipeline using first-order logic rules
to calculate performance scores for each batter against an opponent pitcher.
"""

from typing import Dict, List, Optional
from .input_parser import MatchupDataParser
from .score_calculator import ScoreCalculator
from .models import Batter, Pitcher


def analyze_matchup_performance(
    input_file: str,
    rule_evaluator: Optional[object] = None
) -> Dict[str, float]:
    """
    Analyze matchup performance for all batters against an opponent pitcher.
    
    This is the main public API for Module 1. It:
    1. Parses batter and pitcher statistics from a file
    2. Evaluates first-order logic rules to determine score adjustments
    3. Calculates final performance scores (0-100) for each batter
    
    Args:
        input_file: Path to CSV or JSON file containing:
                   - Batter statistics (BA, K, OBP, SLG, HR, RBI, handedness)
                   - Pitcher statistics (ERA, WHIP, K rate, handedness, walk rate)
        rule_evaluator: Optional rule evaluator object with an evaluate() method
                       that takes (batters, pitcher) and returns {batter_name: adjustment}
                       If None, only base scores are calculated (no rule adjustments)
    
    Returns:
        Dictionary mapping batter names to performance scores (0-100)
        Format: {batter_name: score}
        Higher scores indicate better expected performance against the pitcher.
    
    Example:
        >>> scores = analyze_matchup_performance('matchup_stats.json')
        >>> print(scores['Mike Trout'])
        72.5
        >>> # Use with custom rule evaluator
        >>> from module1.rule_evaluator import RuleEvaluator
        >>> evaluator = RuleEvaluator()
        >>> scores = analyze_matchup_performance('data.json', rule_evaluator=evaluator)
    """
    # Step 1: Parse input file
    parser = MatchupDataParser()
    batters, pitcher = parser.parse(input_file)
    
    # Step 2: Get rule-based adjustments (if rule evaluator provided)
    adjustments: Dict[str, float] = {}
    if rule_evaluator is not None:
        try:
            # Rule evaluator should have an evaluate method
            # Signature: evaluate(batters: List[Batter], pitcher: Pitcher) -> Dict[str, float]
            if hasattr(rule_evaluator, 'evaluate'):
                adjustments = rule_evaluator.evaluate(batters, pitcher)
            else:
                # Fallback: try calling it directly if it's callable
                adjustments = rule_evaluator(batters, pitcher) if callable(rule_evaluator) else {}
        except Exception:
            # If rule evaluation fails, continue with base scores only
            adjustments = {}
    
    # Step 3: Calculate final scores
    score_calculator = ScoreCalculator()
    scores = score_calculator.calculate_all_scores(batters, adjustments)
    
    return scores


def analyze_batter_vs_pitchers(
    batter: Batter,
    pitchers: List[Pitcher],
    rule_evaluator: Optional[object] = None
) -> Dict[str, float]:
    """
    Analyze one batter's performance against multiple pitchers.
    
    This function evaluates how a single batter performs against different
    opponent pitchers, returning a score for each pitcher matchup.
    
    Args:
        batter: Single Batter object to evaluate
        pitchers: List of Pitcher objects to compare against
        rule_evaluator: Optional rule evaluator object with an evaluate() method
                       that takes (batter, pitcher) and returns adjustment value
                       If None, only base scores are calculated (no rule adjustments)
    
    Returns:
        Dictionary mapping pitcher names to performance scores (0-100)
        Format: {pitcher_name: score}
        Higher scores indicate better expected performance against that pitcher.
        If pitcher has no name, uses "Pitcher_1", "Pitcher_2", etc.
    
    Example:
        >>> batter = Batter(name="Mike Trout", ba=0.306, k=132, obp=0.419,
        ...                 slg=0.582, hr=40, rbi=80, handedness="R")
        >>> pitchers = [Pitcher(name="Cole", era=2.63, whip=0.98, k_rate=0.33,
        ...                     handedness="RHP", walk_rate=0.06),
        ...              Pitcher(name="Verlander", era=3.22, whip=1.05, k_rate=0.28,
        ...                      handedness="RHP", walk_rate=0.07)]
        >>> scores = analyze_batter_vs_pitchers(batter, pitchers)
        >>> print(scores)
        {'Cole': 43.40, 'Verlander': 42.15}
    """
    if batter is None:
        raise ValueError("batter must be a Batter object")
    
    if not pitchers:
        raise ValueError("pitchers list cannot be empty")
    
    score_calculator = ScoreCalculator()
    results: Dict[str, float] = {}
    
    for i, pitcher in enumerate(pitchers):
        # Get pitcher identifier (name or default)
        pitcher_id = pitcher.name if pitcher.name else f"Pitcher_{i+1}"
        
        # Calculate base score (same for all pitchers - based on batter stats)
        base_score = score_calculator.calculate_base_score(batter)
        
        # Get rule-based adjustment for this specific batter-pitcher matchup
        adjustment = 0.0
        if rule_evaluator is not None:
            try:
                # Rule evaluator should handle single batter-pitcher evaluation
                # Option 1: Has evaluate_single method
                if hasattr(rule_evaluator, 'evaluate_single'):
                    adjustment = rule_evaluator.evaluate_single(batter, pitcher)
                # Option 2: Has evaluate method that can handle single batter
                elif hasattr(rule_evaluator, 'evaluate'):
                    # Try calling with single batter wrapped in list
                    single_batter_adjustments = rule_evaluator.evaluate([batter], pitcher)
                    adjustment = single_batter_adjustments.get(batter.name, 0.0)
                # Option 3: Callable function
                elif callable(rule_evaluator):
                    adjustment = rule_evaluator(batter, pitcher)
            except Exception:
                # If rule evaluation fails, use base score only
                adjustment = 0.0
        
        # Calculate final score
        final_score = score_calculator.apply_adjustments(base_score, adjustment)
        results[pitcher_id] = final_score
    
    return results


def analyze_batter_vs_pitchers_from_file(
    input_file: str,
    batter_name: Optional[str] = None,
    rule_evaluator: Optional[object] = None
) -> Dict[str, float]:
    """
    Analyze one batter's performance against multiple pitchers from a file.
    
    Convenience function that parses a file and analyzes one batter against
    multiple pitchers. The file format should have:
    - One batter (or specify batter_name to select one)
    - Multiple pitchers (in "pitchers" array instead of single "pitcher")
    
    Args:
        input_file: Path to CSV or JSON file containing:
                   - One or more batter statistics
                   - Multiple pitcher statistics (in "pitchers" array)
        batter_name: Optional name of batter to analyze. If None and file has
                     multiple batters, uses the first one.
        rule_evaluator: Optional rule evaluator object
    
    Returns:
        Dictionary mapping pitcher names to performance scores (0-100)
        Format: {pitcher_name: score}
    
    Example:
        >>> scores = analyze_batter_vs_pitchers_from_file('batter_vs_pitchers.json')
        >>> print(scores)
        {'Gerrit Cole': 43.40, 'Justin Verlander': 42.15, 'Jacob deGrom': 41.80}
    """
    from pathlib import Path
    import json
    import csv
    
    path = Path(input_file)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Parse file to get batters and multiple pitchers
    if path.suffix.lower() == '.json':
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle format with multiple pitchers
        if isinstance(data, dict):
            batters_data = data.get('batters', [])
            # Check for "pitchers" (plural) first, then fall back to "pitcher"
            pitchers_data = data.get('pitchers', [])
            if not pitchers_data and 'pitcher' in data:
                pitchers_data = [data['pitcher']]  # Single pitcher wrapped in list
        else:
            raise ValueError("Invalid JSON format")
        
        if not pitchers_data:
            raise ValueError("No pitcher statistics found in JSON file")
        
        # Create batter
        parser = MatchupDataParser()
        batters = [parser._create_batter(b) for b in batters_data]
        pitchers = [parser._create_pitcher(p) for p in pitchers_data]
        
    elif path.suffix.lower() == '.csv':
        parser = MatchupDataParser()
        batters = []
        pitchers = []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if 'era' in row and row['era']:
                    # This is a pitcher row
                    pitchers.append(parser._create_pitcher(row))
                else:
                    # This is a batter row
                    batters.append(parser._create_batter(row))
        
        if not pitchers:
            raise ValueError("No pitcher statistics found in CSV file")
        if not batters:
            raise ValueError("No batter statistics found in CSV file")
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    
    # Select batter
    if batter_name:
        batter = next((b for b in batters if b.name == batter_name), None)
        if batter is None:
            raise ValueError(f"Batter '{batter_name}' not found in file")
    else:
        if not batters:
            raise ValueError("No batters found in file")
        batter = batters[0]
    
    # Analyze batter against all pitchers
    return analyze_batter_vs_pitchers(batter, pitchers, rule_evaluator)


def analyze_matchups_matrix(
    batters: List[Batter],
    pitchers: List[Pitcher],
    rule_evaluator: Optional[object] = None
) -> Dict[str, Dict[str, float]]:
    """
    Analyze multiple batters against multiple pitchers (matrix analysis).
    
    This function evaluates all batter-pitcher combinations, returning a
    nested dictionary with scores for each matchup.
    
    Args:
        batters: List of Batter objects to evaluate
        pitchers: List of Pitcher objects to compare against
        rule_evaluator: Optional rule evaluator object with an evaluate_single() method
                       that takes (batter, pitcher) and returns adjustment value
                       If None, only base scores are calculated (no rule adjustments)
    
    Returns:
        Nested dictionary mapping batter names to pitcher scores
        Format: {batter_name: {pitcher_name: score}}
        Higher scores indicate better expected performance for that batter-pitcher matchup.
    
    Example:
        >>> batters = [Batter(name="Trout", ...), Batter(name="Freeman", ...)]
        >>> pitchers = [Pitcher(name="Cole", ...), Pitcher(name="Verlander", ...)]
        >>> scores = analyze_matchups_matrix(batters, pitchers)
        >>> print(scores['Trout']['Cole'])
        43.40
        >>> # Access all matchups for a batter
        >>> print(scores['Trout'])
        {'Cole': 43.40, 'Verlander': 42.15}
    """
    if not batters:
        raise ValueError("batters list cannot be empty")
    
    if not pitchers:
        raise ValueError("pitchers list cannot be empty")
    
    score_calculator = ScoreCalculator()
    results: Dict[str, Dict[str, float]] = {}
    
    for batter in batters:
        batter_scores: Dict[str, float] = {}
        
        for i, pitcher in enumerate(pitchers):
            # Get pitcher identifier (name or default)
            pitcher_id = pitcher.name if pitcher.name else f"Pitcher_{i+1}"
            
            # Calculate base score for this batter
            base_score = score_calculator.calculate_base_score(batter)
            
            # Get rule-based adjustment for this specific batter-pitcher matchup
            adjustment = 0.0
            if rule_evaluator is not None:
                try:
                    # Rule evaluator should handle single batter-pitcher evaluation
                    # Option 1: Has evaluate_single method
                    if hasattr(rule_evaluator, 'evaluate_single'):
                        adjustment = rule_evaluator.evaluate_single(batter, pitcher)
                    # Option 2: Has evaluate method that can handle single batter
                    elif hasattr(rule_evaluator, 'evaluate'):
                        # Try calling with single batter wrapped in list
                        single_batter_adjustments = rule_evaluator.evaluate([batter], pitcher)
                        adjustment = single_batter_adjustments.get(batter.name, 0.0)
                    # Option 3: Callable function
                    elif callable(rule_evaluator):
                        adjustment = rule_evaluator(batter, pitcher)
                except Exception:
                    # If rule evaluation fails, use base score only
                    adjustment = 0.0
            
            # Calculate final score
            final_score = score_calculator.apply_adjustments(base_score, adjustment)
            batter_scores[pitcher_id] = final_score
        
        results[batter.name] = batter_scores
    
    return results


def analyze_matchups_matrix_from_file(
    input_file: str,
    rule_evaluator: Optional[object] = None
) -> Dict[str, Dict[str, float]]:
    """
    Analyze multiple batters against multiple pitchers from a file.
    
    Convenience function that parses a file and analyzes all batter-pitcher
    combinations. The file format should have:
    - Multiple batters
    - Multiple pitchers (in "pitchers" array instead of single "pitcher")
    
    Args:
        input_file: Path to CSV or JSON file containing:
                   - Multiple batter statistics
                   - Multiple pitcher statistics (in "pitchers" array)
        rule_evaluator: Optional rule evaluator object
    
    Returns:
        Nested dictionary mapping batter names to pitcher scores
        Format: {batter_name: {pitcher_name: score}}
    
    Example:
        >>> scores = analyze_matchups_matrix_from_file('matchups_matrix.json')
        >>> print(scores['Mike Trout']['Gerrit Cole'])
        43.40
        >>> # Get all matchups for a specific batter
        >>> print(scores['Mike Trout'])
        {'Gerrit Cole': 43.40, 'Justin Verlander': 42.15, ...}
    """
    from pathlib import Path
    import json
    import csv
    
    path = Path(input_file)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Parse file to get batters and multiple pitchers
    if path.suffix.lower() == '.json':
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle format with multiple pitchers
        if isinstance(data, dict):
            batters_data = data.get('batters', [])
            # Check for "pitchers" (plural) first, then fall back to "pitcher"
            pitchers_data = data.get('pitchers', [])
            if not pitchers_data and 'pitcher' in data:
                pitchers_data = [data['pitcher']]  # Single pitcher wrapped in list
        else:
            raise ValueError("Invalid JSON format")
        
        if not pitchers_data:
            raise ValueError("No pitcher statistics found in JSON file")
        if not batters_data:
            raise ValueError("No batter statistics found in JSON file")
        
        # Create batters and pitchers
        parser = MatchupDataParser()
        batters = [parser._create_batter(b) for b in batters_data]
        pitchers = [parser._create_pitcher(p) for p in pitchers_data]
        
    elif path.suffix.lower() == '.csv':
        parser = MatchupDataParser()
        batters = []
        pitchers = []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if 'era' in row and row['era']:
                    # This is a pitcher row
                    pitchers.append(parser._create_pitcher(row))
                else:
                    # This is a batter row
                    batters.append(parser._create_batter(row))
        
        if not pitchers:
            raise ValueError("No pitcher statistics found in CSV file")
        if not batters:
            raise ValueError("No batter statistics found in CSV file")
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    
    # Analyze all batters against all pitchers
    return analyze_matchups_matrix(batters, pitchers, rule_evaluator)
