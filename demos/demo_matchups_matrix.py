"""
Demo script for analyzing multiple batters against multiple pitchers.

Demonstrates the matrix analysis functionality that evaluates all
batter-pitcher combinations.
"""

from src.module1.matchup_analyzer import (
    analyze_matchups_matrix,
    analyze_matchups_matrix_from_file
)
from src.module1.models import Batter, Pitcher


def main():
    """Run demo of matrix matchup analysis."""
    print("=" * 70)
    print("Module 1: Multiple Batters vs Multiple Pitchers (Matrix Analysis)")
    print("=" * 70)
    print()
    
    # Method 1: Using objects directly
    print("Method 1: Analyzing multiple batters against multiple pitchers (using objects)")
    print("-" * 70)
    
    batters = [
        Batter(name="Mike Trout", ba=0.306, k=132, obp=0.419, slg=0.582,
               hr=40, rbi=80, handedness="R"),
        Batter(name="Freddie Freeman", ba=0.331, k=121, obp=0.410, slg=0.567,
               hr=29, rbi=102, handedness="L"),
        Batter(name="Mookie Betts", ba=0.307, k=131, obp=0.408, slg=0.579,
               hr=39, rbi=107, handedness="R"),
    ]
    
    pitchers = [
        Pitcher(name="Gerrit Cole", era=2.63, whip=0.98, k_rate=0.33,
                handedness="RHP", walk_rate=0.06),
        Pitcher(name="Justin Verlander", era=3.22, whip=1.05, k_rate=0.28,
                handedness="RHP", walk_rate=0.07),
        Pitcher(name="Jacob deGrom", era=2.67, whip=0.95, k_rate=0.35,
                handedness="RHP", walk_rate=0.05),
    ]
    
    scores_matrix = analyze_matchups_matrix(batters, pitchers)
    
    print(f"\nAnalyzing {len(batters)} batters against {len(pitchers)} pitchers:")
    print(f"Total matchups: {len(batters) * len(pitchers)}")
    print()
    
    # Display as a table
    print(f"{'Batter':<20}", end="")
    for pitcher in pitchers:
        pitcher_name = pitcher.name if pitcher.name else "Unknown"
        print(f"{pitcher_name:>15}", end="")
    print()
    print("-" * 70)
    
    for batter in batters:
        print(f"{batter.name:<20}", end="")
        for pitcher in pitchers:
            pitcher_id = pitcher.name if pitcher.name else "Unknown"
            score = scores_matrix[batter.name][pitcher_id]
            print(f"{score:>15.2f}", end="")
        print()
    
    print()
    print("=" * 70)
    
    # Method 2: Using file input
    print("\nMethod 2: Analyzing from file (JSON)")
    print("-" * 70)
    
    try:
        scores_from_file = analyze_matchups_matrix_from_file(
            '../test_data/matchups_matrix.json'
        )
        
        print(f"\nFound {len(scores_from_file)} batters against {len(list(scores_from_file.values())[0])} pitchers:")
        print()
        
        # Get pitcher names from first batter's scores
        pitcher_names = list(scores_from_file[list(scores_from_file.keys())[0]].keys())
        
        # Display as a table
        print(f"{'Batter':<20}", end="")
        for pitcher_name in pitcher_names:
            print(f"{pitcher_name:>15}", end="")
        print()
        print("-" * 70)
        
        for batter_name, pitcher_scores in scores_from_file.items():
            print(f"{batter_name:<20}", end="")
            for pitcher_name in pitcher_names:
                score = pitcher_scores[pitcher_name]
                print(f"{score:>15.2f}", end="")
            print()
        
        print()
        print("Example: Access specific matchup:")
        first_batter = list(scores_from_file.keys())[0]
        first_pitcher = pitcher_names[0]
        print(f"  scores['{first_batter}']['{first_pitcher}'] = {scores_from_file[first_batter][first_pitcher]:.2f}")
        
    except FileNotFoundError:
        print("Error: ../test_data/matchups_matrix.json not found")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    print("=" * 70)
    print("Note: These scores are base scores calculated from batter statistics.")
    print("Rule-based adjustments will be applied when Partner B's components")
    print("(logic_engine.py, matchup_rules.py, rule_evaluator.py) are implemented.")
    print("=" * 70)


if __name__ == '__main__':
    main()
