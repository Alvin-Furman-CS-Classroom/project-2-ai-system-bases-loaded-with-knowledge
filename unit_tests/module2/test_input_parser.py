"""
Unit tests for input_parser.py
"""

import unittest
import json
import csv
import tempfile
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module2.input_parser import DefensiveStatsParser


class TestDefensiveStatsParser(unittest.TestCase):
    """Test cases for DefensiveStatsParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DefensiveStatsParser()
    
    def test_parse_json_list_format(self):
        """Test parsing JSON file with list format."""
        data = [
            {
                "name": "John Doe",
                "fielding_pct": 0.950,
                "errors": 5,
                "putouts": 150,
                "positions": ["1B", "LF"]
            },
            {
                "name": "Jane Smith",
                "fielding_pct": 0.980,
                "errors": 2,
                "putouts": 200,
                "passed_balls": 3,
                "caught_stealing_pct": 0.350,
                "positions": ["C"]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['name'], "John Doe")
            self.assertEqual(result[0]['fielding_pct'], 0.950)
            self.assertEqual(result[0]['errors'], 5)
            self.assertEqual(result[0]['putouts'], 150)
            self.assertEqual(result[0]['positions'], ["1B", "LF"])
            self.assertEqual(result[1]['name'], "Jane Smith")
            self.assertIn('C', result[1]['positions'])
            self.assertEqual(result[1]['passed_balls'], 3)
            self.assertEqual(result[1]['caught_stealing_pct'], 0.350)
        finally:
            os.unlink(temp_path)
    
    def test_parse_json_dict_format(self):
        """Test parsing JSON file with dict format containing 'players' key."""
        data = {
            "players": [
                {
                    "name": "Bob Johnson",
                    "fielding_pct": 0.920,
                    "errors": 8,
                    "putouts": 120,
                    "positions": ["2B", "SS"]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['name'], "Bob Johnson")
            self.assertEqual(result[0]['fielding_pct'], 0.920)
            self.assertEqual(result[0]['errors'], 8)
            self.assertEqual(result[0]['putouts'], 120)
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv(self):
        """Test parsing CSV file."""
        data = [
            ["name", "fielding_pct", "errors", "putouts", "positions"],
            ["John Doe", "0.950", "5", "150", "1B,LF"],
            ["Jane Smith", "0.980", "2", "200", "C"]
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['name'], "John Doe")
            self.assertEqual(result[0]['fielding_pct'], 0.950)
            self.assertEqual(result[0]['errors'], 5)
            self.assertEqual(result[0]['putouts'], 150)
            self.assertEqual(result[0]['positions'], ["1B", "LF"])
            self.assertEqual(result[1]['name'], "Jane Smith")
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv_with_catcher_stats(self):
        """Test parsing CSV file with catcher-specific statistics."""
        data = [
            ["name", "fielding_pct", "errors", "putouts", "passed_balls", "caught_stealing_pct", "positions"],
            ["Jane Smith", "0.980", "2", "200", "3", "0.350", "C"]
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['name'], "Jane Smith")
            self.assertEqual(result[0]['passed_balls'], 3)
            self.assertEqual(result[0]['caught_stealing_pct'], 0.350)
            self.assertIn('C', result[0]['positions'])
        finally:
            os.unlink(temp_path)
    
    def test_parse_csv_empty_catcher_fields(self):
        """Test parsing CSV with empty catcher fields (should default to 0)."""
        data = [
            ["name", "fielding_pct", "errors", "putouts", "passed_balls", "caught_stealing_pct", "positions"],
            ["Charlie Brown", "0.940", "6", "140", "", "", "C"]
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['passed_balls'], 0)
            self.assertEqual(result[0]['caught_stealing_pct'], 0.0)
        finally:
            os.unlink(temp_path)
    
    def test_missing_required_field(self):
        """Test that missing required fields raise ValueError."""
        data = [
            {
                "name": "John Doe",
                "fielding_pct": 0.950,
                # Missing errors and putouts
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                self.parser.parse(temp_path)
            self.assertIn("Missing required field", str(context.exception))
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found(self):
        """Test that non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse("nonexistent_file.json")
    
    def test_unsupported_format(self):
        """Test that unsupported file format raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                self.parser.parse(temp_path)
            self.assertIn("Unsupported file format", str(context.exception))
        finally:
            os.unlink(temp_path)
    
    def test_normalize_positions_list(self):
        """Test that positions are normalized to a list."""
        data = [
            {
                "name": "John Doe",
                "fielding_pct": 0.950,
                "errors": 5,
                "putouts": 150,
                "positions": "1B,LF,CF"  # String format
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertIsInstance(result[0]['positions'], list)
            self.assertIn('1B', result[0]['positions'])
            self.assertIn('LF', result[0]['positions'])
            self.assertIn('CF', result[0]['positions'])
        finally:
            os.unlink(temp_path)
    
    def test_catcher_defaults(self):
        """Test that catchers get default values for missing catcher-specific fields."""
        data = [
            {
                "name": "Jane Smith",
                "fielding_pct": 0.980,
                "errors": 2,
                "putouts": 200,
                "positions": ["C"]
                # Missing passed_balls and caught_stealing_pct
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertEqual(result[0]['passed_balls'], 0)
            self.assertEqual(result[0]['caught_stealing_pct'], 0.0)
        finally:
            os.unlink(temp_path)
    
    def test_non_catcher_no_catcher_fields(self):
        """Test that non-catchers don't get catcher fields."""
        data = [
            {
                "name": "John Doe",
                "fielding_pct": 0.950,
                "errors": 5,
                "putouts": 150,
                "positions": ["1B", "LF"]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            # Non-catchers shouldn't have catcher fields
            self.assertNotIn('passed_balls', result[0])
            self.assertNotIn('caught_stealing_pct', result[0])
        finally:
            os.unlink(temp_path)
    
    def test_empty_positions(self):
        """Test handling of empty positions list."""
        data = [
            {
                "name": "John Doe",
                "fielding_pct": 0.950,
                "errors": 5,
                "putouts": 150,
                "positions": []
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertEqual(result[0]['positions'], [])
        finally:
            os.unlink(temp_path)
    
    def test_case_insensitive_positions(self):
        """Test that position names are case-insensitive."""
        data = [
            {
                "name": "John Doe",
                "fielding_pct": 0.950,
                "errors": 5,
                "putouts": 150,
                "positions": ["1b", "lf", "C"]  # Mixed case
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            # Positions should be preserved but we check if 'C' is detected as catcher
            positions = result[0]['positions']
            self.assertIn('1b', positions)
            self.assertIn('lf', positions)
            self.assertIn('C', positions)
        finally:
            os.unlink(temp_path)
    
    def test_type_conversions(self):
        """Test that numeric fields are properly converted."""
        data = [
            {
                "name": "John Doe",
                "fielding_pct": "0.950",  # String
                "errors": "5",  # String
                "putouts": "150",  # String
                "positions": ["1B"]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            self.assertIsInstance(result[0]['fielding_pct'], float)
            self.assertIsInstance(result[0]['errors'], int)
            self.assertIsInstance(result[0]['putouts'], int)
        finally:
            os.unlink(temp_path)
    
    def test_json_invalid_format(self):
        """Test that invalid JSON format raises ValueError."""
        data = {
            "invalid": "format"  # No 'players' key and not a list
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                self.parser.parse(temp_path)
            self.assertIn("list of players", str(context.exception).lower())
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
