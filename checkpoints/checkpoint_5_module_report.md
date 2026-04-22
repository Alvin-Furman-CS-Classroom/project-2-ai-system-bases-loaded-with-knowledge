# Module Rubric Report — Module 5: Adaptive Planning

## Summary

Module 5 implements **planning**: validated **game state** plus **current lineup** and **bench** feed **rule-based tactical recommendations** (pinch hitter, pinch runner, defensive replacement, lineup/matchup watch) with weighted scoring and **conflict resolution** for overlapping bench usage. The public API `generate_adaptive_plan` returns `recommendations`, `multi_inning_plan`, and `summary`. **12** Module 5 unit tests (`test_game_state`, `test_strategy_rules`, `test_planner`) and **1** end-to-end integration test (`test_module1_2_3_4_5_integration`) pass with `PYTHONPATH=src`. **README.md** includes a full **Module 5 Specification**, run/test commands, and pointers to the dashboard and `MODULE5_WORK_SPLIT.md`. Live replan from the browser is supported via `demos/dashboard_plan_server.py` and embedded `replan_context` in the generated HTML.

## Findings

### 1. Specification Clarity (Score: 4/4)

**Strengths:**

- Module plan row in `README.md` states topic (Planning), inputs, outputs, and dependencies on Modules 1–4.
- **Module 5 Specification** documents `game_state`, `current_lineup`, `bench_players`, score maps, outputs, file layout, integration steps, and tests.
- `pitcher_fatigue` is documented as accepted but **not** used for recommendations (no pitching module).

**Evidence:** `README.md` **Module 5 Specification**; `MODULE5_WORK_SPLIT.md`.

### 2. Inputs/Outputs (Score: 4/4)

**Strengths:**

- Inputs match the spec: normalized game state fields, batting order + field positions, bench entries with `name` and `roles`, flat offensive/defensive score maps, optional `innings_ahead`.
- Outputs: structured recommendations with explainable `reason` strings; multi-inning horizon; summary metadata including `lineup_snapshot`.

**Evidence:** `generate_adaptive_plan` in `src/module5/planner.py`; README outputs list.

### 3. Dependencies (Score: 4/4)

**Strengths:**

- Standard library only in Module 5 core.
- Typical pipeline uses Module 1–4 outputs as inputs; Module 5 code does not hard-import Module 1–4 (clean boundary for testing).

**Evidence:** `src/module5/*.py` imports; integration test composes full pipeline externally.

### 4. Test Coverage (Score: 4/4)

**Strengths:**

- **Unit (state):** normalization, missing keys, outs range, substitution invariants (`unit_tests/module5/test_game_state.py`).
- **Unit (planner):** output shape, determinism, empty bench behavior, invalid lineup → `PlanningInputError` (`test_planner.py`).
- **Unit (rules):** favorable vs poor bench choice, missing metrics → `StrategyRuleError`, conflict filtering, **DH not used as defensive replacement slot** (`test_strategy_rules.py`).
- **Integration:** real `test_data` → Modules 1–5; non-empty explainable recommendations; no overlapping bench conflicts in returned list (`integration_tests/module5/test_module1_2_3_4_5_integration.py`).

**Evidence:**

```bash
PYTHONPATH=src python3 -m unittest discover -s unit_tests/module5 -p "test_*.py" -v
PYTHONPATH=src python3 -m unittest integration_tests.module5.test_module1_2_3_4_5_integration -v
```

### 5. Documentation (Score: 4/4)

**Strengths:**

- README **Running** section includes Module 5 usage snippet and test commands.
- `web/README.md` covers dashboard generation; demo prints server URL for live replan.
- Work split documented in `MODULE5_WORK_SPLIT.md`.

**Evidence:** `README.md`; `web/README.md`; `MODULE5_WORK_SPLIT.md`; `demos/dashboard_plan_server.py` module docstring.

### 6. Integration Readiness (Score: 4/4)

**Strengths:**

- Integration test consumes Module 1–4 outputs and realistic game state.
- `demos/module4_pipeline_data.py` builds `replan_context` and `module5_plan` for the dashboard; `generate_adaptive_plan` is also exposed via HTTP POST `/api/plan` for interactive editing.

**Evidence:** `integration_tests/module5/test_module1_2_3_4_5_integration.py`; `demos/module4_pipeline_data.py`; `demos/dashboard_plan_server.py`.

### 7. AI Concept Implementation (Score: 4/4)

**Strengths:**

- **Planning** is explicit: state abstraction, candidate actions, scored tradeoffs (impact, urgency, feasibility, risk), horizon windows, and a multi-inning **plan** structure—not a black-box ML call.
- Deterministic tie-breaking supports reproducible tests and demos.

**Evidence:** `evaluate_strategy_recommendations`; `_build_multi_inning_plan` in `planner.py`.

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

- None for core Checkpoint 5 deliverables if instructor sign-off matches this evidence.

### Medium Priority

1. Update **Team** row and **AGENTS.md** placeholders if the course requires named ownership for Checkpoint 5.

### Low Priority

2. Optional: add `checkpoints/checkpoint_5_*` links to the README **Checkpoint Log** row for Module 5 (see project-wide report).

## Overall Assessment

**Grade: A+ (100%)** on the seven criteria above.

Module 5 completes the planned five-module AI pipeline with a clear planning layer, tests, integration, and optional interactive UI/server path.

## References (course / rubric)

- AI System rubric: [ai-system.rubric.md](https://csc-343.path.app/projects/project-2-ai-system/ai-system.rubric.md)
- Code elegance rubric: [code-elegance.rubric.md](https://csc-343.path.app/rubrics/code-elegance.rubric.md)
