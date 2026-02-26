#!/usr/bin/env python3
"""
Demo script for Module 2: Defensive Performance Analysis.

Prints parsed data, facts, raw evaluations (0-1), and final scores (0-100)
to show the pipeline working correctly. Uses test_data/defensive_stats.json
by default; pass a file path as an argument to use CSV or another file.

Run from repo root:
  PYTHONPATH=src python3 demo_defensive_analysis.py
  PYTHONPATH=src python3 demo_defensive_analysis.py test_data/defensive_stats.csv
"""

import sys
from pathlib import Path

# Allow importing module2 from src
REPO_ROOT = Path(__file__).resolve().parent
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from module2.input_parser import DefensiveStatsParser
from module2.knowledge_base import DefensiveKnowledgeBase
from module2.position_evaluator import PositionEvaluator
from module2.score_calculator import ScoreCalculator


def main():
    data_dir = REPO_ROOT / "test_data"
    default_path = data_dir / "defensive_stats.json"
    input_file = sys.argv[1] if len(sys.argv) > 1 else str(default_path)

    print("=" * 70)
    print("Module 2: Defensive Performance Analysis — Demo")
    print("=" * 70)
    print(f"Input file: {input_file}\n")

    # 1. Parse
    parser = DefensiveStatsParser()
    players_data = parser.parse(input_file)
    print(f"[PARSED] {len(players_data)} players loaded.\n")

    # 2. Initialize components
    kb = DefensiveKnowledgeBase()
    position_evaluator = PositionEvaluator(kb)
    score_calculator = ScoreCalculator(kb)

    # 3. Build facts (evaluate + predict all positions for all players)
    facts_dict = position_evaluator.evaluate_all_players(
        players_data, predict_all_positions=True
    )
    print("[FACTS] Defensive facts per player/position (played + predicted):\n")

    for player_name in sorted(facts_dict.keys()):
        pos_facts = facts_dict[player_name]
        if not pos_facts:
            print(f"  {player_name}: (no eligible positions)")
            continue
        print(f"  {player_name}:")
        for pos in sorted(pos_facts.keys()):
            fact = pos_facts[pos]
            # Show key fact fields
            parts = [
                f"fielding_pct={fact.fielding_pct:.3f}",
                f"errors={fact.errors}",
                f"putouts={fact.putouts}",
            ]
            if fact.is_catcher:
                parts.extend([
                    f"passed_balls={fact.passed_balls}",
                    f"caught_stealing_pct={fact.caught_stealing_pct:.3f}",
                ])
            raw = kb.evaluate(fact)
            score_100 = score_calculator.calculate_score(fact)
            print(f"    {pos}: {', '.join(parts)}")
            print(f"         -> raw evaluation (0-1): {raw:.4f}  |  score (0-100): {score_100:.2f}")
        print()

    # 4. Final scores (same as analyze_defensive_performance output)
    scores = score_calculator.calculate_all_scores(facts_dict)
    print("[SCORES] Final defensive scores (0-100) by player and position:\n")

    for player_name in sorted(scores.keys()):
        pos_scores = scores[player_name]
        if not pos_scores:
            continue
        line = f"  {player_name}: " + "  |  ".join(
            f"{pos}={pos_scores[pos]:.1f}" for pos in sorted(pos_scores.keys())
        )
        print(line)

    print("\n" + "=" * 70)
    print("Demo complete. Facts, evaluations, and scores printed above.")
    print("=" * 70)


if __name__ == "__main__":
    main()
