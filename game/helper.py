"""Various helper functions"""
from __future__ import annotations

from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other: Point | tuple) -> Point:
        if isinstance(other, Point):
            return Point(self.x + other[0], self.y + other[1])
        return NotImplemented

    def __sub__(self, other: Point | tuple) -> Point:
        if isinstance(other, Point):
            return Point(self.x - other[0], self.y - other[1])
        return NotImplemented

    def __mul__(self, other: int):  # type: ignore[override]
        """Multiply vector by a scalar"""
        return Point(self.x * other, self.y * other)


UP, LEFT, DOWN, RIGHT, IDLE = (
    Point(0, -1),
    Point(-1, 0),
    Point(0, 1),
    Point(1, 0),
    Point(0, 0),
)


def get_facing_direction(move: Point, original_direction: int) -> int:
    """Get the cardinal direction an entity should be facing after making a move."""
    if sum(move) < 0:
        return 1 if min(move) == move[0] else 0
    elif sum(move) > 0:
        return 3 if max(move) == move[0] else 2
    return original_direction


def is_in_map(point: Point, dims: tuple[int, int]) -> bool:
    """Return whether point lies in the map"""
    return 0 <= point.x < dims[0] and 0 <= point.y < dims[1]
