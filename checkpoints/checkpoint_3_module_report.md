# Module Rubric Report — Module 3: Defensive Position Assignment (CSP)

## Summary

Module 3 assigns nine defensive positions via a **constraint satisfaction problem** solved with **backtracking**, **MRV**, **forward checking**, optional **LCV**, and **branch-and-bound**. The public API `assign_defensive_positions` combines Module 1 offensive scores and Module 2 defensive scores with eligibility and optional locks. An optional **`defensive_stress_profile="up_the_middle"`** scales defense using **FanGraphs WAR positional-adjustment runs** (documented in `docs/MODULE3_DEFENSIVE_LEVERAGE_SOURCES.md`). The module specification, run commands, and research citation are integrated into **README.md**. **22** Module 3 unit tests and **1** integration test (Modules 1+2+3) pass with `PYTHONPATH=src`.

## Findings

### 1. Specification Clarity (Score: 4/4)

**Strengths:**
- Full **Module 3 Specification** in `README.md`: topic, inputs, outputs, dependencies, integration example, tests, pointer to `MODULE3_WORK_SPLIT.md`.
- Clear distinction between dict inputs and optional parameters (`weights`, `lock_positions`, `positions`, `defensive_stress_profile`).

**Evidence:**
- `README.md`: **Module 3 Specification** section (after Module 2).
- `src/module3/position_assignment.py`: module docstring summarizes pipeline and stress profile.

### 2. Inputs/Outputs (Score: 4/4)

**Strengths:**
- Inputs are typed and documented: three dicts plus optional kwargs.
- Output shape `{position: player_name}` is explicit; infeasibility raises `InfeasibleLineupError` (subclass of `ValueError`) with a clear message; bad inputs use `InvalidLineupInputError`.
- Pitcher (`P`) handling documented (no Module 2 defensive term; neutral leverage).

**Evidence:**
- `assign_defensive_positions` docstring: `Args` / `Returns` (`position_assignment.py`).
- `_build_position_domains` validates missing offense/defense per eligibility.

### 3. Dependencies (Score: 4/4)

**Strengths:**
- Standard library only; depends on Module 1 & 2 only through **data** passed in (no circular imports).
- Internal split: `csp_solver.py` (generic CSP) vs `position_assignment.py` (baseball domain).

**Evidence:**
- `README.md` Setup: Python 3.8+, stdlib only.
- `src/module3/__init__.py` exports public API and research constants.

### 4. Test Coverage (Score: 4/4)

**Strengths:**
- **Unit:** CSP toy problems, all-different, optimization, branch-and-bound consistency, locks, partial constraints, API errors (`test_csp_solver.py`).
- **Unit:** Happy path, locks, bad inputs, infeasible lineup (`InfeasibleLineupError`), defensive stress profile + FanGraphs formula check (`test_position_assignment.py`).
- **Integration:** Real `test_data` matchup + defensive JSON → assignment (`integration_tests/module3/test_module1_2_3_integration.py`).

**Evidence:**
- `PYTHONPATH=src python3 -m unittest discover -s unit_tests/module3 -p "test_*.py" -v` → **22 tests, OK**.
- `PYTHONPATH=src python3 -m unittest integration_tests.module3.test_module1_2_3_integration -v` → **1 test, OK**.

### 5. Documentation (Score: 4/4)

**Strengths:**
- README Module 3 spec + **Running Module 3** + **Running Module 3 tests** with `PYTHONPATH=src`.
- `docs/MODULE3_DEFENSIVE_LEVERAGE_SOURCES.md` cites FanGraphs Library positional adjustment and explains mapping + caveats.
- `solve_max_csp` and helpers documented; `_recursive_search_maximize` and `_assign_and_forward_check` have focused docstrings after refactor.

**Evidence:**
- `README.md`: Module 3 sections; Checkpoint log row 3 points to this report.
- `csp_solver.py`: class/method docstrings for tracker and forward-check helper.

### 6. Integration Readiness (Score: 4/4)

**Strengths:**
- Example uses `analyze_matchup_performance` with **`RuleEvaluator()`** (recommended for full Module 1 behavior) and `analyze_defensive_performance`.
- Output is a plain dict ready for Module 4 (nine named players).

**Evidence:**
- `README.md` Module 3 example code block.
- `integration_tests/module3/test_module1_2_3_integration.py` builds eligibility from JSON and calls `assign_defensive_positions`.

### 7. AI Concept Implementation (Score: 4/4)

**Strengths:**
- **CSP** is explicit: variables = positions, domains = eligible players, **all-different**, optional locks, **additive objective** maximized by search.
- **MRV**, **forward checking** (domain copy + prune), **LCV**, **branch-and-bound** (optimistic upper bound) implemented in `csp_solver.py`.

**Evidence:**
- `_mrv_variable`, `_lcv_order_values`, `_upper_bound_additive`, `_assign_and_forward_check`, `_recursive_search_maximize` in `csp_solver.py`.
- `assign_defensive_positions` builds `score_for` and calls `solve_max_csp` (`position_assignment.py`).

## Scores Summary

| Criterion | Score | Max |
|-----------|-------|-----|
| Specification Clarity | 4 | 4 |
| Inputs/Outputs | 4 | 4 |
| Dependencies | 4 | 4 |
| Test Coverage | 4 | 4 |
| Documentation | 4 | 4 |
| Integration Readiness | 4 | 4 |
| AI Concept Implementation | 4 | 4 |
| **Total** | **28** | **28** |

## Action Items

### High Priority
- None for core checkpoint deliverables.

### Medium Priority
1. **Participation / GitHub:** Confirm each teammate meets course participation and PR/commit expectations (instructor-reviewed; not assessed in this file).
2. Optional: add a small **`demos/`** script that prints a Module 3 assignment from `test_data/` for demos.

### Low Priority
3. Expose `linear_scale` on `assign_defensive_positions` if you want sensitivity analysis without editing `DEFAULT_LEVERAGE_LINEAR_SCALE`.

## Overall Assessment

**Grade: A+ (100%)** on the seven criteria above.

Module 3 meets the checkpoint narrative for **CSP**, documents **I/O** and **test commands**, grounds optional leverage scaling in **cited** sabermetrics methodology, and stays **modular** (generic solver + domain wrapper). Ready for **Module 4** consumption pending team **Git/participation** sign-off by the instructor.

## References (course / rubric)

- CSC-343 course hub: [index.path](https://csc-343.path.app/index.path)
- AI System rubric: [ai-system.rubric.md](https://csc-343.path.app/projects/project-2-ai-system/ai-system.rubric.md)
- Code elegance rubric: [code-elegance.rubric.md](https://csc-343.path.app/rubrics/code-elegance.rubric.md)
- FanGraphs positional adjustment (leverage source): [library.fangraphs.com — Positional Adjustment](https://library.fangraphs.com/misc/war/positional-adjustment/)
