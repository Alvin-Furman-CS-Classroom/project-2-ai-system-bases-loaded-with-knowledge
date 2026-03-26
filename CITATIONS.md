# Citations for Cross-Position Prediction Statistics

## Position Similarity Scores

### FanGraphs - Positional Adjustments and Defensive Spectrum
- **Source**: FanGraphs Community Blog - "How the Positional Adjustments Have Changed Over Time"
- **URL**: https://community.fangraphs.com/how-the-positional-adjustments-have-changed-over-time-part-1/
- **Key Findings**:
  - LF vs RF: ~2 runs difference per 162 games
  - CF vs corner outfield: ~11-12 runs better defensively
  - SS vs 3B: ~4.7 runs difference
  - SS vs 2B: ~4.2 runs difference
  - 2B vs 3B: ~1 run difference

### Inside the Book - Fielding Position Adjustments
- **Source**: Inside the Book - "Playing The Percentages In Baseball"
- **URL**: https://insidethebook.com/ee/index.php/site/article/fielding_position_adjustments
- **Key Findings**:
  - CF is 8.7 runs per season better than corner outfielders
  - SS is 4.7 runs better than 3B and 4.2 runs better than 2B

### FanGraphs - Historical Position Adjustments
- **Source**: FanGraphs Baseball Blog - "Historical Position Adjustments"
- **URL**: https://blogs.fangraphs.com/historical-position-adjustments/
- **Key Findings**:
  - UZR positional adjustments revised with 2008 data
  - Confirms defensive spectrum rankings

### Baseball Prospectus - Position Transition Research
- **Source**: Baseball Prospectus - "Baseball Therapy: Learning A New Position Is Free"
- **URL**: https://www.baseballprospectus.com/news/article/30076/baseball-therapy-learning-a-new-position-is-free/
- **Key Findings**:
  - Position transitions don't necessarily harm offensive development
  - Experience at a position matters significantly

### SABR - Position Swap Value
- **Source**: Society for American Baseball Research - "The Value of Swapping Positions"
- **URL**: https://sabr.org/latest/the-value-of-swapping-positions
- **Key Findings**:
  - Historical analysis of position swaps
  - Right-field-to-center-field swap occurs most frequently

## Fielding Statistics

### Baseball-Reference - Standard Fielding Statistics
- **Source**: Baseball-Reference.com - "Major League Baseball Standard Fielding"
- **URL**: https://www.baseball-reference.com/leagues/majors/field.shtml
- **Usage**: Reference for position-specific fielding percentage and error statistics

### Test Data Analysis
- **Source**: Project test data (`test_data/defensive_stats.json`)
- **Calculated Averages**:
  - Fielding percentages by position
  - Error rates normalized to CF baseline
  - Position-specific defensive statistics

## Implementation Notes

The cross-position prediction system combines:
1. **MLB research data** on defensive spectrum and position difficulty
2. **Statistical analysis** of test data to derive error rate multipliers
3. **Position similarity scores** based on defensive value differences (runs saved)

All similarity scores and adjustments are derived from these sources and calculated from the provided test data.
