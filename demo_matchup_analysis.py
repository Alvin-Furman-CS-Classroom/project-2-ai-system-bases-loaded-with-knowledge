"""
Demo script for Module 1: Matchup Analysis

Demonstrates how to use the matchup analysis module to calculate
performance scores for batters against an opponent pitcher.
"""

from src.module1.matchup_analyzer import analyze_matchup_performance


def main():
    """Run demo of matchup analysis."""
    print("=" * 60)
    print("Module 1: Matchup Analysis Demo")
    print("=" * 60)
    print()
    
    # Analyze matchup performance from JSON file
    print("Analyzing matchup performance from JSON file...")
    print("-" * 60)
    
    try:
        scores = analyze_matchup_performance('test_data/matchup_stats.json')
        
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
        print("Error: test_data/matchup_stats.json not found")
        print("Please ensure the test data file exists.")
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
