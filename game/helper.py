"""Various helper functions"""
from __future__ import annotations

import math
from enum import Enum
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


class Facing(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


def get_facing_direction(move: Point, original_direction: int) -> int:
    """Get the cardinal direction an entity should be facing after making a move."""
    if move == Point(0, 0):
        return original_direction
    # Adding a cheeky +1 to degrees so 45 and -45 don't both equate to the same direction.
    degrees = math.atan2(*move) / math.pi * 180 + 1
    compass_lookup = round(degrees / 90) % 360
    return [2, 3, 0, 1][compass_lookup % 4]
    # if sum(move) < 0:
    #     return 1 if min(move) == move[0] else 0
    # elif sum(move) > 0:
    #     return 3 if max(move) == move[0] else 2
    # return original_direction


def is_in_map(point: Point, dims: tuple[int, int]) -> bool:
    """Return whether point lies in the map"""
    return 0 <= point.x < dims[0] and 0 <= point.y < dims[1]
