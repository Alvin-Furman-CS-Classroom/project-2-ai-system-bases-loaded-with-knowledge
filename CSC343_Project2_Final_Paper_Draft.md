# Baseball/Softball Lineup Optimization System:
# A Five-Module AI Pipeline for Lineup Construction and Adaptive Game Planning

**Team Members:** Kali Javetski, Sylvia Burroughs

## Abstract

This paper presents a five-module AI system for baseball and softball lineup optimization that supports pre-game lineup construction and in-game strategy adaptation. The system addresses a common coaching challenge: balancing offensive matchups, defensive reliability, position constraints, batting-order strategy, and changing game conditions in a systematic, explainable way. The pipeline combines first-order logic for batter-pitcher matchup evaluation, knowledge-base scoring for defensive performance, constraint satisfaction for defensive assignment, a genetic algorithm for batting-order optimization, and a planning module for multi-inning tactical recommendations.

The architecture is modular and contract-driven: each stage produces structured outputs consumed by downstream stages. This design supports testing, reproducibility, and inspection of intermediate decisions rather than treating optimization as a black box. Evaluation emphasizes implementation correctness, integration reliability, and evidence-backed reporting through unit tests, integration tests, and rubric-aligned checkpoint reports.

Results indicate that combining symbolic logic, constrained search, evolutionary optimization, and planning yields a coherent decision-support workflow. The system does not replace coaching expertise, but it provides transparent recommendations and explicit tradeoffs.

## 1. Introduction

Lineup management in baseball and softball is a constrained optimization problem with human, statistical, and tactical dimensions. Coaches must decide who plays, where they play, batting order, and when to adjust during the game while balancing offense, defense, and substitution flexibility [1], [2].

This project formalizes that decision process into an interpretable AI pipeline. The task is decomposed into five modules with explicit inputs and outputs: offensive and defensive scoring, constrained assignment, batting-order optimization, and game-state-aware planning.

The scope is intentionally focused. The system supports lineup decisions using available player and opponent context, but it does not model every baseball variable or claim to automate all tactical coaching judgment. For example, planning accepts a `pitcher_fatigue` field for compatibility but does not issue bullpen or pitching-change recommendations because a pitching module was not implemented in this project.

The goal is an end-to-end system that is explainable, modular, and testable while demonstrating coherent integration of multiple AI paradigms.

## 2. System Architecture

The architecture follows a staged, dependency-aware pipeline where each module transforms inputs into structured outputs for later modules. At a high level:

1. Module 1 produces offensive matchup scores.
2. Module 2 produces defensive position-aware scores.
3. Module 3 assigns players to positions under hard constraints.
4. Module 4 optimizes batting-order permutations for selected players.
5. Module 5 generates tactical recommendations over a short time horizon.

The first two modules run independently because they evaluate offense and defense separately. Module 3 combines them under eligibility constraints. Module 4 orders the selected nine players. Module 5 uses lineup outputs plus game context and bench availability to generate prioritized recommendations and a multi-inning plan.

A key architecture decision was to maintain explicit module contracts rather than implicit shared state. This improves debugging and integration reliability because each stage can be validated independently and in chained tests. Integration suites cover Modules 1-3, Modules 3-4, and full Modules 1-5 flow.

**[Insert Figure 1: End-to-end architecture and data flow diagram]**

## 3. Module Implementation Summary

### 3.1 Module 1 - First-Order Logic Matchup Analysis

Module 1 evaluates expected batter performance against an opponent pitcher using quantified logical rules over structured baseball statistics. Inputs include batter metrics (e.g., BA, OBP, SLG, HR, RBI, handedness) and pitcher metrics (e.g., ERA, WHIP, K-rate, walk rate, handedness) [1], [2]. The output is a normalized offensive score map for batters.

First-order logic was chosen for interpretability. Rules can be inspected and justified in baseball terms (e.g., high-OBP batters vs. high-walk-rate pitchers, or handedness effects) [1], [2]. This module also avoids dependence on direct head-to-head history, so it can score unseen batter/pitcher pairs.

### 3.2 Module 2 - Knowledge-Base Defensive Analysis

Module 2 scores defensive performance by position-relevant heuristics using a knowledge-base approach. Inputs include defensive stats such as fielding percentage, errors, putouts, and catcher-specific attributes (e.g., passed balls, caught stealing percentage) [3], [4]. The output maps players to position-specific defensive scores.

The reasoning model mirrors coaching intuition: defensive value depends on position demands. Catcher evaluation uses role-specific metrics, while non-catcher positions use general fielding indicators [3], [4]. This preserves interpretability and still provides consistent numeric outputs for downstream modules.

### 3.3 Module 3 - CSP Defensive Position Assignment

Module 3 formulates lineup assignment as a constraint satisfaction problem with objective optimization. Inputs include Module 1 offensive scores, Module 2 defensive scores, and position-eligibility mappings. The output is a valid `{position: player}` assignment that maximizes weighted objective value under constraints.

Core constraints include one player per position and eligibility validity. The objective balances offensive and defensive contributions with configurable weighting and optional defensive stress profiles. The optional defensive leverage profile was informed by FanGraphs positional-adjustment runs as a transparent proxy for relative defensive difficulty across positions [5], [6], and by broader sabermetric discussions of defensive spectrum tradeoffs [11]. CSP was selected because it guarantees legal lineups while still optimizing assignment quality.

### 3.4 Module 4 - Genetic Batting Order Optimization

Module 4 optimizes batting order among the selected nine players using a genetic algorithm. Inputs include selected players, batter-stat features, and optional fitness blending parameters/hyperparameters. Output includes optimized order and fitness metadata.

The batting-order search space is combinatorial (9! permutations), so GA is used to efficiently explore candidates through mutation, selection, and elite retention. The implementation supports seeded runs and early stopping when fitness stagnates, balancing performance and reproducibility. The lineup fitness structure follows common sabermetric intuition: prioritize on-base skills near the top and power production in run-driving slots [1], [7], [12].

### 3.5 Module 5 - Adaptive Planning

Module 5 transforms game context into actionable recommendations over a short horizon (default multi-inning window). Inputs include normalized game state, current lineup, bench roles/attributes, and offensive/defensive score maps. Output contains:
- prioritized `recommendations`,
- a `multi_inning_plan`,
- and a `summary` snapshot.

The planning design emphasizes explainability and conflict management. Candidate actions are scored by impact, urgency, and feasibility; recommendation ordering uses deterministic tie-breaking; and bench-usage conflicts are resolved before final output.

## 4. Evaluation Methodology

The evaluation strategy focused on technical soundness, integration quality, and evidence-backed reporting rather than external predictive benchmarking outside project scope.

### 4.1 What Was Evaluated

Evaluation targeted:
- module-level correctness,
- cross-module handoff integrity,
- output structure validity,
- deterministic behavior,
- and demonstration readiness.

### 4.2 Metrics and Criteria

Given the project design, key metrics were implementation-oriented:
- test pass status (unit and integration),
- test breadth (module-level and chain-level coverage),
- completeness of module contracts (inputs/outputs/dependencies),
- evidence of end-to-end execution,
- and rubric-aligned quality indicators (clarity, coherence, integration readiness, concept correctness).

Checkpoint rubric reports were used as formal quality artifacts summarizing criteria-level findings, strengths, and action items [9], [10].

### 4.3 Test Setup and Data

The project uses Python standard-library-based core modules and structured test suites under `unit_tests/` and `integration_tests/`, with sample datasets in `test_data/`. Tests are organized by module and integration chain, enabling both local defect isolation and pipeline-level validation.

Representative integration coverage includes:
- Modules 1-3 (offense + defense into CSP assignment),
- Modules 3-4 (assignment into batting order optimization),
- Modules 1-5 (full end-to-end flow into planning outputs).

For Module 5, unit tests cover state validation, output structure, rule behavior, and error handling. Integration tests verify explainable non-empty recommendations and bench-conflict safety.

Project-level reporting also documented approximate unit-test method distribution: Module 1 (~132), Module 2 (~67), Module 3 (~22), Module 4 (~13), and Module 5 (12), plus three integration chains [10]. We do not treat test count as a quality proxy by itself; instead, it is used with coverage intent (rules, constraints, interfaces, and end-to-end behavior).

### 4.4 Result Collection Process

Results were collected from:
- automated unit/integration test runs,
- module and project checkpoint reports,
- and demo execution paths, including dashboard generation and live replanning.

This multi-source evidence model keeps claims traceable.

**[Insert Table I: Evaluation matrix mapping modules to tests and criteria]**

## 5. Results

The system produced a complete five-module decision-support pipeline with documented integration and reproducible execution behavior across required AI topics. Results support architectural coherence, successful pipeline chaining, and practical demonstration readiness.

### 5.1 Architectural and Integration Outcomes

All five modules were implemented with explicit contracts and dependencies, and integration tests confirm that outputs from earlier stages are valid inputs for later stages. Specifically, the repository includes chained tests for Modules 1-3, 3-4, and full 1-5 execution, which validates both intermediate handoffs and final planning outputs [10].

The architecture remained consistent with documented scope. For example, planning avoids unsupported pitching recommendations while still using game state and lineup context for tactical suggestions.

### 5.2 Testing and Reliability Outcomes

Checkpoint/project reporting indicates strong test infrastructure and broad coverage, including higher unit-test volume in earlier modules and focused suites plus integration reliance in later modules [10]. Module 5 reporting documented passing unit tests (`test_game_state`, `test_strategy_rules`, `test_planner`) and passing end-to-end integration for Modules 1-5 [9].

Deterministic tie-breaking and seeded optimization reduce run-to-run ambiguity, improving debugging and reproducibility.

### 5.3 Demonstration and Usability Outcomes

The project includes a browser dashboard and local planning server path for context edits and replanning requests, improving interpretability and interaction. This demonstration layer also served as behavioral evidence: recommendation objects, inning-window summaries, and no-conflict bench usage can be inspected in rendered outputs and API responses [9].

### 5.4 Strengths and Weaknesses Observed

**Strengths**
- End-to-end coherence across five distinct AI paradigms.
- Explainable outputs at each stage rather than opaque end-only recommendations.
- Structured testing and checkpoint evidence aligned to project rubric expectations.
- Practical demo pathway for visualizing outputs and iterative what-if context changes.

**Weaknesses**
- Tactical breadth in Module 5 is constrained by scope (no pitcher-management module).
- Unit-test distribution is uneven across modules (later modules rely relatively more on integration).
- Recommendation quality is tied to input data quality and rule/fitness assumptions.

Overall, the project met implementation goals without overclaiming.

**[Insert Figure 2: Sample dashboard snapshot showing lineup and plan outputs]**
**[Insert Table II: Example recommendation types by score/inning context]**

## 6. Proposal Delta

### Delta 1: Planning Scope Clarification

The planning module accepts `pitcher_fatigue` in input normalization but does not issue pitching-change recommendations. This reflects a scope boundary: no separate pitching strategy module was implemented.

### Delta 2: Enhanced Demo Integration

The final project includes dashboard generation and a local planning server route for interactive replan behavior.

### Delta 3: Evaluation Emphasis on Integration Reliability

Later-stage validation relies more heavily on chain integration testing, while earlier modules include larger unit-depth coverage.

### Delta 4: Refined Contract Documentation

Module specifications were expanded in project docs to tighten I/O boundaries and reduce ambiguity.

No required module was dropped; the five-module core architecture remained intact.

## 7. Limitations and Failure Analysis

### Limitation 1: Partial Tactical Coverage in In-Game Planning

The current planning layer does not model pitcher substitution strategy or bullpen optimization. This limits late-game recommendation breadth where pitching decisions dominate.

- **Likely cause:** scoped project boundaries and absence of a pitcher-specific model.
- **Improvement path:** add pitcher-state representation, bullpen role availability, and fatigue/matchup transition rules for planning actions.

### Limitation 2: Data Dependency and Input Sensitivity

The system assumes structured and sufficiently complete statistical input. Missing fields, inconsistent schemas, or weak feature quality can propagate uncertainty into scoring, assignment, and recommendations [1], [2], [3].

- **Likely cause:** rule-driven and optimization-driven modules are only as strong as normalized inputs.
- **Improvement path:** expand validation diagnostics, confidence flags, and fallback imputation strategies; provide user-facing warnings when recommendation confidence is data-limited.

### Limitation 3: Rule and Weight Calibration Constraints

Because module scoring and fitness are designed for interpretability and assignment quality, they are sensitive to rule thresholds and weight choices.

- **Likely cause:** static heuristics and configured weight defaults.
- **Improvement path:** add scenario-based calibration workflows, weight-sensitivity studies, and optional data-driven tuning while preserving interpretability.

### Limitation 4: External Generalization Not Fully Benchmarked

The system was evaluated on project datasets and scenario tests, not on large external longitudinal game corpora; broad generalization claims are not made.

- **Likely cause:** project scope/time and emphasis on architecture/integration over large-scale predictive benchmarking.
- **Improvement path:** run retrospective studies against broader datasets and compare recommendation outcomes against baseline heuristics.

## 8. Individual Contributions

### Kali Javetski
- Contributed to architecture framing and module-level specification refinement.
- Contributed to technical writing, project reporting, and final paper composition.

### Sylvia Burroughs
- Led core implementation across modules and key technical integration work.
- Built and stabilized module interfaces and test harnesses for pipeline chaining.
- Supported code-level quality improvements and final system readiness.

### Relative Effort Estimate (Totals = 100%)
- Kali Javetski: **50%**
- Sylvia Burroughs: **50%**

## 9. Conclusions and Future Work

This project demonstrates that lineup optimization in baseball/softball is well-suited to a multi-paradigm AI approach. First-order logic supports interpretable offensive matchup reasoning; knowledge-base methods provide structured defensive evaluation; CSP enforces legal assignments under constraints; genetic algorithms efficiently search batting-order permutations; and planning converts optimization outputs into game-state-responsive recommendations.

The most important result is the coherent integration of all five modules into a usable pipeline. Each module has a role, interfaces, and test-backed behavior, making the system inspectable and extensible.

Future work should focus on tactical completeness and calibration depth. High-priority next steps include pitcher/bullpen planning, expanded scenario datasets, recommendation-confidence reporting, and sensitivity analysis for rule thresholds and fitness weights. Another direction is explanation panels showing why recommendations were selected and what alternatives were considered, including clearer treatment of position-switch uncertainty observed in baseball analysis literature [13].

In summary, the project meets its objective: a modular, evidence-based AI decision-support system that aligns with course topics and demonstrates end-to-end reasoning under realistic lineup constraints [8], [9], [10].

## 10. References

[1] FanGraphs, "On-Base Percentage (OBP)," FanGraphs Library. [Online]. Available: https://library.fangraphs.com/offense/obp/. [Accessed: Apr. 27, 2026].

[2] FanGraphs, "Slugging Percentage (SLG)," FanGraphs Library. [Online]. Available: https://library.fangraphs.com/offense/slg/. [Accessed: Apr. 27, 2026].

[3] Baseball-Reference, "Major League Baseball Standard Fielding," Baseball-Reference.com. [Online]. Available: https://www.baseball-reference.com/leagues/majors/field.shtml. [Accessed: Apr. 27, 2026].

[4] MLB, "Caught Stealing Percentage (CS%)," MLB Glossary. [Online]. Available: https://www.mlb.com/glossary/standard-stats/caught-stealing-percentage. [Accessed: Apr. 27, 2026].

[5] P. Slowinski, "Positional Adjustment," FanGraphs Sabermetrics Library. [Online]. Available: https://library.fangraphs.com/misc/war/positional-adjustment/. [Accessed: Apr. 27, 2026].

[6] FanGraphs Community, "How the Positional Adjustments Have Changed Over Time (Part 1)," FanGraphs Community Blog. [Online]. Available: https://community.fangraphs.com/how-the-positional-adjustments-have-changed-over-time-part-1/. [Accessed: Apr. 27, 2026].

[7] T. M. Tango, M. G. Lichtman, and A. E. Dolphin, *The Book: Playing the Percentages in Baseball*. Washington, DC, USA: Potomac Books, 2007.

[8] K. Javetski and S. Burroughs, "Baseball/Softball Lineup Optimization System," project `README.md`, 2026.

[9] "Module Rubric Report - Module 5: Adaptive Planning," `checkpoints/checkpoint_5_module_report.md`, 2026.

[10] "Module Rubric Report - Project (Full AI System)," `checkpoints/project_module_rubric_report.md`, 2026.

[11] T. M. Tango, "Fielding Position Adjustments," *Inside The Book*. [Online]. Available: https://insidethebook.com/ee/index.php/site/article/fielding_position_adjustments. [Accessed: Apr. 27, 2026].

[12] J. M. Bradbury, *The Sabermetric Revolution: Assessing the Growth of Analytics in Baseball*. Philadelphia, PA, USA: Univ. of Pennsylvania Press, 2023.

[13] Baseball Prospectus, "Baseball Therapy: Learning A New Position Is Free," BaseballProspectus.com. [Online]. Available: https://www.baseballprospectus.com/news/article/30076/baseball-therapy-learning-a-new-position-is-free/. [Accessed: Apr. 27, 2026].
