"""Module 4 public exports."""

from module4.batting_order import optimize_batting_order
from module4.field_ui import (
    print_field_positions,
    print_lineup_and_field,
    render_field_positions,
    render_lineup_and_field,
)
from module4.genetic_optimizer import InvalidOptimizationInputError, run_genetic_lineup_optimization
from module4.lineup_fitness import (
    LineupFitnessError,
    LineupFitnessWeights,
    MissingBattingStatsError,
    evaluate_lineup_fitness,
    make_lineup_fitness_function,
)
from module4.web_ui import render_lineup_dashboard_html, write_lineup_dashboard_html

__all__ = [
    "InvalidOptimizationInputError",
    "LineupFitnessError",
    "LineupFitnessWeights",
    "MissingBattingStatsError",
    "evaluate_lineup_fitness",
    "make_lineup_fitness_function",
    "optimize_batting_order",
    "render_field_positions",
    "render_lineup_and_field",
    "print_field_positions",
    "print_lineup_and_field",
    "render_lineup_dashboard_html",
    "write_lineup_dashboard_html",
    "run_genetic_lineup_optimization",
]
