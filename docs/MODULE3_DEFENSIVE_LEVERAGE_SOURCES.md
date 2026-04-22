# Module 3 — Research basis for defensive leverage multipliers

## Primary source (published methodology)

**FanGraphs Sabermetrics Library — *Positional Adjustment***  
URL: <https://library.fangraphs.com/misc/war/positional-adjustment/>  
Author: Piper Slowinski; describes how FanGraphs incorporates **positional adjustment** into **WAR**.

The article gives a **table of runs per full defensive season** (1,458 innings ≈ 162 games) by position. These values summarize **how much harder or easier** each position is relative to the others when comparing players on a common scale—grounded in **analysis of players who changed positions** (methodology attributed to work including **Tom Tango**, linked from that page).

### FanGraphs table (runs per full season at position)

| Position | Adjustment (runs) |
|----------|-------------------|
| C        | +12.5             |
| 1B       | -12.5             |
| 2B       | +2.5              |
| SS       | +7.5              |
| 3B       | +2.5              |
| LF       | -7.5              |
| CF       | +2.5              |
| RF       | -7.5              |

*(DH is listed in FanGraphs as -17.5; we do not use DH in defensive lineup assignment.)*

**Pitcher (P):** Not in this fielding table. Module 3 uses **no Module 2 defensive grade** for `P` (defensive term is 0); leverage for `P` is set to **neutral (multiplier 1.0)** so the optional profile does not invent pitching-fielding data.

## How we use it in code

We do **not** recompute WAR. We use the **ordering and relative magnitudes** of the official adjustments as a **transparent proxy** for “how much defensive quality at this slot matters in aggregate player evaluation,” and map runs → multipliers with a **small linear scale** so values stay near 1.0:

\[
\text{multiplier}(\text{pos}) = 1 + s \times \text{runs}_{\text{FG}}(\text{pos})
\]

Default \(s\) is **`DEFAULT_LEVERAGE_LINEAR_SCALE`** (`0.016` in `src/module3/position_assignment.py`) → roughly **0.8 … 1.2** for MLB positions in the table (C highest, 1B lowest).

**Caveat (stated on FanGraphs):** these adjustments are **estimates** and “guides more than firm rules”; the game evolves. Our mapping is **documented and reproducible**; you may change `linear_scale` or supply an alternate run table if you adopt newer research (e.g. follow-up pieces linked from the FanGraphs article).

## Further reading (from FanGraphs page)

- Tom Tango, *Positional adjustments — any updates?* (linked from FanGraphs Library page)  
- Hardball Times / follow-ups on re-examining WAR’s defensive spectrum (linked from same page)

## Implementation

See `src/module3/position_assignment.py`:

- `FGRAPHS_POSITIONAL_ADJUSTMENT_RUNS` — numeric table from the Library article  
- `DEFAULT_LEVERAGE_LINEAR_SCALE` — default \(s\) in `multiplier = 1 + s × runs`  
- `defense_multipliers_from_positional_adjustment_runs()` — runs → multipliers  
- `DEFENSIVE_LEVERAGE_UP_THE_MIDDLE` — default dict used when `defensive_stress_profile="up_the_middle"`
