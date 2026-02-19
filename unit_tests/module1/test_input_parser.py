"""
Unit tests for Module 1 input parser.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module1.input_parser import MatchupDataParser
from module1.models import Batter, Pitcher


class TestInputParser(unittest.TestCase):
    """Test cases for input parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = MatchupDataParser()
        self.test_data_dir = Path(__file__).parent.parent.parent / 'test_data'
    
    def test_parse_json(self):
        """Test parsing JSON file."""
        json_file = self.test_data_dir / 'matchup_stats.json'
        if json_file.exists():
            batters, pitcher = self.parser.parse(str(json_file))
            
            self.assertIsInstance(batters, list)
            self.assertGreater(len(batters), 0)
            self.assertIsInstance(batters[0], Batter)
            self.assertIsInstance(pitcher, Pitcher)
            
            # Check first batter
            self.assertEqual(batters[0].name, "Mike Trout")
            self.assertEqual(batters[0].ba, 0.306)
            
            # Check pitcher
            self.assertEqual(pitcher.name, "Gerrit Cole")
            self.assertEqual(pitcher.era, 2.63)
    
    def test_parse_csv(self):
        """Test parsing CSV file."""
        csv_file = self.test_data_dir / 'matchup_stats.csv'
        if csv_file.exists():
            batters, pitcher = self.parser.parse(str(csv_file))
            
            self.assertIsInstance(batters, list)
            self.assertGreater(len(batters), 0)
            self.assertIsInstance(batters[0], Batter)
            self.assertIsInstance(pitcher, Pitcher)
    
    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse('nonexistent_file.json')
    
    def test_parse_invalid_format(self):
        """Test parsing file with invalid format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test data")
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                self.parser.parse(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_create_batter_from_dict(self):
        """Test creating batter from dictionary."""
        data = {
            'name': 'Test Player',
            'ba': '0.300',
            'k': '100',
            'obp': '0.350',
            'slg': '0.450',
            'hr': '20',
            'rbi': '70',
            'handedness': 'R'
        }
        batter = self.parser._create_batter(data)
        self.assertIsInstance(batter, Batter)
        self.assertEqual(batter.name, 'Test Player')
        self.assertEqual(batter.ba, 0.300)
    
    def test_create_pitcher_from_dict(self):
        """Test creating pitcher from dictionary."""
        data = {
            'name': 'Test Pitcher',
            'era': '3.50',
            'whip': '1.20',
            'k_rate': '0.25',
            'handedness': 'RHP',
            'walk_rate': '0.08'
        }
        pitcher = self.parser._create_pitcher(data)
        self.assertIsInstance(pitcher, Pitcher)
        self.assertEqual(pitcher.name, 'Test Pitcher')
        self.assertEqual(pitcher.era, 3.50)
    
    def test_pitcher_handedness_conversion(self):
        """Test conversion of pitcher handedness formats."""
        # Test 'L' -> 'LHP'
        data = {'era': 3.0, 'whip': 1.0, 'k_rate': 0.25, 'handedness': 'L', 'walk_rate': 0.08}
        pitcher = self.parser._create_pitcher(data)
        self.assertEqual(pitcher.handedness, 'LHP')
        
        # Test 'R' -> 'RHP'
        data['handedness'] = 'R'
        pitcher = self.parser._create_pitcher(data)
        self.assertEqual(pitcher.handedness, 'RHP')


if __name__ == '__main__':
    unittest.main()
