"""A-Maze-ing main entry point: loads config, generates a maze, and
displays it in the terminal with ANSI colored blocks and an
interactive menu.

Usage:
    python3 a_maze_ing.py config.txt
"""

from __future__ import annotations

import os
import sys
from collections import deque
from typing import Optional

from config import ConfigError, MazeConfig, load_config
from maze_generator import EAST, NORTH, SOUTH, WEST, MazeGenerator

RESET = "\033[0m"


def _bg(color: int) -> str:
    """Build an ANSI background-color escape code for a 256-color palette index."""
    return f"\033[48;5;{color}m"


BLACK_BG = 0
WALL_COLORS = [15, 226, 51, 208]  # white, yellow, cyan, orange -- rotated with option 3
ENTRY_COLOR = 201  # magenta
EXIT_COLOR = 196   # red
PATH_COLOR = 45    # light blue

# (dx, dy) offset to reach the neighboring cell in each direction.
_DIRS = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0), WEST: (-1, 0)}


def shortest_path(maze: MazeGenerator) -> list[tuple[int, int]]:
    """Compute the shortest path from maze.entry to maze.exit via BFS.

    Returns:
        The list of (x, y) cells from entry to exit, inclusive. Empty
        list if no path exists (shouldn't happen on a valid maze).
    """
    start, goal = maze.entry, maze.exit
    queue: deque[tuple[int, int]] = deque([start])
    came_from: dict[tuple[int, int], Optional[tuple[int, int]]] = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        x, y = current
        for direction, (dx, dy) in _DIRS.items():
            if maze.has_wall(x, y, direction):
                continue
            neighbor = (x + dx, y + dy)
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    if goal not in came_from:
        return []

    path: list[tuple[int, int]] = []
    node: Optional[tuple[int, int]] = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


def render(
    maze: MazeGenerator,
    wall_color: int,
    path: Optional[set[tuple[int, int]]] = None,
) -> str:
    """Render the maze as colored ANSI blocks (2 chars wide per cell)."""
    path = path or set()
    rows, cols = 2 * maze.height + 1, 2 * maze.width + 1
    canvas = [[_bg(BLACK_BG) + "  " + RESET for _ in range(cols)] for _ in range(rows)]
    wall_block = _bg(wall_color) + "  " + RESET

    def set_cell(row: int, col: int, block: str) -> None:
        canvas[row][col] = block

    for row in range(rows):
        for col in range(cols):
            if row % 2 == 0 and col % 2 == 0:
                set_cell(row, col, wall_block)

    for y in range(maze.height):
        for x in range(maze.width):
            row, col = 2 * y + 1, 2 * x + 1
            if maze.has_wall(x, y, NORTH):
                set_cell(row - 1, col, wall_block)
            if maze.has_wall(x, y, SOUTH):
                set_cell(row + 1, col, wall_block)
            if maze.has_wall(x, y, WEST):
                set_cell(row, col - 1, wall_block)
            if maze.has_wall(x, y, EAST):
                set_cell(row, col + 1, wall_block)

            if (x, y) == maze.entry:
                set_cell(row, col, _bg(ENTRY_COLOR) + "  " + RESET)
            elif (x, y) == maze.exit:
                set_cell(row, col, _bg(EXIT_COLOR) + "  " + RESET)
            elif (x, y) in path:
                set_cell(row, col, _bg(PATH_COLOR) + "  " + RESET)

    return "\n".join("".join(row) for row in canvas)


def _build_maze(config: MazeConfig) -> MazeGenerator:
    """Create a MazeGenerator from a MazeConfig and run its generation."""
    maze = MazeGenerator(
        config.width, config.height, config.entry, config.exit, config.seed, config.perfect
    )
    try:
        maze.generate()
    except NotImplementedError:
        # TODO(partner): remove this once generate() is implemented --
        # for now we keep a fully-walled maze so the display can be tested.
        print("(algorithme de generation pas encore implemente - murs tous fermes)")
    return maze


def main() -> None:
    """Entry point: python3 a_maze_ing.py config.txt"""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        config = load_config(sys.argv[1])
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        sys.exit(1)

    maze = _build_maze(config)
    show_path = False
    color_index = 0

    while True:
        # os.system("clear")
        path = set(shortest_path(maze)) if show_path else None
        print(render(maze, WALL_COLORS[color_index], path))
        print()
        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
        choice = input("Choice? (1-4): ").strip()

        if choice == "1":
            maze = _build_maze(config)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index = (color_index + 1) % len(WALL_COLORS)
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
