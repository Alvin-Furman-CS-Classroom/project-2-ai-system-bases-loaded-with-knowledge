"""
Browser-based external UI for Module 4 lineup + field visualization.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Dict, Sequence

REQUIRED_POSITIONS = ("P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF")


def _validate_inputs(batting_order: Sequence[str], position_assignment: Dict[str, str]) -> None:
    if len(batting_order) != 9 or len(set(batting_order)) != 9:
        raise ValueError("batting_order must contain exactly 9 unique players")
    missing = [p for p in REQUIRED_POSITIONS if p not in position_assignment]
    if missing:
        raise ValueError(f"Missing required positions: {missing}")


def render_lineup_dashboard_html(
    batting_order: Sequence[str],
    position_assignment: Dict[str, str],
    *,
    title: str = "Module 4 Lineup Dashboard",
) -> str:
    """Return a full HTML page showing batting order and baseball diamond."""
    _validate_inputs(batting_order, position_assignment)

    order_items = "\n".join(
        f"<li><span class='slot'>{i}.</span> {html.escape(name)}</li>"
        for i, name in enumerate(batting_order, start=1)
    )

    def p(pos: str) -> str:
        return html.escape(position_assignment[pos])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
      background: #0b1020;
      color: #e8ecf3;
    }}
    .wrap {{
      max-width: 1100px;
      margin: 24px auto;
      padding: 0 16px;
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 18px;
    }}
    .card {{
      background: #141a2f;
      border: 1px solid #243050;
      border-radius: 12px;
      padding: 16px;
    }}
    h2 {{
      margin-top: 0;
      font-size: 1.05rem;
      letter-spacing: 0.02em;
    }}
    ol {{
      margin: 0;
      padding-left: 0;
      list-style: none;
      display: grid;
      gap: 8px;
    }}
    li {{
      background: #1a2340;
      border: 1px solid #2a3760;
      border-radius: 8px;
      padding: 8px 10px;
    }}
    .slot {{
      display: inline-block;
      width: 2ch;
      color: #7ec8ff;
      font-weight: 600;
    }}
    .field {{
      position: relative;
      min-height: 520px;
      overflow: hidden;
      background:
        radial-gradient(circle at 50% 72%, #2e6a3f 0%, #225233 45%, #1a3f27 100%);
    }}
    .diamond {{
      position: absolute;
      left: 50%;
      top: 58%;
      width: 240px;
      height: 240px;
      border: 3px solid #d8c39a;
      transform: translate(-50%, -50%) rotate(45deg);
      box-sizing: border-box;
    }}
    .pos {{
      position: absolute;
      background: rgba(11,16,32,0.85);
      border: 1px solid #4b5f97;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 0.82rem;
      white-space: nowrap;
      transform: translate(-50%, -50%);
    }}
    .label {{
      display: inline-block;
      color: #9ed2ff;
      font-weight: 700;
      margin-right: 6px;
    }}
    .lf {{ left: 18%; top: 24%; }}
    .cf {{ left: 50%; top: 16%; }}
    .rf {{ left: 82%; top: 24%; }}
    .ss {{ left: 39%; top: 40%; }}
    .b2 {{ left: 61%; top: 40%; }}
    .b3 {{ left: 30%; top: 52%; }}
    .b1 {{ left: 70%; top: 52%; }}
    .p  {{ left: 50%; top: 55%; }}
    .c  {{ left: 50%; top: 76%; }}
    @media (max-width: 860px) {{
      .wrap {{ grid-template-columns: 1fr; }}
      .field {{ min-height: 440px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="card">
      <h2>Batting Order (Module 4)</h2>
      <ol>
        {order_items}
      </ol>
    </section>
    <section class="card field">
      <h2>Defensive Diamond</h2>
      <div class="diamond"></div>
      <div class="pos lf"><span class="label">LF</span>{p("LF")}</div>
      <div class="pos cf"><span class="label">CF</span>{p("CF")}</div>
      <div class="pos rf"><span class="label">RF</span>{p("RF")}</div>
      <div class="pos ss"><span class="label">SS</span>{p("SS")}</div>
      <div class="pos b2"><span class="label">2B</span>{p("2B")}</div>
      <div class="pos b3"><span class="label">3B</span>{p("3B")}</div>
      <div class="pos b1"><span class="label">1B</span>{p("1B")}</div>
      <div class="pos p"><span class="label">P</span>{p("P")}</div>
      <div class="pos c"><span class="label">C</span>{p("C")}</div>
    </section>
  </div>
</body>
</html>
"""


def write_lineup_dashboard_html(
    batting_order: Sequence[str],
    position_assignment: Dict[str, str],
    output_path: str,
    *,
    title: str = "Module 4 Lineup Dashboard",
) -> Path:
    """Write dashboard HTML to disk and return path."""
    rendered = render_lineup_dashboard_html(
        batting_order, position_assignment, title=title
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return path
