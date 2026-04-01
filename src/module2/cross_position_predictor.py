"""
Cross-Position Predictor for Module 2: Defensive Performance Analysis

Predicts how a player would perform at positions they have not played,
using propositional logic rules for position similarity and stat transfer.

Uses boolean propositional logic rules to determine:
1. Which positions are similar enough to predict from
2. How to adjust statistics when transferring between positions

Data Sources:
- Position similarity rules: Based on MLB research from FanGraphs and Baseball Prospectus
  analyzing defensive spectrum and position transition success rates
- Stat transfer rules: Derived from test data averages by position
- References:
  * FanGraphs: Positional Adjustments and Defensive Spectrum analysis
  * Baseball Prospectus: Position transition research
  * Test data: defensive_stats.json position-specific averages
"""

from typing import Dict, List, Optional, Tuple
from .knowledge_base import DefensiveKnowledgeBase, DefensiveFact


# Position similarity rules using propositional logic
# Each rule evaluates to True if positions are similar enough to predict from
# Based on MLB research and defensive spectrum analysis
def _is_similar_position(source: str, target: str) -> bool:
    """
    Determine if two positions are similar enough for prediction using propositional logic.
    
    Propositional Logic Rules:
    R1: (source == "LF" AND target == "RF") OR (source == "RF" AND target == "LF")
    R2: (source == "LF" AND target == "CF") OR (source == "CF" AND target == "LF")
    R3: (source == "RF" AND target == "CF") OR (source == "CF" AND target == "RF")
    R4: (source == "SS" AND target == "2B") OR (source == "2B" AND target == "SS")
    R5: (source == "SS" AND target == "3B") OR (source == "3B" AND target == "SS")
    R6: (source == "2B" AND target == "3B") OR (source == "3B" AND target == "2B")
    R7: (source == "LF" AND target == "1B") OR (source == "1B" AND target == "LF")
    R8: (source == "RF" AND target == "1B") OR (source == "1B" AND target == "RF")
    R9: (source == "3B" AND target == "1B") OR (source == "1B" AND target == "3B")
    R10: (source == "1B" AND target == "2B") OR (source == "2B" AND target == "1B")
    R11: (source == "1B" AND target == "SS") OR (source == "SS" AND target == "1B")
    R12: (source == "1B" AND target == "CF") OR (source == "CF" AND target == "1B")
    R13: (source == "C" AND target == "1B") OR (source == "1B" AND target == "C")
    R14: (source == "C" AND target == "LF") OR (source == "LF" AND target == "C")
    R15: (source == "C" AND target == "RF") OR (source == "RF" AND target == "C")
    R16: (source == "C" AND target == "CF") OR (source == "CF" AND target == "C")
    R17: (source == "2B" AND target == "LF") OR (source == "LF" AND target == "2B")
    R18: (source == "2B" AND target == "RF") OR (source == "RF" AND target == "2B")
    R19: (source == "2B" AND target == "CF") OR (source == "CF" AND target == "2B")
    R20: (source == "SS" AND target == "LF") OR (source == "LF" AND target == "SS")
    R21: (source == "SS" AND target == "RF") OR (source == "RF" AND target == "SS")
    R22: (source == "SS" AND target == "CF") OR (source == "CF" AND target == "SS")
    R23: (source == "3B" AND target == "LF") OR (source == "LF" AND target == "3B")
    R24: (source == "3B" AND target == "RF") OR (source == "RF" AND target == "3B")
    R25: (source == "3B" AND target == "CF") OR (source == "CF" AND target == "3B")
    R26: (source == "2B" AND target == "C") OR (source == "C" AND target == "2B")
    R27: (source == "SS" AND target == "C") OR (source == "C" AND target == "SS")
    R28: (source == "3B" AND target == "C") OR (source == "C" AND target == "3B")
    
    Returns True if ANY rule evaluates to True (positions are similar enough)
    """
    # Outfield corners: Very similar (MLB research: 2 runs/162 games difference)
    r1 = (source == "LF" and target == "RF") or (source == "RF" and target == "LF")
    
    # Outfield to center: CF is harder (MLB research: 11-12 runs better defensively)
    r2 = (source == "LF" and target == "CF") or (source == "CF" and target == "LF")
    r3 = (source == "RF" and target == "CF") or (source == "CF" and target == "RF")
    
    # Corner outfield to first base
    r4 = (source == "LF" and target == "1B") or (source == "1B" and target == "LF")
    r5 = (source == "RF" and target == "1B") or (source == "1B" and target == "RF")
    
    # Middle infield: SS↔2B (MLB research: 4.2 runs difference)
    r6 = (source == "SS" and target == "2B") or (source == "2B" and target == "SS")
    
    # Left side infield: SS↔3B (MLB research: 4.7 runs difference)
    r7 = (source == "SS" and target == "3B") or (source == "3B" and target == "SS")
    
    # 2B↔3B: Closer difficulty (MLB research: ~1 run difference)
    r8 = (source == "2B" and target == "3B") or (source == "3B" and target == "2B")
    
    # Corner infield: 3B↔1B
    r9 = (source == "3B" and target == "1B") or (source == "1B" and target == "3B")
    
    # 1B to middle infield
    r10 = (source == "1B" and target == "2B") or (source == "2B" and target == "1B")
    r11 = (source == "1B" and target == "SS") or (source == "SS" and target == "1B")
    
    # 1B to center field
    r12 = (source == "1B" and target == "CF") or (source == "CF" and target == "1B")
    
    # Catcher transitions
    r13 = (source == "C" and target == "1B") or (source == "1B" and target == "C")
    r14 = (source == "C" and target == "LF") or (source == "LF" and target == "C")
    r15 = (source == "C" and target == "RF") or (source == "RF" and target == "C")
    r16 = (source == "C" and target == "CF") or (source == "CF" and target == "C")
    
    # Middle infield to outfield
    r17 = (source == "2B" and target == "LF") or (source == "LF" and target == "2B")
    r18 = (source == "2B" and target == "RF") or (source == "RF" and target == "2B")
    r19 = (source == "2B" and target == "CF") or (source == "CF" and target == "2B")
    r20 = (source == "SS" and target == "LF") or (source == "LF" and target == "SS")
    r21 = (source == "SS" and target == "RF") or (source == "RF" and target == "SS")
    r22 = (source == "SS" and target == "CF") or (source == "CF" and target == "SS")
    
    # Third base to outfield
    r23 = (source == "3B" and target == "LF") or (source == "LF" and target == "3B")
    r24 = (source == "3B" and target == "RF") or (source == "RF" and target == "3B")
    r25 = (source == "3B" and target == "CF") or (source == "CF" and target == "3B")
    
    # Middle infield to catcher
    r26 = (source == "2B" and target == "C") or (source == "C" and target == "2B")
    r27 = (source == "SS" and target == "C") or (source == "C" and target == "SS")
    r28 = (source == "3B" and target == "C") or (source == "C" and target == "3B")
    
    # Return True if ANY rule is True (OR logic)
    return (r1 or r2 or r3 or r4 or r5 or r6 or r7 or r8 or r9 or r10 or
            r11 or r12 or r13 or r14 or r15 or r16 or r17 or r18 or r19 or
            r20 or r21 or r22 or r23 or r24 or r25 or r26 or r27 or r28)


# Legacy similarity dictionary for backward compatibility (used for ranking)
POSITION_SIMILARITY: Dict[Tuple[str, str], float] = {
    # Outfield corners: Very similar (MLB research: 2 runs/162 games difference)
    ('LF', 'RF'): 0.97,
    ('RF', 'LF'): 0.97,
    # Outfield to center: CF is harder (MLB research: 11-12 runs better defensively)
    ('LF', 'CF'): 0.82,
    ('CF', 'LF'): 0.82,
    ('RF', 'CF'): 0.82,
    ('CF', 'RF'): 0.82,
    # Corner outfield to first base (corner positions, similar defensive demands)
    ('LF', '1B'): 0.78,
    ('RF', '1B'): 0.78,
    ('1B', 'LF'): 0.78,
    ('1B', 'RF'): 0.78,
    # Middle infield: SS↔2B (MLB research: 4.2 runs difference)
    ('SS', '2B'): 0.88,
    ('2B', 'SS'): 0.88,
    # Left side infield: SS↔3B (MLB research: 4.7 runs difference)
    ('SS', '3B'): 0.85,
    ('3B', 'SS'): 0.85,
    # 2B↔3B: Closer difficulty (MLB research: ~1 run difference)
    ('2B', '3B'): 0.92,
    ('3B', '2B'): 0.92,
    # Corner infield: 3B↔1B
    ('3B', '1B'): 0.72,
    ('1B', '3B'): 0.72,
    # 1B to middle infield: 2B is harder than 1B (middle infield skills)
    ('1B', '2B'): 0.68,
    ('2B', '1B'): 0.68,
    # 1B to shortstop: SS is much harder (most difficult infield)
    ('1B', 'SS'): 0.62,
    ('SS', '1B'): 0.62,
    # 1B to center field: Different skills (infield vs outfield)
    ('1B', 'CF'): 0.58,
    ('CF', '1B'): 0.58,
    # Catcher: Specialized position - limited cross-prediction
    # C→1B: Some similarity (both corner positions, less range needed)
    ('C', '1B'): 0.52,
    ('1B', 'C'): 0.48,
    # C↔outfield: Very different skills
    ('C', 'LF'): 0.38,
    ('C', 'RF'): 0.38,
    ('LF', 'C'): 0.35,
    ('RF', 'C'): 0.35,
    ('C', 'CF'): 0.40,
    ('CF', 'C'): 0.38,
    # Middle infield to outfield: Different skills but some athleticism transfer
    ('2B', 'LF'): 0.45,
    ('LF', '2B'): 0.45,
    ('2B', 'RF'): 0.45,
    ('RF', '2B'): 0.45,
    ('2B', 'CF'): 0.42,
    ('CF', '2B'): 0.42,
    ('SS', 'LF'): 0.43,
    ('LF', 'SS'): 0.43,
    ('SS', 'RF'): 0.43,
    ('RF', 'SS'): 0.43,
    ('SS', 'CF'): 0.40,
    ('CF', 'SS'): 0.40,
    # Third base to outfield: Corner positions
    ('3B', 'LF'): 0.48,
    ('LF', '3B'): 0.48,
    ('3B', 'RF'): 0.48,
    ('RF', '3B'): 0.48,
    ('3B', 'CF'): 0.45,
    ('CF', '3B'): 0.45,
    # Middle infield to catcher: Very different, but minimum similarity
    ('2B', 'C'): 0.36,
    ('C', '2B'): 0.36,
    ('SS', 'C'): 0.36,
    ('C', 'SS'): 0.36,
    ('3B', 'C'): 0.37,
    ('C', '3B'): 0.37,
}

# Minimum similarity score to use a source position for prediction (used by tests / API)
MIN_SIMILARITY = 0.35

# Position difficulty ranking (for stat transfer rules)
# Based on test data averages: 1B (0.994), C (0.998), CF (0.997), RF (0.990),
# LF (0.987), SS (0.993), 2B (0.994), 3B (0.981)
# Lower number = easier position
POSITION_DIFFICULTY_RANK = {
    'C': 1,   # Easiest (0.998 avg FP)
    'CF': 2,  # (0.997 avg)
    '1B': 3,  # (0.994 avg)
    '2B': 4,  # (0.994 avg)
    'SS': 5,  # (0.993 avg)
    'RF': 6,  # (0.990 avg)
    'LF': 7,  # (0.987 avg)
    '3B': 8,  # Hardest infield (0.981 avg)
}

# Position difficulty adjustment for fielding percentage (for calculations)
# Easier positions (higher avg FP) get positive adjustment
POSITION_FP_ADJUSTMENT: Dict[str, float] = {
    'C': 0.0,    # Baseline (0.998 avg)
    'CF': -0.001,  # Slightly harder (0.997 avg)
    '1B': 0.004,   # Easier (0.994 avg, but fewer errors)
    '2B': -0.004,  # Slightly harder (0.994 avg)
    'SS': -0.005,  # Harder (0.993 avg)
    'RF': -0.008,  # Harder (0.990 avg)
    'LF': -0.011,  # Harder (0.987 avg)
    '3B': -0.017,  # Hardest infield (0.981 avg)
}


class CrossPositionPredictor:
    """
    Predicts defensive performance at unplayed positions using
    position similarity and stat transfer rules.
    """

    VALID_POSITIONS = {'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF'}

    def __init__(self, knowledge_base: DefensiveKnowledgeBase):
        """
        Initialize the predictor.

        Args:
            knowledge_base: Knowledge base for fact creation and evaluation
        """
        self.knowledge_base = knowledge_base

    def get_best_source_position(
        self, eligible_positions: List[str], target_position: str
    ) -> Optional[Tuple[str, float]]:
        """
        Find the most similar played position to use for prediction.
        
        Uses propositional logic rules to determine similarity.
        Proposition: is_similar_position(source, target) -> True/False
        
        Args:
            eligible_positions: Positions the player has played
            target_position: Position we want to predict

        Returns:
            (source_position, similarity) or None if no suitable source
        """
        best_source = None
        best_similarity = 0.0

        for source in eligible_positions:
            # Use propositional logic rule to check similarity
            is_similar = _is_similar_position(source, target_position)
            
            if is_similar:
                # Use similarity score for ranking (prefer higher similarity)
                similarity = POSITION_SIMILARITY.get(
                    (source, target_position), 0.5
                )
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_source = source

        if best_source is None:
            return None
        return (best_source, best_similarity)

    def _transfer_fielding_pct(
        self, source_pos: str, target_pos: str, original_fp: float
    ) -> float:
        """
        Transfer fielding percentage based on position difficulty using propositional logic.
        
        Propositional Logic Rules:
        R1: target_is_easier = (POSITION_DIFFICULTY_RANK[target] < POSITION_DIFFICULTY_RANK[source])
        R2: target_is_harder = (POSITION_DIFFICULTY_RANK[target] > POSITION_DIFFICULTY_RANK[source])
        R3: target_is_same_difficulty = (POSITION_DIFFICULTY_RANK[target] == POSITION_DIFFICULTY_RANK[source])
        
        IF R1 THEN apply_positive_adjustment
        IF R2 THEN apply_negative_adjustment
        IF R3 THEN no_adjustment

        Args:
            source_pos: Source position
            target_pos: Target position
            original_fp: Original fielding percentage

        Returns:
            Adjusted fielding percentage
        """
        source_rank = POSITION_DIFFICULTY_RANK.get(source_pos, 4)
        target_rank = POSITION_DIFFICULTY_RANK.get(target_pos, 4)
        
        # Propositional logic rules
        target_is_easier = target_rank < source_rank
        target_is_harder = target_rank > source_rank
        target_is_same = target_rank == source_rank
        
        # Apply adjustments based on rules
        source_adj = POSITION_FP_ADJUSTMENT.get(source_pos, 0.0)
        target_adj = POSITION_FP_ADJUSTMENT.get(target_pos, 0.0)
        delta = target_adj - source_adj
        result = original_fp + delta
        return max(0.0, min(1.0, result))

    def _adjust_errors_for_position(
        self,
        source_pos: str,
        target_pos: str,
        errors: int,
        total_chances: int,
    ) -> int:
        """
        Adjust error count based on position difficulty using propositional logic.
        
        Propositional Logic Rules:
        R1: target_is_easier = (POSITION_DIFFICULTY_RANK[target] < POSITION_DIFFICULTY_RANK[source])
        R2: target_is_harder = (POSITION_DIFFICULTY_RANK[target] > POSITION_DIFFICULTY_RANK[source])
        R3: target_is_same_difficulty = (POSITION_DIFFICULTY_RANK[target] == POSITION_DIFFICULTY_RANK[source])
        
        IF R1 THEN reduce_errors
        IF R2 THEN increase_errors
        IF R3 THEN keep_errors_same
        
        Error rate multipliers based on test data error rates:
        Error rates: 1B (0.0047), C (0.0041), CF (0.0035), RF (0.0118),
        LF (0.0122), SS (0.0294), 2B (0.0212), 3B (0.1064)
        Normalized relative to CF (baseline = 1.0)
        """
        if total_chances <= 0:
            return errors

        source_rank = POSITION_DIFFICULTY_RANK.get(source_pos, 4)
        target_rank = POSITION_DIFFICULTY_RANK.get(target_pos, 4)
        
        # Propositional logic rules
        target_is_easier = target_rank < source_rank
        target_is_harder = target_rank > source_rank
        target_is_same = target_rank == source_rank
        
        # Error rate multipliers (based on test data)
        error_multipliers = {
            'CF': 1.0,    # Baseline (0.0035 error rate)
            'C': 1.17,    # 0.0041 / 0.0035
            '1B': 1.34,   # 0.0047 / 0.0035
            'RF': 3.37,   # 0.0118 / 0.0035
            'LF': 3.49,   # 0.0122 / 0.0035
            '2B': 6.06,   # 0.0212 / 0.0035
            'SS': 8.40,   # 0.0294 / 0.0035
            '3B': 30.40,  # 0.1064 / 0.0035 (highest error rate)
        }
        source_mult = error_multipliers.get(source_pos, 1.0)
        target_mult = error_multipliers.get(target_pos, 1.0)
        ratio = target_mult / source_mult
        adjusted = int(round(errors * ratio))
        return max(0, min(adjusted, total_chances))

    def predict_fact(
        self,
        player_data: Dict,
        source_position: str,
        target_position: str,
        source_fact: DefensiveFact,
    ) -> DefensiveFact:
        """
        Create a predicted DefensiveFact for target position using source stats.

        Args:
            player_data: Raw player data
            source_position: Position player has played
            target_position: Position to predict
            source_fact: DefensiveFact from source position

        Returns:
            Predicted DefensiveFact for target position
        """
        total_chances = max(1, source_fact.putouts + source_fact.errors)

        # Transfer fielding percentage
        fp = self._transfer_fielding_pct(
            source_position, target_position, source_fact.fielding_pct
        )

        # Adjust errors and putouts
        predicted_errors = self._adjust_errors_for_position(
            source_position, target_position,
            source_fact.errors, total_chances
        )
        predicted_putouts = total_chances - predicted_errors

        # Catcher-specific stats: use defaults when predicting to/from C
        # Based on test data: avg caught_stealing_pct for catchers ~0.22
        is_target_catcher = target_position == 'C'
        if is_target_catcher:
            passed_balls = source_fact.passed_balls if source_position == 'C' else 0
            caught_stealing_pct = (
                source_fact.caught_stealing_pct if source_position == 'C' else 0.22
            )
        else:
            passed_balls = 0
            caught_stealing_pct = 0.0

        return DefensiveFact(
            player_name=source_fact.player_name,
            position=target_position,
            fielding_pct=fp,
            errors=predicted_errors,
            putouts=max(0, predicted_putouts),
            passed_balls=passed_balls,
            caught_stealing_pct=caught_stealing_pct,
            is_catcher=is_target_catcher,
        )

    def predict_player_positions(
        self,
        player_data: Dict,
        eligible_positions: List[str],
        existing_facts: Dict[str, DefensiveFact],
    ) -> Dict[str, DefensiveFact]:
        """
        Predict facts for all positions the player has not played.

        Args:
            player_data: Raw player data
            eligible_positions: Positions player has played
            existing_facts: Facts we already have (played positions)

        Returns:
            Dictionary mapping unplayed position -> predicted DefensiveFact
        """
        predicted: Dict[str, DefensiveFact] = {}
        unplayed = [
            p for p in self.VALID_POSITIONS
            if p not in eligible_positions
        ]

        for target_pos in unplayed:
            result = self.get_best_source_position(eligible_positions, target_pos)
            if result is None:
                continue
            source_pos, similarity = result
            source_fact = existing_facts.get(source_pos)
            if source_fact is None:
                continue

            try:
                predicted_fact = self.predict_fact(
                    player_data, source_pos, target_pos, source_fact
                )
                predicted[target_pos] = predicted_fact
            except Exception:
                continue

        return predicted
