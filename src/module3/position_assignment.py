"""
Module 3: Defensive position assignment (CSP wrapper).

This module converts:
  - Module 1 offensive scores: {player_name: score}
  - Module 2 defensive scores: {player_name: {position: score}}
  - eligibility: {player_name: [positions...]}
into an assignment of 9 players to 9 positions.

Search is performed by ``csp_solver.solve_max_csp`` (MRV, forward checking, LCV, branch-and-bound).

**Defensive stress profile (optional):** ``defensive_stress_profile="up_the_middle"`` scales the
*defensive* part of the objective using **research-based positional difficulty** from FanGraphs’
published **WAR positional adjustment** runs (see ``docs/MODULE3_DEFENSIVE_LEVERAGE_SOURCES.md``).
Offense is unchanged; the pitcher's defensive term stays 0 in Module 2, so ``P`` uses a neutral
multiplier (1.0).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple, Union

from .csp_solver import solve_max_csp


class LineupAssignmentError(ValueError):
    """
    Base exception for defensive lineup assignment in Module 3.

    Subclasses ``ValueError`` so callers may keep using ``except ValueError``.
    """


class InvalidLineupInputError(LineupAssignmentError):
    """Scores, eligibility, locks, weights, or stress profile are invalid or inconsistent."""


class InfeasibleLineupError(LineupAssignmentError):
    """No complete assignment satisfies eligibility, all-different, and locks."""


DEFAULT_POSITIONS: List[str] = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]
FIELD_POSITIONS: List[str] = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]

# Maps FanGraphs positional-adjustment runs to multipliers near 1.0 (see docs).
DEFAULT_LEVERAGE_LINEAR_SCALE: float = 0.016

# FanGraphs Sabermetrics Library — Positional Adjustment (runs per ~162 defensive games).
# https://library.fangraphs.com/misc/war/positional-adjustment/
# Methodology traces to analyses of players changing positions (see article + Tango links).
FGRAPHS_POSITIONAL_ADJUSTMENT_RUNS: Dict[str, float] = {
    "C": 12.5,
    "1B": -12.5,
    "2B": 2.5,
    "SS": 7.5,
    "3B": 2.5,
    "LF": -7.5,
    "CF": 2.5,
    "RF": -7.5,
}


def defense_multipliers_from_positional_adjustment_runs(
    *,
    linear_scale: float = DEFAULT_LEVERAGE_LINEAR_SCALE,
    pitcher_multiplier: float = 1.0,
) -> Dict[str, float]:
    """
    Map FanGraphs-style positional adjustment runs to multipliers near 1.0.

    multiplier(pos) = 1.0 + linear_scale * runs_FG(pos)

    Default ``linear_scale`` is ``DEFAULT_LEVERAGE_LINEAR_SCALE``.

    ``P`` is not in the FanGraphs fielding table; we use ``pitcher_multiplier`` (default neutral).

    See ``docs/MODULE3_DEFENSIVE_LEVERAGE_SOURCES.md`` for citations and caveats.
    """
    out: Dict[str, float] = {"P": float(pitcher_multiplier)}
    for pos, runs in FGRAPHS_POSITIONAL_ADJUSTMENT_RUNS.items():
        out[pos] = 1.0 + float(linear_scale) * runs
    return out


# Default profile used when defensive_stress_profile == "up_the_middle" (research-backed).
DEFENSIVE_LEVERAGE_UP_THE_MIDDLE: Dict[str, float] = (
    defense_multipliers_from_positional_adjustment_runs()
)

StressProfile = Union[None, Literal["flat"], Literal["up_the_middle"]]


def _defense_multipliers_for_profile(
    profile: StressProfile,
    positions: List[str],
) -> Dict[str, float]:
    if profile is None or profile == "flat":
        return {p: 1.0 for p in positions}
    if profile == "up_the_middle":
        out: Dict[str, float] = {}
        for p in positions:
            if p not in DEFENSIVE_LEVERAGE_UP_THE_MIDDLE:
                raise InvalidLineupInputError(
                    f"Unknown position {p!r} for defensive stress profile "
                    f"(expected one of {sorted(DEFENSIVE_LEVERAGE_UP_THE_MIDDLE.keys())})"
                )
            out[p] = DEFENSIVE_LEVERAGE_UP_THE_MIDDLE[p]
        return out
    raise InvalidLineupInputError(
        f"defensive_stress_profile must be None, 'flat', or 'up_the_middle', not {profile!r}"
    )


def _normalize_weights(weights: Optional[object]) -> Tuple[float, float]:
    # weights can be:
    # - None: use defaults
    # - (w_def, w_off)
    # - {"w_def": ..., "w_off": ...}
    if weights is None:
        return 0.65, 0.35

    if isinstance(weights, dict):
        w_def = float(weights.get("w_def", 0.65))
        w_off = float(weights.get("w_off", 0.35))
        return w_def, w_off

    if isinstance(weights, (tuple, list)) and len(weights) == 2:
        return float(weights[0]), float(weights[1])

    raise InvalidLineupInputError(
        "weights must be None, a (w_def, w_off) tuple, or {'w_def':..., 'w_off':...}"
    )


@dataclass(frozen=True)
class _DomainItem:
    player: str
    offense: float
    defense: float


def _build_position_domains(
    offensive_scores: Dict[str, float],
    defensive_scores: Dict[str, Dict[str, float]],
    position_eligibility: Dict[str, List[str]],
    positions: List[str],
) -> Dict[str, List[_DomainItem]]:
    domains: Dict[str, List[_DomainItem]] = {pos: [] for pos in positions}

    # Pre-validate offensive scores referenced by eligibility.
    for player in position_eligibility.keys():
        if player not in offensive_scores:
            raise InvalidLineupInputError(f"Missing offensive score for eligible player: {player}")

    for player, eligible_positions in position_eligibility.items():
        offense = float(offensive_scores[player])

        for pos in eligible_positions:
            if pos not in domains:
                continue

            if pos == "P":
                # Pitcher "position" has no defensive component in Module 2.
                domains[pos].append(_DomainItem(player=player, offense=offense, defense=0.0))
                continue

            # For field positions, defensive score is required.
            if player not in defensive_scores or pos not in defensive_scores[player]:
                raise InvalidLineupInputError(
                    f"Missing defensive score for player '{player}' at position '{pos}'"
                )

            domains[pos].append(
                _DomainItem(player=player, offense=offense, defense=float(defensive_scores[player][pos]))
            )

    # Ensure every position has at least one eligible player.
    for pos, domain in domains.items():
        if not domain:
            raise InvalidLineupInputError(f"No eligible players found for position '{pos}'")

    return domains


def assign_defensive_positions(
    offensive_scores: Dict[str, float],
    defensive_scores: Dict[str, Dict[str, float]],
    position_eligibility: Dict[str, List[str]],
    *,
    weights: Optional[object] = None,
    lock_positions: Optional[Dict[str, str]] = None,
    positions: Optional[List[str]] = None,
    defensive_stress_profile: StressProfile = None,
) -> Dict[str, str]:
    """
    Assign 9 players to positions by maximizing an objective that blends:
      - offensive value (Module 1)
      - defensive value (Module 2)

    Args:
        offensive_scores: {player_name: score} from Module 1 (0-100)
        defensive_scores: {player_name: {position: score}} from Module 2 (0-100)
        position_eligibility: {player_name: [positions...]}
        weights: defaults to w_def=0.65, w_off=0.35
        lock_positions: optional {position: player_name}
        positions: optional override of which positions to solve for
        defensive_stress_profile: optional ``\"up_the_middle\"`` to scale defense using
            FanGraphs positional-adjustment runs (see ``docs/MODULE3_DEFENSIVE_LEVERAGE_SOURCES.md``).
            ``None`` and ``\"flat\"`` use multiplier 1.0 everywhere.

    Returns:
        {position: player_name}

    Raises:
        InvalidLineupInputError: Invalid or inconsistent inputs (including bad weights/profile).
        InfeasibleLineupError: CSP found no satisfying assignment.
    """
    if not offensive_scores:
        raise InvalidLineupInputError("offensive_scores must be a non-empty dict")
    if not position_eligibility:
        raise InvalidLineupInputError("position_eligibility must be a non-empty dict")

    pos_list = positions[:] if positions is not None else DEFAULT_POSITIONS[:]
    w_def, w_off = _normalize_weights(weights)
    leverage = _defense_multipliers_for_profile(defensive_stress_profile, pos_list)

    item_domains = _build_position_domains(
        offensive_scores=offensive_scores,
        defensive_scores=defensive_scores,
        position_eligibility=position_eligibility,
        positions=pos_list,
    )

    locked: Dict[str, str] = dict(lock_positions or {})
    for pos, player in locked.items():
        if pos not in pos_list:
            raise InvalidLineupInputError(f"lock position '{pos}' is not in positions list")

        if player not in {item.player for item in item_domains[pos]}:
            raise InvalidLineupInputError(
                f"Locked player '{player}' is not eligible for position '{pos}'"
            )

    locked_players = list(locked.values())
    if len(set(locked_players)) != len(locked_players):
        raise InvalidLineupInputError(
            "lock_positions has duplicate player names for different positions"
        )

    # CSP domains: position -> list of player names (deterministic order).
    player_domains: Dict[str, List[str]] = {
        pos: sorted({item.player for item in items}) for pos, items in item_domains.items()
    }

    score_for: Dict[Tuple[str, str], float] = {}
    for pos, items in item_domains.items():
        mult = leverage[pos]
        for item in items:
            score_for[(pos, item.player)] = (
                w_def * item.defense * mult + w_off * item.offense
            )

    def contribution(position: str, player: str) -> float:
        try:
            return score_for[(position, player)]
        except KeyError as exc:
            raise InvalidLineupInputError(
                f"Internal inconsistency: no score for player {player!r} at position {position!r}"
            ) from exc

    result = solve_max_csp(
        pos_list,
        player_domains,
        contribution,
        all_different=True,
        locked=locked if locked else None,
    )

    if result is None:
        raise InfeasibleLineupError("No feasible assignment found for the given constraints")

    return result
