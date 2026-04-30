# Module 1: Matchup Analysis with First-Order Logic
## Baseball Lineup Optimization System

---

## Slide 1: Module 1 Overview & Purpose

### **Module 1: Matchup Analysis**
**Topic:** First-Order Logic  
**Goal:** Predict offensive performance scores (0-100) for each batter against opponent pitchers

---

### **What Module 1 Does**
- Analyzes how **Atlanta Braves batters** perform against **MLB pitchers**
- Uses **first-order logic rules** with quantifiers (∀, ∃) to evaluate matchups
- Produces **performance scores** that feed into later modules (CSP, Search, Planning)

---

### **Inputs & Outputs**

**Inputs:**
- **Batter Statistics:** BA, OBP, SLG, HR, RBI, K, handedness (L/R/S)
- **Pitcher Statistics:** ERA, WHIP, K rate, walk rate, handedness (LHP/RHP)
- **Data Source:** Real 2025 MLB statistics (26 Braves batters, 157 MLB pitchers)

**Outputs:**
- Performance scores (0-100) for each batter-pitcher matchup
- Dictionary format: `{batter_name: score}` or `{batter_name: {pitcher_name: score}}`

---

### **Key Features**
✅ **Realistic Data:** 2025 Braves batting stats aligned with Module 2 defensive data  
✅ **Comprehensive Coverage:** 157 unique MLB pitchers from 2025 season  
✅ **Multiple Analysis Modes:** Single pitcher, single batter, or full matrix analysis  
✅ **First-Order Logic:** Universal (∀) and existential (∃) quantifiers for rule evaluation

---

## Slide 2: Technical Implementation & Results

### **Module 1: Technical Architecture**

---

### **First-Order Logic Implementation**

**Universal Quantifier (∀):**
- "For all batters, if OBP > 0.350 and pitcher walk rate > 0.10, then increase score"
- "For all left-handed batters, if pitcher is LHP, then reduce score by 15%"

**Existential Quantifier (∃):**
- "There exists a batter such that SLG > 0.500 and pitcher ERA > 4.00, then increase score"

---

### **Rule Examples**

| Rule Type | Condition | Adjustment |
|-----------|-----------|------------|
| **Handedness** | Same-handed matchup (L vs LHP) | -15.0 penalty |
| **OBP Advantage** | Batter OBP > 0.350, Pitcher walk rate > 0.10 | +8.0 bonus |
| **Power Matchup** | Batter SLG > 0.500, Pitcher ERA > 4.00 | +10.0 bonus |
| **Strikeout Risk** | Batter K rate high, Pitcher K rate > 0.25 | -12.0 penalty |

---

### **System Architecture**

```
Input Files (JSON/CSV)
    ↓
MatchupDataParser → Batter & Pitcher Objects
    ↓
RuleEvaluator + LogicEngine → Apply FOL Rules
    ↓
ScoreCalculator → Final Performance Scores (0-100)
    ↓
Output: {batter_name: score}
```

---

### **Test Results & Validation**

✅ **132 Unit Tests - All Passing**  
- Input parsing (JSON/CSV formats)  
- First-order logic quantifiers (∀, ∃)  
- Individual matchup rules  
- End-to-end score calculation  
- Matrix analysis (5 batters × 157 pitchers = 785 matchups)

**Test Data:**
- 26 Braves batters (aligned with Module 2)
- 157 unique MLB pitchers (2025 season)
- Realistic 2025 statistics from Baseball-Reference

---

### **Integration Ready**
Module 1 outputs feed directly into:
- **Module 3 (CSP):** Offensive scores for position assignment
- **Module 4 (Search):** Performance data for batting order optimization
- **Module 5 (Planning):** Matchup predictions for in-game adjustments
