"""Various helper functions"""
from __future__ import annotations
# import pygame
# from gui_helper import get_dims
from typing import NamedTuple

TSIZE = 25


def add_tuple(x: tuple, y: tuple) -> tuple:
    return tuple(x + y for x, y in zip(x, y))


class Vector(NamedTuple):
    x: int
    y: int

    def __add__(self, other: tuple) -> Vector:
        if isinstance(other, Vector) or isinstance(other, Point):
            return Vector(self.x+other[0], self.y+other[1])
        return NotImplemented

    def __sub__(self, other: tuple) -> Vector:
        if isinstance(other, Vector) or isinstance(other, Point):
            return Vector(self.x-other[0], self.y-other[1])
        return NotImplemented

    def __type__(self) -> type[tuple]:
        return tuple


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other: tuple) -> Point:
        if isinstance(other, Vector) or isinstance(other, Point):
            return Point(self.x+other[0], self.y+other[1])
        return NotImplemented

    def __sub__(self, other: tuple) -> Point:
        if isinstance(other, Vector) or isinstance(other, Point):
            return Point(self.x-other[0], self.y-other[1])
        return NotImplemented

    def __type__(self) -> type[tuple]:
        return tuple


UP, LEFT, DOWN, RIGHT, IDLE = Vector(-1, 0), Vector(0, -1), Vector(1, 0), Vector(0, 1), Vector(0, 0)
FACING = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}


def facing(vector: Vector, original_direction: int) -> int:
    if sum(vector) < 0:
        if min(vector) == vector[0]:
            return 0
        else:
            return 1
    elif sum(vector) > 0:
        if max(vector) == vector[0]:
            return 2
        else:
            return 3
    return original_direction
