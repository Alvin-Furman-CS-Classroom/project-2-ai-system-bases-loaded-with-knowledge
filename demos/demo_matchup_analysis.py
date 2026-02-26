"""
Demo script for Module 1: Matchup Analysis

Demonstrates how to use the matchup analysis module to calculate
performance scores for batters against an opponent pitcher.
"""

import sys
from pathlib import Path

# Resolve test_data path relative to repo root (works when run from repo root or demos/)
REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DATA = REPO_ROOT / 'test_data'
sys.path.insert(0, str(REPO_ROOT / 'src'))

from module1.matchup_analyzer import analyze_matchup_performance
from module1.rule_evaluator import RuleEvaluator


def main():
    """Run demo of matchup analysis."""
    print("=" * 60)
    print("Module 1: Matchup Analysis Demo")
    print("=" * 60)
    print()
    
    json_path = TEST_DATA / 'matchup_stats.json'
    
    # Analyze matchup performance from JSON file (with first-order logic rules)
    print("Analyzing matchup performance from JSON file...")
    print("-" * 60)
    
    try:
        evaluator = RuleEvaluator()
        scores = analyze_matchup_performance(str(json_path), rule_evaluator=evaluator)
        
        print(f"\nFound {len(scores)} batters:")
        print()
        
        # Sort by score (descending) for better display
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"{'Batter Name':<30} {'Score':>10}")
        print("-" * 42)
        for batter_name, score in sorted_scores:
            print(f"{batter_name:<30} {score:>10.2f}")
        
        print()
        print(f"Best matchup: {sorted_scores[0][0]} ({sorted_scores[0][1]:.2f})")
        print(f"Worst matchup: {sorted_scores[-1][0]} ({sorted_scores[-1][1]:.2f})")
        
    except FileNotFoundError:
        print(f"Error: {json_path} not found")
        print("Run from repo root: python3 demos/demo_matchup_analysis.py")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    print("=" * 60)
    print("Scores use first-order logic rules (handedness, OBP/walk rate, etc.).")
    print("=" * 60)


if __name__ == '__main__':
    main()
