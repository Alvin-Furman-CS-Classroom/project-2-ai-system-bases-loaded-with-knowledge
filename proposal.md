# Baseball/Softball Lineup Optimization System

## System Overview

This system uses AI-driven optimization to support lineup construction and strategic decision-making in baseball/softball by selecting, ordering, and dynamically adjusting players to maximize performance under changing game conditions. Baseball and softball are well-suited for AI because they generate extensive historical data, involve multiple interconnected decision points, and require strategic planning that balances competing objectives.

The system assists coaches by analyzing player statistics, opponent characteristics, and game context to recommend pre-game lineups and make adaptive in-game adjustments. The workflow begins with first-order logic-based matchup analysis using quantified rules to predict how each batter performs against the opponent pitcher, complemented by defensive performance evaluation using knowledge-based rules that weight defensive metrics more heavily for critical positions (catcher, shortstop, third base). These analyses feed into a constraint satisfaction problem assigning players to optimal defensive positions while balancing offensive and defensive capabilities. A search-based algorithm optimizes the batting order, strategically placing high on-base percentage players early, power hitters in the middle, and lower-performing players at the end. Finally, a planning module monitors game state and creates adaptive strategies, recommending substitutions, lineup modifications, and tactical shifts across multiple innings. Together, these modules demonstrate how various AI techniques work synergistically to solve complex optimization problems where logical inference, constraint satisfaction, search-based ordering, and multi-step planning all play essential roles.

## Modules

### Module 1: Matchup Analysis

**Topics:** First-Order Logic

**Input:** A file (CSV or JSON format) containing player statistics including:
- **Batter statistics:** batting average, strikeouts, on-base percentage, slugging percentage, home runs, runs batted in
- **Opponent pitcher statistics:** ERA, WHIP, strikeout rate, handedness (LHP/RHP), walk rate

**Output:** A predicted performance score (0-100) for each batter, representing their expected effectiveness against the opponent pitcher. The output format is a data structure (e.g., dictionary/map or CSV) mapping each batter to their score, derived through logical inference from first-order logic rules encoding matchup relationships.

**Integration:** This module analyzes how each batter on the roster performs against the opponent's starting pitcher using quantified logical rules (e.g., "For all batters, if batter OBP > 0.350 and pitcher walk rate > 0.10, then increase score"). The performance predictions are used by subsequent modules to optimize the batting order and defensive positions.

**Prerequisites:** Course content on First-Order Logic required.

---

### Module 2: Defensive Performance Analysis

**Topics:** Knowledge Bases

**Input:** A file (CSV or JSON format) containing defensive statistics for each player:
- **For all players:** fielding percentage, errors, putouts
- **For catchers only:** passed balls, caught stealing percentage, fielding percentage

**Output:** Position-specific defensive performance scores (0-100) for each player at each position they can play. The output format is a data structure mapping each player-position combination to their defensive score, calculated using heuristic rules that combine relevant defensive statistics (e.g., catchers evaluated using fielding percentage, passed balls, and caught stealing percentage; other positions using fielding percentage, errors, and putouts).

**Integration:** This module evaluates defensive capabilities for all players, producing position-specific defensive scores that complement the offensive matchup scores from Module 1. These position-specific defensive scores are used by Module 3 (Position Assignment), which applies additional position-specific weighting when balancing offensive and defensive performance, with greater emphasis on defensive quality for catcher, shortstop, and third base positions.

**Prerequisites:** No prior modules required (Module 1 can run in parallel since it analyzes different aspects). Course content on Knowledge Bases required.

---

### Module 3: Position Assignment

**Topics:** Constraint Satisfaction Problem (CSP)

**Input:** 
- Predicted offensive performance scores (0-100) for each batter from Module 1
- Defensive performance scores (0-100) for each player-position combination from Module 2
- Position eligibility data: for each batter, a list of defensive positions they can play (C, 1B, 2B, 3B, SS, LF, CF, RF)

**Output:** An assignment of 9 players to positions: 8 defensive positions (C, 1B, 2B, 3B, SS, LF, CF, RF) and 1 designated hitter (DH). The output format is a mapping/assignment structure (e.g., dictionary or JSON) showing which player is assigned to each position. The assignment balances offensive and defensive performance by combining offensive scores from Module 1 with position-specific defensive scores from Module 2, applying additional position-specific weights that emphasize defensive quality more heavily for catcher, shortstop, and third base positions.

**Integration:** This module selects the optimal 9 players (one for each defensive position plus DH) by combining offensive matchup scores from Module 1 and defensive performance scores from Module 2. The selected players are then passed to Module 4 for batting order optimization.

**Prerequisites:** Modules 1 and 2 must be completed first. Course content on Constraint Satisfaction Problems required.

---

### Module 4: Batting Order Optimization

**Topics:** Search Algorithms (A*, Beam Search)

**Input:** 
- The 9 selected players assigned to positions from Module 3
- Access to the original input file containing detailed batter statistics (on-base percentage, home runs, slugging percentage, runs batted in)

**Output:** A complete batting order (positions 1-9) assigning each of the 9 selected players to a batting spot. The order follows strategic rules: spots 1-2 contain players with highest on-base percentage, spots 3-5 contain players with highest power numbers (home runs, slugging percentage, runs batted in), and spots 6-9 contain players with lowest overall performance scores.

**Integration:** This module takes the optimal 9 players from Module 3 and arranges them in an optimal batting order based on their statistical profiles. The complete lineup (defensive positions and batting order) is the final output of the system.

**Prerequisites:** Modules 1, 2, and 3 must be completed first. Course content on Search Algorithms (A*, Beam Search) required.

---

### Module 5: Adaptive Lineup Adjustment

**Topics:** Planning

**Input:** 
- Current game state: current score, inning number, position in the batting lineup (beginning, middle, or end)
- Available bench players
- Performance scores from Module 1 (offensive matchup scores)
- Defensive scores from Module 2
- Current optimized lineup from Module 4
- Information about which players have already been used/substituted

**Output:** 
- Immediate recommendations for the current game situation, including suggested substitutions, strategy shifts, batting order modifications, and defensive position changes
- A multi-inning plan (2-3 innings ahead) outlining when to make strategic adjustments based on anticipated game scenarios. The plan includes prioritized actions such as: prioritizing offense when losing in late innings, strengthening defense when winning, and balancing offense/defense in tied/close games.

**Integration:** This module takes the pre-game optimized lineup from Module 4 and adapts it dynamically based on in-game situations. It uses the performance metrics from Modules 1 and 2 to make informed decisions about substitutions and strategic adjustments throughout the game.

**Prerequisites:** Modules 1, 2, 3, and 4 must be completed first. Course content on Planning algorithms required.

---

## Feasibility Study

| Module | Required Topic(s) | Topic Covered By | Checkpoint Due |
| ------ | ----------------- | ---------------- | -------------- |
| 2      | Knowledge Bases    | Topic 1: First 1.5 weeks (Propositional Logic) | Checkpoint 1 (Feb 11) |
| 1      | First-Order Logic   | Topic 3: Weeks 3-4.5 (First-Order Logic) | Checkpoint 2 (Feb 26) |
| 3      | Constraint Satisfaction Problems (CSP) | Topic 4: Weeks 4.5-5.5 (Advanced Search - CSP covered here) | Checkpoint 3 (March 19) - Note: Requires completion of Modules 1 and 2 |
| 4      | Search Algorithms (A*, Beam Search) | Topic 2: Weeks 1.5-3 (Informed Search) | Checkpoint 4 (April 2) - Note: Requires completion of Modules 1, 2, and 3 |
| 5      | Planning           | Not explicitly listed - may be covered with Search/Advanced Search or separately; verify with instructor | Checkpoint 5 (April 16) |

## Coverage Rationale

This system leverages five AI topics, each selected for their natural fit with different aspects of lineup optimization in baseball/softball.

**First-Order Logic** is well-suited for matchup analysis because it allows the system to encode quantified rules about batter-pitcher relationships using logical formulas. Rules such as "For all left-handed batters, if the pitcher is left-handed, then reduce performance score by 15%" or "There exists a batter such that their slugging percentage > 0.500 and pitcher ERA > 4.00, then increase score" can be expressed and reasoned about using first-order logic. This logical approach provides an interpretable and rule-based method for evaluating offensive matchups based on statistical relationships.

**Knowledge Bases** excel at defensive performance evaluation because defense is not fully captured by statistics alone. A knowledge base allows the system to encode rules, positional heuristics, and contextual knowledge mirroring how coaches think about defense. The use of structured knowledge rather than pure numerical optimization makes knowledge bases an effective and interpretable tool for defensive evaluation.

**Constraint Satisfaction Problems (CSP)** map naturally to position assignment because it involves satisfying multiple constraints simultaneously. When writing a lineup, a player can only occupy exactly one position, physical and skill requirements must be met, and team rules or preferences must be respected. CSPs ensure valid lineups while preventing illegal or impractical assignments, reflecting the real constraints coaches face when setting a defensive lineup.

**Search Algorithms** work well for batting order optimization because creating an optimal batting order involves choosing the best sequence of hitters from many possible options. Search methods can compare different lineup orders and identify ones that are likely to produce more runs. This approach goes beyond traditional lineup rules by testing multiple possibilities and selecting an order that best fits the team's strengths.

**Planning** enables adaptive lineup adjustments because baseball and softball are dynamic sports where decisions change based on game context. Planning allows the system to model sequences of decisions over time, supporting adjustments like pinch hitting, defensive shifts, or lineup changes, capturing the strategic, forward-looking nature of game management.

**Trade-offs considered:** Alternative approaches were evaluated for each module. For matchup analysis, machine learning could have been used to learn patterns from historical data, but first-order logic was chosen for its interpretability and ability to encode explicit domain knowledge about baseball matchups. Knowledge bases were also considered but first-order logic's quantifiers provide more expressive power for modeling relationships between all batters and the pitcher. For position assignment, pure optimization algorithms could work, but CSP was selected for its explicit constraint modeling and interpretability. Game theory was considered for strategic interactions but planning was preferred for its ability to sequence multiple decisions across innings.
