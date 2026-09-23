from __future__ import annotations

from typing import Optional


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

_OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}

_DELTA = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0), WEST: (-1, 0)}

_ALL_WALLS_CLOSED = NORTH | EAST | SOUTH | WEST


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        seed: Optional[int] = None,
        perfect: bool = False,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = seed
        self.perfect = perfect
        self.grid: list[list[int]] = [
            [_ALL_WALLS_CLOSED for _ in range(width)] for _ in range(height)
        ]

    def remove_wall(self, x: int, y: int, direction: int) -> None:
        self.grid[y][x] &= ~direction

        dx, dy = _DELTA[direction]
        nx, ny = x + dx, y + dy
        if 0 <= nx < self.width and 0 <= ny < self.height:
            self.grid[ny][nx] &= ~_OPPOSITE[direction]

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        return bool(self.grid[y][x] & direction)

    def generate(self) -> None:
        raise NotImplementedError("generation algorithm not implemented yet")