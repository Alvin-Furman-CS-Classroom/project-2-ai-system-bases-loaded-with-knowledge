"""
Unit tests for defensive_analyzer.py (integration tests)
"""

import unittest
import json
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from module2.defensive_analyzer import analyze_defensive_performance
from module2.knowledge_base import DefensiveFact

# Path to test_data files (used for integration tests without mocks)
_TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'test_data'
_JSON_PATH = _TEST_DATA_DIR / 'defensive_stats.json'
_CSV_PATH = _TEST_DATA_DIR / 'defensive_stats.csv'


class TestDefensiveAnalyzer(unittest.TestCase):
    """Test cases for the main defensive analyzer (integration tests)."""

    def test_analyze_test_data_json(self):
        """Full analysis on test_data/defensive_stats.json returns dict with expected players and scores in 0-100."""
        result = analyze_defensive_performance(str(_JSON_PATH))
        self.assertIsInstance(result, dict)
        self.assertIn('Matt Olson', result)
        self.assertIn('Drake Baldwin', result)
        self.assertIn('Sean Murphy', result)
        for player_name, position_scores in result.items():
            self.assertIsInstance(position_scores, dict)
            for pos, score in position_scores.items():
                self.assertGreaterEqual(score, 0.0, f"{player_name} @ {pos}")
                self.assertLessEqual(score, 100.0, f"{player_name} @ {pos}")

    def test_analyze_test_data_csv(self):
        """Full analysis on test_data/defensive_stats.csv returns dict with expected players and scores in 0-100."""
        result = analyze_defensive_performance(str(_CSV_PATH))
        self.assertIsInstance(result, dict)
        self.assertIn('Matt Olson', result)
        self.assertIn('Drake Baldwin', result)
        for player_name, position_scores in result.items():
            for pos, score in position_scores.items():
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 100.0)
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample test data
        self.sample_players_data = [
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
        
        # Sample facts dictionary (what PositionEvaluator would return)
        self.sample_facts_dict = {
            "John Doe": {
                "1B": DefensiveFact(
                    player_name="John Doe",
                    position="1B",
                    fielding_pct=0.950,
                    errors=5,
                    putouts=150,
                    is_catcher=False
                ),
                "LF": DefensiveFact(
                    player_name="John Doe",
                    position="LF",
                    fielding_pct=0.950,
                    errors=5,
                    putouts=150,
                    is_catcher=False
                )
            },
            "Jane Smith": {
                "C": DefensiveFact(
                    player_name="Jane Smith",
                    position="C",
                    fielding_pct=0.980,
                    errors=2,
                    putouts=200,
                    passed_balls=3,
                    caught_stealing_pct=0.350,
                    is_catcher=True
                )
            }
        }
        
        # Sample scores dictionary (what ScoreCalculator would return)
        self.sample_scores = {
            "John Doe": {
                "1B": 85.5,
                "LF": 82.3
            },
            "Jane Smith": {
                "C": 88.7
            }
        }
    
    @patch('module2.defensive_analyzer.ScoreCalculator')
    @patch('module2.defensive_analyzer.PositionEvaluator')
    @patch('module2.defensive_analyzer.DefensiveKnowledgeBase')
    @patch('module2.defensive_analyzer.DefensiveStatsParser')
    def test_analyze_defensive_performance_json(self, mock_parser_class, mock_kb_class, 
                                                 mock_evaluator_class, mock_calculator_class):
        """Test full analysis pipeline with JSON input."""
        # Create test JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_players_data, f)
            temp_path = f.name
        
        try:
            # Set up mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = self.sample_players_data
            mock_parser_class.return_value = mock_parser
            
            mock_kb = Mock()
            mock_kb_class.return_value = mock_kb
            
            mock_evaluator = Mock()
            mock_evaluator.evaluate_all_players.return_value = self.sample_facts_dict
            mock_evaluator_class.return_value = mock_evaluator
            
            mock_calculator = Mock()
            mock_calculator.calculate_all_scores.return_value = self.sample_scores
            mock_calculator_class.return_value = mock_calculator
            
            # Run the analyzer
            result = analyze_defensive_performance(temp_path)
            
            # Verify parser was called correctly
            mock_parser.parse.assert_called_once_with(temp_path)
            
            # Verify components were initialized
            mock_kb_class.assert_called_once()
            mock_evaluator_class.assert_called_once_with(mock_kb)
            mock_calculator_class.assert_called_once_with(mock_kb)
            
            # Verify evaluator was called with parsed data
            mock_evaluator.evaluate_all_players.assert_called_once_with(self.sample_players_data)
            
            # Verify calculator was called with facts
            mock_calculator.calculate_all_scores.assert_called_once_with(self.sample_facts_dict)
            
            # Verify result
            self.assertEqual(result, self.sample_scores)
            self.assertIn("John Doe", result)
            self.assertIn("Jane Smith", result)
            self.assertEqual(result["John Doe"]["1B"], 85.5)
            self.assertEqual(result["Jane Smith"]["C"], 88.7)
        finally:
            os.unlink(temp_path)
    
    @patch('module2.defensive_analyzer.ScoreCalculator')
    @patch('module2.defensive_analyzer.PositionEvaluator')
    @patch('module2.defensive_analyzer.DefensiveKnowledgeBase')
    @patch('module2.defensive_analyzer.DefensiveStatsParser')
    def test_analyze_defensive_performance_csv(self, mock_parser_class, mock_kb_class,
                                               mock_evaluator_class, mock_calculator_class):
        """Test full analysis pipeline with CSV input."""
        # Create test CSV file
        csv_content = """name,fielding_pct,errors,putouts,positions
John Doe,0.950,5,150,"1B,LF"
Jane Smith,0.980,2,200,C
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            # Set up mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = self.sample_players_data
            mock_parser_class.return_value = mock_parser
            
            mock_kb = Mock()
            mock_kb_class.return_value = mock_kb
            
            mock_evaluator = Mock()
            mock_evaluator.evaluate_all_players.return_value = self.sample_facts_dict
            mock_evaluator_class.return_value = mock_evaluator
            
            mock_calculator = Mock()
            mock_calculator.calculate_all_scores.return_value = self.sample_scores
            mock_calculator_class.return_value = mock_calculator
            
            # Run the analyzer
            result = analyze_defensive_performance(temp_path)
            
            # Verify CSV was parsed
            mock_parser.parse.assert_called_once_with(temp_path)
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("John Doe", result)
            self.assertIn("Jane Smith", result)
        finally:
            os.unlink(temp_path)
    
    @patch('module2.defensive_analyzer.ScoreCalculator')
    @patch('module2.defensive_analyzer.PositionEvaluator')
    @patch('module2.defensive_analyzer.DefensiveKnowledgeBase')
    @patch('module2.defensive_analyzer.DefensiveStatsParser')
    def test_analyze_defensive_performance_empty_positions(self, mock_parser_class, mock_kb_class,
                                                          mock_evaluator_class, mock_calculator_class):
        """Test analysis with player having no eligible positions."""
        # Player with no positions
        players_data = [
            {
                "name": "John Doe",
                "fielding_pct": 0.950,
                "errors": 5,
                "putouts": 150,
                "positions": []
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(players_data, f)
            temp_path = f.name
        
        try:
            # Set up mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = players_data
            mock_parser_class.return_value = mock_parser
            
            mock_kb = Mock()
            mock_kb_class.return_value = mock_kb
            
            # Position evaluator returns empty dict for player with no positions
            mock_evaluator = Mock()
            mock_evaluator.evaluate_all_players.return_value = {}
            mock_evaluator_class.return_value = mock_evaluator
            
            mock_calculator = Mock()
            mock_calculator.calculate_all_scores.return_value = {}
            mock_calculator_class.return_value = mock_calculator
            
            # Run the analyzer
            result = analyze_defensive_performance(temp_path)
            
            # Verify result is empty (player with no positions excluded)
            self.assertEqual(result, {})
        finally:
            os.unlink(temp_path)
    
    @patch('module2.defensive_analyzer.ScoreCalculator')
    @patch('module2.defensive_analyzer.PositionEvaluator')
    @patch('module2.defensive_analyzer.DefensiveKnowledgeBase')
    @patch('module2.defensive_analyzer.DefensiveStatsParser')
    def test_analyze_defensive_performance_score_ordering(self, mock_parser_class, mock_kb_class,
                                                          mock_evaluator_class, mock_calculator_class):
        """Test that better players get higher scores."""
        players_data = [
            {
                "name": "Excellent Player",
                "fielding_pct": 0.990,
                "errors": 1,
                "putouts": 300,
                "positions": ["SS"]
            },
            {
                "name": "Poor Player",
                "fielding_pct": 0.850,
                "errors": 15,
                "putouts": 50,
                "positions": ["SS"]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(players_data, f)
            temp_path = f.name
        
        try:
            # Set up mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = players_data
            mock_parser_class.return_value = mock_parser
            
            mock_kb = Mock()
            mock_kb_class.return_value = mock_kb
            
            mock_evaluator = Mock()
            mock_evaluator.evaluate_all_players.return_value = {
                "Excellent Player": {
                    "SS": DefensiveFact(
                        player_name="Excellent Player",
                        position="SS",
                        fielding_pct=0.990,
                        errors=1,
                        putouts=300,
                        is_catcher=False
                    )
                },
                "Poor Player": {
                    "SS": DefensiveFact(
                        player_name="Poor Player",
                        position="SS",
                        fielding_pct=0.850,
                        errors=15,
                        putouts=50,
                        is_catcher=False
                    )
                }
            }
            mock_evaluator_class.return_value = mock_evaluator
            
            mock_calculator = Mock()
            # Better player should have higher score
            mock_calculator.calculate_all_scores.return_value = {
                "Excellent Player": {"SS": 95.0},
                "Poor Player": {"SS": 70.0}
            }
            mock_calculator_class.return_value = mock_calculator
            
            # Run the analyzer
            result = analyze_defensive_performance(temp_path)
            
            excellent_score = result["Excellent Player"]["SS"]
            poor_score = result["Poor Player"]["SS"]
            
            # Excellent player should have higher score
            self.assertGreater(excellent_score, poor_score)
            self.assertGreaterEqual(excellent_score, 90.0)
            self.assertLess(poor_score, 80.0)
        finally:
            os.unlink(temp_path)
    
    @patch('module2.defensive_analyzer.ScoreCalculator')
    @patch('module2.defensive_analyzer.PositionEvaluator')
    @patch('module2.defensive_analyzer.DefensiveKnowledgeBase')
    @patch('module2.defensive_analyzer.DefensiveStatsParser')
    def test_analyze_defensive_performance_multiple_positions(self, mock_parser_class, mock_kb_class,
                                                              mock_evaluator_class, mock_calculator_class):
        """Test analysis with player having multiple positions."""
        players_data = [
            {
                "name": "Bob Johnson",
                "fielding_pct": 0.920,
                "errors": 8,
                "putouts": 120,
                "positions": ["2B", "SS", "3B"]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(players_data, f)
            temp_path = f.name
        
        try:
            # Set up mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = players_data
            mock_parser_class.return_value = mock_parser
            
            mock_kb = Mock()
            mock_kb_class.return_value = mock_kb
            
            mock_evaluator = Mock()
            mock_evaluator.evaluate_all_players.return_value = {
                "Bob Johnson": {
                    "2B": DefensiveFact("Bob Johnson", "2B", 0.920, 8, 120, is_catcher=False),
                    "SS": DefensiveFact("Bob Johnson", "SS", 0.920, 8, 120, is_catcher=False),
                    "3B": DefensiveFact("Bob Johnson", "3B", 0.920, 8, 120, is_catcher=False)
                }
            }
            mock_evaluator_class.return_value = mock_evaluator
            
            mock_calculator = Mock()
            mock_calculator.calculate_all_scores.return_value = {
                "Bob Johnson": {
                    "2B": 80.0,
                    "SS": 82.0,
                    "3B": 78.0
                }
            }
            mock_calculator_class.return_value = mock_calculator
            
            # Run the analyzer
            result = analyze_defensive_performance(temp_path)
            
            # Verify all positions are included
            self.assertIn("Bob Johnson", result)
            self.assertIn("2B", result["Bob Johnson"])
            self.assertIn("SS", result["Bob Johnson"])
            self.assertIn("3B", result["Bob Johnson"])
            self.assertEqual(len(result["Bob Johnson"]), 3)
        finally:
            os.unlink(temp_path)
    
    @patch('module2.defensive_analyzer.ScoreCalculator')
    @patch('module2.defensive_analyzer.PositionEvaluator')
    @patch('module2.defensive_analyzer.DefensiveKnowledgeBase')
    @patch('module2.defensive_analyzer.DefensiveStatsParser')
    def test_analyze_defensive_performance_catcher(self, mock_parser_class, mock_kb_class,
                                                    mock_evaluator_class, mock_calculator_class):
        """Test analysis with catcher player."""
        players_data = [
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
            json.dump(players_data, f)
            temp_path = f.name
        
        try:
            # Set up mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = players_data
            mock_parser_class.return_value = mock_parser
            
            mock_kb = Mock()
            mock_kb_class.return_value = mock_kb
            
            mock_evaluator = Mock()
            mock_evaluator.evaluate_all_players.return_value = {
                "Jane Smith": {
                    "C": DefensiveFact(
                        player_name="Jane Smith",
                        position="C",
                        fielding_pct=0.980,
                        errors=2,
                        putouts=200,
                        passed_balls=3,
                        caught_stealing_pct=0.350,
                        is_catcher=True
                    )
                }
            }
            mock_evaluator_class.return_value = mock_evaluator
            
            mock_calculator = Mock()
            mock_calculator.calculate_all_scores.return_value = {
                "Jane Smith": {"C": 88.7}
            }
            mock_calculator_class.return_value = mock_calculator
            
            # Run the analyzer
            result = analyze_defensive_performance(temp_path)
            
            # Verify catcher is evaluated
            self.assertIn("Jane Smith", result)
            self.assertIn("C", result["Jane Smith"])
            self.assertEqual(result["Jane Smith"]["C"], 88.7)
        finally:
            os.unlink(temp_path)
    
    @patch('module2.defensive_analyzer.ScoreCalculator')
    @patch('module2.defensive_analyzer.PositionEvaluator')
    @patch('module2.defensive_analyzer.DefensiveKnowledgeBase')
    @patch('module2.defensive_analyzer.DefensiveStatsParser')
    def test_analyze_defensive_performance_pipeline_order(self, mock_parser_class, mock_kb_class,
                                                           mock_evaluator_class, mock_calculator_class):
        """Test that the pipeline executes in the correct order."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_players_data, f)
            temp_path = f.name
        
        try:
            # Set up mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = self.sample_players_data
            mock_parser_class.return_value = mock_parser
            
            mock_kb = Mock()
            mock_kb_class.return_value = mock_kb
            
            mock_evaluator = Mock()
            mock_evaluator.evaluate_all_players.return_value = self.sample_facts_dict
            mock_evaluator_class.return_value = mock_evaluator
            
            mock_calculator = Mock()
            mock_calculator.calculate_all_scores.return_value = self.sample_scores
            mock_calculator_class.return_value = mock_calculator
            
            # Run the analyzer
            analyze_defensive_performance(temp_path)
            
            # Verify call order using call_count and call order
            # Parser should be called first
            self.assertEqual(mock_parser.parse.call_count, 1)
            
            # Components should be initialized
            self.assertEqual(mock_kb_class.call_count, 1)
            self.assertEqual(mock_evaluator_class.call_count, 1)
            self.assertEqual(mock_calculator_class.call_count, 1)
            
            # Evaluator should be called with parsed data
            self.assertEqual(mock_evaluator.evaluate_all_players.call_count, 1)
            
            # Calculator should be called with facts
            self.assertEqual(mock_calculator.calculate_all_scores.call_count, 1)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
