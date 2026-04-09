"""
Browser-based external UI for Module 4 lineup + field visualization.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

REQUIRED_POSITIONS = ("C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH")


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
    outfield_profiles: Optional[Mapping[str, Mapping[str, float]]] = None,
    outfield_profiles_predicted: Optional[Mapping[str, Mapping[str, float]]] = None,
    defensive_profiles: Optional[Mapping[str, Mapping[str, float]]] = None,
    offensive_profiles: Optional[Mapping[str, float]] = None,
    eligibility_profiles: Optional[Mapping[str, Sequence[str]]] = None,
    pipeline_context: Optional[Mapping[str, Any]] = None,
) -> str:
    """Return a full HTML page showing batting order and baseball diamond."""
    _validate_inputs(batting_order, position_assignment)

    current_dh = position_assignment.get("DH", "")
    order_items_parts = []
    for i, name in enumerate(batting_order, start=1):
        badge = " <span class='role-badge'>DH</span>" if name == current_dh else ""
        order_items_parts.append(
            f"<li data-player='{html.escape(name)}'>"
            f"<span class='slot'>{i}.</span> "
            f"<span class='batter-name'>{html.escape(name)}</span>"
            f"{badge}"
            "</li>"
        )
    order_items = "\n".join(order_items_parts)

    def p(pos: str) -> str:
        return html.escape(position_assignment[pos])

    profiles_json = json.dumps(outfield_profiles or {}, ensure_ascii=False)
    predicted_profiles_json = json.dumps(outfield_profiles_predicted or {}, ensure_ascii=False)
    defensive_profiles_json = json.dumps(defensive_profiles or {}, ensure_ascii=False)
    offensive_profiles_json = json.dumps(offensive_profiles or {}, ensure_ascii=False)
    eligibility_profiles_json = json.dumps(eligibility_profiles or {}, ensure_ascii=False)

    module5_section = ""
    if module5_plan:
        recommendations = list(module5_plan.get("recommendations", []))
        if recommendations:
            recommendation_items = "\n".join(
                (
                    "<li>"
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
                "<tr>"
                f"<td>{html.escape(str(inning.get('inning', '?')))}</td>"
                f"<td>{html.escape(str(inning.get('half', 'tbd')))}</td>"
                f"<td>{html.escape(str(inning.get('objective', 'n/a')))}</td>"
                f"<td>{action_count}</td>"
                "</tr>"
            )
        inning_rows_html = "\n".join(inning_rows) or (
            "<tr><td colspan='4'>No inning plan generated.</td></tr>"
        )

        module5_section = f"""
    <section class="card module5">
      <h2>Adaptive Planning (Module 5)</h2>
      <ul class="recommendations">
        {recommendation_items}
      </ul>
      <h3>Multi-Inning Outlook</h3>
      <table>
        <thead>
          <tr><th>Inning</th><th>Half</th><th>Objective</th><th>Actions</th></tr>
        </thead>
        <tbody>
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
      max-width: 1240px;
      margin: 24px auto;
      padding: 0 16px;
      display: grid;
      grid-template-columns: minmax(300px, 340px) minmax(640px, 1fr);
      gap: 18px;
      align-items: start;
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
    .batter-name {{
      font-weight: 500;
    }}
    .role-badge {{
      display: inline-block;
      margin-left: 8px;
      padding: 1px 6px;
      border-radius: 999px;
      border: 1px solid #3d5892;
      color: #9ed2ff;
      background: #192746;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.03em;
    }}
    .lineup-card {{
      grid-column: 1;
      grid-row: 1;
    }}
    .field {{
      grid-column: 2;
      grid-row: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .field-visual {{
      position: relative;
      min-height: 520px;
      overflow: hidden;
      border: 1px solid #2a3760;
      border-radius: 10px;
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
    .defensive-slot {{
      cursor: grab;
      user-select: none;
      padding-right: 34px;
    }}
    .defensive-slot.dragging {{
      opacity: 0.72;
      border-color: #8cc6ff;
    }}
    .defensive-slot.drop-target {{
      border-color: #74b8ff;
      box-shadow: 0 0 0 2px rgba(116,184,255,0.25);
    }}
    .defensive-slot.locked {{
      border-color: #e0b85b;
      box-shadow: 0 0 0 2px rgba(224,184,91,0.25);
    }}
    .lock-btn {{
      position: absolute;
      right: 6px;
      top: 50%;
      transform: translateY(-50%);
      border: 1px solid #4a5f94;
      border-radius: 999px;
      background: #1b2846;
      color: #d8e3ff;
      font-size: 0.62rem;
      line-height: 1;
      padding: 3px 6px;
      cursor: pointer;
    }}
    .lock-btn.active {{
      border-color: #e0b85b;
      background: #5a451e;
      color: #ffe2a3;
    }}
    .ss {{ left: 39%; top: 40%; }}
    .b2 {{ left: 61%; top: 40%; }}
    .b3 {{ left: 30%; top: 52%; }}
    .b1 {{ left: 70%; top: 52%; }}
    .c  {{ left: 50%; top: 76%; }}
    .dh {{ left: 79%; top: 76%; }}
    .module5 {{
      grid-column: 1 / -1;
      grid-row: 2;
    }}
    .field-footer {{
      background: rgba(11,16,32,0.9);
      border: 1px solid #30416e;
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 0.88rem;
      line-height: 1.4;
    }}
    .field-footer .value {{
      color: #8fd1ff;
      font-weight: 700;
    }}
    .field-footer .value.conf-high {{
      color: #61d095;
    }}
    .field-footer .value.conf-medium {{
      color: #f0c45b;
    }}
    .field-footer .value.conf-low {{
      color: #f17a7a;
    }}
    .field-footer .hint {{
      color: #bdcae6;
      margin-top: 4px;
      font-size: 0.82rem;
    }}
    .mode-toggle {{
      margin-top: 8px;
      display: inline-flex;
      gap: 8px;
      align-items: center;
      border: 1px solid #30416e;
      border-radius: 999px;
      padding: 4px;
      background: rgba(11,16,32,0.7);
    }}
    .mode-toggle button {{
      border: 1px solid #3a4f82;
      background: #1a2340;
      color: #c8d6f3;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 0.78rem;
      cursor: pointer;
    }}
    .mode-toggle button.active {{
      background: #24406f;
      color: #eaf2ff;
      border-color: #5f93d8;
      font-weight: 600;
    }}
    .mode-label {{
      margin-top: 6px;
      color: #9ed2ff;
      font-size: 0.8rem;
    }}
    .predictive-toggle {{
      margin-top: 8px;
      color: #c7d5f1;
      font-size: 0.79rem;
      display: flex;
      align-items: center;
      gap: 7px;
    }}
    .predictive-toggle input {{
      accent-color: #74b8ff;
    }}
    .field-footer .explain {{
      margin-top: 6px;
      color: #9ed2ff;
      font-size: 0.8rem;
    }}
    .field-footer .subexplain {{
      margin-top: 3px;
      color: #a8b8db;
      font-size: 0.76rem;
    }}
    .field-footer .subexplain.conf-high {{
      color: #86dfae;
    }}
    .field-footer .subexplain.conf-medium {{
      color: #f2cf73;
    }}
    .field-footer .subexplain.conf-low {{
      color: #ff9a9a;
    }}
    .why-panel {{
      margin-top: 10px;
      border: 1px solid #30416e;
      border-radius: 10px;
      background: rgba(9, 14, 30, 0.9);
      padding: 10px 12px;
    }}
    .why-panel h4 {{
      margin: 0 0 8px;
      font-size: 0.86rem;
      color: #9ed2ff;
      letter-spacing: 0.02em;
    }}
    .why-list {{
      margin: 0;
      padding-left: 0;
      list-style: none;
      display: grid;
      gap: 4px;
      font-size: 0.8rem;
      color: #c6d2ef;
    }}
    .why-list li {{
      border: 1px solid #26355d;
      border-radius: 7px;
      background: #151f3b;
      padding: 6px 8px;
      line-height: 1.25;
    }}
    .why-score {{
      color: #8fd1ff;
      font-weight: 700;
    }}
    .recommendations {{
      margin: 0 0 12px;
      padding-left: 0;
      list-style: none;
      display: grid;
      gap: 8px;
    }}
    .recommendations li {{
      background: #1a2340;
      border: 1px solid #2a3760;
      border-radius: 8px;
      padding: 10px;
      line-height: 1.35;
    }}
    .recommendations span {{
      color: #c9d4ee;
      font-size: 0.9rem;
    }}
    h3 {{
      margin: 0 0 8px;
      font-size: 0.95rem;
      color: #bcd3ff;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }}
    th, td {{
      border: 1px solid #2a3760;
      padding: 7px 9px;
      text-align: left;
    }}
    th {{
      background: #1b2545;
      color: #9ed2ff;
      font-weight: 600;
    }}
    @media (max-width: 1040px) {{
      .wrap {{ grid-template-columns: 1fr; }}
      .lineup-card,
      .field,
      .module5 {{
        grid-column: 1;
        grid-row: auto;
      }}
      .field-visual {{ min-height: 440px; }}
    }}
  </style>
</head>
<body>
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
        Outfield Confidence: <span id="outfield-confidence" class="value">--</span>/100
        <div class="hint">Use LOCK on a position to freeze it. Dropping another player re-optimizes all unlocked positions.</div>
        <div id="outfield-subexplain" class="subexplain"></div>
        <div class="mode-toggle">
          <button id="mode-strict" type="button">Strict Mode</button>
          <button id="mode-free" type="button" class="active">Free Mode</button>
        </div>
        <label class="predictive-toggle">
          <input id="predictive-confidence" type="checkbox" checked />
          Use projected outfield fit for unplayed positions
        </label>
        <div id="mode-label" class="mode-label"></div>
        <div id="optimizer-explain" class="explain"></div>
        <div class="why-panel">
          <h4>Why This Move</h4>
          <ul id="why-move-list" class="why-list"></ul>
        </div>
      </div>
    </section>
{module5_section}
{pipeline_section}
  </div>
  <script>
    (function () {{
      const outfieldProfiles = {profiles_json};
      const outfieldPredictedProfiles = {predicted_profiles_json};
      const defensiveProfiles = {defensive_profiles_json};
      const offensiveProfiles = {offensive_profiles_json};
      const eligibilityProfiles = {eligibility_profiles_json};
      const allPositions = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"];
      const slots = Array.from(document.querySelectorAll(".defensive-slot"));
      const valueEl = document.getElementById("outfield-confidence");
      const outfieldSubEl = document.getElementById("outfield-subexplain");
      const explainEl = document.getElementById("optimizer-explain");
      const whyListEl = document.getElementById("why-move-list");
      const modeLabelEl = document.getElementById("mode-label");
      const strictBtn = document.getElementById("mode-strict");
      const freeBtn = document.getElementById("mode-free");
      const predictiveConfidenceEl = document.getElementById("predictive-confidence");
      const lockButtons = Array.from(document.querySelectorAll(".lock-btn"));
      let dragSourcePos = null;
      let strictMode = false;
      const lockedPositions = new Set();

      function getSlotByPos(pos) {{
        return document.querySelector('.defensive-slot[data-pos="' + pos + '"]');
      }}

      function getPlayerAt(pos) {{
        const slot = getSlotByPos(pos);
        if (!slot) return "";
        const playerEl = slot.querySelector(".player");
        return playerEl ? playerEl.textContent.trim() : "";
      }}

      function setPlayerAt(pos, player) {{
        const slot = getSlotByPos(pos);
        if (!slot) return;
        const playerEl = slot.querySelector(".player");
        if (playerEl) playerEl.textContent = player;
      }}

      function defensiveScore(player, pos) {{
        const score = defensiveProfiles[player] ? defensiveProfiles[player][pos] : undefined;
        const numeric = Number(score);
        return Number.isFinite(numeric) ? numeric : 0.0;
      }}

      function offensiveScore(player) {{
        const numeric = Number(offensiveProfiles[player]);
        return Number.isFinite(numeric) ? numeric : 0.0;
      }}

      function scorePlayerForPosition(player, pos) {{
        if (pos === "DH") return offensiveScore(player);
        return defensiveScore(player, pos);
      }}

      function isEligible(player, pos) {{
        if (!strictMode) return true;
        if (pos === "DH") return true;
        const allowed = eligibilityProfiles[player] || [];
        return allowed.includes(pos);
      }}

      function currentAssignment() {{
        const assignment = {{}};
        for (const pos of allPositions) {{
          assignment[pos] = getPlayerAt(pos);
        }}
        return assignment;
      }}

      function renderLocks() {{
        for (const slot of slots) {{
          const pos = slot.dataset.pos || "";
          const isLocked = lockedPositions.has(pos);
          slot.classList.toggle("locked", isLocked);
        }}
        for (const btn of lockButtons) {{
          const pos = btn.dataset.lockPos || "";
          const isLocked = lockedPositions.has(pos);
          btn.classList.toggle("active", isLocked);
          btn.textContent = isLocked ? "LOCKED" : "LOCK";
        }}
      }}

      function outfieldScore(player, pos) {{
        const played = Number(
          outfieldProfiles[player] ? outfieldProfiles[player][pos] : 0.0
        );
        const projected = Number(
          outfieldPredictedProfiles[player] ? outfieldPredictedProfiles[player][pos] : 0.0
        );
        const playedScore = Number.isFinite(played) ? played : 0.0;
        const projectedScore = Number.isFinite(projected) ? projected : 0.0;

        const usePredictive = predictiveConfidenceEl ? predictiveConfidenceEl.checked : true;
        if (!usePredictive) return playedScore;
        if (playedScore <= 0.0) return projectedScore;
        // Keep real-played value primary, but let projection influence.
        return 0.7 * playedScore + 0.3 * projectedScore;
      }}

      function updateOutfieldConfidence() {{
        const positions = ["LF", "CF", "RF"];
        const players = positions.map((pos) => getPlayerAt(pos));
        let currentTotal = 0.0;
        for (const pos of positions) {{
          const player = getPlayerAt(pos);
          currentTotal += outfieldScore(player, pos);
        }}

        // Normalize against the best OF arrangement achievable with these same three players.
        const permutations = [
          [players[0], players[1], players[2]],
          [players[0], players[2], players[1]],
          [players[1], players[0], players[2]],
          [players[1], players[2], players[0]],
          [players[2], players[0], players[1]],
          [players[2], players[1], players[0]],
        ];
        let bestTotal = 0.0;
        for (const perm of permutations) {{
          const score =
            outfieldScore(perm[0], "LF") +
            outfieldScore(perm[1], "CF") +
            outfieldScore(perm[2], "RF");
          if (score > bestTotal) bestTotal = score;
        }}

        const relativeFit =
          bestTotal > 0 ? (currentTotal / bestTotal) * 100.0 : 0.0;
        const absoluteFit = Math.max(0.0, Math.min((currentTotal / 300.0) * 100.0, 100.0));
        // Blend absolute quality and arrangement optimality so weak trios do not show 100.
        const confidence = 0.65 * absoluteFit + 0.35 * relativeFit;
        valueEl.textContent = confidence.toFixed(1);
        valueEl.classList.remove("conf-high", "conf-medium", "conf-low");
        if (outfieldSubEl) {{
          outfieldSubEl.classList.remove("conf-high", "conf-medium", "conf-low");
        }}
        let tierClass = "conf-low";
        if (confidence >= 85.0) {{
          tierClass = "conf-high";
        }} else if (confidence >= 60.0) {{
          tierClass = "conf-medium";
        }}
        valueEl.classList.add(tierClass);
        if (outfieldSubEl) {{
          outfieldSubEl.classList.add(tierClass);
          const tierLabel = tierClass === "conf-high"
            ? "High"
            : tierClass === "conf-medium"
            ? "Medium"
            : "Low";
          const predictiveLabel =
            predictiveConfidenceEl && predictiveConfidenceEl.checked
              ? "predictive-assisted"
              : "played-only";
          outfieldSubEl.textContent =
            tierLabel +
            " confidence (" +
            predictiveLabel +
            ") | " +
            "Current OF fit: " +
            currentTotal.toFixed(1) +
            " / 300.0"
            + " | Relative: " + relativeFit.toFixed(1)
            + " | Trio best: " + bestTotal.toFixed(1);
        }}
      }}

      function totalDefenseFitScore() {{
        let total = 0.0;
        for (const pos of allPositions) {{
          const player = getPlayerAt(pos);
          total += scorePlayerForPosition(player, pos);
        }}
        return total;
      }}

      function renderWhyThisMove() {{
        if (!whyListEl) return;
        const rows = [];
        for (const pos of allPositions) {{
          const player = getPlayerAt(pos);
          const score = scorePlayerForPosition(player, pos);
          const scoreLabel = pos === "DH" ? "offense" : "defense";
          rows.push(
            "<li><strong>" +
              pos +
              "</strong> -> " +
              player +
              " | " +
              scoreLabel +
              ": <span class='why-score'>" +
              score.toFixed(1) +
              "</span></li>"
          );
        }}
        whyListEl.innerHTML = rows.join("");
      }}

      function updateBattingLineupDHTag() {{
        const dhPlayer = getPlayerAt("DH");
        const lineupItems = Array.from(document.querySelectorAll("ol li[data-player]"));
        for (const li of lineupItems) {{
          const player = li.dataset.player || "";
          let badge = li.querySelector(".role-badge");
          if (player === dhPlayer) {{
            if (!badge) {{
              badge = document.createElement("span");
              badge.className = "role-badge";
              badge.textContent = "DH";
              li.appendChild(document.createTextNode(" "));
              li.appendChild(badge);
            }}
          }} else if (badge) {{
            badge.remove();
          }}
        }}
      }}

      function applyAssignment(assignment) {{
        for (const pos of allPositions) {{
          if (assignment[pos]) setPlayerAt(pos, assignment[pos]);
        }}
      }}

      function optimizeDefenseWithLockedPlayer(lockedPlayer, lockedPos) {{
        if (!lockedPlayer || !lockedPos) return;
        if (lockedPositions.has(lockedPos)) {{
          if (explainEl) {{
            explainEl.textContent = "Target position is locked. Unlock it first to modify.";
          }}
          return;
        }}
        const current = currentAssignment();
        const players = Array.from(new Set(Object.values(current).filter(Boolean)));
        const fixedAssignments = {{}};
        for (const pos of lockedPositions) {{
          if (pos === lockedPos) continue;
          const player = current[pos];
          if (player) fixedAssignments[pos] = player;
        }}
        const fixedPlayers = new Set(Object.values(fixedAssignments));
        if (fixedPlayers.has(lockedPlayer)) {{
          if (explainEl) {{
            explainEl.textContent =
              "Dragged player is already fixed in another locked position.";
          }}
          return;
        }}

        const remainingPlayers = players.filter(
          (p) => p !== lockedPlayer && !fixedPlayers.has(p)
        );
        const remainingPositions = allPositions.filter(
          (p) => p !== lockedPos && !(p in fixedAssignments)
        );

        const best = {{
          score: -Infinity,
          assignment: null,
        }};

        function backtrack(posIdx, availablePlayers, partial, runningScore) {{
          if (posIdx >= remainingPositions.length) {{
            if (runningScore > best.score) {{
              best.score = runningScore;
              best.assignment = Object.assign({{}}, partial);
            }}
            return;
          }}

          const pos = remainingPositions[posIdx];
          for (let i = 0; i < availablePlayers.length; i += 1) {{
            const player = availablePlayers[i];
            if (!isEligible(player, pos)) {{
              continue;
            }}
            partial[pos] = player;
            const nextPlayers = availablePlayers.slice(0, i).concat(availablePlayers.slice(i + 1));
            backtrack(
              posIdx + 1,
              nextPlayers,
              partial,
              runningScore + scorePlayerForPosition(player, pos),
            );
            delete partial[pos];
          }}
        }}

        backtrack(0, remainingPlayers, {{}}, 0.0);
        if (!best.assignment) {{
          if (explainEl) {{
            explainEl.textContent =
              "No valid reassignment found with eligibility constraints for that lock.";
          }}
          return;
        }}
        const optimized = Object.assign({{}}, fixedAssignments, best.assignment || {{}});
        optimized[lockedPos] = lockedPlayer;
        applyAssignment(optimized);
        updateBattingLineupDHTag();
        updateOutfieldConfidence();
        if (explainEl) {{
          explainEl.textContent =
            "Locked " +
            lockedPlayer +
            " at " +
            lockedPos +
            " | Total fit score: " +
            totalDefenseFitScore().toFixed(1);
        }}
        renderWhyThisMove();
      }}

      function clearDropStyles() {{
        for (const slot of slots) {{
          slot.classList.remove("drop-target");
          slot.classList.remove("dragging");
        }}
      }}

      function renderModeUI() {{
        if (!strictBtn || !freeBtn) return;
        strictBtn.classList.toggle("active", strictMode);
        freeBtn.classList.toggle("active", !strictMode);
        if (modeLabelEl) {{
          modeLabelEl.textContent = strictMode
            ? "Strict Mode: only eligible defensive positions are allowed."
            : "Free Mode: any player can be moved to any defensive position.";
        }}
      }}

      if (strictBtn) {{
        strictBtn.addEventListener("click", () => {{
          strictMode = true;
          renderModeUI();
        }});
      }}
      if (freeBtn) {{
        freeBtn.addEventListener("click", () => {{
          strictMode = false;
          renderModeUI();
        }});
      }}
      if (predictiveConfidenceEl) {{
        predictiveConfidenceEl.addEventListener("change", () => {{
          updateOutfieldConfidence();
        }});
      }}

      for (const slot of slots) {{
        slot.addEventListener("dragstart", (event) => {{
          dragSourcePos = slot.dataset.pos || null;
          if (dragSourcePos && lockedPositions.has(dragSourcePos)) {{
            event.preventDefault();
            if (explainEl) {{
              explainEl.textContent =
                "Source position is locked. Unlock it first to drag this player.";
            }}
            return;
          }}
          slot.classList.add("dragging");
          if (event.dataTransfer) {{
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData("text/plain", dragSourcePos || "");
          }}
        }});

        slot.addEventListener("dragover", (event) => {{
          event.preventDefault();
          slot.classList.add("drop-target");
          if (event.dataTransfer) event.dataTransfer.dropEffect = "move";
        }});

        slot.addEventListener("dragleave", () => {{
          slot.classList.remove("drop-target");
        }});

        slot.addEventListener("drop", (event) => {{
          event.preventDefault();
          const sourcePos = dragSourcePos || (event.dataTransfer ? event.dataTransfer.getData("text/plain") : "");
          const targetPos = slot.dataset.pos || "";
          const draggedPlayer = getPlayerAt(sourcePos);
          optimizeDefenseWithLockedPlayer(draggedPlayer, targetPos);
          clearDropStyles();
        }});

        slot.addEventListener("dragend", () => {{
          clearDropStyles();
          dragSourcePos = null;
        }});
      }}

      for (const btn of lockButtons) {{
        btn.addEventListener("click", (event) => {{
          event.stopPropagation();
          const pos = btn.dataset.lockPos || "";
          if (!pos) return;
          if (lockedPositions.has(pos)) {{
            lockedPositions.delete(pos);
          }} else {{
            lockedPositions.add(pos);
          }}
          renderLocks();
          if (explainEl) {{
            explainEl.textContent =
              lockedPositions.size > 0
                ? "Locked positions: " + Array.from(lockedPositions).sort().join(", ")
                : "No positions locked.";
          }}
        }});
      }}

      updateBattingLineupDHTag();
      updateOutfieldConfidence();
      renderWhyThisMove();
      renderModeUI();
      renderLocks();
      if (explainEl) {{
        explainEl.textContent =
          "Initial total fit score: " + totalDefenseFitScore().toFixed(1);
      }}
    }})();
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
    outfield_profiles: Optional[Mapping[str, Mapping[str, float]]] = None,
    outfield_profiles_predicted: Optional[Mapping[str, Mapping[str, float]]] = None,
    defensive_profiles: Optional[Mapping[str, Mapping[str, float]]] = None,
    offensive_profiles: Optional[Mapping[str, float]] = None,
    eligibility_profiles: Optional[Mapping[str, Sequence[str]]] = None,
    pipeline_context: Optional[Mapping[str, Any]] = None,
) -> Path:
    """Write dashboard HTML to disk and return path."""
    rendered = render_lineup_dashboard_html(
        batting_order,
        position_assignment,
        title=title,
        module5_plan=module5_plan,
        outfield_profiles=outfield_profiles,
        outfield_profiles_predicted=outfield_profiles_predicted,
        defensive_profiles=defensive_profiles,
        offensive_profiles=offensive_profiles,
        eligibility_profiles=eligibility_profiles,
        pipeline_context=pipeline_context,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return path
