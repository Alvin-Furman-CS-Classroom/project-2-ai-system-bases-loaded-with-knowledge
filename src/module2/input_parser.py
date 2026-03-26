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
            normalized_player = self._normalize_keys(player)
            self._validate_required_fields(normalized_player)
            normalized_player = self._normalize_positions(normalized_player)
            normalized_player = self._ensure_catcher_defaults(normalized_player)
            normalized_player = self._convert_numeric_fields(normalized_player)
            normalized.append(normalized_player)
        
        return normalized
    
    def _normalize_keys(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize dictionary keys to lowercase."""
        return {k.lower().strip(): v for k, v in player.items()}
    
    def _validate_required_fields(self, player: Dict[str, Any]) -> None:
        """Validate that all required fields are present."""
        for field in self.required_fields:
            if field not in player:
                raise ValueError(f"Missing required field: {field} for player {player.get('name', 'unknown')}")
    
    def _normalize_positions(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize position field to a list format."""
        if 'positions' not in player:
            # Try alternative field names
            for alt in ['position', 'eligible_positions', 'pos']:
                if alt in player:
                    pos_value = player[alt]
                    if isinstance(pos_value, str):
                        player['positions'] = [p.strip() for p in pos_value.split(',')]
                    elif isinstance(pos_value, list):
                        player['positions'] = pos_value
                    break
            else:
                # Default to empty list if no positions specified
                player['positions'] = []
        
        # Ensure positions is a list
        if isinstance(player['positions'], str):
            player['positions'] = [p.strip() for p in player['positions'].split(',')]
        
        return player
    
    def _ensure_catcher_defaults(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for catcher-specific fields if player is a catcher."""
        positions = [p.upper() for p in player['positions']]
        is_catcher = 'C' in positions
        
        if is_catcher:
            for field in self.catcher_fields:
                if field not in player:
                    if field == 'passed_balls':
                        player[field] = 0
                    elif field == 'caught_stealing_pct':
                        player[field] = 0.0
        
        return player
    
    def _convert_numeric_fields(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Convert numeric fields to appropriate types."""
        player['fielding_pct'] = float(player['fielding_pct'])
        player['errors'] = int(player['errors'])
        player['putouts'] = int(player['putouts'])
        
        positions = [p.upper() for p in player['positions']]
        if 'C' in positions:
            player['passed_balls'] = int(player.get('passed_balls', 0))
            player['caught_stealing_pct'] = float(player.get('caught_stealing_pct', 0.0))
        
        return player
