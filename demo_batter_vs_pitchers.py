"""
Demo script for analyzing one batter against multiple pitchers.

Demonstrates the new functionality to evaluate how a single batter
performs against different opponent pitchers.
"""

from src.module1.matchup_analyzer import (
    analyze_batter_vs_pitchers,
    analyze_batter_vs_pitchers_from_file
)
from src.module1.models import Batter, Pitcher


def main():
    """Run demo of batter vs multiple pitchers analysis."""
    print("=" * 60)
    print("Module 1: Batter vs Multiple Pitchers Demo")
    print("=" * 60)
    print()
    
    # Method 1: Using objects directly
    print("Method 1: Analyzing batter against multiple pitchers (using objects)")
    print("-" * 60)
    
    batter = Batter(
        name="Mike Trout",
        ba=0.306,
        k=132,
        obp=0.419,
        slg=0.582,
        hr=40,
        rbi=80,
        handedness="R"
    )
    
    pitchers = [
        Pitcher(name="Gerrit Cole", era=2.63, whip=0.98, k_rate=0.33,
                handedness="RHP", walk_rate=0.06),
        Pitcher(name="Justin Verlander", era=3.22, whip=1.05, k_rate=0.28,
                handedness="RHP", walk_rate=0.07),
        Pitcher(name="Jacob deGrom", era=2.67, whip=0.95, k_rate=0.35,
                handedness="RHP", walk_rate=0.05),
    ]
    
    scores = analyze_batter_vs_pitchers(batter, pitchers)
    
    print(f"\nAnalyzing {batter.name} against {len(pitchers)} pitchers:")
    print()
    print(f"{'Pitcher Name':<30} {'Score':>10}")
    print("-" * 42)
    
    # Sort by score (descending) for better display
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for pitcher_name, score in sorted_scores:
        print(f"{pitcher_name:<30} {score:>10.2f}")
    
    print()
    print(f"Best matchup: {sorted_scores[0][0]} ({sorted_scores[0][1]:.2f})")
    print(f"Worst matchup: {sorted_scores[-1][0]} ({sorted_scores[-1][1]:.2f})")
    
    print()
    print("=" * 60)
    
    # Method 2: Using file input
    print("\nMethod 2: Analyzing from file (JSON)")
    print("-" * 60)
    
    try:
        scores_from_file = analyze_batter_vs_pitchers_from_file(
            'test_data/batter_vs_pitchers.json'
        )
        
        print(f"\nFound {len(scores_from_file)} pitcher matchups:")
        print()
        print(f"{'Pitcher Name':<30} {'Score':>10}")
        print("-" * 42)
        
        sorted_file_scores = sorted(scores_from_file.items(), 
                                   key=lambda x: x[1], reverse=True)
        for pitcher_name, score in sorted_file_scores:
            print(f"{pitcher_name:<30} {score:>10.2f}")
        
    except FileNotFoundError:
        print("Error: test_data/batter_vs_pitchers.json not found")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    print("=" * 60)
    print("Note: These scores are base scores calculated from batter statistics.")
    print("Rule-based adjustments will be applied when Partner B's components")
    print("(logic_engine.py, matchup_rules.py, rule_evaluator.py) are implemented.")
    print("=" * 60)


if __name__ == '__main__':
    main()
