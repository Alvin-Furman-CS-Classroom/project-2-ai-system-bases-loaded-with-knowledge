"""
Unit tests for Module 1 matchup rules.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.matchup_rules import (
    handedness_penalty,
    obp_walk_advantage,
    power_vs_era_advantage,
    strikeout_matchup,
    obp_vs_whip_advantage,
    elite_batter_bonus,
    elite_pitcher_penalty,
    power_hitter_bonus,
    contact_hitter_advantage,
    get_all_rules,
    evaluate_single_matchup
)
from module1.models import Batter, Pitcher


class TestMatchupRules(unittest.TestCase):
    """Test cases for matchup rule functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test batters
        self.elite_batter = Batter(
            name="Elite Player",
            ba=0.320,
            k=90,
            obp=0.420,
            slg=0.580,
            hr=35,
            rbi=100,
            handedness="R"
        )
        
        self.lefty_batter = Batter(
            name="Lefty",
            ba=0.280,
            k=110,
            obp=0.360,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="L"
        )
        
        self.switch_hitter = Batter(
            name="Switch",
            ba=0.290,
            k=100,
            obp=0.350,
            slg=0.440,
            hr=18,
            rbi=65,
            handedness="S"
        )
        
        self.power_hitter = Batter(
            name="Power",
            ba=0.260,
            k=140,
            obp=0.340,
            slg=0.520,
            hr=32,
            rbi=85,
            handedness="R"
        )
        
        self.contact_hitter = Batter(
            name="Contact",
            ba=0.310,
            k=80,
            obp=0.380,
            slg=0.420,
            hr=12,
            rbi=60,
            handedness="R"
        )
        
        # Create test pitchers
        self.lefty_pitcher = Pitcher(
            name="Lefty Pitcher",
            era=3.50,
            whip=1.20,
            k_rate=0.25,
            handedness="LHP",
            walk_rate=0.08
        )
        
        self.righty_pitcher = Pitcher(
            name="Righty Pitcher",
            era=2.80,
            whip=1.05,
            k_rate=0.28,
            handedness="RHP",
            walk_rate=0.07
        )
        
        self.elite_pitcher = Pitcher(
            name="Elite Pitcher",
            era=2.20,
            whip=0.95,
            k_rate=0.32,
            handedness="RHP",
            walk_rate=0.05
        )
        
        self.weak_pitcher = Pitcher(
            name="Weak Pitcher",
            era=4.50,
            whip=1.40,
            k_rate=0.22,
            handedness="RHP",
            walk_rate=0.12
        )
        
        self.high_k_pitcher = Pitcher(
            name="High K Pitcher",
            era=3.20,
            whip=1.15,
            k_rate=0.35,
            handedness="RHP",
            walk_rate=0.09
        )
    
    def test_handedness_penalty_same_handed(self):
        """Test handedness penalty for same-handed matchup."""
        # Righty batter vs righty pitcher
        adjustment = handedness_penalty(self.elite_batter, self.righty_pitcher)
        self.assertEqual(adjustment, -15.0)
        
        # Lefty batter vs lefty pitcher
        adjustment = handedness_penalty(self.lefty_batter, self.lefty_pitcher)
        self.assertEqual(adjustment, -15.0)
    
    def test_handedness_penalty_opposite_handed(self):
        """Test handedness bonus for opposite-handed matchup."""
        # Righty batter vs lefty pitcher
        adjustment = handedness_penalty(self.elite_batter, self.lefty_pitcher)
        self.assertEqual(adjustment, 5.0)
        
        # Lefty batter vs righty pitcher
        adjustment = handedness_penalty(self.lefty_batter, self.righty_pitcher)
        self.assertEqual(adjustment, 5.0)
    
    def test_handedness_penalty_switch_hitter(self):
        """Test that switch hitters are not affected by handedness."""
        adjustment = handedness_penalty(self.switch_hitter, self.lefty_pitcher)
        self.assertEqual(adjustment, 0.0)
        
        adjustment = handedness_penalty(self.switch_hitter, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)
    
    def test_handedness_penalty_none_inputs(self):
        """Test handedness penalty with None inputs."""
        adjustment = handedness_penalty(None, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)
        
        adjustment = handedness_penalty(self.elite_batter, None)
        self.assertEqual(adjustment, 0.0)
    
    def test_obp_walk_advantage_positive(self):
        """Test OBP vs walk rate advantage when conditions are met."""
        adjustment = obp_walk_advantage(self.elite_batter, self.weak_pitcher)
        self.assertEqual(adjustment, 8.0)  # OBP 0.420 > 0.350, walk_rate 0.12 > 0.10
    
    def test_obp_walk_advantage_not_met(self):
        """Test OBP vs walk rate when conditions are not met."""
        adjustment = obp_walk_advantage(self.lefty_batter, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)  # OBP 0.360 > 0.350 but walk_rate 0.07 < 0.10
    
    def test_power_vs_era_advantage_strong(self):
        """Test power vs ERA advantage (strong case)."""
        adjustment = power_vs_era_advantage(self.power_hitter, self.weak_pitcher)
        self.assertEqual(adjustment, 10.0)  # SLG 0.520 > 0.500, ERA 4.50 > 4.00
    
    def test_power_vs_era_advantage_moderate(self):
        """Test power vs ERA advantage (moderate case)."""
        pitcher = Pitcher(
            name="Moderate",
            era=3.50,
            whip=1.10,
            k_rate=0.25,
            handedness="RHP",
            walk_rate=0.08
        )
        adjustment = power_vs_era_advantage(self.power_hitter, pitcher)
        self.assertEqual(adjustment, 5.0)  # SLG > 0.500, ERA 3.50 > 3.00 but < 4.00
    
    def test_power_vs_era_advantage_none(self):
        """Test power vs ERA when conditions are not met."""
        adjustment = power_vs_era_advantage(self.lefty_batter, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)  # SLG 0.450 < 0.500
    
    def test_strikeout_matchup_high_k_batter(self):
        """Test strikeout matchup with high K batter vs high K pitcher."""
        high_k_batter = Batter(
            name="High K",
            ba=0.250,
            k=160,
            obp=0.320,
            slg=0.400,
            hr=15,
            rbi=50,
            handedness="R"
        )
        adjustment = strikeout_matchup(high_k_batter, self.high_k_pitcher)
        self.assertEqual(adjustment, -8.0)  # High K batter vs high K pitcher
    
    def test_strikeout_matchup_contact_hitter(self):
        """Test strikeout matchup with contact hitter vs high K pitcher."""
        adjustment = strikeout_matchup(self.contact_hitter, self.high_k_pitcher)
        self.assertEqual(adjustment, 5.0)  # Low K batter (80) vs high K pitcher
    
    def test_strikeout_matchup_no_effect(self):
        """Test strikeout matchup when conditions are not met."""
        adjustment = strikeout_matchup(self.elite_batter, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)  # K rate 0.28 < 0.30
    
    def test_obp_vs_whip_advantage(self):
        """Test OBP vs WHIP advantage."""
        adjustment = obp_vs_whip_advantage(self.elite_batter, self.weak_pitcher)
        self.assertEqual(adjustment, 7.0)  # OBP 0.420 > 0.400, WHIP 1.40 > 1.30
    
    def test_obp_vs_whip_no_advantage(self):
        """Test OBP vs WHIP when conditions are not met."""
        adjustment = obp_vs_whip_advantage(self.lefty_batter, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)  # OBP 0.360 < 0.400
    
    def test_elite_batter_bonus(self):
        """Test elite batter bonus."""
        adjustment = elite_batter_bonus(self.elite_batter, self.righty_pitcher)
        self.assertEqual(adjustment, 6.0)  # BA 0.320 > 0.300, OBP 0.420 > 0.400, SLG 0.580 > 0.500
    
    def test_elite_batter_no_bonus(self):
        """Test elite batter when not elite."""
        adjustment = elite_batter_bonus(self.lefty_batter, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)  # Doesn't meet all elite criteria
    
    def test_elite_pitcher_penalty_strong(self):
        """Test elite pitcher penalty (strong case)."""
        adjustment = elite_pitcher_penalty(self.elite_batter, self.elite_pitcher)
        self.assertEqual(adjustment, -12.0)  # ERA 2.20 < 2.50, WHIP 0.95 < 1.00, K_rate 0.32 > 0.30
    
    def test_elite_pitcher_penalty_moderate(self):
        """Test elite pitcher penalty (moderate case)."""
        moderate_pitcher = Pitcher(
            name="Moderate",
            era=2.80,
            whip=1.05,
            k_rate=0.27,
            handedness="RHP",
            walk_rate=0.07
        )
        adjustment = elite_pitcher_penalty(self.elite_batter, moderate_pitcher)
        self.assertEqual(adjustment, -6.0)  # ERA 2.80 < 3.00, WHIP 1.05 < 1.10, K_rate 0.27 > 0.25
    
    def test_elite_pitcher_no_penalty(self):
        """Test elite pitcher when not elite."""
        adjustment = elite_pitcher_penalty(self.elite_batter, self.weak_pitcher)
        self.assertEqual(adjustment, 0.0)
    
    def test_power_hitter_bonus(self):
        """Test power hitter bonus."""
        adjustment = power_hitter_bonus(self.power_hitter, self.weak_pitcher)
        self.assertEqual(adjustment, 9.0)  # HR 32 > 30, SLG 0.520 > 0.500, ERA 4.50 > 4.00
    
    def test_power_hitter_no_bonus(self):
        """Test power hitter when conditions are not met."""
        adjustment = power_hitter_bonus(self.power_hitter, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)  # ERA 2.80 < 4.00
    
    def test_contact_hitter_advantage(self):
        """Test contact hitter advantage."""
        adjustment = contact_hitter_advantage(self.contact_hitter, self.high_k_pitcher)
        self.assertEqual(adjustment, 7.0)  # K 80 < 100, BA 0.310 > 0.300, K_rate 0.35 > 0.30
    
    def test_contact_hitter_no_advantage(self):
        """Test contact hitter when conditions are not met."""
        adjustment = contact_hitter_advantage(self.contact_hitter, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)  # K_rate 0.28 < 0.30
    
    def test_get_all_rules(self):
        """Test getting all rules."""
        rules = get_all_rules()
        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)
        # Check that all items are callable
        for rule in rules:
            self.assertTrue(callable(rule))
    
    def test_evaluate_single_matchup(self):
        """Test evaluating all rules for a single matchup."""
        adjustment = evaluate_single_matchup(self.elite_batter, self.weak_pitcher)
        # Should combine multiple rules
        self.assertIsInstance(adjustment, float)
        # Should be non-zero (multiple rules should apply)
        self.assertNotEqual(adjustment, 0.0)
    
    def test_evaluate_single_matchup_none_inputs(self):
        """Test evaluating matchup with None inputs."""
        adjustment = evaluate_single_matchup(None, self.righty_pitcher)
        self.assertEqual(adjustment, 0.0)
        
        adjustment = evaluate_single_matchup(self.elite_batter, None)
        self.assertEqual(adjustment, 0.0)


if __name__ == '__main__':
    unittest.main()
