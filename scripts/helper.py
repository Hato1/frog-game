"""Various helper functions"""
from __future__ import annotations
# import pygame
# from gui_helper import get_dims

TSIZE = 25


def add_tuple(x: tuple, y: tuple) -> tuple:
    return tuple(x + y for x, y in zip(x, y))


class Vector(tuple):
    def __add__(self, thing2: tuple) -> Vector:
        return Vector((self[0]+thing2[0], self[1]+thing2[1]))

    def __sub__(self, thing2: tuple) -> Vector:
        return Vector((self[0]-thing2[0], self[1]-thing2[1]))

    def __type__(self) -> type[tuple]:
        return tuple


UP, LEFT, DOWN, RIGHT, IDLE = Vector((-1, 0)), Vector((0, -1)), Vector((1, 0)), Vector((0, 1)), Vector((0, 0))
FACING = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}


def facing(vector, original_direction):
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
