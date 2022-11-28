"""Various helper functions"""
from __future__ import annotations

import math
import traceback
from enum import Enum
from typing import NamedTuple, Optional


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

    def __repr__(self):
        return f"({self.x}, {self.y})"


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


# TODO: Make these Enums
COLORS = {
    "k": 0,  # black
    "r": 1,  # red
    "g": 2,  # green
    "y": 3,  # yellow
    "b": 4,  # blue
    "m": 5,  # magenta
    "c": 6,  # cyan
    "w": 7,  # white
}

EFFECTS = {
    "b": 1,  # bold
    "f": 2,  # faint
    "i": 3,  # italic
    "u": 4,  # underline
    "x": 5,  # blinking
    "y": 6,  # fast blinking
    "r": 7,  # reverse
    "h": 8,  # hide
    "s": 9,  # strikethrough
}


def c(fmt, fg=None, bg=None, style: Optional[list[str]] = None):
    """Colour a string"""
    # properties
    props: list[int] = []
    if style:
        props = [EFFECTS[s] for s in style]
    else:
        props.append(0)
    if isinstance(fg, str):
        props.append(30 + COLORS[fg])
    # else:
    #     props.append(20)
    if isinstance(bg, str):
        props.append(40 + COLORS[bg])

    # display
    formatted_props = ";".join([str(x) for x in props])
    return f"\x1b[{formatted_props}m{fmt}\x1b[0m"


class IndentedLogging:
    def __init__(self, level):
        self.level = level
        self.base_indent = len(traceback.extract_stack())
        self.fg = None

    def __call__(self, msg: str):
        stack_delta = len(traceback.extract_stack()) - self.base_indent
        prefix = "    " * min(stack_delta, 2)
        self.level(c(prefix + msg, fg=self.fg))
