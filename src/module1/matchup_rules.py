"""
Matchup Rules for Module 1: Matchup Analysis

Defines all matchup rules as functions that evaluate batter-pitcher matchups
and return score adjustments. Rules encode baseball knowledge about how
different statistics and characteristics affect performance.
"""

from typing import Tuple
from .models import Batter, Pitcher


def handedness_penalty(batter: Batter, pitcher: Pitcher) -> float:
    """
    Apply penalty for same-handed matchups.
    
    Rule: Same-handed matchups (L vs LHP, R vs RHP) are generally disadvantageous
    for batters. Switch hitters are not penalized.
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment (negative for penalty, positive for bonus)
        - Same-handed: -15.0 penalty
        - Opposite-handed: +5.0 bonus
        - Switch hitter: 0.0 (no adjustment)
    """
    if batter is None or pitcher is None:
        return 0.0
    
    # Switch hitters are not affected by handedness matchups
    if batter.is_switch_hitter():
        return 0.0
    
    # Same-handed matchup (disadvantageous for batter)
    batter_hand = batter.handedness
    pitcher_hand = pitcher.handedness[0]  # 'LHP' -> 'L', 'RHP' -> 'R'
    
    if batter_hand == pitcher_hand:
        return -15.0  # Penalty for same-handed matchup
    else:
        return 5.0  # Bonus for opposite-handed matchup


def obp_walk_advantage(batter: Batter, pitcher: Pitcher) -> float:
    """
    Evaluate advantage when batter's OBP significantly exceeds pitcher's walk rate.
    
    Rule: If batter OBP > 0.350 and pitcher walk rate > 0.10, the batter has
    an advantage (high OBP batter against high walk rate pitcher).
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment:
        - If OBP > 0.350 and walk_rate > 0.10: +8.0 bonus
        - Otherwise: 0.0
    """
    if batter is None or pitcher is None:
        return 0.0
    
    if batter.obp > 0.350 and pitcher.walk_rate > 0.10:
        return 8.0
    
    return 0.0


def power_vs_era_advantage(batter: Batter, pitcher: Pitcher) -> float:
    """
    Evaluate advantage when batter's slugging significantly exceeds pitcher's ERA.
    
    Rule: If batter SLG > 0.500 and pitcher ERA > 4.00, the batter has a power
    advantage against a weaker pitcher.
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment:
        - If SLG > 0.500 and ERA > 4.00: +10.0 bonus
        - If SLG > 0.500 and ERA > 3.00: +5.0 bonus
        - Otherwise: 0.0
    """
    if batter is None or pitcher is None:
        return 0.0
    
    if batter.slg > 0.500:
        if pitcher.era > 4.00:
            return 10.0
        elif pitcher.era > 3.00:
            return 5.0
    
    return 0.0


def strikeout_matchup(batter: Batter, pitcher: Pitcher) -> float:
    """
    Evaluate strikeout risk based on batter strikeouts vs pitcher strikeout rate.
    
    Rule: High strikeout batters against high strikeout rate pitchers face increased risk.
    Low strikeout batters against high strikeout rate pitchers have an advantage.
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment:
        - If batter has high K count (>150) and pitcher K_rate > 0.30: -8.0 penalty
        - If batter has low K count (<100) and pitcher K_rate > 0.30: +5.0 bonus
        - Otherwise: 0.0
    """
    if batter is None or pitcher is None:
        return 0.0
    
    if pitcher.k_rate > 0.30:  # High strikeout pitcher
        if batter.k > 150:  # High strikeout batter
            return -8.0  # Penalty: strikeout-prone batter vs strikeout pitcher
        elif batter.k < 100:  # Low strikeout batter
            return 5.0  # Bonus: contact hitter vs strikeout pitcher
    
    return 0.0


def obp_vs_whip_advantage(batter: Batter, pitcher: Pitcher) -> float:
    """
    Evaluate advantage when batter's OBP is high relative to pitcher's WHIP.
    
    Rule: High OBP batters (>0.400) against high WHIP pitchers (>1.30) have advantage.
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment:
        - If OBP > 0.400 and WHIP > 1.30: +7.0 bonus
        - Otherwise: 0.0
    """
    if batter is None or pitcher is None:
        return 0.0
    
    if batter.obp > 0.400 and pitcher.whip > 1.30:
        return 7.0
    
    return 0.0


def elite_batter_bonus(batter: Batter, pitcher: Pitcher) -> float:
    """
    Apply bonus for elite batters (high BA, OBP, SLG combination).
    
    Rule: Elite batters (BA > 0.300, OBP > 0.400, SLG > 0.500) get a bonus
    regardless of pitcher, representing their overall skill.
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment:
        - If BA > 0.300, OBP > 0.400, SLG > 0.500: +6.0 bonus
        - Otherwise: 0.0
    """
    if batter is None or pitcher is None:
        return 0.0
    
    if batter.ba > 0.300 and batter.obp > 0.400 and batter.slg > 0.500:
        return 6.0
    
    return 0.0


def elite_pitcher_penalty(batter: Batter, pitcher: Pitcher) -> float:
    """
    Apply penalty when facing elite pitchers.
    
    Rule: Elite pitchers (low ERA < 2.50, low WHIP < 1.00, high K_rate > 0.30)
    reduce all batters' effectiveness.
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment:
        - If ERA < 2.50, WHIP < 1.00, K_rate > 0.30: -12.0 penalty
        - If ERA < 3.00, WHIP < 1.10, K_rate > 0.25: -6.0 penalty
        - Otherwise: 0.0
    """
    if batter is None or pitcher is None:
        return 0.0
    
    if pitcher.era < 2.50 and pitcher.whip < 1.00 and pitcher.k_rate > 0.30:
        return -12.0  # Elite pitcher penalty
    elif pitcher.era < 3.00 and pitcher.whip < 1.10 and pitcher.k_rate > 0.25:
        return -6.0  # Very good pitcher penalty
    
    return 0.0


def power_hitter_bonus(batter: Batter, pitcher: Pitcher) -> float:
    """
    Apply bonus for power hitters against weaker pitchers.
    
    Rule: Power hitters (HR > 30, SLG > 0.500) get bonus against pitchers
    with higher ERA (> 4.00).
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment:
        - If HR > 30, SLG > 0.500, ERA > 4.00: +9.0 bonus
        - Otherwise: 0.0
    """
    if batter is None or pitcher is None:
        return 0.0
    
    if batter.hr > 30 and batter.slg > 0.500 and pitcher.era > 4.00:
        return 9.0
    
    return 0.0


def contact_hitter_advantage(batter: Batter, pitcher: Pitcher) -> float:
    """
    Apply advantage for contact hitters against strikeout pitchers.
    
    Rule: Contact hitters (low K < 100, high BA > 0.300) have advantage
    against high strikeout rate pitchers (> 0.30).
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Score adjustment:
        - If K < 100, BA > 0.300, K_rate > 0.30: +7.0 bonus
        - Otherwise: 0.0
    """
    if batter is None or pitcher is None:
        return 0.0
    
    if batter.k < 100 and batter.ba > 0.300 and pitcher.k_rate > 0.30:
        return 7.0
    
    return 0.0


def get_all_rules() -> list:
    """
    Get a list of all matchup rule functions.
    
    Returns:
        List of rule functions that take (Batter, Pitcher) and return float
    """
    return [
        handedness_penalty,
        obp_walk_advantage,
        power_vs_era_advantage,
        strikeout_matchup,
        obp_vs_whip_advantage,
        elite_batter_bonus,
        elite_pitcher_penalty,
        power_hitter_bonus,
        contact_hitter_advantage
    ]


def evaluate_single_matchup(batter: Batter, pitcher: Pitcher) -> float:
    """
    Evaluate all rules for a single batter-pitcher matchup.
    
    This function applies all matchup rules and returns the total adjustment.
    
    Args:
        batter: Batter object
        pitcher: Pitcher object
    
    Returns:
        Total score adjustment from all rules
    """
    if batter is None or pitcher is None:
        return 0.0
    
    total_adjustment = 0.0
    
    for rule in get_all_rules():
        try:
            adjustment = rule(batter, pitcher)
            total_adjustment += adjustment
        except Exception:
            # If a rule fails, continue with other rules
            continue
    
    return total_adjustment
