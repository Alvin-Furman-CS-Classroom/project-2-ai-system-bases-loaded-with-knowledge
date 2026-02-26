"""
Data models for Module 1: Matchup Analysis

Defines Batter and Pitcher dataclasses to represent player statistics.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Batter:
    """
    Represents a batter with their offensive statistics.
    
    Attributes:
        name: Player's name
        ba: Batting average (0.0 to 1.0)
        k: Number of strikeouts (non-negative integer)
        obp: On-base percentage (0.0 to 1.0)
        slg: Slugging percentage (0.0 to 1.0)
        hr: Home runs (non-negative integer)
        rbi: Runs batted in (non-negative integer)
        handedness: Batting handedness ('L' for left, 'R' for right, 'S' for switch)
    """
    name: str
    ba: float
    k: int
    obp: float
    slg: float
    hr: int
    rbi: int
    handedness: str
    
    def __post_init__(self):
        """Validate batter data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Batter name cannot be empty")
        
        if not (0.0 <= self.ba <= 1.0):
            raise ValueError(f"Batting average must be between 0.0 and 1.0, got {self.ba}")
        
        if self.k < 0:
            raise ValueError(f"Strikeouts must be non-negative, got {self.k}")
        
        if not (0.0 <= self.obp <= 1.0):
            raise ValueError(f"On-base percentage must be between 0.0 and 1.0, got {self.obp}")
        
        if not (0.0 <= self.slg <= 1.0):
            raise ValueError(f"Slugging percentage must be between 0.0 and 1.0, got {self.slg}")
        
        if self.hr < 0:
            raise ValueError(f"Home runs must be non-negative, got {self.hr}")
        
        if self.rbi < 0:
            raise ValueError(f"Runs batted in must be non-negative, got {self.rbi}")
        
        if self.handedness.upper() not in ['L', 'R', 'S']:
            raise ValueError(f"Handedness must be 'L', 'R', or 'S', got {self.handedness}")
        
        # Normalize handedness to uppercase
        self.handedness = self.handedness.upper()
    
    def is_left_handed(self) -> bool:
        """Check if batter is left-handed."""
        return self.handedness == 'L'
    
    def is_right_handed(self) -> bool:
        """Check if batter is right-handed."""
        return self.handedness == 'R'
    
    def is_switch_hitter(self) -> bool:
        """Check if batter is a switch hitter."""
        return self.handedness == 'S'


@dataclass
class Pitcher:
    """
    Represents an opponent pitcher with their statistics.
    
    Attributes:
        name: Pitcher's name (optional)
        era: Earned run average (non-negative float)
        whip: Walks plus hits per inning pitched (non-negative float)
        k_rate: Strikeout rate (0.0 to 1.0, proportion of batters struck out)
        handedness: Pitching handedness ('LHP' for left-handed pitcher, 'RHP' for right-handed pitcher)
        walk_rate: Walk rate (0.0 to 1.0, proportion of batters walked)
    """
    era: float
    whip: float
    k_rate: float
    handedness: str
    walk_rate: float
    name: Optional[str] = None
    
    def __post_init__(self):
        """Validate pitcher data after initialization."""
        if self.era < 0:
            raise ValueError(f"ERA must be non-negative, got {self.era}")
        
        if self.whip < 0:
            raise ValueError(f"WHIP must be non-negative, got {self.whip}")
        
        if not (0.0 <= self.k_rate <= 1.0):
            raise ValueError(f"Strikeout rate must be between 0.0 and 1.0, got {self.k_rate}")
        
        if self.handedness.upper() not in ['LHP', 'RHP']:
            raise ValueError(f"Handedness must be 'LHP' or 'RHP', got {self.handedness}")
        
        if not (0.0 <= self.walk_rate <= 1.0):
            raise ValueError(f"Walk rate must be between 0.0 and 1.0, got {self.walk_rate}")
        
        # Normalize handedness to uppercase
        self.handedness = self.handedness.upper()
    
    def is_left_handed(self) -> bool:
        """Check if pitcher is left-handed."""
        return self.handedness == 'LHP'
    
    def is_right_handed(self) -> bool:
        """Check if pitcher is right-handed."""
        return self.handedness == 'RHP'
