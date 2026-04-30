# Module 4 (Checkpoint 4) — Two-Person Work Split Plan

This file splits **Module 4: batting order optimization with genetic algorithms** into two parallel workstreams so two people can build and merge quickly.

## Shared agreement (do first, 15-20 min)

- **Input contract**:
  - `selected_players`: list of 9 unique player names from Module 3
  - `batter_stats`: `{player_name: {obp, slg, hr, rbi, ...}}`
  - optional `offensive_scores` from Module 1 for fitness blending
- **Output contract**:
  - `optimized_order`: list of 9 unique players in batting slots 1-9
  - metadata: `best_fitness`, `generations_run`, `seed`
- **GA defaults**: `population_size=120`, `generations=250`, `mutation_rate=0.08`, `elite_count=6`
- **Determinism**: public API supports `seed` for reproducible tests
- **File layout**:
  - `src/module4/genetic_optimizer.py` — GA engine (selection/crossover/mutation loop)
  - `src/module4/lineup_fitness.py` — baseball scoring objective
  - `src/module4/batting_order.py` — public API wrapper
  - `unit_tests/module4/test_genetic_optimizer.py`
  - `unit_tests/module4/test_lineup_fitness.py`
  - `integration_tests/module4/test_module3_4_integration.py`

## Person A — GA engine + operator tests

**Goal:** deliver a reusable optimizer that only generates valid lineup permutations.

### A1 — Implement GA core (`src/module4/genetic_optimizer.py`)

- Represent each chromosome as a permutation of exactly 9 players.
- Create initial population from random valid permutations.
- Implement selection (tournament or rank), crossover (order-preserving), mutation (swap/inversion), and elitism.
- Stop on generation limit or stagnation threshold.

### A2 — Expose optimizer entrypoint

- Function signature example:
  - `run_genetic_lineup_optimization(players, fitness_fn, *, population_size=..., generations=..., mutation_rate=..., elite_count=..., seed=None)`
- Return best lineup and run metadata.

### A3 — Unit tests (`unit_tests/module4/test_genetic_optimizer.py`)

- Population contains only valid permutations of the 9 players.
- Crossover and mutation preserve uniqueness and length.
- Seeded runs are deterministic.
- Best fitness does not regress with elitism.

**Deliverable:** GA engine + passing operator-level tests.

## Person B — fitness model + integration/tests

**Goal:** encode baseball batting-order heuristics in a fitness function and integrate with Module 3 output.

### B1 — Fitness function (`src/module4/lineup_fitness.py`)

- Define weighted scoring that rewards:
  - high OBP in slots 1-2
  - high SLG/HR/RBI in slots 3-5
  - balanced remaining production for slots 6-9
- Add optional penalty terms for poor slot matches.
- Keep weights as constants/parameters for easier tuning.

### B2 — Public wrapper (`src/module4/batting_order.py`)

- Validate input shape (exactly 9 unique players with stats).
- Wire GA core to fitness function.
- Return standardized output format used by downstream planning.

### B3 — Tests

- `unit_tests/module4/test_lineup_fitness.py`:
  - known toy lineup scores higher than intentionally poor lineup
  - missing stats produce clear error
- `integration_tests/module4/test_module3_4_integration.py`:
  - feed Module 3 assignment into Module 4
  - assert output has 9 unique players and valid ordering

**Deliverable:** fitness + wrapper + integration tests.

## Integration + merge checklist (both, ~30 min)

- Ensure `src/module4/__init__.py` exports public API.
- Merge Person A branch first; Person B rebases/merges after.
- Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s unit_tests/module4 -p "test_*.py" -v
PYTHONPATH=src python3 -m unittest integration_tests.module4.test_module3_4_integration -v
```

- Update `README.md` checkpoint evidence for Module 4 after tests pass.
