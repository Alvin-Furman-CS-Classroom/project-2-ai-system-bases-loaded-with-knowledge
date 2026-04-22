## Project Context

- **System title:** Baseball/Softball Lineup Optimization System
- **Theme:** AI-supported lineup construction and in-game adaptation using FOL, knowledge bases, CSP, genetic search, and planning—stdlib Python, test-driven modules, browser dashboard for Module 4–5.
- **Proposal link or summary:** Approved proposal in [`proposal.md`](proposal.md) at repo root; aligns with README overview and module plan.

**Module plan:**

| Module | Topic(s) | Inputs | Outputs | Depends On | Checkpoint |
| ------ | -------- | ------ | ------- | ---------- | ---------- |
| 1 | First-Order Logic | CSV/JSON with batter stats (BA, K, OBP, SLG, HR, RBI) and pitcher stats (ERA, WHIP, K rate, handedness, walk rate) | Performance scores (0-100) for each batter | None | Checkpoint 2 (Feb 26) |
| 2 | Knowledge Bases | CSV/JSON with defensive stats (fielding %, errors, putouts; catcher-specific stats) | Position-specific defensive scores (0-100) | None | Checkpoint 1 (Feb 11) |
| 3 | CSP | Offensive scores (Module 1), defensive scores (Module 2), position eligibility | Assignment of 9 players to positions | Modules 1, 2 | Checkpoint 3 (March 19) |
| 4 | Genetic Algorithms | 9 selected players from Module 3, detailed batter stats | Optimal batting order (1-9) | Modules 1, 2, 3 | Checkpoint 4 (April 2) |
| 5 | Planning | Game state, bench players, performance scores, current lineup | Adaptive recommendations and multi-inning plan | Modules 1, 2, 3, 4 | Checkpoint 5 (April 16) |
| 6 (optional) |  |  |  |  |  |

## Constraints

- 5-6 modules total, each tied to course topics.
- Each module must have clear inputs/outputs and tests.
- Align module timing with the course schedule.

## How the Agent Should Help

- Draft plans for each module before coding.
- Suggest clean architecture and module boundaries.
- Identify missing tests and edge cases.
- Review work against the rubric using the code-review skill.

## Agent Workflow

1. Ask for the current module spec from `README.md`.
2. Produce a plan (use "Plan" mode if available).
3. Wait for approval before writing or editing code.
4. After implementation, run the code-review skill and list gaps.

## Key References

- Project Instructions: https://csc-343.path.app/projects/project-2-ai-system/ai-system.project.md
- Code elegance rubric: https://csc-343.path.app/rubrics/code-elegance.rubric.md
- Course schedule: https://csc-343.path.app/resources/course.schedule.md
- Rubric: https://csc-343.path.app/projects/project-2-ai-system/ai-system.rubric.md
