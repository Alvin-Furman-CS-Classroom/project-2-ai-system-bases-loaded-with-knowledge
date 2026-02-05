"""
Input parser for Module 2: Defensive Performance Analysis

Parses CSV and JSON files containing defensive statistics.
"""

import json
import csv
from typing import Dict, List, Any
from pathlib import Path


class DefensiveStatsParser:
    """Parser for defensive statistics from CSV or JSON files."""
    
    def __init__(self):
        """Initialize the parser."""
        self.required_fields = ['name', 'fielding_pct', 'errors', 'putouts']
        self.catcher_fields = ['passed_balls', 'caught_stealing_pct']
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse defensive statistics from a file.
        
        Args:
            file_path: Path to CSV or JSON file
            
        Returns:
            List of dictionaries containing player defensive statistics
            
        Raises:
            ValueError: If file format is unsupported or required fields are missing
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() == '.json':
            players = self._parse_json(file_path)
        elif path.suffix.lower() == '.csv':
            players = self._parse_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Use .csv or .json")
        
        return self._validate_and_normalize(players)
    
    def _parse_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'players' in data:
            return data['players']
        else:
            raise ValueError("JSON must contain a list of players or a 'players' key")
    
    def _parse_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV file."""
        players = []
        
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Convert string values to appropriate types
                player = {}
                for key, value in row.items():
                    key = key.strip().lower()
                    if key in ['fielding_pct', 'caught_stealing_pct']:
                        player[key] = float(value) if value else 0.0
                    elif key in ['errors', 'putouts', 'passed_balls']:
                        player[key] = int(value) if value else 0
                    elif key == 'positions':
                        # Handle comma-separated positions
                        player[key] = [p.strip() for p in value.split(',')] if value else []
                    else:
                        player[key] = value
                
                players.append(player)
        
        return players
    
    def _validate_and_normalize(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and normalize player data.
        
        Args:
            players: List of player dictionaries
            
        Returns:
            Normalized list of player dictionaries
        """
        normalized = []
        
        for player in players:
            # Normalize keys to lowercase
            normalized_player = {k.lower().strip(): v for k, v in player.items()}
            
            # Validate required fields
            for field in self.required_fields:
                if field not in normalized_player:
                    raise ValueError(f"Missing required field: {field} for player {normalized_player.get('name', 'unknown')}")
            
            # Handle position eligibility
            if 'positions' not in normalized_player:
                # Try alternative field names
                for alt in ['position', 'eligible_positions', 'pos']:
                    if alt in normalized_player:
                        pos_value = normalized_player[alt]
                        if isinstance(pos_value, str):
                            normalized_player['positions'] = [p.strip() for p in pos_value.split(',')]
                        elif isinstance(pos_value, list):
                            normalized_player['positions'] = pos_value
                        break
                else:
                    # Default to empty list if no positions specified
                    normalized_player['positions'] = []
            
            # Ensure positions is a list
            if isinstance(normalized_player['positions'], str):
                normalized_player['positions'] = [p.strip() for p in normalized_player['positions'].split(',')]
            
            # Identify if player is a catcher
            positions = [p.upper() for p in normalized_player['positions']]
            is_catcher = 'C' in positions
            
            # Validate catcher-specific fields if player is a catcher
            if is_catcher:
                for field in self.catcher_fields:
                    if field not in normalized_player:
                        # Set default values if missing
                        if field == 'passed_balls':
                            normalized_player[field] = 0
                        elif field == 'caught_stealing_pct':
                            normalized_player[field] = 0.0
            
            # Convert numeric fields to appropriate types
            normalized_player['fielding_pct'] = float(normalized_player['fielding_pct'])
            normalized_player['errors'] = int(normalized_player['errors'])
            normalized_player['putouts'] = int(normalized_player['putouts'])
            
            if is_catcher:
                normalized_player['passed_balls'] = int(normalized_player.get('passed_balls', 0))
                normalized_player['caught_stealing_pct'] = float(normalized_player.get('caught_stealing_pct', 0.0))
            
            normalized.append(normalized_player)
        
        return normalized
