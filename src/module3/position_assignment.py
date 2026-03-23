"""
Module 3: Defensive position assignment (CSP wrapper).

This module converts:
  - Module 1 offensive scores: {player_name: score}
  - Module 2 defensive scores: {player_name: {position: score}}
  - eligibility: {player_name: [positions...]}
into an assignment of 9 players to 9 positions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Iterable


DEFAULT_POSITIONS: List[str] = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]
FIELD_POSITIONS: List[str] = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]


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

    raise ValueError("weights must be None, a (w_def, w_off) tuple, or {'w_def':..., 'w_off':...}")


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
            raise ValueError(f"Missing offensive score for eligible player: {player}")

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
                raise ValueError(
                    f"Missing defensive score for player '{player}' at position '{pos}'"
                )

            domains[pos].append(
                _DomainItem(player=player, offense=offense, defense=float(defensive_scores[player][pos]))
            )

    # Ensure every position has at least one eligible player.
    for pos, domain in domains.items():
        if not domain:
            raise ValueError(f"No eligible players found for position '{pos}'")

    return domains


def assign_defensive_positions(
    offensive_scores: Dict[str, float],
    defensive_scores: Dict[str, Dict[str, float]],
    position_eligibility: Dict[str, List[str]],
    *,
    weights: Optional[object] = None,
    lock_positions: Optional[Dict[str, str]] = None,
    positions: Optional[List[str]] = None,
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

    Returns:
        {position: player_name}
    """
    if not offensive_scores:
        raise ValueError("offensive_scores must be a non-empty dict")
    if not position_eligibility:
        raise ValueError("position_eligibility must be a non-empty dict")

    pos_list = positions[:] if positions is not None else DEFAULT_POSITIONS[:]
    w_def, w_off = _normalize_weights(weights)

    domains = _build_position_domains(
        offensive_scores=offensive_scores,
        defensive_scores=defensive_scores,
        position_eligibility=position_eligibility,
        positions=pos_list,
    )

    locked: Dict[str, str] = dict(lock_positions or {})
    for pos, player in locked.items():
        if pos not in pos_list:
            raise ValueError(f"lock position '{pos}' is not in positions list")

        # Check player is in that position domain.
        if player not in {item.player for item in domains[pos]}:
            raise ValueError(f"Locked player '{player}' is not eligible for position '{pos}'")

    # Validate locked players uniqueness.
    locked_players = list(locked.values())
    if len(set(locked_players)) != len(locked_players):
        raise ValueError("lock_positions has duplicate player names for different positions")

    # Backtracking search with MRV + forward checking.
    best_assignment: Optional[Dict[str, str]] = None
    best_score: float = float("-inf")

    assigned: Dict[str, str] = {}
    used_players: set[str] = set()

    # Apply locked assignments first.
    for pos, player in locked.items():
        assigned[pos] = player
        used_players.add(player)

    def position_objective(pos: str, item: _DomainItem) -> float:
        return w_def * item.defense + w_off * item.offense

    # Build mutable candidate sets (forward checking) from immutable domains.
    # Used to implement MRV efficiently without copying too much state.
    def domain_candidates_for(pos: str) -> List[_DomainItem]:
        return [item for item in domains[pos] if item.player not in used_players]

    # Simple feasibility pruning: for all unassigned positions, ensure at least one candidate remains.
    def all_unassigned_have_candidates() -> bool:
        for p in pos_list:
            if p in assigned:
                continue
            if not domain_candidates_for(p):
                return False
        return True

    def pick_next_position() -> Optional[str]:
        # MRV: select unassigned position with smallest remaining domain.
        unassigned = [p for p in pos_list if p not in assigned]
        if not unassigned:
            return None
        return min(unassigned, key=lambda p: len(domain_candidates_for(p)))

    def backtrack() -> None:
        nonlocal best_assignment, best_score

        if len(assigned) == len(pos_list):
            # Evaluate final score.
            total = 0.0
            for p in pos_list:
                player = assigned[p]
                # Find the matching domain item quickly.
                # Domain sizes are small (eligibility list), so linear scan is fine.
                item = next(item for item in domains[p] if item.player == player)
                total += position_objective(p, item)

            if total > best_score:
                best_score = total
                best_assignment = dict(assigned)
            return

        if not all_unassigned_have_candidates():
            return

        next_pos = pick_next_position()
        if next_pos is None:
            return

        candidates = domain_candidates_for(next_pos)
        # Optional LCV-like ordering: try higher objective contributions first.
        candidates.sort(key=lambda it: position_objective(next_pos, it), reverse=True)

        for item in candidates:
            # Assign and forward-check.
            assigned[next_pos] = item.player
            used_players.add(item.player)

            backtrack()

            used_players.remove(item.player)
            assigned.pop(next_pos, None)

    backtrack()

    if best_assignment is None:
        raise ValueError("No feasible assignment found for the given constraints")

    # Final shape: {position: player_name}
    return best_assignment

