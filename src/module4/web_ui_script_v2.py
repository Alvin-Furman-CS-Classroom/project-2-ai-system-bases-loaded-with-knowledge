"""
Client-side script for the Module 4 lineup dashboard (diamond drag-drop, Module 5 replan).
"""

from __future__ import annotations


def build_dashboard_script(
    *,
    defensive_profiles_json: str,
    defensive_profiles_predicted_json: str,
    offensive_profiles_json: str,
    eligibility_profiles_json: str,
) -> str:
    """Return the inline script body (IIFE) with profile JSON injected."""
    return """    (function () {{
      const defensiveProfiles = __DEFENSIVE_PROFILES_JSON__;
      const defensivePredictedProfiles = __DEFENSIVE_PROFILES_PREDICTED_JSON__;
      const offensiveProfiles = __OFFENSIVE_PROFILES_JSON__;
      const eligibilityProfiles = __ELIGIBILITY_PROFILES_JSON__;
      const allPositions = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"];
      const slots = Array.from(document.querySelectorAll(".defensive-slot"));
      const lineupDefenseEl = document.getElementById("lineup-defense-confidence");
      const lineupDefenseSubEl = document.getElementById("lineup-defense-subexplain");
      const lineupCompareEl = document.getElementById("lineup-change-compare");
      const explainEl = document.getElementById("optimizer-explain");
      const whyListEl = document.getElementById("why-move-list");
      const modeLabelEl = document.getElementById("mode-label");
      const strictBtn = document.getElementById("mode-strict");
      const freeBtn = document.getElementById("mode-free");
      const unavailablePosEl = document.getElementById("unavailable-position");
      const lockButtons = Array.from(document.querySelectorAll(".lock-btn"));
      const inspectorEl = document.getElementById("player-inspector");
      const lineupRows = Array.from(document.querySelectorAll(".lineup-card ol li[data-player]"));
      const module5Root = document.getElementById("module5-root");
      const replanContextEl = document.getElementById("replan-context");
      let replanContext = {{}};
      if (replanContextEl && replanContextEl.textContent) {{
        try {{
          replanContext = JSON.parse(replanContextEl.textContent);
        }} catch (err) {{
          replanContext = {{}};
        }}
      }}
      let dragSourcePos = null;
      let strictMode = false;
      const lockedPositions = new Set();
      let lastFocusedPlayer = null;
      let inactivePlayer = "";
      let injectedReplacementPlayer = "";
      let inactiveForPosition = "";
      const originalAssignment = {};
      for (const pos of allPositions) {{
        const slot = document.querySelector('.defensive-slot[data-pos="' + pos + '"]');
        const playerEl = slot ? slot.querySelector(".player") : null;
        originalAssignment[pos] = playerEl ? playerEl.textContent.trim() : "";
      }}
      const originalLineupOrder = lineupRows.map((li) => li.dataset.player || "");

      function getUnavailablePosition() {{
        const raw = unavailablePosEl ? unavailablePosEl.value : "";
        return allPositions.includes(raw) && raw !== "DH" ? raw : "";
      }}

      function getBenchCandidates() {{
        const bench = Array.isArray(replanContext.bench_players) ? replanContext.bench_players : [];
        return bench
          .map((b) => (b && b.name ? String(b.name).trim() : ""))
          .filter(Boolean);
      }}

      function ensureBenchProfiles(playerName, unavailablePos) {{
        if (!playerName) return;
        if (!Object.prototype.hasOwnProperty.call(offensiveProfiles, playerName)) {{
          offensiveProfiles[playerName] = Number(
            (replanContext.offensive_scores && replanContext.offensive_scores[playerName]) || 50.0
          );
        }}
        if (!Object.prototype.hasOwnProperty.call(defensiveProfiles, playerName)) {{
          defensiveProfiles[playerName] = {{}};
        }}
        if (!Object.prototype.hasOwnProperty.call(defensivePredictedProfiles, playerName)) {{
          defensivePredictedProfiles[playerName] = {{}};
        }}

        for (const pos of allPositions) {{
          if (pos === "DH") continue;
          if (!Object.prototype.hasOwnProperty.call(defensiveProfiles[playerName], pos)) {{
            defensiveProfiles[playerName][pos] = Number(
              (replanContext.defensive_scores && replanContext.defensive_scores[playerName]) || 50.0
            );
          }}
          if (!Object.prototype.hasOwnProperty.call(defensivePredictedProfiles[playerName], pos)) {{
            defensivePredictedProfiles[playerName][pos] = Number(defensiveProfiles[playerName][pos]);
          }}
        }}

        if (!Object.prototype.hasOwnProperty.call(eligibilityProfiles, playerName)) {{
          const roleSource = (Array.isArray(replanContext.bench_players) ? replanContext.bench_players : [])
            .find((b) => b && b.name === playerName);
          const roles = Array.isArray(roleSource && roleSource.roles) ? roleSource.roles : [];
          const allowed = new Set(["DH"]);
          for (const role of roles) {{
            const norm = String(role || "").trim().toUpperCase();
            if (allPositions.includes(norm) && norm !== "DH") allowed.add(norm);
          }}
          eligibilityProfiles[playerName] = Array.from(allowed);
        }}
      }}

      function hydrateBenchProfiles(unavailablePos) {{
        const benchNames = getBenchCandidates();
        for (const name of benchNames) ensureBenchProfiles(name, unavailablePos || "");
      }}

      function hydrateCurrentAssignmentProfiles(unavailablePos) {{
        for (const pos of allPositions) {{
          const player = getPlayerAt(pos);
          if (player) ensureBenchProfiles(player, unavailablePos || "");
        }}
      }}

      function replacePlayerEverywhere(oldName, newName) {{
        if (!oldName || !newName || oldName === newName) return;
        for (const pos of allPositions) {{
          if (getPlayerAt(pos) === oldName) setPlayerAt(pos, newName);
        }}
        for (const li of lineupRows) {{
          if ((li.dataset.player || "") === oldName) {{
            li.dataset.player = newName;
            const nameEl = li.querySelector(".batter-name");
            if (nameEl) nameEl.textContent = newName;
          }}
        }}
      }}

      function chooseBenchReplacement(unavailablePos, outPlayer) {{
        const currentPlayers = new Set(Object.values(currentAssignment()).filter(Boolean));
        const benchNames = getBenchCandidates().filter((name) => !currentPlayers.has(name) && name !== outPlayer);
        if (benchNames.length === 0) return "";
        const basePlayers = Array.from(currentPlayers).filter((name) => name !== outPlayer);
        const emergencyPenalty = 0.75;

        function scoreForPos(player, pos) {{
          if (player === outPlayer) return -1000.0;
          if (pos === "DH") return offensiveScore(player);
          const base = defensiveScore(player, pos);
          if (pos === unavailablePos && unavailablePos) {{
            const allowed = eligibilityProfiles[player] || [];
            const isNatural = allowed.includes(unavailablePos);
            if (!isNatural) {{
              const predicted = defensiveScorePredicted(player, unavailablePos);
              const emergencyScore = predicted > 0.0 ? predicted : base;
              return emergencyPenalty * emergencyScore;
            }}
            return base;
          }}
          return base;
        }}

        function eligibleForPos(player, pos) {{
          if (player === outPlayer) return false;
          if (pos === "DH") return true;
          if (pos === unavailablePos && unavailablePos) {{
            return true;
          }}
          // During replacement simulation, allow out-of-position assignments so
          // we choose the candidate that maximizes total lineup fit.
          return true;
        }}

        function bestAssignmentScore(playerPool) {{
          const players = Array.from(playerPool);
          if (players.length !== allPositions.length) return -Infinity;
          let best = -Infinity;

          function backtrack(posIdx, availablePlayers, runningScore) {{
            if (posIdx >= allPositions.length) {{
              if (runningScore > best) best = runningScore;
              return;
            }}
            const pos = allPositions[posIdx];
            for (let i = 0; i < availablePlayers.length; i += 1) {{
              const player = availablePlayers[i];
              if (!eligibleForPos(player, pos)) continue;
              const next = availablePlayers.slice(0, i).concat(availablePlayers.slice(i + 1));
              backtrack(posIdx + 1, next, runningScore + scoreForPos(player, pos));
            }}
          }}

          backtrack(0, players, 0.0);
          return best;
        }}

        let bestName = "";
        let bestTotal = -Infinity;
        for (const name of benchNames) {{
          ensureBenchProfiles(name, unavailablePos);
          const pool = basePlayers.concat(name);
          const total = bestAssignmentScore(pool);
          if (Number.isFinite(total) && total > bestTotal) {{
            bestTotal = total;
            bestName = name;
          }}
        }}
        return bestName;
      }}

      function applyUnavailablePlayerReplacement() {{
        const unavailablePos = getUnavailablePosition();
        hydrateBenchProfiles(unavailablePos);
        hydrateCurrentAssignmentProfiles(unavailablePos);
        if (!unavailablePos) {{
          inactivePlayer = "";
          injectedReplacementPlayer = "";
          inactiveForPosition = "";
          return true;
        }}
        if (inactivePlayer && inactiveForPosition === unavailablePos) return true;
        if (inactivePlayer && inactiveForPosition !== unavailablePos) {{
          inactivePlayer = "";
          injectedReplacementPlayer = "";
          inactiveForPosition = "";
        }}

        const outPlayer = getPlayerAt(unavailablePos);
        if (!outPlayer) return false;
        const replacement = chooseBenchReplacement(unavailablePos, outPlayer);
        if (!replacement) {{
          if (explainEl) {{
            explainEl.textContent =
              "No bench replacement available for unavailable " + unavailablePos + ".";
          }}
          return false;
        }}
        inactivePlayer = outPlayer;
        injectedReplacementPlayer = replacement;
        inactiveForPosition = unavailablePos;
        replacePlayerEverywhere(outPlayer, replacement);
        return true;
      }}

      function restoreOriginalState() {{
        inactivePlayer = "";
        injectedReplacementPlayer = "";
        inactiveForPosition = "";
        lockedPositions.clear();
        for (const pos of allPositions) {{
          if (originalAssignment[pos]) setPlayerAt(pos, originalAssignment[pos]);
        }}
        for (let i = 0; i < lineupRows.length; i += 1) {{
          const li = lineupRows[i];
          const player = originalLineupOrder[i] || "";
          if (!player) continue;
          li.dataset.player = player;
          const nameEl = li.querySelector(".batter-name");
          if (nameEl) nameEl.textContent = player;
        }}
        renderLocks();
      }}

      function resetDashboardToInitial() {{
        if (unavailablePosEl) unavailablePosEl.value = "";
        restoreOriginalState();
        strictMode = false;
        renderModeUI();
        hydrateBenchProfiles("");
        hydrateCurrentAssignmentProfiles("");
        renderBenchScoreTable();
        updateBattingLineupDHTag();
        lastFocusedPlayer = null;
        clearSelectionHighlights();
        renderInspectorPrimary("");
        const snap = cloneAssignment();
        const shuffled = applyBestShuffleIfBelowPerfect();
        updateOverallDefenseConfidence();
        renderLineupCompare(snap, cloneAssignment(), {{ kind: "load" }});
        renderWhyThisMove();
        if (explainEl) {{
          explainEl.textContent =
            "Dashboard reset. Total fit score: " + totalDefenseFitScore().toFixed(1) +
            (shuffled ? " (auto-shuffle improved placement among the same nine.)" : "");
        }}
        refreshFocusAfterAssignment();
      }}

      function clearSelectionHighlights() {{
        for (const li of lineupRows) li.classList.remove("highlighted");
        for (const slot of slots) slot.classList.remove("highlighted");
        document.querySelectorAll("#m5-recommendations .rec-item").forEach((el) => {{
          el.classList.remove("active");
        }});
      }}

      function highlightPlayerEverywhere(player) {{
        if (!player) return;
        for (const li of lineupRows) {{
          if ((li.dataset.player || "") === player) li.classList.add("highlighted");
        }}
        for (const pos of allPositions) {{
          if (getPlayerAt(pos) === player) {{
            const slot = getSlotByPos(pos);
            if (slot) slot.classList.add("highlighted");
          }}
        }}
      }}

      function positionsForPlayer(player) {{
        const out = [];
        for (const pos of allPositions) {{
          if (getPlayerAt(pos) === player) out.push(pos);
        }}
        return out;
      }}

      function renderInspectorPrimary(player) {{
        if (!inspectorEl) return;
        if (!player) {{
          inspectorEl.innerHTML =
            "<h4>Player focus</h4>" +
            "<p class=\\"hint inspector-body\\">" +
            "Click a batter in the lineup, a player name on the diamond, or a Module 5 recommendation.</p>";
          return;
        }}
        const off = offensiveScore(player);
        const posList = positionsForPlayer(player);
        const offLabel = Object.prototype.hasOwnProperty.call(offensiveProfiles, player)
          ? off.toFixed(1)
          : "—";
        const defMap = defensiveProfiles[player] || {{}};
        const defLines = Object.keys(defMap)
          .sort()
          .map((pos) => "<div><span class=\\"inspector-pos\\">" + pos + "</span>: " + Number(defMap[pos]).toFixed(1) + "</div>")
          .join("");
        const posSummary = posList.length > 0 ? posList.join(", ") : "(not on diamond in current assignment)";
        inspectorEl.innerHTML =
          "<h4>Player focus</h4>" +
          "<div class=\\"inspector-name\\">" + player + "</div>" +
          "<div class=\\"inspector-grid\\">" +
          "<div><span class=\\"inspector-pos\\">Module 1 offense</span>: " + offLabel + "</div>" +
          "<div><span class=\\"inspector-pos\\">Current positions</span>: " + posSummary + "</div>" +
          (defLines
            ? "<div style=\\"margin-top:6px\\"><span class=\\"inspector-pos\\">Module 2 defense by position</span></div>" + defLines
            : "<div><span class=\\"inspector-pos\\">Module 2 defense</span>: —</div>") +
          "</div>";
      }}

      function renderInspectorRecommendation(bench, target, position) {{
        if (!inspectorEl) return;
        const parts = [];
        parts.push("<h4>Recommendation focus</h4><div class=\\"inspector-grid\\">");
        if (bench) parts.push("<div><span class=\\"inspector-pos\\">Bench / sub</span>: " + bench + "</div>");
        if (target) parts.push("<div><span class=\\"inspector-pos\\">On-field target</span>: " + target + "</div>");
        if (position) parts.push("<div><span class=\\"inspector-pos\\">Position</span>: " + position + "</div>");
        parts.push("<div class=\\"hint\\" style=\\"margin-top:8px\\">Highlighted players match this action where they appear in the lineup or on the diamond.</div></div>");
        inspectorEl.innerHTML = parts.join("");
      }}

      function renderInspectorInningSummary(cells) {{
        if (!inspectorEl || !cells || cells.length < 4) return;
        const inn = cells[0].textContent.trim();
        const half = cells[1].textContent.trim();
        const objective = cells[2].textContent.trim();
        const actions = cells[3].textContent.trim();
        inspectorEl.innerHTML =
          "<h4>Inning window</h4>" +
          "<div class=\\"inspector-grid\\">" +
          "<div><span class=\\"inspector-pos\\">Inning</span>: " + inn + " (" + half + ")</div>" +
          "<div><span class=\\"inspector-pos\\">Objective</span>: " + objective + "</div>" +
          "<div><span class=\\"inspector-pos\\">Planned actions</span>: " + actions + "</div>" +
          "</div><p class=\\"hint\\" style=\\"margin-top:8px\\">Use the Adaptive Planning list above for full rationale.</p>";
      }}

      function activateLineupPlayer(player) {{
        lastFocusedPlayer = player || null;
        clearSelectionHighlights();
        highlightPlayerEverywhere(player);
        renderInspectorPrimary(player);
      }}

      function activateFieldPlayer(player) {{
        lastFocusedPlayer = player || null;
        clearSelectionHighlights();
        highlightPlayerEverywhere(player);
        renderInspectorPrimary(player);
      }}

      function refreshFocusAfterAssignment() {{
        if (!lastFocusedPlayer) return;
        clearSelectionHighlights();
        highlightPlayerEverywhere(lastFocusedPlayer);
        renderInspectorPrimary(lastFocusedPlayer);
      }}

      function escapeHtml(str) {{
        return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
      }}

      function cloneAssignment() {{
        const a = {{}};
        for (const pos of allPositions) a[pos] = getPlayerAt(pos);
        return a;
      }}

      function totalFitForAssignment(ass) {{
        let t = 0.0;
        for (const pos of allPositions) {{
          const pl = ass[pos];
          if (!pl) continue;
          t += scorePlayerForPosition(pl, pos);
        }}
        return t;
      }}

      function diffAssignmentPositions(before, after) {{
        const out = [];
        for (const pos of allPositions) {{
          if (before[pos] !== after[pos]) out.push(pos);
        }}
        return out;
      }}

      function renderLineupCompare(before, after, meta) {{
        if (!lineupCompareEl) return;
        const bFit = totalFitForAssignment(before);
        const aFit = totalFitForAssignment(after);
        const diffPos = diffAssignmentPositions(before, after);
        if (diffPos.length === 0 && Math.abs(aFit - bFit) < 0.05) {{
          lineupCompareEl.innerHTML =
            "<p class=\\"lineup-compare-note\\">No defensive positions changed in this step.</p>";
          return;
        }}

        const k = meta && meta.kind ? meta.kind : "shuffle";
        let intro = "";
        if (k === "load") {{
          intro =
            "<p class=\\"lineup-compare-intro\\">Compared to the <strong>original</strong> field loaded on this page, the layout below is the best reordering of the <strong>same nine players</strong> for total fit (Module 2 defense + Module 1 offense at DH), honoring locks and Strict/Free rules.</p>";
        }} else if (k === "drag") {{
          const pl = escapeHtml(meta.player || "");
          const tp = escapeHtml(meta.targetPos || "");
          intro =
            "<p class=\\"lineup-compare-intro\\">You moved <strong>" +
            pl +
            "</strong> to <strong>" +
            tp +
            "</strong>. After re-optimizing the other unlocked spots, this field is the best full assignment the dashboard can build for these nine under the current rules.</p>";
        }} else if (k === "unavailable") {{
          const pp = escapeHtml(meta.position || "");
          intro =
            "<p class=\\"lineup-compare-intro\\">With <strong>" +
            pp +
            "</strong> treated as unavailable for the natural starter, the bench swap and reshuffle change the defense versus the lineup <strong>before</strong> this adjustment.</p>";
        }} else if (k === "mode") {{
          const m = meta.strict ? "Strict" : "Free";
          intro =
            "<p class=\\"lineup-compare-intro\\">After switching to <strong>" +
            m +
            "</strong> placement rules, the best-supported field for the same nine changed as follows.</p>";
        }} else if (k === "lock") {{
          intro =
            "<p class=\\"lineup-compare-intro\\">Lock settings changed; unlocked positions were re-balanced toward the best total fit.</p>";
        }} else {{
          intro =
            "<p class=\\"lineup-compare-intro\\">Unlocked positions were adjusted toward the best total fit for these nine players.</p>";
        }}

        const rows = [];
        for (const pos of diffPos) {{
          const bp = escapeHtml(before[pos] || "");
          const ap = escapeHtml(after[pos] || "");
          const ds =
            scorePlayerForPosition(after[pos], pos) - scorePlayerForPosition(before[pos], pos);
          const dsL = ds >= 0 ? "+" + ds.toFixed(1) : ds.toFixed(1);
          rows.push(
            "<tr><td><strong>" +
              escapeHtml(pos) +
              "</strong></td><td>" +
              bp +
              "</td><td>" +
              ap +
              "</td><td class=\\"lineup-compare-delta\\">" +
              dsL +
              "</td></tr>"
          );
        }}

        const gain = aFit - bFit;
        const gainS = gain >= 0 ? "+" + gain.toFixed(1) : gain.toFixed(1);

        lineupCompareEl.innerHTML =
          intro +
          "<table class=\\"lineup-compare-table\\"><thead><tr><th>Pos</th><th>Before</th><th>After</th><th>Δ fit</th></tr></thead><tbody>" +
          rows.join("") +
          "</tbody></table>" +
          "<p class=\\"lineup-compare-totals\\"><strong>Total fit</strong> (sum over positions): " +
          bFit.toFixed(1) +
          " → " +
          aFit.toFixed(1) +
          " (" +
          gainS +
          ")</p>" +
          "<p class=\\"lineup-compare-why\\">Higher total means a better combined matchup score for this roster — individual cells do not need to be 100.</p>";
      }}

      function renderBenchScoreTable() {{
        const body = document.getElementById("bench-score-body");
        if (!body) return;
        const bench = Array.isArray(replanContext.bench_players) ? replanContext.bench_players : [];
        if (bench.length === 0) {{
          body.innerHTML = "<tr><td colspan='11'>No bench players in planner context.</td></tr>";
          return;
        }}

        const posCols = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"];
        const rows = [];
        for (const playerInfo of bench) {{
          if (!playerInfo || !playerInfo.name) continue;
          const name = String(playerInfo.name);
          // Bench players are not part of the initial 9 rendered profiles;
          // hydrate their offense/defense maps from replan_context first.
          ensureBenchProfiles(name, "");
          const roles = Array.isArray(playerInfo.roles) ? playerInfo.roles.map((r) => String(r)).join(", ") : "—";
          const off = offensiveScore(name).toFixed(1);
          const scoreCells = posCols.map((pos) => {{
            const played = defensiveScore(name, pos);
            const predicted = defensiveScorePredicted(name, pos);
            if (predicted > 0.0 && Math.abs(predicted - played) > 0.01) {{
              return played.toFixed(1) + " / " + predicted.toFixed(1);
            }}
            return played.toFixed(1);
          }});
          rows.push(
            "<tr>" +
              "<td>" + escapeHtml(name) + "</td>" +
              "<td>" + escapeHtml(roles) + "</td>" +
              "<td>" + off + "</td>" +
              scoreCells.map((v) => "<td>" + v + "</td>").join("") +
            "</tr>"
          );
        }}
        body.innerHTML = rows.length > 0
          ? rows.join("")
          : "<tr><td colspan='11'>No bench players in planner context.</td></tr>";
      }}

      function readGameStateForm() {{
        const inning = parseInt(document.getElementById("gs-inning")?.value || "1", 10);
        const half = document.getElementById("gs-half")?.value || "bottom";
        const outs = parseInt(document.getElementById("gs-outs")?.value || "0", 10);
        const scoreFor = parseInt(document.getElementById("gs-score-for")?.value || "0", 10);
        const scoreAgainst = parseInt(document.getElementById("gs-score-against")?.value || "0", 10);
        const b1 = document.getElementById("gs-base-1")?.checked || false;
        const b2 = document.getElementById("gs-base-2")?.checked || false;
        const b3 = document.getElementById("gs-base-3")?.checked || false;
        const subsUsed = parseInt(document.getElementById("gs-subs-used")?.value || "0", 10);
        const subsLimit = parseInt(document.getElementById("gs-subs-limit")?.value || "5", 10);
        return {{
          inning: Math.max(1, inning),
          half: half,
          outs: Math.max(0, Math.min(2, outs)),
          score_for: Math.max(0, scoreFor),
          score_against: Math.max(0, scoreAgainst),
          bases: [b1, b2, b3],
          substitutions_used: Math.max(0, subsUsed),
          substitutions_limit: Math.max(0, subsLimit),
          pitcher_fatigue: 0.0,
        }};
      }}

      function battingOrderFromDom() {{
        return lineupRows.map((li) => li.dataset.player || "").filter(Boolean);
      }}

      function buildPlanningDefensiveScores() {{
        hydrateCurrentAssignmentProfiles(getUnavailablePosition());
        const base = Object.assign({{}}, replanContext.defensive_scores || {{}});
        for (const pos of allPositions) {{
          const player = getPlayerAt(pos);
          if (!player) continue;
          const byPos = defensiveProfiles[player];
          if (byPos && Object.prototype.hasOwnProperty.call(byPos, pos)) {{
            base[player] = Number(byPos[pos]);
          }} else if (!Object.prototype.hasOwnProperty.call(base, player)) {{
            base[player] = 0.0;
          }}
        }}
        return base;
      }}

      function renderModule5FromPlan(plan) {{
        const list = document.getElementById("m5-recommendations");
        const tbody = document.getElementById("m5-inning-body");
        if (!list || !tbody || !plan) return;
        const recs = plan.recommendations || [];
        if (recs.length === 0) {{
          list.innerHTML = "<li><strong>No immediate recommendations.</strong> <span>Module 5 did not flag a high-priority action for this state.</span></li>";
        }} else {{
          list.innerHTML = recs.map((rec) => {{
            const at = escapeHtml(rec.action_type || "action");
            const pr = escapeHtml(String(rec.priority != null ? rec.priority : "?"));
            const conf = Number(rec.confidence != null ? rec.confidence : 0).toFixed(2);
            const reason = escapeHtml(rec.reason || "No rationale provided.");
            const bp = escapeHtml(rec.bench_player || "");
            const tp = escapeHtml(rec.target_player || "");
            const ps = escapeHtml(rec.position || "");
            return '<li class="rec-item" tabindex="0" role="button" data-bench-player="' + bp + '" data-target-player="' + tp + '" data-position="' + ps + '"><strong>' + at + "</strong> (priority " + pr + ", confidence " + conf + ")<br/><span>" + reason + "</span></li>";
          }}).join("");
        }}
        const rows = plan.multi_inning_plan || [];
        if (rows.length === 0) {{
          tbody.innerHTML = "<tr><td colspan='4'>No inning plan generated.</td></tr>";
        }} else {{
          tbody.innerHTML = rows.map((row) => {{
            const inn = escapeHtml(String(row.inning != null ? row.inning : "?"));
            const hf = escapeHtml(String(row.half || "tbd"));
            const obj = escapeHtml(String(row.objective || "n/a"));
            const cnt = Array.isArray(row.recommended_actions) ? row.recommended_actions.length : 0;
            return '<tr class="inning-row" tabindex="0" role="row"><td>' + inn + "</td><td>" + hf + "</td><td>" + obj + "</td><td>" + cnt + "</td></tr>";
          }}).join("");
        }}
      }}

      async function runModule5Replan() {{
        const status = document.getElementById("m5-replan-status");
        if (!replanContext || !replanContext.bench_players) {{
          if (status) status.textContent = "";
          return;
        }}
        if (status) status.textContent = "Contacting planner…";
        const payload = {{
          game_state: readGameStateForm(),
          current_lineup: {{
            batting_order: battingOrderFromDom(),
            field_positions: currentAssignment(),
          }},
          bench_players: replanContext.bench_players,
          offensive_scores: replanContext.offensive_scores,
          defensive_scores: buildPlanningDefensiveScores(),
          innings_ahead: replanContext.innings_ahead || 3,
        }};
        try {{
          const res = await fetch("/api/plan", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify(payload),
          }});
          const text = await res.text();
          if (!res.ok) {{
            if (status) status.textContent = "Planner error (" + res.status + "): " + (text || res.statusText).slice(0, 200);
            return;
          }}
          const plan = JSON.parse(text);
          renderModule5FromPlan(plan);
          if (status) status.textContent = "Plan updated at " + new Date().toLocaleTimeString() + " (Module 5).";
        }} catch (err) {{
          if (status) status.textContent = "Could not reach /api/plan. Run PYTHONPATH=src python3 demos/dashboard_plan_server.py and open the dashboard from http://127.0.0.1:8765/ (not a file:// URL).";
        }}
      }}

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

      function defensiveScorePredicted(player, pos) {{
        const score = defensivePredictedProfiles[player] ? defensivePredictedProfiles[player][pos] : undefined;
        const numeric = Number(score);
        return Number.isFinite(numeric) ? numeric : 0.0;
      }}

      function offensiveScore(player) {{
        const numeric = Number(offensiveProfiles[player]);
        return Number.isFinite(numeric) ? numeric : 0.0;
      }}

      function scorePlayerForPosition(player, pos) {{
        if (player === inactivePlayer) return -1000.0;
        if (pos === "DH") return offensiveScore(player);
        const base = defensiveScore(player, pos);
        const unavailablePos = getUnavailablePosition();
        if (pos === unavailablePos && unavailablePos) {{
          const allowed = eligibilityProfiles[player] || [];
          const isNatural = allowed.includes(unavailablePos);
          if (!isNatural) {{
            const predicted = defensiveScorePredicted(player, unavailablePos);
            const emergencyScore = predicted > 0.0 ? predicted : base;
            return 0.75 * emergencyScore;
          }}
          return base;
        }}
        return base;
      }}

      function isEligible(player, pos) {{
        if (!strictMode) return true;
        if (pos === "DH") return true;
        if (player === inactivePlayer) return false;
        const unavailablePos = getUnavailablePosition();
        if (pos === unavailablePos && unavailablePos) {{
          return true;
        }}
        const allowed = eligibilityProfiles[player] || [];
        return allowed.includes(pos);
      }}

      function currentAssignment() {{
        const assignment = {{}};
        for (const pos of allPositions) assignment[pos] = getPlayerAt(pos);
        return assignment;
      }}

      function renderLocks() {{
        for (const slot of slots) {{
          const pos = slot.dataset.pos || "";
          slot.classList.toggle("locked", lockedPositions.has(pos));
        }}
        for (const btn of lockButtons) {{
          const pos = btn.dataset.lockPos || "";
          const isLocked = lockedPositions.has(pos);
          btn.classList.toggle("active", isLocked);
          btn.textContent = isLocked ? "LOCKED" : "LOCK";
        }}
      }}

      function bestFullLineupPermutationResult() {{
        const positions = [...allPositions];
        const roster = positions.map((pos) => getPlayerAt(pos));
        const fixed = {{}};
        for (const pos of lockedPositions) {{
          fixed[pos] = getPlayerAt(pos);
        }}
        const remainingPositions = positions.filter((pos) => !lockedPositions.has(pos));
        const fixedPlayers = new Set();
        for (const pos of lockedPositions) {{
          const name = getPlayerAt(pos);
          if (name) fixedPlayers.add(name);
        }}
        const remainingPlayers = roster.filter((p) => !fixedPlayers.has(p));
        const n = remainingPositions.length;
        if (remainingPlayers.length !== n) {{
          return {{ score: -Infinity, assignment: null }};
        }}

        function fullScore(assignObj) {{
          let sum = 0.0;
          for (const pos of positions) {{
            const pl = assignObj[pos];
            if (!pl) return -Infinity;
            sum += scorePlayerForPosition(pl, pos);
          }}
          return sum;
        }}

        if (n === 0) {{
          const merged = {{}};
          for (const pos of positions) {{
            merged[pos] = getPlayerAt(pos);
          }}
          const s = fullScore(merged);
          return {{ score: s, assignment: merged }};
        }}

        let bestScore = -Infinity;
        let bestAssignment = null;
        const used = new Array(n).fill(false);
        const pickIdx = new Array(n);

        function dfs(depth) {{
          if (depth === n) {{
            const merged = Object.assign({{}}, fixed);
            for (let j = 0; j < n; j += 1) {{
              merged[remainingPositions[j]] = remainingPlayers[pickIdx[j]];
            }}
            const sum = fullScore(merged);
            if (sum > bestScore) {{
              bestScore = sum;
              bestAssignment = merged;
            }}
            return;
          }}
          for (let i = 0; i < n; i += 1) {{
            if (used[i]) continue;
            const player = remainingPlayers[i];
            const pos = remainingPositions[depth];
            if (!isEligible(player, pos)) continue;
            used[i] = true;
            pickIdx[depth] = i;
            dfs(depth + 1);
            used[i] = false;
          }}
        }}

        dfs(0);
        return {{ score: bestScore, assignment: bestAssignment }};
      }}

      function totalDefenseFitScore() {{
        let total = 0.0;
        for (const pos of allPositions) total += scorePlayerForPosition(getPlayerAt(pos), pos);
        return total;
      }}

      function applyBestShuffleIfBelowPerfect() {{
        const result = bestFullLineupPermutationResult();
        if (!result.assignment || !Number.isFinite(result.score)) return false;
        const current = totalDefenseFitScore();
        if (result.score - current <= 0.01) return false;
        applyAssignment(result.assignment);
        updateBattingLineupDHTag();
        updateOverallDefenseConfidence();
        refreshFocusAfterAssignment();
        return true;
      }}

      function updateOverallDefenseConfidence() {{
        if (!lineupDefenseEl) return;
        const currentTotal = totalDefenseFitScore();
        const bestTotal = bestFullLineupPermutationResult().score;
        lineupDefenseEl.classList.remove("conf-high", "conf-medium", "conf-low");
        if (lineupDefenseSubEl) lineupDefenseSubEl.classList.remove("conf-high", "conf-medium", "conf-low");

        if (!Number.isFinite(bestTotal) || bestTotal <= 0.0) {{
          lineupDefenseEl.textContent = "—";
          lineupDefenseEl.classList.add("conf-low");
          if (lineupDefenseSubEl) {{
            lineupDefenseSubEl.textContent = strictMode
              ? "Strict mode: no complete eligible assignment found for these nine players."
              : "Could not score best-case reassignment.";
          }}
          return;
        }}

        const efficiency = Math.min(100.0, (currentTotal / bestTotal) * 100.0);
        lineupDefenseEl.textContent = efficiency.toFixed(1);
        let tierClass = "conf-low";
        if (efficiency >= 85.0) tierClass = "conf-high";
        else if (efficiency >= 60.0) tierClass = "conf-medium";
        lineupDefenseEl.classList.add(tierClass);
        if (lineupDefenseSubEl) {{
          lineupDefenseSubEl.classList.add(tierClass);
          const modeBits = strictMode ? "Strict eligibility" : "Free placement";
          lineupDefenseSubEl.textContent =
            "Totals for this shuffle comparison: current " +
            currentTotal.toFixed(1) +
            " · best among all permutations " +
            bestTotal.toFixed(1) +
            " · " +
            modeBits +
            ".";
        }}
      }}

      function renderWhyThisMove() {{
        if (!whyListEl) return;
        const rows = [];
        const unavailablePos = getUnavailablePosition();
        for (const pos of allPositions) {{
          const player = getPlayerAt(pos);
          const score = scorePlayerForPosition(player, pos);
          const scoreLabel = pos === "DH" ? "offense" : "defense";
          const emergencyTag = unavailablePos && pos === unavailablePos ? " (emergency)" : "";
          rows.push("<li><strong>" + pos + "</strong> -> " + player + emergencyTag + " | " + scoreLabel + ": <span class='why-score'>" + score.toFixed(1) + "</span></li>");
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

      function optimizeDefenseWithLockedPlayer(lockedPlayer, lockedPos, compareMeta) {{
        if (!lockedPlayer || !lockedPos) return;
        if (lockedPositions.has(lockedPos)) {{
          if (explainEl) explainEl.textContent = "Target position is locked. Unlock it first to modify.";
          return;
        }}
        const beforeFieldMutation = cloneAssignment();
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
          if (explainEl) explainEl.textContent = "Dragged player is already fixed in another locked position.";
          return;
        }}

        const remainingPlayers = players.filter((p) => p !== lockedPlayer && !fixedPlayers.has(p));
        const remainingPositions = allPositions.filter((p) => p !== lockedPos && !(p in fixedAssignments));
        const best = {{ score: -Infinity, assignment: null }};

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
            if (!isEligible(player, pos)) continue;
            partial[pos] = player;
            const nextPlayers = availablePlayers.slice(0, i).concat(availablePlayers.slice(i + 1));
            backtrack(posIdx + 1, nextPlayers, partial, runningScore + scorePlayerForPosition(player, pos));
            delete partial[pos];
          }}
        }}

        backtrack(0, remainingPlayers, {{}}, 0.0);
        if (!best.assignment) {{
          if (explainEl) explainEl.textContent = "No valid reassignment found with current constraints for that lock.";
          return;
        }}
        const optimized = Object.assign({{}}, fixedAssignments, best.assignment || {{}});
        optimized[lockedPos] = lockedPlayer;
        applyAssignment(optimized);
        updateBattingLineupDHTag();
        // Diamond drag: do not run global permutation shuffle afterward — it can move
        // the player off the cell they dropped on and feels like the drag did nothing.
        const isDiamondDrag = !compareMeta || compareMeta.kind === "drag";
        const autoShuffle = isDiamondDrag ? false : applyBestShuffleIfBelowPerfect();
        if (!autoShuffle) {{
          updateOverallDefenseConfidence();
        }}
        if (explainEl && !autoShuffle) {{
          const unavailablePos = getUnavailablePosition();
          const extra = unavailablePos ? " | Unavailable natural position: " + unavailablePos : "";
          explainEl.textContent = "Locked " + lockedPlayer + " at " + lockedPos + extra + " | Total fit score: " + totalDefenseFitScore().toFixed(1);
        }}
        const afterFieldMutation = cloneAssignment();
        const meta =
          compareMeta && compareMeta.kind
            ? compareMeta
            : {{ kind: "drag", player: lockedPlayer, targetPos: lockedPos }};
        const beforeForCompare =
          compareMeta && compareMeta.beforeAssignment ? compareMeta.beforeAssignment : beforeFieldMutation;
        renderLineupCompare(beforeForCompare, afterFieldMutation, meta);
        renderWhyThisMove();
        refreshFocusAfterAssignment();
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

      if (strictBtn) strictBtn.addEventListener("click", () => {{
        const snap = cloneAssignment();
        strictMode = true;
        renderModeUI();
        applyBestShuffleIfBelowPerfect();
        updateOverallDefenseConfidence();
        renderLineupCompare(snap, cloneAssignment(), {{ kind: "mode", strict: true }});
        renderWhyThisMove();
        refreshFocusAfterAssignment();
      }});
      if (freeBtn) freeBtn.addEventListener("click", () => {{
        const snap = cloneAssignment();
        strictMode = false;
        renderModeUI();
        applyBestShuffleIfBelowPerfect();
        updateOverallDefenseConfidence();
        renderLineupCompare(snap, cloneAssignment(), {{ kind: "mode", strict: false }});
        renderWhyThisMove();
        refreshFocusAfterAssignment();
      }});
      const resetBtn = document.getElementById("dashboard-reset");
      if (resetBtn) resetBtn.addEventListener("click", () => {{ resetDashboardToInitial(); }});
      if (unavailablePosEl) {{
        unavailablePosEl.addEventListener("change", () => {{
          const unavailablePos = getUnavailablePosition();
          hydrateBenchProfiles(unavailablePos);
          restoreOriginalState();
          const snap = cloneAssignment();
          const applied = applyUnavailablePlayerReplacement();
          let ranOptimize = false;
          if (unavailablePos && applied) {{
            const seedPlayer = getPlayerAt(unavailablePos);
            if (seedPlayer) {{
              optimizeDefenseWithLockedPlayer(seedPlayer, unavailablePos, {{
                kind: "unavailable",
                position: unavailablePos,
                beforeAssignment: snap,
              }});
              ranOptimize = true;
            }}
          }}
          if (!ranOptimize) {{
            const shuffled = applyBestShuffleIfBelowPerfect();
            if (!shuffled) {{
              updateOverallDefenseConfidence();
            }}
            renderLineupCompare(snap, cloneAssignment(), {{
              kind: "unavailable",
              position: unavailablePos || "",
            }});
          }}
          renderWhyThisMove();
          refreshFocusAfterAssignment();
          if (explainEl) {{
            const parts = [];
            if (unavailablePos) {{
              parts.push("Unavailable natural position: " + unavailablePos + ".");
              if (typeof inactivePlayer === "string" && inactivePlayer) {{
                parts.push("Player out: " + inactivePlayer + ".");
              }}
            }} else {{
              parts.push("No unavailable-position override.");
            }}
            parts.push("Total fit score: " + totalDefenseFitScore().toFixed(1));
            explainEl.textContent = parts.join(" ");
          }}
        }});
      }}

      for (const slot of slots) {{
        slot.addEventListener("dragstart", (event) => {{
          dragSourcePos = slot.dataset.pos || null;
          if (dragSourcePos && lockedPositions.has(dragSourcePos)) {{
            event.preventDefault();
            if (explainEl) explainEl.textContent = "Source position is locked. Unlock it first to drag this player.";
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
        slot.addEventListener("dragleave", () => {{ slot.classList.remove("drop-target"); }});
        slot.addEventListener("drop", (event) => {{
          event.preventDefault();
          const sourcePos = dragSourcePos || (event.dataTransfer ? event.dataTransfer.getData("text/plain") : "");
          const targetPos = slot.dataset.pos || "";
          const draggedPlayer = getPlayerAt(sourcePos);
          optimizeDefenseWithLockedPlayer(draggedPlayer, targetPos);
          clearDropStyles();
        }});
        slot.addEventListener("dragend", () => {{ clearDropStyles(); dragSourcePos = null; }});
      }}

      for (const btn of lockButtons) {{
        btn.addEventListener("click", (event) => {{
          event.stopPropagation();
          const pos = btn.dataset.lockPos || "";
          if (!pos) return;
          const snap = cloneAssignment();
          if (lockedPositions.has(pos)) lockedPositions.delete(pos);
          else lockedPositions.add(pos);
          renderLocks();
          const shuffled = applyBestShuffleIfBelowPerfect();
          updateOverallDefenseConfidence();
          renderLineupCompare(snap, cloneAssignment(), {{ kind: "lock" }});
          renderWhyThisMove();
          refreshFocusAfterAssignment();
          if (explainEl && !shuffled) {{
            explainEl.textContent = lockedPositions.size > 0
              ? "Locked positions: " + Array.from(lockedPositions).sort().join(", ")
              : "No positions locked.";
          }}
        }});
      }}

      for (const li of lineupRows) {{
        li.addEventListener("click", () => {{
          const player = li.dataset.player || "";
          if (player) activateLineupPlayer(player);
        }});
        li.addEventListener("keydown", (event) => {{
          if (event.key === "Enter" || event.key === " ") {{
            event.preventDefault();
            const player = li.dataset.player || "";
            if (player) activateLineupPlayer(player);
          }}
        }});
      }}

      for (const slot of slots) {{
        const playerEl = slot.querySelector(".player");
        if (playerEl) {{
          playerEl.addEventListener("click", (event) => {{
            event.stopPropagation();
            const player = playerEl.textContent.trim();
            if (player) activateFieldPlayer(player);
          }});
        }}
      }}

      if (module5Root) {{
        module5Root.addEventListener("click", (event) => {{
          const rec = event.target.closest(".rec-item");
          if (rec && rec.closest("#m5-recommendations")) {{
            lastFocusedPlayer = null;
            clearSelectionHighlights();
            rec.classList.add("active");
            const bench = rec.dataset.benchPlayer || "";
            const target = rec.dataset.targetPlayer || "";
            const position = rec.dataset.position || "";
            if (bench) highlightPlayerEverywhere(bench);
            if (target && target !== "slowest_current_runner") highlightPlayerEverywhere(target);
            renderInspectorRecommendation(bench, target, position);
            return;
          }}
          const row = event.target.closest("tr.inning-row");
          if (row && row.closest("#m5-inning-body")) {{
            lastFocusedPlayer = null;
            const cells = Array.from(row.querySelectorAll("td"));
            clearSelectionHighlights();
            renderInspectorInningSummary(cells);
          }}
        }});
        module5Root.addEventListener("keydown", (event) => {{
          if (event.key !== "Enter" && event.key !== " ") return;
          const rec = event.target.closest(".rec-item");
          if (rec && rec.closest("#m5-recommendations")) {{
            event.preventDefault();
            rec.click();
            return;
          }}
          const row = event.target.closest("tr.inning-row");
          if (row && row.closest("#m5-inning-body")) {{
            event.preventDefault();
            row.click();
          }}
        }});
      }}

      let replanDebounce = null;
      function scheduleAutoReplan() {{
        const auto = document.getElementById("gs-auto-refresh");
        if (!auto || !auto.checked) return;
        if (replanDebounce) clearTimeout(replanDebounce);
        replanDebounce = setTimeout(() => {{ runModule5Replan(); }}, 450);
      }}

      const refreshPlanBtn = document.getElementById("m5-refresh-plan");
      if (refreshPlanBtn) refreshPlanBtn.addEventListener("click", () => {{ runModule5Replan(); }});
      const gsWatchIds = [
        "gs-inning", "gs-half", "gs-outs", "gs-score-for", "gs-score-against",
        "gs-base-1", "gs-base-2", "gs-base-3", "gs-subs-used", "gs-subs-limit",
      ];
      for (const gid of gsWatchIds) {{
        const gel = document.getElementById(gid);
        if (gel) gel.addEventListener("change", scheduleAutoReplan);
      }}

      updateBattingLineupDHTag();
      renderModeUI();
      renderLocks();
      hydrateBenchProfiles(getUnavailablePosition());
      hydrateCurrentAssignmentProfiles(getUnavailablePosition());
      renderBenchScoreTable();
      const bootSnap = cloneAssignment();
      const bootShuffle = applyBestShuffleIfBelowPerfect();
      updateOverallDefenseConfidence();
      renderLineupCompare(bootSnap, cloneAssignment(), {{ kind: "load" }});
      renderWhyThisMove();
      if (explainEl && !bootShuffle) {{
        explainEl.textContent = "Initial total fit score: " + totalDefenseFitScore().toFixed(1);
      }}
    }})();""".replace("{{", "{").replace("}}", "}").replace("__DEFENSIVE_PROFILES_JSON__", defensive_profiles_json).replace(
        "__DEFENSIVE_PROFILES_PREDICTED_JSON__", defensive_profiles_predicted_json
    ).replace(
        "__OFFENSIVE_PROFILES_JSON__", offensive_profiles_json
    ).replace(
        "__ELIGIBILITY_PROFILES_JSON__", eligibility_profiles_json
    )
