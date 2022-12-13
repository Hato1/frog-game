"""Various helper functions"""
from __future__ import annotations

import traceback
from typing import NamedTuple, Optional


class Point(NamedTuple):
    """Used for storing vectors and adding them together."""

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


# Movement vectors
UP, LEFT, DOWN, RIGHT, IDLE = (
    Point(0, -1),
    Point(-1, 0),
    Point(0, 1),
    Point(1, 0),
    Point(0, 0),
)


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
    """Colour a string. Colour begins at the start, then colour resets at the end.
    Due to this, colour can be overridden mid-string.
    """
    # properties
    props: list[int] = []
    if style:
        props = [EFFECTS[s] for s in style]
    else:
        props.append(0)
    if isinstance(fg, str):
        props.append(30 + COLORS[fg])
    if isinstance(bg, str):
        props.append(40 + COLORS[bg])

    # display
    formatted_props = ";".join([str(x) for x in props])
    return f"\x1b[{formatted_props}m{fmt}\x1b[0m"


class IndentedLogging:
    """Logging object that indents logs based on how many functions it is deep relative to the instantiation time."""

    def __init__(self, level):
        self.level = level
        self.base_indent = len(traceback.extract_stack())
        self.maximum_indent = 2
        self.fg = None

    def __call__(self, msg: str):
        """Log."""
        stack_delta = len(traceback.extract_stack()) - self.base_indent
        prefix = "    " * min(stack_delta, self.maximum_indent)
        self.level(c(prefix + msg, fg=self.fg))


class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)
