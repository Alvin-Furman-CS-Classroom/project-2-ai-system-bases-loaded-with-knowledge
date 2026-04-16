"""
Game-state validation and normalization for Module 5 planning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Tuple

_VALID_HALVES = {"top", "bottom"}


class GameStateValidationError(ValueError):
    """Raised when game-state input violates Module 5 contracts."""


@dataclass(frozen=True)
class NormalizedGameState:
    inning: int
    half: str
    outs: int
    score_for: int
    score_against: int
    bases: Tuple[bool, bool, bool]
    substitutions_used: int
    substitutions_limit: int
    pitcher_fatigue: float

    @property
    def substitutions_remaining(self) -> int:
        return self.substitutions_limit - self.substitutions_used

    @property
    def score_diff(self) -> int:
        return self.score_for - self.score_against


def _require_key(data: Mapping[str, Any], key: str) -> Any:
    if key not in data:
        raise GameStateValidationError(f"game_state missing required key {key!r}")
    return data[key]


def _coerce_non_negative_int(name: str, value: Any) -> int:
    if isinstance(value, bool):
        raise GameStateValidationError(f"{name} must be an integer, got bool")
    try:
        int_value = int(value)
    except (TypeError, ValueError) as exc:
        raise GameStateValidationError(f"{name} must be an integer") from exc
    if int_value < 0:
        raise GameStateValidationError(f"{name} must be >= 0")
    return int_value


def _validate_bases(value: Any) -> Tuple[bool, bool, bool]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, dict)):
        raise GameStateValidationError(
            "bases must be an iterable of three booleans [first, second, third]"
        )
    values = list(value)
    if len(values) != 3:
        raise GameStateValidationError("bases must contain exactly three entries")
    validated = []
    for idx, base_occupied in enumerate(values):
        if not isinstance(base_occupied, bool):
            raise GameStateValidationError(
                f"bases index {idx} must be bool, got {type(base_occupied).__name__}"
            )
        validated.append(base_occupied)
    return tuple(validated)  # type: ignore[return-value]


def normalize_game_state(game_state: Mapping[str, Any]) -> NormalizedGameState:
    """
    Validate and normalize game state.

    Required keys:
      inning, half, outs, score_for, score_against, bases,
      substitutions_used, substitutions_limit

    Optional keys:
      pitcher_fatigue (default 0.0, clamped to [0, 1]). Reserved for future use; Module 5 does
      not emit pitching or bullpen recommendations because the project has no pitcher module.
    """
    inning = _coerce_non_negative_int("inning", _require_key(game_state, "inning"))
    if inning < 1:
        raise GameStateValidationError("inning must be >= 1")

    half_raw = _require_key(game_state, "half")
    if not isinstance(half_raw, str):
        raise GameStateValidationError("half must be a string: 'top' or 'bottom'")
    half = half_raw.strip().lower()
    if half not in _VALID_HALVES:
        raise GameStateValidationError("half must be 'top' or 'bottom'")

    outs = _coerce_non_negative_int("outs", _require_key(game_state, "outs"))
    if outs > 2:
        raise GameStateValidationError("outs must be in range [0, 2]")

    score_for = _coerce_non_negative_int("score_for", _require_key(game_state, "score_for"))
    score_against = _coerce_non_negative_int(
        "score_against", _require_key(game_state, "score_against")
    )

    bases = _validate_bases(_require_key(game_state, "bases"))

    substitutions_used = _coerce_non_negative_int(
        "substitutions_used", _require_key(game_state, "substitutions_used")
    )
    substitutions_limit = _coerce_non_negative_int(
        "substitutions_limit", _require_key(game_state, "substitutions_limit")
    )
    if substitutions_used > substitutions_limit:
        raise GameStateValidationError(
            "substitutions_used cannot exceed substitutions_limit"
        )

    fatigue_raw = game_state.get("pitcher_fatigue", 0.0)
    try:
        fatigue = float(fatigue_raw)
    except (TypeError, ValueError) as exc:
        raise GameStateValidationError("pitcher_fatigue must be numeric") from exc
    fatigue = max(0.0, min(fatigue, 1.0))

    return NormalizedGameState(
        inning=inning,
        half=half,
        outs=outs,
        score_for=score_for,
        score_against=score_against,
        bases=bases,
        substitutions_used=substitutions_used,
        substitutions_limit=substitutions_limit,
        pitcher_fatigue=fatigue,
    )


def validate_bench_players(bench_players: Iterable[Mapping[str, Any]]) -> None:
    """
    Validate bench list entries.

    Each bench player must provide:
      - name: non-empty string
      - roles: iterable of non-empty strings
    """
    seen_names = set()
    for idx, player in enumerate(bench_players):
        if "name" not in player:
            raise GameStateValidationError(f"bench player #{idx} missing 'name'")
        name = player["name"]
        if not isinstance(name, str) or not name.strip():
            raise GameStateValidationError(
                f"bench player #{idx} has invalid 'name' value {name!r}"
            )
        normalized_name = name.strip()
        if normalized_name in seen_names:
            raise GameStateValidationError(f"duplicate bench player name {normalized_name!r}")
        seen_names.add(normalized_name)

        if "roles" not in player:
            raise GameStateValidationError(
                f"bench player {normalized_name!r} missing 'roles'"
            )
        roles = list(player["roles"]) if not isinstance(player["roles"], str) else []
        if not roles:
            raise GameStateValidationError(
                f"bench player {normalized_name!r} must include at least one role"
            )
        for role in roles:
            if not isinstance(role, str) or not role.strip():
                raise GameStateValidationError(
                    f"bench player {normalized_name!r} has invalid role {role!r}"
                )


def validate_current_lineup(current_lineup: Mapping[str, Any]) -> Dict[str, str]:
    """
    Validate and normalize current lineup mapping.

    Required format:
      {"batting_order": [9 unique names], "field_positions": {position: player}}
    """
    if "batting_order" not in current_lineup:
        raise GameStateValidationError("current_lineup missing 'batting_order'")
    batting_order = current_lineup["batting_order"]
    if not isinstance(batting_order, list):
        raise GameStateValidationError("current_lineup['batting_order'] must be a list")
    if len(batting_order) != 9:
        raise GameStateValidationError("batting_order must include exactly 9 players")
    if any((not isinstance(name, str) or not name.strip()) for name in batting_order):
        raise GameStateValidationError("batting_order players must be non-empty strings")
    if len(set(batting_order)) != 9:
        raise GameStateValidationError("batting_order players must be unique")

    return {str(slot + 1): name.strip() for slot, name in enumerate(batting_order)}
