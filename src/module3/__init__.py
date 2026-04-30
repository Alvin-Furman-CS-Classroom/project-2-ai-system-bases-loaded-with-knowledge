"""
Module 3: CSP (Constraint Satisfaction Problem) — defensive position assignment.

Exports the public assignment API and the generic CSP solver used underneath.
"""

from .csp_solver import solve_max_csp
from .position_assignment import (
    DEFAULT_LEVERAGE_LINEAR_SCALE,
    DEFAULT_POSITIONS,
    DEFENSIVE_LEVERAGE_UP_THE_MIDDLE,
    FIELD_POSITIONS,
    FGRAPHS_POSITIONAL_ADJUSTMENT_RUNS,
    InfeasibleLineupError,
    InvalidLineupInputError,
    LineupAssignmentError,
    assign_defensive_positions,
    defense_multipliers_from_positional_adjustment_runs,
)

__all__ = [
    "DEFAULT_LEVERAGE_LINEAR_SCALE",
    "DEFAULT_POSITIONS",
    "DEFENSIVE_LEVERAGE_UP_THE_MIDDLE",
    "FIELD_POSITIONS",
    "FGRAPHS_POSITIONAL_ADJUSTMENT_RUNS",
    "InfeasibleLineupError",
    "InvalidLineupInputError",
    "LineupAssignmentError",
    "assign_defensive_positions",
    "defense_multipliers_from_positional_adjustment_runs",
    "solve_max_csp",
]

