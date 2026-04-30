"""
Demo script for analyzing one batter against multiple pitchers.

Demonstrates how to use the matchup analysis module to evaluate how
a single batter performs against different opponent pitchers.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DATA = REPO_ROOT / 'test_data'
sys.path.insert(0, str(REPO_ROOT / 'src'))

from module1.matchup_analyzer import (
    analyze_batter_vs_pitchers,
    analyze_batter_vs_pitchers_from_file
)
from module1.models import Batter, Pitcher
from module1.rule_evaluator import RuleEvaluator


def main():
    """Run demo of batter vs multiple pitchers analysis."""
    print("=" * 60)
    print("Module 1: Batter vs Multiple Pitchers Demo")
    print("=" * 60)
    print()
    
    # Method 1: Using objects (matches test_data/batter_vs_pitchers.json first batter)
    print("Method 1: Analyzing batter against multiple pitchers (using objects)")
    print("-" * 60)
    
    batter = Batter(
        name="Jonathan Ornelas",
        ba=0.5,
        k=0,
        obp=0.5,
        slg=0.5,
        hr=0,
        rbi=0,
        handedness="R"
    )
    
    pitchers = [
        Pitcher(name="Logan Webb", era=3.22, whip=1.237, k_rate=0.262,
                handedness="RHP", walk_rate=0.054),
        Pitcher(name="Garrett Crochet", era=2.59, whip=1.028, k_rate=0.313,
                handedness="LHP", walk_rate=0.057),
        Pitcher(name="Max Fried", era=2.86, whip=1.101, k_rate=0.236,
                handedness="LHP", walk_rate=0.064),
    ]
    
    scores = analyze_batter_vs_pitchers(batter, pitchers, RuleEvaluator())
    
    print(f"\nAnalyzing {batter.name} against {len(pitchers)} pitchers:")
    print()
    print(f"{'Pitcher Name':<30} {'Score':>10}")
    print("-" * 42)
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for pitcher_name, score in sorted_scores:
        print(f"{pitcher_name:<30} {score:>10.2f}")
    
    print()
    print(f"Best matchup: {sorted_scores[0][0]} ({sorted_scores[0][1]:.2f})")
    print(f"Worst matchup: {sorted_scores[-1][0]} ({sorted_scores[-1][1]:.2f})")
    
    print()
    print("=" * 60)
    
    # Method 2: Using file input (test_data/batter_vs_pitchers.json)
    print("\nMethod 2: Analyzing from file (JSON)")
    print("-" * 60)
    
    json_path = TEST_DATA / 'batter_vs_pitchers.json'
    try:
        scores_from_file = analyze_batter_vs_pitchers_from_file(
            str(json_path), rule_evaluator=RuleEvaluator()
        )
        
        print(f"\nFound {len(scores_from_file)} pitcher matchups:")
        print()
        print(f"{'Pitcher Name':<30} {'Score':>10}")
        print("-" * 42)
        
        sorted_file_scores = sorted(scores_from_file.items(), key=lambda x: x[1], reverse=True)
        for pitcher_name, score in sorted_file_scores[:15]:  # Show top 15
            print(f"{pitcher_name:<30} {score:>10.2f}")
        if len(sorted_file_scores) > 15:
            print(f"  ... and {len(sorted_file_scores) - 15} more")
        
    except FileNotFoundError:
        print(f"Error: {json_path} not found")
        print("Run from repo root: python3 demos/demo_batter_vs_pitchers.py")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    print("=" * 60)
    print("Scores use first-order logic rules (handedness, OBP/walk rate, etc.).")
    print("=" * 60)


if __name__ == '__main__':
    main()
