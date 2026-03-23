"""
Module 3: CSP (Constraint Satisfaction Problem) — defensive position assignment.

Exports the public API for assigning players to defensive positions using
offensive and defensive scores plus eligibility constraints.
"""

from .position_assignment import assign_defensive_positions

__all__ = ["assign_defensive_positions"]

