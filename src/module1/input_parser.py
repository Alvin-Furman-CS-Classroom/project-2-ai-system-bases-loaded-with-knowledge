"""
Input parser for Module 1: Matchup Analysis

Parses CSV and JSON files containing batter and pitcher statistics.
"""

import json
import csv
from typing import List, Tuple, Dict, Any
from pathlib import Path

from .models import Batter, Pitcher


class MatchupDataParser:
    """Parser for matchup statistics from CSV or JSON files."""
    
    def __init__(self):
        """Initialize the parser."""
        self.batter_fields = ['name', 'ba', 'k', 'obp', 'slg', 'hr', 'rbi', 'handedness']
        self.pitcher_fields = ['era', 'whip', 'k_rate', 'handedness', 'walk_rate']
    
    def parse(self, file_path: str) -> Tuple[List[Batter], Pitcher]:
        """
        Parse matchup statistics from a file.
        
        Args:
            file_path: Path to CSV or JSON file
            
        Returns:
            Tuple of (list of Batter objects, Pitcher object)
            
        Raises:
            ValueError: If file format is unsupported or required fields are missing
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() == '.json':
            return self._parse_json(file_path)
        elif path.suffix.lower() == '.csv':
            return self._parse_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Use .csv or .json")
    
    def _parse_json(self, file_path: str) -> Tuple[List[Batter], Pitcher]:
        """Parse JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle two possible JSON formats:
        # Format 1: {"batters": [...], "pitcher": {...}}
        # Format 2: {"batters": [...], "pitcher_stats": {...}}
        if isinstance(data, dict):
            batters_data = data.get('batters', [])
            pitcher_data = data.get('pitcher') or data.get('pitcher_stats', {})
        elif isinstance(data, list):
            # If it's a list, assume all entries are batters and pitcher is separate
            # This format would need pitcher data passed separately
            batters_data = data
            pitcher_data = {}
        else:
            raise ValueError("Invalid JSON format: expected object with 'batters' and 'pitcher' keys")
        
        if not pitcher_data:
            raise ValueError("Pitcher statistics not found in JSON file")
        
        batters = [self._create_batter(b) for b in batters_data]
        pitcher = self._create_pitcher(pitcher_data)
        
        return batters, pitcher
    
    def _parse_csv(self, file_path: str) -> Tuple[List[Batter], Pitcher]:
        """Parse CSV file."""
        batters = []
        pitcher_data = None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Check if this row is a pitcher (has pitcher-specific fields)
                if 'era' in row and row['era']:
                    if pitcher_data is not None:
                        raise ValueError("Multiple pitcher entries found in CSV file")
                    pitcher_data = row
                else:
                    # This is a batter row
                    batter = self._create_batter(row)
                    batters.append(batter)
        
        if pitcher_data is None:
            raise ValueError("Pitcher statistics not found in CSV file")
        
        if not batters:
            raise ValueError("No batter statistics found in CSV file")
        
        pitcher = self._create_pitcher(pitcher_data)
        
        return batters, pitcher
    
    def _create_batter(self, data: Dict[str, Any]) -> Batter:
        """Create a Batter object from dictionary data."""
        # Handle missing or empty values
        name = str(data.get('name', '')).strip()
        if not name:
            raise ValueError("Batter name is required")
        
        # Convert string values to appropriate types
        ba = self._to_float(data.get('ba', 0))
        k = self._to_int(data.get('k', 0))
        obp = self._to_float(data.get('obp', 0))
        slg = self._to_float(data.get('slg', 0))
        hr = self._to_int(data.get('hr', 0))
        rbi = self._to_int(data.get('rbi', 0))
        handedness = str(data.get('handedness', 'R')).strip()
        
        return Batter(
            name=name,
            ba=ba,
            k=k,
            obp=obp,
            slg=slg,
            hr=hr,
            rbi=rbi,
            handedness=handedness
        )
    
    def _create_pitcher(self, data: Dict[str, Any]) -> Pitcher:
        """Create a Pitcher object from dictionary data."""
        # Handle missing or empty values
        name = data.get('name')
        if name:
            name = str(name).strip() or None
        
        era = self._to_float(data.get('era', 0))
        whip = self._to_float(data.get('whip', 0))
        k_rate = self._to_float(data.get('k_rate', 0))
        walk_rate = self._to_float(data.get('walk_rate', 0))
        
        # Handle handedness - could be 'LHP'/'RHP' or 'L'/'R'
        handedness = str(data.get('handedness', 'RHP')).strip().upper()
        if handedness in ['L', 'LEFT']:
            handedness = 'LHP'
        elif handedness in ['R', 'RIGHT']:
            handedness = 'RHP'
        
        return Pitcher(
            name=name,
            era=era,
            whip=whip,
            k_rate=k_rate,
            handedness=handedness,
            walk_rate=walk_rate
        )
    
    def _to_float(self, value: Any) -> float:
        """Convert value to float, handling empty strings and None."""
        if value is None or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert '{value}' to float")
    
    def _to_int(self, value: Any) -> int:
        """Convert value to int, handling empty strings and None."""
        if value is None or value == '':
            return 0
        try:
            return int(float(value))  # Convert via float to handle "1.0" strings
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert '{value}' to int")
