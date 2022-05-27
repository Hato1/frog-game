"""Various helper functions"""
from __future__ import annotations
import pygame


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


assets = {
    "Player": pygame.image.load("assets/Frog.png"),
    "Barrel": pygame.image.load("assets/Barrel.png"),
    "Frog": pygame.image.load("assets/BadFrog.png"),
    "Tileset": pygame.image.load("assets/Tileset.png"),
    "Grass": pygame.image.load("assets/Grass.png"),
    "Stone": pygame.image.load("assets/Stone.png"),
    "rockwall": pygame.image.load("assets/rockwall.png"),
}
