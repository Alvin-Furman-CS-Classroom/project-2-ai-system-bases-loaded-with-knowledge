# Module Rubric Report — Module 4: Batting Order (Genetic Algorithms)

## Summary

Module 4 optimizes **batting order** for nine selected players using a **genetic algorithm** (permutation-preserving population, tournament selection, order crossover, swap/inversion mutation, elitism, stagnation early-stop). **Fitness** encodes baseball heuristics (OBP top, power middle, balanced tail) with optional Module 1 score blending. The public API `optimize_batting_order` validates inputs, wires fitness to the GA, and returns a standardized result dict. **10** Module 4 unit tests and **1** integration test (Modules 1+2+3+4 on `test_data`) pass with `PYTHONPATH=src`. **README.md** includes a **Module 4 Specification**, **Running Module 4**, and test commands. Optional terminal and **web** dashboards (`web/module4_dashboard.html`, demos) visualize lineup + defensive assignment from the real pipeline. Work split reference: `MODULE4_WORK_SPLIT.md`.

## Findings

### 1. Specification Clarity (Score: 4/4)

**Strengths:**
- Module plan row in `README.md` states topic (Genetic Algorithms), inputs, outputs, and dependencies.
- Dedicated **Module 4 Specification** in `README.md`: inputs, outputs, default GA parameters (including `stagnation_limit`), dependencies, integration, tests, work-split pointer.
- `MODULE4_WORK_SPLIT.md` documents shared contracts (I/O, GA defaults, determinism via `seed`).

**Evidence:** `README.md` **Module 4 Specification**; `MODULE4_WORK_SPLIT.md`; `src/module4/batting_order.py` docstring.

### 2. Inputs/Outputs (Score: 4/4)

**Strengths:**
- Inputs: `selected_players` (9 unique names), `batter_stats` with required keys `obp`, `slg`, `hr`, `rbi`; optional `offensive_scores` for Module 1 blend; tunable GA hyperparameters and `LineupFitnessWeights`.
- Outputs: `{"optimized_order", "best_fitness", "generations_run", "seed"}` from `optimize_batting_order`.
- GA layer returns `(best_lineup, metadata)` with extended metadata (`best_fitness_by_generation`, hyperparameters) for debugging.

**Evidence:** `optimize_batting_order` in `src/module4/batting_order.py`; `run_genetic_lineup_optimization` in `src/module4/genetic_optimizer.py`.

### 3. Dependencies (Score: 4/4)

**Strengths:**
- Standard library only for core Module 4.
- No circular imports; GA engine depends only on `Callable`/permutation logic; fitness depends on dict stats; wrapper composes both.

**Evidence:** `README.md` Setup; imports in `src/module4/*.py`.

### 4. Test Coverage (Score: 4/4)

**Strengths:**
- **Unit (GA):** valid permutations, crossover/mutation preserve uniqueness, seeded determinism, elitism non-regression of best-fitness history (`unit_tests/module4/test_genetic_optimizer.py`).
- **Unit (fitness):** good vs poor lineup scoring, missing stats errors, closure matches direct evaluation (`test_lineup_fitness.py`).
- **Unit (UI helper):** field render includes positions; missing position raises (`test_field_ui.py`).
- **Integration:** real `matchup_stats.json` + `defensive_stats.json` → Module 3 assignment → Module 4 order; asserts 9 unique players and metadata (`integration_tests/module4/test_module3_4_integration.py`).

**Evidence:**
- `PYTHONPATH=src python3 -m unittest discover -s unit_tests/module4 -p "test_*.py" -v` → **10 tests, OK**.
- `PYTHONPATH=src python3 -m unittest integration_tests.module4.test_module3_4_integration -v` → **1 test, OK**.

### 5. Documentation (Score: 4/4)

**Strengths:**
- Module docstrings on GA engine, fitness, public API; `web/README.md` for generating/viewing dashboard.
- `MODULE4_WORK_SPLIT.md` explains file layout and Partner A/B roles.
- README **Running** section includes Module 4 usage snippet; **Testing** section includes Module 4 test commands; checkpoint log row points to reports.

**Evidence:** `README.md` (Module 4 spec, Running, tests, checkpoint log); `web/README.md`; `MODULE4_WORK_SPLIT.md`.

### 6. Integration Readiness (Score: 4/4)

**Strengths:**
- Integration test exercises full chain through Module 4; output dict is ready for Module 5 planning.
- `demos/module4_pipeline_data.py` computes live UI inputs from `test_data`.

**Evidence:** `integration_tests/module4/test_module3_4_integration.py`; `demos/module4_pipeline_data.py`.

### 7. AI Concept Implementation (Score: 4/4)

**Strengths:**
- **Genetic algorithm** is explicit: population of permutations, fitness-based selection, crossover, mutation, elitism, generation loop, stagnation stop.
- Defaults documented in code: `population_size=120`, `generations=250`, `mutation_rate=0.08`, `elite_count=6`, `stagnation_limit=60`.

**Evidence:** `DEFAULT_*` constants and `run_genetic_lineup_optimization` in `src/module4/genetic_optimizer.py`.

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
- None for core checkpoint deliverables (README Module 4 spec and run/test commands added).

### Medium Priority
1. Confirm course **Git/participation** expectations with the instructor for all teammates.

### Low Priority
2. Optional: document tuning guidance (when to raise `generations` vs `population_size`) in README or `docs/`.

## Overall Assessment

**Grade: A+ (100%)** on the seven criteria above.

Module 4 meets the checkpoint narrative for **genetic algorithms**, documents **I/O** and **test commands** in README, integrates Modules 1–4 on real `test_data`, and stays modular (GA engine + fitness + API + optional UI). Ready for **Module 5** pending team **Git/participation** sign-off by the instructor.

## References (course / rubric)

- CSC-343 course hub: [index.path](https://csc-343.path.app/index.path)
- AI System rubric: [ai-system.rubric.md](https://csc-343.path.app/projects/project-2-ai-system/ai-system.rubric.md)
- Code elegance rubric: [code-elegance.rubric.md](https://csc-343.path.app/rubrics/code-elegance.rubric.md)
