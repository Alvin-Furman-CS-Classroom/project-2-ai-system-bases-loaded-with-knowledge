"""
Demo script for analyzing multiple batters against multiple pitchers.

Demonstrates the matrix analysis functionality that evaluates all
batter-pitcher combinations.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DATA = REPO_ROOT / 'test_data'
sys.path.insert(0, str(REPO_ROOT / 'src'))

from module1.matchup_analyzer import (
    analyze_matchups_matrix,
    analyze_matchups_matrix_from_file
)
from module1.models import Batter, Pitcher
from module1.rule_evaluator import RuleEvaluator


def main():
    """Run demo of matrix matchup analysis."""
    print("=" * 70)
    print("Module 1: Multiple Batters vs Multiple Pitchers (Matrix Analysis)")
    print("=" * 70)
    print()
    
    # Method 1: Using objects (matches first batters/pitchers in test_data/matchups_matrix.json)
    print("Method 1: Analyzing multiple batters vs multiple pitchers (using objects)")
    print("-" * 70)
    
    batters = [
        Batter(name="Matt Olson", ba=0.272, k=176, obp=0.366, slg=0.484,
               hr=29, rbi=95, handedness="L"),
        Batter(name="Michael Harris II", ba=0.249, k=128, obp=0.268, slg=0.409,
               hr=20, rbi=86, handedness="L"),
        Batter(name="Ozzie Albies", ba=0.24, k=94, obp=0.306, slg=0.365,
               hr=16, rbi=74, handedness="S"),
    ]
    
    pitchers = [
        Pitcher(name="Logan Webb", era=3.22, whip=1.237, k_rate=0.262,
                handedness="RHP", walk_rate=0.054),
        Pitcher(name="Garrett Crochet", era=2.59, whip=1.028, k_rate=0.313,
                handedness="LHP", walk_rate=0.057),
        Pitcher(name="Max Fried", era=2.86, whip=1.101, k_rate=0.236,
                handedness="LHP", walk_rate=0.064),
    ]
    
    scores_matrix = analyze_matchups_matrix(batters, pitchers, RuleEvaluator())
    
    print(f"\nAnalyzing {len(batters)} batters against {len(pitchers)} pitchers:")
    print(f"Total matchups: {len(batters) * len(pitchers)}")
    print()
    
    print(f"{'Batter':<20}", end="")
    for p in pitchers:
        print(f"{(p.name or 'Unknown'):>15}", end="")
    print()
    print("-" * 70)
    
    for batter in batters:
        print(f"{batter.name:<20}", end="")
        for p in pitchers:
            pid = p.name or "Unknown"
            print(f"{scores_matrix[batter.name][pid]:>15.2f}", end="")
        print()
    
    print()
    print("=" * 70)
    
    # Method 2: From file (test_data/matchups_matrix.json)
    print("\nMethod 2: Analyzing from file (JSON)")
    print("-" * 70)
    
    json_path = TEST_DATA / 'matchups_matrix.json'
    try:
        scores_from_file = analyze_matchups_matrix_from_file(
            str(json_path), rule_evaluator=RuleEvaluator()
        )
        
        batter_names = list(scores_from_file.keys())
        pitcher_names = list(scores_from_file[batter_names[0]].keys())
        print(f"\nFound {len(batter_names)} batters against {len(pitcher_names)} pitchers:")
        print()
        
        # Show first 5 batters, first 5 pitchers to fit screen
        show_batters = batter_names[:5]
        show_pitchers = pitcher_names[:5]
        
        print(f"{'Batter':<20}", end="")
        for pn in show_pitchers:
            print(f"{pn:>15}", end="")
        print()
        print("-" * 70)
        
        for bn in show_batters:
            print(f"{bn:<20}", end="")
            for pn in show_pitchers:
                print(f"{scores_from_file[bn][pn]:>15.2f}", end="")
            print()
        
        if len(batter_names) > 5 or len(pitcher_names) > 5:
            print(f"  ... (showing 5x5; full matrix: {len(batter_names)}x{len(pitcher_names)})")
        
        print()
        print("Example: Access specific matchup:")
        print(f"  scores['{batter_names[0]}']['{pitcher_names[0]}'] = {scores_from_file[batter_names[0]][pitcher_names[0]]:.2f}")
        
    except FileNotFoundError:
        print(f"Error: {json_path} not found")
        print("Run from repo root: python3 demos/demo_matchups_matrix.py")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    print("=" * 70)
    print("Scores use first-order logic rules (handedness, OBP/walk rate, etc.).")
    print("=" * 70)


if __name__ == '__main__':
    main()
