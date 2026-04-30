# Module 3 (Checkpoint 3) — Two-Person Work Split Plan

This file splits **Module 3: CSP defensive position assignment** into two parallel workstreams so two people can implement it quickly and merge cleanly.

## Shared agreement (do first, 10–15 min)

- **Positions list**: `["P","C","1B","2B","3B","SS","LF","CF","RF"]`
- **Output format**: assignment dict `{position: player_name}`
- **Eligibility format**: `position_eligibility = {player_name: [positions...]}` (passed in directly or parsed from a small JSON/CSV later)
- **Objective weights (default)**: `w_def = 0.65`, `w_off = 0.35`
- **File layout**:
  - `src/module3/csp_solver.py` — generic CSP/backtracking solver
  - `src/module3/position_assignment.py` — baseball-specific wrapper + public API
  - `src/module3/__init__.py` — exports public API
  - `unit_tests/module3/test_csp_solver.py`
  - `unit_tests/module3/test_position_assignment.py`
  - `integration_tests/module3/test_module1_2_3_integration.py`

**Owner:** Person B (records the decisions in this file/README as needed).

## Person A — CSP engine + unit tests

**Goal:** deliver a reusable solver that can maximize an objective under constraints.

### A1 — Implement solver core (`src/module3/csp_solver.py`)

- **Represent**:
  - variables (positions)
  - domains (eligible players per position)
  - constraints (callables / helpers)
  - partial assignment
- **Backtracking** that returns the **best** solution by objective score:
  - track best assignment + best score
  - prune infeasible partial assignments early

### A2 — Add heuristics

- **MRV**: pick next unassigned variable with smallest remaining domain
- **Forward checking**: after assigning `position -> player`, remove `player` from other positions’ domains
- Optional: **LCV**: order candidate players to preserve flexibility

### A3 — Unit tests (`unit_tests/module3/test_csp_solver.py`)

- **Toy CSP feasibility**: solver finds a valid assignment for a small CSP
- **All-different**: verify solver enforces unique values when requested
- **Optimization**: when multiple feasible solutions exist, ensure it picks higher objective
- **Unsatisfiable case**: solver returns `None` (or raises a clear error — decide in shared agreement)

**Deliverable:** `csp_solver.py` + passing solver unit tests.

## Person B — Position assignment wrapper + tests/integration

**Goal:** translate lineup assignment into CSP inputs and validate outputs.

### B1 — Public API wrapper (`src/module3/position_assignment.py`)

Implement a function like:

`assign_defensive_positions(offensive_scores, defensive_scores, position_eligibility, *, weights=..., lock_positions=None) -> {position: player_name}`

- **Build domains** from `position_eligibility`
- **Add constraints**:
  - eligibility (domain membership)
  - all-different across positions
  - optional locked positions (e.g., `{"C": "Jane Smith"}`)
- **Objective**:
  - per-position utility: `w_def * defensive_scores[player][pos] + w_off * offensive_scores[player]`
  - maximize total utility over 9 positions
- **Validate inputs/outputs**:
  - all 9 positions assigned
  - no duplicate players
  - required scores exist for each used `(player, position)`
  - errors are clear when data is missing

### B2 — Unit tests (`unit_tests/module3/test_position_assignment.py`)

- **Happy path**: deterministic best assignment for a small crafted roster
- **Lock constraint**: forces a specific player to a specific position
- **Bad inputs**: missing eligibility / missing scores → clear exception

### B3 — Integration test (`integration_tests/module3/test_module1_2_3_integration.py`)

- Run:
  - `src.module1.matchup_analyzer.analyze_matchup_performance(...)`
  - `src.module2.defensive_analyzer.analyze_defensive_performance(...)`
  - feed both + a constructed `position_eligibility` into Module 3
- Assert:
  - output includes all 9 positions
  - all assigned players are unique
  - assigned players exist in source score dicts

**Deliverable:** `position_assignment.py` + unit tests + integration test.

## Integration + merge checklist (Person B, ~20–30 min)

- Ensure `src/module3/__init__.py` exports the public function.
- Run tests:

```bash
python3 -m unittest discover -s unit_tests -p "test_*.py" -v
python3 -m unittest discover -s integration_tests -p "test_*.py" -v
```

- Update `README.md`:
  - add **Module 3 Specification** (inputs/outputs/dependencies/tests)
  - fill **Checkpoint Log** row for checkpoint 3 with evidence (test commands + sample output snippet)

