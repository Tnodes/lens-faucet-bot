import heapq
from typing import List, Tuple, Dict, Optional
from src.models.maze import MazeData


class MazeSolver:
    @staticmethod
    def can_move(current_val: int, next_val: int, direction: str) -> bool:
        """
        Checks if movement is possible between cells based on wall bitmasks.
        
        Wall bitmasks:
        1 = top wall
        2 = right wall
        4 = bottom wall
        8 = left wall
        """
        direction_bits = {
            'up':    (1, 4),  # current top wall, next bottom wall
            'right': (2, 8),  # current right wall, next left wall
            'down':  (4, 1),  # current bottom wall, next top wall
            'left':  (8, 2),  # current left wall, next right wall
        }
        curr_bit, opp_bit = direction_bits[direction]
        
        # Check if either cell has a blocking wall
        return not (current_val & curr_bit or next_val & opp_bit)

    @staticmethod
    def get_neighbors(r: int, c: int, maze: List[List[int]]) -> List[Tuple[int, int, str]]:
        """Get valid neighboring cells and their directions."""
        directions = [
            (-1, 0, 'up'),
            (0, 1, 'right'),
            (1, 0, 'down'),
            (0, -1, 'left')
        ]
        neighbors = []
        
        rows, cols = len(maze), len(maze[0])
        current_val = maze[r][c]
        
        for dr, dc, move_name in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                next_val = maze[nr][nc]
                if MazeSolver.can_move(current_val, next_val, move_name):
                    neighbors.append((nr, nc, move_name))
        return neighbors

    @staticmethod
    def manhattan_distance(r: int, c: int, goal_r: int, goal_c: int) -> int:
        """Calculate Manhattan distance heuristic."""
        return abs(r - goal_r) + abs(c - goal_c)

    @staticmethod
    def reconstruct_path(came_from: Dict[Tuple[int, int], Tuple[int, int, str]], 
                        goal: Tuple[int, int]) -> List[str]:
        """Reconstruct the solution path from the came_from dictionary."""
        path_moves = []
        current = goal
        
        while current in came_from:
            prev_r, prev_c, move_dir = came_from[current]
            path_moves.append(move_dir)
            current = (prev_r, prev_c)
            
        return list(reversed(path_moves))

    @staticmethod
    def solve(maze_data: MazeData) -> Optional[List[str]]:
        """
        Solve the maze using A* algorithm.
        Returns list of moves or None if no solution exists.
        """
        maze = maze_data.walls
        rows, cols = len(maze), len(maze[0])
        
        # Get goal position from maze data
        goal_r, goal_c = maze_data.goal_pos
        start = (0, 0)  # Starting position is always top-left
        goal = (goal_r, goal_c)
        
        # Initialize g_score matrix (cost from start to each cell)
        g_score = [[float('inf')] * cols for _ in range(rows)]
        g_score[0][0] = 0
        
        # Dictionary to reconstruct path
        came_from = {}
        
        # Priority queue for frontier: (f_score, row, col)
        start_h = MazeSolver.manhattan_distance(0, 0, goal_r, goal_c)
        frontier = [(start_h, 0, 0)]
        
        while frontier:
            f_current, r, c = heapq.heappop(frontier)
            
            # Found the goal
            if (r, c) == goal:
                return MazeSolver.reconstruct_path(came_from, goal)
            
            # Skip if this node's f_score is outdated
            current_f = g_score[r][c] + MazeSolver.manhattan_distance(r, c, goal_r, goal_c)
            if f_current > current_f:
                continue
            
            # Explore neighbors
            current_g = g_score[r][c]
            for nr, nc, move_dir in MazeSolver.get_neighbors(r, c, maze):
                tentative_g = current_g + 1
                
                if tentative_g < g_score[nr][nc]:
                    g_score[nr][nc] = tentative_g
                    came_from[(nr, nc)] = (r, c, move_dir)
                    f_new = tentative_g + MazeSolver.manhattan_distance(nr, nc, goal_r, goal_c)
                    heapq.heappush(frontier, (f_new, nr, nc))
        
        return None  # No solution found 