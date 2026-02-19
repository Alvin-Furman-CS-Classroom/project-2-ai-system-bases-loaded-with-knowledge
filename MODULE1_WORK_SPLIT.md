# Module 1 Work Split: Matchup Analysis

## Overview
This document divides Module 1 implementation between two partners for parallel development.

---

## Partner A: Data Layer & Score Calculation

### Responsibilities
**Core Components:**
1. **Data Models** (`src/module1/models.py`)
   - `Batter` dataclass with all batter statistics
   - `Pitcher` dataclass with all pitcher statistics
   - Validation methods for data integrity

2. **Input Parser** (`src/module1/input_parser.py`)
   - Parse JSON format (batters array + pitcher object)
   - Parse CSV format (batter rows + pitcher row)
   - Validate required fields and data types
   - Error handling for malformed input
   - Return `(List[Batter], Pitcher)` tuple

3. **Score Calculator** (`src/module1/score_calculator.py`)
   - Base score calculation from batter stats (BA, OBP, SLG)
   - Score adjustment application (receives adjustments from rules)
   - Score normalization to 0-100 range
   - Edge case handling (missing data, extreme values)

4. **Main Analyzer** (`src/module1/matchup_analyzer.py`)
   - `analyze_matchup_performance()` function (main entry point)
   - Orchestrates: parsing → rule evaluation → scoring
   - Returns `{batter_name: score}` dictionary
   - Public API for the module

### Tests
- `unit_tests/module1/test_input_parser.py` - Test CSV/JSON parsing, validation, error handling
- `unit_tests/module1/test_score_calculator.py` - Test normalization, edge cases, boundaries
- `unit_tests/module1/test_matchup_analyzer.py` - Test end-to-end integration
- `unit_tests/module1/test_models.py` - Test dataclass validation

### Test Data
- Create `test_data/matchup_stats.json` - Sample JSON input
- Create `test_data/matchup_stats.csv` - Sample CSV input

### Dependencies
- Partner A's components are foundational - Partner B will depend on these
- Partner A should complete models.py and input_parser.py first so Partner B can use them

---

## Partner B: Logic Engine & Rules

### Responsibilities
**Core Components:**
1. **First-Order Logic Engine** (`src/module1/logic_engine.py`)
   - Universal quantifier (∀) implementation: `apply_universal_rule()`
   - Existential quantifier (∃) implementation: `check_existential_rule()`
   - Rule evaluation framework
   - Rule application mechanism (returns score adjustments)

2. **Matchup Rules** (`src/module1/matchup_rules.py`)
   - Define all matchup rules as functions
   - Handedness rules (same-handed vs. opposite-handed matchups)
   - Statistical threshold rules (OBP vs walk rate, SLG vs ERA, etc.)
   - Rule functions take `(Batter, Pitcher)` and return score adjustments
   - Examples:
     - `handedness_penalty(batter, pitcher) -> float`
     - `obp_walk_advantage(batter, pitcher) -> float`
     - `power_vs_era_advantage(batter, pitcher) -> float`
     - `strikeout_matchup(batter, pitcher) -> float`

3. **Rule Evaluator** (`src/module1/rule_evaluator.py`)
   - Combines logic engine with rules
   - Applies all rules to all batters
   - Collects score adjustments
   - Returns adjustments dictionary: `{batter_name: total_adjustment}`

### Tests
- `unit_tests/module1/test_logic_engine.py` - Test ∀ and ∃ quantifiers, rule application
- `unit_tests/module1/test_matchup_rules.py` - Test each rule individually
- `unit_tests/module1/test_rule_evaluator.py` - Test rule combination and evaluation

### Dependencies
- Partner B depends on Partner A's `models.py` (Batter, Pitcher classes)
- Partner B will provide score adjustments that Partner A's score calculator uses

---

## Integration Points

### How Components Connect

```
Partner A:                    Partner B:
┌─────────────┐              ┌─────────────┐
│ Input       │              │ Logic       │
│ Parser      │──Batter──>   │ Engine      │
│             │──Pitcher──>  │             │
└─────────────┘              └─────────────┘
      │                              │
      │                              │
      ▼                              ▼
┌─────────────┐              ┌─────────────┐
│ Score       │<──adjustments─│ Rule        │
│ Calculator  │              │ Evaluator    │
└─────────────┘              └─────────────┘
      │                              │
      └──────────┬───────────────────┘
                 ▼
         ┌─────────────┐
         │ Main        │
         │ Analyzer    │
         └─────────────┘
```

### Interface Contracts

**Partner A provides:**
- `Batter` and `Pitcher` classes from `models.py`
- `parse_matchup_data(file_path: str) -> Tuple[List[Batter], Pitcher]` from `input_parser.py`
- `calculate_score(base_score: float, adjustments: float) -> float` from `score_calculator.py` (0-100 range)

**Partner B provides:**
- `evaluate_rules(batters: List[Batter], pitcher: Pitcher) -> Dict[str, float]` from `rule_evaluator.py`
  - Returns `{batter_name: total_score_adjustment}`

**Main Analyzer (Partner A) will:**
```python
def analyze_matchup_performance(file_path: str) -> Dict[str, float]:
    batters, pitcher = parse_matchup_data(file_path)
    adjustments = evaluate_rules(batters, pitcher)  # Partner B's function
    scores = {}
    for batter in batters:
        base_score = calculate_base_score(batter)
        adjustment = adjustments.get(batter.name, 0.0)
        scores[batter.name] = normalize_score(base_score + adjustment)
    return scores
```

---

## Workflow & Timeline

### Phase 1: Foundation (Both partners start simultaneously)
- **Partner A:** Create `models.py` with Batter and Pitcher dataclasses
- **Partner B:** Design logic engine interface and rule structure
- **Sync Point:** Partner A shares models.py, Partner B reviews interface design

### Phase 2: Core Implementation (Parallel work)
- **Partner A:** Implement input parser, score calculator
- **Partner B:** Implement logic engine, define matchup rules
- **Sync Point:** Both partners test their components independently

### Phase 3: Integration (Collaborative)
- **Partner A:** Implement main analyzer, integrate Partner B's rule evaluator
- **Partner B:** Create rule evaluator that uses Partner A's models
- **Sync Point:** Test full integration together

### Phase 4: Testing & Refinement (Both partners)
- **Partner A:** Write tests for parser, calculator, analyzer
- **Partner B:** Write tests for logic engine, rules, evaluator
- **Sync Point:** Run all tests, fix integration issues

---

## File Ownership Summary

### Partner A Files:
- `src/module1/models.py`
- `src/module1/input_parser.py`
- `src/module1/score_calculator.py`
- `src/module1/matchup_analyzer.py`
- `unit_tests/module1/test_models.py`
- `unit_tests/module1/test_input_parser.py`
- `unit_tests/module1/test_score_calculator.py`
- `unit_tests/module1/test_matchup_analyzer.py`
- `test_data/matchup_stats.json`
- `test_data/matchup_stats.csv`

### Partner B Files:
- `src/module1/logic_engine.py`
- `src/module1/matchup_rules.py`
- `src/module1/rule_evaluator.py`
- `unit_tests/module1/test_logic_engine.py`
- `unit_tests/module1/test_matchup_rules.py`
- `unit_tests/module1/test_rule_evaluator.py`

### Shared Files:
- `src/module1/__init__.py` - Both partners contribute exports
- `README.md` - Both partners update documentation

---

## Communication Guidelines

1. **Interface First:** Partner A should finalize `models.py` early so Partner B can start
2. **Mock Data:** Partner B can create mock Batter/Pitcher objects for testing before Partner A's parser is ready
3. **Score Adjustments:** Partner B returns raw adjustments (can be negative), Partner A handles normalization
4. **Rule Definitions:** Partner B should document all rules clearly for Partner A to understand
5. **Test Data:** Partner A creates test files, Partner B can add additional test cases

---

## Estimated Complexity Balance

**Partner A:** ~40% of work
- Data models: Low-Medium complexity
- Input parser: Medium complexity (CSV/JSON handling)
- Score calculator: Medium complexity (normalization logic)
- Main analyzer: Low complexity (orchestration)

**Partner B:** ~40% of work  
- Logic engine: Medium-High complexity (quantifier implementation)
- Matchup rules: Medium complexity (rule definitions)
- Rule evaluator: Medium complexity (integration logic)

**Shared:** ~20% of work
- Testing integration
- Documentation
- Code review

---

## Success Criteria

Both partners should ensure:
- ✅ All components have comprehensive unit tests
- ✅ Code follows project style (see Module 2 for reference)
- ✅ Components integrate seamlessly
- ✅ Edge cases are handled
- ✅ Documentation is clear
- ✅ Scores are always in 0-100 range
- ✅ First-order logic quantifiers are properly implemented
