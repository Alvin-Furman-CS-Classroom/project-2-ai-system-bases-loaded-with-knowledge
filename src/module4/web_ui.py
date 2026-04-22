"""
Browser-based external UI for Module 4 lineup + field visualization.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from module4.web_ui_script_v2 import build_dashboard_script
from module4.web_ui_styles import get_dashboard_css

REQUIRED_POSITIONS = ("C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH")


def _attr_escape(value: Any) -> str:
    """Escape text for use inside HTML double-quoted attributes."""
    return html.escape(str(value or ""), quote=True)


def _game_state_form_html(game_state: Mapping[str, Any]) -> str:
    """Markup for editable Module 5 game-state controls (live replan via local server)."""
    inning = int(game_state.get("inning", 1))
    half = str(game_state.get("half", "bottom")).strip().lower()
    if half not in ("top", "bottom"):
        half = "bottom"
    outs = max(0, min(2, int(game_state.get("outs", 0))))
    score_for = max(0, int(game_state.get("score_for", 0)))
    score_against = max(0, int(game_state.get("score_against", 0)))
    raw_bases = game_state.get("bases", [False, False, False])
    b_list = list(raw_bases) if isinstance(raw_bases, (list, tuple)) else [False, False, False]
    while len(b_list) < 3:
        b_list.append(False)
    subs_used = max(0, int(game_state.get("substitutions_used", 0)))
    subs_limit = max(0, int(game_state.get("substitutions_limit", 5)))
    top_sel = " selected" if half == "top" else ""
    bot_sel = " selected" if half == "bottom" else ""
    o0 = " selected" if outs == 0 else ""
    o1 = " selected" if outs == 1 else ""
    o2 = " selected" if outs == 2 else ""
    c1 = " checked" if bool(b_list[0]) else ""
    c2 = " checked" if bool(b_list[1]) else ""
    c3 = " checked" if bool(b_list[2]) else ""
    return f"""
      <div class="gs-form">
        <h3>Game state (editable)</h3>
        <p class="hint gs-hint">
          Adjust the situation and click <strong>Refresh plan</strong> to rerun Module 5 with the Python planner.
          Serve this page with
          <code>PYTHONPATH=src python3 demos/dashboard_plan_server.py</code>
          (then open the URL it prints).
        </p>
        <div class="gs-grid">
          <label>Inning <input id="gs-inning" type="number" min="1" max="18" value="{inning}" /></label>
          <label>Half
            <select id="gs-half">
              <option value="top"{top_sel}>Top</option>
              <option value="bottom"{bot_sel}>Bottom</option>
            </select>
          </label>
          <label>Outs
            <select id="gs-outs">
              <option value="0"{o0}>0</option>
              <option value="1"{o1}>1</option>
              <option value="2"{o2}>2</option>
            </select>
          </label>
          <label>Runs (us) <input id="gs-score-for" type="number" min="0" max="99" value="{score_for}" /></label>
          <label>Runs (them) <input id="gs-score-against" type="number" min="0" max="99" value="{score_against}" /></label>
          <div class="gs-bases">
            <span class="gs-bases-label">Bases</span>
            <label><input id="gs-base-1" type="checkbox"{c1} /> 1st</label>
            <label><input id="gs-base-2" type="checkbox"{c2} /> 2nd</label>
            <label><input id="gs-base-3" type="checkbox"{c3} /> 3rd</label>
          </div>
          <label>Subs used <input id="gs-subs-used" type="number" min="0" max="25" value="{subs_used}" /></label>
          <label>Subs limit <input id="gs-subs-limit" type="number" min="0" max="25" value="{subs_limit}" /></label>
        </div>
        <div class="gs-actions">
          <button type="button" id="m5-refresh-plan" class="gs-btn">Refresh plan</button>
          <label class="gs-auto"><input id="gs-auto-refresh" type="checkbox" /> Auto-refresh on change</label>
        </div>
        <p id="m5-replan-status" class="hint"></p>
      </div>
    """


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
    module5_plan: Optional[Mapping[str, Any]] = None,
    defensive_profiles: Optional[Mapping[str, Mapping[str, float]]] = None,
    defensive_profiles_predicted: Optional[Mapping[str, Mapping[str, float]]] = None,
    offensive_profiles: Optional[Mapping[str, float]] = None,
    eligibility_profiles: Optional[Mapping[str, Sequence[str]]] = None,
    pipeline_context: Optional[Mapping[str, Any]] = None,
    replan_context: Optional[Mapping[str, Any]] = None,
) -> str:
    """Return a full HTML page showing batting order and baseball diamond."""
    _validate_inputs(batting_order, position_assignment)

    current_dh = position_assignment.get("DH", "")
    order_items_parts = []
    for i, name in enumerate(batting_order, start=1):
        badge = " <span class='role-badge'>DH</span>" if name == current_dh else ""
        order_items_parts.append(
            f"<li class=\"lineup-row\" data-player=\"{html.escape(name)}\" tabindex=\"0\" role=\"button\">"
            f"<span class='slot'>{i}.</span> "
            f"<span class='batter-name'>{html.escape(name)}</span>"
            f"{badge}"
            "</li>"
        )
    order_items = "\n".join(order_items_parts)

    def p(pos: str) -> str:
        return html.escape(position_assignment[pos])

    defensive_profiles_json = json.dumps(defensive_profiles or {}, ensure_ascii=False)
    defensive_profiles_predicted_json = json.dumps(
        defensive_profiles_predicted or {}, ensure_ascii=False
    )
    offensive_profiles_json = json.dumps(offensive_profiles or {}, ensure_ascii=False)
    eligibility_profiles_json = json.dumps(eligibility_profiles or {}, ensure_ascii=False)

    module5_section = ""
    if module5_plan:
        recommendations = list(module5_plan.get("recommendations", []))
        if recommendations:
            recommendation_items = "\n".join(
                (
                    "<li class=\"rec-item\" tabindex=\"0\" role=\"button\" "
                    f"data-bench-player=\"{_attr_escape(rec.get('bench_player'))}\" "
                    f"data-target-player=\"{_attr_escape(rec.get('target_player'))}\" "
                    f"data-position=\"{_attr_escape(rec.get('position'))}\">"
                    f"<strong>{html.escape(str(rec.get('action_type', 'action')))}</strong> "
                    f"(priority {html.escape(str(rec.get('priority', '?')))}, "
                    f"confidence {float(rec.get('confidence', 0.0)):.2f})<br/>"
                    f"<span>{html.escape(str(rec.get('reason', 'No rationale provided.')))}</span>"
                    "</li>"
                )
                for rec in recommendations
            )
        else:
            recommendation_items = (
                "<li><strong>No immediate recommendations.</strong> "
                "<span>Module 5 did not flag a high-priority action for this state.</span></li>"
            )

        inning_rows = []
        for inning in module5_plan.get("multi_inning_plan", []):
            action_count = len(inning.get("recommended_actions", []))
            inning_rows.append(
                "<tr class=\"inning-row\" tabindex=\"0\" role=\"row\">"
                f"<td>{html.escape(str(inning.get('inning', '?')))}</td>"
                f"<td>{html.escape(str(inning.get('half', 'tbd')))}</td>"
                f"<td>{html.escape(str(inning.get('objective', 'n/a')))}</td>"
                f"<td>{action_count}</td>"
                "</tr>"
            )
        inning_rows_html = "\n".join(inning_rows) or (
            "<tr><td colspan='4'>No inning plan generated.</td></tr>"
        )

        gs_form = ""
        if replan_context and isinstance(replan_context.get("game_state"), Mapping):
            gs_form = _game_state_form_html(replan_context["game_state"])

        module5_section = f"""
    <section class="card module5" id="module5-root">
      <h2>Adaptive Planning (Module 5)</h2>
      {gs_form}
      <h3>Bench Player Scores</h3>
      <div class="bench-table-wrap">
        <table id="bench-score-table">
          <thead>
            <tr>
              <th>Player</th>
              <th>Roles</th>
              <th>OFF (DH)</th>
              <th>C</th>
              <th>1B</th>
              <th>2B</th>
              <th>3B</th>
              <th>SS</th>
              <th>LF</th>
              <th>CF</th>
              <th>RF</th>
            </tr>
          </thead>
          <tbody id="bench-score-body">
            <tr><td colspan="11">Bench score table will load from planner context.</td></tr>
          </tbody>
        </table>
      </div>
      <ul id="m5-recommendations" class="recommendations">
        {recommendation_items}
      </ul>
      <h3>Multi-Inning Outlook</h3>
      <table>
        <thead>
          <tr><th>Inning</th><th>Half</th><th>Objective</th><th>Actions</th></tr>
        </thead>
        <tbody id="m5-inning-body">
          {inning_rows_html}
        </tbody>
      </table>
    </section>
"""

    pipeline_section = ""
    if pipeline_context:
        sources = pipeline_context.get("data_sources", {})
        pipeline_section = f"""
    <section class="card module5">
      <h2>Pipeline Connections</h2>
      <ul class="recommendations">
        <li><strong>Module 1 -> Offensive scores:</strong> {int(pipeline_context.get("module1_players_scored", 0))} players</li>
        <li><strong>Module 2 -> Defensive scores:</strong> {int(pipeline_context.get("module2_players_scored", 0))} players</li>
        <li><strong>Module 3 -> Assignment:</strong> {int(pipeline_context.get("module3_positions_assigned", 0))} positions solved</li>
        <li><strong>Module 4 -> Batting optimization:</strong> fitness {float(pipeline_context.get("module4_best_fitness", 0.0)):.3f}, generations {int(pipeline_context.get("module4_generations_run", 0))}</li>
        <li><strong>Module 5 -> Planning:</strong> {int(pipeline_context.get("module5_recommendations", 0))} recommendations</li>
      </ul>
      <h3>Data Sources</h3>
      <table>
        <tbody>
          <tr><td>Matchup stats (M1/M4)</td><td>{html.escape(str(sources.get("matchup_stats", "")))}</td></tr>
          <tr><td>Defensive stats (M2/M3)</td><td>{html.escape(str(sources.get("defensive_stats", "")))}</td></tr>
          <tr><td>Pipeline seed</td><td>{html.escape(str(pipeline_context.get("seed", "")))}</td></tr>
        </tbody>
      </table>
    </section>
"""

    replan_json_script = ""
    if replan_context:
        replan_json_script = (
            f'  <script type="application/json" id="replan-context">'
            f"{json.dumps(replan_context, ensure_ascii=False)}"
            f"</script>\n"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
{get_dashboard_css()}
  </style>
</head>
<body>
{replan_json_script}
  <header class="site-header" role="banner">
    <div class="site-header-inner">
      <h1 class="site-title">{html.escape(title)}</h1>
      <span class="site-tagline">Batting order · field · planning</span>
    </div>
  </header>
  <div class="wrap">
    <section class="card lineup-card">
      <h2>Batting Order (Module 4)</h2>
      <ol>
        {order_items}
      </ol>
    </section>
    <section class="card field">
      <h2>Defensive Diamond</h2>
      <div class="field-visual">
        <div class="diamond"></div>
        <div class="pos lf defensive-slot" data-pos="LF" draggable="true"><span class="label">LF</span><span class="player">{p("LF")}</span><button class="lock-btn" data-lock-pos="LF" type="button">LOCK</button></div>
        <div class="pos cf defensive-slot" data-pos="CF" draggable="true"><span class="label">CF</span><span class="player">{p("CF")}</span><button class="lock-btn" data-lock-pos="CF" type="button">LOCK</button></div>
        <div class="pos rf defensive-slot" data-pos="RF" draggable="true"><span class="label">RF</span><span class="player">{p("RF")}</span><button class="lock-btn" data-lock-pos="RF" type="button">LOCK</button></div>
        <div class="pos ss defensive-slot" data-pos="SS" draggable="true"><span class="label">SS</span><span class="player">{p("SS")}</span><button class="lock-btn" data-lock-pos="SS" type="button">LOCK</button></div>
        <div class="pos b2 defensive-slot" data-pos="2B" draggable="true"><span class="label">2B</span><span class="player">{p("2B")}</span><button class="lock-btn" data-lock-pos="2B" type="button">LOCK</button></div>
        <div class="pos b3 defensive-slot" data-pos="3B" draggable="true"><span class="label">3B</span><span class="player">{p("3B")}</span><button class="lock-btn" data-lock-pos="3B" type="button">LOCK</button></div>
        <div class="pos b1 defensive-slot" data-pos="1B" draggable="true"><span class="label">1B</span><span class="player">{p("1B")}</span><button class="lock-btn" data-lock-pos="1B" type="button">LOCK</button></div>
        <div class="pos c defensive-slot" data-pos="C" draggable="true"><span class="label">C</span><span class="player">{p("C")}</span><button class="lock-btn" data-lock-pos="C" type="button">LOCK</button></div>
        <div class="pos dh defensive-slot" data-pos="DH" draggable="true"><span class="label">DH</span><span class="player">{p("DH")}</span><button class="lock-btn" data-lock-pos="DH" type="button">LOCK</button></div>
      </div>
      <div class="field-footer">
        <div class="placement-metric" aria-describedby="lineup-defense-subexplain">
          <div class="placement-metric-title">Shuffle efficiency (same 9 players)</div>
          <div id="lineup-change-compare" class="lineup-compare" aria-live="polite">
            <p class="lineup-compare-placeholder">When the field changes, a before → after breakdown and fit totals will appear here.</p>
          </div>
          <div class="confidence-row placement-metric-scoreline">
            <span class="placement-metric-score-label">Match to best possible total:</span>
            <span id="lineup-defense-confidence" class="value" title="100 = current total equals best permutation total for this roster.">--</span><span class="placement-metric-unit">/100</span>
          </div>
          <div id="lineup-defense-subexplain" class="subexplain placement-metric-detail"></div>
        </div>
        <div class="hint">Use LOCK on a position to freeze it. Dropping another player re-optimizes all unlocked positions.</div>
        <div class="field-actions">
          <div class="mode-toggle">
            <button id="mode-strict" type="button">Strict Mode</button>
            <button id="mode-free" type="button" class="active">Free Mode</button>
          </div>
          <button id="dashboard-reset" type="button" class="btn-reset">Reset</button>
        </div>
        <label class="predictive-toggle">
          Unavailable natural position
          <select id="unavailable-position">
            <option value="">None</option>
            <option value="C">C</option>
            <option value="1B">1B</option>
            <option value="2B">2B</option>
            <option value="3B">3B</option>
            <option value="SS">SS</option>
            <option value="LF">LF</option>
            <option value="CF">CF</option>
            <option value="RF">RF</option>
          </select>
        </label>
        <div id="mode-label" class="mode-label"></div>
        <div id="optimizer-explain" class="explain"></div>
        <div class="why-panel">
          <h4>Why This Move</h4>
          <ul id="why-move-list" class="why-list"></ul>
        </div>
        <div id="player-inspector" class="player-inspector">
          <h4>Player focus</h4>
          <p class="hint inspector-body">
            Click a batter in the lineup, a player name on the diamond, or a Module 5 recommendation to cross-highlight and see scores.
          </p>
        </div>
      </div>
    </section>
{module5_section}
{pipeline_section}
  </div>
  <script>
{build_dashboard_script(
    defensive_profiles_json=defensive_profiles_json,
    defensive_profiles_predicted_json=defensive_profiles_predicted_json,
    offensive_profiles_json=offensive_profiles_json,
    eligibility_profiles_json=eligibility_profiles_json,
)}
  </script>
</body>
</html>
"""


def write_lineup_dashboard_html(
    batting_order: Sequence[str],
    position_assignment: Dict[str, str],
    output_path: str,
    *,
    title: str = "Module 4 Lineup Dashboard",
    module5_plan: Optional[Mapping[str, Any]] = None,
    defensive_profiles: Optional[Mapping[str, Mapping[str, float]]] = None,
    defensive_profiles_predicted: Optional[Mapping[str, Mapping[str, float]]] = None,
    offensive_profiles: Optional[Mapping[str, float]] = None,
    eligibility_profiles: Optional[Mapping[str, Sequence[str]]] = None,
    pipeline_context: Optional[Mapping[str, Any]] = None,
    replan_context: Optional[Mapping[str, Any]] = None,
) -> Path:
    """Write dashboard HTML to disk and return path."""
    rendered = render_lineup_dashboard_html(
        batting_order,
        position_assignment,
        title=title,
        module5_plan=module5_plan,
        defensive_profiles=defensive_profiles,
        defensive_profiles_predicted=defensive_profiles_predicted,
        offensive_profiles=offensive_profiles,
        eligibility_profiles=eligibility_profiles,
        pipeline_context=pipeline_context,
        replan_context=replan_context,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return path
