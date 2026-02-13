"""
Position Evaluator for Module 2: Defensive Performance Analysis

Determines which positions to evaluate for each player and constructs
DefensiveFact objects for each player-position combination.
"""

from typing import Dict, List
from .knowledge_base import DefensiveKnowledgeBase, DefensiveFact


class PositionEvaluator:
    """Evaluates defensive performance for eligible positions."""
    
    # Valid defensive positions
    VALID_POSITIONS = {'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF'}
    
    def __init__(self, knowledge_base: DefensiveKnowledgeBase):
        """
        Initialize position evaluator.
        
        Args:
            knowledge_base: Knowledge base containing evaluation rules
        """
        # Store reference to the knowledge base for fact creation/evaluation
        self.knowledge_base = knowledge_base
    
    def get_eligible_positions(self, player_data: Dict) -> List[str]:
        """
        Get list of eligible positions for a player.
        
        Args:
            player_data: Dictionary containing player data with 'positions' field
            
        Returns:
            List of valid position strings
        """
        positions = player_data.get('positions')

        if positions is None:
            return []

        # Normalize input: accept list or comma-separated string
        if isinstance(positions, str):
            # split on common delimiters
            parts = [p.strip().upper() for p in positions.replace('/', ',').split(',') if p.strip()]
        elif isinstance(positions, (list, tuple)):
            parts = [str(p).strip().upper() for p in positions if str(p).strip()]
        else:
            return []

        # Filter to valid defensive positions while preserving order
        eligible = [p for p in parts if p in self.VALID_POSITIONS]
        return eligible
    
    def evaluate_player_positions(self, player_data: Dict) -> Dict[str, DefensiveFact]:
        """
        Create defensive facts for all eligible positions of a player.
        
        Args:
            player_data: Dictionary containing player statistics
            
        Returns:
            Dictionary mapping position to DefensiveFact
        """
        facts: Dict[str, DefensiveFact] = {}
        positions = self.get_eligible_positions(player_data)

        for pos in positions:
            # Prefer using the knowledge base to build facts if available
            fact = None
            try:
                fact = self.knowledge_base.add_fact(player_data, pos)
            except Exception:
                fact = None

            # Fallback: construct DefensiveFact directly
            if fact is None:
                fact = DefensiveFact(
                    player_name=player_data.get('player_name', 'Unknown'),
                    position=pos,
                    fielding_pct=float(player_data.get('fielding_pct', 0.0)),
                    errors=int(player_data.get('errors', 0)),
                    putouts=int(player_data.get('putouts', 0)),
                    passed_balls=int(player_data.get('passed_balls', 0)),
                    caught_stealing_pct=float(player_data.get('caught_stealing_pct', 0.0)),
                    is_catcher=(pos == 'C')
                )

            facts[pos] = fact

        return facts
    
    def evaluate_all_players(self, players_data: List[Dict]) -> Dict[str, Dict[str, DefensiveFact]]:
        """
        Evaluate all positions for all players.
        
        Args:
            players_data: List of player data dictionaries
            
        Returns:
            Dictionary mapping player_name to position facts
            Format: {player_name: {position: DefensiveFact}}
        """
        results: Dict[str, Dict[str, DefensiveFact]] = {}

        for pdata in players_data:
            # Expect player name in data; fall back to a generated key if missing
            player_name = pdata.get('player_name') or pdata.get('name') or str(pdata.get('id', 'unknown'))
            position_facts = self.evaluate_player_positions(pdata)
            results[player_name] = position_facts

        return results
