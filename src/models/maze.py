from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class MazeData:
    """Data class representing a maze from the Lens Faucet API."""
    walls: List[List[int]]
    session_id: str
    goal_pos: Tuple[int, int]

@dataclass
class MazeSolution:
    """Data class representing a solved maze with its solution."""
    moves: List[str]
    session_id: str 