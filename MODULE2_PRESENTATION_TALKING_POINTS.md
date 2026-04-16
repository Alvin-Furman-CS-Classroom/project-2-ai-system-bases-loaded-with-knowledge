# Module 2 Presentation: Defensive Performance Analysis
## Talking Points for Professor Presentation

---

## 1. Module Overview & Purpose

### What Module 2 Does
- **Core Function**: Evaluates defensive capabilities of all players at each position they can play
- **AI Technique**: Knowledge Bases (propositional logic rules)
- **Output**: Position-specific defensive performance scores (0-100 scale) for every player-position combination
- **Key Insight**: Defense requires domain knowledge and heuristics, not just raw statistics—making knowledge bases the ideal AI approach

### Why Knowledge Bases?
- Defense evaluation involves **structured rules** and **position-specific heuristics** that mirror how coaches think
- Knowledge bases allow encoding of **interpretable rules** rather than black-box numerical optimization
- Different positions require different evaluation criteria (catchers vs. infielders vs. outfielders)
- Provides **transparency** in how defensive scores are calculated

---

## 2. Technical Architecture

### Input Processing
- **Input Format**: CSV or JSON files containing defensive statistics
- **For All Players**: 
  - Fielding percentage
  - Errors
  - Putouts
- **For Catchers Only**:
  - Passed balls
  - Caught stealing percentage
  - Fielding percentage

### Knowledge Base Structure
- **DefensiveKnowledgeBase**: Contains rules and facts about defensive performance
- **Two Rule Types**:
  1. **Catcher Rule**: 
     - Weighted combination: 40% fielding percentage, 30% passed ball prevention, 30% caught stealing percentage
     - Formula: `0.4*fielding_pct + 0.3*(1-normalized_passed_balls) + 0.3*caught_stealing_pct`
  
  2. **General Position Rule** (for all non-catcher positions):
     - Weighted combination: 50% fielding percentage, 30% error prevention, 20% putout activity
     - Formula: `0.5*fielding_pct + 0.3*(1-normalized_errors) + 0.2*normalized_putouts`

### Processing Pipeline
1. **Input Parser**: Reads and validates CSV/JSON defensive statistics
2. **Position Evaluator**: Creates defensive facts for each player-position combination
3. **Knowledge Base**: Applies position-specific rules to evaluate facts
4. **Score Calculator**: Converts rule outputs to 0-100 scale scores
5. **Output**: Dictionary mapping `{player_name: {position: score}}`

---

## 3. Integration with Rest of System

### Downstream Dependencies (Modules That Use Module 2)

#### Module 3: Position Assignment (CSP)
- **Primary Consumer**: Module 3 combines offensive scores (Module 1) with defensive scores (Module 2)
- **How It's Used**:
  - Module 3 needs to assign 9 players to 8 defensive positions + DH
  - Uses defensive scores to balance offensive and defensive capabilities
  - Applies **position-specific weighting**—defensive quality matters more for critical positions:
    - Catcher (C)
    - Shortstop (SS)
    - Third Base (3B)
  - Example: A player with high offensive score but low defensive score at shortstop might be assigned to DH instead

#### Module 5: Adaptive Lineup Adjustment (Planning)
- **Secondary Consumer**: Module 5 uses defensive scores for in-game strategic decisions
- **How It's Used**:
  - When making substitution recommendations during the game
  - When deciding whether to prioritize offense or defense based on game state
  - When planning defensive position changes mid-game
  - Example: If winning in late innings, might substitute a player with higher defensive score to protect the lead

### Independence from Module 1
- **Key Point**: Module 2 has **no dependencies**—it can run independently or in parallel with Module 1
- Both modules analyze different aspects (offense vs. defense) and their outputs are combined later in Module 3
- This modularity allows for parallel development and testing

---

## 4. Key Design Decisions

### Position-Specific Rules
- **Why Different Rules?**: Catchers have unique responsibilities (handling pitchers, controlling base runners) that require different metrics
- **Catcher Evaluation**: Emphasizes game management (caught stealing) and reliability (passed balls)
- **General Positions**: Emphasize fielding fundamentals (fielding percentage, errors) and activity (putouts)

### Score Normalization
- **Input Flexibility**: Handles fielding percentages as 0-1 or 0-100 scale
- **Output Consistency**: All scores normalized to 0-100 range for easy comparison
- **Error Handling**: Gracefully handles missing data with sensible defaults

### Knowledge Base vs. Machine Learning
- **Why Knowledge Bases?**: 
  - Interpretable rules that coaches can understand and verify
  - No training data required
  - Explicit encoding of baseball domain knowledge
  - Transparent decision-making process

---

## 5. Example Use Case

### Scenario
- Input: Defensive stats for 15 players, each eligible for 2-3 positions
- Processing: Module 2 evaluates each player at each eligible position
- Output: Scores like:
  ```
  {
    "John Doe": {"1B": 85.5, "LF": 82.3},
    "Jane Smith": {"C": 88.7},
    "Mike Johnson": {"SS": 91.2, "3B": 87.4}
  }
  ```

### Integration Flow
1. **Module 1** produces offensive scores: `{"John Doe": 75, "Jane Smith": 82, ...}`
2. **Module 2** produces defensive scores: `{"John Doe": {"1B": 85.5, ...}, ...}`
3. **Module 3** combines both to assign:
   - Jane Smith → Catcher (high defensive score at C, good offensive score)
   - John Doe → 1B (good defensive score, decent offensive score)
   - Mike Johnson → SS (excellent defensive score, critical position)

---

## 6. Testing & Validation

### Test Coverage
- **Input Parsing**: CSV and JSON formats, edge cases (missing data)
- **Knowledge Base Rules**: Catcher vs. general position evaluation
- **Score Calculation**: Normalization, boundary conditions
- **Integration**: End-to-end pipeline testing
- **Edge Cases**: Players with no position eligibility, missing statistics

### Validation Approach
- Unit tests for each component (parser, knowledge base, evaluator, calculator)
- Integration tests for the full pipeline
- Test data includes realistic baseball statistics

---

## 7. Summary Points for Closing

### Key Takeaways
1. **Module 2 provides the defensive evaluation component** that complements Module 1's offensive analysis
2. **Knowledge bases are ideal** for encoding position-specific defensive heuristics
3. **Output feeds into Module 3** (position assignment) and **Module 5** (adaptive planning)
4. **No dependencies**—can be developed and tested independently
5. **Interpretable rules** make the system transparent and coach-friendly

### Role in Overall System
- Module 2 is a **foundational component** that enables the system to balance offense and defense
- Without defensive evaluation, the system would only optimize for offense, leading to poor defensive lineups
- The position-specific scores allow the system to make intelligent trade-offs (e.g., strong defender at shortstop vs. strong hitter at DH)

---

## Additional Notes for Q&A

### Potential Questions & Answers

**Q: Why not use machine learning for defensive evaluation?**
A: Knowledge bases provide interpretable rules that coaches can verify and understand. ML would require training data and produce less transparent results.

**Q: How do you handle players who can play multiple positions?**
A: Module 2 evaluates each player at every position they're eligible for, producing separate scores. Module 3 then uses these scores to make the optimal assignment.

**Q: What if a player has missing defensive statistics?**
A: The system uses sensible defaults (e.g., 0 errors, 0 putouts) and the knowledge base rules handle these cases gracefully, producing lower but valid scores.

**Q: How do the weights in the rules (0.4, 0.3, etc.) get determined?**
A: These are domain heuristics based on baseball coaching knowledge about which defensive metrics matter most for each position. They could be tuned based on expert feedback.
