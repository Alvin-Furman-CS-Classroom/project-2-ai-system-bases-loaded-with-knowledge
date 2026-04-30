# Module 5 (Checkpoint 5) — Two-Person Work Split Plan

This file splits **Module 5: planning and adaptive in-game recommendations** into two parallel workstreams so two people can build and merge quickly.

## Shared agreement (do first, 15-20 min)

- **Input contract**:
  - `game_state`: inning/half, outs, score, base occupancy, pitcher context, substitutions used
  - `current_lineup`: batting order and field assignments
  - `bench_players`: available substitutes with role/eligibility metadata
  - `offensive_scores` and `defensive_scores` from prior modules
- **Output contract**:
  - `recommendations`: prioritized actions (substitution, tactical shift, lineup tweak)
  - `multi_inning_plan`: recommended actions by inning window with rationale
  - metadata: confidence/priority tags and constraints checked
- **Planning defaults**:
  - lookahead horizon of next 3 innings
  - deterministic tie-breaking for reproducible tests
- **File layout**:
  - `src/module5/game_state.py` — input validation + state helpers
  - `src/module5/strategy_rules.py` — tactical rule evaluation and scoring
  - `src/module5/planner.py` — public API wrapper and orchestration
  - `unit_tests/module5/test_game_state.py`
  - `unit_tests/module5/test_strategy_rules.py`
  - `unit_tests/module5/test_planner.py`
  - `integration_tests/module5/test_module1_2_3_4_5_integration.py`

## Person A — game state model + planning engine

**Goal:** deliver a reliable planner that converts validated game context into a structured multi-inning plan.

### A1 — Implement state model + validation (`src/module5/game_state.py`)

- Validate required fields and domain constraints:
  - inning >= 1, outs in 0..2, score integers, legal base states
  - substitutions remaining and bench availability are non-negative and consistent
- Normalize state into a consistent internal structure used by planner/rules.

### A2 — Implement planner core (`src/module5/planner.py`)

- Function signature example:
  - `generate_adaptive_plan(game_state, current_lineup, bench_players, offensive_scores, defensive_scores, *, innings_ahead=3)`
- Orchestrate:
  - candidate action generation
  - rule-based scoring/ranking
  - conflict resolution (no incompatible simultaneous actions)
- Return standardized output consumed by downstream demo/report artifacts.

### A3 — Unit tests (`unit_tests/module5/test_game_state.py`, `unit_tests/module5/test_planner.py`)

- Invalid state inputs raise clear, actionable errors.
- Planner output contains required keys and valid inning windows.
- Deterministic behavior with equivalent inputs.
- Edge cases: empty bench, no legal substitutions, tied recommendations.

**Deliverable:** validated state handling + planner orchestration + passing planner/state tests.

## Person B — tactical rules + integration/tests

**Goal:** encode baseball/softball tactical heuristics into ranked, explainable recommendations and prove end-to-end integration.

### B1 — Rule engine (`src/module5/strategy_rules.py`)

- Implement rules for:
  - pinch hitter opportunities (offense boost situations)
  - pinch runner opportunities (late-game speed leverage)
  - defensive replacements (protecting leads)
  - lineup or matchup adjustments using projected performance context
- Score each candidate with weighted factors (impact, risk, urgency, feasibility).
- Include short rationale strings for explainability.

### B2 — Planner integration support

- Expose clean rule-evaluation functions consumed by `planner.py`.
- Ensure no duplicate or contradictory recommendation objects are emitted.
- Keep constants/weights centralized for tuning.

### B3 — Tests

- `unit_tests/module5/test_strategy_rules.py`:
  - favorable scenario ranks above intentionally poor choice
  - missing player metrics/eligibility yields clear error
  - incompatible actions are filtered or demoted
- `integration_tests/module5/test_module1_2_3_4_5_integration.py`:
  - consume Module 1-4 outputs and realistic game state
  - assert non-empty, valid, explainable recommendations
  - assert no player appears in conflicting simultaneous roles

**Deliverable:** tactical rule scoring + recommendation explainability + full integration coverage.

## Integration + merge checklist (both, ~30 min)

- Ensure `src/module5/__init__.py` exports public planning API.
- Merge Person A branch first; Person B rebases/merges after.
- Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s unit_tests/module5 -p "test_*.py" -v
PYTHONPATH=src python3 -m unittest integration_tests.module5.test_module1_2_3_4_5_integration -v
```

- Update `README.md` checkpoint evidence for Module 5 after tests pass.
