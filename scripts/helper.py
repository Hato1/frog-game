"""Various helper functions"""
from __future__ import annotations

import logging
from typing import NamedTuple, Union

import pygame as pg

TSIZE = 25


class Benchmark:
    def __init__(self) -> None:
        self.time = pg.time.get_ticks()

    def log_time_delta(self) -> None:
        new_time = pg.time.get_ticks()
        difference = new_time - self.time
        self.time = new_time
        logging.debug(msg=difference)


def add_tuple(x: tuple, y: tuple) -> tuple:
    return tuple(x + y for x, y in zip(x, y))


class Vector(NamedTuple):
    x: int
    y: int

    def __add__(self, other: tuple) -> Vector:
        if isinstance(other, (Vector, Point)):
            return Vector(self.x + other[0], self.y + other[1])
        return NotImplemented

    def __sub__(self, other: tuple) -> Vector:
        if isinstance(other, (Vector, Point)):
            return Vector(self.x - other[0], self.y - other[1])
        return NotImplemented


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other: Union[Point, tuple]) -> Point:
        if isinstance(other, (Vector, Point)):
            return Point(self.x + other[0], self.y + other[1])
        return NotImplemented

    def __sub__(self, other: Union[Point, tuple]) -> Point:
        if isinstance(other, (Vector, Point)):
            return Point(self.x - other[0], self.y - other[1])
        return NotImplemented


UP, LEFT, DOWN, RIGHT, IDLE = (
    Vector(-1, 0),
    Vector(0, -1),
    Vector(1, 0),
    Vector(0, 1),
    Vector(0, 0),
)
FACING = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}


def facing(vector: Vector, original_direction: int) -> int:
    if sum(vector) < 0:
        return 0 if min(vector) == vector[0] else 1
    elif sum(vector) > 0:
        return 2 if max(vector) == vector[0] else 3
    return original_direction
