"""
Unit tests for Module 1 data models.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.models import Batter, Pitcher


class TestBatter(unittest.TestCase):
    """Test cases for Batter dataclass."""
    
    def test_valid_batter(self):
        """Test creating a valid batter."""
        batter = Batter(
            name="Test Player",
            ba=0.300,
            k=100,
            obp=0.350,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="R"
        )
        self.assertEqual(batter.name, "Test Player")
        self.assertEqual(batter.ba, 0.300)
        self.assertFalse(batter.is_left_handed())
        self.assertTrue(batter.is_right_handed())
    
    def test_left_handed_batter(self):
        """Test left-handed batter."""
        batter = Batter(
            name="Lefty",
            ba=0.280,
            k=120,
            obp=0.340,
            slg=0.420,
            hr=15,
            rbi=60,
            handedness="L"
        )
        self.assertTrue(batter.is_left_handed())
        self.assertFalse(batter.is_right_handed())
    
    def test_switch_hitter(self):
        """Test switch hitter."""
        batter = Batter(
            name="Switch",
            ba=0.290,
            k=110,
            obp=0.360,
            slg=0.440,
            hr=18,
            rbi=65,
            handedness="S"
        )
        self.assertTrue(batter.is_switch_hitter())
    
    def test_invalid_batting_average(self):
        """Test validation of batting average."""
        with self.assertRaises(ValueError):
            Batter(
                name="Test",
                ba=1.5,  # Invalid: > 1.0
                k=100,
                obp=0.350,
                slg=0.450,
                hr=20,
                rbi=70,
                handedness="R"
            )
    
    def test_invalid_handedness(self):
        """Test validation of handedness."""
        with self.assertRaises(ValueError):
            Batter(
                name="Test",
                ba=0.300,
                k=100,
                obp=0.350,
                slg=0.450,
                hr=20,
                rbi=70,
                handedness="X"  # Invalid
            )
    
    def test_handedness_normalization(self):
        """Test that handedness is normalized to uppercase."""
        batter = Batter(
            name="Test",
            ba=0.300,
            k=100,
            obp=0.350,
            slg=0.450,
            hr=20,
            rbi=70,
            handedness="l"  # Lowercase
        )
        self.assertEqual(batter.handedness, "L")


class TestPitcher(unittest.TestCase):
    """Test cases for Pitcher dataclass."""
    
    def test_valid_pitcher(self):
        """Test creating a valid pitcher."""
        pitcher = Pitcher(
            name="Test Pitcher",
            era=3.50,
            whip=1.20,
            k_rate=0.25,
            handedness="RHP",
            walk_rate=0.08
        )
        self.assertEqual(pitcher.name, "Test Pitcher")
        self.assertEqual(pitcher.era, 3.50)
        self.assertTrue(pitcher.is_right_handed())
        self.assertFalse(pitcher.is_left_handed())
    
    def test_left_handed_pitcher(self):
        """Test left-handed pitcher."""
        pitcher = Pitcher(
            era=2.80,
            whip=1.10,
            k_rate=0.28,
            handedness="LHP",
            walk_rate=0.07
        )
        self.assertTrue(pitcher.is_left_handed())
        self.assertFalse(pitcher.is_right_handed())
    
    def test_pitcher_without_name(self):
        """Test pitcher without name."""
        pitcher = Pitcher(
            era=3.00,
            whip=1.15,
            k_rate=0.26,
            handedness="RHP",
            walk_rate=0.09
        )
        self.assertIsNone(pitcher.name)
    
    def test_invalid_era(self):
        """Test validation of ERA."""
        with self.assertRaises(ValueError):
            Pitcher(
                era=-1.0,  # Invalid: negative
                whip=1.20,
                k_rate=0.25,
                handedness="RHP",
                walk_rate=0.08
            )
    
    def test_invalid_k_rate(self):
        """Test validation of strikeout rate."""
        with self.assertRaises(ValueError):
            Pitcher(
                era=3.50,
                whip=1.20,
                k_rate=1.5,  # Invalid: > 1.0
                handedness="RHP",
                walk_rate=0.08
            )
    
    def test_handedness_normalization(self):
        """Test that handedness is normalized to uppercase."""
        pitcher = Pitcher(
            era=3.50,
            whip=1.20,
            k_rate=0.25,
            handedness="lhp",  # Lowercase
            walk_rate=0.08
        )
        self.assertEqual(pitcher.handedness, "LHP")


if __name__ == '__main__':
    unittest.main()
