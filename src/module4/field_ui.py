"""
Terminal field visualization for baseball/softball defensive positions.

Also includes a high-level side-by-side dashboard:
- batting order column
- defensive diamond column
"""

from __future__ import annotations

from typing import Dict, Sequence

REQUIRED_POSITIONS = ("P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF")


def _short(name: str, width: int = 12) -> str:
    if len(name) <= width:
        return name.ljust(width)
    return (name[: width - 1] + "…") if width > 1 else name[:width]


def render_field_positions(position_assignment: Dict[str, str]) -> str:
    """
    Return an ASCII baseball field with player names at each defensive position.
    """
    missing = [p for p in REQUIRED_POSITIONS if p not in position_assignment]
    if missing:
        raise ValueError(f"Missing required positions: {missing}")

    lf = _short(position_assignment["LF"])
    cf = _short(position_assignment["CF"])
    rf = _short(position_assignment["RF"])
    ss = _short(position_assignment["SS"])
    b2 = _short(position_assignment["2B"])
    b3 = _short(position_assignment["3B"])
    b1 = _short(position_assignment["1B"])
    p = _short(position_assignment["P"])
    c = _short(position_assignment["C"])

    return "\n".join(
        [
            "                         OUTFIELD",
            "",
            f"      LF [{lf}]      CF [{cf}]      RF [{rf}]",
            "",
            "                           |",
            f"          3B [{b3}]   SS [{ss}]   2B [{b2}]   1B [{b1}]",
            "                           |",
            f"                        P [{p}]",
            f"                        C [{c}]",
            "",
            "                          HOME",
        ]
    )


def print_field_positions(position_assignment: Dict[str, str]) -> None:
    """Print the rendered field to stdout."""
    print(render_field_positions(position_assignment))


def render_lineup_and_field(
    batting_order: Sequence[str],
    position_assignment: Dict[str, str],
) -> str:
    """
    Render batting order and field diagram side-by-side.

    Left column: batting order (1-9)
    Right column: baseball field with defensive assignments
    """
    if len(batting_order) != 9 or len(set(batting_order)) != 9:
        raise ValueError("batting_order must contain exactly 9 unique players")

    left_lines = ["BATTING ORDER", ""] + [
        f"{idx}. {name}" for idx, name in enumerate(batting_order, start=1)
    ]
    right_lines = render_field_positions(position_assignment).splitlines()

    left_width = max(len(line) for line in left_lines) + 4
    max_rows = max(len(left_lines), len(right_lines))
    padded_left = left_lines + [""] * (max_rows - len(left_lines))
    padded_right = right_lines + [""] * (max_rows - len(right_lines))

    merged = []
    for l, r in zip(padded_left, padded_right):
        merged.append(l.ljust(left_width) + r)
    return "\n".join(merged)


def print_lineup_and_field(
    batting_order: Sequence[str],
    position_assignment: Dict[str, str],
) -> None:
    """Print side-by-side batting order + field visualization."""
    print(render_lineup_and_field(batting_order, position_assignment))
