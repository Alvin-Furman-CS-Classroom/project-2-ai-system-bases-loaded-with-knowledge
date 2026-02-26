# Baseball/Softball Lineup Optimization System

## Overview

This system uses AI-driven optimization to support lineup construction and strategic decision-making in baseball/softball by selecting, ordering, and dynamically adjusting players to maximize performance under changing game conditions. The system assists coaches by analyzing player statistics, opponent characteristics, and game context to recommend pre-game lineups and make adaptive in-game adjustments.

The workflow begins with first-order logic-based matchup analysis using quantified rules to predict how each batter performs against the opponent pitcher, complemented by defensive performance evaluation using knowledge-based rules. These analyses feed into a constraint satisfaction problem assigning players to optimal defensive positions while balancing offensive and defensive capabilities. A search-based algorithm optimizes the batting order, strategically placing high on-base percentage players early, power hitters in the middle, and lower-performing players at the end. Finally, a planning module monitors game state and creates adaptive strategies, recommending substitutions, lineup modifications, and tactical shifts across multiple innings.

## Team

- Member 1
- Member 2
- Member 3 (if applicable)

## Proposal

See `proposal.md` for the full approved proposal.

## Module Plan

Your system must include 5-6 modules. Fill in the table below as you plan each module.

| Module | Topic(s) | Inputs | Outputs | Depends On | Checkpoint |
| ------ | -------- | ------ | ------- | ---------- | ---------- |
| 1 | First-Order Logic | CSV/JSON with batter stats (BA, K, OBP, SLG, HR, RBI) and pitcher stats (ERA, WHIP, K rate, handedness, walk rate) | Performance scores (0-100) for each batter | None | Checkpoint 2 (Feb 26) |
| 2 | Knowledge Bases | CSV/JSON with defensive stats (fielding %, errors, putouts; catcher-specific stats) | Position-specific defensive scores (0-100) | None | Checkpoint 1 (Feb 11) |
| 3 | CSP | Offensive scores (Module 1), defensive scores (Module 2), position eligibility | Assignment of 9 players to positions | Modules 1, 2 | Checkpoint 3 (March 19) |
| 4 | Search Algorithms | 9 selected players from Module 3, detailed batter stats | Optimal batting order (1-9) | Modules 1, 2, 3 | Checkpoint 4 (April 2) |
| 5 | Planning | Game state, bench players, performance scores, current lineup | Adaptive recommendations and multi-inning plan | Modules 1, 2, 3, 4 | Checkpoint 5 (April 16) |
| 6 (optional) |  |  |  |  |  |

## Module 1 Specification: Matchup Analysis

**Topic:** First-Order Logic

**Inputs:**
- CSV or JSON file containing player statistics:
  - **Batter statistics:** batting average (BA), strikeouts (K), on-base percentage (OBP), slugging percentage (SLG), home runs (HR), runs batted in (RBI), handedness (L/R)
  - **Opponent pitcher statistics:** ERA, WHIP, strikeout rate (K rate), handedness (LHP/RHP), walk rate

**Outputs:**
- Performance scores (0-100) for each batter representing their expected effectiveness against the opponent pitcher
- Output format: Dictionary/map or JSON structure mapping each batter name to their performance score
- Scores derived through logical inference from first-order logic rules encoding matchup relationships using quantifiers (∀ for all, ∃ there exists)
- **No head-to-head data required:** the module predicts performance for every batter against every pitcher using only batter and pitcher profiles (e.g. season stats, handedness), so it works for pairs who have never faced each other

**Dependencies:** None

**Integration with Other Modules:**
- Module 1 outputs offensive performance scores that will be combined with defensive scores (from Module 2) in Module 3 (CSP) to assign players to optimal defensive positions.
- Module 1 scores will also be used by Module 4 (Search Algorithms) to optimize the batting order.
- The `analyze_matchup_performance` function returns a dictionary `{batter_name: score}` that can be directly used as input to subsequent modules.
- Example usage in Module 3: `offensive_scores = analyze_matchup_performance('matchup_stats.json')` (pitcher stats are in the file; optionally pass `rule_evaluator=RuleEvaluator()` for first-order logic adjustments)

**First-Order Logic Rules:**
The module uses quantified logical rules to evaluate matchups. Examples include:
- Universal quantifier (∀): "For all batters, if batter OBP > 0.350 and pitcher walk rate > 0.10, then increase score"
- Universal quantifier with conditions: "For all left-handed batters, if the pitcher is left-handed, then reduce performance score by 15%"
- Existential quantifier (∃): "There exists a batter such that their slugging percentage > 0.500 and pitcher ERA > 4.00, then increase score"
- Rules combine batter statistics with pitcher statistics to predict performance

**Tests:**
- Unit tests for:
  - First-order logic rule evaluation (universal and existential quantifiers)
  - Score calculation for various batter-pitcher combinations
  - Handedness matchup rules (same-handed vs. opposite-handed)
  - Statistical threshold rules (OBP, SLG, ERA, etc.)
  - Edge cases (missing data, extreme values, boundary conditions)
  - Input parsing (CSV and JSON formats)
  - Output formatting
  - Score normalization (ensuring scores are in 0-100 range)

## Module 2 Specification: Defensive Performance Analysis

**Topic:** Knowledge Bases

**Inputs:**
- CSV or JSON file containing defensive statistics for each player:
  - **For all players:** fielding percentage, errors, putouts
  - **For catchers only:** passed balls, caught stealing percentage, fielding percentage

**Outputs:**
- Position-specific defensive performance scores (0-100) for each player at each position they can play
- Output format: Dictionary/map or JSON structure mapping each player-position combination to their defensive score
- Scores calculated using heuristic rules that combine relevant defensive statistics:
  - Catchers: fielding percentage, passed balls, caught stealing percentage
  - Other positions: fielding percentage, errors, putouts

**Dependencies:** None

**Integration with Other Modules:**
- Module 2 outputs defensive scores that will be combined with offensive scores (from Module 1) in Module 3 (CSP) to assign players to optimal defensive positions.
- The `analyze_defensive_performance` function returns a dictionary `{player_name: {position: score}}` that can be directly used as input to Module 3's constraint satisfaction problem.
- Example usage in Module 3: `defensive_scores = analyze_defensive_performance('defensive_stats.json')`

**Tests:**
- Unit tests for:
  - Knowledge base rule evaluation
  - Position-specific score calculations (catcher vs. other positions)
  - Score calculation for various player-position combinations
  - Edge cases (missing data, players with no position eligibility)
  - Input parsing (CSV and JSON formats)
  - Output formatting

## Repository Layout

```
your-repo/
├── src/                              # main system source code
├── unit_tests/                       # unit tests (parallel structure to src/)
├── integration_tests/                # integration tests (new folder for each module)
├── .claude/skills/code-review/SKILL.md  # rubric-based agent review
├── AGENTS.md                         # instructions for your LLM agent
└── README.md                         # system overview and checkpoints
```

## Setup

**Dependencies:**
- Python 3.8 or higher
- Standard library modules only (no external dependencies required)

**Setup Steps:**
1. Ensure Python 3.8+ is installed
2. No additional package installation required (uses only standard library)

## Running

### Module 2: Defensive Performance Analysis

**Using the module programmatically:**
```python
from src.module2.defensive_analyzer import analyze_defensive_performance

# Analyze defensive statistics (default: predicts all positions)
scores = analyze_defensive_performance('test_data/defensive_stats.json')

# scores is a dictionary: {player_name: {position: score}}
# Example: {'John Doe': {'1B': 85.5, 'LF': 82.3, 'RF': 78.2, ...}}
# By default, scores include predicted performance at unplayed positions.

# Only evaluate played positions (no predictions):
scores = analyze_defensive_performance('defensive_stats.json', predict_all_positions=False)
```

**Cross-Position Prediction:**
By default, the module predicts each player's performance at positions they have not played, using position similarity rules (e.g., LF↔RF, SS↔2B) and stat transfer heuristics. Set `predict_all_positions=False` to only return scores for positions each player has actually played.

**Input File Format:**

JSON format:
```json
[
  {
    "name": "John Doe",
    "fielding_pct": 0.950,
    "errors": 5,
    "putouts": 150,
    "positions": ["1B", "LF"]
  },
  {
    "name": "Jane Smith",
    "fielding_pct": 0.980,
    "errors": 2,
    "putouts": 200,
    "passed_balls": 3,
    "caught_stealing_pct": 0.350,
    "positions": ["C"]
  }
]
```

CSV format:
```csv
name,fielding_pct,errors,putouts,passed_balls,caught_stealing_pct,positions
John Doe,0.950,5,150,,,"1B,LF"
Jane Smith,0.980,2,200,3,0.350,C
```

**Output Format:**
Dictionary mapping player names to position scores (0-100):
```python
{
  "John Doe": {"1B": 85.5, "LF": 82.3},
  "Jane Smith": {"C": 88.7}
}
```

## Testing

**Unit Tests** (`unit_tests/`): Mirror the structure of `src/`. Each module should have corresponding unit tests.

**Running Module 2 Tests:**
```bash
# Run all Module 2 unit tests
python3 -m unittest discover -s unit_tests/module2 -p "test_*.py" -v

# Run a specific test file
python3 -m unittest unit_tests.module2.test_defensive_analyzer -v
```

**Test Coverage:**
- Input parser (CSV and JSON formats)
- Knowledge base rules (catcher and general positions)
- Position evaluator
- Score calculator
- Full integration tests

**Test Data:**
Sample test data files are available in `test_data/`:
- `defensive_stats.json` - JSON format example
- `defensive_stats.csv` - CSV format example

**Integration Tests** (`integration_tests/`): Create a new subfolder for each module beyond the first, demonstrating how modules work together.

## Checkpoint Log

| Checkpoint | Date | Modules Included | Status | Evidence |
| ---------- | ---- | ---------------- | ------ | -------- |
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |

## Required Workflow (Agent-Guided)

Before each module:

1. Write a short module spec in this README (inputs, outputs, dependencies, tests).
2. Ask the agent to propose a plan in "Plan" mode.
3. Review and edit the plan. You must understand and approve the approach.
4. Implement the module in `src/`.
5. Unit test the module, placing tests in `unit_tests/` (parallel structure to `src/`).
6. For modules beyond the first, add integration tests in `integration_tests/` (new subfolder per module).
7. Run a rubric review using the code-review skill at `.claude/skills/code-review/SKILL.md`.

Keep `AGENTS.md` updated with your module plan, constraints, and links to APIs/data sources.

## References

List libraries, APIs, datasets, and other references used by the system.
